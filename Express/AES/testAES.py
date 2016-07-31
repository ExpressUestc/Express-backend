# coding:utf8
import base64
from Crypto.Cipher import AES
# should be 16 bytes long
from Express.utils.encrypt import encrypt, decrypt

key = '12345678abcdefgh'
cipher = AES.new(key)
message = "你好!"

if __name__ == '__main__':
    print "Message:",message
    print "Encrypted:",encrypt(key,message)
    print "Decrypted:",decrypt(key,encrypt(key,message))