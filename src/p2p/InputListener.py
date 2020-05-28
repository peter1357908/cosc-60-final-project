# This is the code for the InputListener Thread:

import threading
# import File
# import FileInfoTable
# import SNode_helpers

import CNode_helper

class InputListener(threading.Thread):

    # Initialize InputListener Thread
    # TODO: Add paramaters as arguments are determined
    def __init__(self,supernodeIP, table):
        threading.Thread.__init__(self)
        self.supernodeIP = supernodeIP  # IP of supernode, 127.0.0.1 if is a supernode
        self.table = table # File Info Table
        if supernodeIP == "127.0.0.1":
            self.childTable = ChildInfoTable()
            self.superList = SupernodeList()
        get_source_addr() # set your own ip and port values from STUN server
        connect_p2p(ip = self.supernodeIP, port = 5000) #connect to the p2p via port 5000 (handshake)
        join_p2p() #join the network 

    # Methods for handling each parsed case:
    # A note on the following methods: "file" is always a File Object.

    # Construct Request DHT packet and send to supernodeIP:
    def requestDHT(self, all_dht):
        # CNode_helper.requestDHT(all_dht)
        if all_dht:
            print("requesting entire DHT")
        print("Requested DHT from ", self.supernodeIP)
        request_dht(all_dht)

    # Request list of supernodes
    def request_supernodes(self):
        # TODO
        # CNode_helper.request_super_list()
        print("requesting all the supernodes")
        request_super_list()

    # Begin a download:
    def beginDownload(self, downloadIP, file):
        # downloader = Downloader(self.supernodeIP, downloadIP, file)
        # downloader.start()
        print("Attempting to download from ", downloadIP)
        request_file(file,supernodeIP,5001)

        #TODO FIGURE OUT HOLE PUNCHING HERE
    
    # Offer a New File
    def offerNewFile(self, file):
        # TODO:
            # STILL NEED TO FIGURE OUT FILE SIZE ETC AS PARAMETERS
        # CNode_helper.post_file(file_size, id_size, filename)
        print("Announcing a new file is being offered: ", file)
    
    # Announce a file is no longer being offered:
    def removeOfferedFile(self, file):
        # TODO:
        # need corresponding protocol message?
        print(f"{file} is no longer being offered")
    
    # Disconnect from the network:
    def disconnect(self):
        # CNode_helper.send_disconnect()
        print("Disconnected from the network. Goodbye!")
        send_disconnect()

    # Return a stirng informing user about the usage
    def usage_statement(self):
        print("usage statement stub")
        pass


    # TODO: run() method of the listener: constantly listen for input and parse it out:
    # I Think SNode_helpers can 'help' with parsing and calling these methods
    def run(self):
        while True:
            # # If the command requires a file as an arg: 
            #     fileID = 'parsed'
            #     offerer = 'parsed'
            #     fileInfo = 'parsed'
            #     name = 'parsed'
            #     file = File(fileID, offerer, fileInfo, name)
            #     downloadIP = file.getOfferer()

            # Parse out user input
            user_input = input("> ")

            if not user_input:
                continue
            if user_input.isspace():
                continue

            # user input tokens are space delimited
            input_tks = user_input.split(" ")
            assert len(input_tks) > 0
            print(f"input tks are {input_tks}")
            if input_tks[0] == "req":
                assert len(input_tks) >= 2
                if input_tks[1] == "files":
                    # If input is request for information:
                    all_dht = False
                    if len(input_tks) >= 3 and input_tks[2] == "all":
                        all_dht = True
                    self.requestDHT(all_dht)
                elif input_tks[1] == "supernodes":
                    self.request_supernodes()
                elif input_tks[1] == "dl":
                    assert len(input_tks) >= 4
                    # Else if input is to begin a download:
                    file_id = input_tks[2]
                    # TODO: need to add validation for IP:port
                    file_host = input_tks[3].split(":")
                    file = None
                    downloadIP = None
                    self.beginDownload(downloadIP, file)
            elif input_tks[0] == "post":
                assert len(input_tks) >= 2

                if input_tks[1] == "offer":
                    assert len(input_tks) >= 3
                    # Else if input is to offer a new file:
                    file_id = input_tks[2]
                    self.offerNewFile(file=None)
                elif input_tks[1] == "rm":
                    assert len(input_tks) >= 3
                    file_id = input_tks[2]
                    self.removeOfferedFile(file=None)
                elif input_tks[1] == "disconnect":
                    # Else if input is to disconnect from the network
                    self.disconnect()

            else:
                print(f"command not recognized {input_tks[0]}")
                # Then, print out list of possible commmands:
                print(self.usage_statement())
