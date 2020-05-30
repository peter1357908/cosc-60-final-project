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
HARDCODED_SUPERNODE_IP_DOTLESS = "104055097253"
HARDCODED_SUPERNODE_PORT = 5000

SUPERNODE_LOOPBACK_IP = "127.0.0.1"

'''
    bootstrap_connect attempts to connect to supernodeIP:supernodePort by using cnode_helper's connect and join
    Takes an argument from the main program denoting whether to join as a supernode or regular node
    Returns (sendID, recvID) for successful connect and join; returns None (or gets blocked) otherwise
'''
def bootstrap_connect(ownIP, ownPort, supernodeIP, supernodePort, as_supernode=False):
    sendID = CNode_helper.connect_p2p(ip=supernodeIP, port=supernodePort)
    # assuming that 0 is the "bad case"
    if sendID == 0:
        return None
    if as_supernode:
        recvID = CNode_helper.join_p2p(sendID, ownIP, ownPort, 1)
    else:
        recvID = CNode_helper.join_p2p(sendID, ownIP, ownPort, 0)
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
        mainListener = MainListener.MainListener(
            isSupernode=True, ownIP=HARDCODED_SUPERNODE_IP_DOTLESS, ownPort=HARDCODED_SUPERNODE_PORT, is_first=True).start()
    else:
        isSupernode = args.supernode
        # If not a supernode:
        if not isSupernode:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # and if the port-forwarding is configured
            if args.port_forward:
                ownIP, ownPort = CNode_helper.get_own_addr(sock)

                bootstrapSendID, bootstrapRecvID = bootstrap_connect(ownIP, ownPort, HARDCODED_SUPERNODE_IP, HARDCODED_SUPERNODE_PORT, False)

                mainListener = MainListener.MainListener(isSupernode, ownIP, ownPort, bootstrapSendID, bootstrapRecvID, False)
                mainListener.start()

if __name__ == "__main__":
    main()
