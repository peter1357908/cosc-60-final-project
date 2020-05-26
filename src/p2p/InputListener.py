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
        while true:
            # Parse out user input
                
                # If the command requires a file as an arg: 
                    fileID = 'parsed'
                    offerer = 'parsed'
                    fileInfo = 'parsed'
                    name = 'parsed'
                    file = File(fileID, offerer, fileInfo, name)

                    downloadIP = file.getOfferer()

            # If input is request for information:
                self.requestDHT()
            # Else if input is to begin a download:
                self.beginDownload(downloadIP, file)
            # Else if input is to offer a new file:
                self.offerNewFile(file)
            # Else if input is to remove a file currently offered:
                self.removeOfferedFile(file)
            # Else if input is to disconnect from the network:
                self.disconnect()
            # Else:
                print("Unknown Command.")
                # Then, print out list of possible commmands:
            






