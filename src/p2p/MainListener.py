#! /usr/bin/python3

import threading
import asyncio
import sys
sys.path.append('../mrt/')
sys.path.append('../../../src/data-structures/')
import mrt
import FileInfoTable

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
    
    # info - 0, 1, 2 
    # 0 = regular node
    # 1 = supernode
    # 2 = relayed supernode
    def handleJoinRequest(self, info):
        pass

    def handleSupernodeJoinRequest(self):
        pass

    def handleSupernodeListRequest(self):
        pass
    # handles both cases
    def handleLocalDHTEntriesRequest(self):
        pass
    # handles both cases
    def handleAllDHTEntriesRequest(self):
        pass
    
    def handleFileTransferRequest(self):
        pass
    
    def run(self):
        # TODO: may need to add an mrt_open here?? to indicate readyness to accept incoming connections
        while True:
            newConnectionID = mrt.accept1()
            # pass in mainlistener
            messageListener = MessageListener(self, newConnectionID)
            # spawn message listener thread
            messageListener.start()
