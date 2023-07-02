from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

def generate_rsa_key(name, secert):
    key = RSA.generate(2048)
    encrypted_key = key.export_key(passphrase=secert, pkcs=8, protection="scryptAndAES128-CBC")
    with open(name + "_rsa_key.bin", "wb") as f:
        f.write(encrypted_key)
    
    return key

def get_rsa_key(name, secert):
    try:
        with open(name + "_rsa_key.bin", "rb") as f:
            key = RSA.import_key(f.read(), passphrase=secert)
        return key
    except:
        return generate_rsa_key(name, secert)

def encrypt_message(message, recipient_public_key, session_key):
    cipher_rsa = PKCS1_OAEP.new(recipient_public_key)
    enc_session_key = cipher_rsa.encrypt(session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode())
    return enc_session_key, cipher_aes.nonce, tag, ciphertext

def decrypt_message(enc_session_key, nonce, tag, ciphertext, private_key):
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    plaintext = cipher_aes.decrypt(ciphertext)
    return plaintext.decode()




    