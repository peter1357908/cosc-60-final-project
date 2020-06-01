# Extra Features

1. The network tries to form connections between nodes (automatically) to increase the resilience of the network:

    * In our network, any node who joins the network will get a list of all supernodes that are known by its bootstrapping supernode as the very first response indicting a successful join.
    * If the node that just joined is a supernode, it will attempt to connect to all those supernodes to increase the resilience of the network (to add to scalability, this behavior can be changed easily so that each supernode only keeps track of, and connects to, a limited number of other supernodes).
    * If the node that joined is a childnode, it will not connect to any more supernodes to eliminate unnecessary connections, but since it has this list of all supernodes in its memory and that it can always re-request the list to get updates, it always knows what other supernodes there are, to connect to in case its own bootstrapping supernode goes down.
  
1. Clients know (remember or re-learn) which files are downloadable on their new network:
    * this is achieved by the `request DHT entries` commands, the details of which can be found in [Userguide.md](./Userguide.md). After running those commands, the user will get a list of files that are currently offered on the network (which files are shown depends on what type of `request` is run)
    * the list will be printed in human-readable format to allow users to distinguish between different files (currently the file's name, the file's size, and the user who offers it are all available so that the user can distinguish between, say, the files with the same filenames being offered on the network).
    * to ensure input sanity, the users are forbidden to download a file if the user's program has not gotten the relevant information from a request on DHT entries (to reduce unnecessary/malicious download requests being sent over the network).

1. Routes for exchanging files are efficient (this might be hard to test if you've already implemented option 1, so perhaps turn that into a switch)
    
    * currently, since all supernodes would be connected to each other but each childnode must be connected only to its bootstrapping supernode, the flow of file exchanges goes like this for a childnode-to-childnode exchange (other more straight-forward exchanges can be found in [Protocol.md](./Protocol.md):
        1. childnode C1 sends a request to its bootstrapping supernode S1 specifying that it wants to download a file offered by C2, whose bootstrapping supernode is S2. C1 also performs UDP-holepunching to allow receiving messages from C2.
        2. Since S1 knows S2 but not C2, S1 forwards the request to S2.
        3. S2 sees that the request is intended for one of its children, C2, S2 forwards the request to C2
        4. C2 sees that the request is intended for it and try starting a file-transfer stream by connecting to C1.
    
    * (in other words, the routes are very efficient because we assume that the supernodes are inter-connected)

1. Think about scalability of your project and argue why for your implementation the network can have >2^16  nodes (in an unscalable implementation, when 2^16 people broadcast 1 file, 2^16*2^16 = 4 billion messages might need to be exchanged by a single node)

    * Our protocol ensures that a file offer is only maintained by one supernode (so in order to offer a file, at most one message would be send - from a childnode, 1 message to its bootstrapper; from a supernode, no message as it directly updates its Local-DHT).
    * Our protocol also ensures that a file's offer information is only transmitted as needed; it would not be automatically broadcast to every other node (however, this does mean that the user's knowledge on what files are offered are only as new as the user's last request for DHT entries.
    * Admittedly, our protocol's scalability varies and depends on the supernode-to-childnode ratio - the more supernodes there are, the more children can be attached to the network (more scalable), but also the more inter-connected the supernodes are (less scalable). The maximum capacity of our P2P network should occur at a "sweet spot" along the ratio axis - a certain supernode-to-childnode ratio would ensure the maximum number of total nodes on one network.

1. Our own extra features:

    * we ensure that multiple users can share files with the same filename, in which case the files are distinguished by who offers each of them.


