# User Guide

## Description

The purpose of this document is to describe how a user of the P2P network should interact with the P2P client.

The user must have Python 3 installed and have a command-line interface, for now.

Commands are issued to the client CLI via stdin, and upon pressing enter, the command is sent.

Commands have the syntax:

\[command type\] \[options\]

Currently, two command types are supported:
- `req`
- `post`

`req` and `post` correspond directly to the `Request` and `Post` message types in [Protocol.md](./Protocol.md).

### Request

- `req files all`

This requests the entire DHT.

- `req files`

This requests only the local DHT.

- `req supernodes`

This requests a list of all supernodes in the P2P network.

- `req dl fileID fileHost`

This requests a download of a file named fileID from fileHost (IP:port)

### Post

- `post offer fileID`

This notifies the supernode that a file named fileID is ready for hosting.

- `post rm fileID`

This notifies the supernode that a file named fileID no longer available for hosting.

- `post disconnect`

This notifies the supernode that we wish to leave the network

### Notes

We may want to have a `req search fileID` which runs `req files` and/or `req files all`, and looks for peers who have the given fileID.
The list of peers could be returned to the user, so that the user can then initiate a download. Maybe make this a stretch-goal issue?.