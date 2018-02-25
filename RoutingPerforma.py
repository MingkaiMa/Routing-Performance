
from collections import defaultdict



import sys
import random
from collections import defaultdict


network_scheme = sys.argv[1]
routing_scheme = sys.argv[2]
topology_file = sys.argv[3]
workload_file = sys.argv[4]
packet_rate = sys.argv[5]
L = []


max_value = float('inf')
non = float('nan')

dic_let_to_nb = {}

for i in range(26):
    dic_let_to_nb[chr(65 + i)] = i
    

Graph = [[(max_value, max_value, max_value, non)] * 26 for _ in range(26)]
for i in range(26):
    for j in range(26):
        if(i == j):
            Graph[i][j] = (0, 0, 0, non)

with open(topology_file) as file:
    for line in file:
        s = line.split()
        Graph[dic_let_to_nb[s[0]]][dic_let_to_nb[s[1]]] = (1, int(s[2]), int(s[3]), 0)
        Graph[dic_let_to_nb[s[1]]][dic_let_to_nb[s[0]]] = (1, int(s[2]), int(s[3]), 0)


def shortest_hop_path(start_node, dest_node, Graph):
    path = []
    
    D = [max_value] * 26
    P = [-1] * 26
    S = [0] * 26

    for i in range(26):
        D[i] = Graph[start_node][i][0]
        if(D[i] != max_value):
            P[i] = start_node

    S[start_node] = 1


    for i in range(26):
        min_value = max_value
        for j in range(26):
            if((not S[j]) and D[j] < min_value):

                min_value = D[j]
                k = j

        S[k] = 1

        for j in range(26):
            if((not S[j]) and D[j] > D[k] + Graph[k][j][0]):
                D[j] = D[k] + Graph[k][j][0]
                P[j] = k


 
    if(D[dest_node] != max_value):
        t = dest_node
        for i in range(D[dest_node] + 1):
            path.append(t)
            t = P[t]
            
    path.reverse()
    return path
            

def is_intersect(interval_1, interval_2):
    if max(interval_1[0], interval_2[0]) < min(interval_1[1], interval_2[1]):
        return True
    return False


def shortest_hop_circuit():
    dic = defaultdict(list)

    total_number_of_virtual_circuit_requests = 0
    total_number_of_packets = 0
    number_of_successfully_routed_packets = 0
    number_of_blocked_packets = 0
    number_of_hops = 0
    cumulative_propagation_delay = 0


    with open(workload_file) as file:
        for line in file:
            total_number_of_virtual_circuit_requests += 1
            
            
            block_flag = 0
            s = line.split()
            total_number_of_packets += int(packet_rate * float(s[3]))
            shortest_path = shortest_hop_path(dic_let_to_nb[s[1]], dic_let_to_nb[s[2]], Graph)
            now_interval = (float(s[0]), float(s[0]) + float(s[3]))
            temp_dic = {}
            for i in range(len(shortest_path) - 1):
                
                now_link = (shortest_path[i], shortest_path[i + 1])
                oppo_link = (shortest_path[i + 1], shortest_path[i])
                if now_link not in dic and oppo_link not in dic:
                    temp_dic[now_link] = now_interval
                elif now_link not in dic and oppo_link in dic:
                    n = 1
                    for time_interval in dic[oppo_link]:
                        if is_intersect(now_interval, time_interval):
                            n += 1

                    if n > Graph[shortest_path[i]][shortest_path[i + 1]][2]:
                        block_flag = 1
                        break
                    else:
                        temp_dic[oppo_link] = now_interval
                        
                elif now_link in dic:
                    n = 1
                    for time_interval in dic[now_link]:
                        
                        if is_intersect(now_interval, time_interval):
       
                            n += 1               
                    if n > Graph[shortest_path[i]][shortest_path[i + 1]][2]:

                        block_flag = 1
                        break
                    else:
                        temp_dic[now_link] = now_interval

            if block_flag == 1:
                number_of_blocked_packets += int(packet_rate * float(s[3]))
            else:
                number_of_successfully_routed_packets += int(packet_rate * float(s[3]))
                number_of_hops += len(shortest_path)
                for i in range(len(shortest_path) - 1):
                    cumulative_propagation_delay += Graph[shortest_path[i]][shortest_path[i + 1]][1]
                for link in temp_dic:
                    dic[link].append(temp_dic[link])
            



    print('total number of virtual circuit requests: ', total_number_of_virtual_circuit_requests)
    print('total number of packets: ', total_number_of_packets)
    print('number of successfully routed packets: ', number_of_successfully_routed_packets)
    print('percentage of successfully routed packets: {:5.2f}'.format((number_of_successfully_routed_packets /
                                                                      total_number_of_packets) * 100 ))
    print('number of blocked packets: ', number_of_blocked_packets)
    print('percentage of blocked packets: {:5.2f}'.format((number_of_blocked_packets /
                                                          total_number_of_packets) * 100))
    print('average number of hops per circuit: {:5.2f}'.format(number_of_hops / total_number_of_virtual_circuit_requests))
    print('average cumulative propagation delay per circuit: {:5.2f}'.format(cumulative_propagation_delay /
                                                                             total_number_of_virtual_circuit_requests))

        

                
            
