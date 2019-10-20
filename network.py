'''
Created on Oct 12, 2016

@author: mwittie
'''
import queue
import threading


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
        self.mtu = None

    ##get packet from the queue interface
    def get(self):
        try:
            print("Queue: ", self.queue.get(False))
            return self.queue.get(False)
        except queue.Empty:
            return None

    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)


## Implements a network layer packet (different from the RDT packet
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths
    dst_addr_S_length = 5
    general_length = 5
    datagramId = 0

    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S, length):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.length = length

    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()

    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return byte_S

    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        length = len(byte_S)
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length : ]

        return self(dst_addr, data_S, length)

    @classmethod
    def split_packet(self, bytes_packet, MTU, destination):
        fragmentId = 0
        count = 0
        array_count=0
        array_buffer = []
        packet_array = [] # array list
        for b in bytes_packet:
            print("Count: ", count)
            count = count + 1
            print("Type: " , type(b))
            print("B: ", b)
            array_buffer.append(b)

            if count >= MTU:
                packet_array.append(str(destination).zfill(self.dst_addr_S_length)) # destination
                packet_array.append(str(self.datagramId).zfill(self.general_length)) # datagramId
                packet_array.append(str(fragmentId).zfill(self.general_length)) # fragmentId
                packet_array.append(array_buffer) # data
                count = 0
                array_count += 1
                array_buffer = []
                fragmentId += 1



        # created an array of segmented packets
        self.datagramId += 1


        return packet_array


## Implements a network host for receiving and transmitting data
class Host:#segmentation also should be implemented in the client

    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False #for thread termination

    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)

    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):
        #need to split here ?
        p = NetworkPacket(dst_addr, data_S,None)
        bytes_to_compute_length = p.to_byte_S()
        # print("Bytes: " , bytes_to_compute_length)
        packet = NetworkPacket.from_byte_S(bytes_to_compute_length)
        destination = packet.dst_addr
        # print("Destination: ", destination)
        if packet.length is not None:
            if packet.length > self.out_intf_L[0].mtu:
                print("packet too big")#need to split
                packet_array = NetworkPacket.split_packet(bytes_to_compute_length,self.out_intf_L[0].mtu, destination)
                for packet in packet_array:
                    s = ""
                    p_string = s.join(packet)
                    pack = NetworkPacket.from_byte_S(p_string)
                    self.out_intf_L[0].put(pack.to_byte_S())
            else:
                self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully NO SEG
        print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

    ## receive packet from the network layer
    def udt_receive(self):

        pkt_S = self.in_intf_L[0].get()

        if pkt_S is not None:
            print('%s: received packet "%s" on the in interface' % (self, pkt_S))

    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return



## Implements a multi-interface router described in class
class Router:

    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self): #we need to change this method to implement fragmentation#MTU is in bytes
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                    # HERE you will need to implement a lookup into the
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i
                    if p.length is not None:
                        print(self.out_intf_L[i].mtu)
                        if p.length > self.out_intf_L[i].mtu:
                            print("e")
                            #split
                        for i in self.out_intf_L:
                            if self.out_intf_L[i].visited is False:
                                self.out_intf_L[i] = True
                                self.out_intf_L[i].put(p.to_byte_S(), True)
                                print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                                    % (self, p, i, i, self.out_intf_L[i].mtu))
                            else:
                                print('Error :(')
                    self.out_intf_L[i].put(p.to_byte_S(), True)
                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                        % (self, p, i, i, self.out_intf_L[i].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass

    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return
