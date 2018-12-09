#!/bin/bash
mn -c

sudo modprobe tcp_probe

# Figure 1 **************************************************
time=12
bwnet=100
delay=0.25
dctcp_red_limit=1000000
dctcp_red_min=30000
dctcp_red_max=30001
dctcp_red_avpkt=1500
dctcp_red_burst=20
dctcp_red_prob=1
iperf_port=5001
iperf=~/iperf-patched/src/iperf

for qsize in 200; do
    rm -rf dctcpdata1-q$qsize
    rm -rf tcpdata1-q$qsize
    
    dir1=dctcpdata1-q$qsize
    
    python dctcp.py --delay $delay \
    -b $bwnet \
    -B $bwnet \
    -d $dir1 \
    --maxq $qsize \
    -t $time \
    --red_limit $dctcp_red_limit \
    --red_min $dctcp_red_min \
    --red_max $dctcp_red_max \
    --red_avpkt $dctcp_red_avpkt \
    --red_burst $dctcp_red_burst \
    --red_prob $dctcp_red_prob \
    --dctcp 1 \
    --red 0 \
    --iperf $iperf -k 0 -n 3
    
    dir2=tcpdata1-q$qsize
    
    python dctcp.py --delay $delay \
    -b 100 \
    -d $dir2 \
    --maxq $qsize \
    -t $time \
    --dctcp 0 \
    --red 0 \
    --iperf $iperf \
    -k 0 \
    -n 3
    
done


# Figure 2 **************************************************
time=30
bwnet=100
delay=1
dctcp_red_limit=1000000
dctcp_red_avpkt=1000
dctcp_red_burst=100
dctcp_red_prob=1
iperf_port=5001
iperf=~/iperf-patched/src/iperf

for qsize in 200; do
    rm -rf dctcpdata2-q$qsize
    dir3=dctcpdata2-q$qsize
    
    for k in 3 5 9 15 20 30 40 60 80 100; do
        dctcp_red_min=`expr $k \\* $dctcp_red_avpkt`
        dctcp_red_max=`expr $dctcp_red_min + 1`
	
        python dctcp.py --delay $delay \
	-b $bwnet \
	-B $bwnet \
	-k $k \
	-d $dir3 \
	--maxq $qsize \
	-t $time \
        --red_limit $dctcp_red_limit \
        --red_min $dctcp_red_min \
        --red_max $dctcp_red_max \
        --red_avpkt $dctcp_red_avpkt \
        --red_burst $dctcp_red_burst \
        --red_prob $dctcp_red_prob \
        --dctcp 1 \
	--red 0\
        --iperf $iperf \
	-n 3
	
    done
done


# Figure 3 **************************************************
time=80
bwnet=100
delay=0.5
dctcp_red_limit=1000000
dctcp_red_min=20000
dctcp_red_max=20001
dctcp_red_avpkt=1000
dctcp_red_burst=20
dctcp_red_prob=1
iperf_port=5001
iperf=~/iperf-patched/src/iperf
for qsize in 200; do
    for hosts in 3 21; do
        rm -rf dctcpdata3-h$hosts
        rm -rf tcpdata3-h$hosts
	
	 dir4=dctcpdata3-h$hosts
	
	 python dctcp.py --delay $delay \
	 -b $bwnet \
	 -B $bwnet \
	 -d $dir4 \
	 --maxq $qsize \
	 -t $time \
	 --red_limit $dctcp_red_limit \
	 --red_min $dctcp_red_min \
	 --red_max $dctcp_red_max \
	 --red_avpkt $dctcp_red_avpkt \
	 --red_burst $dctcp_red_burst \
	 --red_prob $dctcp_red_prob \
	 --dctcp 1 \
	 --red 0 \
	 --iperf $iperf \
	 -k 0 \
	 -n $hosts
	      
	 dir5=tcpdata3-h$hosts
	      
	 python dctcp.py --delay $delay \
	 -b 100 \
	 -d $dir5 \
	 --maxq $qsize \
	 -t $time \
	 --dctcp 0 \
	 --red 0 \
	 --iperf $iperf \
	 -k 0 \
	 -n $hosts
	      
    done
done

mkdir graphs
python plot_all.py
