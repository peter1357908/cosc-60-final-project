# used by both supernodes and childnodes to keep track of the MRT IDs
# by the connection address
#
# The data structure should be a Python Dictionary specified as follows:
#
# key: connection address (IPv4, Port) tuple
#
# value: MRT sendID (no need to keep track of recvID because only MessageListener needs it)
#
# (IPv4 addresses should be a 12-byte human-readable ASCII string;
#  Port number should be a 5-byte human-readable  ASCII string)
