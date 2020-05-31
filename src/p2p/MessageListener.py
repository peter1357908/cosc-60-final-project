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
            # Accept a packet from the current recvID
            packet = mrt_receive1(self.recvID)           

            while len(packet) > 0:
                # Parse the packet:
                # Grab the data included in the message headers
                messageType = packet[0:4].decode()
                messageLen = int(packet[4:8].decode())
                sourceIP = packet[8:20].decode()
                sourcePort = int(packet[20:25].decode())
                sourceAddrTuple = (sourceIP, sourcePort)
                
                # POST 
                if messageType == '0001':    # If the message is a post:
                    postType = packet[25:29].decode()
                    if postType == '000a':   # If the message announces a new file
                        # TODO: parse out necessary info for the file list (usually a list with 1 file)
                        fileSize = int(packet[29:33])
                        fileIDLength = int(packet[33:37])
                        fileID = packet[37:37+fileIDLength].decode()
                        self.manager.handleFilePost(sourceIP, sourcePort, fileID, fileSize)
                        print(f'file post.... fsize: {fileSize}, fid_len: {fileIDLength}, fid: {fileID}')
                    elif postType == '000b':    # If the messages announces a disconnect
                        self.manager.handleRequestDisconnect(sourceIP, sourcePort)
                        return # terminate this MessageListener thread
                        
                # REQUEST
                elif messageType == '0101':
                    print(f'request received')
                    requestType = packet[25:29].decode()
                    misc = packet[29:33].decode()

                    # Request to join the network:
                    if requestType == '000a':
                        print(f'request to join received... type: {misc}')
                        print(f'trying to connect to {splitIP(sourceIP)}:{sourcePort}')
                        # TODO: make this connection attempt non-blocking / timeout?
                        sendID = mrt_connect(host=splitIP(sourceIP), port=int(sourcePort))
                        print("connection succeeded")
                        self.manager.handleJoinRequest(int(misc), sendID, sourceIP, sourcePort)
                    
                    # Request for a supernode's supernode set:
                    elif requestType == '000b':
                        self.manager.handleSupernodeSetRequest(sourceIP, sourcePort)

                    # Request for a supernode's Local-DHT entries (on all files / one file):
                    elif requestType == '000c':
                        fileIDLength = int(misc)
                        fileID = ''
                        if fileIDLength > 0:
                            fileIDIndex = 33
                            fileID = packet[fileIDIndex:fileIDIndex+fileIDLength].decode()
                        self.manager.handleLocalDHTEntriesRequest(sourceIP, sourcePort, fileID)
                    
                    # Request for all DHT entrie (on all files / one file):
                    elif requestType == '000d':
                        fileIDLength = int(misc)
                        fileID = ''
                        if fileIDLength > 0:
                            fileIDIndex = 33
                            fileID = packet[fileIDIndex:fileIDIndex+fileIDLength].decode()
                        self.manager.handleAllDHTEntriesRequest(sourceIP, sourcePort, misc, fileID)

                    # file transfer
                    elif requestType == '000e':
                        fileIDLength = int(misc)
                        fileIDIndex = 33
                        fileID = packet[fileIDIndex:fileIDIndex+fileIDLength].decode()
                        OffererIPv4Index = fileIDIndex + fileIDLength
                        offererIPv4 = packet[OffererIPv4Index:OffererIPv4Index+12].decode()
                        OffererPortIndex = OffererIPv4Index + 12
                        offererPort = int(packet[OffererPortIndex:OffererPortIndex+5])
                        print(f'id: {fileID}, offererIP: {offererIPv4}, offererPort = {offererPort}')
                        if offererIPv4 == self.manager.ownIP and offererPort == int(self.manager.ownPort):
                            #TODO: load file and sent (or pass to manager to handle this)
                            #1. Open file
                            file_to_send = open(fileID, 'a+')
                            byte_size = file_to_send.tell()
                            # puts the cursor back at tbeginning
                            #3. Split into smaller fragments and loop by invoking handleFileRequest repeatedly until it's done
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
                                print(f'length of current read: {len(current_part)}\n')
                                # Send the packet using mrt_send1()
                                # If the end of the file is reached:
                                if len(current_part) < 1024:
                                    # Send it off using mrt_send1
                                    # TODO: need to format this as a file transfer messages
                                    
                                    self.manager.handleFileTransfer(sourceIP,sourcePort, current_part,fileID)


                                    # Exit out of the while loop
                                    break
                                
                                self.manager.handleFileTransfer(sourceIP,sourcePort,current_part,fileID)
                                time.sleep(1)
                            file_to_send.close()

                        else: 
                            #TODO: pass message along to the correct childnode
                            #TODO: there should be a function in manager that will search through the childnodes and then 
                            # relay message to them 
                            self.manager.handleRelayRequest(offerer_ipv4, offerer_port, file_id)

                elif messageType == '1111':
                    fileIDIndex = 33
                    fileIDLength = int(packet[29:33])
                    fileID = packet[fileIDIndex:fileIDIndex + fileIDLength].decode()
                    chunk_size_index = fileIDIndex + fileIDLength
                    chunk_size = int(packet[chunk_size_index:chunk_size_index+4])
                    data = packet[chunk_size_index+4:chunk_size_index+ 4 + chunk_size].decode()

                    with open(fileID,'a+') as infile:
                        infile.write(data)

                #update packet because this is stream based
                print(f'last packet = {packet[:25+messageLen]}\n\n\n')
                print(f'new paket = {packet[25+messageLen:]}\n\n\n')
                packet = packet[25+messageLen:]



