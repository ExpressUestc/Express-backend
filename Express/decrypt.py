from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64
from Crypto import Random
from Crypto.PublicKey import RSA


def decryptMessage(encryptmessage):
    with open('/home/projects/Expressbackend/Express/test/private.pem') as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        decryptmessage = cipher.decrypt(base64.b64decode(encryptmessage), Random.new().read)
    return decryptmessage
