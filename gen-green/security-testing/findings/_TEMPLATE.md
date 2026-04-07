# Finding: TC-XXXX-XX

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-XXXX-XX |
| **Severity** | Critical / High / Medium / Low / Info |
| **CVSS Score** | X.X |
| **Status** | Open / Fixed / Accepted Risk |
| **Environment** | DEV |
| **OWASP Category** | A0X:2021 - Category Name |
| **CWE** | CWE-XXX |

---

## Issue Title

<!-- Mô tả ngắn gọn bằng tiếng Việt -->

## Type

<!-- Authentication / Authorization / Injection / Business Logic / Configuration / ... -->

## Affected Component

- **Service:** Public API / Admin API / File API
- **Endpoint:** `METHOD /path`
- **File:** `backend/path/to/file.go:line`

## Steps to Reproduce

1. <!-- Bước 1 -->
2. <!-- Bước 2 -->
3. <!-- Bước 3 -->

**Command:**
```bash
# curl/httpie command đầy đủ để reproduce
http GET $TARGET_PUBLIC/endpoint \
  Authorization:"Bearer $TOKEN_USER"
```

## Actual Result

<!-- Kết quả thực tế - cái gì sai? -->

## Expected Result (Remediation)

<!-- Hệ thống nên xử lý thế nào? -->

## Impact

<!-- Hậu quả nếu bị khai thác -->

## Evidence

<!-- Screenshot: -->
![Description](../evidence/screenshots/TC-XXXX-XX-01.png)

<!-- Response dump: -->
```json
// Response body
```

## References

- https://owasp.org/Top10/A0X_2021-Category/
- https://cwe.mitre.org/data/definitions/XXX.html
