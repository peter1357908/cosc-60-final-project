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
# For ease of constructing and parsing P2P messages, FileInfoTable has
# __len__(), __repr(), importByString(), and getFileInfoTableByID()
#
# (IPv4 addresses should be a 12-byte human-readable ASCII string;
#  Port number should be a 5-byte human-readable  ASCII string)
# (assumes sane input; does not check input sanity)

NUMBER_LENGTH = 4
IPv4_LENGTH = 12
PORT_LENGTH = 5

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
    
    if fileInfoDict is None:
      fileInfoDict = dict()
      self.tb[fileID] = fileInfoDict
    fileInfoDict[offerer] = fileInfo

  # returns the underlying dictionary object corresponding
  # to the specified fileID
  def getFileInfoDictByID(self, fileID):
    return self.tb.get(fileID)

  # note that the data strcuture for the "table" is a Python Dictionary
  def getTable(self):
    return self.tb

  # returns a newly instantiated FileInfoTable object with only one entry:
  # the fileID to its fileInfoDict (to enable usage of __repr__(self))
  def getFileInfoTableByID(self, fileID):
    fileInfoDict = self.tb.get(fileID)
    if fileInfoDict is None:
      return None
    # DANGEROUS: nested class usage... might be a better way to this
    newFileInfoTable = FileInfoTable()
    newFileInfoTable.tb[fileID] = fileInfoDict
    return newFileInfoTable
  
  # only for handling the content of "request response 100c"
  # maintainer should be the (Source IPv4, Source port) string tuple
  # from the "request response 100c" message in question
  def importByString(self, string, maintainer):
    numLDHTEntries = int(string[0:NUMBER_LENGTH])
    fileEntryIndex = NUMBER_LENGTH
    for _i in range(numLDHTEntries):
      fileIDLength = int(string[fileEntryIndex:fileEntryIndex+NUMBER_LENGTH])
      fileIDIndex = fileEntryIndex + NUMBER_LENGTH
      fileID = string[fileIDIndex:fileIDIndex+fileIDLength]

      fileInfoDict = self.tb.get(fileID)
      if fileInfoDict is None:
          fileInfoDict = dict()
          self.tb[fileID] = fileInfoDict

      numFileEntriesIndex = fileIDIndex + fileIDLength
      numFileEntries = int(string[numFileEntriesIndex:numFileEntriesIndex+4])
      IPv4Index = numFileEntriesIndex + NUMBER_LENGTH
      for _j in range(numFileEntries):
        offererIPv4 = string[IPv4Index:IPv4Index+IPv4_LENGTH]
        PortIndex = IPv4Index + IPv4_LENGTH
        offererPort = string[PortIndex:PortIndex+PORT_LENGTH]
        fileSizeIndex = PortIndex + PORT_LENGTH
        fileSize = int(string[fileSizeIndex:fileSizeIndex+NUMBER_LENGTH])
        IPv4Index = fileSizeIndex + NUMBER_LENGTH

        fileInfo = FileInfo(fileSize, maintainer)
        fileInfoDict[(offererIPv4, offererPort)] = fileInfo
      
      # by this point IPv4Index from inside the file entry loop actually points to the next file entry
      fileEntryIndex = IPv4Index

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
    for fileID in fileIDSet:
      # the following should be the same as removeFileInfoByOfferer()
      fileInfoDict = self.tb.get(fileID)
      if fileInfoDict is not None:
        fileInfoDict.pop(offerer, None)
        if not fileInfoDict:
          self.tb.pop(fileID)
  
  # return the number of (distinct) FileIDs
  def __len__(self):
    return len(self.tb)

  # essentially the message value for "request response 100c"
  # (which includes everything except the message type "100c")
  def __repr__(self):
    fileIDs = self.tb.keys()
    numLDHTEntries = len(fileIDs)
    if numLDHTEntries == 0:
      return '0000'
    
    return_string = f'{numLDHTEntries:04d}'
    for fileID in fileIDs:
      fileInfoDict = self.tb.get(fileID)
      return_string += f'{len(fileID):04d}{fileID}{len(fileInfoDict):04d}'
      for offerer in fileInfoDict:
        fileInfo = fileInfoDict.get(offerer)
        return_string += f'{offerer[0]}{offerer[1]}{fileInfo.size:04d}'
    
    return return_string