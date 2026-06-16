import argparse
import hashlib

def encrypt(text, shift, verify):
    enc_txt = ""
    for c in text:
        if c.isalpha() and c.islower():
            new = chr((ord(c) - ord('a') + shift)%26 + ord('a'))
            enc_txt += new
        elif c.isalpha() and c.isupper():
            new = chr((ord(c) - ord('A') + shift)%26 + ord('A'))
            enc_txt += new
        else:
            enc_txt += c
    print(enc_txt)
    if verify:
        texthashing = hashlib.sha256(text.encode()).hexdigest()
        with open("encrypted.enc", "w+") as f:
            f.write(f"HASH: \n{texthashing}\nTEXT:\n{enc_txt}")
    else:
        with open("encrypted.enc", "w+") as f:
            f.write(enc_txt)

def decrypt(text, shift, verify, texthashing):
    actual_txt = ""
    for c in text:
        if c.isalpha() and c.islower():
            new = chr((ord(c) - ord('a') - shift)%26 + ord('a'))
            actual_txt += new
        elif c.isalpha() and c.isupper():
            new = chr((ord(c) - ord('A') - shift)%26 + ord('A'))
            actual_txt += new
        else:
            actual_txt += c
    print(actual_txt)

    if verify:
        actualhash = hashlib.sha256(actual_txt.encode()).hexdigest()
        if actualhash == texthashing:
            print("Integrity verified")
            with open("decrypted.txt", "w+") as f:
                f.write(actual_txt)
        else:
            print("Tampering detected")
    else:
        with open("decrypted.txt", "w+") as f:
            f.write(actual_txt)

def brute_ciphertext(text):
    common_words = {"the", "and", "is", "in", "to", "of", "that", "it", "for", "you"}
    crypts = []

    for shift in range(25):
        encrypted = ""
        score = 0
        for c in text.lower():  
            if c.isalpha():
                new = chr((ord(c) - ord('a') - shift)%26 + ord('a'))
                encrypted += new
            else:
                encrypted += c
        
        for word in encrypted.split():
            if word in common_words:
                score += 1
        crypts.append((score, shift, encrypted))
    top3 = sorted(crypts, reverse=True)[:3]

    for score, shift, text in top3:
        print(f"\nSHIFT: {shift}\nTEXT: {text}")

def freqanalysis(text):
    from collections import Counter
    letters = [c.lower() for c in text if c.isalpha()]
    counts = Counter(letters)
    top3 = counts.most_common(3)

    results = []
    for letter, count in top3:
        shift = (ord(letter) - ord('e')) % 26
        decrypted = ""
        for c in text:
            if c.islower():
                decrypted += chr((ord(c) - ord('a') - shift) % 26 + ord('a'))
            elif c.isupper():
                decrypted += chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            else:
                decrypted += c

        results.append((count, letter, shift, decrypted))
    for count, letter, shift, decrypted in results:
        print(f"\nMost frequent letter guess: {letter}")
        print(f"Shift guessed: {shift}")
        print(f"Frequency: {count}")
        print(f"Decrypted text:\n{decrypted}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode")
    parser.add_argument("file")
    parser.add_argument("--shift", type=int)
    parser.add_argument("--verify", action="store_true")

    args = parser.parse_args()

    if args.mode in ["encrypt", "decrypt"] and args.shift is None:
        print("Shift is required for encrypt/decrypt")
        return

    if args.mode == "encrypt":
        with open(args.file, "r") as f:
            text = f.read()
        encrypt(text, args.shift, args.verify)
    elif args.mode == "decrypt" and args.verify:
        with open(args.file, "r") as f:
            lines = [line.strip('\n') for line in f.readlines()]
            texthashing = lines[1].strip()
            text = "".join(lines[3:])
        decrypt(text, args.shift, args.verify, texthashing)
    elif args.mode == "decrypt" and not args.verify:
        with open(args.file, "r") as f:
            text = f.read()
        decrypt(text, args.shift, args.verify, "-")
    elif args.mode == "crack":
        with open(args.file, "r") as f:
            text = f.read()
        brute_ciphertext(text)
        freqanalysis(text)
    else:
        print("Invalid mode. Use encrypt/decrypt/crack.")

main()

