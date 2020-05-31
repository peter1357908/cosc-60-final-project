# Protocol Write-up

**Foye, Gao, Ma, Parker, and Vojdanovski**

## Protocol Overview

The [requirements](https://canvas.dartmouth.edu/courses/39576/assignments/234934) for the lab stipulate that the protocol is built on a reliable form of UDP, which Matt has offered us to use.

Before reading this, familiarize yourself with the jobs of supernodes and child
nodes [here](https://gitlab.cs.dartmouth.edu/hyperistic/cosc-60-final-project/blob/master/Structure.md).

Note: this document uses GitHub Markdown tables to represent the structure of a transmission. Each cell of a table should correspond to a 4 byte field. Fields that end with an ellipsis have arbitrary length.

All IPv4 addresses are represented by a 12-byte ASCII string, and all port numbers are represented by a 5-byte ASCII string. All other numbers (e.g. `Message Length`, `File ID Length`) are 4-byte ASCII strings. The unit for all `size` and `length` fields is **byte**.

The general structure of a packet on our network will be:

| UDP  |
| ---- |
| Matt's MRT Protocol |
| This module's P2P Protocol |

Our protocol has following types of transimissions:

*  Posts
*  Requests
*  File-transfer

Where `Posts` are notifications of new information, `Requests` are requests for some unknown information, and `File-transfers` are the special case where a file is being transferred between a requesting node and an offering node.

Our P2P Protocol will be partitioned as follows, with each partition 
being 4 bytes in length:

| Type | Message Length |
| ---- | ---- |
| Source IPv4 ... | Source Port ... |
| Message ... |

* `Type` specifies if the message is a(n):

  *  Post - "0001"
  *  Request - "0101"
  *  File-transfer - "1111"
  *  Indication of error - "0000"

* `Message Length` is the length of the `Message` part of the transmission.

* `Source IPv4` is the IPv4 address of the initial creator of the message, in case the message needs to be forwarded.

* `Source Port` is the port number the source is listening on

* `Message` is the payload of the transmission (whose composition is specified below).

## Types of Messages

### Requests:

* Request to join the network - "000a"
* Request for a supernode's supernode set - "000b"
* Request for a supernode's Local-DHT (on all files/one file) - "000c"
* Request for all DHT entries (on all files / one file): - "000d"
* Request for a file-transfer - "000e"

#### Request to join the network:

* Request:

  | 000a | request type |
  | ---- | ---- |

  `request type` will be `0000` for a regular node join request, and `0001` for a supernode join request, and `0002` for a relayed supernode join request (see below)

* Response:

  * If `request type` is `0000` or `0001`, the receiver sends the following response to the requester (the `Supernode entries` should not contain the requesting node).

    | 100a | Number of supernode entries | Supernode entries ... |
    | ---- | ---- | ---- |
    
    Each `supernode entry` has the following format:

    | IPv4 ... | Port ... |
    | ---- | ---- |
    
  * If `request type` is `0000`, the receiver recognizes `(Source IPv4, Source Port)` as a paired childnode (and keep track of it).

  * If `request type` is `0001` or `0002`, the receiver recognizes `(Source IPv4, Source Port)` as a known supernode (and keep track of it).
  
  * If `request type` is `0001`, the receiver also needs to send the following request to all supernodes it knows with the same `(Source IPv4, Source Port)` as the request message:

    | 000a | 0002 |
    | ---- | ---- |
  
#### Request for a supernode's supernode set:

* Request:

  | 000b |
  | ---- |
  
  (Only the type field is necessary)

* Response:

  | 100a | Number of supernode entries | Supernode entries ... |
  | ---- | ---- | ---- |
  
  Each `supernode entry` has the following format:

  | IPv4 ... | Port ... |
  | ---- | ---- |
  
  (which is the same as the response for Request `000a`)
  
#### Request for a supernode's Local-DHT entries (on all files / one file):

* Request:

  | 000c | File ID length | File ID ... |
  | ---- | ---- | ---- |
  
  (currently, the supernode can send this request to all known supernodes, but a childnode can only send this request to its bootstrapping supernode)
  
  If the requester wants all entries, `File ID length` should be `0000` (and consequently have nothing for `File ID`).
  
  Else, the requester specifies the file whose entries it wants with `File ID length` and `File ID`.


* Response:

  | 100c | Number of Local-DHT entries | Local-DHT entries ... |
  | ---- | ---- | ---- |
  
  * Each `Local-DHT entry`  has the following format:
  
    | File ID length | File ID ... | Number of file entries | File entries ... |
    | ---- | ---- | ---- | ---- |

    * Each `File entry` has the following format:

      | Offerer IPv4 ... | Offerer Port ... | File Size |
      | ---- | ---- | ---- |

      NOTE: the requesting node should distinguish between different supernodes' response by `(Source IPv4, Source Port)`. Knowing which supernode maintains a Local-DHT entry is necessary for crafting the request `000e` below.
  
  For robust-ness, the supernode should always respond to request `000c` (if no entries are found, respond with `number` being `0000` and no `Local-DHT entry`).
  
#### Request for all DHT entries (on all files / one file):

* Request:

  | 000d | Requester IPv4 | Requester Port | File ID length | File ID ... |
  | ---- | ---- | ---- | ---- | ---- |
  
  This request should be sent from a childnode (a supernode should directly use request type `000c`) to a supernode (which does not have to be its bootstrapping supernode); in this case, `(Requester IPv4, Requester Port)` is the same as `(Source IPv4, Source Port)` because they both specify the requesting childnode.

* Response:

  If `(Requester IPv4, Requester Port)` specifies a child of the receiving supernode:
  
    1. Respond to `(Source IPv4, Source Port)` as if the request is of type `000c` (craft a `100c` response)

    1. Craft the same message with its own `(IPv4, Port)` as the `(Source IPv4, Source Port)` (keep all other fields the same) and send it to all known supernodes
  
  Else (it has received a relayed request as crafted above):
  
    Respond to `(Source IPv4, Source Port)` with the following format:

    | 100d | Requester IPv4 | Requester Port | Number of Local-DHT entries | Local-DHT entries ... |
    | ---- | ---- | ---- | ---- | ---- |

    * Each `Local-DHT entry`  has the following format:

        | File ID length | File ID ... | Number of file entries | File entries ... |
        | ---- | ---- | ---- | ---- |

        * Each `File entry` has the following format:

          | Offerer IPv4 ... | Offerer Port ... | File Size |
          | ---- | ---- | ---- |
    
    **Upon receiving request `100d`**, craft a `100c` response with the received information to `(Requester IPv4, Requester Port)` with `(Source IPv4, Source Port)` being the same as that from the `100d` (see "NOTE" for `100c` for why this is important).
  

#### Request for a file-transfer:

* Request:

  | 000e | File ID length |
  | ---- | ---- |
  | File ID ... | Offerer IPv4 ... |
  | Offerer Port ... | |
  
  If the offerer is not a supernode, send a dummy UDP-holepunching message to the offerer.
  
  This message needs to be sent to the supernode that maintains the file's Local-DHT entry (the maintainer information should have been recorded from a request response `100c`. This message would be forwarded to the offering childnode if the file is not offered by the supernode itself)

* Response: 
  
  Since the current protocol **does not require back-and-forth on the P2P layer**:
  
  * If `(Offerer IPv4, Offerer Port)` specifies the receiving node, connect to `(Source IPv4, Source Port)` and start sending File-Transfer messages accordingly (hole-punching is already)
  
  * Else if the receiving node is a supernode **AND** if `(Offerer IPv4, Offerer Port)` specifies a childnode paired with the receiving supernode and it does offer the requested file, the supernode should "forward" the exact same message (same `(Source IPv4, Source Port)`) to that childnode.

---

### Posts:

* Notification for offering a new file - "000a"
* Notification for intention to disconnect - "000b"

#### Notification for offering a new file:

* Post:

  | 000a | File Size |
  | ---- | ---- |
  | File ID length | File ID ... |

  `File Size` is the size of the file (originally number of fragments).

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

  | 000a | File ID length |
  | ---- | ---- |
  | File ID ... | File Data ... |

  The node that is to receive the file-transfer is responsible for keeping track of which file it is downloading and if it has fully received the file.
  
  Currently, the length of `File Data` in `000a` is capped at **1024** bytes.

  (No response is necessary.)
