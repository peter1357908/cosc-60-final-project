#! /usr/bin/python3

# Message Listener Thread:
import threading
import File
import FileInfoTable
import sys
sys.path.append("../mrt/")
sys.path.append('../data-structures/')
from mrt import *


class MessageListener(threading.Thread):

    # Initialize MessageListener Thread
    # TODO: Add paramaters as arguments are determined
    def __init__(self, mainListener, connID):
        print("Message Listener Instantiated")
        threading.Thread.__init__(self)
        # Main Listener 
        # Connection ID
        self.connID = connID
        self.sendID = 0

        self.manager = mainListener
    

    # Methods for handling each parsed method:
    # A note on the following methods: 'file' is always a File object
    # and 'files' is an array of File objects

    def setSendID(self, ID):
        self.sendID = ID

    # Accept a new connection
    def acceptConnection(self, connectedIP):
        #TODO: Add the connected IP to the list of child nodes
        pass
        

    # Accept a new supernode connection. This message will only be received by supernodes
    def acceptSupernodeConnection(self, connectedIP):
        #TODO: add the connected IP to the list of connected supernodes
        pass

    # Process a child node disconnecting. Currently, supernodes cannot disconnect without 
    # Shutting down the network.
    def processDisconnect(self, disconnectedIP):
        # TODO: remove the disconnected IP from the list of child nodes
        # Also remove the files offered by disconnectedIP from HT
        pass

    # Add a list of File objects to the HT:
    def addFiles(self, files):
        # TODO: For every file in files, add that file to the HT & print a debug statement
        pass
    
    # Remove a list of File objects from the HT:
    def removeFiles(self, files):
        # TODO: For every file in files, remove file from the HT
        pass

    # Send back local-DHT
    def sendBackHT(self, destinationIP):
        # TODO: Craft Requests for Local DHT's from all the supernodes
        # TODO: Receive the Local DHT's
        # TODO: Put them into packets
        # TODO: Send those packets to the requesting node
        pass
        
    def sendBackLocalHT(self, destinationIP):
        pass
    
    # Accept the request for upload from another client and start sending the file
    def acceptUpload(self, file, destinationIP):
        fileSender = FileSender(file, destinationIP)
        fileSender.start()
        pass
    
    # When a download message is received but the destination is not the current node
    # pass on the packet to the appropriate node:
    def passOn(self, destinationIP):
        # TODO: pass on & figure out a way to do so.
        # If the current node is not the supernode of the destination, 
            # pass on the packet to the supernode of that packet
        # Else, if the current node is that child node's (dest.) supernode
            # pass on the packet to the destination.
        pass
        
    def sendBackSupernodeList(self, destinationIP):
        # TODO: Create message to send back supernode list
        # TODO: Send message
        pass



    def splitIP(self, ip):
        ip_split = [int(ip[i:i+3]) for i in range(0, len(ip), 3)]
        return ".".join([str(x) for x in ip_split])   




    # TODO: run() method:
    def run(self):
        print("MessageListener started...")

        while True:    
            # Accept a packet from the current connID
            packet = mrt_receive1(self.connID)            
            print(packet)
            # Parse the packet:
            # Grab the data included in the message headers
            messageType = packet[0:4].decode()
            messageLen = int(packet[4:8].decode())
            sourceIP = packet[8:20].decode()
            sourcePort = int(packet[20:25].decode())
            sourceAddrTuple = (sourceIP, sourcePort)
            
            # POST 
            if messageType == '0001':    # If the message is a post:
                # TODO: Now, parse the Post Type:
                postType = packet[25:29].decode()
                if postType == '000a':   # If the message announces a new file
                    # TODO: parse out necessary info for the file list (usually a list with 1 file)
                    fileSize = int(packet[29:33])
                    fileIDLength = int(packet[33:37])
                    fileID = packet[37:37+fileIDLength].decode()
                    # self.manager.handlePostFile()
                    print(f'file post.... fsize: {fileSize}, fid_len: {fileIDLength}, fid: {fileID}')
                    fInfo.addFileInfo(file_id.decode(),ip_addr,file_size.decode()) # TODO: Find the actual name for these
                    childHash.addFile(sourceIP, file_id)
                elif postType == '000b':    # If the messages announces a disconnect
                    # Note: a child node will never receive this message, since
                    # our network is a "structured" p2p network
                    # TODO: Make sure that the Child hash actually takes in an ip and again, rename to self.CHild etc.
                    child_files = childHash.popChild(ip)
                    fInfo.removeAllFileInfoByOfferer(child_files, ip_addr)
                    self.processDisconnect(ip)

            # REQUEST
            elif messageType == '0101':
                print(f'request received')
                requestType = packet[25:29].decode()
                misc = packet[29:33].decode()
                if requestType == '000a':
                    print(f'request to join received... type: {misc}')
                    # need to connect back to the childnode to send stuff
                    print(f"trying to connect to {self.splitIP(sourceIP)}:{sourcePort}")
                    send_id = mrt_connect(host=self.splitIP(sourceIP), port=int(sourcePort))
                    print("request: connected back to childnode")
                    # join as a regular node
                    if misc == '0000':
                        self.manager.handleJoinRequest(0, send_id, sourceIP, sourcePort)
                         
                    # join as a supernode
                    elif r_misc == '0001':

                        pass
                    # relayed supernode
                    elif r_mis == '0002':
                        pass
                         
                    # join as a supernode
                    elif r_misc == '0001':

                        pass
                    # relayed supernode
                    elif r_mis == '0002':
                        pass
                         
                    # join as a supernode
                    elif r_misc == '0001':

                        pass
                    # relayed supernode
                    elif r_mis == '0002':
                        pass
                         
                    # join as a supernode
                    elif r_misc == '0001':

                        pass
                    # relayed supernode
                    elif r_mis == '0002':
                        pass
                         
                    # join as a supernode
                    elif r_misc == '0001':

                        pass
                    # relayed supernode
                    elif r_mis == '0002':
                        pass
                         
                    # join as a supernode
                    elif r_misc == '0001':

                        pass
                    # relayed supernode
                    elif r_mis == '0002':
                        pass
                         
                    # join as a supernode
                    elif r_misc == '0001':

                        pass
                    # relayed supernode
                    elif r_mis == '0002':
                        pass
                elif requestType == '000b':
                    #TODO: Request for a supernode's supernode list
                    #self.manager.handleSupernodeListRequest(sourceIP,port,) 
                    pass
                # file transfer
                elif requestType == '000e':
                    end_of_id = 29+int(misc)
                    file_id = packet[29:end_of_id]
                    offerer_ipv4 = packet[end_of_id:end_of_id+12]
                    offerer_port = packet[end_of_id+12:end_of_id+17]

                    if offerer_ipv4 == self.manager.ownIP and offerer_port == self.manager.ownPort:
                        #TODO: load file and sent (or pass to manager to handle this)
                        #1. Open file
                        file_to_send = open(file_id, 'a+')
                        byte_size = file.tell()
                        # puts the cursor back at tbeginning
                        #3. Split into smaller fragments and loop using mrt_send1() until sent
                        # The current fragment size is maxxed at 1024 bytes.
                        if (byte_size%1024 == 0):
                            #append a " " to the end of file
                            file_to_send.write(' ')
                        file_to_send.seek(0,0) #send back to start for reading
                        total_fragments = int((byte_size / 1024)) + 1
                        # Loop using mrt_send1()
                        while True: 
                            # Read in the file_to_send into a 1024 byte buffer
                            current_part = file_to_send.read(1024)
                            # Send the packet using mrt_send1()
                            # If the end of the file is reached:
                            if len(current_part) < 1024:
                                # Send it off using mrt_send1
                                # TODO: need to format this as a file transfer messages
                                mrt_send1(self.sendID, current_part)

                                # Exit out of the while loop
                                break
                            mrt_send1(self.sendID, current_part)
                        file_to_send.close()  



                    else: 
                        #TODO: pass message along to the correct childnode
                        #TODO: there should be a function in manager that will search through the childnodes and then 
                        # relay message to them 
                        self.manager.handleRelayRequest(self.connID, offerer_ipv4, offerer_port, file_id)
