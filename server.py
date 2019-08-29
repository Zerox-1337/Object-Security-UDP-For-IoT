import socket
from dh import diffie_hellman
import time


IP = "127.0.0.1"
SERVER_PORT = 8083
CLIENT_PORT = 8084
CACHE_PORT = 8085
PACKET_SIZE = 64

# Setup Server connection to client.
sock = socket.socket(socket.AF_INET, # Internet
                   socket.SOCK_DGRAM) # UDP
sock.bind((IP, SERVER_PORT))
print("UDP is up!")

def receive():
	data = ""
	while True:
		msg, addr = sock.recvfrom(PACKET_SIZE) # buffer size is 64 bytes
		if (msg=="EOF"):
			break
		else:
			data += msg
	return data

def send(data, port):
	packets = ["%s"%data[i:i+PACKET_SIZE] for i in range(0,len(data),PACKET_SIZE)]
	for p in packets:
		sock.sendto(p, (IP, port))
	sock.sendto("EOF", (IP, port))


#Perform DH. 
dh = diffie_hellman()
key = dh.generate_public_key()


# Receive public values from client, create shared secret + Fernet.
data=receive()
signature = data[0:256]
data = data[256:]
verify = dh.verify_message(data, signature, "certs/client.key")


# Send key with signed signature using public/private keys
signed = dh.sign_message(key, "certs/server.key") # client


send(signed + key, CLIENT_PORT) # Concat so that the first 256 bytes is the signature


if verify == 1:
	f = dh.generate_symetric_encryption_key(data) # Fernet created from shared secret.

	# Receive encrypted Fernet message from client
	data = "empty"
	while data=="empty":
		time.sleep(0.1)
		send("Server", CACHE_PORT)
		data =receive()
	valid = 1;
	try:
		decrypted = f.decrypt(data, 10) # 10 seconds.
	except cryptography.fernet.InvalidToken:
		valid = 0
	if valid == 1:
		print("Secret message received: "+decrypted)
		send("Close",CACHE_PORT)
	else : 
		print "Error: Old Message"
		send("Close",CACHE_PORT)
else:
	print "Invalid signature from client"
	send("Close",CACHE_PORT)
