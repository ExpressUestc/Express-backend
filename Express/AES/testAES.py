# coding:utf8
import base64
from Crypto.Cipher import AES
# should be 16 bytes long
from Express.utils.encrypt import encrypt, decrypt

key = '12345678abcdefgh'
cipher = AES.new(key)
message = "你好2!"

if __name__ == '__main__':
    print "Message:",message
    print "Encrypted:",encrypt(message,cipher)
    print "Decrypted:",decrypt(encrypt(message,cipher),cipher)