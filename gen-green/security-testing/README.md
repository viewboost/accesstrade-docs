# VCreator Security Testing - Hướng Dẫn Thực Hiện

## Quick Start

### 1. Install Tools

```bash
# Core
brew install --cask owasp-zap    # hoặc download Burp Suite
brew install httpie jq nmap nuclei ffuf

# JWT
git clone https://github.com/ticarpi/jwt_tool.git ~/tools/jwt_tool
alias jwt_tool='python3 ~/tools/jwt_tool/jwt_tool.py'

# Go/Node scanning
go install golang.org/x/vuln/cmd/govulncheck@latest
```

### 2. Setup Environment

```bash
# Target URLs - THAY BẰNG DEV HOST THẬT
export TARGET_PUBLIC="http://<DEV_HOST>:3000"
export TARGET_ADMIN="http://<DEV_HOST>:3001"
export TARGET_FILE="http://<DEV_HOST>:3002"

# JWT Tokens - lấy từ test accounts
export TOKEN_USER="<jwt-token>"
export TOKEN_ADMIN="<jwt-token>"
export TOKEN_COLLABORATOR="<jwt-token>"
export TOKEN_ROOT="<jwt-token>"

# Verify
http GET $TARGET_PUBLIC/app-data
```

### 3. Test Workflow

```
Bước 1: Mở file 01-information-gathering.md
Bước 2: Làm từng test case, điền Status: Passed / Issues Found / N/A
Bước 3: Mỗi "Issues Found" → copy _TEMPLATE.md → findings/TC-XXXX-XX.md
Bước 4: Chụp screenshot → evidence/screenshots/
Bước 5: Tiếp tục file 02, 03... cho tới 13
Bước 6: Chạy automated scans → scans/
Bước 7: Tổng hợp vào 00-pentest-report.md
```

---

## Cấu Trúc Thư Mục

```
security-testing/
├── README.md                    ← BẠN ĐANG ĐỌC FILE NÀY
├── 00-pentest-report.md         ← Báo cáo tổng hợp (điền cuối cùng)
├── 01-information-gathering.md  ← 13 category test sheets
├── 02-authentication-testing.md    (điền Status khi test)
├── 03-authorization-testing.md
├── 04-session-management.md
├── 05-identity-management.md
├── 06-data-validation.md
├── 07-error-handling.md
├── 08-client-side-testing.md
├── 09-business-logic.md         ← CRITICAL: financial logic
├── 10-cryptography.md
├── 11-api-testing.md
├── 12-file-upload-testing.md    ← CRITICAL: file service riêng
├── 13-configuration.md
├── findings/                    ← Chi tiết từng finding
│   ├── _TEMPLATE.md                (copy template → TC-XXX.md)
│   └── TC-ATHN-04.md              (ví dụ)
├── evidence/
│   ├── screenshots/             ← Screenshots
│   └── responses/               ← Response dumps (.json, .txt)
└── scans/                       ← Automated scan output
    ├── nmap-results.txt
    ├── nuclei-results.txt
    ├── govulncheck-results.txt
    └── npm-audit-*.json
```

---

## Severity Rating Guide

| Severity | Khi nào dùng | Ví dụ VCreator |
|----------|-------------|----------------|
| **Critical** | RCE, Auth bypass toàn hệ thống, dump full DB | JWT bypass cho phép access mọi endpoint |
| **High** | PII leak, privilege escalation, financial logic bug | IDOR lộ bank info, double withdraw |
| **Medium** | XSS stored, info disclosure, CORS misconfiguration | Stored XSS trong content, error leak DB info |
| **Low** | Missing headers, verbose errors, outdated libs | Thiếu CSP header, React 16 outdated |
| **Info** | Best practice recommendations | Suggest HSTS, suggest rate limiting |

---

## Thứ Tự Ưu Tiên Test

1. **02-authentication** → Nền tảng, nếu auth broken thì mọi thứ vô nghĩa
2. **03-authorization** → IDOR và privilege escalation
3. **09-business-logic** → Financial: withdraw, cashflow, reward
4. **12-file-upload** → ZIP Slip, upload bypass
5. **06-data-validation** → NoSQL injection, XSS
6. **01-information** → Recon (có thể làm trước hoặc song song)
7. Còn lại theo thứ tự

---

## Automated Scans (chạy song song với manual testing)

```bash
# Port scan
nmap -sV -sC -p- <DEV_HOST> -oN scans/nmap-results.txt

# Nuclei vulnerability scan
nuclei -u $TARGET_PUBLIC -o scans/nuclei-public.txt
nuclei -u $TARGET_ADMIN -H "Authorization: Bearer $TOKEN_ADMIN" -o scans/nuclei-admin.txt

# Go dependency scan
cd ../../backend && govulncheck ./... > ../../.bmad/security-testing/scans/govulncheck-results.txt 2>&1

# Frontend dependency scan
cd ../../frontend && npm audit --json > ../../.bmad/security-testing/scans/npm-audit-frontend.json 2>&1
cd ../../admin && npm audit --json > ../../.bmad/security-testing/scans/npm-audit-admin.json 2>&1
```

---

## Tips

- **Mỗi finding ghi ngay**, đừng đợi cuối ngày
- **Screenshot = evidence**, không có screenshot = không có proof
- **curl/httpie command** trong mỗi finding để ai cũng reproduce được
- **Critical findings báo ngay**, đừng đợi report xong
- **Backup dev DB trước khi test** business logic (withdraw, cashflow)
