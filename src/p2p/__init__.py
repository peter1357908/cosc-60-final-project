#! /usr/bin/python3

import InputListener
import MessageListener
import FileInfoTable

# Alright, So this will attempt to connect to the default supernode.
# If the connection is successful, then the __init__ file will begin the two main threads

# TODO: Parse the arguments
# If the node is a supernode, supernodeIP is loopback / 127.0.0.1
supernodeIP = 'parsed'

# If a supernode, also include a ChildNodeTable and SupernodeTable

table  = FileInfoTable()


# Attempt to connect to the supernode:
#####

# TODO: MRT CODE GOES HERE


#####

# If not successful:
    # Print out error message and system.exit(1)

# If successful:

    # Begin The User Input Thread
    # TODO: Arguments to be passed to InputListener instantiation
    inputListener = InputListener(supernodeIP, table)
    inputListener.start()
    

    # Begin The Packet / Message Listener Thread
    # TODO: Arguments to be passed to MessageListener instantiation
    messageListener = MessageListener(table)
    messageListener.start()

