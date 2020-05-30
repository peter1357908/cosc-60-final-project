"""
Child Node Helper files for COSC 60 FInal Project


May 2020
"""
import sys
sys.path.append('../mrt/')
import socket
import binascii
from mrt import * 
from stun import *

""" DEFINITIONS """
POST = '0001'
REQUEST = '0101'
FILE_TRANSFER = '1111'
ERROR = '0000'

""" SUB DEFINITIONS """

""" REQUESTS """
R_JOIN = '000a'
R_LIST = '000b'
R_LOCAL_DHT = '000c'
R_GLOBAL_DHT = '000d'
R_FILE_TRANS = '000e'


""" POSTS """
P_NEW_FILE = '000a'
P_DISCONNECT = '000b'

SUPERNODE_IP = '192.168.0.249'
SUPERNODE_PORT = 11235
SUPERNODE_ID = 0


#TODO: GET SOURCE IP USING STUN STUFF
SOURCE_IP = '1921689249'
SOURCE_PORT = 12345
SOCK = 0

"""
GENERAL NOTE: I JUST REALIZED THAT I DIDNT ADD LENGTH,
SOURCE IPV4 ETC
ALSO I THINK THAT WE NEED TO HAVE SOURCE PORT IN THERE 
AS WELL 
"""

"""
Connects to supernode using mrt_connect
Returns an ID connection object
"""
def connect_p2p(ip = SUPERNODE_IP,port = SUPERNODE_PORT):
	global SUPERNODE_ID
	SUPERNODE_ID = mrt_connect(ip,port)
	print(SUPERNODE_ID)

"""
Function to get the source ip and port (public) for the client
TODO: NEED TO INITIALIZE SOCK 
"""
def set_source_addr(sock):
	global SOURCE_IP,SOURCE_PORT,SOCK
	SOCK = sock
	ip, SOURCE_PORT = get_address(sock)
	SOURCE_PORT = str(SOURCE_PORT).zfill(5)
	ip = str(ip).split('.')
	ip = [x.zfill(3) for x in ip]
	SOURCE_IP = ''.join(ip)
	print(f'source_ip: {SOURCE_IP}, source_port: {SOURCE_PORT}')

def get_source_addr(sock):
	ip, port = get_address(sock)
	port = str(port).zfill(5)
	ip = str(ip).split('.')
	ip = [x.zfill(3) for x in ip]
	ip = ''.join(ip)
	return (ip,port)
	print(f'source_ip: {SOURCE_IP}, source_port: {SOURCE_PORT}')

"""
Function to join the network, takes one parameter
join_type:
	0: join as chlid node
	1: join as supernode
	2: join as relayed supernode
"""
def join_p2p(join_type = 0):
	values = ''.join([R_JOIN,f'{join_type:04d}'])
	msg_len = len(values)
	msg = ''.join([REQUEST,f'{msg_len:04d}',SOURCE_IP,SOURCE_PORT,values])
	send_p2p_msg(msg)


"""
Function to create the request for DHT
Takes one arg: all (bool)
	all = True: send '000d'
	all = False: send '000c'
	default is True
"""
def request_local_dht(filename = ''):
	if len(filename) > 0:
		values = ''.join([R_LOCAL_DHT,f'{len(filename):04d}',filename])
	else:
		values = ''.join([R_LOCAL_DHT,'0000'])
	msg_len = len(values)
	msg = ''.join([REQUEST,f'{msg_len:04d}',SOURCE_IP,SOURCE_PORT,values])
	send_p2p_msg(msg)


def request_global_dht(filename = ''):
	if len(filename) > 0:
		values = ''.join([R_GLOBAL_DHT,f'{len(filename):04d}',filename])
	else:
		values = ''.join([R_GLOBAL_DHT,'0000'])
	msg_len = len(values)
	msg = ''.join([REQUEST,f'{msg_len:04d}',SOURCE_IP,SOURCE_PORT,values])
	send_p2p_msg(msg)

"""
Function to request supernode list
Takes no parameters
"""
def request_super_list():
	values = ''.join([R_LIST])
	msg_len = len(values)
	msg = ''.join([REQUEST,f'{msg_len:04d}',SOURCE_IP,SOURCE_PORT,values])
	send_p2p_msg(msg)


"""
Function to send new file post
PARAMETERS: 
	File Size: int of byte size
	File ID length: int of byte size
	File ID: string
"""
def post_file(file_size,id_size,filename):
	values = ''.join([P_NEW_FILE,f'{file_size:04d}',f'{id_size:04d}',filename])
	msg_len = len(values)
	msg = ''.join([POST,f'{msg_len:04d}',SOURCE_IP,SOURCE_PORT,values])
	send_p2p_msg(msg)


"""
Function to request a file
PARAMETERS:
	file_id: str
	ip: ip string in standard format ie 'xxx.xxx.xxx.xxx'
	port: integer
"""
def request_file(file_id,ip,port):
	id_len = len(file_id)
	ip = str(ip).split('.')
	ip = [x.zfill(3) for x in ip]
	ip = ''.join(ip)
	port = port.zfill(5)
	values = ''.join([R_FILE_TRANS,f'{id_len:04d}',file_id,ip,port])
	msg_len = len(values)
	msg = ''.join([REQUEST,f'{msg_len:04d}',SOURCE_IP,SOURCE_PORT,values])


"""
Function to send request to disconnect
"""
def send_disconnect():
	values = ''.join([P_DISCONNECT])
	msg_len = len(values)
	msg = ''.join([POST,f'{msg_len:04d}',SOURCE_IP,SOURCE_PORT,values])
	send_p2p_msg(msg)

"""
Function to send the pre-made p2p message. 
Message must be in binary (use binascii.unhexlify)
Sends to SUPERNODE_ID
"""
def send_p2p_msg(msg):
	mrt_send1(SUPERNODE_ID,msg)

