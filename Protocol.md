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

| Type | Value Length (in bytes) |
| ---- | ---- |
| Source IPv4 | Source IPv4 | 
| Value | Value . . . |

"Type" is a 2-byte value that specifies if the message is a(n):

*  Post - "0x0001"
*  Request - "0x0101"
*  File-transfer - "0x1111"
*  Indication of error - "0x0000"

Where "Message Length" is the length of the `value` part of the message (depends on the message type).

The "Source IPv4" address is the address of the initial creator of the message, in case the message needs to be forwarded.

"Value" is a function-specific field with arbitrary length.

## Types of Messages

### Requests:

* Request to join the network - "0x000a"
* Request for a supernode's supernode list - "0x000b"
* Request for a supernode's Local-DHT - "0x000c"
* Request for all DHT entries in the network - "0x000d"
* Request for a file-transfer - "0x000e"

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

  | 000a | request type |
  | ---- | ---- |

  `request type` will be `0000` for a regular node join request, and `0001` for a supernode join request, and `0002` for a relayed supernode join request (see below)

* Response:

  * If `request type` is `0000` or `0001`, the receiver sends the following response to the requester.

    | 100a | number of supernode list entries in this response |
    | ---- | ---- |
    | supernode list | supernode list . . . |
  
  * If `request type` is `0001` or `0002`, the receiver adds the IP address specified in `Source IPv4` to its supernode list.
  
  * If `request type` is `0001`, the receiver also needs to send the following request to all supernodes it knows with the same `Source IPv4` as the request message:

    | 000a | 0002 |
    | ---- | ---- |
  
  
  
#### Request for a supernode's supernode list:

* Request:

  | 000b |
  | ---- |
  
  (Only the type field is necessary)

* Response:

  | 100b | number of supernode list entries in this response |
  | ---- | ---- |
  | supernode list | supernode list . . . |
  
#### Request for a supernode's Local-DHT:

* Request:

  | 000c |
  | ---- |
  
  (Only the type field is necessary)


* Response:

  | 100c | number of Local-DHT entries in this response |
  | ---- | ---- |
  | Local-DHT | Local-DHT . . . |
  
#### Request for all DHT entries in the network:

* Request:

  | 000d |
  | ---- |
  
  This request should be sent from a child node (a supernode should directly use request type `000c`) to a supernode (which does not have to be its bootstrapping supernode).

* Response:

  There is no direct response; the supernode that receives the request will query all the supernodes it knows and forward all the responses (type `100c`) to the requester.


#### Request for a file-transfer:*

* Request:

  | 000e | File ID length (in bytes) |
  | ---- | ---- |
  | File ID | File ID . . . |

  This message is sent to a node which supposedly offers this file (for UDP-holepunching) **AND** to the supernode that is the bootstrapping node for that sharing node (unless the sharing node is a supernode).

  There is no direct response to this request; if the receiving node is a:
  
  * supernode:
    
    * If the supernode's IP is the same as `Source IPv4`, this means that it just received the dummy message meant for UDP-holepunching; ignore it.
    * Else if the requested file is offered by the supernode, "forward" the exact same message to the node specified by `Source IP` for UDP-holepunching.
    * Else, the supernode should "forward" the exact same message (same `Source IPv4`) to the child node that offers the file as specified by `File ID`.
    
  * child node:
    
    * If the child node's IP is the same as `Source IPv4`, this means that it just received the dummy message meant for UDP-holepunching; ignore it.
    * Else, child node should "forward" the exact same message (same `Source IPv4`) to the node specified by `Source IP` for UDP-holepunching.

---

### Posts:

* Notification for offering a new file - "0x000a"
* Notification for intention to disconnect - "0x000b"

#### Notification for offering a new file:

* Post:

  | 000a | File Size (in bytes) |
  | ---- | ---- |
  | File ID length (in bytes) | File ID . . . |

  `File Size` is the size of the file in bytes (originally number of fragments).

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

* A file-transfer message contains the binary data of the file being transferred. (There is only one kind of file-transfer message - type `000a`)

  | 000a | data... |
  | ---- | ---- |

  The node that is to receive the file-transfer is responsible for keeping track of which file it is downloading and if it has fully received the file.

  (we could also put file ID length and file ID in the message to allow easy book-keeping) <--- We definitely need to, else we have no idea what is happening if we have multiple request - Vlado

  (No response is necessary.)

