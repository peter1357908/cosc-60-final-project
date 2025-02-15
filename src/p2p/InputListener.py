# This is the code for the InputListener Thread:

import threading
import asyncio
import sys
sys.path.append('../mrt/')
sys.path.append('../data-structures/')
from mrt import *
from FileInfoTable import *
from ChildrenInfoTable import *
from MainListener import *
import os
import CNode_helper

# helper function for converting 12-byte IP for P2P into dot-delimited IP
def splitIP(ip):
    ip_split = [int(ip[i:i+3]) for i in range(0, len(ip), 3)]
    return ".".join([str(x) for x in ip_split]) 

class InputListener(threading.Thread):
    def __init__(self, mainListener, ownIP, ownPort, bootstrapSendID, isSupernode):
        threading.Thread.__init__(self)
        self.manager = mainListener
        self.ownIP = ownIP
        self.ownPort = ownPort
        self.bootstrapSendID = bootstrapSendID
        self.isSupernode = isSupernode

    # Methods for handling each parsed case:
    # A note on the following methods: "file" is always a File Object.

    # Construct Request DHT packet and send to supernodeIP:
    def requestDHT(self, filename, isRequestingGlobalDHT):
        if isRequestingGlobalDHT:
            if self.isSupernode:
                # move this logic to MainListener
                with self.manager.supernodeSetLock:
                    with self.manager.addrToIDTableLock:
                        for supernodeAddr in self.supernodeSet.getSet():
                            targetSendID = self.manager.addrToIDTable[supernodeAddr]
                            CNode_helper.request_local_dht(targetSendID, supernodeAddr[0], supernodeAddr[1], filename)
            else:
                CNode_helper.request_global_dht(self.bootstrapSendID, self.ownIP, self.ownPort, filename)
        else:
            if self.isSupernode:
                # just print the local dht (copied from MessageListener; should move to MainListener)
                DHTString = str(self.manager.fileInfoTable)
                num_DHT_entries = int(DHTString[0:4])
                cur_idx = 4

                # for each local DHT entry
                for i in range(num_DHT_entries):
                    # see Protocol.md
                    print(f"*** request type 100c - LOCAL DHT entry number {i+1}: ***")
                    file_id_length = int(DHTString[cur_idx:cur_idx + 4])
                    cur_idx += 4

                    file_id = DHTString[cur_idx:cur_idx + file_id_length]
                    cur_idx += file_id_length

                    print(f"---- fileID : {file_id}")

                    num_file_entries = int(DHTString[cur_idx:cur_idx +4])
                    cur_idx += 4
                    # for each file entry
                    for j in range(num_file_entries):
                        offerer_ip = DHTString[cur_idx:cur_idx+12]
                        cur_idx += 12
                        offerer_port = DHTString[cur_idx:cur_idx+5]
                        cur_idx += 5
                        file_size = DHTString[cur_idx:cur_idx+4]
                        cur_idx += 4
                        print(f"    -- {splitIP(offerer_ip)}:{int(offerer_port)}, size: {file_size}")
            else:
                CNode_helper.request_local_dht(self.bootstrapSendID, self.ownIP, self.ownPort, filename)

    # Request list of supernodes
    def requestSupernodes(self):
        print("requesting all the supernodes")
        CNode_helper.request_super_set(
            self.bootstrapSendID, self.ownIP, self.ownPort)

    # Begin a download (input are all in P2P format):
    def beginDownload(self, fileID, maintainerIP, maintainerPort, offererIP, offererPort):
        CNode_helper.request_file(self.bootstrapSendID, self.ownIP, self.ownPort,
                                  fileID, maintainerIP, maintainerPort, offererIP, offererPort)
    
    # Offer a New File
    def offerNewFile(self, filename):
        print("Announcing a new file is being offered: ", filename)
        
        if not os.path.exists(filename):
            print(f"the file you've offered does not exist on your machine! -- {filename}")
        else:
            file_size = os.path.getsize(filename)
            
            CNode_helper.post_file(
                self.bootstrapSendID, self.ownIP, self.ownPort, file_size, len(filename), filename)
    
    # Announce a file is no longer being offered:
    def removeOfferedFile(self, filename):
        # TODO:
        # need corresponding protocol message?
        print(f"{filename} is no longer being offered")
    
    # Disconnect from the network:
    def disconnect(self):
        # CNode_helper.send_disconnect()
        print("Disconnected from the network. Goodbye!")
        CNode_helper.send_disconnect(
            self.bootstrapSendID, self.ownIP, self.ownPort)

    # Return a stirng informing user about the usage
    def usage_statement(self):
        print("usage statement stub")
        pass


    # TODO: run() method of the listener: constantly listen for input and parse it out:
    # I Think SNode_helpers can 'help' with parsing and calling these methods
    def run(self):
        print(f'InputListener started...')
        while True:
            # Parse out user input
            user_input = input("> ")

            if not user_input:
                continue
            if user_input.isspace():
                continue

            # user input tokens are space delimited

            input_tks = user_input.split(" ")
            try:
                assert len(input_tks) > 0
            except: 
                print(f'Usage: [req,post] arg2 arg3 See Userguide.md for details')
                continue
            print(f"input tks are {input_tks}")
            if input_tks[0] == "req":
                try:
                    assert len(input_tks) >= 2
                except:
                    print(f'Usage: req files (all/local)')
                    continue
                if input_tks[1] == "files":
                    try:
                        assert len(input_tks) >= 3
                    except:
                        print(f'Usage: req [files,supernodes,dl] arg3')
                        continue
                    if input_tks[2] == "all" and len(input_tks) >= 4:
                        file_id = input_tks[3]
                        self.requestDHT(file_id, True)
                    elif input_tks[2] == "all":
                        self.requestDHT('', True)
                    elif input_tks[2] == "local" and len(input_tks) >= 4:
                        file_id = input_tks[3]
                        self.requestDHT(file_id, False)
                    elif input_tks[2] == "local":
                        self.requestDHT('', False)
                    else:
                        print("ERR")
                        self.usage_statement()
                elif input_tks[1] == "supernodes":
                    if not self.isSupernode:
                        self.requestSupernodes()
                    else:
                        supernodeString = str(self.manager.supernodeSet)

                        num_supernode_entries = int(supernodeString[0:4])
                        cur_idx = 4
                        print(f"*** number of supernode entries is {num_supernode_entries}")
                        for i in range(num_supernode_entries):
                            try:
                                snodeIP = supernodeString[cur_idx:cur_idx+12]
                                cur_idx += 12
                                snodePort = supernodeString[cur_idx:cur_idx+5]
                                cur_idx += 5
                                print(f"    -- SUPERNODE at {splitIP(snodeIP)}:{snodePort}")
                            except IndexError as e:
                                print("fake 100a received from supernode, cannot index supernode ip, port, index out of bounds")

                elif input_tks[1] == "dl":
                    try: 
                        assert len(input_tks) >= 4
                    except:
                        print("usage: dl file_id file_host")
                        continue
                    # Else if input is to begin a download:
                    file_id = input_tks[2]
                    # TODO: need to add validation for IP:port
                    file_host = input_tks[3].split(":")
                    try:
                        assert(len(file_host) == 2)
                    except:
                        print(f'Usage: req dl file_id (offererIP:offererPort)')
                        continue

                    # convert the input IPv4 and Port to P2P format
                    offererIP = ''.join([x.zfill(3) for x in (file_host[0].strip('(').split('.'))])
                    offererPort = file_host[1].strip(')').zfill(5)

                    
                    # TODO: move the following logic to MainListener:
                    with self.manager.fileInfoTableLock:
                        tempFileInfoDict = self.manager.fileInfoTable.getFileInfoDictByID(file_id)
                        if tempFileInfoDict is None:
                            print('You should not request a file that I do not know exisited; request global DHT entries first (tempFileInfoDict is `None`)')
                            continue
                        tempFileInfo = tempFileInfoDict.get((offererIP, offererPort), None)
                        if tempFileInfo is None:
                            print('You should not request a file that I do not know exisited; request global DHT entries first (tempFileInfo is `None`)')
                            continue
                        maintainerIP, maintainerPort = tempFileInfo.maintainer

                    print(
                        f'Attempting to download \'{file_id}\' from {offererIP}:{offererPort}. Contacting the file\'s DHT entry maintainer at {maintainerIP}:{maintainerPort}. The addresses are in P2P format.')
                    self.beginDownload(file_id, maintainerIP, maintainerPort, offererIP, offererPort)

            elif input_tks[0] == "post":
                try:
                    assert len(input_tks) >= 2
                except:
                    print("Usage: post (offer/rm/disconnect)")
                    continue
                if input_tks[1] == "offer":
                    try:
                        assert len(input_tks) == 3
                    except:
                        print("Usage: post offer file_id")
                        continue
                    # Else if input is to offer a new file:
                    file_id = input_tks[2]

                    if not self.isSupernode:
                        self.offerNewFile(file_id)
                    else:
                        if not os.path.exists(file_id):
                            print(f"the file you've offered to post doesn't exist! {file_id}")
                        else:
                            self.manager.handleFilePost(self.ownIP, self.ownPort, file_id, os.path.getsize(file_id))
                elif input_tks[1] == "rm":
                    try:
                        assert len(input_tks) >= 3
                    except:
                        print("Usage: post rm file_id")
                        continue
                    file_id = input_tks[2]
                    self.removeOfferedFile(file_id)
                elif input_tks[1] == "disconnect":
                    # Else if input is to disconnect from the network
                    self.disconnect()
                else:
                    print("Unknown 'post' command.")

            else:
                print(f"command not recognized {input_tks[0]}")
                # Then, print out list of possible commmands:
                print(self.usage_statement())
