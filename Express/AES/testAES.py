import base64
from Crypto.Cipher import AES
# should be 16 bytes long
obj = AES.new('helloworld123456',AES.MODE_CBC,'helloworld123456')
message = "The answer is no"
ciphertext = base64.b64encode(obj.encrypt(message))
print ciphertext