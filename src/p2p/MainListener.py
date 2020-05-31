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
        self.addrToIDTable = dict() # maps (IP, Port) to MRT sendID
        self.fileInfoTableLock = threading.Lock() # pass to spawned threads
        self.childTableLock = threading.Lock() # pass to spawned threads
        self.supernodeSetLock = threading.Lock() # pass to spawned threads
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
            childAddr = (sourceIP, sourcePort)
            with self.childTableLock:
                self.childTable.addChild(childAddr)
            with self.addrToIDTableLock:
                self.addrToIDTable[childAddr]=sendID
            mrt_send1(sendID, response)
            
        elif type == 1:
            print("sending receive message back, type 100a")
            response_type = '100a'
            values = f'{response_type}{self.supernodeSet}'
            response = ''.join([REQUEST, f'{len(values):04d}', self.ownIP, self.ownPort, values])

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

        elif type == 2:
            # keep track of the supernode
            superAddr = (sourceIP, sourcePort)
            with self.supernodeSetLock:
                self.supernodeSet.add(superAddr)
            with self.addrToIDTableLock:
                self.addrToIDTable[superAddr]=sendID
            
        else:
            print(f"handleJoinRequest(): type \'{type}\' not found")

    '''
        See Protocol.md
    '''
    def handleSupernodeSetRequest(self, sourceIP, sourcePort):
        response_type = '100a'
        values = f'{response_type}{self.supernodeSet}'
        response = ''.join([response_type,f'{len(values):04d}', self.ownIP, self.ownPort, values])

        with self.addrToIDTableLock:
            sourceSendID = self.addrToIDTable[(sourceIP, sourcePort)]

        print(f"sending supernode set back to {sourceIP}:{sourcePort} using {sourceSendID}")
        mrt_send1(sourceSendID, response)

    # handles both cases
    # all_files_requested is True/False indicating whether or not to request all cfiles
    def handleLocalDHTEntriesRequest(self, sourceIP, sourcePort, fileID):
        response_type = '100c'

        if len(fileID) > 0:
            # requested entries on one particular file
            tempFileInfoTable = self.fileInfoTable.getFileInfoTableByID(fileID)
            values = ''.join([response_type,str(tempFileInfoTable)])
        else:
            # requested entries on ALL files
            values = ''.join([response_type,str(self.fileInfoTable)])
        
        response = ''.join([response_type,f'{len(values):04d}',self.ownIP,self.ownPort,values])

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

                        msg_len = len(values)
                        msg = ''.join(['0101', f'{msg_len:04d}', sourceIP, sourcePort, values])
                        mrt_send1(supernodeSendID, msg)

    
    # see Protocol.md for 'Request for a file transfer'
    # source is the client that sent the request
    # offerer is the client that source would like to download the file from
    def handleFileTransferRequest(self, sourceIP, sourcePort, offererIP, offererPort, fileRequestedID):
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

    def handleRelayRequest(self, offererIP, offererPort, fileRequestedID):
        # TODO: for one supernode/two supernodes, this is fine, but for more supernodes interconnected
        # there may be a supernode issues
        child = (offererIP, offererPort)
        if self.childTable.hasChild(child) and self.childHasFile(child, fileRequestedID):
            # relay the message
            response_type = '000e'
            values = ''.join([response_type, f'{len():04d}', fileRequestedID, offererIP, offererPort])
            response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
            # mrt.mrt_send1()
        

    '''
        handles POSTing a file
        notification for offering a new file 000a
        sourceIP, sourcePort - client that sent the POST message
        fileID - see Protocol.md
        fileSize
        Updates local DHT, does not send a message

    '''
    def handleFilePost(self, offerIP, offerPort, fileID, fileSize):
        # update the local DHT
        offerer = (offerIP, offerPort)
        newFileInfo = FileInfo(fileSize, (self.ownIP, self.ownPort))
        with self.fileInfoTableLock:
            self.fileInfoTable.addFileInfo(fileID, offerer, newFileInfo)

        # update childreninfotable as well
        if offerer != (self.ownIP, self.ownIP):
            with self.childTableLock:
                self.childTable.addFile(offerer, fileID)

        print(f'handle file post in mainlistener {fileID} of size {fileSize} from {offerIP}:{offerPort}')
        print(f'hash table now looks like: {self.fileInfoTable}')

    '''
        POST 
        notification for request to disconnect 000b 
    '''
    def handleRequestDisconnect(self, sourceIP, sourcePort):
        # TODO: handle supernode disconnection?
        childAddr = (sourceIP, sourcePort)
        with self.childTableLock:
            child_files = self.childTable.popChild(childAddr)
        with self.fileInfoTableLock:
            self.fileInfoTable.removeAllFileInfoByOfferer(child_files, childAddr)

        response_type = "100b"
        values = ''.join([response_type])
        response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
        
        with self.addrToIDTableLock:
            childSendID = self.addrToIDTable[childAddr]

        mrt_send1(childSendID, response)


    '''
        Note: not sure if we need this function - maybe it should start a downloader/uploader 
    '''
    def handleFileTransfer(self, sourceIP, sourcePort, curr_file_part,fileID):
        response_type = '000a'
        fileID_length = len(fileID)
        childAddr = (sourceIP, sourcePort)
        len_data = len(curr_file_part)
        values = ''.join([response_type,f'{fileID_length:04d}',fileID,f'{len_data:04d}',curr_file_part])
        response = ''.join([FILE_TRANSFER,f'{len(values):04d}',self.ownIP,self.ownPort,values])

        with self.addrToIDTableLock:
            childSendID = self.addrToIDTable[childAddr]

        mrt_send1(childSendID, response)

    def handleUserQuitInput(self):
        self.shouldQuit = True
        self.quitCV.notify()

    def isQuit(self):
        return self.shouldQuit
    
    def run(self):
        print(f'MainListener starting... IP: {self.ownIP} port: {self.ownPort}')
        if self.is_first:
            mrt_open(s=1)
        
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
                time.sleep(2)
                new_connections = mrt_accept_all() # This is non-blocking so that the thread can service other functions
                if len(new_connections) > 0:
                    for recvID in new_connections:
                        messageListener = MessageListener.MessageListener(self, recvID)
                        messageListener.start()
        else:
            with self.quitCV:
                self.quitCV.wait_for(self.isQuit)
                return
