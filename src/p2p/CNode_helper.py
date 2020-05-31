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
RECV_ID = 0


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
	return SUPERNODE_ID

"""
Function to get own ip and port (public) for the client
Takes in an initialized UDP socket
"""
def get_own_addr(sock):
	# get_address() is from STUN module
	ip, port = get_address(sock)
	port = str(port).zfill(5)
	ip = str(ip).split('.')
	ip = [x.zfill(3) for x in ip]
	ip = ''.join(ip)
	return (ip, port)

"""
Function to join the network, takes one parameter
join_type:
	0: join as chlidnode
	1: join as supernode
"""
def join_p2p(recv_sock,send_id, source_ip, source_port, join_type = 0):
	global RECV_ID
	mrt_open(s=recv_sock)
	values = ''.join([R_JOIN,f'{join_type:04d}'])
	msg_len = len(values)
	msg = ''.join([REQUEST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id,msg)
	RECV_ID = mrt_accept1()
	return RECV_ID
	


"""
Function to create the request for DHT
Takes one arg: all (bool)
	all = True: send '000d'
	all = False: send '000c'
	default is True
"""
def request_local_dht(send_id, source_ip, source_port, filename=''):
	if len(filename) > 0:
		values = ''.join([R_LOCAL_DHT,f'{len(filename):04d}',filename])
	else:
		values = ''.join([R_LOCAL_DHT,'0000'])
	msg_len = len(values)
	msg = ''.join([REQUEST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id,msg)


def request_global_dht(send_id, source_ip, source_port, filename=''):
	if len(filename) > 0:
		values = ''.join([R_GLOBAL_DHT,f'{len(filename):04d}',filename])
	else:
		values = ''.join([R_GLOBAL_DHT,'0000'])
	msg_len = len(values)
	msg = ''.join([REQUEST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id,msg)

"""
Function to request supernode list
Takes no parameters
"""
def request_super_list(send_id, source_ip, source_port):
	values = ''.join([R_LIST])
	msg_len = len(values)
	msg = ''.join([REQUEST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id,msg)


"""
Function to send new file post
PARAMETERS: 
	File Size: int of byte size
	File ID length: int of byte size
	File ID: string
"""
def post_file(send_id, source_ip, source_port, file_size, id_size, filename):
	values = ''.join([P_NEW_FILE,f'{file_size:04d}',f'{id_size:04d}',filename])
	msg_len = len(values)
	msg = ''.join([POST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id,msg)


"""
Function to request a file
PARAMETERS:
	file_id: str
	ip: ip string in standard format ie 'xxx.xxx.xxx.xxx'
	port: integer
"""


def request_file(send_id, source_ip, source_port, file_id, ip, port):
	# Send request for file along to supernode:
	id_len = len(file_id)
	padded_ip = str(ip).split('.')
	padded_ip = [x.zfill(3) for x in padded_ip]
	padded_ip = ''.join(padded_ip)
	padded_port = port.zfill(5)
	values = ''.join([R_FILE_TRANS,f'{id_len:04d}',file_id,padded_ip,padded_port])
	msg_len = len(values)
	msg = ''.join([REQUEST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id, msg)
	# Start UDP hole punch with direct peer:
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto('UDP-holepunch'.encode(),(ip, port)) # hole punch
	download_id = mrt_accept1()
	return download_id #TODO: Need to actually download file with mrt_receive1(download_id) in the input listener

	#TODO: 1. Send first request to supernode to relay message along
	# 2. Start UDP hole punch with direct peer
	# 3. MRT_ACCEPT() new connection from peer (hopefully hole punch worked because this blocks)
		


"""
Function to send request to disconnect
"""
def send_disconnect(send_id, source_ip, source_port):
	values = ''.join([P_DISCONNECT])
	msg_len = len(values)
	msg = ''.join([POST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id, msg)

"""
Function to send the pre-made p2p message. 
Message must be in binary (use binascii.unhexlify)
Sends to SUPERNODE_ID
"""
def send_p2p_msg(sock,msg):
	print(f'sending to: {sock}, msg: {msg}')
	mrt_send1(sock, msg)
