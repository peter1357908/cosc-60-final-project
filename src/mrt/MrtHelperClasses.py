"""
Matthew Parker
COSC 60

Data Structures for Lab3 Mrt
APRIL 2020
"""

import time
import threading
import sys




"""
Repeated Timer object based on threading timer.
Found this on https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds
"""
class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def check_running(self):
  	return self.is_running

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False

"""
Packet object. Mainly used for receving messages 
"""
class Packet:
	def __init__(self):
		self.checksum = 0
		self.kind = ""
		self.window = "0000"
		self.conn_id = 0
		self.frag = 0
		self.data = b''

	def create_inpacket(self,data):
		self.kind = data[4:8].decode()
		self.window = data[8:12].decode()
		self.conn_id = int(data[12:16].decode())
		self.frag = int(data[16:20].decode())
		self.data = data[20:]

	def create_ack_packet(self,checksum,kind,window,conn,frag):
		self.checksum = checksum
		self.kind = kind
		self.window = window
		self.conn = conn
		self.frag = frag

	def __str__(self):
		return f'Kind = {self.kind}, Window = {self.window}, conn_id = {self.conn_id}, frag = {self.frag}'

"""
Data structure for handing connections
Holds the conn_id, address, window, buffer adn frag
Also has a timer for repeat sending of messages
"""
class Connection: 
	def __init__(self,conn_id,frag,addr):
		self.conn_id = conn_id
		self.addr = addr
		self.window = 0
		self.buffer = b''
		self.frag = 0
		self.timer = ''
		self.lmt = ""
		self.sending = False
		self.receiving = False
		self.send_timers = [] #list of timers to resend messages
		self.send_queue = {} #sending queue for outgoing messages
		self.latest_frag = 0 #keep track of latest_frag received
		self.qrf = 0 #quick return field

	def set_timer(self,interval,function,*args):
		self.timer = RepeatedTimer(interval,function,*args)
		self.timer.stop()

	def start_timer(self):
		self.timer.start()
	
	def increase_qrf(self):
		self.qrf += 1
	def reset_qrf(self):
		self.qrf = 0

	def get_latest_frag(self):
		self.latest_frag +=1
		return self.latest_frag

	def update_frag(self,frag):
		self.frag = frag

	def stop_timer(self):
		self.timer.stop()

	def add_send_timer(self,func,*args):
		self.send_timers.append(RepeatedTimer(2,func,*args))

	def del_send_timer(self):
		self.send_timers[0].stop()
		del self.send_timers[0]

	def add_send_queue(self,key,value):
		self.send_queue[key] = value

	def del_send_queue(self,key):
		del self.send_queue[key]

	def check_timer(self):
		if type(self.timer) == str:
			return False
		return self.timer.check_running()

	def is_sending(self):
		return self.sending

	def is_receiving(self):
		return self.receiving

	def get_id(self):
		return int(self.conn_id)

		#read entire buffer
	def dump_buffer(self):
		b_temp = self.buffer
		self.buffer = b''
		return b_temp

	## Return ascii representation of data padded with 0's 
	## always 4 bytes
	def return_padded(self):
		pcid = pad(self.conn_id)
		pw = pad(self.window)
		pf = pad(self.frag)
		return (pcid,pw,pf)

	def update_lmt(self,msg_type):
		self.lmt = msg_type

	def update_window_size(self):
		self.window = 9999-len(self.buffer)
		return self.window

	def check_window_size(self):
		return self.window

	def add_to_buffer(self,data):
		self.buffer += data

	## read data from buffer
	def read_from_buffer(self,len_read):
		b_temp = self.buffer[:len_read]
		self.buffer = self.buffer[len_read:]
		return b_temp

	def check_buffer_size(self):
		return 9999-len(self.buffer)




def pad(x):
	pad = 4 - len(str(x))
	return "0" * pad + str(x)