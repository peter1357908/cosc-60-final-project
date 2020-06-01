#! /usr/bin/python3
#import FileInfo
import FileInfoTable

# A File Class
# Has the same attributes as the Files Peter used for his table

class File():
    # Initialize Instance Variables:
    def __init__(self, fileID, offerer, fileInfo, name):
        self.fileID = fileID
        self.offerer = offerer
        self.fileInfo = fileInfo
        self.name = name
    
    # Getters and Setters for each instance variable:

    # Get File ID
    def getFileID(self):
        return self.fileID
    # Set File ID
    def setFileID(self, newFileID):
        self.fileID = newFileID
    
    # Get Offerer
    def getOfferer(self):
        return self.offerer
    # Set offerer
    def setOfferer(self, newOfferer):
        self.offerer = newOfferer
    
    # Get FileInfo object:
    def getFileInfo(self):
        return self.fileInfo
    # Set FileInfo:
    def setFileInfo(self, newFileInfo):
        self.fileInfo = newFileInfo
    
    # Get file name:
    def getName(self):
        return self.name
    # Set file name:
    def setName(self, newName):
        self.name = newName

