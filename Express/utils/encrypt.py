import base64
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

def pad(s):
    '''
    fill in the string so it can divide by 16
    :param s: message to be encrypted
    :return: message to be encrypted(multiple of 16 in length)
    '''
    return s+((16-len(s)%16)*'{')
def encrypt(key,s):
    '''encrypt message then base64 encode it'''
    cipher = AES.new(key)
    return b2a_hex(cipher.encrypt(pad(s)))
def decrypt(key,s):
    '''decrypt message then cut its {'''
    cipher = AES.new(key)
    dec = cipher.decrypt(a2b_hex(s))
    l = dec.count('{')
    return dec[:len(dec)-l]