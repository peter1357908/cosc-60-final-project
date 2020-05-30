# This is the code for the InputListener Thread:

import threading
import asyncio
import sys
sys.path.append('../mrt/')
sys.path.append('../data-structures/')
import mrt
from FileInfoTable import *
from ChildrenInfoTable import *
import CNode_helper
import os

class InputListener(threading.Thread):

    # Initialize InputListener Thread
    # TODO: Add paramaters as arguments are determined
    def __init__(self,main_listener,ownIP, ownPort, sendID, isSupernode):
        threading.Thread.__init__(self)
        self.manager = main_listener
        self.ownIP = ownIP  # IP of supernode, 127.0.0.1 if is a supernode
        self.ownPort = ownPort
        self.sendID = sendID
        self.isSupernode = isSupernode
        # self.table = table # File Info Table
        # if supernodeIP == "127.0.0.1":
        #     self.childTable = ChildrenInfoTable()
        #     self.superList = []

    # Methods for handling each parsed case:
    # A note on the following methods: "file" is always a File Object.

    # Construct Request DHT packet and send to supernodeIP:
    def request_dht(self, filename,all_lists = False):
        # CNode_helper.requestDHT(all_dht)
        if len(filename) == 0:
            print("Requesting entire DHT")
        print("Requested DHT from ", self.supernodeIP)
        if all_lists:
            print("Requesting from all Supernodes")
            CNode_helper.request_global_dht(self.sendID, self.ownIP, self.ownPort,filename)
        else:
            CNode_helper.request_local_dht(self.sendID,self.ownIP,self.ownPort,filename)

    # Request list of supernodes
    def request_supernodes(self):
        # TODO
        # CNode_helper.request_super_list()
        print("requesting all the supernodes")
        CNode_helper.request_super_list(self.sendID,self.ownIP,self.ownPort)

    # Begin a download:
    def beginDownload(self, file, downloadIP,downloadPort):
        # downloader = Downloader(self.supernodeIP, downloadIP, file)
        # downloader.start()
        print("Attempting to download from ", downloadIP)
        transfer_id = CNode_helper.request_file(self.sendID,self.ownIP,self.ownPort,file,downloadIP,downloadPort)

        # Start download:
        # constantly receive 1?
        new_file = open(file,'a+')
        data = mrt_receive1(transfer_id).decode()
        new_file.write(data)
        while len(data) >= 1024:
            data = mrt_receive1(transfer_id).decode()
            new_file.write(data)
        new_file.close()

        print(f'New file written to {file}')

        #TODO FIGURE OUT HOLE PUNCHING HERE
    
    # Offer a New File
    def offerNewFile(self, file):
        # TODO:
            # STILL NEED TO FIGURE OUT FILE SIZE ETC AS PARAMETERS
        # CNode_helper.post_file(file_size, id_size, filename)
        print("Announcing a new file is being offered: ", file)
        file_size = os.path.getsize(file)
        CNode_helper.post_file(self.sendID,self.ownIP,self.ownPort,file_size,len(file),file)
    
    # Announce a file is no longer being offered:
    def removeOfferedFile(self, file):
        # TODO:
        # need corresponding protocol message?
        print(f"{file} is no longer being offered")
    
    # Disconnect from the network:
    def disconnect(self):
        # CNode_helper.send_disconnect()
        print("Disconnected from the network. Goodbye!")
        CNode_helper.send_disconnect(self.sendID,self.ownIP,self.ownPort)

    # Return a stirng informing user about the usage
    def usage_statement(self):
        print("usage statement stub")
        pass


    # TODO: run() method of the listener: constantly listen for input and parse it out:
    # I Think SNode_helpers can 'help' with parsing and calling these methods
    def run(self):
        while True:
            # # If the command requires a file as an arg: 
            #     fileID = 'parsed'
            #     offerer = 'parsed'
            #     fileInfo = 'parsed'
            #     name = 'parsed'
            #     file = File(fileID, offerer, fileInfo, name)
            #     downloadIP = file.getOfferer()

            # Parse out user input
            user_input = input("> ")

            if not user_input:
                continue
            if user_input.isspace():
                continue

            # user input tokens are space delimited
            input_tks = user_input.split(" ")
            assert len(input_tks) > 0
            print(f"input tks are {input_tks}")
            if input_tks[0] == "req":
                assert len(input_tks) >= 2
                if input_tks[1] == "files":
                    # If input is request for information:
                    all_dht = False
                    if len(input_tks) >= 3 and input_tks[2] == "all":
                        all_dht = True
                    self.requestDHT(all_dht)
                elif input_tks[1] == "supernodes":
                    if not self.isSupernode:
                        self.request_supernodes()
                    else:
                        print(f'{self.manager.supernode_list}')
                elif input_tks[1] == "dl":
                    assert len(input_tks) >= 4
                    # Else if input is to begin a download:
                    file_id = input_tks[2]
                    # TODO: need to add validation for IP:port
                    file_host = input_tks[3].split(":")
                    file = None
                    downloadIP = None
                    self.beginDownload(downloadIP, file)
            elif input_tks[0] == "post":
                assert len(input_tks) >= 2

                if input_tks[1] == "offer":
                    assert len(input_tks) >= 3
                    # Else if input is to offer a new file:
                    file_id = input_tks[2]

                    if not self.isSupernode:
                        self.offerNewFile(file=None)
                    else: 
                        self.manager.handleFilePost(self.ownIP, self.ownPort, self.sendID, file_id, os.path.getsize(file_id))
                elif input_tks[1] == "rm":
                    assert len(input_tks) >= 3
                    file_id = input_tks[2]
                    self.removeOfferedFile(file=None)
                elif input_tks[1] == "disconnect":
                    # Else if input is to disconnect from the network
                    self.disconnect()

            else:
                print(f"command not recognized {input_tks[0]}")
                # Then, print out list of possible commmands:
                print(self.usage_statement())