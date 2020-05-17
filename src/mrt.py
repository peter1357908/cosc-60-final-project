# Matthew Parker
# COSC 60 Lab 3
# Mini Reliable Transport Protocol

import sys
import socket
import threading 
from threading import Timer
from collections import deque
import time
from MrtHelperClasses import *

conns = {}
senders = {}
conn_queue = deque()
close = False
conn_count = 0
sock = 0
recently_closed = []

buffer_lock = threading.Lock() #buffer lock to help with data races


"""
mrt_open: indicate ready-ness to receive incoming connections

Create new socket, startup thread
"""
def mrt_open(host = '192.168.0.249', port = 11235):
	global sock,close
	close = False
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((host,port))
	sock = s
	threading.Thread(target=start_receiver_thread, args=[s]).start()

"""
accept an incoming connection (return a connection), guaranteed to return one (will block until there is one)
"""
def mrt_accept1():
	if len(conn_queue) > 0:
		conn = conn_queue.popleft()
		conn.stop_timer()
		conn.update_window_size()
		send_ack_message(conn.get_id(),"ACON")
		return conn.get_id()
	else:
		while len(conn_queue) == 0:
			time.sleep(.1)
		conn = conn_queue.popleft()
		conn.stop_timer()
		conn.update_window_size()
		send_ack_message(conn.get_id(),"ACON")
		return conn.get_id()


"""
accept all incoming connections (returns a possibly empty set/array of connections), guaranteed not to block
"""
def mrt_accept_all():
	global conn_queue
	ret_conns = []
	while len(conn_queue) > 0:
		conn = conn_queue.popleft()
		conn.stop_timer()
		conn.update_window_size()
		send_ack_message(conn.get_id(),"ACON")
		ret_conns.append(conn.get_id())

	return ret_conns

"""
given a set of connections, returns a connection in which there is currently data to be received (may return no connection if there is no such connection,
 never blocks and ensures that a mrt_receive1 call to the resulting connection will not block either)

Parameters: 
	connections: list of connection ids
"""
def mrt_probe(connections):
	data_ready = []
	for conn in connections: 
		if conn in conns.keys() and len(conns[conn].buffer) > 0:
			data_ready.append(conn)

	return data_ready

"""
Wait for at least one byte of data over a given connection, guaranteed to return data except if the connection closes (will block until there is data or the connection closes)

Loops as long as the id is in the dictionary (not closed)
if there is data in the buffer, return the entire buffer 
otherwise sleep and repeat
"""
def mrt_receive1(id):
	while id in conns:
		conn = conns[id]
		if len(conn.buffer) > 0:
			buffer_lock.acquire()

			data = conn.dump_buffer()
			conn.update_window_size()

			buffer_lock.release()
			return data
		else:
			time.sleep(0.1)
	return -1 #connection closed


"""
Close everything down. Make sure to delete everything then set Close = True
"""
def mrt_close():
	global close,conn_queue,conns
	close = True
	for id in conns.keys():
		send_ack_message(id,"ACLS")
		send_ack_message(id,"ACLS")
		send_ack_message(id,"ACLS")
		try:
			conn_queue[id].stop_timer()
		except:
			pass
	return 0


"""
connect to a given server (return a connection)
"""
def mrt_connect(host  = '192.168.0.249',port = 11235):
	global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	addr = (host,port)
	id = handshake(addr)
	senders[id].receiving=True
	recv_thread = threading.Thread(target=sender_recv_thread,args=(id,))
	recv_thread.start()
	return id

"""
Disconnect from server, close connection
will loop until it gets ACLS from server 
"""
def mrt_disconnect(id):
	conn = senders[id]
	kind = "RCLS"
	window = "0000"
	conn_id = conn.conn_id
	frag = "0000"
	data = ''
	cls_msg = kind+window+conn_id+frag+data
	cls_sum = ichecksum(cls_msg)
	cls_bytes = cls_sum.to_bytes(4,'big')+cls_msg.encode()

	while len(conn.buffer) > 0 or len(conn.send_queue) > 0:
		time.sleep(.5)

	closed = False
	conn.sending = False
	conn.receiving = False

	#failsafe, just kill the timers
	for i in range(len(conn.send_timers)):
		conn.del_send_timer()

	# sleep until both window and buffer are zero



	while not closed:
		sock.settimeout(.03)
		try:
			sock.sendto(cls_bytes,conn.addr)
			data, addr = sock.recvfrom(2048)
			if verify_checksum(data) != 0: # discard packet if checksum doesnt add up
					continue
			p = Packet()
			p.create_inpacket(data)

			if p.kind == "ACLS":
				closed = True
				del senders[id]
		except:
			time.sleep(.1)

	sock.settimeout(None)


