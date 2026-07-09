# AT Core — Đề xuất nâng cấp và bàn giao chính thức về hạ tầng AT

> Diso đề xuất nâng cấp AT Core (lớp gateway giữa các dự án AT và Vendor Service) lên phiên bản chính thức, để mở cho nhiều dự án nội bộ AT cùng tích hợp. Tài liệu này gửi AT để xin phê duyệt phạm vi, nghiệm thu phần đã hoàn thành trong dự án T-Fluencers, và thống nhất kế hoạch triển khai tiếp.

**Ngày:** 06/06/2026
**Trạng thái:** Đề xuất, chờ AT phê duyệt
**Đối tượng đọc:** AT (Tech Lead, Operation, Finance)
**Người đề xuất:** Diso

---

## TL;DR

- AT Core đã được Diso xây dựng và vận hành ổn cho T-Fluencers từ tháng 01/2026.
- T-Fluencers (báo cáo nghiệm thu T5/2026) đặt vấn đề mở AT Core cho các dự án nội bộ AT khác cùng dùng — Diso đề xuất nghiệm thu phần đã có và bổ sung 2 module còn thiếu để vận hành bài bản khi có nhiều partner.
- **Phần lõi đã có sẵn (5/8 module): Partner CRUD + API key, Quota + Rate limit, Enrich + proxy Vendor + circuit breaker, Cache + lưu profile pool, Webhook outbound HMAC + retry + Admin UI events.**
- **Phần cần build mới (3/8 module): Log request theo partner, API + UI thống kê + export CSV, Bộ API document chính thức cho partner (Markdown).**
- Mỗi module nội bộ tự kèm tài liệu kỹ thuật (OpenAPI + admin guide tiếng Việt). Bộ API document cho partner đứng riêng — đáp ứng yêu cầu AT trong báo cáo nghiệm thu T5/2026.

---

## 1. Bối cảnh

### 1.1 Vai trò AT Core

AT đã biết rõ Vendor Service (đang dùng cho T-Fluencers): vendor cấp một endpoint và một API key cho mỗi tài khoản. Nếu nhiều dự án AT cùng dùng chung tài khoản này, sẽ không thống kê tách bạch được dự án nào dùng bao nhiêu, không kiểm soát hạn mức từng dự án, và lộ key chung phải đổi cho tất cả.

**AT Core** là lớp gateway Diso xây dựng để giải bài toán đó:

- Cấp API key riêng cho từng partner (dự án) AT.
- Định danh và tracking từng request theo partner.
- Forward sang Vendor Service bằng key chung duy nhất.
- Cache profile để giảm số call thực tế xuống Vendor.

Mô hình này tương tự cách AT Core đang phục vụ T-Fluencers hôm nay — chỉ có một partner (Techcombank) nên nhiều chức năng vận hành chưa cần bài bản.

### 1.2 Trạng thái hiện tại

AT Core đã chạy production phục vụ T-Fluencers từ tháng 01/2026 với các chức năng:

- Quản lý partner và cấp API key riêng cho từng partner.
- Forward enrich profile sang Vendor Service.
- Cache profile sau khi crawl.
- Tra cứu trạng thái job enrichment.
- Code webhook (HMAC sign + retry) đã có sẵn, T-Fluencers chưa kích hoạt.

### 1.3 AT đặt yêu cầu mở rộng

> *"Cung cấp lại API document để AT có thể đưa dịch vụ về core để tích hợp cho các dịch vụ của AT."*
>
> — Báo cáo nghiệm thu T-Fluencers T5/2026

---

## 2. Vấn đề cần giải quyết khi mở cho dự án thứ hai

Phiên bản hiện tại đủ dùng cho T-Fluencers — một partner, vận hành thủ công. Khi mở cho dự án thứ hai (Ambassador, vCreator-PH...), một số yếu tố cần bổ sung:

