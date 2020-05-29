dds.s"""
Matthew Parker
COSC 60 Lab 4
Stun Client 
May 2020
"""
import socket
import binascii
import sys
import random

""" DEFINITIONS """
REQUEST = '0001' # 1 for binding
SUCCESSRSP = '0101'
ERRORRSP = '0111'
MAGICCOOKIE = '2112A442'

""" ATTRIBUTES """
RESERV = '0000'
MAPPEDADDR = '0001'
RESPADDR = '0002'
CHNGADDR = '0003'
SOURCEADDR = '0004'
CHNGDADDR = '0005'
USERNAME = '0006'
PSWD = '0007'
MESSAGEINTEGRITY = '0008'
ERRORCODE = '0009'
UNKNOWN = '000A'
REFLECFORM = '000B'
REALM = '0014'
NONCE = '0015'
XORMAPPEDADDR = '0020'

"""List of stun servers that support spoofing"""
stun_servers = ['stun.ekiga.net','stun.12connect.com','stun.12voip.com','stun.voiparound.com','stun.aeta.com']

"""
Returns ASCII Rep of 96 bit value 
len = 24
"""
def create_trans_id():
	return binascii.hexlify(random.getrandbits(96).to_bytes(12,'big')).decode()


"""
Main driver for program. Sends a stun request
PARAMS:
	sock -> socket object
	host -> hostname 
	message -> string message to be send
		should include attributes and associated data
		default: ""
RETURN: 
	(resp, ip, port)
	NOTE: resp = bool, if resp = False ip and port will be ''

"""
def send_stun_request(sock,host,message="",PORT = 3478):
	RESPONSE_MESSAGE = {'resp':False,'my_ip':'','my_port':0,'other_ip' :'','other_port':0}
	tid = create_trans_id()
	lenmsg = str(len(message)).zfill(4)
	msg = ''.join([REQUEST,lenmsg,MAGICCOOKIE,tid,message])
	binmsg = binascii.unhexlify(msg) #request message in binary 
	Rc = 7 #max rc value
	#shorten the trials for the repeated tests
	if len(message) > 0:
		Rc = 2

	resp = False
	trial = 1
	timeout = 500 
	sock.sendto(binmsg,(host,PORT))
	while not resp:
		sock.settimeout(timeout/1000) # set timeout in ms
		try:
			data,addr = sock.recvfrom(2048)
			if check_header(data,tid) == 0:
				pass ## RFC 5387: Discard bad incoming messages
			else:
				resp = True

		except: 
			if trial <= Rc:
				trial += 1
				timeout += 500
				sock.sendto(binmsg,(host,PORT))
				#timeout = timeout + trial * 500
			else:
				return RESPONSE_MESSAGE

	data_len = int(binascii.hexlify(data[2:4]),16)
	data = data[20:] # cut off header

	while data_len > 0:
		att_type = binascii.hexlify(data[0:2]).decode()
		att_len = int(binascii.hexlify(data[2:4]),16)
		## Expecing this most of the time, get the IP from this
		if att_type == MAPPEDADDR:
			family = binascii.hexlify(data[4:6]).decode()
			port = int(binascii.hexlify(data[6:8]),16)
			if family == '0001': #IPV4
				# use base 16 when converting from hex -> int
				i1 = str(int(binascii.hexlify(data[8:9]),16))
				i2 = str(int(binascii.hexlify(data[9:10]),16))
				i3 = str(int(binascii.hexlify(data[10:11]),16))
				i4 = str(int(binascii.hexlify(data[11:12]),16))
				ip = ".".join([i1,i2,i3,i4])
			elif family == '0002': #IPV6
				i1 = str(binascii.hexlify(data[8:10]))
				i2 = str(binascii.hexlify(data[10:12]))
				i3 = str(binascii.hexlify(data[12:14]))
				i4 = str(binascii.hexlify(data[14:16]))
				i5 = str(binascii.hexlify(data[16:18]))
				i6 = str(binascii.hexlify(data[18:20]))
				i7 = str(binascii.hexlify(data[20:22]))
				i8 = str(binascii.hexlify(data[22:24]))
				ip = ":".join([i1,i2,i3,i4,i5,i6,i7,i8])
			RESPONSE_MESSAGE['resp'] = True
			RESPONSE_MESSAGE['my_ip'] = ip
			RESPONSE_MESSAGE['my_port'] = port
		## USING 802c and CHNGDADDR to support RFC 5780 -- should help with NAT stuff
		elif att_type == '802c' or CHNGDADDR:
			family = binascii.hexlify(data[4:6]).decode()
			port = int(binascii.hexlify(data[6:8]),16)
			if family == '0001': #IPV4
				# use base 16 when converting from hex -> int
				i1 = str(int(binascii.hexlify(data[8:9]),16))
				i2 = str(int(binascii.hexlify(data[9:10]),16))
				i3 = str(int(binascii.hexlify(data[10:11]),16))
				i4 = str(int(binascii.hexlify(data[11:12]),16))
				ip = ".".join([i1,i2,i3,i4])
			elif family == '0002': #IPV6
				i1 = str(binascii.hexlify(data[8:10]))
				i2 = str(binascii.hexlify(data[10:12]))
				i3 = str(binascii.hexlify(data[12:14]))
				i4 = str(binascii.hexlify(data[14:16]))
				i5 = str(binascii.hexlify(data[16:18]))
				i6 = str(binascii.hexlify(data[18:20]))
				i7 = str(binascii.hexlify(data[20:22]))
				i8 = str(binascii.hexlify(data[22:24]))
				ip = ":".join([i1,i2,i3,i4,i5,i6,i7,i8])
			RESPONSE_MESSAGE['resp'] = True
			RESPONSE_MESSAGE['other_ip'] = ip
			RESPONSE_MESSAGE['other_port'] = port
		new_data = 4 + att_len
		data = data[new_data:]
		data_len = len(data)
	return RESPONSE_MESSAGE


