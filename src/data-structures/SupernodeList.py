# used by both supernodes and childnodes. For supernodes, this is used
# to keep track of all known supernodes; for childnodes, this is used 
# to cache known supernodes
#
# not a specific class; just use a Python List of (IPv4, Port) tuples
# (IPv4 addresses should be a 12-byte human-readable ASCII string;
#  Port number should be a 5-byte human-readable  ASCII string)
