# used by both supernodes and childnodes. For supernodes, this is used
# to keep track of all known supernodes; for childnodes, this is used 
# to cache known supernodes
#
# essentially a Python Set of (IPv4, Port) tuples, but with convenient
# methods like __len__() and __repr__
#
# expect 
#
# (IPv4 addresses should be a 12-byte human-readable ASCII string;
#  Port number should be a 5-byte human-readable  ASCII string)

class SupernodeSet:
  def __init__(self):
    self.set = set()

  def addSupernode(self, IPv4, Port):
    self.set.add(IPv4, Port)

  # does nothing if the supernode to be removed is not found
  def removeSupernode(self, IPv4, Port):
    self.set.discard((IPv4, Port))

  def importByString():

    
  def removeFile(self, child, file):
    fileSet = self.tb.get(child)
    if fileSet is not None:
      fileSet.discard(file)

  def importByString(self, inputString):


  def getSet(self):
    return self.set

  # corresponds to `Number of supernode entries` for "request response 100b"
  def __len__(self):

    # corresponds to `Supernode entries` for "request response 100b"
  def __repr__(self):
    return "".join(ip + port for (ip, port) in self.set)


