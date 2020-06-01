## Welcome to the README of our P2P Network!

We reccomend reading in this order:

Start with [Structure.md](./doc/Structure.md) to get a good idea of the structure of our
network and the responsibilities of supernodes and childnodes.

Afterwards, read [Protocol.md](./doc/Protocol.md) to understand what kind of messages our network uses to communicate.
[Protocol.md](./doc/Protocol.md) also contains specific information on how to implement a peer client for this P2P Network.

Finally, read [Extra.md](./doc/Extra.md) to see a list of extra features / write-up on scalability beyond the baseline functionalities as specified in the assignment instructions.

## To use our P2P Network:

General commandline information can be found in [Userguide.md](./doc/Userguide.md); more detailed instructions are as follows:

Please decide on one end system who wants to cold-start a new network, and change the definitions in [p2p.py](./src/p2p/p2p.py) to reflect that system's own address (`HARDCODED_BOOTSTRAP_*`). After that, simply run `python3 p2p.py -f` to start a network as its first supernode. The address of this supernode (as well as future supernodes) should be public information; as long as a user knows one supernode in a network, it can join the network by connecting only to that supernode.

For anyone who wants to join as a supernode, it should make sure that `HARDCODED_BOOTSTRAP_*` specify the address of the supernode it wants to connect to for bootstrapping (it can be any supernode in the network and not necessarily the first supernode) and `HARDCODED_SUPERNODE_*` should be changed to reflect its own address. Run `python3 p2p.py -s` to start the program.

For anyone who wants to join as a childnode, it should make sure that `HARDCODED_BOOTSTRAP_*` specify the address of the supernode it wants to connect to for bootstrapping (same as above) and start the program by running `python3 p2p.py`.
