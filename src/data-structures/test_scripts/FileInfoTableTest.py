import sys, os
sys.path.append(os.path.abspath('../'))
from FileInfoTable import FileInfoTable, FileInfo

table1 = FileInfoTable()
table2 = FileInfoTable()

info1 = FileInfo(1, ('123456789abc', '12345'))
info2 = FileInfo(2, ('123456789abc', '12345'))
info3 = FileInfo(3, ('123456789abc', '12345'))

table1.addFileInfo('o1', ('cba987654321', '54321'), info1)
table1.addFileInfo('o2', ('cba987654321', '54321'), info2)
table1.addFileInfo('o3', ('cba987654321', '54321'), info3)

table2.importByString(str(table1), '12345')
print(table1)
print(table2)
print(f'str(table1)==str(table2): {str(table1)==str(table2)}')