| Vấn đề | Hệ quả |
|---|---|
| Thống kê lưu lượng đang nằm ở phía T-Fluencers, AT Core chưa có | Nếu giữ pattern này, mỗi partner mới phải tự build lại logic thống kê. AT không có view tập trung để đối soát chi phí Vendor |
| Chưa có log request theo partner ở AT Core | Không biết partner nào gọi bao nhiêu, không phân tích được cache hit/miss để tối ưu cost Vendor |
| Chưa có tài liệu API chính thức | Mỗi partner mới phải hỏi qua chat, không scale |

---

## 3. Đề xuất triển khai

### 3.1 So sánh các phương án

Để mở dịch vụ crawl profile cho các dự án nội bộ AT tiếp theo, AT có 3 hướng đi:

| Phương án | Cách làm | Ưu điểm | Hạn chế |
|---|---|---|---|
| **1. Giữ nguyên — dùng trực tiếp Vendor Service** | Mỗi dự án AT gọi thẳng tới Vendor bằng chung 1 endpoint + 1 API key, mỗi dự án tự thống kê hiệu quả sử dụng phía mình | Không cần đầu tư thêm gì | Không thống kê tách bạch được dự án nào dùng bao nhiêu; không kiểm soát hạn mức từng dự án; lộ key chung phải đổi cho tất cả; mỗi dự án mới phải tự build lại logic thống kê |
| **2. Trả phí Vendor để được cấp thêm API key cho mỗi partner** | AT trả phí khởi tạo cho Vendor để Vendor cấp thêm API key độc lập theo từng dự án | Tách bạch được key theo dự án | Vẫn phụ thuộc Vendor về thống kê và quản lý; chi phí khởi tạo lặp lại mỗi dự án mới; không kiểm soát được hạn mức và logic chung phía AT |
| **3. Nâng cấp hoàn thiện AT Core và nghiệm thu toàn bộ** | Tận dụng AT Core đã có (đã chạy 6 tháng cho T-Fluencers), bổ sung 2 module Log + Thống kê cần thiết | AT làm chủ vận hành, dữ liệu, thống kê tập trung; partner mới onboard nhanh; chỉ một lần đầu tư, dùng được cho mọi dự án sau này | Cần đợt đầu tư hoàn thiện ban đầu (2 module dưới đây) |

Diso đề xuất **phương án 3**.

### 3.2 Phần AT Core đã có sẵn

#### a) Đã production — vận hành 6 tháng cho T-Fluencers

5 module dưới đây đã chạy production cho T-Fluencers, đợt này chỉ rà soát + đóng gói + chạy regression test + bổ sung tài liệu chính thức:

1. **Partner CRUD + sinh API key + check API key + Admin UI onboard.** 8 endpoint `/admin/partners/*` (Create/List/Get/Update/Deactivate/RegenerateKey), sinh API key prefix + hash bcrypt, middleware `partner_auth` check `X-Partner-ID` + `X-API-Key`, trang admin có form cấp key (modal + copy clipboard 1 lần) và form đăng ký webhook URL/secret.

2. **Quota atomic Redis + Rate limit per partner.** `DecrementQuota` atomic Redis INCR, `PartnerRateLimiter` cấu hình per-partner, endpoint `GET /v1/partners/quota` để partner tự check, form admin chỉnh quota.

3. **Nhận enrich + proxy Vendor + circuit breaker.** `POST /v1/partners/profiles/enrich` + `GET /v1/partners/jobs/{id}`, `ipclient` gọi Vendor với circuit breaker, retry, timeout, exponential backoff. Hỗ trợ mode sync / async / cached. Worker async + transformer + duplicate detection.

4. **Cache hit/miss + lưu kết quả profile pool.** Cache check trước khi gọi Vendor (tiết kiệm cost Vendor), lưu kết quả vào profile pool MongoDB, change repository track thay đổi profile theo thời gian, index theo `platform` + `externalId`.

5. **Webhook outbound HMAC + retry + Admin UI events.** Đăng ký webhook URL + secret per partner, HMAC-SHA256 ký payload (header `X-AT-Signature` + `X-AT-Timestamp`), tự động gửi event khi enrich job hoàn tất, `RetryWorker` poll DB và retry theo policy 1m/5m/15m/dead-letter, Admin UI list/detail/retry events. T-Fluencers chưa kích hoạt vì chưa cấu hình `webhookURL` cho partner record của mình, nhưng cơ chế hoạt động đầy đủ trong code.

