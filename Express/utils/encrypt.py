import base64
from Crypto.Cipher import AES

def encrypt(key,string):
    '''
    using AES encryption Algorithm
    :param key: 16 bytes
    :param string: message to be encrypted
    :return: base64 encoded ciphertext
    '''
    obj = AES.new(key,AES.MODE_CBC,key)
    ciphertext = base64.b64encode(obj.encrypt(string))
    return ciphertext