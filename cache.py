import socket
from dh import diffie_hellman
import threading
import time
from threading import Lock


IP = "127.0.0.1"
SERVER_PORT_IN = 8085
SERVER_PORT_OUT = 8083
CLIENT_PORT_IN = 8086
CLIENT_PORT_OUT = 8084
PACKET_SIZE = 64

# Setup connection to client.
sock_client = socket.socket(socket.AF_INET, # Internet
                   socket.SOCK_DGRAM) # UDP


sock_client.bind((IP, CLIENT_PORT_IN))



#sock_client_out.bind((IP, CLIENT_PORT_OUT))

# Setup connection to server.
sock_server = socket.socket(socket.AF_INET, # Internet
                   socket.SOCK_DGRAM) # UDP

sock_server.bind((IP, SERVER_PORT_IN))



#sock_server_out.bind((IP, SERVER_PORT_OUT))

print("CACHE is up!")

def receive(sock):
	data = ""
	while True:
		msg, addr = sock.recvfrom(PACKET_SIZE) # buffer size is 64 bytes
		if (msg=="EOF"):
			break
		else:
			data += msg
	return data

def send(data, sock, port):
	packets = ["%s"%data[i:i+PACKET_SIZE] for i in range(0,len(data),PACKET_SIZE)]
	for p in packets:
		sock.sendto(p, (IP, port))
	sock.sendto("EOF", (IP, port))

exitFlag = 0

class cacheThread (threading.Thread):
   def __init__(self, sock, port, lock, mailbox):
	threading.Thread.__init__(self)
	self.sock = sock
	self.port = port
	self.lock = lock
	self.mailbox = mailbox
   def run(self):
	print "Starting " + self.name
	cache_thread(self.sock, self.port, self.lock, self.mailbox)
	print "Exiting " + self.name

def cache_thread(sock, port, lock, mailbox):
	online = 1
	while online:
		data = receive(sock)
		if data=="Client":
			try:
				lock.acquire()
				mail = mailbox.pop("Client")
				send(mail,sock,port)
				lock.release()
			except:
				send("empty",sock,port)
				lock.release()
		elif data=="Server":
			try:
				lock.acquire()
				mail = mailbox.pop("Server")
				send(mail,sock,port)
			except:
				lock.acquire()
				send("empty",sock,port)
				lock.release()
		elif data=="Close":
				online=0
		else:
			recipient = receive(sock)
			lock.acquire()
			mailbox[recipient]=data
			lock.release()

# Create new threads
lock = Lock()
mailbox = dict()
thread1 = cacheThread(sock_client, CLIENT_PORT_OUT, lock, mailbox)
thread2 = cacheThread(sock_server, SERVER_PORT_OUT, lock, mailbox)

# Start new Threads
thread1.start()
thread2.start()
thread1.join()
thread2.join()


print "Shuting down"
