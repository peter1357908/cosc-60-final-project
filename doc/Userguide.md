# User Guide

## Description

The purpose of this document is to describe how a user of the P2P network should interact with the P2P client.

The user must have Python 3 installed and have a command-line interface, for now.

Commands are issued to the client CLI via stdin, and upon pressing enter, the command is sent.

## P2P Start Syntax:

`python3 p2p.py [join-type]`

Where as `join-type` should be one of the following two:

* `-f`: join as the first supernode (start a new network). `p2p.py` should be modified to contain hard-coded address information of the first supernode.
* `-s`: join as a supernode. `p2p.py` should be modified to contain hard-coded address information of the bootstrapping supernode it wants to connect to as well as the joining supernode's own address information.

If `join-type` is not specified, the node joins as a childnode. `p2p.py` should be modified to contain hard-coded address information of the bootstrapping supernode it wants to connect to.

## User Interface Command Syntax:

`[command type] [options]`

Two command types are supported:
- `req`
- `post`

`req` and `post` correspond directly to the `Request` and `Post` message types in [Protocol.md](./Protocol.md).

### Request


1. Request from the local DHT 
2. Request from the entire DHT

For each mode, you can request either:

1. Just one file 
2. All the files available for the local/entire DHT


- `req files all <specific-file-name>`

This requests just one specific file from the entire DHT

- `req files all`

This requests the entire DHT

- `req files local <specific-file-name>`

This requests just one specific file from the local DHT

- `req files local`

This requests the local DHT

- `req files all`

This requests the entire DHT.

- `req files`

This requests only the local DHT.

- `req supernodes`

This requests a list of all supernodes in the P2P network.

- `req dl fileID fileHostAddr`

This requests a download of a file named `fileID` from `fileHostAddr` in the form `(IPv4:port)` (this information is available for copy-pasting upon a successful DHT request, e.g. `req files local` - in fact, our implementation forbids a user from downloading a file whose information is not made available to the user with a DHT request)

### Post

- `post offer fileID`

This notifies the supernode that a file named fileID is ready for hosting.

- `post rm fileID`

This notifies the supernode that a file named fileID no longer available for hosting.

- `post disconnect`

This notifies the supernode that we wish to leave the network
