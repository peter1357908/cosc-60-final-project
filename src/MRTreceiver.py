"""
Matthew Parker
MRT receiver application for COSC 60 Lab3

APRIL 2020
"""
import sys
from mrt import *
from signal import signal, SIGINT


def check_args():
	if len(sys.argv) != 2:
		print(f'USAGE {sys.argv[0]} num_senders')
		sys.exit(1)
	return 0

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    try:
    	mrt_close()
    except:
    	pass
    sys.exit(0)


def main():

	signal(SIGINT, handler)
	mrt_open()
	connections = []

	for i in range(int(sys.argv[1])):
		conn = mrt_accept1()
		connections.append(conn)


	for i in range(len(connections)):
		data = mrt_receive1(connections[i])
		while data != -1:
			print(f'Connection: {i+1}, data: {data.decode()}')
			data = mrt_receive1(connections[i])
		print(f'Connection {i+1} done, onto the next....')

	print("Done reading.")

	mrt_close()


if __name__=='__main__':
	check_args()

	main()

	sys.exit(0)






