from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

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
    
def encrypt_message_symmetric(message, session_key):
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode())
    return cipher_aes.nonce, tag, ciphertext

def decrypt_message_symmetric(nonce, tag, ciphertext, session_key):
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    plaintext = cipher_aes.decrypt(ciphertext)
    return plaintext.decode()


def sign_message(message, private_key):
    signer = pkcs1_15.new(private_key)
    h = SHA256.new()
    h.update(message.encode())
    return signer.sign(h)

def verify_message(message, signature, public_key):
    rsa_key_bin = RSA.import_key(public_key)
    public_key = rsa_key_bin.publickey()
    verifier = pkcs1_15.new(public_key)
    h = SHA256.new()
    h.update(message.encode())
    try:
        verifier.verify(h, signature)
        return True
    except:
        return False




    