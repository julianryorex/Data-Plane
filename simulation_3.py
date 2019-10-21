'''
Created on Oct 12, 2016

@author: mwittie
'''
import network_3
import link
import threading
from time import sleep

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 1 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads

    #create network nodes
    host1 = network_3.Host(1)
    object_L.append(host1)
    host2 = network_3.Host(2)
    object_L.append(host2)
    router_a = network_3.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)
    ben = network_3.Host(3)
    object_L.append(ben)
    julian = network_3.Host(4)
    object_L.append(julian)
    router_b = network_3.Router(name='B', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_b)
    router_c = network_3.Router(name='C', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_c)
    router_d = network_3.Router(name='D', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_d)

    #create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)

    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    link_layer.add_link(link.Link(host1, 0, router_a, 0, 50))
    link_layer.add_link(link.Link(host2, 0, router_a, 0, 50))
    link_layer.add_link(link.Link(router_a, 0, router_b, 0, 50))
    link_layer.add_link(link.Link(router_a, 0, router_c, 0, 50))
    link_layer.add_link(link.Link(router_b, 0, router_d, 0, 50))
    link_layer.add_link(link.Link(router_c, 0, router_d, 0, 50))
    link_layer.add_link(link.Link(router_d, 0, ben, 0, 50))
    link_layer.add_link(link.Link(router_d, 0, julian, 0, 50))

    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=host1.__str__(), target=host1.run))
    thread_L.append(threading.Thread(name=host2.__str__(), target=host2.run))
    thread_L.append(threading.Thread(name=ben.__str__(), target=ben.run))
    thread_L.append(threading.Thread(name=julian.__str__(), target=julian.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))


    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()


    #create some send events
    for i in range(3):#here we configure the message
        host1.udt_send(3, 'Sample data Mmm %d' % i)


    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")



# writes to host periodically