#### b) Đã định hình và có demo bước đầu với T-Fluencers

Trong quá trình phục vụ T-Fluencers, Diso đã định hình sơ và demo bước đầu 3 chức năng dưới đây. Hiện chưa hoàn thiện, **không nằm trong báo giá đợt này** — nhưng baseline kỹ thuật đã có, các đợt mở rộng sau sẽ không phải làm từ con số 0:

- **Tìm kiếm và matching profile dựa trên campaign** — AT/partner search creator trong pool theo thông tin campaign (category, follower range, engagement, score...) và auto-suggest creator phù hợp. Đã có code search engine + scoring matching, cần hoàn thiện criteria builder UI, ranking algorithm, performance optimization cho pool lớn.
- **Phân quyền profile theo sở hữu partner** — mỗi partner sở hữu một subset profile riêng (creator do partner đó recruit), không thấy được profile của partner khác. Có cơ chế share profile giữa các partner nếu cần. Đã có concept ownership trong data model, cần hoàn thiện ACL middleware, sharing flow, audit ownership transfer.
- **Feedback brand → cập nhật điểm creator** — brand chấm điểm/feedback creator sau khi chạy campaign. Hệ thống tổng hợp feedback và tính lại điểm số theo performance thực tế. Đã có schema feedback + scoring rule sơ bộ, cần hoàn thiện aggregation algorithm, công thức tính lại điểm, anti-gaming.

**Ý nghĩa của các chức năng này với quyết định "có nên build AT Core bài bản":**

Đây là các chức năng có giá trị business cao và đặc trưng cho mô hình influencer platform của AT (Ambassador, vCreator-PH... đều sẽ cần). Nếu mỗi dự án AT tự build lại từ đầu thì rất tốn. Việc đặt chúng ở AT Core làm điểm trung tâm sẽ giúp AT:

- Tận dụng investment đã có (3 chức năng đã có baseline kỹ thuật).
- Tránh trùng lặp giữa các dự án — chỉ build 1 lần ở AT Core, mọi dự án đều dùng được.
- Có roadmap mở rộng rõ ràng cho 6–12 tháng tới mà không phải design lại kiến trúc.

→ Đây là một lý do bổ sung quan trọng để chọn phương án 3 (nâng cấp AT Core bài bản) thay vì phương án 1/2.

### 3.3 Phần cần build mới trong đợt này

Chỉ còn 2 module phải build mới:

**1. Log request theo partner**

Collection `request_logs` gồm `partnerId`, `endpoint`, `vendorCalled`, `status`, `duration`, `cacheHit`, `timestamp`. Middleware ghi log mỗi request đi qua `/v1/partners/*`. Index theo `partnerId` + `timestamp` cho query nhanh. Async write tránh ảnh hưởng latency. Đây là dữ liệu nền cho module thống kê ở dưới.

**2. API + Trang thống kê + Export CSV**

- `GET /admin/stats/partners?from&to` — tổng request theo partner trong khoảng thời gian.
- `GET /admin/stats/vendor?from&to` — tổng request gọi Vendor, phân tách cache hit (không tốn cost Vendor) và vendor miss (có cost).
- `GET /admin/stats/export?from&to&format=csv` — export raw để AT đối soát ngoài hệ thống.
- Trang admin UI: table phân theo partner + filter time range + nút Export CSV. Giữ tối thiểu, không có chart.

Đây là thay đổi quan trọng: thay vì để mỗi partner tự thống kê như T-Fluencers đang làm, nâng tracking lên ngay AT Core. Partner mới chỉ cần tích hợp API, không cần build lại logic đo lưu lượng.

**Tài liệu (OpenAPI spec + admin guide tiếng Việt) phân bổ vào từng module thay vì tách riêng** — mỗi module tự document chính nó để tránh tài liệu rời rạc.

