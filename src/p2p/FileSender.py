#! /usr/bin/python3

# This thread's job is to constantly send the file to the requested node.
# NOTE: I think that files should be sent to the current node's supernode & 
# routed from there.

import threading
import File
import FileInfoTable
import SNode_helpers

class FileSender(threading.Thread):

    # Initialize FileSender Thread
    def __init__(self, file, destinationIP):
        self.threading.Thread.__init__(self)
        self.file = file
        self.destinationIP = destinationIP
        print()

    def sendFile(self, file, destinationIP):
        # break the file into parts
        # create the messages
        # send the file
        print()

    def run(self):
        # Try to connect to the destination ip
        # If possible, directly send the file
        
        # If not possible, send through the supernodes
        print()




        
