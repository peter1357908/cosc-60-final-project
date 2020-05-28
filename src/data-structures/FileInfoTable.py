# used by both supernodes and childnodes. For supernodes, one instance
# should be used as its Local-DHT, and another can be used for
# caching DHT entries from other supernodes; for childnodes, this is only 
# used for caching known DHT entries.
#
# key: File ID (a string of arbitrary length)
#
# value: a non-empty Python Dictionary:
#
#        key: (IPv4, Port) tuple of the node that offers the file
#
#        value: a FileInfo object with misc info on the file
#
# each FileInfo object has the following instance variables:
#   size: the file size in bytes
#   maintainer: (IPv4, Port) tuple of the supernode that maintains
#               this offer's DHT entry. (The supernode should also
#               be the offerer's bootstrapping node)
#
# (IPv4 addresses should be a 12-byte human-readable ASCII string;
#  Port number should be a 5-byte human-readable  ASCII string)
# (assumes sane input; does not check input sanity)

# A dictionary of sets that contains all files by a certain offerer
filesByOfferer = {}

class FileInfo:

    def __init__(self, size, maintainer):
      self.size = size
      self.maintainer = maintainer

class FileInfoTable:

  def __init__(self):
    self.tb = dict()

  # will replace the old fileInfo from the same offerer if it already exists
  def addFileInfo(self, fileID, offerer, fileInfo):
    fileInfoDict = self.tb.get(fileID)
    
    # Create a set of files per offerer
    if filesByOfferer[offerer] is None:
        filesByOfferer[offerer] = {}
    filesByOfferer[offerer].add(fileID)
    
    
    if fileInfoDict is None:
      fileInfoDict = dict()
      self.tb[fileID] = fileInfoDict
    fileInfoDict[offerer] = fileInfo

  def getFileInfoDictByID(self, fileID):
    return self.tb.get(fileID)
  
  def hasFile(self, fileID):
    return (fileID in self.tb)
  
  def hasFileByOfferer(self, fileID, offerer):
    fileInfoDict = self.tb.get(fileID)
    if fileInfoDict is None:
      return False
    return (offerer in fileInfoDict)

  # will remove the fileID entry if the fileInfoDict would be empty after removal
  # does nothing if the corresponding FileInfo is not found
  def removeFileInfoByOfferer(self, fileID, offerer):
    fileInfoDict = self.tb.get(fileID)
    if fileInfoDict is not None:
      fileInfoDict.pop(offerer, None)
      if not fileInfoDict:
        self.tb.pop(fileID)
  
  # executes removeFileInfoByOfferer() on each fileID in fileIDSet
  def removeAllFileInfoByOfferer(self, fileIDSet, offerer):
   # for fileID in fileIDSet:
    for fileID in filesByOfferer[offerer]:
      # the following should be the same as removeFileInfoByOfferer()
      fileInfoDict = self.tb.get(fileID)
      if fileInfoDict is not None:
        fileInfoDict.pop(offerer, None)
        if not fileInfoDict:
          self.tb.pop(fileID)
  
