#! /usr/bin/python3

import threading
from MainListener import *
import sys
sys.path.append('../data-structures/')
import argparse
import socket

# CONST VARIABLES
# TODO: need to change this to an established supernode
HARDCODED_SUPERNODE_IP = "35.212.76.82"
HARDCODED_SUPERNODE_IP_P2P = "035212076082"
HARDCODED_SUPERNODE_PORT = 5000
HARDCODED_SUPERNODE_PORT_P2P = "05000"


'''
    bootstrap_connect attempts to connect to supernodeIP:supernodePort by using cnode_helper's connect and join
    Takes an argument from the main program denoting whether to join as a supernode or regular node
    Returns (sendID, recvID) for successful connect and join; returns None (or gets blocked) otherwise
'''
def bootstrap_connect(ownIP, ownPort, supernodeIP, supernodePort,recv_sock, as_supernode=False):
    print(f'bootstrapping....')
    sendID = CNode_helper.connect_p2p(ip=supernodeIP, port=supernodePort)
    # assuming that 0 is the "bad case"
    print(f'connected...')
    if sendID == 0:
        return None
    if as_supernode:
        recvID = CNode_helper.join_p2p(recv_sock,sendID, ownIP, ownPort, 1)
    else:
        recvID = CNode_helper.join_p2p(recv_sock,sendID, ownIP, ownPort, 0)
    return sendID, recvID

'''
    This is the entry point for the p2p network client
    To run, use python3 p2p.py [--supernode]
    If --super is specified, the client will attempt to join as a supernode
'''
def main():
    parser = argparse.ArgumentParser(description="p2p client")
    parser.add_argument("--supernode", "-s", help="join as a supernode", action="store_true")
    parser.add_argument("--first", "-f", help="join as the first supernode", action="store_true")
    parser.add_argument("--port_forward", "-p",help="do you have port fowarding setup", action="store_true")
    args = parser.parse_args()

    # TODO: join as a childnode

    ### Logic for first ever supernode 
    if args.first:
        print(f'starting up as first ever supernode')
        mainListener = MainListener(
            isSupernode=True, ownIP=HARDCODED_SUPERNODE_IP_P2P, ownPort=HARDCODED_SUPERNODE_PORT_P2P, is_first=True).start()
    else:
        isSupernode = args.supernode
        # If not a supernode:
        if not isSupernode:
            recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            recv_sock.bind(('',5000))
            # and if the port-forwarding is configured
            if args.port_forward:
                ownIP, ownPort = CNode_helper.get_own_addr(recv_sock)
                print(f'ip: {ownIP}, port: {ownPort}')

                bootstrapSendID, bootstrapRecvID = bootstrap_connect(ownIP, ownPort, HARDCODED_SUPERNODE_IP, HARDCODED_SUPERNODE_PORT,recv_sock,False)

                mainListener = MainListener(isSupernode, ownIP, ownPort, bootstrapSendID, bootstrapRecvID, False)
                mainListener.start()

if __name__ == "__main__":
    main()
