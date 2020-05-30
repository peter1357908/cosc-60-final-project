import sys, os
sys.path.append(os.path.abspath('../'))
from SupernodeSet import SupernodeSet

supernodeSet1 = SupernodeSet()
supernodeSet2 = SupernodeSet()

supernode1 = ('IPv411111111', 'Port1')
supernode2 = ('IPv422222222', 'Port2')
supernode3 = ('IPv433333333', 'Port3')

supernodeSet1.addSupernode(supernode1)
supernodeSet1.addSupernode(supernode2)
supernodeSet1.addSupernode(supernode3)

supernodeSet2.importByString(str(supernodeSet1))
print(supernodeSet1)
print(supernodeSet2)
print(
    f'str(supernodeSet1)==str(supernodeSet2): {str(supernodeSet1)==str(supernodeSet2)}')