"""
Called when a sender receives an ACLS message before it has called mrt_disconnect
"""
def forced_shutdown(id):
	print(f'Received ACLS before done sending.... Sender forcing me to close...')
	sender = senders[id]
	sender.sending = False
	sender.receiving = False
	for tmr in sender.send_timers:
		tmr.stop()

	del senders[id]


"""
send a chunk of data over a given connection (may temporarily block execution if the receiver is busy/full)
data is a string
"""
def mrt_send1(id, data):
	copied = False
	if senders[id].is_sending() == False:
		senders[id].sending = True
		send_thread = threading.Thread(target=sender_send_thread,args=(id,))
		send_thread.start()

	if len(data) >= 9999:
		print('Message too long')
		return -1
	while not copied:
		if senders[id].check_buffer_size() > len(data):
			buffer_lock.acquire()
			senders[id].add_to_buffer(data.encode())
			buffer_lock.release()
			copied = True
		else:
			time.sleep(.2)

	return 0
"""
Handles sending of messages to the receiver
Loops until done
"""
def sender_send_thread(id):
	sender = senders[id]
	#loop while sending 
	while sender.is_sending():
		if sender.window == 0 or (len(sender.send_queue) > 0 and sender.window < len(sender.send_queue[min(sender.send_queue.keys())])):
			buffer_lock.acquire()
			for tmr in sender.send_timers:
				tmr.stop()
			buffer_lock.release()	
			send_window_test(id)
			time.sleep(.6)
			buffer_lock.acquire()
			for tmr in sender.send_timers:
				tmr.start()
			buffer_lock.release()
		elif len(sender.buffer) > 0:
			if len(sender.send_queue) < 6:
				add_to_send_queue(sender)
			else:
				time.sleep(.5)
		else:
			time.sleep(.2)

"""
send a tester message to check the current window size, used when pausing messages from low window space
"""
def send_window_test(id):
	kind = "DATA"
	window = "9999"
	cid = senders[id].conn_id
	frag = pad(senders[id].frag)
	data = ''
	pre_message = kind+window+cid+frag+data
	csum = ichecksum(pre_message)
	msg_bytes = csum.to_bytes(4,'big')+pre_message.encode()
	sock.sendto(msg_bytes,senders[id].addr)


"""
Spins up a receiever thread to handle all incoming messages for the sender
Responsible for updating latest frag, sending quick responses etc
"""
def sender_recv_thread(id):
	sender = senders[id]
	while sender.is_receiving():
		data, addr = sock.recvfrom(2048)
		if verify_checksum(data) != 0: # discard packet if checksum doesnt add up
				continue
		p = Packet()
		p.create_inpacket(data)
		#print(p)

		if p.kind == "ACLS":
			forced_shutdown(id)
		sender.window = int(p.window)
		if len(sender.send_queue.keys()) > 0 and p.frag == min(sender.send_queue.keys()):
			buffer_lock.acquire()
			if len(sender.send_timers)>0:
				sender.del_send_timer()
			sender.del_send_queue(p.frag)
			sender.update_frag(p.frag)
			sender.reset_qrf()
			buffer_lock.release()
			#print(f'Killed packet timer {p.frag} timers now: {sender.send_timers}')
		elif len(sender.send_queue.keys()) > 0 and p.frag != min(sender.send_queue.keys()):
			sender.increase_qrf()
			if sender.qrf == 3:
				quick_resend(id)


"""
Implementation of the quick resend to beat timeout
When 3 ou
"""
def quick_resend(id):
	sender = senders[id]
	min_frag = min(sender.send_queue.keys())
	sock.sendto(sender.send_queue[min_frag],sender.addr)
	sock.sendto(sender.send_queue[min_frag],sender.addr)
	sock.sendto(sender.send_queue[min_frag],sender.addr)
	sender.reset_qrf()


def add_to_send_queue(sender):
	buffer_lock.acquire()
	while len(sender.send_queue) < 6 and len(sender.buffer) > 0:
		size_data = min(1418,len(sender.buffer))
		msg_data = sender.read_from_buffer(size_data)
		bytes_message = build_data_message(sender,msg_data)
		sender.send_queue[sender.latest_frag] = bytes_message

		sender.add_send_timer(send_timeout,sender,sender.latest_frag)
		sock.sendto(bytes_message,sender.addr)

	buffer_lock.release()



"""
resend message on timeout
"""
def send_timeout(sender,frag):
	try:
		sock.sendto(sender.send_queue[frag],sender.addr)
	except:
		pass



