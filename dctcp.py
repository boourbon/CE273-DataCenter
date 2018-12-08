import sys
import os
import math
import re
import termcolor as T
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink, TCIntf, Link
from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser
from time import sleep, time
from subprocess import *


#Star topology for DCTCP experiment
class StarTopo(Topo):
    def __init__(self, n=3, cpu=None, bw_host=None, bw_net=None, delay=None, maxq=None, enable_dctcp=None, enable_red=None, show_mininet_commands=False, red_params=None):
        # Add default members to class.
        super(StarTopo, self ).__init__()
        self.n = n
        self.cpu = cpu
        self.bw_host = bw_host
        self.bw_net = bw_net
        self.delay = delay
        self.maxq = maxq
        self.enable_dctcp = enable_dctcp
        self.enable_red = enable_red
        self.red_params = red_params
        self.show_mininet_commands = show_mininet_commands;
        print("Enable DCTCP: %d" % self.enable_dctcp)
        print("Enable RED: %d" % self.enable_red)
        self.create_topology()

    # Set appropriate values for bandwidth, delay, and queue size 
    def create_topology(self):
        hconfig = {'cpu': self.cpu}
        if self.enable_dctcp: 
	    print("Enabling ECN for senders/receiver")
        lconfig_sender = {'bw': self.bw_host, 'delay': self.delay, 'max_queue_size': self.maxq, 
			  'show_commands': self.show_mininet_commands}
        lconfig_receiver = {'bw': self.bw_net, 'delay': 0, 'max_queue_size': self.maxq, 
			    'show_commands': self.show_mininet_commands}                            
        lconfig_switch = {'bw': self.bw_net, 'delay': 0, 'max_queue_size': self.maxq,
                            'enable_ecn': 1 if self.enable_dctcp else 0,
                            'enable_red': 1 if self.enable_red else 0,
                            'red_params': self.red_params if ((self.enable_red or self.enable_dctcp) 
			        and (self.red_params != None)) else None,
                            'show_commands': self.show_mininet_commands} 
        n = self.n
        receiver = self.addHost('h0')
        switch = self.addSwitch('s0')
        hosts = []
        for i in range(n-1):
            hosts.append(self.addHost('h%d' % (i+1), **hconfig))
	self.addLink(receiver, switch, cls=Link,
                      cls1=TCIntf, cls2=TCIntf,
                      params1=lconfig_receiver, params2=lconfig_switch)
        for i in range(n-1):
	    self.addLink(hosts[i], switch, **lconfig_sender)


CALIBRATION_SKIP = 20
CALIBRATION_SAMPLES = 10
NSAMPLES = 8
SAMPLE_PERIOD_SEC = 1.0
SAMPLE_WAIT_SEC = 3.0


def get_txbytes(iface):
    f = open('/proc/net/dev', 'r')
    lines = f.readlines()
    for line in lines:
        if iface in line:
            break
    f.close()
    if not line:
        raise Exception("could not find iface %s in /proc/net/dev:%s" %
                        (iface, lines))
    return float(line.split()[9])


def get_rates(iface, nsamples=NSAMPLES, period=SAMPLE_PERIOD_SEC, wait=SAMPLE_WAIT_SEC):
    nsamples += 1
    last_time = 0
    last_txbytes = 0
    ret = []
    sleep(wait)
    while nsamples:
        nsamples -= 1
        txbytes = get_txbytes(iface)
        now = time()
        elapsed = now - last_time
        last_time = now
        rate = (txbytes - last_txbytes) * 8.0 / 1e6 / elapsed
        if last_txbytes != 0:
            # Wait for 1 second sample
            ret.append(rate)
        last_txbytes = txbytes
        print '.',
        sys.stdout.flush()
        sleep(period)
    return ret


parser = ArgumentParser(description="Bufferbloat tests")
parser.add_argument('--bw-host', '-B',
                    type=float,
                    help="Bandwidth of host links (Mb/s)",
                    default=100)

parser.add_argument('--bw-net', '-b',
                    type=float,
                    help="Bandwidth of bottleneck (network) link (Mb/s)",
                    required=True)

parser.add_argument('--delay',
                    type=float,
                    help="Link propagation delay (ms)",
                    required=True)

parser.add_argument('--dir', '-d',
                    help="Directory to store outputs",
                    required=True)

parser.add_argument('--hosts', '-n',
                    help="Duration (sec) to run the experiment",
                    type=int,
                    default=3)

parser.add_argument('--time', '-t',
                    help="Duration (sec) to run the experiment",
                    type=int,
                    default=10)

parser.add_argument('--maxq',
                    type=int,
                    help="Max buffer size of network interface in packets",
                    default=100)

# RED Parameters 
parser.add_argument('--mark_threshold', '-k',
		    help="Marking threshold",
		    type=int,
		    default="20")

parser.add_argument('--red_limit',
		    help="RED limit",
		    default="1000000")

parser.add_argument('--red_min',
		    help="RED min marking threshold",
		    default="20000")

parser.add_argument('--red_max',
		    help="RED max marking threshold",
		    default="25000")

parser.add_argument('--red_avpkt',
		    help="RED average packet size",
		    default="1000")

parser.add_argument('--red_burst',
		    help="RED burst size",
		    default="20") 

parser.add_argument('--red_prob',
		    help="RED marking probability",
		    default="1")

parser.add_argument('--dctcp',
		    help="Enable DCTCP",
		    type=int,
		    default="0")

