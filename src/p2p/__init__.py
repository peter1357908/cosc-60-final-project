#! /usr/bin/python3

import InputListener
import MessageListener
import FileInfoTable

# Alright, So this will attempt to connect to the default supernode.
# If the connection is successful, then the __init__ file will begin the two main threads

# TODO: Parse the arguments

# TODO: Currently need to specify input argument for determining if the node is
# joining as a supernode or childnode.



# If the node is a supernode, supernodeIP is loopback / 127.0.0.1
# If the node is a childnode, then the IP of the supernode to be joined is an arg
supernodeIP = 'parsed'

# The file info table to hold the files
table  = FileInfoTable()

# If a supernode, then the childnode and supernode tables will be intantated
# in the INputListener thread, since it can check if supernode ip == loopback,
# and if so instantiate ChildNodeTable and SupernodeTable


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

