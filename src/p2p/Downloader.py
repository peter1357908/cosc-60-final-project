#! /usr/bin/python3

# This Thread's job is to constantly receive the file from its sender.
# NOTE: I think that files should be sent through the supernodes by default.

import threading
import File
import FileInfoTable
import SNode_helpers

class Downloader(threading.Thread):

# Initialize Downloader Thread
def __init__(self, file, originIP):
    self.threading.Thread.__init__(self)
    self.file = file
    self.originIP = originIP

def receiveFile(self):
    # Parse the file messages to learn how many packets the file uses
    # Reconstruct the file
    # Save the file
    print()

def run(self):
    # Start listening on the download port (to be specified)
    # call Receive File
    print()
