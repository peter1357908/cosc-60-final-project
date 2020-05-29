#! /usr/bin/python3

import InputListener
import MainListener
sys.path.append('../data-structures/')
import FileInfoTable
import argparse
import CNode_helper
import mrt
import sys


# CONST VARIABLES
# TODO: need to change this to an established supernode
HARDCODED_SUPERNODE_IP = "127.0.0.1"
HARDCODED_SUPERNODE_PORT = "5000"

SUPERNODE_LOOPBACK_IP = "127.0.0.1"

"""
    supernode_connect attempts to connect to HARDCODED_SUPERNODE_IP:HARDCODED_SUPERNODE_PORT by using cnode_helper's connect and join
    Takes an argument from the main program denoting whether to join as a supernode or regular node
    Returns True for successful connect and join, False otherwise
"""
def supernode_connect(as_supernode=False):
    supernode_id = CNode_helper.connect_p2p(ip=HARDCODED_SUPERNODE_IP, port=HARDCODED_SUPERNODE_PORT)
    # assuming that 0 is the "bad case"
    if supernode_id == 0:
        return None

    if as_supernode:
        CNode_helper.join_p2p(1)
    else:
        CNode_helper.join_p2p(0)
    return supernode_id

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
    args = parser.parse_args()

    # If the node is a supernode, supernodeIP is loopback / 127.0.0.1
    # TODO: If the node is joining as a supernode & the network already 
    # If the node is a childnode, then the IP of the supernode to be joined is an arg
    isSupernode = False
    supernodePort = None
    if args.supernode:
        isSupernode = True

    # The file info table to hold the files
    # used by regular node and supernode regardless
    table  = FileInfoTable()

    # if supernodeIP == SUPERNODE_LOOPBACK_IP:
    #     cnodeTable = ChildrenInfoTable()
    #     snodeList = []
    #     pass

    # Attempt to connect to the supernode:
    if isSupernode:
        print("attempting to connect to default supernode AS a supernode")
        # connID = supernode_connect(True)
    else:
        print("attempting to connect to default supernode AS a child node")
        # connID = supernode_connect(False)

    print("connection is good")

    # If not connId:
    # if not res:
    #     print(f"failed to connect to supernode at address {HARDCODED_SUPERNODE_IP}:{HARDCODED_SUPERNODE_PORT}")
    #     exit(-1)

    # Begin The User Input Thread
    inputListener = InputListener(isSupernode, table)
    inputListener.start()
    
    # Begin The Packet / main Listener Thread
    mainListener = MainListener(isSupernode, table)
    MainListener.start()

if __name__ == "__main__":
    main()