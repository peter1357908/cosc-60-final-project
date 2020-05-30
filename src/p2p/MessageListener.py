#! /usr/bin/python3

# Message Listener Thread:

import threading
import File
import FileInfoTable
import sys
sys.path.append('../mrt/')
sys.path.append('../data-structures/')
import mrt
#import SNode_helpers

class MessageListener(threading.Thread):

    # Initialize MessageListener Thread
    # TODO: Add paramaters as arguments are determined
    def __init__(self, mainListener, connID):
        self.threading.Thread.__init__(self)
        # Main Listener 
        self.mainListener = mainListener
        # Connection ID
        self.connID = connID

        self.manager = mainListener

    # Methods for handling each parsed method:
    # A note on the following methods: 'file' is always a File object
    # and 'files' is an array of File objects

    # Accept a new connection
    def acceptConnection(self, connectedIP):
        #TODO: Add the connected IP to the list of child nodes
        pass
        

    # Accept a new supernode connection. This message will only be received by supernodes
    def acceptSupernodeConnection(self, connectedIP):
        #TODO: add the connected IP to the list of connected supernodes
        pass

    # Process a child node disconnecting. Currently, supernodes cannot disconnect without 
    # Shutting down the network.
    def processDisconnect(self, disconnectedIP):
        # TODO: remove the disconnected IP from the list of child nodes
        # Also remove the files offered by disconnectedIP from HT
        pass

    # Add a list of File objects to the HT:
    def addFiles(self, files):
        # TODO: For every file in files, add that file to the HT & print a debug statement
        pass
    
    # Remove a list of File objects from the HT:
    def removeFiles(self, files):
        # TODO: For every file in files, remove file from the HT
        pass

    # Send back local-DHT
    def sendBackHT(self, destinationIP):
        # TODO: Craft Requests for Local DHT's from all the supernodes
        # TODO: Receive the Local DHT's
        # TODO: Put them into packets
        # TODO: Send those packets to the requesting node
        pass
        
    def sendBackLocalHT(self, destinationIP):
        pass
    
    # Accept the request for upload from another client and start sending the file
    def acceptUpload(self, file, destinationIP):
        fileSender = FileSender(file, destinationIP)
        fileSender.start()
        pass
    
    # When a download message is received but the destination is not the current node
    # pass on the packet to the appropriate node:
    def passOn(self, destinationIP):
        # TODO: pass on & figure out a way to do so.
        # If the current node is not the supernode of the destination, 
            # pass on the packet to the supernode of that packet
        # Else, if the current node is that child node's (dest.) supernode
            # pass on the packet to the destination.
        pass
        
    def sendBackSupernodeList(self, destinationIP):
        # TODO: Create message to send back supernode list
        # TODO: Send message
        pass

    # TODO: run() method:
    def run(self):
        while True:
            # Accept a packet from the current connID
            packet = mrt.receive1(self.connID)
            
            # TODO: Accept the packet:
            # In java, this is socket.accept(packet)
            packetContents = ""
            
            
            # Parse out the packet packets:
            
            #TODO: Check the type of the packet:
            messageType = 'parsed'
            requestType = 'parsed'
            
            if messageType == "Post":    # If the message is a post:
                # TODO: Now, parse the Post Type:
                postType == "parsed"
                if postType == "New File Offered":   # If the message announces a new file
                    # TODO: parse out necessary info for the file list (usually a list with 1 file)
                    self.addFiles(files)
                elif postType == "Disconnect":    # If the messages announces a disconnect
                    # Note: a child node will never receive this message, since
                    # our network is a "structured" p2p network
                    # TODO: Parse out the disconnecting IP
                    self.processDisconnect(disconnectedIP)
            elif messageType == "Request":    # If the message is a request:
                # TODO: Now, parse the Request Type
                requestType == "parsed"
                if requestType == "Child Join Network":
                    # Note: a child node will never receive this message, since
                    # our network is a "structured" p2p network
                    # TODO: Parse out joining IP
                    self.acceptConnection(connectedIP)
                elif requestType == "Supernode Join Network":
                    # Note: a child node will never receive this message, since
                    # our network is a "structured" p2p network
                    # TODO: Parse out joining IP
                    self.acceptSupernodeConnection(connectedIP)
                elif requestType == "Supernode List":
                    # Note: a child node will never receive this message, since
                    # our network is a "structured" p2p network
                    # TODO: Parse out IP to send Supernode List back to
                    self.sendBackSupernodeList(destinationIP)
                elif requestType == "Local DHT":
                    # Note: a child node will never receive this message, since
                    # our network is a "structured" p2p network
                    # TODO: Parse out IP to send Local DHT back to
                    # TODO: Craft packet with local DHT to send
                    # TODO: Send Packet
                    self.sendBackLocalHT(destinationIP)
                elif requestType == "Request All DHT":
                    # Note: a child node will never receive this message, since
                    # our network is a "structured" p2p network
                    # TODO: Parse out IP to send DHT back to (should be a child node of this node, or it will be itself)
                    self.sendBackHT(destinationIP)
                elif requestType == "File Transfer":
                    # This type of message is used for UDP holepunching.
                    # NOTE: I'm not entirely sure how this works. Is this like a handshake? A hello message?
                    # Perhaps this is used to initiate a download...?
                    # I would assume that this message would start a "File Receiver" Thread
                    # Peter, do you mind writing / commenting this section of the code
                    # Since you devised that aspect of our protocol>?
                    self.acceptDownload(file, destinationIP)
            elif messageType == "File Transfer":  # If the message is a File Transfer / Download:
                # This message contains the binary data of the file.
                # I would assume this message shouldn't be received on this port (5000)
                # but only on the "File Transfer" port (5001) by the "File Receiver " Thread
                # I put passOn here so that messages-in-transit could be sent to this port
                # and messages-arriving-at-destination would be sent to port 5001
                self.passOn(destinationIP)
            elif messageType == "Error Indication":   # If the message is an error:
                # Its error time boyyyeeeee
                # I don't think we specify error types as of now, so this is the default error message:
                print("Unknown message type...now detonating computer.")
            
            else:    # If the Message Type is unknown:
                print("Unknown Message Type.")
            








    
