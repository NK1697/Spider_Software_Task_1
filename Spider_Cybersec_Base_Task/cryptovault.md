# CryptoVault Write-Up

## Stage 1: Caesar Lock

Each alphabetic character is shifted by a fixed number of positions. For example, with a shift of 3, `A` becomes `D`, `B` becomes `E`, and so on. Decryption simply shifts the letters back by the same amount.
In `cryptovault_stage1-2.py`, lowercase and uppercase letters are handled separately, while spaces, punctuation, and numbers are left unchanged. The program also includes a `crack` mode that tries possible shifts and uses simple word matching and frequency analysis to guess the plaintext.

### Example crack result

The given ciphertext:

```text
Wkh txlfn eurzq ira mxpsv ryhu wkh odcb grj. Fubswrjudskb lv wkh duw ri zulwlqj dqg vroyLqj frghv.
```
is most likely a Caesar shift of 3. The plaintext is:
```text
The quick brown fox jumps over the lazy dog. Cryptography is the art of writing and solving codes.
```
### Pros

- Very easy to understand and implement.
- Fast and simple.
- Decryption is straightforward because the same shift value can be reversed.

### Limitations

- It is trivially breakable because there are only 25 useful shifts.
- An attacker can brute-force every shift quickly.
- It does not hide language patterns. Common letters, word lengths, and repeated words remain visible.
- It only works cleanly on alphabetic text, not arbitrary files like images, PDFs, or executables.
- It provides no real modern security.

### Why frequency analysis works

Human languages have patterns. In English, letters such as `e`, `t`, `a`, `o`, and `i` appear more often than letters like `q`, `x`, and `z`. A Caesar cipher shifts letters but does not destroy these frequency patterns. If the most common ciphertext letter is `h`, an attacker might guess it represents `e`, then calculate the likely shift.
That is why classical substitution ciphers are weak: they conceal letters, but they do not properly conceal statistical structure.

## Stage 2: Hash Guard

Stage 2 adds a `--verify` flag. Before encryption, the program computes a SHA-256 hash of the original plaintext and stores it inside the encrypted output. During decryption, the program decrypts the text, hashes the result again, and compares the new hash with the stored hash.
If the hashes match, the program prints an integrity success message. If they do not match, it prints a tampering warning.

### What it protects against

Hashing protects integrity.
Encryption and hashing solve different problems:
- Encryption gives confidentiality. It hides the file contents.
- Hashing gives integrity. It detects whether the file contents changed.
You need both because a file can be encrypted but still modified. Without an integrity check, the program may decrypt corrupted or altered data without warning.

### Pros

- SHA-256 is a strong cryptographic hash function.
- Even a small change in the file produces a completely different hash.
- It helps detect accidental corruption.

### Limitations

- A plain SHA-256 hash is not the same as authentication.
- Because the hash is stored in the same output file, a malicious attacker who understands the format could modify the ciphertext and replace the stored hash.
- It does not prove who created the file.
- It does not stop tampering by itself; it only detects changes after decryption.
- With the Caesar cipher, the encryption is still weak even if the hash check works.

### Why encryption and hashing are both needed

Encryption without hashing means an attacker may not be able to read the message, but they might still alter it. Hashing without encryption means an attacker can verify whether the message changed, but they can still read the message.
Together, confidentiality and integrity give a stronger security model... the message is hidden, and changes can be detected.

## Stage 3: AES Upgrade

Stage 3 replaces the Caesar cipher with AES-256-CBC from Python's `cryptography` library. AES is a modern symmetric encryption algorithm, meaning the same secret key is used for encryption and decryption.
Instead of using the password directly as the AES key, the program uses PBKDF2-HMAC-SHA256:
```text
password + random salt + many iterations -> 256-bit AES key
```
The code uses:
- AES key size: 32 bytes, which is 256 bits.
- Mode: CBC.
- Padding: PKCS7.
- Salt size: 16 bytes.
- IV size: 16 bytes.
- PBKDF2 iterations: 600000.
- Optional HMAC-SHA256 integrity tag when `--verify` is used.

### What it protects against

AES protects confidentiality much better than Caesar. It can encrypt any file type because it operates on bytes, not just letters. That means it can handle text files, images, PDFs, ZIP files, and other binary data.
PBKDF2 protects against weak password handling. A normal password is not the right size or randomness for an AES key. PBKDF2 turns the password into a proper key and makes password guessing slower.
The random IV protects against repeated encryption patterns in CBC mode. The HMAC tag, when enabled, helps detect tampering.

### Pros

- AES is a real modern encryption algorithm.
- AES-256 uses a large key size.
- The program can encrypt arbitrary file types, not just text.
- A fresh salt means the same password can produce different keys for different encryptions.
- PBKDF2 makes brute-force password guessing slower than a plain hash.
- A fresh IV makes repeated messages encrypt differently.
- HMAC verification gives stronger integrity protection than a plain unkeyed hash.

### Limitations

- Security still depends heavily on the password. A weak password can still be guessed.
- CBC mode does not provide integrity by itself.
- The same derived key is used for both AES encryption and HMAC in the current code.

