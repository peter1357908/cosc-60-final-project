import binascii as btasc
from dataclasses import dataclass
from MSG_Parser_CS60 import FileInfoTable
from MSG_Parser_CS60 import ChildrenInfoTable

import mrt


'''
A temporary position for our Supernode class that is here only for ease of access. Will be its own class at
earliest possibility.
'''
@dataclass
class SuperNode:
    fileHash: FileInfoTable.FileInfoTable
    childHash: ChildrenInfoTable.ChildrenInfoTable

fInfo = FileInfoTable.FileInfoTable()
childHash = ChildrenInfoTable.ChildrenInfoTable()
sNode = SuperNode(fInfo,childHash)

myAddr = '(1000,5001)' #TODO: get the actual IP
myIP = 111111
myPort = 5001

'''
A procedure that receives a message from a lower-ranking peer, decoded and responds if necessary.
Please see procedure.md for more details on the structure of our messages
'''
def msg_parser(msg):
    # Grab the data included in the message headers
    msg_type = msg[0:4]
    print(msg_type.decode())
    msg_len = msg[4:8]
    print(msg_len.decode())
    peer_id = msg[8:12] # NOTE: This is currently unused since we rely on the internal mrt id
    print(peer_id.decode())
    ip_addr = msg[12:16]
    print(ip_addr.decode())
    internal_id = mrt.id_lookup(ip_addr.decode()) # TODO: See formatting of ip_addr
    print(internal_id)
    # Post
    if msg_type.decode() == '0001':
        post_type = msg[16:20]

        # Offer of a new file
        if post_type.decode() == '000a':
            file_size = msg[20:24]
            file_id_length = msg[24:28]
            file_id = msg[28:32]
            fInfo.addFileInfo(file_id.decode(),ip_addr.decode(),file_size.decode())

        # Intent to disconnect
        if post_type.decode() == '000b':
            #Removes all files by this ip address
            fInfo.removeAllFileInfoByOfferer(ip_addr.decode())


    # Request
    if msg_type.decode() == '0101':
        request_type = msg[16:20]
        misc = msg[20:24]

        # joining the network
        if request_type.decode() == '000a':
            r_misc = misc.decode()
            # join as a regular node
            if r_misc == '0000':
                response_type = '100a'
                snodes_num = str(len(supernode_list))
                msg = snodes_num + str(supernode_list)#Remove first and last char of list upon receiving
                response = response_type + '0000' + myAddr + str(len(msg))+msg
                # id is returned by accept1()
                mrt.mrt_send1(id, response)

            # join as a supernode
            elif r_misc == '0001':
                for supernode in supernode_list:
                    new_sn_msg = '0101' + '0000' + ip_addr.decode() + '000a' + '0002'
                    # Find the mrt assigned id for our supernodes
                    sup_id = mrt.id_lookup(supernode) # TODO: Are there situations where mrt doesn't have this ip?
                    mrt.mrt_send1(sup_id, new_sn_msg)

            # relayed supernode request (supernode informing other supernodes ofa new SN)
            elif r_misc == '0002':
                #Note that IP will be a string

                supernode_list.append(ip_addr.decode())

            # error
            else:
                mrt.mrt_send1(ip_addr.decode(), '0000')

        # request supernode list
        if request_type.decode() == '000b':
            response_type = '100b'
            snodes_num = str(len(supernode_list))
            response = response_type + '0000' + myAddr + snodes_num + str(supernode_list)
            # sends a message to the id returned by accept1
            mrt.mrt_send1(id, response)

        # request for local DHT files
        #TODO: Consider doing parsing(say by comma) instead of maintaining a super rigid structure.
        #TODO: Alternative ensure that the FileInfoTable is structured in such a way that this is more easily achievable
        if request_type.decode() == '000c':
            request_file_length = msg[20:24]
            if request_file_length.decode() == '0000':
                #TODO: Do the formatting.
                 mrt.mrt_send1(id, '100c' + '0000' + myAddr + str(fInfo)) #TODO: what does str(finfo) look like?
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

        # TODO: relay the DHT request
        if request_type.decode() == '000d':
            for supernode in supernode_list:
                #TODO: Interface with client side to use their "000c"
                sup_id = mrt.id_lookup(supernode)
                mrt.mrt_send1(sup_id, "")


        if request_type.decode() == '000e':
            file_id_length = msg[16:20].decode()
            id_end = 20+int(file_id_length)
            file_id = msg[20: id_end].decode()
            # Ensure offerer_addr matches the format of myAddr
            offerer_addr = '(' + msg[id_end: id_end+12].decode() + ',' + msg[id_end+12: id_end+17].decode() + ')'
            if not ip_addr == myAddr:
                    if offerer_addr == myAddr:
                        #placeholder before adding the actual file
                        mrt.mrt_send1(id, '7777')
                    else:
                        child_id = mrt.id_lookup(offerer_addr)
                        mrt.mrt_send1(child_id, '000e' + '0000' + myAddr + str(file_id_length)+str(file_id))

    # File-transfer
    if msg_type.decode() == '1111':
        recv_file = msg[16:]
    # Indication of error
    if msg_type.decode() == '0000':
        print("Error occured")
        # TODO: Figure out what we want to do... Perhaps have more details on what type of error this is.. Resend request? Send to different server..


#TODO: MOVE MAIN INTO SEPARATE FILE
if __name__ == '__main__':
    # Starts listening to connections
    mrt.mrt_open(myIP,myPort) #TODO: Supply host IP and appropriate PORT

    supernode_list = []

    # Keep handling requests while running
    # Accepts a connection, receives the message, and parses it
    while True:
        id = mrt.mrt_accept1()
        message = mrt.mrt_receive1(id)
        msg_parser(message)


def append_zeroes(msg, total_len):
    msg = msg + total_len-len(msg) * '0'
    return msg
