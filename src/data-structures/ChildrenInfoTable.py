# used by supernodes to keep track of the childnodes it paired with
# and their respective info (currently the info is only about the files offered)
# 
# key: child (IPv4, Port) tuple
#
# value: a Python Set of File IDs (strings of arbitrary length)
#
# (IPv4 addresses should be a 12-byte human-readable ASCII string;
#  Port number should be a 5-byte human-readable  ASCII string)
# (assumes sane input; does not check input sanity)

class ChildrenInfoTable:

  def __init__(self):
    self.tb = dict()

  # will do nothing if child already exists in the table
  def addChild(self, child):
    if (child not in self.tb):
      self.tb[child] = set()

  # will add the child entry if child is not in the table yet
  # (but there shouldn't be such an occassion)
  def addFile(self, child, file):
    fileSet = self.tb.get(child)
    if fileSet is None:
      fileSet = set()
      self.tb[child] = fileSet
    fileSet.add(file)

  def getFileSetByChild(self, child):
    return self.tb.get(child)
  
  def hasChild(self, child):
    return (child in self.tb)

  # will return False if the child is not present in the table
  def childHasFile(self, child, file):
    fileSet = self.tb.get(child)
    if fileSet is None:
      return False
    return (file in fileSet)

  # does nothing if either child is not in the table or if the file is not found
  def removeFile(self, child, file):
    fileSet = self.tb.get(child)
    if fileSet is not None:
      fileSet.discard(file)

  # returns None if child is not in the table, otherwise returns its fileSet
  def popChild(self, child):
    return self.tb.pop(child, None)