### 3.4 Phạm vi không thuộc đợt này

Các hạng mục dưới đây Diso đề xuất cất sang đợt sau để giữ đợt này gọn, tập trung vào nghiệm thu phần đã có + 2 module thống kê:

- **Subscription/plan per partner** — phân plan free/basic/pro. Đợt này partner = nội bộ AT, chưa cần phân plan.
- **Kích hoạt webhook cho partner thật** — code đã có end-to-end, T-Fluencers chưa dùng nên chưa kích hoạt. Khi AT có partner cần push event → kích hoạt 1 ngày.
- **RBAC management UI + Activity log mở rộng cho partner domain** — RBAC enforce đã có, management UI và activity log mở rộng để sau.
- **Multi-tenant pool access (CONTRIBUTED/BOOKMARKED/BOOKED)** — model và service có sẵn, chưa wire vào pool filter. Khi AT onboard partner ngoài → cần wire.
- **3 chức năng đã định hình + có demo bước đầu** (matching theo campaign, phân quyền profile theo partner, feedback brand → cập nhật điểm) — xem chi tiết ở mục 3.2.b.
- **Self-service partner portal** cho partner tự đăng ký account.
- **Thương mại hoá AT Core ra ngoài AccessTrade** — không phải mục tiêu trước mắt.

---

## 4. Cam kết của Diso

| Hạng mục | Cam kết |
|---|---|
| Bảo trì sau bàn giao | Tiếp tục vận hành chung với gói vận hành Ambassador hiện tại |
| Tài liệu | OpenAPI spec + tech doc + admin guide tiếng Việt, phân bổ vào từng module |
| Source code | AT làm chủ source, Diso không giữ độc quyền |

---

## 5. Lợi ích cho AT

- **Tận dụng tối đa phần lõi đã có** — 5/7 module đã chạy production, không phải build lại logic gateway/cache/webhook cho từng dự án mới.
- **Có công cụ điều phối tài nguyên Vendor giữa các dự án** — dữ liệu thống kê tập trung, có cơ chế hạn mức.
- **Sẵn sàng cho roadmap mở rộng** — Ambassador, vCreator-PH, dự án mới đều có thể onboard trong vài ngày bằng dashboard admin và tài liệu API.
- **Bảo toàn investment vào các chức năng đã định hình** (mục 3.2.b) — matching theo campaign, phân quyền profile theo partner, feedback brand → điểm số. Đây là 3 chức năng đặc trưng cho mô hình influencer platform, mọi dự án AT đều sẽ cần. Việc đặt chúng ở AT Core giúp các đợt mở rộng sau không phải design lại kiến trúc và không trùng lặp công sức giữa các dự án.

---

## 6. Phạm vi không ảnh hưởng

- T-Fluencers production hiện tại giữ nguyên cách gọi API.
- Vendor Service phía sau không sửa giao thức với AT Core.
- Quy trình vận hành AT hiện tại không bị ép thay đổi.

---

## 7. Bước tiếp theo

Diso đề nghị AT:

1. **Chọn phương án triển khai** (mục 3.1) — Diso đề xuất phương án 3.
2. **Thống nhất phạm vi chi tiết** qua một buổi làm việc giữa Diso và Tech Lead AT.
3. **Xác nhận pricing và timeline** trong file `estimate.csv` đính kèm.

Sau khi AT phê duyệt nguyên tắc, Diso sẽ:

1. Viết PRD chi tiết cho 2 module build mới ở mục 3.3 (acceptance criteria, success metric).
2. Viết tech-spec đầy đủ (API contract, schema, error code).
3. Triển khai theo sprint, demo cho AT review mỗi 2 tuần.

---

## 8. Tài liệu liên quan

- `estimate.csv` — Báo giá 7 module theo cụm A/B/C, kèm trạng thái (đã có / build mới / đợt sau).
- `prd.md` — Yêu cầu chức năng + phi chức năng + acceptance criteria chi tiết (sau khi AT phê duyệt nguyên tắc).
- `tech-spec.md` — API contract, schema, error code, code sample, integration guide.
