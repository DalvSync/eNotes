# eNotes
**eNotes** is a secure note app that encrypts each note with its own password using AES‑GCM.
---

## 🚀 Features

- **Per‑Note Passwords**  
  Assign a unique password to every note for granular access control.

- **AES‑GCM Encryption**  
  Encrypts each note with AES‑256 in Galois/Counter Mode (GCM), using PBKDF2‑HMAC‑SHA256 to derive a per‑note key from your password.

- **Cross‑Platform GUI**  
  Built with PyQt5 for a clean, responsive desktop experience on Windows, macOS, and Linux.

- **Zero‑Knowledge Storage**  
  Notes are stored fully encrypted—your passwords and keys never leave your device in plaintext.

- **Easy Backup & Restore**  
  Export your encrypted notes bundle and import it on another device seamlessly.
  

  ## 🔐 Encryption Details

eNotes uses a **purely symmetric** encryption scheme based on AES‑GCM with password‑derived keys. Here’s exactly what happens under the hood:

1. **Per‑Note Passwords & Salt**  
   - When you create or save a note, you choose a password.  
   - The library generates a **16‑byte random salt** (`os.urandom(16)`) for that note.

2. **Key Derivation (PBKDF2‑HMAC‑SHA256)**  
   - A 256‑bit AES key is derived from your password and the salt using **PBKDF2‑HMAC‑SHA256** with **100 000 iterations**.  
   - This slow derivation protects against brute‑force attacks on your password.

3. **AES‑GCM Encryption**  
   - A **12‑byte random nonce** (`os.urandom(12)`) is generated per encryption.  
   - The plaintext note is encrypted with AES‑256 in **Galois/Counter Mode (GCM)**, providing both confidentiality and authentication (integrity).

4. **Blob Format**  
   - The final encrypted file (`<note>.enc`) contains:  
     ```
     [ 16 bytes salt ] ‖ [ 12 bytes nonce ] ‖ [ ciphertext + 16 byte GCM tag ]
     ```
   - On decryption, the salt and nonce are sliced off to re‑derive the key and verify/authenticate the ciphertext.

5. **Decryption Flow**  
   - When you open a note, you enter its password.  
   - The app reads the first 16 bytes to recover the salt, re‑derives the AES key, then reads the next 12 bytes as the nonce, and finally decrypts & verifies the remaining payload (ciphertext + tag).  
   - If the password is wrong or the data has been tampered with, decryption fails with an exception.

This approach ensures that:
- **Each note** has its own unique salt and nonce.
- **Passwords** never leave your machine and are never stored in plaintext.
- **AES‑GCM** protects both confidentiality and integrity of your notes.


To run it, it is advisable to place storage.py, crypto.py, main.pyw and icon.ico in one folder, and run main.pyw.

requirements: pip install PyQt5 cryptography
