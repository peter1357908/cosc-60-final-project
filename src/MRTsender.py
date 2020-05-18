"""
Matthew Parker
MRT receiver application for COSC 60 Lab3

APRIL 2020
"""
import sys
from mrt import *
from signal import signal, SIGINT


def check_args():
	if len(sys.argv) != 1:
		print(f'USAGE {sys.argv[0]} TOO MANY ARGS')
		sys.exit(1)
	return 0

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    try:
    	mrt_disconnect(conn)
    except:
    	pass
    exit(0)


def main():

	conn = mrt_connect()



	#send_message = sys.stdin.readline()

	send_message = ""
	for i in range(2000):
		send_message = send_message + str(i) + " "

	print(len(send_message.encode()))

	while send_message.strip().strip('\r') != ":EXIT":
		mrt_send1(conn,send_message)
		send_message = sys.stdin.readline()

	mrt_disconnect(conn)


	exit(0)

if __name__=='__main__':
	check_args()

	main()

	exit(0)
