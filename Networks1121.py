import queue
import threading
import math

# Why is it not working at the end, meaning why does the frgment list not have the first fragment?


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
        self.mtu = None

    ##get packet from the queue interface
    def get(self):
        try:
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
    header_length = dst_addr_S_length + general_length*2

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
        fragmentId = 0 # initial fragmentID
        count = 0 # counting the number of letters than can fit in a message in a packet
        array_count = 0
        array_buffer = [] # temp array for message
        packet_array = [] # array that has all information to make a packet

        loopCount = 0
        for letter in bytes_packet:

            count += 1
            array_buffer.append(letter)

            # if array_buffer (count) exceeds MTU or we are on the last index of bytes_packet in array_buffer:
            # to check if we are on the last index, I check the index of the current letter in the for loop,
            # and I start the index check from the current position of the loop using loopCount, and I check
            # if it is indeed the last letter in the loop
            if count == (MTU - self.header_length) or bytes_packet.index(letter, loopCount) == len(bytes_packet) - 1 : # index 0 - 34

                packet_array.append(str(destination).zfill(self.dst_addr_S_length)) # destination
                packet_array.append(str(self.datagramId).zfill(self.general_length)) # datagramId
                packet_array.append(str(fragmentId).zfill(self.general_length)) # fragmentId
                packet_array.append(array_buffer) # data
                fragmentId += 1

                if count == (MTU - self.header_length): # do additional things if count exceeds MTU
                    count = 0
                    array_count += 1
                    array_buffer = []

            loopCount += 1

        self.datagramId += 1 # increment for next datagram. (global var)
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

        Message_Length_No_Header = len(data_S)
        p = NetworkPacket(dst_addr, data_S, None)
        bytes_to_compute_length = p.to_byte_S()

        packet = NetworkPacket.from_byte_S(bytes_to_compute_length)
        destination = packet.dst_addr

        if packet.length is not None:
            if packet.length > self.out_intf_L[0].mtu:
                bytes_to_compute_length = bytes_to_compute_length[5:] # remove extra destination

                packet_array = NetworkPacket.split_packet(bytes_to_compute_length, self.out_intf_L[0].mtu, destination)
                print("Initial packet_array: ", packet_array)


                loopRounds = 0 # determine how many loops I need from the length of message

                if Message_Length_No_Header % self.out_intf_L[0].mtu == 0:
                    loopRounds = Message_Length_No_Header/self.out_intf_L[0].mtu
                else:
                    loopRounds = math.ceil(Message_Length_No_Header/self.out_intf_L[0].mtu)

                while(True):
                    loopRounds2 = math.ceil((Message_Length_No_Header + (NetworkPacket.header_length * loopRounds))/self.out_intf_L[0].mtu)

                    if loopRounds == loopRounds2:
                        break
                    else:
                        loopRounds = loopRounds2

                print("Loop Number: ", loopRounds)
                print("Loop Rounds2: ", loopRounds2)
                print("loopRounds*4: ", loopRounds*4)
                print("length: ", len(packet_array))
                print("packet_array: ", packet_array)

                for i in range(3, loopRounds*4, 4): # FOR LOOP for each fragmentId

                    print("I: ", i)
                    print("Packet Array[i]: ", packet_array[i])
                    packet_array[i] = "".join(packet_array[i])
                    string_message = "".join(packet_array[i-3:i+1])
                    print("Stringggg:", string_message)
                    send_packet = NetworkPacket.from_byte_S(string_message)
                    self.out_intf_L[0].put(send_packet.to_byte_S())

            else:
                self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully NO SEG

    ## receive packet from the network layer
    def udt_receive(self, l, datagramId_receive):

        list_empty = False
        fragment = ""


        pkt_S = self.in_intf_L[0].get()


        if pkt_S is not None:
            print("pkts : s",pkt_S)
            datagramId = pkt_S[NetworkPacket.dst_addr_S_length:NetworkPacket.dst_addr_S_length + NetworkPacket.general_length]
            fragmentId = pkt_S[NetworkPacket.dst_addr_S_length + NetworkPacket.general_length:NetworkPacket.dst_addr_S_length + NetworkPacket.general_length + NetworkPacket.general_length]

            if datagramId == datagramId_receive: # if we receive 2 or more fragments of the same datagram
                print("WORKS...")
                # reassemble
                fragment = pkt_S[NetworkPacket.header_length-1:] # message content slice from index header_length - 1

            else:
                list_empty = True
                datagramId_receive = datagramId

            print('%s: received packet "%s" on the in interface' % (self, pkt_S))

            return datagramId, list_empty, fragment

        else:
            return None, None, None

    ## thread target for the host to keep receiving data
    def run(self):

        print (threading.currentThread().getName() + ': Starting')
        fragment_list = []
        datagramId_receive = ""

        while True: #receive data arriving to the in interface

            datagramId_receive, empty, fragment = self.udt_receive(fragment_list, datagramId_receive)

            if datagramId_receive is not None or empty is not None or fragment is not None:
                print("Fragmentt: ", fragment)
                fragment_list.append(fragment)
                print("FR: ", fragment_list)

                if empty is True:
                    print("Datagram: ", fragment_list)
                    fragment_list = []



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
