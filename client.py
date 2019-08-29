import socket
from dh import diffie_hellman


IP = "127.0.0.1"
SERVER_PORT = 8083
CLIENT_PORT = 8084
CACHE_PORT = 8086
PACKET_SIZE = 64


# Setup client connection to server.
sock_out = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock_in = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock_in.bind((IP, CLIENT_PORT))

def send(data, port):
	packets = ["%s"%data[i:i+PACKET_SIZE] for i in range(0,len(data),PACKET_SIZE)]
	for p in packets:
		sock_out.sendto(p, (IP, port))
	sock_out.sendto("EOF", (IP, port))

def receive():
	data = ""
	while True:
		msg, addr = sock_in.recvfrom(PACKET_SIZE) # buffer size is 64 bytes
		if (msg=="EOF"):
			break
		else:
			data += msg
	return data

#Perform DH and send public values to server. 
dh = diffie_hellman()
key = dh.generate_public_key()
signed = dh.sign_message(key, "certs/client.key")

data = signed + key
send(data, SERVER_PORT)




# Receive public values from server, create shared secret + Fernet.
data=receive()

signature = data[0:256]
data = data[256:]; 

verify = dh.verify_message(data, signature, "certs/server.key") # client
if verify == 1:
	f = dh.generate_symetric_encryption_key(data)

	# Encrypt a message using Fernet, send to server.
	token = f.encrypt(b"Super secret hax")
	send(token, CACHE_PORT)
	send("Server", CACHE_PORT)
	print("Secret msg sent!")
	send("Close",CACHE_PORT)
else:
	print "Invalid signature from server"
	send("Close",CACHE_PORT)
# Close connections. 
sock_out.close()
sock_in.close()