"""
See https://tools.ietf.org/html/rfc5780 for details (section 4.3)
I am combining some of these tests into smaller ones

https://tools.ietf.org/html/rfc3489#section-11.2.4 (more tests)
"""
def get_nat_type(sock, serv_list = []):

 	"""
 	Test1: UDP Connectivity Test
 	TO PASS: Must receive response AND other_ip and other_port fields must be filled
 	"""
 	t1 = False
 	servers = stun_servers
 	if len(serv_list) > 0:
 		servers = serv_list


 	stun_server = servers[0]
 	good_servers ={}
 	servs = []
 	for server in servers:
 		stun_info = send_stun_request(sock,server)
 		if stun_info['resp'] == True and stun_info['other_ip'] != '':
 			# Test 1 Passed
 			t1 = True
 			good_servers[server] = stun_info
 			servs.append(server)
 	if not t1:
 		print(f'Could not connect to a STUN server')
 		sys.exit(0)

 	count = 0
 	tries = 0
 	for serv in servs:
 		tries += 1
 		t2_msg = ''.join([CHNGADDR,'0004','00000006'])
 		s2_info = send_stun_request(sock,serv,t2_msg)
 		if s2_info['resp']:
 			count += 1


 	if count == tries: 
 		print(f'Peer may connect to ({good_servers[serv]["my_ip"]} : {good_servers[serv]["my_port"]})')

 	else:
 		print(f'I am ({good_servers[serv]["my_ip"]} : {good_servers[serv]["my_port"]}) , but probably not reachable.')
 	


"""
Extra testing for my own fun. Not for lab4
"""
def extra_testing(sock, serv_list = []):

	servers = stun_servers
	if len(serv_list) > 0:
		servers = serv_list

	stun_server = servers[0]
	good_servers ={}
	servs = []
	t1 = False
	for server in servers:
		stun_info = send_stun_request(sock,server)
		if stun_info['resp'] == True and stun_info['other_ip'] != '':
			# Test 1 Passed
			t1 = True
			good_servers[server] = stun_info
			servs.append(server)
	if not t1:
 		print(f'Could not connect to a STUN server')
 		sys.exit(0)

	count = 0
	print(f'Testing spoofing request, sending to normal server...')
	for serv in servs:
		t2_msg = ''.join([CHNGADDR,'0004','00000006'])
		s2_info = send_stun_request(sock,serv,t2_msg)
		if s2_info['resp']:
			count += 1
	print(f'{count} responses out of {len(servs)} on change request')

	print(f'Testing requesting spoofed port but normal IP......')
	t3_msg = ''.join([CHNGADDR,'0004','00000002'])
	count = 0
	for serv in servs:
		s3_info = send_stun_request(sock,t3_msg)
		if s3_info['resp']:
			count += 1
	print(f'{count} responses out of {len(servs)} with spoofed port request')

	print(f'Testing spoofing request after first sending to alternate-address...')
	count = 0
	for serv in servs:
		s4_info = send_stun_request(sock,good_servers[serv]['other_ip'],t2_msg,good_servers[serv]['other_port'])
		if s4_info['resp']:
			count+=1
	print(f'{count} responses out of {len(servs)} with spoofing after senging to address (RESTRICTED NAT)')



"""
Check header fields on incoming messages
"""
def check_header(data,tid):
	resp_msg_type = binascii.hexlify(data[0:2]).decode()
	resp_cookie = binascii.hexlify(data[4:8]).decode()
	resp_tid = binascii.hexlify(data[8:20]).decode()

	if resp_msg_type == SUCCESSRSP:
		if resp_cookie.upper() == MAGICCOOKIE and resp_tid == tid:
			return 1
	
	return 0



"""
Same as get_nat_info just doenst print
"""
def get_address(sock, serv_list = []):

 	"""
 	Test1: UDP Connectivity Test
 	TO PASS: Must receive response AND other_ip and other_port fields must be filled
 	"""
 	t1 = False
 	servers = stun_servers
 	if len(serv_list) > 0:
 		servers = serv_list


 	stun_server = servers[0]
 	good_servers ={}
 	servs = []
 	for server in servers:
 		stun_info = send_stun_request(sock,server)
 		if stun_info['resp'] == True and stun_info['other_ip'] != '':
 			# Test 1 Passed
 			t1 = True
 			good_servers[server] = stun_info
 			servs.append(server)
 	if not t1:
 		print(f'Could not connect to a STUN server')
 		sys.exit(0)

 	count = 0
 	tries = 0
 	for serv in servs:
 		tries += 1
 		t2_msg = ''.join([CHNGADDR,'0004','00000006'])
 		s2_info = send_stun_request(sock,serv,t2_msg)
 		if s2_info['resp']:
 			count += 1

 	return (good_servers[serv]["my_ip"], good_servers[serv]["my_port"])

