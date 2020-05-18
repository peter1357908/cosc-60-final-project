### This file details the responsibilites of different types of nodes (supernodes, child nodes)

---

### ALL nodes can:

*  Offer files for download
*  Download files
*  Query supernodes for their list of neighbor supernodes
*  Query supernodes for their Local-DHT

*Offer Files for Download*

A child node can offer files for download by notifying its bootstrapping node (a supernode it connected to for joining the network);
a supernode can offer files for download by updating its Local Distributed Hash Table.

*Download Files*

Both child nodes and supernodes can download files from other nodes by directly
requesting them from the node(s) that offer the file.

*Query supernodes for their list of neighbor supernodes*

Each node should be able to query any supernodes it knows (an initial list of supernodes is obtained upon joining the network, from the bootstrapping node it connected to) for their list of neighbor supernodes.

*Query supernodes for their Local-DHT*

Each node should be able to query any supernodes it knows for their Local-DHT.

---

### Supernodes should:

*  Remain online
*  Pair with a limited number of child nodes
*  Maintain a list of neighboring supernodes
*  Maintiain a Local Distributed Hash Table

*Remain online:*

The supernodes are essential for keeping the network operational by bootstrapping
newly joining nodes, maintain its existing children, and exchanging meta-information
with other supernodes, and thus should remain online (if no supernodes are online,
the network is considered offline).

*Pair with a limited number of child nodes:*

The supernode acts as a bootstrapper for nodes wanting to join the network. 
Since it has to be directly available for query, the supernode should be behind either a static NAT or no NAT.

To ensure stability, a supernode should only pair with a limited number of child nodes - once a child node is bootstrapped, it is considered *paired* with the bootstrapping supernode until it disconnects. This is to ensure that the Local-DHT in each supernode does not get too big.
The more supernodes a network has, the more child nodes it can accommodate.

*Maintain a list of neighboring supernodes*

Each supernode maintians a list of all of their neighboring supernodes. This list can be requested by all other nodes with "request list" request, and is sent to the child node when it is being bootstrapped ("request to join").

*Maintiain a Local Distributed Hash Table*

A "Local-DHT" is a hash table which contains all of the files offered by the supernode
and its paried child nodes. The Local-DHT is instantiated with the files the supernode itself offers.
It is updated by "New File" and "Node Disconnecting" posts by the supernode's paired child nodes.
The Local-DHT can be requested by all other nodes with
"request for available files" request.

---

### Child nodes should:

*  Let its bootstrapping node know when it disconnects

*Let its bootstrapping node know when it disconnects*

Since the list of files offered by the child node is maintained by its bootstrapping node, the child node is obligated to notify its bootstrapping node of its intention to disconnect (and thus stop offering those files).

-----

This document can also house more specific information about data structures and the like,
but currently it is just a high-level overview of Supernodes and Child nodes.
