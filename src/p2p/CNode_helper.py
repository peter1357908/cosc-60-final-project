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
import time

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

# The following three values will be updated by connect_p2p()
bootstrapper_ip = '192.168.0.249'
bootstrapper_port = 11235
bootstrapper_sendID = 0


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
def connect_p2p(ip, port):
	global bootstrapper_ip, bootstrapper_port, bootstrapper_sendID
	bootstrapper_ip = ip
	bootstrapper_port = port
	bootstrapper_sendID = mrt_connect(ip, port)
	return bootstrapper_sendID

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
def join_p2p(recv_sock, send_id, source_ip, source_port, join_type = 0):
	mrt_open(s=recv_sock)
	values = ''.join([R_JOIN,f'{join_type:04d}'])
	msg_len = len(values)
	msg = ''.join([REQUEST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id,msg)
	return mrt_accept1()
	


"""
Function to create the request for DHT
Takes one arg: all (bool)
	all = True: send '000d'
	all = False: send '000c'
	default is True
"""
def request_local_dht(send_id, source_ip, source_port, filename):
	if len(filename) > 0:
		values = ''.join([R_LOCAL_DHT,f'{len(filename):04d}',filename])
	else:
		values = ''.join([R_LOCAL_DHT,'0000'])
	msg_len = len(values)
	msg = ''.join([REQUEST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id,msg)


def request_global_dht(send_id, source_ip, source_port, filename):
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
	file_id: string
	ip addresses: strings in P2P format (zero-padded; 12 bytes)
	port numbers: strings in P2P format (zero-padded; 5 bytes)
"""
def request_file(send_id, source_ip, source_port, file_id, maintainer_ip, maintainer_port, offerer_ip, offerer_port):
	file_id_len = len(file_id)

	values = f'{R_FILE_TRANS}{file_id_len:04d}{file_id}{offerer_ip}{offerer_port}{maintainer_ip}{maintainer_port}'
	msg_len = len(values)
	msg = ''.join([REQUEST, f'{msg_len:04d}', source_ip, source_port, values])
	send_p2p_msg(send_id, msg)

	if (offerer_ip, offerer_port) != (bootstrapper_ip, bootstrapper_port):
		# TODO: make it so that the holepunching only stops after the connection is accepted
		for _i in range(3):
			offerer_ip_split = [int(offerer_ip[i:i+3]) for i in range(0, 12, 3)]
			offerer_ip_with_dots = ".".join([str(x) for x in offerer_ip_split])
			mrt_hole_punch(offerer_ip_with_dots, int(offerer_port))
			time.sleep(.2)

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
"""
def send_p2p_msg(sock,msg):
	print(f'*** SEND_P2P_MSG sending to: {sock}, msg: {msg}')
	mrt_send1(sock, msg)
