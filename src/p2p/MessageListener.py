#! /usr/bin/python3

# Message Listener Thread:
import threading
import File
import FileInfoTable
import sys
import time
sys.path.append("../mrt/")
sys.path.append('../data-structures/')
from mrt import *

# helper function for converting 12-byte IP for P2P into dot-delimited IP
def splitIP(ip):
    ip_split = [int(ip[i:i+3]) for i in range(0, len(ip), 3)]
    return ".".join([str(x) for x in ip_split]) 

class MessageListener(threading.Thread):

    # Initialize MessageListener Thread
    # TODO: Add paramaters as arguments are determined
    def __init__(self, mainListener, recvID):
        print("Message Listener Instantiated")
        threading.Thread.__init__(self)
        # Main Listener 
        self.recvID = recvID

        self.manager = mainListener 

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
                sourcePort = packet[20:25].decode()
                
                # POST
                if messageType == '0001':    # If the message is a post:
                    print('POST type received')
                    postType = packet[25:29].decode()
                    if postType == '000a':   # If the message announces a new file
                        # TODO: parse out necessary info for the file list (usually a list with 1 file)
                        fileSize = int(packet[29:33])
                        fileIDLength = int(packet[33:37])
                        fileID = packet[37:37+fileIDLength].decode()
                        self.manager.handleFilePost(sourceIP, sourcePort, fileID, fileSize)
                        print(f'POST offer 000a type; file post.... fsize: {fileSize}, fid_len: {fileIDLength}, fid: {fileID}')
                    elif postType == '000b':    # If the messages announces a disconnect
                        print(f'POST disconnect 000b, {splitIP(sourceIP)}:{sourcePort} would like to disconnect')
                        self.manager.handleDisconnectPost(sourceIP, sourcePort)
                        return

                    elif postType == '100b':
                        print(f'POST disconnect 100b response received')
                        print("You can safely disconnect")

                # REQUEST
                elif messageType == '0101':
                    print(f'REQUEST type received')
                    requestType = packet[25:29].decode()
                    misc = packet[29:33].decode()

                    # Request to join the network:
                    if requestType == '000a':
                        print(f'REQUEST 000a to join received... type: {misc}')
                        print(f'trying to connect to {sourceIP}:{sourcePort}')
                        # TODO: make this connection attempt non-blocking / timeout?
                        sendID = mrt_connect(host=splitIP(sourceIP), port=int(sourcePort))
                        print("This is the sendID" + str(sendID))
                        print("connection succeeded")
                        self.manager.handleJoinRequest(int(misc), sendID, sourceIP, sourcePort)
                    
                    # Request for a supernode's supernode set:
                    elif requestType == '000b':
                        print(f'REQUEST 000b for supernode set received')
                        self.manager.handleSupernodeSetRequest(sourceIP, sourcePort)

                    # Request for a supernode's Local-DHT entries (on all files / one file):
                    elif requestType == '000c':
                        print(f'REQUEST 000c for local DHT entries received')
                        fileIDLength = int(misc)
                        fileID = ''
                        if fileIDLength > 0:
                            fileIDIndex = 33
                            fileID = packet[fileIDIndex:fileIDIndex+fileIDLength].decode()
                        self.manager.handleLocalDHTEntriesRequest(sourceIP, sourcePort, fileID)
                    
                    # Request for all DHT entries (on all files / one file):
                    elif requestType == '000d':
                        print(f'REQUEST 000d for all DHT entries received')
                        fileIDLength = int(misc)
                        fileID = ''
                        if fileIDLength > 0:
                            fileIDIndex = 33
                            fileID = packet[fileIDIndex:fileIDIndex+fileIDLength].decode()
                        self.manager.handleAllDHTEntriesRequest(sourceIP, sourcePort, misc, fileID)

                    # TODO: put things in self.manager.handleFileTransferRequest()
                    # file transfer
                    elif requestType == '000e':
                        fileIDLength = int(misc)
                        fileIDIndex = 33
                        fileID = packet[fileIDIndex:fileIDIndex+fileIDLength].decode()
                        offererIPv4Index = fileIDIndex + fileIDLength
                        offererIPv4 = packet[offererIPv4Index:offererIPv4Index+12].decode()
                        offererPortIndex = offererIPv4Index + 12
                        offererPort = packet[offererPortIndex:offererPortIndex+5].decode()
                        maintainerIPv4Index = offererPortIndex + 5
                        maintainerIPv4 = packet[maintainerIPv4Index:maintainerIPv4Index+12].decode()
                        maintainerPortIndex = maintainerIPv4Index + 12
                        maintainerPort = packet[maintainerPortIndex:maintainerPortIndex+5].decode()
                        print(f'REQUEST 000e for file transfer request received from {splitIP(sourceIP)}:{sourcePort} \
                            maintained by {splitIP(offererIPv4)}:{offererPort}, offered by {splitIP(maintainerIPv4)}:{maintainerPort}')

                        if offererIPv4 == self.manager.ownIP and offererPort == self.manager.ownPort:
                            print("I host the file myself!")
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
                                    
                                    self.manager.handleFileTransfer(sourceIP,sourcePort, current_part,fileID,eof=True)
                                    # Exit out of the while loop
                                    break
                                self.manager.handleFileTransfer(sourceIP,sourcePort,current_part,fileID)
                                time.sleep(1)
                            file_to_send.close()
 
                        else:
                            print("forwarding file request...")
                            self.manager.forwardFileTransferRequest(sourceIP, sourcePort, offererIPv4, offererPort, maintainerIPv4, maintainerPort, misc, fileID)


                    # response from request to join 000a or request for supernodeSet
                    elif requestType == '100a':
                        print("RequestType 100a received!")
                        num_supernode_entries = int(misc)
                        cur_idx = 33
                        print(f"number of supernode entries is {num_supernode_entries}")
                        for i in range(num_supernode_entries):
                            try:
                                snodeIP = packet[cur_idx:cur_idx+12].decode()
                                cur_idx += 12
                                snodePort = packet[cur_idx:cur_idx+5].decode()
                                cur_idx += 5
                                print(f"100a; SUPERNODE at {splitIP(snodeIP)}:{snodePort}")
                            except IndexError as e:
                                print("100a received, cannot index supernode ip, port, index out of bounds")
                        self.manager.handleSupernodeSetRequestResponse(packet[29:25+messageLen].decode())

                    # response from request to get local DHT
                    elif requestType == '100c':
                        print("RequestType 100c received!")
                        pass
                        # This stuff is just pretty print for the user
                        num_DHT_entries = int(misc)
                        cur_idx = 33

                        # for each local DHT entry
                        for i in range(num_DHT_entries):
                            # see Protocol.md
                            print(f"*** request type 100c - LOCAL DHT entry number {i+1}: ***")
                            file_id_length = int(packet[cur_idx:cur_idx + 4].decode())
                            cur_idx += 4

                            file_id = packet[cur_idx:cur_idx + file_id_length].decode()
                            cur_idx += file_id_length

                            print(f"---- fileID : {file_id}")

                            num_file_entries = int(packet[cur_idx:cur_idx +4])
                            cur_idx += 4
                            # for each file entry
                            for j in range(num_file_entries):
                                offerer_ip = packet[cur_idx:cur_idx+12].decode()
                                cur_idx += 12
                                offerer_port = packet[cur_idx:cur_idx+5].decode()
                                cur_idx += 5
                                file_size = packet[cur_idx:cur_idx+4].decode()
                                cur_idx += 4
                                print(f"    -- {splitIP(offerer_ip)}:{offerer_port}, size: {file_size}")
                        print(packet[29:25+messageLen])
                        self.manager.handleLocalDHTEntriesRequestResponse(packet[29:25+messageLen].decode(), sourceIP, sourcePort)

                    # response from request to get entire DHT
                    elif requestType == '100d':
                        print('RequestType 100d received!')
                        pass


                # FILE TRANSFER
                elif messageType == '1111':
                    print("FILE TRANSFER 1111 received")
                    fileIDIndex = 33
                    fileIDLength = int(packet[29:33])
                    fileID = packet[fileIDIndex:fileIDIndex + fileIDLength].decode()
                    chunk_size_index = fileIDIndex + fileIDLength
                    chunk_size = int(packet[chunk_size_index:chunk_size_index+4])
                    data = packet[chunk_size_index+4:chunk_size_index+ 4 + chunk_size].decode()

                    with open(fileID,'a+') as infile:
                        infile.write(data)

                        print(f'Writing data to {fileID}')



                #update packet because this is stream based
                print(f'last packet = {packet[:25+messageLen]}\n\n\n')
                print(f'new paket = {packet[25+messageLen:]}\n\n\n')
                packet = packet[25+messageLen:]

        # outside While loop; clean-ups?


