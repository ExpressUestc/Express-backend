# coding:utf8
import base64
import json
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

# message = {"code" :'6e484a244f',"rcvPhone":'18349342287'}
# message = json.dumps(message)
# message = '009'
message = '007'
# dictMessage = json.loads(message)
# print dictMessage
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
# text = json.loads(text)
# print text['name']