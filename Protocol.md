# Protocol Write-up

**Gao, Ma, Parker, Foye, and Vojdanovski**

## Protocol Overview

The [requirements](https://canvas.dartmouth.edu/courses/39576/assignments/234934) for the lab
stipulate that the protocol is built on a reliable form of UDP, which Matt has
offered us to use.

Before reading this, familiarize yourself with the jobs of supernodes and child
nodes [here](https://gitlab.cs.dartmouth.edu/hyperistic/cosc-60-final-project/blob/master/Structure.md).

Note: this document uses GitHub tables to represent the structure of a packet. Each cell
of a table should correspond to a 2 byte field. If a field ends with an ellipsis, you
should assume that the field has arbitrary length (arbitrary multiple of 2 bytes).

The general structure of a packet on our network will be:

| UDP  |
| ---- |
| Matt's MRT Protocol |
| This module's P2P Protocol |

Our protocol will hope to account for the following types of messages:

*  Posts
*  Requests
*  File-transfer

Where "Posts" are notifications of new information, "Requests" are
requests for some unknown information, and "File-transfers" are the special case
where a file is being transferred between a requesting node and an offering node.

Our P2P Protocol will be partitioned as follows, with each partition 
being 2 bytes in length:

| Type | Message Length |
| ---- | ---- |
| ID part 1 | ID part 2 |
| IPv4 part 1 | IPv4 part 2 | 
| Value part 1| Value . . . |

"Type" is a 2-byte value that specifies if the message is a(n):

*  Post - "0x0001"
*  Request - "0x0101"
*  File-transfer - "0x1111"
*  Indication of error - "0x0000"

Where "ID" is a unique/random message id so messages are not repeated. 
Nodes store these ID's in a regularly cleared cache (every 6 hrs, perhaps) so that
if they can ignore/drop a duplicate message.

Where "Message Length" is the length of the packet, except when the message type is
a file-transfer, in which case it is the total number of fragments that make up the file.

The "IPv4" address is the address of the initial creator of the message, i.e. the 
node posting new info or requesting info.

Here, "Value" is a function-specific field which can be longer than 4 bytes.

## Types of Messages

### Requests:

* Request to join the network - "0x000a"
* Request for a supernode's neighbor list - "0x000b"
* Request for a supernode's Local-DHT - "0x000c"
* Request for a file-transfer - "0x000d"

Typical Request Value:

| Type | Misc |
| ---- | ---- |
| Data | Data |
| Data | Data . . . |

Where "Type" is the request type. I provided some preliminary values for what
each request value might correspond to.

"Misc" is a context-specific value.

#### Request to Join:

* Request:

  | 000a | node type |
  | ---- | ---- |

  `node type` will be `0000` for a child node, and `0001` for a supernode.

* Response:

  | 100a | number of neighbor list entries in this response |
  | ---- | ---- |
  | Neighbor list | Neighbor list . . . |

  When a node sends a request to join to a bootstrapping node (supernode), the bootstrapping node acknowledges the join attempt by sending back its list of neighboring supernodes.
  The neighbor list in the response should not include the joining node (in case the node wants to join as a supernode).

#### Request for a supernode's neighbor list:

* Request:

  | 000b |
  | ---- |
  
  (Only the type field is necessary)


* Response:

  | 100b | number of neighbor list entries in this response |
  | ---- | ---- |
  | Neighbor list | Neighbor list . . . |

  Besides the type field, this response is the same as the response to a `Request to Join`.
  
#### Request for a supernode's Local-DHT:

* Request:

  | 000c |
  | ---- |
  
  (Only the type field is necessary)


* Response:

  | 100c | number of Local-DHT entries in this response |
  | ---- | ---- |
  | Local-DHT | Local-DHT . . . |


#### Request for a file-transfer:*

* Request:

  | 000d | Source IP |
  | ---- | ---- |
  | File ID length (in bytes) | File ID . . . |
  
  The `Source IP` is the IP address of the node that sent this request.

  This message is sent to a node which supposedly offers this file (for UDP-holepunching) **AND** to the supernode that is the bootstrapping node for that sharing node (unless the sharing node is a supernode).

  There is no direct response to this request; if the receiving node is a:
  
  * supernode:
    
    * If the supernode's IP is the same as `Source IP`, this means that it just received the dummy message meant for UDP-holepunching; ignore it.
    * Else if the requested file is offered by the supernode, "forward" the exact same message to the node specified by `Source IP` for UDP-holepunching.
    * Else, supernode should "forward" the exact same message to the child node that offers the file as specified by `File ID`.
    
  * child node:
    
    * If the child node's IP is the same as `Source IP`, this means that it just received the dummy message meant for UDP-holepunching; ignore it.
    * Else, child node should "forward" the exact same message to the node specified by `Source IP` for UDP-holepunching.

---

### Posts:

* Notification for offering a new file - "0x000a"
* Notification for intention to disconnect - "0x000b"

#### Notification for offering a new file:

* Post:

  | 000a | File Size (in bytes) |
  | ---- | ---- |
  | File ID length (in bytes) | File ID . . . |

  `File Size` is the size of the file in fragments.

  This message must be from a child node to its bootstrapping node.
  
  (When a supernode offers a new file, all it has to do is update its local-DHT; it should not send any `Post` messages)

  (No response is needed.)
  

#### Notification for intention to disconnect

* Post:

  | 000b |
  | ---- |

  A node would send this message to its bootstrapping node.
  
* Response:

  | 100b |
  | ---- |

  This response indicates that all clean-ups have been performed so the posting node can safely disconnect.

---

### File-transfer

A file-transfer message contains the binary data of the file being transferred.
There is only one kind of file-transfer message (type `000a`).

| 000a | Total Number of Fragments |
| ---- | ---- |
| Current Fragment Number | data... |

(No response is necessary.)