### What goes wrong if the IV is reused?

AES-CBC needs a unique, unpredictable IV for each encryption. If the same IV is reused with the same key, identical plaintext prefixes can produce identical ciphertext patterns. This leaks information about the structure of the encrypted files.
The IV does not need to be secret, but it must be fresh and random. That is why it is safe to store the IV in the `.enc` file header.

### What PBKDF2 adds that a plain hash does not

A plain hash like SHA-256 is fast. That is usually good, but it is bad for password storage or password-based encryption because attackers can try millions or billions of guesses quickly.
PBKDF2 adds:
- A random salt, so the same password does not always produce the same key.
- Many repeated hashing rounds, so each password guess costs more time.
- A configurable output length, so it can produce a key of the exact size AES needs.
So PBKDF2 does not make a weak password magically strong, but it makes password guessing much harder than using a plain hash directly.


## Stage 4: Hybrid RSA + AES Encryption

Stage 4 upgrades CryptoVault from password-based symmetric encryption to a hybrid cryptographic system that combines RSA public-key cryptography with AES-256-CBC.

Instead of encrypting the file directly with RSA, the program generates a random AES key and uses AES-256-CBC to encrypt the file contents. The AES key is then encrypted using the recipient's RSA public key and stored alongside the encrypted file.

The workflow is:

```text
Plaintext
    ↓
Random AES-256 Key Generated
    ↓
AES-256-CBC Encrypts File
    ↓
RSA Public Key Encrypts AES Key
    ↓
Encrypted AES Key + IV + Ciphertext Stored
```

To decrypt the file:

```text
Encrypted AES Key
    ↓
RSA Private Key Decrypts AES Key
    ↓
Recovered AES Key
    ↓
AES-256-CBC Decrypts Ciphertext
    ↓
Original Plaintext
```

The program includes a `keygen` command that generates a 2048-bit RSA key pair. The public key is used for encryption, while the private key is required for decryption.

### Cryptographic components used

The implementation uses:

- RSA key size: 2048 bits.
- RSA padding: OAEP.
- OAEP hash function: SHA-256.
- AES key size: 32 bytes (256 bits).
- AES mode: CBC.
- IV size: 16 bytes.
- Padding for AES block alignment.
- Random AES key generated using `os.urandom()`.

A custom file header stores:

```text
Magic identifier
Encrypted AES key length
RSA-encrypted AES key
AES IV
Salt
Ciphertext
```

This allows the decryption process to recover all information needed to decrypt the file except the RSA private key.

### What it protects against

The main advantage of Stage 4 is that encryption no longer depends on a user password.

In Stage 3, security depended on the strength of the chosen password. If the password was weak, an attacker could potentially perform a brute-force attack against it.

In Stage 4, a random AES key is generated automatically for every encryption. This key is then protected using RSA. An attacker cannot decrypt the file unless they possess the matching RSA private key.

The hybrid design also solves a major practical limitation of RSA. RSA is inefficient for encrypting large files directly, while AES is extremely fast. By encrypting only the AES key with RSA and the file contents with AES, the program gains the advantages of both algorithms.

### Pros

- Uses public-key cryptography, so encryption does not require sharing a secret password.
- RSA allows anyone with the public key to encrypt data.
- Only the holder of the private key can decrypt the file.
- Random AES keys prevent reuse of encryption keys between files.
- Works on arbitrary binary files such as images, PDFs, ZIP archives, and executables.

### Limitations

- RSA encryption alone does not provide authentication.
- Protection depends on keeping the RSA private key secure. If the private key is stolen, encrypted files can be decrypted.

### Why hybrid encryption is used

RSA and AES are designed for different purposes.

RSA is computationally expensive and is best suited for encrypting small amounts of data such as keys. Encrypting an entire large file with RSA would be inefficient and, for sufficiently large files, impossible because RSA can only encrypt data smaller than its modulus size.

AES is extremely fast and can efficiently encrypt files of any size.

Hybrid encryption combines the strengths of both:

- RSA securely exchanges or protects the AES key.
- AES efficiently encrypts the actual file contents.

This is the same general approach used by many real-world systems, including secure email systems, TLS/HTTPS connections, and encrypted file-sharing applications.

### Why OAEP is important

RSA encryption should never be used without a secure padding scheme.

The implementation uses OAEP (Optimal Asymmetric Encryption Padding) with SHA-256. OAEP introduces randomness into RSA encryption so that encrypting the same AES key twice produces different ciphertexts.

Without proper padding, RSA can become vulnerable to several mathematical attacks. OAEP helps ensure that RSA encryption remains secure even when attackers can observe many encrypted messages.

### Public Key vs Private Key

The RSA key pair consists of:

```text
Public Key  -> Used for encryption
Private Key -> Used for decryption
```

The public key can be distributed freely because it cannot be used to recover encrypted data.

The private key must remain secret. Anyone who obtains the private key can decrypt every file encrypted with the corresponding public key.

This separation of keys is one of the major advantages of public-key cryptography because it removes the need to share a secret password before encryption can occur.
