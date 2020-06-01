# User Guide

## Description

The purpose of this document is to describe how a user of the P2P network should interact with the P2P client.

The user must have Python 3 installed and have a command-line interface.

Both the supernode and the child nodes may issue these commands. Note that the supernodes will continue to function in the absence of user input.

Commands are issued to the client CLI via stdin, and upon pressing enter, the command is sent.

Commands have the syntax:

\[command type\] \[options\]

Currently, two command types are supported:
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

This requests the local DHT, that is the supernode's DHT.


- `req supernodes`

This requests a list of all supernodes in the P2P network.

- `req dl fileID (IP:port)`

This requests a download of a file named fileID.

A big caveat is that before downloading, the user must `req files local` or `req files all`
since we assume that the user must search for available files and hosts before choosing to download.

### Post

- `post offer fileID`

This notifies the supernode that a file named fileID is ready for hosting.

- `post rm fileID`

This notifies the supernode that a file named fileID no longer available for hosting.

- `post disconnect`

This notifies the supernode that we wish to leave the network

