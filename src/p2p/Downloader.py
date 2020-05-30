#! /usr/bin/python3

# This Thread's job is to constantly receive the file from its sender.
# NOTE: I think that files should be sent through the supernodes by default.

sys.path.append('../mrt/')
sys.path.append('../data-structures/')
import threading
import File
from FileInfoTable import FileInfo, FileInfoTable
from ChildrenInfoTable import ChildrenInfoTable
import SNode_helpers



class Downloader(threading.Thread):

# Initialize Downloader Thread
    def __init__(self, file, originIP):
        self.threading.Thread.__init__(self)
        self.file = file
        self.originIP = originIP
        self.downloadedSize = 0
        self.totalSize = #TODO: NEED TO FINISH THIS STUFF

    def receiveFile(self):
        # Parse the file messages to learn how many packets the file uses
        # Reconstruct the file
        # Save the file
        pass

    def run(self, dlIP, dlPort):
        # Start listening on the download port (to be specified)
        # call Receive File
        