def shortest_delay_path(start_node, dest_node, Graph):
    path = []
    
    D = [max_value] * 26
    P = [-1] * 26
    S = [0] * 26

    for i in range(26):
        D[i] = Graph[start_node][i][1]
        if(D[i] != max_value):
            P[i] = start_node

    S[start_node] = 1


    for i in range(26):
        min_value = max_value
        for j in range(26):
            if((not S[j]) and D[j] < min_value):

                min_value = D[j]
                k = j

        S[k] = 1

        for j in range(26):
            if((not S[j]) and D[j] > D[k] + Graph[k][j][1]):
                D[j] = D[k] + Graph[k][j][1]
                P[j] = k


    
    if(D[dest_node] != max_value):
        t = dest_node
        while True:
            if(t == start_node):
                path.append(t)
                break
            else:
                path.append(t)
                t = P[t]
            
    path.reverse()
    return path



def find_all_path(start_node, dest_node, Graph):
    visited = []
    result = []

    stack = [[start_node]]
    while stack:
        path = stack.pop()
        if(path.count(path[-1]) > 1):
            continue
        D = Graph[path[-1]]
        for i in reversed(range(len(D))):
            if(D[i][0] != max_value and D[i][0] != 0):
                if i == dest_node:
                    result.append(path + [i])
                else:
                    stack.append(path + [i])

    return result

def find_least_loaded_path(all_path, current_time, dic):
    

    all_load = []
    for path in all_path:
        #print(path)
        max_ratio = 0
        for i in range(len(path) - 1):
            occu_count = 0
            if len(dic[(path[i], path[i + 1])]) != 0:
                #print('*', (path[i], path[i + 1]))
                for time_interval in dic[(path[i], path[i + 1])]:
                    #print('paht is: ', (path[i], path[i + 1]), time_interval)
                    if time_interval[0] <= current_time and time_interval[1] >= current_time:
                        occu_count += 1
            elif len(dic[(path[i + 1], path[i])]) != 0:
                #print('**', (path[i + 1], path[i]))
                for time_interval in dic[(path[i + 1], path[i])]:
                    #print('paht is oppo: ', (path[i], path[i + 1]), time_interval)
                    if time_interval[0] <= current_time and time_interval[1] >= current_time:
                        occu_count += 1
                    

            if ((occu_count / Graph[path[i]][path[i + 1]][2]) > max_ratio):
                max_ratio = occu_count / Graph[path[i]][path[i + 1]][2]
 #       print('ppp', path, max_ratio)

        
        all_load.append(max_ratio)

    
            

 #   t = random.choice([i for i, j in enumerate(all_load) if j == min(all_load)])
    t = all_load.index(min(all_load))
    return all_path[t]
    
    


def shortest_delay_circuit():
    dic = defaultdict(list)

    total_number_of_virtual_circuit_requests = 0
    total_number_of_packets = 0
    number_of_successfully_routed_packets = 0
    number_of_blocked_packets = 0
    number_of_hops = 0
    cumulative_propagation_delay = 0


    with open(workload_file) as file:
        for line in file:
            total_number_of_virtual_circuit_requests += 1
            block_flag = 0
            s = line.split()
            total_number_of_packets += int(packet_rate * float(s[3]))
            shortest_path = shortest_delay_path(dic_let_to_nb[s[1]], dic_let_to_nb[s[2]], Graph)
            now_interval = (float(s[0]), float(s[0]) + float(s[3]))
            temp_dic = {}
            for i in range(len(shortest_path) - 1):
                
                now_link = (shortest_path[i], shortest_path[i + 1])
                oppo_link = (shortest_path[i + 1], shortest_path[i])
                if now_link not in dic and oppo_link not in dic:
                    temp_dic[now_link] = now_interval
                elif now_link not in dic and oppo_link in dic:
                    n = 1
                    for time_interval in dic[oppo_link]:
                        if is_intersect(now_interval, time_interval):
                            n += 1

                    if n > Graph[shortest_path[i]][shortest_path[i + 1]][2]:
                        block_flag = 1
                        break
                    else:
                        temp_dic[oppo_link] = now_interval
                        
                elif now_link in dic:
                    n = 1
                    for time_interval in dic[now_link]:
                        
                        if is_intersect(now_interval, time_interval):
       
                            n += 1               
                    if n > Graph[shortest_path[i]][shortest_path[i + 1]][2]:

                        block_flag = 1
                        break
                    else:
                        temp_dic[now_link] = now_interval

            if block_flag == 1:
                number_of_blocked_packets += int(packet_rate * float(s[3]))
            else:
                number_of_successfully_routed_packets += int(packet_rate * float(s[3]))
                number_of_hops += len(shortest_path)
                for i in range(len(shortest_path) - 1):
                    cumulative_propagation_delay += Graph[shortest_path[i]][shortest_path[i + 1]][1]
                for link in temp_dic:
                    dic[link].append(temp_dic[link])
            



    print('total number of virtual circuit requests: ', total_number_of_virtual_circuit_requests)
    print('total number of packets: ', total_number_of_packets)
    print('number of successfully routed packets: ', number_of_successfully_routed_packets)
    print('percentage of successfully routed packets: {:5.2f}'.format((number_of_successfully_routed_packets /
                                                                      total_number_of_packets) * 100 ))
    print('number of blocked packets: ', number_of_blocked_packets)
    print('percentage of blocked packets: {:5.2f}'.format((number_of_blocked_packets /
                                                          total_number_of_packets) * 100))
    print('average number of hops per circuit: {:5.2f}'.format(number_of_hops / total_number_of_virtual_circuit_requests))
    print('average cumulative propagation delay per circuit: {:5.2f}'.format(cumulative_propagation_delay /
                                                                             total_number_of_virtual_circuit_requests))



