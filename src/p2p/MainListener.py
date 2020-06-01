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
from CNode_helper import *
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
                print(f'handle join request type 0 addrToIDTable: {self.addrToIDTable}')

            # print the address to send id table
            print("addr to send table is ", self.addrToIDTable)
            
            # craft and send response `100a`
            response_type = '100a'
            values = f'{response_type}{self.supernodeSet}'
            response = f'{REQUEST}{len(values):04d}{self.ownIP}{self.ownPort}{values}'
            send_p2p_msg(sendID, response)
            
        elif type == 1:
            # relay supernode join request
            # DANGEROUS: nested locks (but by itself it is fine)
            with self.supernodeSetLock:
                with self.addrToIDTableLock:
                    for supernodeAddr in self.supernodeSet.getSet():
                        supernodeSendID = self.addrToIDTable.get(supernodeAddr, None)
                        print(f'handle join request type 1 addrToIDTable after getting supernodeAddr: {self.addrToIDTable}')
                        values = '000a0002'
                        msg_len = len(values)
                        msg = ''.join(['0101', f'{msg_len:04d}', sourceIP, sourcePort, values])
                        send_p2p_msg(supernodeSendID, msg)
            
            # keep track of the supernode after relaying the request
            superAddr = (sourceIP, sourcePort)
            with self.supernodeSetLock:
                self.supernodeSet.add(superAddr)
            with self.addrToIDTableLock:
                self.addrToIDTable[superAddr]=sendID
                print(f'handle join request type 1 addrToIDTable after adding the joining supernode\'s address: {self.addrToIDTable}')

            # print the address to send id table
            print("addr to send table is ", self.addrToIDTable)

            # craft and send response `100a`
            response_type = '100a'
            values = f'{response_type}{self.supernodeSet}'
            response = f'{REQUEST}{len(values):04d}{self.ownIP}{self.ownPort}{values}'
            send_p2p_msg(sendID, response)

        elif type == 2:
            # keep track of the supernode
            superAddr = (sourceIP, sourcePort)
            with self.supernodeSetLock:
                self.supernodeSet.add(superAddr)
            with self.addrToIDTableLock:
                self.addrToIDTable[superAddr]=sendID

            # print the address to send id table
            print("addr to send table is ", self.addrToIDTable)
            
        else:
            print(f"handleJoinRequest(): type \'{type}\' not found")

    '''
        See Protocol.md
    '''
    def handleSupernodeSetRequest(self, sourceIP, sourcePort):
        response_type = '100a'
        values = f'{response_type}{self.supernodeSet}'
        response = f'{REQUEST}{len(values):04d}{self.ownIP}{self.ownPort}{values}'

        with self.addrToIDTableLock:
            sourceSendID = self.addrToIDTable.get((sourceIP, sourcePort), None)

        # print the address to send id table
        print("addr to send table is ", self.addrToIDTable)

        print(f"sending supernode set back to {sourceIP}:{sourcePort} using {sourceSendID}")
        send_p2p_msg(sourceSendID, response)
    
    # handles request response `100a`
    # `responseString` should not contain the type `100a`, and should be decoded already (NOT binary)
    def handleSupernodeSetRequestResponse(self, responseString):
        with self.supernodeSetLock:
            self.supernodeSet.importByString(responseString)

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
            sourceSendID = self.addrToIDTable.get((sourceIP, sourcePort), None)

        # print the address to send id table
        print("addr to send table is ", self.addrToIDTable)

        send_p2p_msg(sourceSendID, response)

    # handles the request response `100c`
    # `responseString` should not contain the type `100c`, and should be decoded already (NOT binary)
    def handleLocalDHTEntriesRequestResponse(self, responseString, sourceIP, sourcePort):
        with self.fileInfoTableLock:
            self.fileInfoTable.importByString(responseString, (sourceIP, sourcePort))
            

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
                        supernodeSendID = self.addrToIDTable.get(supernode, None)
                        
                        if len(fileID) > 0:
                            values = f'000c{fileIDLengthString}{fileID}'
                        # if the requester wants entries on ALL files
                        else:
                            values = '000c0000'

                        # print the address to send id table
                        print("addr to send table is ", self.addrToIDTable)

                        msg = f'{REQUEST}{len(values):04d}{self.ownIP}{self.ownPort}{values}'
                        send_p2p_msg(supernodeSendID, msg)

    # handles message-forwarding for request 000e
    def forwardFileTransferRequest(self, sourceIP, sourcePort, offererIPv4, offererPort, maintainerIPv4, maintainerPort, fileIDLengthString, fileID):
        if not self.isSupernode:
            # should not even attempt forwarding if self is not supernode
            return

        targetSendID = None
        maintainerAddr = (maintainerIPv4, maintainerPort)
        # if self is maintainer
        if maintainerAddr == (self.ownIP, self.ownPort):
            with self.childTableLock:
                offererAddr = (offererIPv4, offererPort)
                if self.childTable.childHasFile(offererAddr, fileID):
                    with self.addrToIDTableLock:
                        targetSendID = self.addrToIDTable.get(offererAddr, None)
                else:
                    return
        else:
            with self.addrToIDTableLock:
                targetSendID = self.addrToIDTable.get(maintainerAddr, None)

        # print the address to send id table
        print("forwardfiletransferreq, addr to send table is ", self.addrToIDTable)
        
        # TODO: consider taking in the original message to allow forwarding
        values = f'000e{fileIDLengthString}{fileID}{offererIPv4}{offererPort}{maintainerIPv4}{maintainerPort}'
        msg = f'{REQUEST}{len(values):04d}{sourceIP}{sourcePort}{values}'
        send_p2p_msg(targetSendID, msg)

    '''
        handles POSTing a file
        notification for offering a new file 000a
        sourceIP, sourcePort - client that sent the POST message
        fileID - see Protocol.md
        fileSize
        Updates local DHT, does not send a message
    '''
    def handleFilePost(self, offererIP, offerPort, fileID, fileSize):
        # update the local DHT
        offererAddr = (offererIP, offerPort)
        newFileInfo = FileInfo(fileSize, (self.ownIP, self.ownPort))
        with self.fileInfoTableLock:
            self.fileInfoTable.addFileInfo(fileID, offererAddr, newFileInfo)

        # update childrenInfoTable as well
        if offererAddr != (self.ownIP, self.ownPort):
            with self.childTableLock:
                self.childTable.addFile(offererAddr, fileID)

        # print the address to send id table
        print("handlefilepost addr to send table is ", self.addrToIDTable)

        print(f'handle file post in mainlistener: \'{fileID}\' of size {fileSize} from {offererIP}:{offerPort}')
        print(f'hash table now looks like: {self.fileInfoTable}')

    '''
        POST 
        notification for request to disconnect 000b 
    '''
    def handleDisconnectPost(self, sourceIP, sourcePort):
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
            childSendID = self.addrToIDTable.pop(childAddr, None)

        send_p2p_msg(childSendID, response)


    '''
        This function is invoked by message listener upon receiving a file transfer request
    '''
    def handleFileTransfer(self, sourceIP, sourcePort, curr_file_part, fileID, eof=False):
        recvAddr = (sourceIP, sourcePort)
        with self.addrToIDTableLock:
            recvSendID = self.addrToIDTable[recvAddr]

        # print the address to send id table
        print("handlefiletransfer, addr to send table is ", self.addrToIDTable)

        response_type = '000a'
        fileID_length = len(fileID)
        len_data = len(curr_file_part)
        values = ''.join([response_type,f'{fileID_length:04d}',fileID,f'{len_data:04d}',curr_file_part])
        response = ''.join([FILE_TRANSFER,f'{len(values):04d}',self.ownIP,self.ownPort,values])
        send_p2p_msg(recvSendID, response)

        if eof:
            if (self.isSupernode and not self.childTable.hasChild(recvAddr)) or (recvSendID != self.bootstrapSendID):
                mrt_disconnect(recvSendID)

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
        
        print('MainListener going into connection accepting loop...')
        # TODO: mrt_accept1() blocks by sleeping; update with condition variable?
        while True:
            recvID = mrt_accept1()
            messageListener = MessageListener.MessageListener(self, recvID)
            messageListener.start()