"""
build and return data message
"""
def build_data_message(sender,data):
	kind = "DATA"
	window = "0000"
	sid = sender.conn_id
	frag = pad(sender.get_latest_frag())
	pre_message = kind+window+sid+frag+data.decode()
	icsum = ichecksum(pre_message)
	bytes_message = icsum.to_bytes(4,'big') + pre_message.encode()
	return bytes_message

"""
break data into 1400 byte segments and return list
the list includes messages that are ready to send
"""



"""
Initiate handshake with server, return connection id and store connection stuff in senders{}
"""
def handshake(addr):
	global sock
	kind = "RCON"
	window_size = "0000"
	id = "0000"
	frag = "0000"
	data = ''
	join_msg = kind+window_size+id+frag+data
	jcsum = ichecksum(join_msg)
	bytes_join = jcsum.to_bytes(4,'big')+join_msg.encode()
	joined = False

	sock.settimeout(.01)
	while not joined:
		try:
			sock.sendto(bytes_join,addr)
			data, addr = sock.recvfrom(2048)
			if verify_checksum(data) != 0: # discard packet if checksum doesnt add up
					continue
			p = Packet()
			p.create_inpacket(data)

			if p.kind == "ACON":
				id = reg_sender(p,addr)
				joined = True

		except:
			time.sleep(.1)

	sock.settimeout(None) #back into blocking mode
	return id

"""
Register sender for connect call
"""
def reg_sender(packet,addr):
	global senders
	conn_id = pad(packet.conn_id)
	c = Connection(conn_id,packet.frag,addr)
	senders[c.get_id()] = c

	return c.get_id()



"""
Should handle all incoming connections on the socket

Starts by checking checksum, will discard if bad.
Creates a packet and fills with data before sending to the packet handler function

"""
def start_receiver_thread(socket):
	global close
	while close == False:
		data, addr = socket.recvfrom(2048)
		if verify_checksum(data) != 0: # discard packet if checksum doesnt add up
			continue
		p = Packet()
		p.create_inpacket(data)
		if p.kind == "RCLS" and p.conn_id in recently_closed:
			resend_close(addr)
		else:
			if check_conn(p,addr) == 0: 
				reg_conn(p,addr)

			direct_server_message(p)


"""
directs messages depending on the Kind
Params:
	packet : packet from packet class

"""
def direct_server_message(packet):
	conn = conns[packet.conn_id]
	if packet.kind == "RCON":
		conn.update_frag(packet.frag) # update the frag to have last frag number
		conn.update_lmt("ACON") # update the last message type
		send_ack_message(packet.conn_id,"ACON")
		if not conn.check_timer() and not close:
			conn.set_timer(.01,window_zero_repeat,packet.conn_id,"ACON")
			conn.start_timer()
	elif packet.kind == "DATA":
		if conn in conn_queue: # if its still in the queue it hasnt been accepted, check for empty data otherwise discard
			if len(packet.data) == 0:
				# sender has no data to send right now, stop sending timed messages
				conn.stop_timer()
		else: 
			#connection has been accepted
			# updated frag and LMT
			if packet.window == "9999":
				send_ack_message(packet.conn_id,conn.lmt)
			elif check_frag(packet) > 1:
				# packet out of order, dont store resend last ACK
				#print(f'packet out of order, packet frag: {packet.frag}, conn_frag: {conn.frag}')
				send_ack_message(packet.conn_id,conn.lmt)
			elif check_frag(packet) <=0:
				#print(f'packet already received, resending frag')
				resend_old_packet(packet.conn_id,packet.frag,conn.lmt)
			else:
				if check_buffer_space(packet.conn_id,packet.data) == 0:
					#print(f'not enough buffer space, sending ACK')
					#not enough space, resend lass ack with window size
					send_ack_message(packet.conn_id,conn.lmt)
				else:
					store_data(packet)
					#print(f'stored data, buffer now looks like {conn.buffer} and window size of {conn.window}')
					send_ack_message(packet.conn_id,conn.lmt)

	elif packet.kind == "RCLS":
		if len(conn.buffer) >0:
			pass
		else:
			send_ack_message(packet.conn_id,"ACLS")
			close_connection(packet.conn_id)
	else :
		pass


def resend_old_packet(id,frag,msg_kind):
	#print(f'ID: {id}, conns: {conns.keys()}')
	addr = conns[id].addr
	cid,window,f = conns[id].return_padded()
	frag = pad(frag)
	pre_message = msg_kind + window + cid + frag + ''
	checksum = ichecksum(pre_message)
	send_message(addr, checksum, pre_message)

