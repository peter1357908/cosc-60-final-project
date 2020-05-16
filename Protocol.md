**Protocol Writeup for Gao, Ma, Parker, Foye, and Vojdanovski**

The [requirements](https://canvas.dartmouth.edu/courses/39576/assignments/234934) for the lab
stipulate that the protocol is built on a reliable for of UDP, which Matt has
offered us to use.

Before reading this, familiarize yourself with the jobs of supernodes and child
nodes here. (Hyperlink is on its way. Writing this document now.)

So, the general structure of a packet on our network will be:

| UDP |
| ----- |
| Matt's Protocol | 
| Our P2P Protocol |  

Our protocol will hope to account for the following types of messages:

*  Posts
*  Requests
*  Downloads

Where "Posts" are some sort of notification of new information, "Requests" are
requests for some unknown information, and "Downloads" are the special case
where the file is being transferred across the network.

Our P2P Protocol will have the general structure, which each partition corresponding
to 2 bytes:

| Type | Message Length |
| ------ | ------ |
| ID | ID |
| IPv4 | IPv4 | 
| Value | Value . . . |

"Type" is a 2-byte value that specifies if the message is a:
*  Request for Information - "0x0001"
*  Notification / Post of New Information "0x0101"
*  A Download-in-Progress "0x1111"
*  An invalid packet response / error response "0x0000"

(I included some preliminary byte values for each type, open to change.)


Where "ID" is a unique/random message id so messages are not repeated. 
Nodes store these ID's in a regurarily cleared cache (every 6 hrs, perhaps) so that
if they received a duplicate, flooded message they can ignore it.

Where "Message Length" is the length of the packet, except when the message type is
a download, in which case it is the total number of fragments that make up the file.

The "IPv4" address is the address of the initial creator of the message, i.e. the 
node posting new info or requesting info.

Here, "Value" is a function-specific field which can be longer than 4 bytes.

The functions / value-fields which we are implementing are:

**Requests:**
* A request to connect to a bootstrapping node "0x000a"
* A request for available files "0x000b"
* A request for a download  "0x000c"

Typical Request Value:

| Type | Misc |
| ------ | ------ |
| Data | Data |
| Data | Data . . . | 

Where "Type" is the request type. I provided some preliminary values for what
each request value might correspond to.

"Misc" is a context-specific value.

Note: it looks like the messages could be slightly different for supernodes and
children nodes. I will try and specify where and how they are different.

*Request to Connect:*

*Client Version:*

Initial Request:

| 000a | null / zeros |
| ------ | ------ |
| null | null |

No data is required for a request to connect

Response:

| 1000a | total # of supernodes |
| ------ | ------ |
| Local-DHT | Local-DHT . . . |

When a node connects to a bootstrap node for the first time, the bootstrap node
acknowledges the connection by sending back the available files of the bootstrap
node's children. (One of which being the newly-connected node.) Here, "Local-DHT"
means the part of the DHT which resides on the children of the bootstrapping node.
That is to say, not necessarily the entire DHT. This is just a way to kill two
birds with one stone. However, if we decided to not have anything in the connection 
acknowledgement, that would be reasonable too. 

(An aside: we decided that bootstrap nodes would operate as super-nodes, with
children who each held part of the DHT. The supernode would be connected to other
supernodes, with their own children. A child would interact with its corresponding
parent-supernode by connecting to it & asking for information, i.e. the contents
of the DHT. The supernode would then reach out to its children / other supernodes
for their parts of the DHT and return it to the child who requested the information.)

I want the response to include the total # of supernodes because of the way the protocol
could handle requests for available files, see below in "Request for available files"

*Supernode Version:*

When someone wants to join the network as a supernode, they should send a specific
packet to its specified supernode neighbor, with the Misc value being non-zero

Request:

| 000a | 1111 |
| ------ | ------ |
| null | null |
| null | null | 

Response:

| 100a | number of supernodes |
| ------ | ------ |
| Supernode list | Supernode list . . . |

The response to a supernode-join request should not contain the local DHT, but 
instead the current list of supernodes and number of supernodes.

*Request for available files:*

Request:

| 000b | length |
| ------ | ------ |
| null | null |

No data is needed when requesting information.
I'm not clear on to whom these requests should be sent. My guess is to send them to the respective supernode
and have them handle it by passing it on to their neighboring supernodes, who pass it on to their 
neighbors, and so on...


Response:

| 100b | supernode #'s' |
| ------ | ------ |
| DHT | DHT . . . |

I think this response packet would be crafted by the supernodes with their respective Local-DHT's throughout the network,
and sent back to the requesting node with a corresponding supernode number. Once the node has
responses from every supernode, it knows it has all the data. It can then remove the repeated values
and have all of the DHT. It can clear those stored values by / update them by sending out another 
Request for available files.


*Request for a Download:*

Request:

| 000c | null |
| ------ | ------ |
| ID of file | ID of file . . . |

This message is sent to out to a node which is supposed to contain this file. 

The response to this request is a the attempt to open a download stream.

If there is no response to this message after a TTL, then the node might be offline.
This should then prompt another request for the DHT.
(There is room for optimization here by reaching out to the supernode of the "offline"
device to see if it is really offline instead of sending a network-wide flood. That can
come later though, as it requires additional info, such as which node belongs to who, etc.)

-------

**Posts:**
* A notification that the node offers a new file (this is akin to notification that a node joined the network) "0x000x"
* A notification that the node is leaving the network "0x000y"

*Notification the Node Offers a New File:*

Post:

| 000x | File ID |
| ------ | ------ |
| File Name | File Name . . . |
| File Size | File Size | 

More bytes can be allotted for each field, but I think that 4 bytes per is not too
bad. I could see much more being needed for "File Name."" File Size is the size 
of the file in MB.

I think that this message only needs to be sent to the node's corresponding supernode
so it can update its Local DHT.


No response is needed.

*Notification that a Node is leaving the Network:*

Post:

| 000y | null |
| ------ | ------ |
| null | null |

A node would send this message to its corresponding supernode. The supernode handles
the message by removing the files associated with the senders IP from the DHT.

Note: Any requests-to-download to this IP address will now be dropped.

**Downloads: "0x1111**
A download message contains the actual data of the file being downloaded.
There is only one kind of download message, so a Type of 0000 is fine.

| 0000 | Current Fragment of File |
| ------ | ------ |
| data | data |
| data | data . . . | 

This packet (and all packets are) is a fixed size, where the last packet in the stream is 0-padded. 
Once the downlaoding node has acknowledged as many packets as the file is specified to have,
it knows it has all of the file and the download will end.



