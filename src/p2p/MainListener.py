#! /usr/bin/python3

import threading
import sys

import InputListener
sys.path.append('../mrt/')
sys.path.append('../data-structures/')
from FileInfoTable import FileInfoTable, FileInfo
from ChildrenInfoTable import ChildrenInfoTable
from SupernodeSet import SupernodeSet
from mrt import * 
import MessageListener
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
            # keep track of the childnode before responding
            childAddr = (sourceIP, sourcePort)
            with self.childTableLock:
                self.childTable.addChild(childAddr)
            with self.addrToIDTableLock:
                self.addrToIDTable[childAddr] = sendID
            
            # craft and send response `100a`
            response_type = '100a'
            values = f'{response_type}{self.supernodeSet}'
            response = f'{REQUEST}{len(values):04d}{self.ownIP}{self.ownPort}{values}'
            mrt_send1(sendID, response)
            
        elif type == 1:
            # relay supernode join request
            # DANGEROUS: nested locks (but by itself it is fine)
            with self.supernodeSetLock:
                with self.addrToIDTableLock:
                    for supernode in self.supernodeSet.getSet():
                        supernodeSendID = self.addrToIDTable.get(supernode)
                        values = '000a0002'
                        msg_len = len(values)
                        msg = ''.join(['0101', f'{msg_len:04d}', sourceIP, sourcePort, values])
                        mrt_send1(supernodeSendID, msg)
            
            # keep track of the supernode after relaying the request
            superAddr = (sourceIP, sourcePort)
            with self.supernodeSetLock:
                self.supernodeSet.add(superAddr)
            with self.addrToIDTableLock:
                self.addrToIDTable[superAddr]=sendID

            # craft and send response `100a`
            response_type = '100a'
            values = f'{response_type}{self.supernodeSet}'
            response = f'{REQUEST}{len(values):04d}{self.ownIP}{self.ownPort}{values}'
            mrt_send1(sendID, response)

        elif type == 2:
            supernode_list.add() #(IPV4,port)
            #TODO: add functionality for relayed supernode
            
        else:
            print(f"{type} not found")

    '''
        See protocol md
    '''
    def handleSupernodeSetRequest(self, sourceIP, sourcePort):
        response_type = '100a'
        values = f'{response_type}{self.supernodeSet}'
        response = f'{REQUEST}{len(values):04d}{self.ownIP}{self.ownPort}{values}'

        with self.addrToIDTableLock:
            sourceSendID = self.addrToIDTable[(sourceIP, sourcePort)]

        print(f"sending supernode set back to {sourceIP}:{sourcePort} using {sourceSendID}")
        mrt_send1(sourceSendID, response)

    # handles both cases of request `000c`
    def handleLocalDHTEntriesRequest(self, sourceIP, sourcePort, fileID):
        response_type = '100c'

        if len(fileID) > 0:
            # requested entries on one particular file
            tempFileInfoTable = self.fileInfoTable.getFileInfoTableByID(fileID)
            values = f'{response_type}{tempFileInfoTable}'
        else:
            # requested entries on ALL files
            values = f'{response_type}{self.fileInfoTable}'
        
        response = f'{REQUEST}{len(values):04d}{self.ownIP}{self.ownPort}{values}'

        with self.addrToIDTableLock:
            sourceSendID = self.addrToIDTable[(sourceIP, sourcePort)]

        mrt_send1(sourceSendID, response)

    def handleAllDHTEntriesRequest(self, sourceIP, sourcePort, fileIDLengthString, fileID):
        #TODO: This one is the most complicated as we first need to collect all of the file info from the other supernodes...
        supernodeAddr = (sourceIP, sourcePort)

        if supernodeAddr not in self.supernodeSet.getSet():
            # respond to the requesting node as if the request is of type '000c'
            self.handleLocalDHTEntriesRequest(sourceIP, sourcePort, fileID)

            # forward the message with type '000c' to all the known supernodes
            with self.supernodeSetLock:
                with self.addrToIDTableLock:
                    for supernode in self.supernodeSet.getSet():
                        supernodeSendID = self.addrToIDTable.get(supernode)
                        
                        if len(fileID) > 0:
                            values = f'000c{fileIDLengthString}{fileID}'
                        # if the requester wants entries on ALL files
                        else:
                            values = '000c0000'

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
            # TODO: mrt_accept1() blocks by sleeping; update with condition variable?
            while True:
                recvID = mrt_accept1()
                messageListener = MessageListener.MessageListener(self, recvID)
                messageListener.start()
                        
        else:
            with self.quitCV:
                self.quitCV.wait_for(self.shouldQuit)
                return