"""
resent the close connection message
"""
def resend_close(addr):
	gc_msg = "ACLS000000000000"
	gc_sum = ichecksum(gc_msg)
	gc_bytes = gc_sum.to_bytes(4,'big')+gc_msg.encode()
	sock.sendto(gc_bytes,addr)
	sock.sendto(gc_bytes,addr)
	sock.sendto(gc_bytes,addr)


"""
closes down connection, stops timer and deletes object
"""
def close_connection(id):
	conn = conns[id]
	recently_closed.append(id)
	try:
		conn.stop_timer()
	finally:
		pass
	del conns[id]
	del conn 

"""
Double check the window size before adding
Used before adding to buffer 
"""
def check_buffer_space(id, data):
	conn = conns[id]
	if conn.update_window_size() < len(data):
		return 0
	return 1

"""
Stores data from packet into buffer 
LOCKED FUNCTION to prevent data races

Completes the following:
	adds to buffer (prechecked buffer size)
	updates the latest frag
	updates last message type (lmt)
	updates window size
"""
def store_data(packet):
	buffer_lock.acquire()
	conn = conns[packet.conn_id]
	conn.add_to_buffer(packet.data)
	conn.update_window_size()
	conn.update_frag(packet.frag)
	conn.update_lmt("ADAT")
	buffer_lock.release()


"""
Check that the message is the expected next message
packet frag = last_frag + 1
"""
def check_frag(packet):
	return packet.frag - conns[packet.conn_id].frag 

"""
Repeat the last ACK sent due to zero window
WIll stop timer when window size increases or 
"""
def window_zero_repeat(id, msg_kind):
	## if the window size has increased stop sending
	## if the sender marked window hold stop sending
	if conns[id].check_window_size() > 0:
		conns[id].stop_timer()
	send_ack_message(id,msg_kind)

"""
Used to ack messages from sender
Pass connection and message kind

"""
def send_ack_message(id,msg_kind):
	#print(f'ID: {id}, conns: {conns.keys()}')
	addr = conns[id].addr
	cid,window,frag = conns[id].return_padded()
	pre_message = msg_kind + window + cid + frag + ''
	checksum = ichecksum(pre_message)
	send_message(addr, checksum, pre_message)
		
"""
sends messages out. Takes checksum and premessage as args
"""
def send_message(addr,checksum, pre_message):
	final_msg = checksum.to_bytes(4,'big') + pre_message.encode()
	sock.sendto(final_msg,addr)

"""
Creates a new connection. Used when reading a packet of kind RCON and conn_id = 0
Also sets the packet id to the new ID
"""
def reg_conn(packet,addr):
	global conn_count, conn_queue,conns
	conn_count += 1
	packet.conn_id=conn_count
	conn_id = pad(conn_count)
	c = Connection(conn_id,packet.frag,addr)
	conns[conn_count] = c
	conn_queue.append(c)

"""
Pads ints to have four bytes ascii
example pad(55) -> "0055"
"""
def pad(x):
	pad = 4 - len(str(x))
	return "0" * pad + str(x)
"""
Check the connection id
returns 0 if id == 0 or id not in conn_ids (shouldnt happen but fail safe)
"""
def check_conn(packet,addr):

	if packet.conn_id == 0 and len(conns) == 0:
		return 0
	else:
		for key in conns.keys():
			if key == packet.conn_id:
				return 1
			elif addr == conns[key].addr:
				packet.conn_id = key
				return 1
		return 0
"""
Calculate the Internet Checksum 
Using this code from https://github.com/mdelatorre/checksum/blob/master/ichecksum.py
"""
def ichecksum(data, sum=0):
    """ Compute the Internet Checksum of the supplied data.  The checksum is
    initialized to zero.  Place the return value in the checksum field of a
    packet.  When the packet is received, check the checksum, by passing
    in the checksum field of the packet and the data.  If the result is zero,
    then the checksum has not detected an error.
    """
    # make 16 bit words out of every two adjacent 8 bit words in the packet
    # and add them up
    for i in range(0,len(data),2):
        if i + 1 >= len(data):
            sum += ord(data[i]) & 0xFF
        else:
            w = ((ord(data[i]) << 8) & 0xFF00) + (ord(data[i+1]) & 0xFF)
            sum += w

    # take only 16 bits out of the 32 bit sum and add up the carries
    while (sum >> 16) > 0:
        sum = (sum & 0xFFFF) + (sum >> 16)

    # one's complement the result
    sum = ~sum

    return sum & 0xFFFF

"""
Verifies the checksum using djb2 hash
Return
	0: successful checksum
   !0: bad checksum, discard 
"""
def verify_checksum(data):
	csum_recv = int.from_bytes(data[:4],'big') # Get the first 4 bytes
	csum_calc = ichecksum(data[4:].decode())
	return csum_recv - csum_calc


