# 04 - Session Management Testing

**Service:** Public API (:3000), Admin API (:3001), File API (:3002)
**Tester:** <!-- Điền tên -->
**Date:** 2026-04-XX

---

| TC ID | WSTG Ref | Tên Test Case | Các bước thực hiện | Kết quả mong đợi | Status | Note |
|-------|----------|--------------|-------------------|------------------|--------|------|
| TC-SESS-01 | WSTG-SESS-01 | Kiểm tra Session Management Schema | 1. Login, xem JWT token structure (header, payload, signature)<br>2. Check token storage: localStorage? sessionStorage? cookie?<br>3. Kiểm tra token có chứa sensitive data (password, email) không | - JWT chỉ chứa minimal claims (_id, name, isRoot, type, partner)<br>- Không chứa PII hoặc secrets<br>- Token stored securely (không plain text trong URL) | | |
| TC-SESS-02 | WSTG-SESS-02 | Kiểm tra Cookie Attributes | 1. Kiểm tra tất cả cookies set bởi server<br>2. Check attributes: `Secure`, `HttpOnly`, `SameSite`, `Domain`, `Path`<br>3. Kiểm tra cookie expiration | - Cookies có Secure, HttpOnly, SameSite=Strict/Lax<br>- Domain/Path restrictive<br>- Expiration hợp lý | | VCreator dùng JWT trong header, không phải cookie - nhưng check cả Firebase cookies |
| TC-SESS-03 | WSTG-SESS-03 | Kiểm tra Session Fixation | 1. Lấy JWT token trước khi login<br>2. Login → kiểm tra token có thay đổi không<br>3. Thử force token cũ vào session mới | - Token mới được issue sau mỗi lần login<br>- Token cũ invalid sau login mới | | |
| TC-SESS-04 | WSTG-SESS-04 | Kiểm tra Cross-Site Request Forgery (CSRF) | 1. Tạo HTML page với form auto-submit tới API endpoint<br>2. Kiểm tra state parameter trong OAuth flows<br>3. Xem có CSRF token trong requests không | - API yêu cầu JWT trong header (Bearer) → CSRF mitigation tự nhiên<br>- OAuth flows có state parameter<br>- Không dùng cookie-based auth cho API | | JWT trong Authorization header inherently chống CSRF |
| TC-SESS-05 | WSTG-SESS-05 | Kiểm tra Logout / Token Revocation | 1. Login lấy token<br>2. Gọi logout endpoint (nếu có)<br>3. Dùng token cũ gọi `/users/me` → vẫn valid?<br>4. Kiểm tra có token blacklist mechanism không | - Token bị invalidate sau logout<br>- Server có blacklist/revocation mechanism<br>- Token cũ bị reject | | |
| TC-SESS-06 | WSTG-SESS-06 | Kiểm tra Session Timeout | 1. Login lấy token, check `exp` claim<br>2. Đợi token gần hết hạn, gọi API<br>3. Đợi token hết hạn, gọi API<br>4. Kiểm tra token lifetime (quá dài?) | - Token có exp hợp lý (access: 15-60 min, refresh: 7-30 days)<br>- Expired token bị reject (401)<br>- Không có infinite lifetime tokens | | |
| TC-SESS-07 | WSTG-SESS-07 | Kiểm tra Session Overlap | 1. Login từ 2 devices/browsers đồng thời<br>2. Kiểm tra cả 2 sessions đều valid?<br>3. Logout từ device A, kiểm tra device B | - Policy rõ ràng: cho phép multi-session hoặc single-session<br>- Nếu single-session: login mới invalidate session cũ | | |
| TC-SESS-08 | WSTG-SESS-08 | Kiểm tra JWT Token Entropy | 1. Thu thập 5-10 JWT tokens liên tiếp<br>2. So sánh signature, kiểm tra randomness<br>3. Check có predictable pattern không | - Mỗi token unique<br>- Signature không predictable<br>- Không có sequential pattern | | |
| TC-SESS-09 | WSTG-SESS-09 | Kiểm tra Token trong URL / Referer | 1. Kiểm tra token có xuất hiện trong URL params không<br>2. Check Referer header có leak token không<br>3. Kiểm tra browser history/logs | - Token KHÔNG ở URL params<br>- Token KHÔNG bị leak qua Referer<br>- Token chỉ trong Authorization header | | |
