import argparse
import os
import struct
import sys
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def keygen(public_path, private_path):
    private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())
    public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

    with open(private_path, "wb") as f:
        f.write(private_pem)
    with open(public_path, "wb") as f:
        f.write(public_pem)

def encrypt_aes_cbc(data, aes_key, iv):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(padded_data) + encryptor.finalize()


def decrypt_aes_cbc(ciphertext, aes_key, iv):
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()


def encrypt_file(input_path, public_key_path, output_path):
    with open(input_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    aes_key = os.urandom(32)
    iv = os.urandom(16)
    salt = os.urandom(16)

    with open(input_path, "rb") as f:
        plaintext = f.read()

    ciphertext = encrypt_aes_cbc(plaintext, aes_key, iv)
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    header = (b"CV4RSA1\n" + struct.pack(">H", len(encrypted_aes_key)) + encrypted_aes_key + iv + salt)

    with open(output_path, "wb") as f:
        f.write(header + ciphertext)

    print(f"Encrypted {input_path} -> {output_path}")


def parse_encrypted_file(data):
    if not data.startswith(b"CV4RSA1\n"):
        raise ValueError("This does not look like a CryptoVault4 RSA-encrypted file.")

    offset = len(b"CV4RSA1\n")
    if len(data) < offset + 2:
        raise ValueError("Encrypted file header is incomplete.")

    encrypted_key_len = struct.unpack(">H", data[offset : offset + 2])[0]
    offset += 2

    header_end = offset + encrypted_key_len + 16 + 16
    if len(data) < header_end:
        raise ValueError("Encrypted file header is incomplete.")

    encrypted_aes_key = data[offset : offset + encrypted_key_len]
    offset += encrypted_key_len
    iv = data[offset : offset + 16]
    offset += 16
    salt = data[offset : offset + 16]
    offset += 16
    ciphertext = data[offset:]

    return encrypted_aes_key, iv, salt, ciphertext


def decrypt_file(input_path, private_key_path, output_path):
    with open(input_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    with open(input_path, "rb") as f:
        encrypted_file = f.read()

    encrypted_aes_key, iv, salt, ciphertext = parse_encrypted_file(encrypted_file)
    _ = salt

    try:
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
            ),
        )
    except Exception:
        print(
            "Error: RSA private key could not decrypt the AES key. "
            "This is probably the wrong private key."
        )
        sys.exit(1)

    try:
        plaintext = decrypt_aes_cbc(ciphertext, aes_key, iv)
    except Exception:
        print("Error: AES decryption failed. The file may be corrupted or modified.")
        sys.exit(1)

    with open(output_path, "wb") as f:
        f.write(plaintext)

def main():
    parser = argparse.ArgumentParser(
        description="CryptoVault4: hybrid RSA + AES-256-CBC file encryption"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    keygen_parser = subparsers.add_parser("keygen", help="Generate an RSA keypair")
    keygen_parser.add_argument("--public", default="public.pem")
    keygen_parser.add_argument("--private", default="private.pem")

    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    encrypt_parser.add_argument("file")
    encrypt_parser.add_argument("--public-key", default="public.pem")
    encrypt_parser.add_argument("-o", "--output", default="encrypted.enc")

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a file")
    decrypt_parser.add_argument("file")
    decrypt_parser.add_argument("--private-key", default="private.pem")
    decrypt_parser.add_argument("-o", "--output", default="decrypted.txt")

    args = parser.parse_args()

    if args.command == "keygen":
        keygen(args.public, args.private)
    elif args.command == "encrypt":
        encrypt_file(args.file, args.public_key, args.output)
    elif args.command == "decrypt":
        decrypt_file(args.file, args.private_key, args.output)

main()
