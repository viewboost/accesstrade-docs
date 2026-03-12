# BÁO CÁO ĐÁNH GIÁ AN TOÀN THÔNG TIN

### Dự án: **Techcombank Influencer Platform (T-Fluencers)**

**Phiên bản báo cáo:** 2.0
**Thời gian đánh giá:** 04/03/2026 – 11/03/2026
**Môi trường kiểm thử:** UAT/DEV (`tfluencer-dev.scalef.com`, `tfluencer-admin-dev.scalef.com`)

---

## Lịch sử thay đổi

| Phiên bản | Ngày       | Người thay đổi | Mô tả                                    |
| --------- | ---------- | --------------- | ----------------------------------------- |
| 1.0       | —          | Security Team   | Đánh giá lần đầu — phát hiện 5 lỗ hổng   |
| 2.0       | 12/03/2026 | Security Team   | Retest v1.0 + đánh giá mới trên phạm vi mở rộng |

---

## Mục lục

- [1. Mục tiêu](#1-mục-tiêu)
- [2. Phạm vi](#2-phạm-vi)
- [3. Phương pháp kiểm thử](#3-phương-pháp-kiểm-thử)
- [4. Công cụ sử dụng](#4-công-cụ-sử-dụng)
- [5. Điều kiện vào/ra](#5-điều-kiện-vàora)
- [6. Thống kê tổng quan](#6-thống-kê-tổng-quan)
- [7. Kết quả Retest lỗ hổng v1.0](#7-kết-quả-retest-lỗ-hổng-v10)
- [8. Danh sách phát hiện mới v2.0](#8-danh-sách-phát-hiện-mới-v30)
- [9. Chi tiết theo danh mục OWASP](#9-chi-tiết-theo-danh-mục-owasp)
- [10. SLA Xử lý](#10-sla-xử-lý)
- [11. Rủi ro & Biện pháp](#11-rủi-ro--biện-pháp)
- [12. Nguồn lực](#12-nguồn-lực)
- [13. Kết luận & Khuyến nghị](#13-kết-luận--khuyến-nghị)
- [14. Chữ ký xác nhận](#14-chữ-ký-xác-nhận)

---

## 1. Mục tiêu

- **Retest** toàn bộ 5 lỗ hổng phát hiện ở phiên bản 1.0, xác nhận đã được khắc phục.
- **Đánh giá mới** trên phạm vi mở rộng: phát hiện lỗ hổng bảo mật trong hạ tầng, hệ thống, API và ứng dụng.
- Đánh giá mức độ rủi ro bảo mật và đề xuất biện pháp cải tiến.
- Đảm bảo tuân thủ các tiêu chuẩn bảo mật (OWASP Top 10).

---

## 2. Phạm vi

| Hạng mục       | Chi tiết                                                                 |
| --------------- | ------------------------------------------------------------------------ |
| Infrastructure  | Server, Network, Database (MongoDB)                                      |
| Systems         | Operating systems, middleware (Redis, MinIO, Asynq)                      |
| Applications    | Cổng Influencer (`tfluencer-dev`), Cổng quản trị (`tfluencer-admin-dev`) |
| APIs            | Public API (Creator), Admin API, File API                                |

---

## 3. Phương pháp kiểm thử

Dựa trên **OWASP Testing Guide v4.2 Checklist**, bao gồm 12 danh mục:

1. Information Gathering
2. Configuration and Deploy Management Testing
3. Identity Management Testing
4. Authentication Testing
5. Authorization Testing
6. Session Management Testing
7. Data Validation Testing
8. Error Handling
9. Cryptography
10. Business Logic Testing
11. Client Side Testing
12. API Testing

**Phương pháp:** Kết hợp quét tự động (automated scanning) và kiểm thử thủ công (manual penetration testing).

---

## 4. Công cụ sử dụng

| Công cụ              | Mục đích                                      |
| -------------------- | --------------------------------------------- |
| Burp Suite           | Proxy, scan lỗ hổng web, intercept request    |
| OWASP ZAP            | Quét tự động lỗ hổng web                      |
| Nmap                 | Quét port, fingerprint dịch vụ                |
| dirsearch / ffuf     | Khám phá thư mục, file ẩn                     |
| Dependabot / npm audit | Kiểm tra dependencies lỗi thời              |
| Browser DevTools     | Kiểm tra client-side, cookies, localStorage   |
| Postman / curl       | Kiểm thử API thủ công                         |

---

## 5. Điều kiện vào/ra

### Entry Criteria
- Tính năng chính ổn định; môi trường kiểm thử sẵn sàng và được phê duyệt
- Tài khoản kiểm thử, dữ liệu mẫu, và kênh liên lạc vận hành đã được cấp

### Exit Criteria
- Liệt kê được tất cả lỗ hổng tồn tại
- Các lỗ hổng được lên kế hoạch theo dõi và xử lý
- Tuân thủ các tiêu chuẩn bảo mật (OWASP Top 10)
- Không có truy cập trái phép hoặc lộ dữ liệu
- Session và dữ liệu nhạy cảm được bảo vệ tốt

---

## 6. Thống kê tổng quan

### 6.1. Tổng hợp kết quả

| Danh mục                                       | Tổng TC | Pass | N/A | Fail | Tỉ lệ lỗi |
| ---------------------------------------------- | ------- | ---- | --- | ---- | ---------- |
| Information Gathering                          | 10      | 6    | 4   | 0    | 0%         |
| Configuration and Deploy Management Testing    | 16      | 14   | 1   | **1**| **6.3%**   |
| Identity Management Testing                    | 14      | 11   | 3   | 0    | 0%         |
| Authentication Testing                         | 10      | 6    | 2   | **2**| **20%**    |
| Authorization Testing                          | 4       | 4    | 0   | 0    | 0%         |
| Session Management Testing                     | 9       | 5    | 4   | 0    | 0%         |
| Data Validation Testing                        | 19      | 17   | 2   | 0    | 0%         |
| Error Handling                                 | 8       | 8    | 0   | 0    | 0%         |
| Cryptography                                   | 8       | 7    | 0   | **1**| **12.5%**  |
| Business Logic Testing                         | 13      | 12   | 1   | 0    | 0%         |
| Client Side Testing                            | 20      | 18   | 2   | 0    | 0%         |
| API Testing                                    | 10      | 9    | 0   | **1**| **10%**    |
| **TỔNG**                                       | **141** | **117** | **19** | **5** | **3.5%** |

### 6.2. Phân bố theo mức độ nghiêm trọng

| Mức độ   | Số lượng | Tỉ lệ |
| -------- | -------- | ------ |
| Critical | 0        | 0%     |
| High     | 1        | 20%    |
| Medium   | 4        | 80%    |
| Low      | 0        | 0%     |
| **Tổng** | **5**    | 100%   |

---

## 7. Kết quả Retest lỗ hổng v1.0

Toàn bộ 5 lỗ hổng phát hiện ở v1.0 đã được khắc phục và xác nhận qua retest:

| #  | Lỗ hổng v1.0                                | Severity | OWASP Ref    | Biện pháp đã áp dụng                                                            | Status v2.0    | Evidence      |
| -- | -------------------------------------------- | -------- | ------------ | -------------------------------------------------------------------------------- | -------------- | ------------- |
| 1  | Outdated/Vulnerable Dependencies             | Medium   | WSTG-CONF-01 | Rà soát và cập nhật toàn bộ dependencies trong package.json                      | **✅ Closed**  | TC-CONF-02    |
| 2  | Remember-me Token Reuse Across Devices       | Medium   | WSTG-ATHN-05 | Ràng buộc token theo device fingerprint; set Secure, HttpOnly, SameSite; rotate khi logout | **✅ Closed**  | TC-ATHN-05    |
| 3  | Weak Password Policy                         | Medium   | WSTG-ATHN-07 | Bổ sung ràng buộc mật khẩu tối thiểu 10 ký tự, đa dạng ký tự; chặn mật khẩu phổ biến | **✅ Closed**  | TC-ATHN-07    |
| 4  | PII chưa mã hóa trong Database               | High     | WSTG-CRYP-03 | Mã hóa AES-256 cho toàn bộ field PII (phone, email, số tài khoản ngân hàng)     | **✅ Closed**  | TC-CRYP-05    |
| 5  | API Input Validation thiếu server-side        | Medium   | WSTG-APIT-02 | Bổ sung server-side validation, chặn và chuẩn hóa dữ liệu đầu vào              | **✅ Closed**  | TC-APIT-01    |

> **Kết luận retest:** Tất cả 5 lỗ hổng từ v1.0 đã được khắc phục thành công. Không phát hiện regression.

---

## 8. Danh sách phát hiện mới v2.0

**Không phát hiện lỗ hổng mới** trong đợt đánh giá v2.0.

Tất cả 141 test cases (trừ 5 retest items đã closed và 19 N/A) đều đạt kết quả Pass.

---

## 9. Chi tiết theo danh mục OWASP

### 9.1. Information Gathering (10 TCs — 6 Pass, 4 N/A)

| ID          | Test Case                            | Kết quả | Ghi chú                                   |
| ----------- | ------------------------------------ | ------- | ----------------------------------------- |
| TC-INFO-01  | Search Engine Recon                  | Pass    |                                           |
| TC-INFO-02  | Fingerprint Web Server               | Pass    |                                           |
| TC-INFO-03  | Webserver Metafiles (.git, .env)     | Pass    | Không lộ file nhạy cảm                    |
| TC-INFO-04  | Directory Discovery                  | Pass    | dirsearch/ffuf — không tìm thấy path ẩn  |
| TC-INFO-05  | JS/HTML Info Leakage                 | Pass    | Không lộ thông tin nhạy cảm trong source  |
| TC-INFO-06  | Input Vectors Identification         | Pass    |                                           |
| TC-INFO-07  | Map Execution Paths                  | N/A     | Có trong tài liệu đặc tả                 |
| TC-INFO-08  | Framework Fingerprinting             | N/A     | Có trong tài liệu bảo mật                |
| TC-INFO-09  | App Fingerprinting                   | N/A     | Có trong tài liệu bảo mật                |
| TC-INFO-10  | Map Architecture                     | N/A     | Có trong tài liệu bảo mật                |

### 9.2. Configuration and Deploy Management (16 TCs — 14 Pass, 1 N/A, 1 Fail→Closed)

| ID          | Test Case                          | Kết quả        | Ghi chú                                      |
| ----------- | ---------------------------------- | -------------- | --------------------------------------------- |
| TC-CONF-01  | Network/Firewall Config            | Pass           | Port 80/443 allow, dashboard IP whitelist     |
| TC-CONF-02  | Framework/Package Versions         | Fail → Closed  | **v1.0 finding — đã fix, retest pass**        |
| TC-CONF-03  | Config File Leakage                | Pass           |                                               |
| TC-CONF-04  | Default Files/Directories          | Pass           |                                               |
| TC-CONF-05  | Debug Code Leftover                | Pass           |                                               |
| TC-CONF-06  | Logging Configuration              | Pass           |                                               |
| TC-CONF-07  | Sensitive File Extensions          | Pass           |                                               |
| TC-CONF-08  | Backup Files                       | Pass           |                                               |
| TC-CONF-09  | Admin Interface Enumeration        | Pass           |                                               |
| TC-CONF-10  | HTTP Methods                       | Pass           |                                               |
| TC-CONF-11  | HTTP Method Bypass                 | Pass           |                                               |
| TC-CONF-12  | HSTS                               | Pass           | max-age=63072000; includeSubDomains; preload  |
| TC-CONF-13  | RIA Cross-Domain Policy            | N/A            | Không sử dụng                                 |
| TC-CONF-14  | File Permissions                   | Pass           |                                               |
| TC-CONF-15  | Subdomain Takeover                 | Pass           |                                               |
| TC-CONF-16  | Cloud Storage ACL                  | Pass           |                                               |

### 9.3. Identity Management (14 TCs — 11 Pass, 3 N/A)

| ID          | Test Case                                  | Kết quả | Ghi chú                          |
| ----------- | ------------------------------------------ | ------- | --------------------------------- |
| TC-IDNT-01  | Role Definitions                           | Pass    |                                   |
| TC-IDNT-02  | Role Permissions Verification              | Pass    |                                   |
| TC-IDNT-03  | JWT Role Tampering                         | Pass    |                                   |
| TC-IDNT-04  | OAuth Registration (Google/TikTok)         | Pass    |                                   |
| TC-IDNT-05  | Identity Validation on Registration        | Pass    |                                   |
| TC-IDNT-06  | Duplicate Identity Check                   | Pass    |                                   |
| TC-IDNT-07  | Account Creation Permission                | Pass    |                                   |
| TC-IDNT-08  | Admin Privilege Escalation via Account     | Pass    |                                   |
| TC-IDNT-09  | Account Creation Logging                   | Pass    |                                   |
| TC-IDNT-10  | Error on Non-Existent Account Login        | Pass    |                                   |
| TC-IDNT-11  | Password Reset with Invalid Email          | N/A     | Không có chức năng này            |
| TC-IDNT-12  | Timing Attack on Account Enumeration       | Pass    |                                   |
| TC-IDNT-13  | Username Policy                            | N/A     | Không sử dụng username            |
| TC-IDNT-14  | Guessable Usernames                        | N/A     | Không sử dụng username            |

### 9.4. Authentication Testing (10 TCs — 6 Pass, 2 N/A, 2 Fail→Closed)

| ID          | Test Case                          | Kết quả        | Ghi chú                                 |
| ----------- | ---------------------------------- | -------------- | ---------------------------------------- |
| TC-ATHN-01  | Credentials over Encrypted Channel | Pass           |                                          |
| TC-ATHN-02  | Default Credentials                | Pass           |                                          |
| TC-ATHN-03  | Account Lockout                    | Pass           | 7 lần thất bại → khóa 2 giờ             |
| TC-ATHN-04  | Auth Bypass (JWT)                  | Pass           |                                          |
| TC-ATHN-05  | Remember Me Token Reuse            | Fail → Closed  | **v1.0 finding — đã fix, retest pass**   |
| TC-ATHN-06  | Browser Cache Weakness             | Pass           |                                          |
| TC-ATHN-07  | Weak Password Policy               | Fail → Closed  | **v1.0 finding — đã fix, retest pass**   |
| TC-ATHN-08  | Security Questions                 | N/A            | Không sử dụng                            |
| TC-ATHN-09  | Password Reset                     | N/A            | Không có chức năng                       |
| TC-ATHN-10  | Alternative Auth Channel (OTP)     | Pass           |                                          |

### 9.5. Authorization Testing (4 TCs — 4 Pass)

| ID          | Test Case                                  | Kết quả | Ghi chú                                          |
| ----------- | ------------------------------------------ | ------- | ------------------------------------------------- |
| TC-ATHZ-01  | Directory Traversal / File Include         | Pass    |                                                   |
| TC-ATHZ-02  | Authorization Bypass (Horizontal+Vertical) | Pass    | Test IDOR trên submission/contract/payment        |
| TC-ATHZ-03  | Privilege Escalation via Injection/Tamper   | Pass    | JWT claim tampering, extra JSON fields            |
| TC-ATHZ-04  | IDOR on Submissions/Payments/Contracts     | Pass    |                                                   |

### 9.6. Session Management (9 TCs — 5 Pass, 4 N/A)

| ID          | Test Case                  | Kết quả | Ghi chú                                   |
| ----------- | -------------------------- | ------- | ----------------------------------------- |
| TC-SESS-01  | Token Randomness/Reuse     | Pass    |                                           |
| TC-SESS-02  | Cookie Attributes          | N/A     | App không sử dụng cookies (JWT-based)     |
| TC-SESS-03  | Session Fixation           | Pass    |                                           |
| TC-SESS-04  | Exposed Session Variables  | Pass    |                                           |
| TC-SESS-05  | CSRF                       | N/A     | App không sử dụng cookies (JWT-based)     |
| TC-SESS-06  | Logout Invalidation        | Pass    |                                           |
| TC-SESS-07  | Session Timeout            | Pass    | User token: 6 ngày, Admin: 8 giờ         |
| TC-SESS-08  | Session Puzzling           | N/A     | Không áp dụng cho kiến trúc JWT stateless |
| TC-SESS-09  | Session Hijacking          | N/A     | Đã cover qua TC-ATHN-05 (token reuse)    |

### 9.7. Data Validation Testing (19 TCs — 17 Pass, 2 N/A)

| ID          | Test Case                        | Kết quả | Ghi chú                               |
| ----------- | -------------------------------- | ------- | -------------------------------------- |
| TC-INPV-01  | Reflected XSS                    | Pass    |                                        |
| TC-INPV-02  | Stored XSS                       | Pass    |                                        |
| TC-INPV-03  | HTTP Verb Tampering              | Pass    |                                        |
| TC-INPV-04  | HTTP Parameter Pollution         | Pass    |                                        |
| TC-INPV-05  | SQL Injection                    | N/A     | Hệ thống sử dụng MongoDB (NoSQL)      |
| TC-INPV-06  | LDAP Injection                   | Pass    |                                        |
| TC-INPV-07  | XML Injection                    | N/A     | Không sử dụng XML                      |
| TC-INPV-08  | SSI Injection                    | Pass    |                                        |
| TC-INPV-09  | XPath Injection                  | Pass    |                                        |
| TC-INPV-10  | IMAP/SMTP Injection              | Pass    |                                        |
| TC-INPV-11  | Code Injection (SSTI/eval)       | Pass    |                                        |
| TC-INPV-12  | Command Injection (shell/ffmpeg) | Pass    | Test cụ thể cho FFmpeg file processing |
| TC-INPV-13  | Format String Injection          | Pass    |                                        |
| TC-INPV-14  | Incubated Vulnerability          | Pass    |                                        |
| TC-INPV-15  | HTTP Response Splitting/Smuggling| Pass    |                                        |
| TC-INPV-16  | HTTP Request Monitoring          | Pass    |                                        |
| TC-INPV-17  | Host Header Injection            | Pass    |                                        |
| TC-INPV-18  | SSTI                             | Pass    |                                        |
| TC-INPV-19  | SSRF (Video metadata / OCR)      | Pass    | Test SSRF qua video URL và OCR callback|

### 9.8. Error Handling (8 TCs — 8 Pass)

| ID          | Test Case                          | Kết quả | Ghi chú                                       |
| ----------- | ---------------------------------- | ------- | ---------------------------------------------- |
| TC-ERRH-01  | Error Code Analysis                | Pass    | Không lộ stack trace trong response            |
| TC-ERRH-02  | Stack Trace Leakage                | Pass    |                                                |
| TC-ERRH-03  | Error Message Info Disclosure      | Pass    | Error message không chứa thông tin nhạy cảm   |
| TC-ERRH-04  | Custom Error Pages                 | Pass    |                                                |
| TC-ERRH-05  | Application Error Handling         | Pass    |                                                |
| TC-ERRH-06  | 404 Page Handling                  | Pass    |                                                |
| TC-ERRH-07  | 500 Error Handling                 | Pass    |                                                |
| TC-ERRH-08  | Verbose Error in API               | Pass    |                                                |

### 9.9. Cryptography (8 TCs — 7 Pass, 1 Fail→Closed)

| ID          | Test Case                     | Kết quả        | Ghi chú                                         |
| ----------- | ----------------------------- | -------------- | ------------------------------------------------ |
| TC-CRYP-01  | TLS Configuration             | Pass           | TLS 1.2+ only (đã disable TLS 1.0/1.1)          |
| TC-CRYP-02  | Certificate Chain              | Pass           |                                                  |
| TC-CRYP-03  | Padding Oracle                 | Pass           |                                                  |
| TC-CRYP-04  | Unencrypted PII Transit        | Pass           | Toàn bộ PII mã hóa trong transit (TLS)          |
| TC-CRYP-05  | Data-at-rest Encryption        | Fail → Closed  | **v1.0 finding — đã fix, retest pass**           |
| TC-CRYP-06  | Weak Algorithms                | Pass           |                                                  |
| TC-CRYP-07  | OTP Implementation             | Pass           |                                                  |
| TC-CRYP-08  | TLS Downgrade/MITM             | Pass           |                                                  |

### 9.10. Business Logic Testing (13 TCs — 12 Pass, 1 N/A)

| ID          | Test Case                             | Kết quả | Ghi chú                                          |
| ----------- | ------------------------------------- | ------- | ------------------------------------------------- |
| TC-BUSL-01  | Data Validation in Business Flow      | Pass    |                                                   |
| TC-BUSL-02  | Forged Request Validation             | Pass    |                                                   |
| TC-BUSL-03  | Integrity Checks                      | Pass    |                                                   |
| TC-BUSL-04  | Process Timing Manipulation           | Pass    | Test tham gia campaign quá deadline               |
| TC-BUSL-05  | API Call Limit / Rate Limit           | Pass    |                                                   |
| TC-BUSL-06  | Workflow Bypass                       | Pass    | Test gọi payout không qua bước duyệt             |
| TC-BUSL-07  | Application Misuse Prevention         | Pass    |                                                   |
| TC-BUSL-08  | File Upload Validation                | Pass    | Test malicious files, wrong extensions            |
| TC-BUSL-09  | Quota Enforcement                     | Pass    | Test budget cap enforcement                       |
| TC-BUSL-10  | Payment Logic Integrity               | Pass    |                                                   |
| TC-BUSL-11  | Batch Upload Validation               | N/A     |                                                   |
| TC-BUSL-12  | Role-based Business Logic             | Pass    |                                                   |
| TC-BUSL-13  | Data Export Authorization             | Pass    |                                                   |

### 9.11. Client Side Testing (20 TCs — 18 Pass, 2 N/A)

| ID          | Test Case                          | Kết quả | Ghi chú                              |
| ----------- | ---------------------------------- | ------- | ------------------------------------- |
| TC-CLNT-01  | DOM-based XSS                      | Pass    |                                       |
| TC-CLNT-02  | JavaScript Execution               | Pass    |                                       |
| TC-CLNT-03  | HTML Injection                     | Pass    |                                       |
| TC-CLNT-04  | Client-side URL Redirect           | Pass    |                                       |
| TC-CLNT-05  | CSS Injection                      | Pass    |                                       |
| TC-CLNT-06  | Client-side Resource Manipulation  | Pass    |                                       |
| TC-CLNT-07  | CORS Misconfiguration              | Pass    |                                       |
| TC-CLNT-08  | Clickjacking                       | Pass    | X-Frame-Options / CSP frame-ancestors |
| TC-CLNT-09  | Cross-origin Messaging             | Pass    |                                       |
| TC-CLNT-10  | Client-side Storage Security       | Pass    |                                       |
| TC-CLNT-11  | Content Security Policy            | Pass    |                                       |
| TC-CLNT-12  | JavaScript Library Vulnerabilities | Pass    |                                       |
| TC-CLNT-13  | Open Redirect                      | Pass    |                                       |
| TC-CLNT-14  | Subresource Integrity              | Pass    |                                       |
| TC-CLNT-15  | WebSocket Security                 | N/A     | Không sử dụng WebSocket              |
| TC-CLNT-16  | Browser Feature Exploitation       | Pass    |                                       |
| TC-CLNT-17  | Reverse Tabnabbing                 | Pass    |                                       |
| TC-CLNT-18  | PostMessage Validation             | Pass    |                                       |
| TC-CLNT-19  | LocalStorage Role Manipulation     | N/A     | Không lưu role trên localStorage     |
| TC-CLNT-20  | Third-party Script Injection       | Pass    |                                       |

### 9.12. API Testing (10 TCs — 9 Pass, 1 Fail→Closed)

| ID          | Test Case                        | Kết quả        | Ghi chú                                  |
| ----------- | -------------------------------- | -------------- | ----------------------------------------- |
| TC-APIT-01  | API Input Validation             | Fail → Closed  | **v1.0 finding — đã fix, retest pass**    |
| TC-APIT-02  | API Authentication               | Pass           |                                           |
| TC-APIT-03  | API Key Exposure                 | Pass           |                                           |
| TC-APIT-04  | RBAC Enforcement on API          | Pass           |                                           |
| TC-APIT-05  | BOLA (Broken Object Level Auth)  | Pass           |                                           |
| TC-APIT-06  | Rate Limiting                    | Pass           | ≤100 req/min (public), ≤300 req/min (admin)|
| TC-APIT-07  | Mass Assignment                  | Pass           |                                           |
| TC-APIT-08  | Sensitive Data in API Response   | Pass           |                                           |
| TC-APIT-09  | Security Misconfiguration        | Pass           |                                           |
| TC-APIT-10  | API Error Handling               | Pass           |                                           |

---

## 10. SLA Xử lý

| Mức độ   | Thời hạn xử lý |
| -------- | --------------- |
| Critical | 24 giờ          |
| High     | 3 ngày          |
| Medium   | 10 ngày         |
| Low      | 30 ngày         |

---

## 11. Rủi ro & Biện pháp

| Rủi ro                                                                | Biện pháp                                            |
| --------------------------------------------------------------------- | ---------------------------------------------------- |
| Quét tự động có thể bỏ sót hoặc tạo false positive                   | Kết hợp quét tự động và kiểm thử thủ công            |
| Quét có thể làm tăng tải tài nguyên, ảnh hưởng hiệu năng             | Test trên môi trường UAT/DEV riêng biệt              |
| Mất thời gian làm quen công cụ/luồng hệ thống                        | Lập kế hoạch phối hợp rõ ràng với dev team           |

---

## 12. Nguồn lực

| Vai trò          | Trách nhiệm                                         |
| ---------------- | ---------------------------------------------------- |
| Security Tester  | Thực hiện kiểm thử, lập báo cáo                     |
| DevOps / IT      | Cung cấp quyền truy cập, hỗ trợ môi trường          |
| Developer        | Khắc phục lỗ hổng, hỗ trợ retest                    |
| Project Manager  | Điều phối, theo dõi tiến độ                          |

---

## 13. Kết luận & Khuyến nghị

### Kết luận

- **Retest v1.0:** Toàn bộ 5/5 lỗ hổng đã được khắc phục thành công (1 High, 4 Medium → Closed).
- **Đánh giá v2.0:** Không phát hiện lỗ hổng mới trên 141 test cases.
- Hệ thống đáp ứng tiêu chuẩn OWASP Top 10 tại thời điểm đánh giá.

### Khuyến nghị

1. **Duy trì giám sát dependencies** — Cấu hình Dependabot hoặc Snyk tự động quét định kỳ.
2. **Bổ sung MFA cho Admin** — Khuyến nghị triển khai TOTP (Google Authenticator) cho tài khoản quản trị.
3. **Rà soát định kỳ** — Đánh giá bảo mật mỗi quý hoặc khi có thay đổi lớn.
4. **Monitoring & alerting** — Thiết lập cảnh báo khi phát hiện pattern tấn công bất thường (brute force, injection attempts).

---

## 14. Chữ ký xác nhận

**Người lập báo cáo**

(Ký, ghi rõ họ tên)

Ngày … tháng … năm …

---

**Trưởng nhóm phát triển**

(Ký, ghi rõ họ tên)

Ngày … tháng … năm …

---

**Đại diện đơn vị phát triển**

(Ký, ghi rõ họ tên)

Ngày … tháng … năm …
