#! /usr/bin/python3

import threading
from MainListener import *
import sys
sys.path.append('../data-structures/')
import argparse
import socket
import CNode_helper

# CONST VARIABLES
HARDCODED_BOOTSTRAP_IP = "35.212.76.82"
HARDCODED_BOOTSTRAP_IP_P2P = "035212076082"
HARDCODED_BOOTSTRAP_PORT = 5000
HARDCODED_BOOTSTRAP_PORT_P2P = "05000"

HARDCODED_SUPERNODE_IP = "35.245.175.182"
HARDCODED_SUPERNODE_IP_P2P = "035245175182"
HARDCODED_SUPERNODE_PORT = 5000
HARDCODED_SUPERNODE_PORT_P2P = "05000"


'''
    bootstrap_connect attempts to connect to supernodeIP:supernodePort by using cnode_helper's connect and join
    Takes an argument from the main program denoting whether to join as a supernode or regular node
    Returns (sendID, recvID) for successful connect and join; returns None (or gets blocked) otherwise
'''
def bootstrap_connect(ownIP, ownPort, bootstrapperIP, bootstrapperPort, recv_sock, as_supernode):
    print(f'bootstrapping....')
    sendID = CNode_helper.connect_p2p(bootstrapperIP, bootstrapperPort)
    # assuming that 0 is the "bad case"
    print(f'connected...')
    if sendID == 0:
        return None
    if as_supernode:
        # TODO: no magic numbas plz
        recvID = CNode_helper.join_p2p(recv_sock, sendID, bootstrapperIP, 5001, ownIP, ownPort, 1)
    else:
        recvID = CNode_helper.join_p2p(recv_sock, sendID, bootstrapperIP, 5001, ownIP, ownPort, 0)
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
    args = parser.parse_args()

    # TODO: join as a childnode

    ### Logic for first ever supernode 
    if args.first:
        print(f'starting up as first ever supernode')
        # TODO: we should find a way to get own IP and Port without STUN for supernodes
        # TODO: we should not hardcode first node's IP and Port
        mainListener = MainListener(isSupernode=True, ownIP=HARDCODED_BOOTSTRAP_IP_P2P, ownPort=HARDCODED_BOOTSTRAP_PORT_P2P, is_first=True)
        mainListener.start()
    else:
        isSupernode = args.supernode
        if isSupernode:
            recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            recv_sock.bind(('',5000))

            bootstrapSendID, bootstrapRecvID = bootstrap_connect(HARDCODED_SUPERNODE_IP_P2P, HARDCODED_SUPERNODE_PORT_P2P, HARDCODED_BOOTSTRAP_IP, HARDCODED_BOOTSTRAP_PORT, recv_sock, True)

            mainListener = MainListener(True, HARDCODED_SUPERNODE_IP_P2P, HARDCODED_SUPERNODE_PORT_P2P, bootstrapSendID, bootstrapRecvID, HARDCODED_BOOTSTRAP_IP_P2P, HARDCODED_BOOTSTRAP_PORT_P2P, False)
            mainListener.start()
        else:
            recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            recv_sock.bind(('',5000))

            ownIP, ownPort = CNode_helper.get_own_addr(recv_sock)

            bootstrapSendID, bootstrapRecvID = bootstrap_connect(ownIP, ownPort, HARDCODED_BOOTSTRAP_IP, HARDCODED_BOOTSTRAP_PORT, recv_sock, False)

            mainListener = MainListener(False, ownIP, ownPort, bootstrapSendID, bootstrapRecvID, HARDCODED_BOOTSTRAP_IP_P2P, HARDCODED_BOOTSTRAP_PORT_P2P, False)
            mainListener.start()

if __name__ == "__main__":
    main()
