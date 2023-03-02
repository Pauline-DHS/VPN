from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# Générer une paire de clés RSA
key = RSA.generate(2048)

# Message à signer
message = b"Hello, world!"

# Hash du message
h = SHA256.new(message)

# Signer le hash avec la clé privée
signature = pkcs1_15.new(key).sign(h)
print(key.publickey())
# Vérifier la signature avec la clé publique
try:
    pkcs1_15.new(key.publickey()).verify(h, signature)
    print("La signature est valide.")
except (ValueError, TypeError):
    print("La signature est invalide.")
