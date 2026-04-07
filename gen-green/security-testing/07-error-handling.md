# 07 - Error Handling

**Service:** Public API (:3000), Admin API (:3001), File API (:3002)
**Tester:** <!-- Điền tên -->
**Date:** 2026-04-XX

---

| TC ID | WSTG Ref | Tên Test Case | Các bước thực hiện | Kết quả mong đợi | Status | Note |
|-------|----------|--------------|-------------------|------------------|--------|------|
| TC-ERRH-01 | WSTG-ERRH-01 | Kiểm tra Error Codes | 1. Gửi request tới endpoint không tồn tại → 404 format?<br>2. Gửi sai method → 405?<br>3. Gửi body invalid → 400?<br>4. Không auth → 401? Thiếu quyền → 403? | - Status codes chuẩn và consistent<br>- Error response format thống nhất<br>- Không có unexpected 500 cho invalid input | | |
| TC-ERRH-02 | WSTG-ERRH-02 | Kiểm tra Stack Trace Leakage | 1. Gửi malformed JSON body<br>2. Gửi invalid ObjectID<br>3. Gọi endpoint gây panic (nếu tìm được)<br>4. Kiểm tra response có Go stack trace không | - Không có stack trace trong response<br>- Không có internal file paths<br>- Recovery middleware catch panics | | Code dùng `fmt.Println(err)` - check có leak ra response không |
| TC-ERRH-03 | WSTG-ERRH-03 | Kiểm tra Database Error Leakage | 1. Gửi invalid MongoDB query trigger<br>2. Gửi duplicate key (unique index violation)<br>3. Kiểm tra error message: có chứa collection name, field name, query? | - DB errors wrapped, không trả raw MongoDB error<br>- Collection/field names không exposed<br>- Generic "server error" message | | `cc.Response400(nil, err.Error())` - raw error exposure |
| TC-ERRH-04 | WSTG-ERRH-04 | Kiểm tra Third-party Error Leakage | 1. Trigger MinIO error (upload invalid)<br>2. Trigger Firebase error<br>3. Trigger TikTok API error<br>4. Trigger Redis error (if possible) | - Third-party error details không exposed cho client<br>- Internal service names/URLs không leak<br>- Generic error message thay thế | | |
| TC-ERRH-05 | WSTG-ERRH-05 | Kiểm tra Error Handling Consistency | 1. So sánh error format giữa 3 services (public, admin, file)<br>2. Kiểm tra error response structure: có field nào consistent?<br>3. Xem có endpoint nào trả HTML error thay vì JSON | - Error format consistent (JSON structure)<br>- Không trả HTML error pages<br>- Status codes consistent across services | | |
| TC-ERRH-06 | WSTG-ERRH-06 | Kiểm tra Verbose Error Messages | 1. `http GET $TARGET_PUBLIC/events/invalid-id Authorization:"Bearer $TOKEN_USER"`<br>2. Gửi request thiếu required fields<br>3. Gửi invalid file type upload | - Error messages không chứa: file paths, function names, line numbers<br>- Messages generic nhưng useful cho client<br>- Không tiết lộ business logic internal | | |
| TC-ERRH-07 | WSTG-ERRH-07 | Kiểm tra Rate Limit Error Handling | 1. Gửi 100 requests/s tới cùng endpoint<br>2. Kiểm tra có 429 Too Many Requests không<br>3. Kiểm tra response có `Retry-After` header | - Rate limiting trả 429<br>- Retry-After header present<br>- Không crash/slow down server | | |
| TC-ERRH-08 | WSTG-ERRH-08 | Kiểm tra Large Payload Error | 1. Gửi JSON body 10MB<br>2. Upload file 500MB<br>3. Gửi request với 1000 headers | - Server reject gracefully (413, 400)<br>- Không OOM hoặc crash<br>- Error response nhanh, không timeout | | |
