#! /usr/bin/python3

import threading
import sys

import InputListener
sys.path.append('../mrt/')
sys.path.append('../data-structures/')
from FileInfoTable import FileInfoTable, FileInfo
from ChildrenInfoTable import ChildrenInfoTable
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
    def __init__(self, isSupernode, ownIP, ownPort, recv_sock,super_send_id = '', super_recv_id = '', is_first = False):
        threading.Thread.__init__(self)
        self.isSupernode = isSupernode
        self.ownIP = ownIP
        self.ownPort = ownPort
        self.recv_sock = recv_sock
        self.super_send_id = super_send_id
        self.super_recv_id = super_recv_id
        self.is_first = is_first
        self.fileInfoTable = FileInfoTable() # File Info Table
        self.childTable = ChildrenInfoTable() # Child Info Table
        self.supernode_list = [] # Supernodelist
        self.fileInfoTableLock = threading.Lock() # pass to spawned threads
        self.childTableLock = threading.Lock() # pass to spawned threads
        self.supernodeLock = threading.Lock() # pass to spawned threads
        
    
    # type - 0, 1, 2
    # 0 = regular node
    # 1 = supernode
    # 2 = relayed supernode
    def handleJoinRequest(self, type, sendID): #TODO: add ip and port? 
        # send number of supernode entries, supernode entries
        if type == 0:
            # keep sour
            response_type = '100a'
            values = ''.join([response_type, f'{len(supernode_list):04d}',str(supernode_list)])
            response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
            # id is returned by accept1()
            #TODO: Need to add the duplex capability here just need to figure out where and how we are storing these connections
            mrt_send1(sendID, response)
        elif type == 1:
            #TODO: Add functionality to keep track of supernode
            response_type = '100a'
            values = ''.join([response_type, f'{len(supernode_list):04d}',str(supernode_list)])
            response = ''.join([REQUEST,f'{len(values):04d}',self.ownIP,self.ownPort,values])
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

    
    def run(self):

        print(f'Coming alive... IP: {self.ownIP} port: {self.ownPort}, socket: {self.recv_sock}')
        mrt_open() 
        #conn = mrt_accept1()
        #print(conn)
        # Begin The User Input Thread
        # Need to Pass in a SupernodePort and a SendID
        supernodeIP = "HARDCODE (possibly clay?)"
        supernodePort = "HARDCODE (possibly clay?)"
        inputListener = InputListener.InputListener(self, self.ownIP, self.ownPort, self.super_send_id, self.isSupernode)
        inputListener.start()
        print(f'started input listener...')
        # Msg Listener super_send & super_recv
        # Supernode Listener
        if not self.is_first:
            superListener = MessageListener(self, self.super_recv_id)
            superListener.start()

        
        # if supernode:
        print(f'looping, waiting for connections... ')
        while True:
            # Any new incoming connections
            #print(f'in loop')
            time.sleep(3)
            new_connections = mrt_accept_all() # This is non-blocking so that the thread can service other functions
            print(new_connections)
            if len(new_connections) > 0:
                print(f'{len(new_connections)} waiting... ')
            # Get conn id
                for connID in new_connections:
                    # pass in mainlistener
                    messageListener = MessageListener.MessageListener(self, connID)
                    # spawn message listener thread
                    messageListener.start()
                    print(f'started message listener...')
                    
                
        # if not supernode
            #loop until you want to leave the network.
            # new connections (msg listener etc) should be handled by the requestForFileTransfer function

        # if supernode: 
            # listen for new connections
            # spawn new listeners if a new connection comes in 

    ''' Utility functions '''
    def formatFileInfoTable(self):
        pass
    
    '''
        Format supernode list for message sending 
    '''
    def formatSupernodeList(self):
        return "".join(ip + port for (ip, port) in self.supernode_list)