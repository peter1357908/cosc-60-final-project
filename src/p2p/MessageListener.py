#! /usr/bin/python3

# Message Listener Thread:

import threading
import File
import FileInfoTable
import sys
sys.path.append('../mrt/')
sys.path.append('../data-structures/')
from mrt import *
#import SNode_helpers

class MessageListener(threading.Thread):

    # Initialize MessageListener Thread
    # TODO: Add paramaters as arguments are determined
    def __init__(self, mainListener, connID):
        print("Message Listener Instantiated")
        threading.Thread.__init__(self)
        # Main Listener 
        self.mainListener = mainListener
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

    # TODO: run() method:
    def run(self):

        print("Message Listener running.")
        while True:
            
            # Accept a packet from the current connID
            packet = mrt_receive1(self.connID)            
            print(packet)
            # Parse out the packet packets:
            # Grab the data included in the message headers
            messageType = packet[0:4].decode()
            messageLen = int(packet[4:8])
            receive_ip = packet[8:20].decode()
            port = int(packet[20:25].decode())
            ipAddr = (receive_ip,port)            
            
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
                    childHash.addFile(receive_ip, file_id)
                elif postType == '000b':    # If the messages announces a disconnect
                    # Note: a child node will never receive this message, since
                    # our network is a "structured" p2p network
                    # TODO: Make sure that the Child hash actually takes in an ip and again, rename to self.CHild etc.
                    child_files = childHash.popChild(ip)
                    fInfo.removeAllFileInfoByOfferer(child_files, ip_addr)
                    self.processDisconnect(ip)
            elif messageType == '0101':    # If the message is a request:
                print(f'request received')
                requestType = msg[25:29].decode()
                misc = msg[29:33]
                if requestType == '000a':
                    rMisc = misc.decode()
                    self.sendID=mrt_connect(ip=source_ip,port=port)
                    print(f'request to join received... type: {misc}')
                    # join as a regular node
                    if rMisc == '0000':

                        #TODO: VLADO PLEASE REVIEW THIS CHUNK AND DECIDE IF YOU WANT IT OR NOT
                        responseType = '100a'
                        snodesNum = str(len(supernode_list)) # TODO: rename to whatever it should be
                        msg = snodesNum + str(supernode_list)#Remove first and last char of list upon receiving
                        response = responseType + myAddr + str(len(msg))+msg
                        childHash = {}
                        childrenHash.addChild(receive_ip, childHash)

                        #TODO: I think we just need to pass everything up one level here VLADO/PETER PLEASE CONFIRM AND COMPLETE
                    # join as a supernode
                    elif r_misc == '0001':

                        pass
                    # relayed supernode
                    elif r_mis == '0002':
                        pass
                elif requestType == '000b':
                    #TODO: Request for a supernode's supernode list
                    self.manager.handleSupernodeListRequest(receive_ip,port,) 
                # file transfer
                elif requestType == '000e':
                    end_of_id = 29+int(misc)
                    file_id = msg[29:end_of_id]
                    offerer_ipv4 = msg[end_of_id:end_of_id+12]
                    offerer_port = msg[end_of_id+12:end_of_id+17]

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