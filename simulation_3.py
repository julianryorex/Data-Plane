import network_3
import link
import threading
from time import sleep

# configuration parameters
router_queue_size = 0  # 0 means unlimited
# give the network_3 sufficient time to transfer all packets before quitting
simulation_time = 10

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads
    #first tuple entry is output port, second address to forward to
    table_a = [(2, 3), (3, 4)]
    table_b = [(1,3)]
    table_c = [( 1, 4)]
    table_d = [(2, 3), (3, 4)]

    # create network_3 nodes
    host1 = network_3.Host(1)
    object_L.append(host1)
    host2 = network_3.Host(2)
    object_L.append(host2)
    router_a = network_3.Router(name='A', intf_count=4, max_queue_size=router_queue_size, forward_table = table_a)
    host3 = network_3.Host(3)
    object_L.append(host3)
    host4 = network_3.Host(4)
    object_L.append(host4)
    router_b = network_3.Router(name='B', intf_count=2, max_queue_size=router_queue_size, forward_table = table_b)
    object_L.append(router_b)
    router_c = network_3.Router(name='C', intf_count=2, max_queue_size=router_queue_size, forward_table = table_c)
    object_L.append(router_c)
    router_d = network_3.Router(name='D', intf_count=4, max_queue_size=router_queue_size, forward_table = table_d)
    object_L.append(router_d)

    # create a Link Layer to keep track of links between network_3 nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)

    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    link_layer.add_link(link.Link(host1, 0, router_a, 0, 50))
    link_layer.add_link(link.Link(host2, 0, router_a, 1, 50))
    link_layer.add_link(link.Link(router_a, 2, router_b, 0, 50))
    link_layer.add_link(link.Link(router_a, 3, router_c, 0, 50))
    link_layer.add_link(link.Link(router_b, 1, router_d, 0, 50))
    link_layer.add_link(link.Link(router_c, 1, router_d, 1, 50))
    link_layer.add_link(link.Link(router_d, 2, host3, 0, 50))
    link_layer.add_link(link.Link(router_d, 3, host4, 0, 50))

     #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=host1.__str__(), target=host1.run))
    thread_L.append(threading.Thread(name=host2.__str__(), target=host2.run))
    thread_L.append(threading.Thread(name=host3.__str__(), target=host3.run))
    thread_L.append(threading.Thread(name=host4.__str__(), target=host4.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))


    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()


    #create some send events
    for i in range(1):#here we configure the message
        #host2.udt_send(4, 'Sample data Mmm %d' % i)
        host1.udt_send(3, 'Sample data Mmm %d' % i)


    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")