def shortest_loaded_circuit():
    count = 0
    dic = defaultdict(list)
    total_number_of_virtual_circuit_requests = 0
    total_number_of_packets = 0
    number_of_successfully_routed_packets = 0
    number_of_blocked_packets = 0
    number_of_hops = 0
    cumulative_propagation_delay = 0

    with open(workload_file) as file:
        for line in file:
            count += 1
            total_number_of_virtual_circuit_requests += 1
            block_flag = 0
            s = line.split()
            total_number_of_packets += int(packet_rate * float(s[3]))
            all_path = find_all_path(dic_let_to_nb[s[1]], dic_let_to_nb[s[2]], Graph)
            shortest_path = find_least_loaded_path(all_path, float(s[0]), dic)
#            print(shortest_path)

            now_interval = (float(s[0]), float(s[0]) + float(s[3]))
#            print(now_interval)
            temp_dic = {}

            for i in range(len(shortest_path) - 1):
                now_link = (shortest_path[i], shortest_path[i + 1])
                oppo_link = (shortest_path[i + 1], shortest_path[i])

                if (len(dic[now_link]) == 0) and (len(dic[oppo_link]) == 0):
                    temp_dic[now_link] = now_interval
                elif (len(dic[now_link]) == 0) and len(dic[oppo_link]) != 0:
                    n = 1
                    for time_interval in dic[oppo_link]:
                        if is_intersect(now_interval, time_interval):
                            n += 1
                    
                    if n > Graph[shortest_path[i]][shortest_path[i + 1]][2]:
                        block_flag = 1
                        break
                    else:
                        temp_dic[oppo_link] = now_interval
                        
                elif len(dic[now_link]) != 0:
                    n = 1
                    for time_interval in dic[now_link]:
                        
                        if is_intersect(now_interval, time_interval):
                            n += 1
                        
                    if n > Graph[shortest_path[i]][shortest_path[i + 1]][2]:
                        block_flag = 1
                        break
                    else:
                        temp_dic[now_link] = now_interval


            if block_flag == 1:
                number_of_blocked_packets += int(packet_rate * float(s[3]))
                
            else:
                number_of_successfully_routed_packets += int(packet_rate * float(s[3]))
                number_of_hops += len(shortest_path)
                for i in range(len(shortest_path) - 1):
                    cumulative_propagation_delay += Graph[shortest_path[i]][shortest_path[i + 1]][1]
                for link in temp_dic:

                    dic[link].append(temp_dic[link])

    print('total number of virtual circuit requests: ', total_number_of_virtual_circuit_requests)
    print('total number of packets: ', total_number_of_packets)
    print('number of successfully routed packets: ', number_of_successfully_routed_packets)
    print('percentage of successfully routed packets: {:5.2f}'.format((number_of_successfully_routed_packets /
                                                                      total_number_of_packets) * 100 ))
    print('number of blocked packets: ', number_of_blocked_packets)
    print('percentage of blocked packets: {:5.2f}'.format((number_of_blocked_packets /
                                                          total_number_of_packets) * 100))
    print('average number of hops per circuit: {:5.2f}'.format(number_of_hops / total_number_of_virtual_circuit_requests))
    print('average cumulative propagation delay per circuit: {:5.2f}'.format(cumulative_propagation_delay /
                                                                             total_number_of_virtual_circuit_requests))

if routing_scheme == 'SHP':
    shortest_hop_circuit()
    
elif routing_scheme == 'SDP':
    shortest_delay_circuit()

elif routing_scheme == 'LLP':
    shortest_loaded_circuit()


