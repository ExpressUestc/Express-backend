from Crypto import Random
from Crypto.PublicKey import RSA
rng = Random.new().read
rsa = RSA.generate(1024,rng)

private_pem = rsa.exportKey()
with open('private.pem', 'w') as f:
    f.write(private_pem)

public_pem = rsa.publickey().exportKey()
with open('public.pem', 'w') as f:
    f.write(public_pem)