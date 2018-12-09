import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

if __name__ == "__main__":
    
    plt.figure()

    data1 = pd.read_csv('tcpdata1-q200/q.txt', sep=',', header=None)
    data2 = pd.read_csv('dctcpdata1-q200/q.txt', sep=',', header=None)
    
    data1=np.array(data1)
    y = data1[:, 1]
    plt.plot(y, 'r--',label="tcp")
    
    data2=np.array(data2)
    y = data2[:, 1]
    plt.plot( y, 'k-',label="dctcp")

    plt.xlabel("Time(*0.57s)")
    plt.ylabel("Q size(packets)")

    plt.legend()
    plt.savefig('graphs/qsize.png')
    plt.show()

    plt.figure()
    
    data3 = pd.read_csv('dctcpdata2-q200/k.txt',sep = ',', header = None)
    data3 = np.array(data3)

    x = data3[:,0]
    y = data3[:,1]

    plt.plot(x,y, 'k+', x,y, 'k' ,label="k sweep")
    plt.xlabel("K")
    plt.ylabel("Throughput(Mbps)")
    plt.axis([0,100,0,100])

    plt.savefig('graphs/throughput.png')
    plt.show()

    plt.figure()
    
    data4 = pd.read_csv('dctcpdata3-h3/q.txt', sep=',', header=None)
    data4 = np.array(data4)

    q1 = data4[:, 1]
    q1_dic = {}
    for x in q1:
        if int(x) not in q1_dic.keys():
            q1_dic[int(x)] = 1
        else:
            q1_dic[int(x)] += 1
    count1 = [0] * 201
    cdf1 = [0] * 201
    for x in q1_dic.keys():
        count1[x] = q1_dic[x]
    t1 = sum(count1)
    for i in range(1,201):
        cdf1[i] = cdf1[i-1] + count1[i]/t1
    plt.plot(cdf1,'b', label="dctcp_2flows")

    data5 = pd.read_csv('dctcpdata3-h21/q.txt', sep=',', header=None)
    data5 = np.array(data5)

    q2 = data5[:, 1]
    q2_dic = {}
    for x in q2:
        if int(x) not in q2_dic.keys():
            q2_dic[int(x)] = 1
        else:
            q2_dic[int(x)] += 1
    count2 = [0] * 201
    cdf2 = [0] * 201
    for x in q2_dic.keys():
        count2[x] = q2_dic[x]
    t2 = sum(count2)
    for i in range(1, 201):
        cdf2[i] = cdf2[i - 1] + count2[i] / t2
    plt.plot(cdf2, 'g', label="dctcp_20flows")

    data6 = pd.read_csv('tcpdata3-h3/q.txt', sep=',', header=None)
    data6 = np.array(data6)

    q3 = data6[:, 1]
    q3_dic = {}
    for x in q3:
        if int(x) not in q3_dic.keys():
            q3_dic[int(x)] = 1
        else:
            q3_dic[int(x)] += 1
    count3 = [0] * 201
    cdf3 = [0] * 201
    for x in q3_dic.keys():
        count3[x] = q3_dic[x]
    t3 = sum(count3)
    for i in range(1, 201):
        cdf3[i] = cdf3[i - 1] + count3[i] / t3
    plt.plot(cdf3, 'k--', label="tcp_2flows")

    data7 = pd.read_csv('tcpdata3-h21/q.txt', sep=',', header=None)
    data7 = np.array(data7)

    q4 = data7[:, 1]
    q4_dic = {}
    for x in q4:
        if int(x) not in q4_dic.keys():
            q4_dic[int(x)] = 1
        else:
            q4_dic[int(x)] += 1
    count4 = [0] * 201
    cdf4 = [0] * 201
    for x in q4_dic.keys():
        count4[x] = q4_dic[x]
    t4 = sum(count4)
    for i in range(1, 201):
        cdf4[i] = cdf4[i - 1] + count4[i] / t4
    plt.plot(cdf4, 'k', label="tcp_20flows")
    plt.axis([0,200,0,1])
    plt.xlabel("Q size(packets)")
    plt.ylabel("cdf")

    plt.legend()
    plt.savefig('graphs/cdf.png')
    plt.show()
