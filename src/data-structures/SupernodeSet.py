# used by both supernodes and childnodes. For supernodes, this is used
# to keep track of all known supernodes; for childnodes, this is used 
# to cache known supernodes
#
# The underlying data structure is a Python Set of (IPv4, Port) tuples
# (such a tuple is expected as input to addSupernode() and removeSupernode())
#
# For ease of constructing and parsing P2P messages, ChildrenInfoTable has
# __len__(), __repr(), and importByString()
#
# (IPv4 addresses should be a 12-byte human-readable ASCII string;
#  Port number should be a 5-byte human-readable  ASCII string)

NUMBER_LENGTH = 4
IPv4_LENGTH = 12
PORT_LENGTH = 5

class SupernodeSet:
  def __init__(self):
    self.set = set()

  def addSupernode(self, supernode):
    self.set.add(supernode)

  # does nothing if the supernode to be removed is not found
  def removeSupernode(self, supernode):
    self.set.discard(supernode)

  # only for handling the content of "request response 100a"
  # and "request response 100b"
  def importByString(self, string):
    numSupernodes = int(string[0:NUMBER_LENGTH])

    IPv4Index = NUMBER_LENGTH
    for _i in range(numSupernodes):
      IPv4 = string[IPv4Index:IPv4Index+IPv4_LENGTH]
      PortIndex = IPv4Index + IPv4_LENGTH
      Port = string[PortIndex:PortIndex+PORT_LENGTH]
      IPv4Index = PortIndex + PORT_LENGTH
      self.set.add((IPv4, Port))

  def getSet(self):
    return self.set

  # return number of supernodes found in this SupernodeSet
  def __len__(self):
    return len(self.set)

  # essentially the message value for "request response 100a" and 
  # "request response 100b"
  # (which includes everything except the message type "100a"/"100b")
  def __repr__(self):
    numSupernodes = len(self.set)
    if numSupernodes == 0:
      return '0000'

    return_string = f'{numSupernodes:04d}'
    for (IPv4, Port) in self.set:
      return_string += IPv4 + Port

    return return_string

