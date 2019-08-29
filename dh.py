from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidSignature
import base64

class diffie_hellman:
	
	def __init__(self):
		prime_14=0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
		pn = dh.DHParameterNumbers(prime_14, 2)
		parameters = pn.parameters(default_backend())	
		self.private_key = parameters.generate_private_key()
		self.public_key = self.private_key.public_key()

	def generate_public_key(self):
		return self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

	
	def generate_symetric_encryption_key(self,data):
		key = load_pem_public_key(data, backend=default_backend())
		shared_key = self.private_key.exchange(key)
		derived_key = HKDF(
			algorithm=hashes.SHA256(),
			length=32,
			salt=None,
			info=b'handshake data',
			backend=default_backend()
		).derive(shared_key)
		key = base64.urlsafe_b64encode(derived_key)
		f = Fernet(key)
		return f
 
	# We assume that client and server got each others public key already

	def load_private_key(self,key_file_name): 
    		with open(key_file_name, "rb") as key_file:
        		private_key = serialization.load_pem_private_key(
            			key_file.read(),
	   	 		password=None,
	    			backend=default_backend()
        		) 
    		return private_key;

	def load_public_key(self,key_file_name): # Cheat code, we used the private key to get the public key, but you can obviously get the public key another legit way. Just assume we already have the public key stored or that we exchanged it from the other party. 
    		with open(key_file_name, "rb") as key_file:
        		private_key = serialization.load_pem_private_key(
            			key_file.read(),
	   	 		password=None,
	    			backend=default_backend()
        		) 
    		return private_key.public_key(); 
    			
		
	def sign_message(self,message, key_file_name):
		private_key = self.load_private_key(key_file_name) 
		signature = private_key.sign(
			message,
			padding.PSS(
				mgf=padding.MGF1(hashes.SHA256()),
				salt_length=padding.PSS.MAX_LENGTH
			),
			hashes.SHA256()
		)
		return signature
		
	# Loads the public key used to verify, then returns 1 if valid signature.
	def verify_message(self,message, signature, key_file_name): 
    		public_key = self.load_public_key(key_file_name) 

    		pem = public_key.public_bytes(
           		encoding=serialization.Encoding.PEM,
           		format=serialization.PublicFormat.SubjectPublicKeyInfo
    		)
		val = 1
		try:
			public_key.verify(
				signature,
				message,
				padding.PSS(
					mgf=padding.MGF1(hashes.SHA256()),
        				salt_length=padding.PSS.MAX_LENGTH
				),
				hashes.SHA256()
			)
		except InvalidSignature:
			val = 0
			print("exception")

		return val

		
		
    		#return public_key
