#! /usr/bin/python3

import threading
import MainListener
import sys
sys.path.append('../mrt/')
sys.path.append('../data-structures/')
import argparse
#import CNode_helper
#import mrt
import socket
import CNode_helper

# CONST VARIABLES
# TODO: need to change this to an established supernode
HARDCODED_SUPERNODE_IP = "104.55.97.253"
HARDCODED_SUPERNODE_PORT = 5000

SUPERNODE_LOOPBACK_IP = "127.0.0.1"

"""
    supernode_connect attempts to connect to HARDCODED_SUPERNODE_IP:HARDCODED_SUPERNODE_PORT by using cnode_helper's connect and join
    Takes an argument from the main program denoting whether to join as a supernode or regular node
    Returns True for successful connect and join, False otherwise
"""
def supernode_connect(sourceIP, sourcePort, as_supernode=False):
    sendID = CNode_helper.connect_p2p(ip=HARDCODED_SUPERNODE_IP, port=HARDCODED_SUPERNODE_PORT)
    # assuming that 0 is the "bad case"
    if sendID == 0:
        return None

    if as_supernode:
        recvID = CNode_helper.join_p2p(sendID, sourceIP, sourcePort, 1)
    else:
        recvID = CNode_helper.join_p2p(sendID, sourceIP, sourcePort, 0)
    return (sendID, recv_id)

'''
    This is the entry point for the p2p network client
    To run, use python3 __init__.py [--supernode]
    If --super is specified, the client will attempt to join as a supernode
'''
def main():

    # Alright, So this will attempt to connect to the default supernode.
    # If the connection is successful, then the __init__ file will begin the two main threads
    parser = argparse.ArgumentParser(description="p2p client")
    parser.add_argument("--supernode", "-s", help="join as a supernode", action="store_true")
    parser.add_argument("--first", "-f", help="be the first supernode", action="store_true")
    parser.add_argument("--port_forward", "-p",help="do you have port fowarding setup", action="store_true")
    args = parser.parse_args()

    # TODO: If the node is joining as a supernode & the network already ??
    # If the node is a childnode, then the IP of the supernode to be joined is an arg
    supernodePort = None
    isSupernode= args.supernode


    # Attempt to connect to the supernode:

    ### Logic for first ever supernode 
    if args.first:
        print(f'starting up as first ever supernode')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # sourceIP, sourcePort = CNode_helper.get_source_addr(sock)
        # print(f'ip: {sourceIP}, port: {sourcePort}')
        #static startup for clay
        print(f'About to come alive... socket: {sock}')
        mainListener = MainListener.MainListener(isSupernode=True,ownIP='104055097253',ownPort=5000,recv_sock=sock,is_first = True).start()
    else:
        print("connection is good")

        # If not connId:
        # if not res:
        #     print(f"failed to connect to supernode at address {HARDCODED_SUPERNODE_IP}:{HARDCODED_SUPERNODE_PORT}")
        #     exit(-1)
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #sourceIP, sourcePort = CNode_helper.get_source_addr(sock)

        # If not a supernode:
        if not isSupernode: 
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if args.port_forward:
                #sock.bind(('',5000))
                sourceIP,sourcePort = CNode_helper.get_source_addr(sock)

                send_id, recv_id = supernode_connect(sourceIP, sourcePort, False)
            print(f'send id : {send_id}, recv_id = {recv_id}')
            
        #super_send_id, super_recv_id = supernode_connect(False)


        # Begin The Packet / main Listener Thread
        mainListener = MainListener.MainListener(isSupernode, sourceIP, sourcePort, sock, super_send_id, super_recv_id)
        mainListener.start()

if __name__ == "__main__":
    main()
