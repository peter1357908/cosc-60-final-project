#! /usr/bin/python3

import InputListener
# import MessageListener
# import FileInfoTable
import argparse
import CNode_helper


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
    supernode_idobj = CNode_helper.connect_p2p(ip=HARDCODED_SUPERNODE_IP, port=HARDCODED_SUPERNODE_PORT)
    if not supernode_idobj:
        return False

    if as_supernode:
        CNode_helper.join_p2p(1)
    else:
        CNode_helper.join_p2p(0)

    return True

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
    # If the node is a childnode, then the IP of the supernode to be joined is an arg
    supernodeIP = None
    supernodePort = None
    if args.supernode:
        supernodeIP = SUPERNODE_LOOPBACK_IP

    # The file info table to hold the files
    # used by regular node and supernode regardless
    # table  = FileInfoTable()
    # TODO: instantiate tables
    table = None

    if supernodeIP == SUPERNODE_LOOPBACK_IP:
        # If a supernode, then the childnode and supernode tables will be intantated
        # in the INputListener thread, since it can check if supernode ip == loopback,
        # and if so instantiate ChildNodeTable and SupernodeTable
        # TODO: instantiate tables
        pass

    # Attempt to connect to the supernode:
    if supernodeIP == SUPERNODE_LOOPBACK_IP:
        print("attempting to connect to default supernode AS a supernode")
        res = supernode_connect(True)
    else:
        print("attempting to connect to default supernode AS a child node")
        res = supernode_connect(False)

    # If not successful:
    if not res:
        print(f"failed to connect to supernode at address {HARDCODED_SUPERNODE_IP}:{HARDCODED_SUPERNODE_PORT}")
        exit(-1)

    # Begin The User Input Thread
    inputListener = InputListener(supernodeIP, table)
    inputListener.start()
    
    # Begin The Packet / Message Listener Thread
    messageListener = MessageListener(table)
    messageListener.start()

if __name__ == "__main__":
    main()