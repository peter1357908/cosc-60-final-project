#! /usr/bin/python3

# Message Listener Thread:
import threading
import File
import FileInfoTable
import sys
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
    def __init__(self, mainListener, connID):
        print("Message Listener Instantiated")
        threading.Thread.__init__(self)
        # Main Listener 
        # Connection ID
        self.connID = connID
        self.sendID = 0

        self.manager = mainListener 

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
                postType = packet[25:29].decode()
                if postType == '000a':   # If the message announces a new file
                    # TODO: parse out necessary info for the file list (usually a list with 1 file)
                    fileSize = int(packet[29:33])
                    fileIDLength = int(packet[33:37])
                    fileID = packet[37:37+fileIDLength].decode()
                    self.manager.handleFilePost(sourceIP, sourcePort, fileID, fileSize)
                    print(f'file post.... fsize: {fileSize}, fid_len: {fileIDLength}, fid: {fileID}')
                elif postType == '000b':    # If the messages announces a disconnect
                    self.manager.handleRequestDisconnect(sourceIP, sourcePort, connID)
                    return # terminate this MessageListener thread
                    

            # REQUEST
            elif messageType == '0101':
                print(f'request received')
                requestType = packet[25:29].decode()
                misc = packet[29:33].decode()
                if requestType == '000a':
                    print(f'request to join received... type: {misc}')
                    # need to connect back to the childnode to send stuff
                    print(f"trying to connect to {splitIP(sourceIP)}:{sourcePort}")
                    sendID = mrt_connect(host=splitIP(sourceIP), port=int(sourcePort))
                    print("request: connected back to childnode")
                    # join as a regular node
                    if misc == '0000':
                        self.manager.handleJoinRequest(0, sendID, sourceIP, sourcePort)
                    # join as a supernode
                    elif misc == '0001':
                        self.manager.handleJoinRequest(1, sendID, sourceIP, sourcePort)
                    # relayed supernode
                    elif misc == '0002':
                        self.manager.handleJoinRequest(2, sendID, sourceIP, sourcePort)
                    
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
