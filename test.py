import hashlib

# La chaîne à hacher
message = "Hello, World!"
message2 = "Hello, World!"

# Hachage en SHA-256
hash_object = hashlib.sha256(message.encode())
hash = hashlib.sha256(message2.encode())
# Convertir le hash en hexadécimal
hex_dig = hash_object.hexdigest()
hex_dig2 = hash.hexdigest()
print(hex_dig)
print(hex_dig2)
