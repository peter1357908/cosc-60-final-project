### This file details the responsibilites of different types of nodes (supernodes, child nodes)

---

### All nodes can:

*  Offer files for download
*  Download files

*Offer Files for Download*

A child node can offer files for download by notifying its parent supernode;
a supernode can offer files for download by updating its Local Distributed Hash Table.

*Download Files*

Both the child and the supernode can download files from other nodes by directly
connecting to the node(s) that offer the file (the information on who has which file is
stored in Local Distributed Hash Tables and distributed by supernodes).

---

### Supernodes should:

*  Remain online
*  Connect to a limited number of child nodes
*  Maintiain a Local Distributed Hash Table
*  Connect to other Supernodes

*Remain online:*

The supernodes are essential for keeping the network operational by bootstrapping
newly joining nodes, maintain its existing children, and exchanging meta-information
with other supernodes, and thus should remain online (if no supernodes are online,
the network is considered offline).

*Connect to a limited number of child nodes:*

The supernode acts as a bootstrapper for nodes wanting to join the network. From 
the child nodes' perspective, the child only has one neighbor: the supernode. This way,
the supernode can manage local requests for information. *The supernode does not act as a middle man during downloads.*
(it is not responsible for relaying the actual download/upload stream).
The supernode should be behind either a static NAT or no NAT, for convienence.

To ensure stability, a supernode should only connect to a limited number of child nodes.
The more supernodes a network has, the more child nodes it can accommodate.

*Maintiain a Local Distributed Hash Table*

A "Local-DHT" is a hash table which contains all of the files offered by the supernode
and its children. The local DHT is instantiated with the files the supernode itself offers.
It is updated by "New File" and "Node Disconnecting" posts by the supernode's children.
The Local DHT is requested by child nodes and other supernodes when a node sends out a 
"request for available files" request. A child node of a supernode will never
request another supernode's local-DHT. That will always be done through the child's 
corresponding supernode. A supernode can only talk to its children and other supernodes
when exchanging meta-information, but it can uploading to/download from all nodes in the network.

*Connect to other Supernodes*

Each supernode maintians a table of all of their neighboring supernodes by IP address,
mainly so it can ask other supernodes for their respective Local-DHT's. This table also enables
a supernode to inform its children on how many supernodes are currently online.

---

### Child nodes should:

*  Connect to one and only one supernode

*Connect to one and only one supernode*

By connecting to a supernode, the child ensures that its information requests
are heard and orderly distributed. Since a child connects to only one supernode,
it is clean and simple to handle nodes joining and quitting the network.

-----

This document can also house more specific information about data structures and the like,
but currently it is just a high-level overview of Supernodes and Child nodes.
