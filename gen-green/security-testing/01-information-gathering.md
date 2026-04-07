# 01 - Information Gathering

**Service:** Public API (:3000), Admin API (:3001), File API (:3002)
**Tester:** <!-- Điền tên -->
**Date:** 2026-04-XX

---

| TC ID | WSTG Ref | Tên Test Case | Các bước thực hiện | Kết quả mong đợi | Status | Note |
|-------|----------|--------------|-------------------|------------------|--------|------|
| TC-INFO-01 | WSTG-INFO-01 | Tìm kiếm thông tin rò rỉ qua search engine | 1. Google dork: `site:*.diso.vn inurl:vcreator`<br>2. Tìm trên GitHub: `"viewboost" OR "vcreator" password OR secret OR key`<br>3. Kiểm tra Shodan/Censys cho IP dev host | - Không có thông tin nhạy cảm (credentials, internal paths) trên search engine<br>- Source code không public chứa secrets | | |
| TC-INFO-02 | WSTG-INFO-02 | Fingerprint web server | 1. `http -v GET $TARGET_PUBLIC/app-data` → xem response headers<br>2. Kiểm tra header `Server`, `X-Powered-By`<br>3. Lặp lại cho :3001 và :3002 | - Server không tiết lộ version cụ thể (Go, Echo)<br>- Không có header `X-Powered-By`<br>- Không có debug/version endpoint | | |
| TC-INFO-03 | WSTG-INFO-03 | Xác định web application framework | 1. Dùng Wappalyzer trên frontend URLs<br>2. Kiểm tra response headers, cookies pattern<br>3. Xem page source cho framework fingerprint (React, Umi, Ant Design) | - Framework fingerprint không tiết lộ version chính xác<br>- Không có default error pages tiết lộ framework | | |
| TC-INFO-04 | WSTG-INFO-04 | Liệt kê ứng dụng trên web server | 1. `nmap -sV -p 3000,3001,3002 <DEV_HOST>`<br>2. Kiểm tra virtual hosts, subdomains<br>3. Xem có service nào unexpected trên cùng host | - Chỉ 3 services expected chạy trên host<br>- Không có service phụ exposed (debug, monitoring) | | |
| TC-INFO-05 | WSTG-INFO-05 | Xác định nội dung và chức năng ẩn | 1. `ffuf -u $TARGET_PUBLIC/FUZZ -w common.txt`<br>2. `ffuf -u $TARGET_ADMIN/FUZZ -w common.txt -H "Authorization: Bearer $TOKEN_ADMIN"`<br>3. Kiểm tra: `/swagger`, `/docs`, `/debug`, `/pprof`, `/metrics`, `/health` | - Không có endpoint ẩn (swagger, debug, pprof, metrics) exposed<br>- Admin endpoints chỉ accessible với auth | | |
| TC-INFO-06 | WSTG-INFO-06 | Xác định điểm truy cập ứng dụng (entry points) | 1. Extract endpoints từ Swagger JSON (public, admin, file)<br>2. Map tất cả HTTP methods cho mỗi endpoint<br>3. Xác định params: path params (`:id`), query params, body params<br>4. Liệt kê headers custom (X-Api-Key, Device-ID, FCM-Token...) | - Đã map đầy đủ endpoints cho 3 services<br>- Xác định được tất cả entry points cần test | | |
| TC-INFO-07 | WSTG-INFO-07 | Map execution paths qua ứng dụng | 1. Trace flow: Login → Browse events → Join event → Submit content → Withdraw<br>2. Trace admin flow: Login → Manage events → Review content → Approve → Reconcile<br>3. Trace file flow: Upload → Process → Store (MinIO) → Serve | - Hiểu rõ business flow để test logic<br>- Xác định critical paths (financial, PII) | | |
| TC-INFO-08 | WSTG-INFO-08 | Fingerprint web application framework (API level) | 1. Gửi invalid request xem error format (Echo default?)<br>2. `http GET $TARGET_PUBLIC/nonexistent-endpoint`<br>3. Xem error response structure, status codes | - Error responses không tiết lộ framework version<br>- 404 response không có stack trace | | |
| TC-INFO-09 | WSTG-INFO-09 | Kiểm tra database exposure | 1. `nmap -p 27017,27018 <DEV_HOST>` (MongoDB)<br>2. `nmap -p 6379 <DEV_HOST>` (Redis)<br>3. `nmap -p 9000 <DEV_HOST>` (MinIO)<br>4. Thử connect: `mongosh mongodb://<DEV_HOST>:27018` | - MongoDB/Redis/MinIO KHÔNG accessible từ external network<br>- Chỉ accessible từ internal network hoặc qua VPN | | |
| TC-INFO-10 | WSTG-INFO-10 | Kiểm tra Swagger/API docs exposure | 1. `http GET $TARGET_PUBLIC/swagger/index.html`<br>2. `http GET $TARGET_PUBLIC/swagger/doc.json`<br>3. `http GET $TARGET_ADMIN/swagger/index.html`<br>4. Lặp lại cho File service :3002 | - Swagger UI/JSON KHÔNG accessible trên production/staging<br>- Nếu enabled trên dev → ghi nhận là Info finding | | |
