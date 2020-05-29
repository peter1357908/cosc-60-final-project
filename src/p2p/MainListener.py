#! /usr/bin/python3

import threading
import asyncio
sys.path.append('../mrt/')
sys.path.append('../data-structures/')
import mrt
import FilenfoTable

class MainListener(threading.Thread):
    def __init__(self, supernodeIP):
        self.threading.Thread.__init__(self)
        self.supernodeIP = supernodeIP # IP of supernode, 127.0.0.1 if is a supernode
        self.fileInfoTable = FileInfoTable() # File Info Table
        self.childTable = ChildrenInfoTable() # Child Info Table
        self.supernodeList = [] # Supernodelist
        self.fileInfoTableLock = asyncio.Lock() # pass to spawned threads
        self.childTableLock = asyncio.Lock() # pass to spawned threads
        self.supernodeLock = asyncio.Lock() # pass to spawned threads

    # - Get Whole Table
    # - Get FileInfoDict
    # - Get Specific Info
    # - Remove File
    # - Add File
    
    def updateFileInfoTable(self, ):
        pass


    def getFileInfo(self):
        pass

    def removeFileInfo(self):
        pass

    def addFile(self):
        pass
        

    def updateChildrenInfoTable(self):
        pass

    def updateSupernodeList(self):
        pass

    def run(self):
        
        while True:
            newConnectionID = mrt.accept1()
            # pass in mainlistener
            messageListener = MessageListener(self, newConnectionID)
            # spawn message listener thread
            messageListener.start()
