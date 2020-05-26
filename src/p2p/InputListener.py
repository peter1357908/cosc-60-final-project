#! /usr/bin/python3

# This is the code for the InputListener Thread:

import threading
import File
import FileInfoTable
import SNode_helpers

class InputListener(threading.Thread):

    # Initialize InputListener Thread
    # TODO: Add paramaters as arguments are determined
    def __init__(self,supernodeIP, table):
        threading.Thread.__init__(self)
        self.supernodeIP = supernodeIP  # IP of supernode, 127.0.0.1 if is a supernode
        self.table = table # File Info Table
        # If the Node is a supernode, then instantiate a childTable and superList
        if supernodeIP == "127.0.0.1":
            self.childTable = ChildrenInfoTable()
            self.superList = SupernodeList()

    # Methods for handling each parsed case:
    # A note on the following methods: "file" is always a File Object.

    # Construct Request DHT packet and send to supernodeIP:
    def requestDHT(self):
        # TODO
        print("Requested DHT from ", self.supernodeIP)

    # Begin a download:
    def beginDownload(self, downloadIP, file):
        downloader = Downloader(self.supernodeIP, downloadIP, file)
        downloader.start()
        print("Attempting to download from ", downloadIP)
    
    # Offer a New File
    def offerNewFile(self, file):
        # TODO
        print("Announcing a new file is being offered: ", file)
    
    # Announce a file is no longer being offered:
    def removeOfferedFile(self, file):
        # TODO:
        print(file.getName(), " is no longer being offered")
    
    # Disconnect from the network:
    def disconnect(self):
        # TODO:
        print("Disconnected from the network. Goodbye!")


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
                    self.request_supernodes()
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
                    self.offerNewFile(file=None)
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







