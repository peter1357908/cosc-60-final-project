# used by supernodes to keep track of the childnodes it paired with
# and their respective info (currently the info is only about the files offered)
# 
# key: child IPv4 address (4 bytes in length and in network byte order)
#
# value: a Python Set of File IDs (strings of arbitrary length)
#
# (assumes sane input; does not check input sanity)

class ChildrenInfoTable:

  def __init__(self):
    self.tb = dict()

  # a Python Set will be initialized if the input fileSet is `None`.
  def addChild(self, IPv4, fileSet):
    if fileSet is None:
      fileSet = set()
    self.tb[IPv4] = fileSet

  # will add the IPv4 entry if it is not in the table yet
  def addFile(self, IPv4, file):
    fileSet = self.tb.get(IPv4)
    if fileSet is None:
      fileSet = set()
      self.tb[IPv4] = fileSet
    fileSet.add(file)

  def getFileSet(self, IPv4):
    return self.tb.get(IPv4)
  
  def hasChild(self, IPv4):
    return (IPv4 in self.tb)

  # will return false if the child is not present in the table
  def childHasFile(self, IPv4, file):
    return (file in self.tb.get(IPv4))

  # does nothing if either IPv4 is not in the table or if the file is not found
  def removeFile(self, IPv4, file):
    fileSet = self.tb.get(IPv4)
    if fileSet is not None:
      fileSet.discard(file)

  # returns None if IPv4 is not in the table, otherwise returns its fileSet
  def popChild(self, IPv4):
    self.tb.pop(IPv4, None)

