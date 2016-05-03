# coding:utf8
import base64
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

message = '任远航 18161251970 cbawqfqwd1'
# message = 'hello ghost, this is a plian text'
with open('public.pem') as f:
    key = f.read()
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(message))
    print cipher_text

with open('private.pem') as f:
    key = f.read()
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    text = cipher.decrypt(base64.b64decode(cipher_text), Random.new().read)
    print text
