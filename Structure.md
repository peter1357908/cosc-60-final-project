**This file details the responsibilites of a supernode and a child node.**

Some assumptions:
1. Supernodes never disconnect.
2. There is always 1 supernode online.

**Supernodes**

I think I should begin by discussing the jobs of a supernode:
*  Connect a limited number of child nodes
*  Maintiain a local Distributed Hash Table
*  Connect to other Supernodes
*  Offering files for download (see child explanation)
*  Download files (see child explanation)

And go through these one by one.

*Connect a limited number of child nodes:*

The supernode acts as a bootstrapper for nodes wanting to join the network. From 
the child nodes' perspective, the child only has one neighbor: the supernode. This way,
the supernode can manage local requests for information. *The supernode does not act as a middle man during downloads.*
The supernode should be behind a static NAT, for convienence. 

*Maintain a Local DHT*

A "Local-DHT" is a hash table which contains all of the files offered by the supernode
and its children. The local DHT is instantiated with the files the supernode itself offers.
It is updated by "New File" and "Node Disconnecting" posts by the supernode's children.
The Local DHT is requested by child nodes and other supernodes when a node sends out a 
"request for available files" request. A child node of a supernode will never
request another supernode's local-DHT. That will always be done through the child's 
corresponding supernode. Only supernodes only talk to other supernodes and their children
when exchanging information. (An exception would be if a child of another supernode requested
a file download from a supernode which was offering the file.)

*Connect to other Supernodes*

Each supernode maintians a table of all of their neighboring supernodes by IP address,
so it is able to inform its children how many supernodes there are. Supernodes also use this
table to ask other supernodes for their respective Local-DHT's when a client requests
available files.

-----

**Children**

The responsibilities of a child node are:

*  Connect to a single supernode and nobody else
*  Offer files for download
*  Download Files

*Connect to a Single Supernode and Nobody Else*

By connecting to just one node, the child ensures that its information requests
are reliable and distributed among the network. It also makes connecting and
disconnecting from the network clean and simple.

*Offer Files for Download*

It is the child's job to offer files for download. It does this by notifying its 
corresponding supernode whenever it is offering a file.

*Download Files*

Both the child and the supernode download files from from other nodes by connecting
to them directly. 

-----

This document can also house more specific information about data structures and the like,
but currently it is just a high-level overview of Supernodes and Child nodes.
