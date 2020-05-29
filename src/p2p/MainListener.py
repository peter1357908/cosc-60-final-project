#! /usr/bin/python3

import threading
import asyncio
import sys

import InputListener
sys.path.append('../mrt/')
sys.path.append('../../../src/data-structures/')
import mrt
import FileInfoTable
import ChildrenInfoTable

class MainListener(threading.Thread):
    '''
        We assume that the input is valid in that:
        isSupernode is a boolean
        ownIP is a 12-byte string in ascii
        ownPort is a 5-byte string in ascii
    '''
    def __init__(self, isSupernode, ownIP, ownPort):
        self.threading.Thread.__init__(self)
        self.isSupernode = isSupernode
        self.ownIP = ownIP
        self.ownPort = ownPort
        self.fileInfoTable = FileInfoTable() # File Info Table
        self.childTable = ChildrenInfoTable() # Child Info Table
        self.supernode_list = [] # Supernodelist
        self.fileInfoTableLock = asyncio.Lock() # pass to spawned threads
        self.childTableLock = asyncio.Lock() # pass to spawned threads
        self.supernodeLock = asyncio.Lock() # pass to spawned threads
    
    # type - 0, 1, 2
    # 0 = regular node
    # 1 = supernode
    # 2 = relayed supernode
    def handleJoinRequest(self, type, sourceMRTID):
        # send number of supernode entries, supernode entries
        if type == 0:
            # keep sour
            response_type = '100a'
            snodes_num = str(len(supernode_list))
            msg = snodes_num.zfill(4) + str(supernode_list) # TODO: format it correctly
            response = response_type + '0000' + self.ownIP + self.ownPort + (str(len(msg))).zfill(4) + msg
            # id is returned by accept1()
            mrt.mrt_send1(sourceMRTID, response)
        elif type == 1:

        elif type == 2:
            
        else:
            print(f"{type} not found")


    '''
        See protocol md
    '''
    def handleSupernodeListRequest(self, sourceIP, sourcePort):
        # 100b | Number of Supernode Entries | Supernode Entries
        # Each supernode entry has the following format:
        #   IPv4 Addr.    Port
        response_type = '100b'
        snodes_num = str(len(supernode_list))
        # TODO: the message syntax is incorrect, look at matt's code
        response = response_type + '0000' + myAddr + snodes_num + self.formatSupernodeList()
        mrt.mrt_send1(id, response)
        pass

    # handles both cases
    # all_files_requested is True/False indicating whether or not to request all files
    def handleLocalDHTEntriesRequest(self, all_files_requested, connID):
        request_file_length = msg[20:24]
        if all_files_requested:
            response_type = '100c'
            mrt.mrt_send1(connID,  response_type + '0000' + myAddr + str(fInfo)) 
        else:
            #TODO: Figure out if it is possible to use FIT to get a formatting mandated by the protocol.md
            file_id = msg[24:24+int(request_file_length)/2].decode()
            file_entries= fInfo.getFileInfoDict(file_id)
            #TODO: File entries having the protocol.md may require some changes to FIT.
            toSend = str(file_id) + str(len(file_entries)) + str(file_entries)
            if toSend:
                mrt.mrt_send1(id, '100c' + '0000' + myAddr + toSend)
            #error
            else:
                mrt.mrt_send1(id, '0000')
        pass

    # handles both cases
    def handleAllDHTEntriesRequest(self):
        pass
    
    def handleFileTransferRequest(self):
        pass
    
    def run(self):
        # TODO: may need to add an mrt_open here?? to indicate readyness to accept incoming connections
        
        # Begin The User Input Thread
        inputListener = InputListener.InputListener(supernodeIP)
        inputListener.start()
        while True:
            newConnectionID = mrt.accept1()
            # pass in mainlistener
            messageListener = MessageListener(self, newConnectionID)
            # spawn message listener thread
            messageListener.start()


    ''' Utility functions '''
    def formatFileInfoTable(self):
        pass
    
    '''
        Format supernode list for message sending 
    '''
    def formatSupernodeList(self):
        return "".join(ip + port for (ip, port) in self.supernode_list)


