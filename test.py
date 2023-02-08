from Crypto.Cipher import AES

def encrypt_AES(key,message):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return (cipher.nonce, tag, ciphertext)

def decrypt_AES(key, nonce, tag, ciphertext):
    print("nonce:",nonce)
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext

key = b'coucou je test f'
plaintext = b'Attack at dawn'

nonce, tag, ciphertext = encrypt_AES(key, plaintext)
decrypted_plaintext = decrypt_AES(key, nonce, tag, ciphertext)

print(ciphertext)

print(decrypted_plaintext)

nonce, tag, ciphertext = encrypt_AES(key, plaintext)
decrypted_plaintext = decrypt_AES(key, nonce, tag, ciphertext)
print(ciphertext)

print(decrypted_plaintext)
nonce, tag, ciphertext = encrypt_AES(key, plaintext)
decrypted_plaintext = decrypt_AES(key, nonce, tag, ciphertext)
print(ciphertext)

print(decrypted_plaintext)