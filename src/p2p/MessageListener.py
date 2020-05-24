#! /usr/bin/python3

# Message Listener Thread:

import threading
import File
import FileInfoTable
import SNode_helpers

class MessageListener(threading.Thread):

    # Initialize MessageListener Thread
    # TODO: Add paramaters as arguments are determined
    def __init__(self, supernodeIP, table):
        self.threading.Thread.__init__(self)
        self.supernodeIP = supernodeIP # IP of supernode, 127.0.0.1 if is a supernode
        self.table = table # File Info Table
        print()

    # Methods for handling each parsed method:
    # A note on the following methods: 'file' is always a File object
    # and 'files' is an array of File objects

    # Accept a new connection
    def acceptConnection(self, connectedIP):
        #TODO: Add the connected IP to the list of child nodes
        print()

    # Accept a new supernode connection. This message will only be received by supernodes
    def acceptSupernodeConnection(self, connectedIP):
        #TODO: add the connected IP to the list of connected supernodes
        print()

    # Process a child node disconnecting. Currently, supernodes cannot disconnect without 
    # Shutting down the network.
    def processDisconnect(self, disconnectedIP):
        # TODO: remove the disconnected IP from the list of child nodes
        # Also remove the files offered by disconnectedIP from HT
        print()

    # Add a list of File objects to the HT:
    def addFiles(self, files):
        # TODO: For every file in files, add that file to the HT & print a debug statement
        print()
    
    # Remove a list of File objects from the HT:
    def removeFiles(self, files):
        # TODO: For every file in files, remove file from the HT
        print()

    # Send back local-DHT
    def sendBackHT(self, destinationIP):
        # TODO: Send back HT using mrt_send
        print()
    
    # Accept the request for download and start sending the file
    def acceptDownload(self, file, destinationIP):
        fileSender = FileSender(file, destinationIP)
        fileSender.start()
        print()
    
    # When a download message is received but the destination is not the current node
    # pass on the packet to the appropriate node:
    def passOn(self, destinationIP):
        # TODO: pass on & figure out a way to do so.
        # If the current node is not the supernode of the destination, 
            # pass on the packet to the supernode of that packet
        # Else, if the current node is that child node's (dest.) supernode
            # pass on the packet to the destination.
        print()

    # TODO: run() method:
    def run(self):
        # Constantly listen for packets:
        while true:
            # Parse out incoming packets:
            connectedIP = 'parsed'
            disconnectedIP = 'parsed'
            # If the command requires a file as an arg: 
            fileID = 'parsed'
            offerer = 'parsed'
            fileInfo = 'parsed'
            name = 'parsed'
            file = File(fileID, offerer, fileInfo, name)

            destinationIP = 'parsed'

            files = "array of all files parsed"
            


            # If the packet is a request to connect packet from a child:
                self.acceptConnection(connectedIP)
            # Else if the packet is a request to connect from a supernode:
                self.acceptSupernodeConnection(connectedIP)
            # Else if the packet is a disconnect packet:
                self.processDisconnect(disconnectedIP)
            # Else if the packet is a request to start a download:
                self.acceptDownload(file, destinationIP)
            # Else if the packet is a file in transfer:
                self.passOn(destinationIP)
            # Else if the packet contains new files / information:
                self.addFiles(files)
            # Else if the packet announces that a file / files is /are no longer offered:
                self.removeFiles(files)
            # Else if the packet is a request for information:
                self.sendBackHT(destinationIP)
            # Else:
                print("Unknown Packet Received.")
                








    
