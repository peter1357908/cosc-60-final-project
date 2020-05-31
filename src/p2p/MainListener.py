#! /usr/bin/python3

import threading
import sys
sys.path.append('../mrt/')
sys.path.append('../data-structures/')
from mrt import *
import InputListener
from FileInfoTable import FileInfoTable, FileInfo
from ChildrenInfoTable import ChildrenInfoTable
from SupernodeSet import SupernodeSet
import MessageListener
import CNode_helper
import time


""" DEFINITIONS """
POST = '0001'
REQUEST = '0101'
FILE_TRANSFER = '1111'
ERROR = '0000'


class MainListener(threading.Thread):
    '''
        We assume that the input is valid in that:
        isSupernode is a boolean
        ownIP is a 12-byte string in ascii
        ownPort is a 5-byte string in ascii
    ''' 

    def __init__(self, isSupernode, ownIP, ownPort, bootstrapSendID='', bootstrapRecvID='', is_first=False):
        threading.Thread.__init__(self)
        self.isSupernode = isSupernode
        self.ownIP = ownIP
        self.ownPort = ownPort
        self.bootstrapSendID = bootstrapSendID
        self.bootstrapRecvID = bootstrapRecvID
        self.is_first = is_first

        # data structures and respective locks
        self.fileInfoTable = FileInfoTable()
        self.childTable = ChildrenInfoTable()
        self.supernodeSet = SupernodeSet()
        self.addrToIDTable = dict() # maps (IP, Port) to MRT ID (send, recv)
        self.fileInfoTableLock = threading.Lock() # pass to spawned threads
        self.childTableLock = threading.Lock() # pass to spawned threads
        self.supernodeLock = threading.Lock() # pass to spawned threads
        self.addrToIDTableLock = threading.Lock()

        # to block this MainListener until user decides to quit
        self.shouldQuit = False
        self.quitCV = threading.Condition()
    
    # type - 0, 1, 2
    # 0 = regular node
    # 1 = supernode
    # 2 = relayed supernode
    def handleJoinRequest(self, type, sendID, sourceIP, sourcePort): 
        # send number of supernode entries, supernode entries
        if type == 0:
            print("sending receive message back, type 100a")
            response_type = '100a'
            values = f'{response_type}{self.supernodeSet}'
            response = ''.join([REQUEST,f'{len(values):04d}', self.ownIP, self.ownPort, values])
            # id is returned by accept1()
            #TODO: Need to add the duplex capability here just need to figure out where and how we are storing these connections
            self.childTable.addChild((sourceIP, sourcePort))
            mrt_send1(sendID, response)
        elif type == 1:
            #TODO: Add functionality to keep track of supernode

            print("sending receive message back")
            response_type = '100a'
            values = f'{response_type}{self.supernodeSet}'
            print(self.ownIP)
            print(self.ownPort)
            response = ''.join([REQUEST, f'{len(values):04d}', self.ownIP, self.ownPort, values])
            # id is returned by accept1()
            mrt_send1(sendID, response)

        elif type == 2:
            supernode_list.add() #(IPV4,port)
            #TODO: add functionality for relayed supernode
            
        else:
            print(f"{type} not found")

    '''
        See protocol md
    '''
    def handleSupernodeListRequest(self, sourceIP, sourcePort,connID):
        # 100b | Number of Supernode Entries | Supernode Entries
        # Each supernode entry has the following format:
        #   IPv4 Addr.    Port
        response_type = '100b'
        snodes_num = str(len(supernode_list))
        values = ''.join([response_type,f'{len(supernode_list):04d}',str(supernode_list)])
        response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
        mrt_send1(connID, response)
        pass

    # handles both cases
    # all_files_requested is True/False indicating whether or not to request all cfiles
    def handleLocalDHTEntriesRequest(self, all_files_requested, connID):
        request_file_length = msg[20:24]
        if all_files_requested:
            response_type = '100c'
            values = ''.JOIN([response_type,f'{len(self.FileInfoTable):04d}',str(self.FileInfoTable)])
            response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
            mrt_send1(connID, response) 
        else:
            file_id = msg[24:24+int(request_file_length)].decode()
            file_entries = self.FileInfoTable.getTableByID(file_id)
            values = ''.join(['100c',f'{len(file_entries):04d}',str(file_entries)])
            response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
            if len(file_entries) > 0:
                mrt_send1(connID, response)
            #error
            else:
                mrt_send1(connID, '0000')
        pass

    # handles both cases 
    def handleAllDHTEntriesRequest(self):
        pass
        #TODO: This one is the most complicated as we first need to collect all of the file info from the other supernodes....

    
    # see Protocol.md for 'Request for a file transfer'
    # source is the client that sent the request
    # offerer is the client that source would like to download the file from
    def handleFileTransferRequest(self, connID, sourceIP, sourcePort, offererIP, offererPort, fileRequestedID):
        if self.isSupernode:
            if sourceIP == self.ownIP and sourcePort == self.ownPort:
                # ignore the message
                pass
            elif offererIP == self.ownIP and offererPort == self.ownPort:
                # "forward" the exact same request message (same (Source IPv4, Source Port)) to the node specified by (Source IPv4, Source Port) for UDP-holepunching.
                response_type = '000e'
                values = ''.join([response_type, f'{len():04d}', fileRequestedID, offererIP, offererPort])
                response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
                # id is returned by accept1()

                # TODO: once Peter has finished the data structure updates 

            else:
                # check that the offererip and port matches a childnode
                child = (offererIP, offererPort)
                if self.childTable.hasChild(child) and self.childTable.childHasFile(child, fileRequestedID):
                    # the supernode should "forward" the exact same message (same (Source IPv4, Source Port)) to that childnode.
                    # TODO: wait for Peter to finish data structure updates
                    pass
        else:
            if sourceIP == self.ownIP and sourcePort == self.ownPort:
                pass
            else:
                # Else, childnode should "forward" the exact same request message (same (Source IPv4, Source Port)) to the node specified by (Source IPv4, Source Port) for UDP-holepunching
                pass

    def handleRelayRequest(self, connID, offererIP, offererPort, fileRequestedID):
        # TODO: for one supernode/two supernodes, this is fine, but for more supernodes interconnected
        # there may be a supernode issues
        child = (offererIP, offererPort)
        if self.childTable.hasChild(child) and self.childHasFile(child, fileRequestedID):
            # relay the message
            response_type = '000e'
            values = ''.join([response_type, f'{len():04d}', fileRequestedID, offererIP, offererPort])
            response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
            # TODO: we need another connID
            # mrt.mrt_send1()
        

    '''
        handles POSTing a file
        notification for offering a new file 000a
        sourceIP, sourcePort - client that sent the POST message
        connID - connection ID of the client
        fileID - see Protocol.md
        fileSize
        Updates local DHT, does not send a message

    '''
    def handleFilePost(self, sourceIP, sourcePort, connID, fileID, fileSize):
        # update the local DHT
        # TODO: set a lock
        offerer = (sourceIP, sourcePort)
        newFileInfo = FileInfo(fileSize, (self.ownIP, self.ownPort))
        self.fileInfoTable.addFileInfo(fileID, offerer, newFileInfo)

        # update childreninfotable as well
        assert(offerer != (self.ownIP, self.ownIP))
        self.childTable.addFile(offerer, fileID)

        print(f"handle file post in mainlistener {fileID} of size {fileSize} from {sourceIP}:{sourcePort}")
        print(f'hash table now looks like: {self.fileInfoTable}')

    '''
        POST 
        notification for request to disconnect 000b 
    '''
    def handleRequestDisconnect(self, sourceIP, sourcePort, connID):
        # terminate the messagelistener thread
        # TODO: perform the necessary clearnup eg. delete entries in the data structures

        # send message indicating the node can safely disconnect
        response_type = "100b"
        values = ''.join([response_type])
        response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
        mrt_send1(connID, response)


    '''
        Note: not sure if we need this function - maybe it should start a downloader/uploader 
    '''
    def handleFileTransfer(self, sourceIP, sourcePort, connID):
        pass

    def handleUserQuitInput(self):
        self.shouldQuit = True
        self.quitCV.notify()

    def isQuit(self):
        return self.shouldQuit
    
    def run(self):
        print(f'MainListener starting... IP: {self.ownIP} port: {self.ownPort}')
        mrt_open()
        inputListener = InputListener.InputListener(self, self.ownIP, self.ownPort, self.bootstrapSendID, self.isSupernode)
        inputListener.start()
        
        if not self.is_first:
            # start listening to the bootstrapping supernode
            bootstrapListener = MessageListener.MessageListener(self, self.bootstrapRecvID)
            bootstrapListener.start()
        
        if self.isSupernode:
            print('MainListener going into connection accepting loop...')
            # TODO: why not accept1()?
            while True:
                time.sleep(3)
                new_connections = mrt_accept_all() # This is non-blocking so that the thread can service other functions
                print(new_connections)
                if len(new_connections) > 0:
                    print(f'{len(new_connections)} waiting... ')
                    for connID in new_connections:
                        messageListener = MessageListener.MessageListener(self, connID)
                        messageListener.start()
        else:
            with self.quitCV:
                self.quitCV.wait_for(self.isQuit)
                return
