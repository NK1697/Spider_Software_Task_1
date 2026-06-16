import argparse
import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import hmac

def encrypt(data, password, verify):
    salt = os.urandom(16)
    iv = os.urandom(16)

    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000, dklen=32)

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    enc_txt = encryptor.update(padded_data) + encryptor.finalize()

    if verify:
        tag = hmac.new(key, enc_txt, hashlib.sha256).digest()
        with open("encrypted.enc", "wb") as f:
            f.write(salt+iv+enc_txt+tag)
    else:
        with open("encrypted.enc", "wb") as f:
            f.write(enc_txt)

def decrypt(enc_txt, password, salt, iv, tag):
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000, dklen=32)
    new_tag = hmac.new(key, enc_txt, hashlib.sha256).digest()
    if tag != "-" and new_tag != tag:
        print("Tampering detected")
        return
    else:
        if tag != "-":
            print("Integrity Verified")
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(enc_txt) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        with open("decrypted.txt", "wb") as f:
            f.write(data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode")
    parser.add_argument("file")
    parser.add_argument("--password", required= True)
    parser.add_argument("--verify", action="store_true")

    args = parser.parse_args()

    if args.mode == "encrypt":
        with open(args.file, "rb") as f:
            data = f.read()
        encrypt(data, args.password, args.verify) 
    
    elif args.mode == "decrypt" and args.verify:
        with open(args.file, "rb") as f:
            data = f.read()
        salt = data[:16]
        iv = data[16:32]
        tag = data[-32:]
        enc_txt = data[32:-32]
        decrypt(enc_txt, args.password, salt, iv, tag)
    
    elif args.mode == "decrypt" and not args.verify:
        with open(args.file, "rb") as f:
            data = f.read()
            salt = data[:16]
            iv = data[16:32]
            enc_txt = data[32:]
        decrypt(enc_txt, args.password, salt, iv, "-")

    else:
        print("Invalid Mode Entered")

main()