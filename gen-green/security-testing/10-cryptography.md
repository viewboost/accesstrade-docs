# 10 - Cryptography

**Service:** All services + Infrastructure
**Tester:** <!-- Điền tên -->
**Date:** 2026-04-XX

---

| TC ID | WSTG Ref | Tên Test Case | Các bước thực hiện | Kết quả mong đợi | Status | Note |
|-------|----------|--------------|-------------------|------------------|--------|------|
| TC-CRYP-01 | WSTG-CRYP-01 | Kiểm tra TLS Configuration | 1. `nmap --script ssl-enum-ciphers -p 443 <DEV_HOST>`<br>2. Kiểm tra TLS version: chỉ TLS 1.2+ ?<br>3. Check weak ciphers (RC4, DES, export ciphers)<br>4. Check certificate validity | - TLS 1.2+ only (no SSLv3, TLS 1.0, 1.1)<br>- Strong ciphers only<br>- Valid certificate | | Hoặc dùng testssl.sh / SSL Labs |
| TC-CRYP-02 | WSTG-CRYP-02 | Kiểm tra Padding Oracle | 1. Nếu có encrypted cookies/tokens: thử modify padding<br>2. Send modified ciphertext, observe error differences | - No padding oracle vulnerability<br>- Consistent error responses for any tampering | | Ít relevant nếu chỉ dùng JWT |
| TC-CRYP-03 | WSTG-CRYP-03 | Kiểm tra Sensitive Data in Transit | 1. Bật Burp proxy, thực hiện full user flow<br>2. Search responses cho: phone, email, CCCD, bank account<br>3. Kiểm tra PII có encrypted hay plaintext trong API response | - PII masked trong API response (email: t***@gmail.com)<br>- Bank account masked (last 4 digits only)<br>- CCCD number not in response (chỉ status) | | |
| TC-CRYP-04 | WSTG-CRYP-04 | Kiểm tra Weak Cryptographic Algorithms | 1. Check JWT algorithm (HS256 minimum, prefer RS256)<br>2. Check password hashing (bcrypt/scrypt/argon2?)<br>3. Check MongoDB connection encryption<br>4. Check MinIO connection (HTTPS?) | - JWT dùng HS256+ (không HS1, none)<br>- Passwords hashed with bcrypt/argon2<br>- MongoDB connection encrypted<br>- MinIO qua HTTPS | | |
| TC-CRYP-05 | WSTG-CRYP-05 | Kiểm tra Encryption of Stored Data (PII) | 1. Kiểm tra MongoDB: fields PII có encrypted at rest không?<br>  - `users` collection: email, phone<br>  - `user-bank-cards`: bank account number<br>  - `identifications`: CCCD number, images<br>2. Kiểm tra MinIO: private bucket có encryption? | - PII fields encrypted (AES-256) trong database<br>- Bank info encrypted at rest<br>- CCCD data encrypted + stored private bucket<br>- MinIO server-side encryption enabled | | CRITICAL cho compliance |
| TC-CRYP-06 | WSTG-CRYP-06 | Kiểm tra JWT Secret Strength | 1. Check secret length: `AUTH_SECRET_PUBLIC`, `AUTH_SECRET_ADMIN`<br>2. Brute force test: `jwt_tool $TOKEN -C -d wordlist.txt`<br>3. Check secret khác nhau giữa environments | - Secret >= 256 bits (32 bytes)<br>- Not in common wordlists<br>- Different per environment (dev/staging/prod) | | |
| TC-CRYP-07 | WSTG-CRYP-07 | Kiểm tra Firebase Credentials Security | 1. Check Firebase credentials storage (base64 in .env)<br>2. Kiểm tra Firebase rules: ai access được gì?<br>3. Check Google Drive service account scope | - Credentials không hardcode<br>- Firebase rules restrictive<br>- Service account minimal permissions | | FIREBASE_CREDENTIALS=base64 in .env |
| TC-CRYP-08 | WSTG-CRYP-08 | Kiểm tra MinIO Presigned URLs | 1. Generate presigned URL, check expiry time<br>2. Thử access URL sau khi expired<br>3. Thử modify URL params (bucket, key)<br>4. Kiểm tra private vs public bucket access | - Presigned URLs expire đúng (10 min)<br>- Expired URLs rejected<br>- Cannot access private bucket without presigned URL<br>- URL signature prevents tampering | | |
