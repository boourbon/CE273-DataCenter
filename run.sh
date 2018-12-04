#!/bin/bash
mn -c

sudo modprobe tcp_probe

#11111111111111111111111111111111111111
time=12
bwnet=100
delay=0.25

# Red settings (for DCTCP)
dctcp_red_limit=1000000
dctcp_red_min=30000
dctcp_red_max=30001
dctcp_red_avpkt=1500
dctcp_red_burst=20
dctcp_red_prob=1
iperf_port=5001
iperf=~/iperf-patched/src/iperf
for qsize in 200; do
    rm -rf dctcpgraphs-q$qsize
    mkdir dctcpgraphs-q$qsize
    rm -rf dctcpbb1-q$qsize
    rm -rf tcpbb1-q$qsize
    dirf=dctcpgraphs-q$qsize
    dir1=dctcpbb1-q$qsize
    python dctcp.py --delay $delay -b $bwnet -B $bwnet -d $dir1 --maxq $qsize -t $time \
    --red_limit $dctcp_red_limit \
    --red_min $dctcp_red_min \
    --red_max $dctcp_red_max \
    --red_avpkt $dctcp_red_avpkt \
    --red_burst $dctcp_red_burst \
    --red_prob $dctcp_red_prob \
    --dctcp 1 \
    --red 0 \
    --iperf $iperf -k 0 -n 3
    dir2=tcpbb1-q$qsize
    python dctcp.py --delay $delay -b 100 -d $dir2 --maxq $qsize -t $time \
    --dctcp 0 --red 0 --iperf $iperf -k 0 -n 3

    python plot_queue.py -f $dir1/q.txt $dir2/q.txt --legend dctcp tcp -o \
    $dirf/dctcp_tcp_queue.png
    #rm -rf $dir1 $dir2
done

#2222222222222222222222222222222222222222
time=30
bwnet=100
delay=1

# Red settings (for DCTCP)
dctcp_red_limit=1000000
dctcp_red_avpkt=1000
dctcp_red_burst=100
dctcp_red_prob=1
iperf_port=5001
iperf=~/iperf-patched/src/iperf
#qsize=200
for qsize in 200; do
    dirf=dctcpgraphs-q$qsize
    rm -rf dctcpbb2-q$qsize
    mkdir dctcpbb2-q$qsize
    dir1=dctcpbb2-q$qsize
    for k in 3 5 9 15 20 30 40 60 80 100; do
        dctcp_red_min=`expr $k \\* $dctcp_red_avpkt`
        dctcp_red_max=`expr $dctcp_red_min + 1`
        python dctcp.py --delay $delay -b $bwnet -B $bwnet -k $k -d $dir1 --maxq $qsize -t $time \
        --red_limit $dctcp_red_limit \
        --red_min $dctcp_red_min \
        --red_max $dctcp_red_max \
        --red_avpkt $dctcp_red_avpkt \
        --red_burst $dctcp_red_burst \
        --red_prob $dctcp_red_prob \
        --dctcp 1 \
	--red 0\
        --iperf $iperf -n 3
    done
done

python plot_k_sweep.py -f $dir1/k.txt -l Ksweep -o $dirf/k_sweep.png
#rm -rf $dir1

#33333333333333333333333333333333333333
time=80
bwnet=100
delay=0.5

# Red settings (for DCTCP)
dctcp_red_limit=1000000
dctcp_red_min=20000
dctcp_red_max=20001
dctcp_red_avpkt=1000
dctcp_red_burst=20
dctcp_red_prob=1
iperf_port=5001
iperf=~/iperf-patched/src/iperf
for qsize in 200; do
    dirf=dctcpgraphs-q$qsize
    for hosts in 3 21; do
	      dir1=dctcpbb3-h$hosts
	      python dctcp.py --delay $delay -b $bwnet -B $bwnet -d $dir1 --maxq $qsize -t $time \
	      --red_limit $dctcp_red_limit \
	      --red_min $dctcp_red_min \
	      --red_max $dctcp_red_max \
	      --red_avpkt $dctcp_red_avpkt \
	      --red_burst $dctcp_red_burst \
	      --red_prob $dctcp_red_prob \
	      --dctcp 1 \
	      --red 0 \
	      --iperf $iperf -k 0 -n $hosts
	      dir2=tcpbb3-h$hosts
	      python dctcp.py --delay $delay -b 100 -d $dir2 --maxq $qsize -t $time \
	      --dctcp 0 --red 0 --iperf $iperf -k 0 -n $hosts
    done
    
    python plot_cdf.py -f dctcpbb3-h3/q.txt dctcpbb3-h21/q.txt tcpbb3-h3/q.txt \
    tcpbb3-h21/q.txt -l dctcp2flows dctcp20flows tcp2flows tcp20flows -o $dirf/cdf_flows.png
    #rm -rf dctcpbb-h3 dctcpbb-h21 tcpbb-h21 tcpbb-h3
done
