# Protocol Write-up

**Foye, Gao, Ma, Parker, and Vojdanovski**

## Protocol Overview

The [requirements](https://canvas.dartmouth.edu/courses/39576/assignments/234934) for the lab stipulate that the protocol is built on a reliable form of UDP, which Matt has offered us to use.

Before reading this, familiarize yourself with the jobs of supernodes and child
nodes [here](https://gitlab.cs.dartmouth.edu/hyperistic/cosc-60-final-project/blob/master/Structure.md).

Note: this document uses GitHub Markdown tables to represent the structure of a transmission. Each cell of a table should correspond to a 2 byte field. Fields that end with an ellipsis have arbitrary length.

All number fields (e.g. `Value Length` are binary and in network byte order (as opposed to ASCII/string form).

The general structure of a packet on our network will be:

| UDP  |
| ---- |
| Matt's MRT Protocol |
| This module's P2P Protocol |

Our protocol has following types of transimissions:

*  Posts
*  Requests
*  File-transfer

Where `Posts` are notifications of new information, `Requests` are
requests for some unknown information, and `File-transfers` are the special case
where a file is being transferred between a requesting node and an offering node.

Our P2P Protocol will be partitioned as follows, with each partition 
being 2 bytes in length:

| Type | Message Length (in bytes) |
| ---- | ---- |
| Source IPv4 | Source IPv4 | 
| Source Port | Message ... |

* `Type` specifies if the message is a(n):

  *  Post - "0x0001"
  *  Request - "0x0101"
  *  File-transfer - "0x1111"
  *  Indication of error - "0x0000"

* `Message Length` is the length of the `Message` part of the transmission.

* `Source IPv4` is the IPv4 address of the initial creator of the message, in case the message needs to be forwarded (in network byte order).

* `Source Port` is the port number the source is listening on (in network byte order)

* `Message` is the payload of the transmission (whose composition is specified below).

## Types of Messages

### Requests:

* Request to join the network - "0x000a"
* Request for a supernode's supernode list - "0x000b"
* Request for a supernode's Local-DHT (on all files/one file) - "0x000c"
* Request for all DHT entries (on all files / one file): - "0x000d"
* Request for a file-transfer - "0x000e"

#### Request to join the network:

* Request:

  | 000a | request type |
  | ---- | ---- |

  `request type` will be `0000` for a regular node join request, and `0001` for a supernode join request, and `0002` for a relayed supernode join request (see below)

* Response:

  * If `request type` is `0000` or `0001`, the receiver sends the following response to the requester.

    | 100a | Number of supernode entries | Supernode entries ... |
    | ---- | ---- | ---- |
    
    Each `supernode entry` has the following format:

    | IPv4 | IPv4 | Port |
    | ---- | ---- | ---- |

  * If `request type` is `0000`, the receiver recognizes `(Source IPv4, Source Port)` as a paired childnode (and keep track of it).

  * If `request type` is `0001` or `0002`, the receiver recognizes `(Source IPv4, Source Port)` as a known supernode (and keep track of it).
  
  * If `request type` is `0001`, the receiver also needs to send the following request to all supernodes it knows with the same `(Source IPv4, Source Port)` as the request message:

    | 000a | 0002 |
    | ---- | ---- |
  
#### Request for a supernode's supernode list:

* Request:

  | 000b |
  | ---- |
  
  (Only the type field is necessary)

* Response:

  | 100b | Number of supernode entries | Supernode entries ... |
  | ---- | ---- | ---- |
  
  Each `supernode entry` has the following format:

  | IPv4 | IPv4 | Port |
  | ---- | ---- | ---- |
  
#### Request for a supernode's Local-DHT entries (on all files / one file):

* Request:

  | 000c | File ID length (in bytes) | File ID ... |
  | ---- | ---- | ---- |
  
  If the requester wants all entries, `File ID length` should be `0x0000` (and consequently have nothing for `File ID`).
  
  Else, the requester specifies the file whose entries it wants with `File ID length` and `File ID`.


* Response:

  | 100c | Number of Local-DHT entries | Local-DHT entries ... |
  | ---- | ---- | ---- |
  
  * Each `Local-DHT entry`  has the following format:
  
    | File ID | Number of file entries | File entries ... |
    | ---- | ---- | ---- |

    * Each `File entry` has the following format:

      | Offerer IPv4 | Offerer IPv4 |
      | ---- | ---- |
      | Offerer Port | File Size |
      
      Note that the requesting node should distinguish between different supernodes' response by `(Source IPv4, Source Port)`. Knowing which supernode maintains a Local-DHT entry is necessary for crafting the request `000e` below.
  
  For robust-ness, the supernode should always respond to request `000c` (if no entries are found, respond with `number` being `0x000` and no `Local-DHT entry`).
  
#### Request for all DHT entries (on all files / one file):

* Request:

  | 000d | File ID length (in bytes) | File ID ... |
  | ---- | ---- | ---- |
  
  This request should be sent from a childnode (a supernode should directly use request type `000c`) to a supernode (which does not have to be its bootstrapping supernode).

* Response:

  The supernode that receives the request will perform two tasks if `(Source IPv4, Source Port)` is not its own address:
  
  1. Respond to the requesting node as if the request is of type `000c`
  
  1. Forward the message with type `000c` instead of `000d` to all the supernodes it knows (so the other supernode will respond to the requesting node directly).

#### Request for a file-transfer:

* Request:

  | 000e | File ID length (in bytes) |
  | ---- | ---- |
  | File ID ... | Offerer IPv4 |
  | Offerer IPv4 | Offerer Port |

  For UDP-holepunching, this message must be sent to the offering node **AND** to the supernode that maintains the file's Local-DHT entry (this information should have been recorded from a request response `100c`).

* Response: 

  If the receiving node is a:
  
  * supernode:
    
    * If `(Source IPv4, Source Port)` specifies the receiving supernode, ignore the message because it is a dummy message meant for UDP-holepunching.
    * Else if `(Offerer IPv4, Offerer Port)` specifies the receiving supernode and it does offer the requested file, "forward" the exact same request message (same `(Source IPv4, Source Port)`) to the node specified by `(Source IPv4, Source Port)` for UDP-holepunching.
    * Else, if `(Offerer IPv4, Offerer Port)` specifies a childnode paired with the receiving supernode and it does offer the requested file, the supernode should "forward" the exact same message (same `(Source IPv4, Source Port)`) to that childnode.
    
  * childnode:
    
    * If `(Source IPv4, Source Port)` specifies the receiving childnode, ignore the message because it is a dummy message meant for UDP-holepunching.
    * Else, childnode should "forward" the exact same request message (same `(Source IPv4, Source Port)`) to the node specified by `(Source IPv4, Source Port)` for UDP-holepunching.

---

### Posts:

* Notification for offering a new file - "0x000a"
* Notification for intention to disconnect - "0x000b"

#### Notification for offering a new file:

* Post:

  | 000a | File Size (in bytes) |
  | ---- | ---- |
  | File ID length (in bytes) | File ID ... |

  `File Size` is the size of the file in bytes (originally number of fragments).

  This message must be from a childnode to its bootstrapping node.
  
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

  | 000a | File ID length (in bytes) |
  | ---- | ---- |
  | File ID ... | File Data ... |

  The node that is to receive the file-transfer is responsible for keeping track of which file it is downloading and if it has fully received the file.
  
  Currently, the length of `File Data` in `000a` is capped at **1024** bytes.

  (No response is necessary.)
