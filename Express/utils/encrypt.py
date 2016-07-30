import base64
from Crypto.Cipher import AES

def pad(s):
    '''
    fill in the string so it can divide by 16
    :param s: message to be encrypted
    :return: message to be encrypted(multiple of 16 in length)
    '''
    return s+((16-len(s)%16)*'{')
def encrypt(s,cipher):
    '''encrypt message then base64 encode it'''
    return base64.b64encode(cipher.encrypt(pad(s)))
def decrypt(s,cipher):
    '''decrypt message then cut its {'''
    dec = cipher.decrypt(base64.b64decode(s))
    l = dec.count('{')
    return dec[:len(dec)-l]