parser.add_argument('--red',
		    help="Enable RED",
		    type=int,
		    default="0")

parser.add_argument('--iperf',
                    dest="iperf",
                    help="Path to custom iperf",
                    required=True)

parser.add_argument('--cong',
                    help="Congestion control algorithm to use",
                    default="reno")

args = parser.parse_args()
CUSTOM_IPERF_PATH = args.iperf
assert(os.path.exists(CUSTOM_IPERF_PATH))
if not os.path.exists(args.dir):
    os.makedirs(args.dir)


def start_tcpprobe(outfile="cwnd.txt"):
    os.system("rmmod tcp_probe; modprobe tcp_probe full=1;")
    Popen("cat /proc/net/tcpprobe > %s/%s" % (args.dir, outfile),
          shell=True)

	
def stop_tcpprobe():
    Popen("killall -9 cat", shell=True).wait()


def SetDCTCPState():
    Popen("sysctl -w net.ipv4.tcp_dctcp_enable=1", shell=True).wait()
    Popen("sysctl -w net.ipv4.tcp_ecn=1", shell=True).wait()


def ResetDCTCPState():
    Popen("sysctl -w net.ipv4.tcp_dctcp_enable=0", shell=True).wait()
    Popen("sysctl -w net.ipv4.tcp_ecn=0", shell=True).wait()


def start_receiver(net):
    h0 = net.getNodeByName('h0')
    print "Starting iperf server..."
    server = h0.popen("%s -s -w 16m" % CUSTOM_IPERF_PATH)


def start_senders(net):
    h0 = net.getNodeByName('h0')
    for i in range(args.hosts-1):
	print "Starting iperf client..."
	hn = net.getNodeByName('h%d' %(i+1))
	client = hn.popen("%s -c " % CUSTOM_IPERF_PATH + h0.IP() + " -t 1000")
	
def monitor_qlen(iface, interval_sec = 0.01, fname='%s/qlen.txt' % default_dir):
    pat_queued = re.compile(r'backlog\s[^\s]+\s([\d]+)p')
    cmd = "tc -s qdisc show dev %s" % (iface)
    ret = []
    open(fname, 'w').write('')
    while 1:
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.stdout.read()
        # Not quite right, but will do for now
        matches = pat_queued.findall(output)
        if matches and len(matches) > 1:
            ret.append(matches[1])
            t = "%f" % time()
            open(fname, 'a').write(t + ',' + matches[1] + '\n')
        sleep(interval_sec)
    return


# Queue occupancy 
def start_qmon(iface, interval_sec=0.5, outfile="q.txt"):
    monitor = Process(target=monitor_qlen,
                      args=(iface, interval_sec, outfile))
    monitor.start()
    return monitor

	
# Compute the median
def median(l):
    s = sorted(l)
    if len(s) % 2 == 1:
        return s[(len(l) + 1) / 2 - 1]
    else:
        lower = s[len(l) / 2 - 1]
        upper = s[len(l) / 2]
        return float(lower + upper) / 2


# Speed of an interface
def set_speed(iface, spd):
    "Change htb maximum rate for interface"
    cmd = ("tc class change dev %s parent 1:0 classid 1:1 "
               "htb rate %s burst 15k" % (iface, spd))
    os.system(cmd)


def dctcp():
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)
    os.system("sudo sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong)
    if (args.dctcp):
        SetDCTCPState()
	edctcp=1
    else:
        ResetDCTCPState()
	edctcp=0

    red_settings = {}
    red_settings['limit'] = args.red_limit
    red_settings['min'] = args.red_min
    red_settings['max'] = args.red_max
    red_settings['avpkt'] = args.red_avpkt
    red_settings['burst'] = args.red_burst
    red_settings['prob'] = args.red_prob

    topo = StarTopo(n=args.hosts, 
		    bw_host=args.bw_host, 
	            delay='%sms' % args.delay,
		    bw_net=args.bw_net,
		    maxq=args.maxq,
		    enable_dctcp=edctcp,
		    enable_red=args.red,
		    red_params=red_settings,
		    show_mininet_commands=0)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink,
 		 autoPinCpus=True)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()

    iface="s0-eth1"
    set_speed(iface, "2Gbit")
    start_receiver(net)
    start_senders(net)
    sleep(5)
    set_speed(iface, "%.2fMbit" % args.bw_net)
    sleep(20)

    # Monitoring the queue sizes.
    qmon = start_qmon(iface='s0-eth1', outfile='%s/q.txt' % (args.dir))
    start_tcpprobe("cwnd.txt")
    start_time = time()
    while True:
        now = time()
        delta = now - start_time
        if delta > args.time:
            break

    # Get the rate of the bottlenect link if the experiment involves marking bandwidth for different threshold
    if(args.mark_threshold):
	rates = get_rates(iface='s0-eth1', nsamples=CALIBRATION_SAMPLES+CALIBRATION_SKIP)
	rates = rates[CALIBRATION_SKIP:]
	reference_rate = median(rates)
	if (reference_rate > 20):
	    with open(args.dir+"/k.txt", "a") as myfile:
		myfile.write(str(args.mark_threshold)+",")
		myfile.write(str(reference_rate))
		myfile.write("\n")
		myfile.close()

    stop_tcpprobe()
    qmon.terminate()
    net.stop()
    Popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()


if __name__ == "__main__":
    dctcp ()
