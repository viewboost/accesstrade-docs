# Product Requirements Document: Influencer Profile cho Ambassador — Đăng ký kênh & Làm giàu dữ liệu (Enrich)

**Date:** 2026-06-11
**Author:** vinhnguyen
**Version:** 1.0
**Project:** Ambassador
**Project Type:** Feature port (clone từ T-Fluencers → Ambassador) — backend (Go/Echo/MongoDB) + frontend creator (Umi/React)
**Project Level:** 3 (scope rộng — 4 mảnh chức năng, tích hợp ngoài AT-Core, schema mới)
**Status:** Draft

---

## Document Overview

PRD này định nghĩa yêu cầu chức năng (FR) và phi chức năng (NFR) cho việc **nhân bản chức năng influencer-profile phía creator từ T-Fluencers (Techcombank) sang Ambassador**: creator tự đăng ký & xác minh kênh social, khai báo hồ sơ, hệ thống tự làm giàu dữ liệu (enrich) qua AT-Core, và creator theo dõi trạng thái kênh.

PRD là source of truth cho phần "what" (chức năng) và "how-well" (chất lượng), đồng thời là **nguồn sinh test case** — mỗi FR + acceptance criteria ánh xạ thẳng thành ca kiểm thử. Phần "how" (kỹ thuật chi tiết: schema, API contract, migration) sẽ nằm ở tech-spec đi kèm (tạo sau).

**Related Documents:**
- Overview: [`overview.md`](./overview.md)
- Tech Spec: *(sẽ tạo ở bước sau)*
- Nguồn tham chiếu (T-Fluencers): chức năng influencer-profile trong codebase `techcombank/backend` — luồng `LinkUserSocial`, collections `user-socials` / `user-social-partners` / `influencer-profiles`, webhook enrichment, AT-Core client.
- Hiện trạng Ambassador (code reference): `ambassabor/backend/internal/model/mg/user_social.go` (collection `user-socials` đã có ở mức cơ bản), `ambassabor/backend/pkg/public/service/user.go` (`LinkUserSocial`, `GetListUserSocial`), `ambassabor/backend/pkg/public/service/content.go` (luồng đăng bài — **giữ nguyên**).

---

## Executive Summary

Ambassador dùng chung nền tảng công nghệ với T-Fluencers nhưng phần hồ sơ influencer mới ở mức **cơ bản**: lưu link/tài khoản creator khai báo, **không** xác minh quyền sở hữu chặt, **không** có dữ liệu hồ sơ đầy đủ (follower thật, engagement, score, nhân khẩu học), creator **không** thấy được trạng thái kênh.

T-Fluencers đã có đầy đủ luồng này (đã chạy production): creator đăng ký kênh → xác minh ownership → khai báo hồ sơ → hệ thống tự gọi **AT-Core** enrich (bất đồng bộ, webhook callback) → lưu enriched data → creator theo dõi trạng thái. Có thêm cron vớt job treo.

Mục tiêu: **port 4 mảnh creator-facing** sang Ambassador, giữ chất lượng đã được chứng minh ở T-Fluencers, **không** đụng tới màn admin dashboard và **không** thay đổi luồng đăng bài hiện tại của Ambassador.

**Ràng buộc cốt lõi (rủi ro cao nhất):** T-Fluencers buộc chặt "đăng bài phải chọn hồ sơ social đã duyệt" ngay ở khâu validation đầu vào (`request/content.go`). Ambassador thì gắn hồ sơ **có điều kiện theo nguồn** (một số nguồn require, còn lại không). Khi port, **không** được bê ràng buộc đồng loạt của T-Fluencers — phải giữ luồng đăng bài Ambassador **y như hiện tại**.

---

## Product Goals

### Business Objectives

1. **Đạt ngang bằng T-Fluencers về dữ liệu hồ sơ influencer** — Ambassador có dữ liệu kênh đầy đủ và đáng tin (follower thật, engagement, score, nhân khẩu học) để chọn creator, phân nhóm chiến dịch, báo cáo cho thương hiệu.
2. **Giảm gian lận, làm sạch dữ liệu** — xác minh quyền sở hữu kênh trước khi ghi nhận, thay vì tin tưởng link creator tự khai.
3. **Không gây gián đoạn** — luồng đăng bài hiện tại của creator Ambassador giữ nguyên 100%; hồ sơ influencer là module song song, không phải tiền đề mới của đăng bài.

### Success Metrics

- 100% kênh đăng ký mới đi qua bước xác minh quyền sở hữu (OAuth / hashtag / crawl) trước khi ở trạng thái "đã đạt".
- ≥ 95% kênh đã liên kết được enrich thành công (có enriched data) trong vòng X phút kể từ lúc đăng ký (X chốt ở tech-spec theo SLA AT-Core).
- 0 job enrich bị kẹt vĩnh viễn — mọi job "treo" được cron vớt và chuyển sang trạng thái cuối (completed/failed) trong ≤ 1 chu kỳ cron.
- **0% thay đổi hành vi đăng bài** — sau deploy, luồng submit content của mọi nguồn cho kết quả giống hệt trước (regression test pass 100%).
- Creator xem được trạng thái + số liệu kênh của mình ngay trên cổng creator (0 báo lỗi "không thấy trạng thái kênh").

---

## Functional Requirements

Tổ chức theo 4 mảnh creator-facing đã chốt trong overview, cộng các yêu cầu nền tảng (data model, AT-Core integration, ranh giới đăng bài).

### FR-001: Creator đăng ký & liên kết kênh social

**Priority:** Must Have

**Description:**
Creator có thể đăng ký một kênh social vào hồ sơ của mình bằng cách chọn nền tảng và cung cấp thông tin tương ứng (OAuth token với TikTok; link kênh + hashtag định danh với YouTube/Facebook/Instagram). Hệ thống tạo bản ghi `user-social` gắn với creator và tạo quan hệ `user-social-partner`.

**Acceptance Criteria:**
- [ ] Creator chọn được nền tảng từ danh sách hỗ trợ (mặc định kế thừa T-Fluencers: TikTok, YouTube, Facebook, Instagram — chốt cuối ở tech-spec theo thực tế Ambassador).
- [ ] Với TikTok: creator đăng nhập ủy quyền (OAuth), hệ thống lấy được thông tin kênh (id, username, name, avatar, followers) từ token.
- [ ] Với YouTube/Facebook/Instagram: creator dán link kênh hợp lệ; link sai định dạng theo nền tảng bị từ chối với thông báo rõ.
- [ ] Hệ thống chặn liên kết một kênh đã được creator khác liên kết (duplicate check theo định danh kênh).
- [ ] Sau khi liên kết thành công, hệ thống tạo bản ghi `user-social` (gắn `user`) và bản ghi `user-social-partner` tương ứng, trả về `userSocialId`.

**Dependencies:** FR-007 (data model), FR-008 (user-social-partner)

---

### FR-002: Xác minh quyền sở hữu kênh (ownership verification)

**Priority:** Must Have

**Description:**
Trước khi một kênh được coi là "đã đạt", hệ thống phải xác minh creator thực sự sở hữu kênh đó, theo phương thức phù hợp từng nền tảng.

**Acceptance Criteria:**
- [ ] TikTok (OAuth): quyền sở hữu xác minh **tự động ngay** qua token → `ownershipMethod = oauth`, `ownershipStatus = verified`.
- [ ] YouTube (URL + hashtag): hệ thống đọc mô tả kênh, kiểm tra có chứa **hashtag định danh** được cấp → pass thì `verified`, chưa có thì `hashtag_pending`.
- [ ] Facebook/Instagram (URL + hashtag): tạo job crawl hồ sơ để kiểm tra hashtag; trong lúc chờ giữ trạng thái pending; có kết quả thì cập nhật `verified`/`failed`.
- [ ] Trạng thái kênh phản ánh đúng kết quả xác minh (chờ / đã đạt / từ chối kèm lý do).
- [ ] Kênh chưa `verified` **không** được tính là kênh "đã đạt" trong các nơi cần điều kiện này.

**Dependencies:** FR-001

---

### FR-003: Creator khai báo hồ sơ (demographics wizard)

**Priority:** Must Have

**Description:**
Sau khi liên kết kênh thành công, creator nhập thông tin định tính về kênh và khán giả vào hồ sơ influencer (lưu ở `influencer-profiles`).

**Acceptance Criteria:**
- [ ] Creator nhập được: lĩnh vực nội dung chính (categories, tối đa 3), lĩnh vực phụ (subCategories, tối đa 10), ngôn ngữ nội dung, độ tuổi khán giả, giới tính, khu vực/thành phố, email liên hệ.
- [ ] Ràng buộc số lượng (categories ≤ 3, subCategories ≤ 10) được enforce; vượt quá bị từ chối với thông báo rõ.
- [ ] Dữ liệu wizard lưu vào bản ghi `influencer-profile` gắn với `user` và `userSocial` tương ứng.
- [ ] Wizard **không bắt buộc** để hoàn tất liên kết kênh (kênh vẫn tồn tại nếu creator bỏ qua wizard) — trừ khi chốt khác ở tech-spec.

**Dependencies:** FR-001, FR-009 (influencer-profile model)

---

### FR-004: Tự động gửi yêu cầu làm giàu dữ liệu (enrich) sang AT-Core

**Priority:** Must Have

**Description:**
Sau khi kênh được liên kết, hệ thống tự động gửi kênh sang AT-Core để enrich, không cần creator thao tác. Hệ thống ghi nhận job để theo dõi.

**Acceptance Criteria:**
- [ ] Hệ thống dựng URL kênh từ dữ liệu `user-social` và gọi AT-Core `POST /v1/partners/profiles/enrich`.
- [ ] Gọi AT-Core dùng **một bộ partner credential dùng chung toàn nền tảng** (X-Partner-ID + X-API-Key), không tách theo tenant.
- [ ] Lưu `atCoreJobId` và `atCoreStatus` (submitted/processing...) vào bản ghi `user-social`.
- [ ] Trường hợp AT-Core trả kết quả ngay (cached/sync): xử lý như completed, cập nhật dữ liệu luôn (không chờ webhook).
- [ ] Lỗi gọi AT-Core (timeout/4xx/5xx) không làm hỏng việc liên kết kênh — creator vẫn liên kết được; job được đánh dấu để retry/recover.

**Dependencies:** FR-001, FR-010 (AT-Core client)

---

### FR-005: Nhận webhook enrichment & lưu enriched data

**Priority:** Must Have

**Description:**
Hệ thống cung cấp endpoint nhận webhook callback từ AT-Core khi job enrich xong, rồi lưu kết quả vào `user-social` và `influencer-profile`.

**Acceptance Criteria:**
- [ ] Có endpoint public nhận webhook (ví dụ `POST /influencer-profiles/webhook/enrichment`), được bảo vệ bằng cơ chế xác thực webhook AT-Core (không phải login creator).
- [ ] Khi `status = completed`: cập nhật `user-social.stats` (followers, views, likes, videoCount, engagementRate, avgViews), set `isEnriched = true`, `atCoreStatus = synced`, `atCoreSyncedAt = now`; đồng thời upsert `influencer-profile` với enriched data (scoreTotal, scoreCategory, handle, platform, avatarUrl, categories, isVerified, avgViews, totalViews, totalLikes, tracking.enrichedAt).
- [ ] Khi `status = failed`: set `atCoreStatus = failed`, ghi `tracking.errorCode` / `tracking.errorMsg` vào influencer-profile.
- [ ] Webhook tìm đúng bản ghi qua `atCoreJobId = payload.JobID`; job không khớp được xử lý an toàn (log, không 5xx).
- [ ] Mỗi webhook payload được lưu vào collection tracking để truy vết.

**Dependencies:** FR-004, FR-009

---

### FR-006: Vớt job enrich treo (stale recovery cron)

**Priority:** Must Have

**Description:**
Tác vụ định kỳ tự rà các job enrich bị treo (đã submit nhưng quá lâu không có webhook) và chủ động hỏi lại AT-Core để cập nhật.

**Acceptance Criteria:**
- [ ] Cron quét `user-social` có `atCoreStatus` ở trạng thái chờ (pending/submitted/processing) và đã quá ngưỡng thời gian (ví dụ > 30 phút) không cập nhật.
- [ ] Với mỗi job treo, hệ thống gọi AT-Core `GET /v1/partners/jobs/{jobId}` để lấy trạng thái mới nhất.
- [ ] Nếu job đã completed/failed: cập nhật DB như luồng webhook (tái dùng cùng logic).
- [ ] Sau mỗi chu kỳ cron, không còn job nào kẹt quá ngưỡng mà không được xử lý.

**Dependencies:** FR-005, FR-010

---

### FR-007: Mở rộng data model `user-social` cho enrichment

**Priority:** Must Have

**Description:**
Bổ sung các trường enrichment & ownership vào model `user-social` hiện có của Ambassador để tương thích luồng port.

**Acceptance Criteria:**
- [ ] `user-social` có thêm các trường: `stats` (UserChannelStats), `isEnriched`, `atCoreJobId`, `atCoreStatus`, `atCoreSyncedAt`, `ownershipStatus`, `ownershipMethod`, `ownershipAt`, `isPrimary`, `isTokenExpired`.
- [ ] Bản ghi `user-social` cũ (đã tồn tại) vẫn đọc/ghi được sau khi thêm trường (backward compatible; trường mới optional/có default).
- [ ] Đối chiếu schema với Ambassador hiện tại được ghi rõ ở tech-spec (trường nào đã có, trường nào thêm mới) — **không** copy mù từ T-Fluencers.

**Dependencies:** —

---

### FR-008: Data model `user-social-partner`

**Priority:** Must Have

**Description:**
Tạo collection/model `user-social-partner` lưu quan hệ creator – kênh – chương trình (partner) và trạng thái duyệt theo partner.

**Acceptance Criteria:**
- [ ] Có model `user-social-partner` với các trường: `user`, `userSocial`, `partner`, `status`, `source`, `reason`, `createdAt`, `updatedAt`.
- [ ] Khi creator liên kết kênh (FR-001), hệ thống tạo bản ghi `user-social-partner` tương ứng.
- [ ] Trạng thái duyệt theo partner truy vấn được để phục vụ điều kiện "kênh đã đạt theo chương trình".

**Dependencies:** FR-001

---

### FR-009: Data model `influencer-profile`

**Priority:** Must Have

**Description:**
Tạo collection/model `influencer-profile` lưu hồ sơ influencer: phần creator khai báo (wizard) + phần enriched từ AT-Core.

**Acceptance Criteria:**
- [ ] Có model `influencer-profile` với các nhóm trường: định danh (`user`, `userSocial`, `profileId`, `handle`, `platform`), creator khai báo (`displayName`, `categories`, `subCategories`, `contentLanguage`, `audienceAge`, `gender`, `city`, `email`), enriched (`scoreTotal`, `scoreCategory`, `avatarUrl`, `description`, `isVerified`, `avgViews`, `totalViews`, `totalLikes`), và `tracking` (enrichedAt/errorCode/errorMsg).
- [ ] Dual-write nhất quán: stats → `user-social`, enriched/score → `influencer-profile` (như luồng T-Fluencers).
- [ ] Upsert đúng theo (`user`, `userSocial`) — không tạo trùng bản ghi cho cùng một kênh.

**Dependencies:** FR-003, FR-005

---

### FR-010: AT-Core client tích hợp

**Priority:** Must Have

**Description:**
Bổ sung client gọi AT-Core (enrich + job status) vào Ambassador, cấu hình bằng partner credential dùng chung.

**Acceptance Criteria:**
- [ ] Client gọi được `POST /v1/partners/profiles/enrich` (trả về JobID/Status/Mode/Profile) và `GET /v1/partners/jobs/{jobId}` (trả về Status/Profile/Error).
- [ ] Credential (X-Partner-ID, X-API-Key, base URL) lấy từ config/env, dùng chung toàn nền tảng.
- [ ] Có xử lý timeout, mã lỗi, và mapping response AT-Core → model nội bộ rõ ràng.

**Dependencies:** —

---

### FR-011: Creator theo dõi trạng thái & số liệu kênh

**Priority:** Must Have

**Description:**
Trên cổng creator, creator xem được danh sách kênh đã đăng ký, nhóm theo nền tảng, kèm trạng thái xác minh và số liệu sau enrich.

**Acceptance Criteria:**
- [ ] Trang hồ sơ hiển thị danh sách kênh nhóm theo nền tảng (TikTok/YouTube/Facebook/Instagram).
- [ ] Mỗi kênh hiển thị trạng thái xác minh (đang chờ / đã đạt / bị từ chối — kèm lý do nếu có).
- [ ] Sau khi enrich về, kênh hiển thị số liệu (followers, views, likes, engagement...) và trạng thái tự cập nhật khi dữ liệu thay đổi.
- [ ] Creator chỉ xem được kênh của chính mình (không lộ kênh creator khác).

**Dependencies:** FR-001, FR-002, FR-005

---

### FR-012: Giữ nguyên luồng đăng bài (submit content) ⚠️

**Priority:** Must Have

**Description:**
Việc port influencer-profile **không** được thay đổi điều kiện gắn hồ sơ social khi đăng bài. Luồng submit content của Ambassador giữ **y như hiện tại**: nguồn nào đang require chọn social thì vẫn require, nguồn nào không thì vẫn không. Tuyệt đối không bê ràng buộc "mọi nguồn đều bắt buộc chọn hồ sơ đã duyệt" của T-Fluencers.

**Acceptance Criteria:**
- [ ] Sau khi triển khai, đăng bài với mọi nguồn cho kết quả **giống hệt** trước khi port (regression):
  - [ ] Nguồn đang require chọn social (ví dụ TikTok, Threads, Facebook post) — vẫn require như cũ.
  - [ ] Nguồn không require — vẫn đăng được mà không cần chọn social.
- [ ] Khâu validation đầu vào của `submit content` **không** bị thêm điều kiện "bắt buộc userSocialId/đã duyệt" áp cho mọi nguồn.
- [ ] Không có thay đổi nào ở `request/content.go` (validation) và service đăng bài khiến nguồn đang đăng tự do bị chặn.
- [ ] Có bộ regression test phủ cả nhánh require và không-require theo nguồn.

**Dependencies:** — (đây là ràng buộc bảo toàn, không phải tính năng mới)

---

### FR-013: Gỡ liên kết kênh (unlink)

**Priority:** Should Have

**Description:**
Creator có thể gỡ một kênh đã liên kết khỏi hồ sơ (kế thừa hành vi đã có ở Ambassador, đảm bảo nhất quán với data model mới).

**Acceptance Criteria:**
- [ ] Creator gỡ được kênh của mình; bản ghi `user-social` chuyển trạng thái phù hợp (inactive) hoặc xóa theo quy ước hiện hành.
- [ ] Gỡ kênh không làm hỏng dữ liệu `influencer-profile`/`user-social-partner` liên quan (xử lý nhất quán, có quy ước rõ ở tech-spec).
- [ ] Gỡ kênh không ảnh hưởng bài đăng đã tạo trước đó.

**Dependencies:** FR-001, FR-007

---

### FR-014: Xử lý token hết hạn / relink (TikTok)

**Priority:** Should Have

**Description:**
Với kênh OAuth (TikTok), khi token hết hạn, hệ thống đánh dấu và cho phép creator liên kết lại để khôi phục dữ liệu.

**Acceptance Criteria:**
- [ ] Khi phát hiện token hết hạn, hệ thống set `isTokenExpired = true` và phản ánh trạng thái cho creator.
- [ ] Creator relink được kênh đã hết hạn token (cập nhật token mới, không tạo bản ghi trùng).
- [ ] Tham chiếu issue đã biết ở Ambassador: `docs/ambassador/issues-may/issue-tiktok-token-expired-relink.md` để đảm bảo nhất quán.

**Dependencies:** FR-001

---

## Non-Functional Requirements

### NFR-001: Performance — Enrich bất đồng bộ, không chặn creator

**Priority:** Must Have

**Description:**
Luồng enrich phải bất đồng bộ; thao tác liên kết kênh của creator không bị treo chờ AT-Core.

**Acceptance Criteria:**
- [ ] Thao tác liên kết kênh trả về cho creator trong thời gian tương đương các thao tác hiện có (không bị kéo dài do chờ enrich).
- [ ] Việc gọi AT-Core enrich chạy ngoài luồng phản hồi đồng bộ (hoặc xử lý "submit rồi trả ngay", chờ webhook).

**Rationale:** AT-Core xử lý vài giây đến vài phút; không được để creator chờ.

---

### NFR-002: Reliability — Không job nào kẹt vĩnh viễn

**Priority:** Must Have

**Description:**
Mọi job enrich phải đi đến trạng thái cuối (completed/failed), kể cả khi webhook bị mất.

**Acceptance Criteria:**
- [ ] Cron recovery (FR-006) đảm bảo job treo được xử lý trong ≤ 1 chu kỳ cron sau khi vượt ngưỡng.
- [ ] Webhook xử lý idempotent: nhận trùng payload cho cùng job không gây sai dữ liệu.

**Rationale:** Phụ thuộc dịch vụ ngoài (AT-Core) → phải có cơ chế tự phục hồi.

---

### NFR-003: Backward compatibility — Không gãy dữ liệu & luồng cũ

**Priority:** Must Have

**Description:**
Thêm trường/collection mới không được làm hỏng dữ liệu `user-social` cũ và các luồng creator đang chạy.

**Acceptance Criteria:**
- [ ] Bản ghi `user-social` cũ đọc/ghi bình thường sau migration (trường mới optional/default).
- [ ] **Luồng đăng bài giữ nguyên 100%** (gắn với FR-012).
- [ ] Migration có thể chạy lại an toàn (idempotent) và có phương án rollback ghi ở tech-spec.

**Rationale:** Ambassador đang vận hành; không được gây downtime/regression.

---

### NFR-004: Security — Xác thực webhook & bảo vệ dữ liệu creator

**Priority:** Must Have

**Description:**
Endpoint webhook và dữ liệu hồ sơ phải được bảo vệ đúng mức.

**Acceptance Criteria:**
- [ ] Webhook enrichment chỉ chấp nhận request hợp lệ từ AT-Core (cơ chế auth webhook), từ chối request giả mạo.
- [ ] Partner credential AT-Core (X-API-Key) lưu trong config/secret, không hardcode, không log ra ngoài.
- [ ] Creator chỉ truy cập được hồ sơ/kênh của chính mình (không IDOR sang creator khác).

**Rationale:** Webhook là endpoint public; credential là bí mật; dữ liệu hồ sơ là dữ liệu cá nhân.

---

### NFR-005: Multi-tenant — Dùng chung credential nhưng cô lập dữ liệu creator

**Priority:** Must Have

**Description:**
Dù dùng chung 1 partner credential gọi AT-Core, dữ liệu creator/kênh vẫn phải gắn đúng tenant/partner.

**Acceptance Criteria:**
- [ ] Bản ghi `user-social-partner` gắn đúng `partner` của tenant phát sinh.
- [ ] Việc dùng chung credential được ghi nhận là quyết định có chủ đích; tác động tới khả năng tách số liệu theo tenant được nêu ở open questions.

**Rationale:** Ambassador là multi-tenant (~14 tenant); credential dùng chung là quyết định đã chốt giai đoạn này.

---

### NFR-006: Maintainability — Tái dùng logic, không copy mù

**Priority:** Should Have

**Description:**
Port phải đối chiếu code 2 bên, tái dùng pattern T-Fluencers nhưng thích nghi với khác biệt của Ambassador.

**Acceptance Criteria:**
- [ ] Logic webhook và recovery dùng chung một đường xử lý (không nhân đôi).
- [ ] Tech-spec ghi rõ bảng đối chiếu trường/luồng giữa Ambassador và T-Fluencers, đánh dấu phần đã có / thêm mới / khác biệt.

**Rationale:** 2 sản phẩm cùng base nhưng đã diverge; copy mù sẽ sinh bug.

---

### NFR-007: Localization — UI creator tiếng Việt

**Priority:** Should Have

**Description:**
Mọi text creator nhìn thấy ở luồng đăng ký kênh / wizard / trạng thái phải tiếng Việt, nhất quán thuật ngữ.

**Acceptance Criteria:**
- [ ] Không hardcode text; text hiển thị qua cơ chế i18n hiện hành của frontend Ambassador.
- [ ] Thuật ngữ nhất quán (kênh, hồ sơ, đã đạt/đang chờ/từ chối...).

**Rationale:** Đối tượng người dùng là creator Việt Nam.

---

## Epics

### EPIC-001: Nền tảng dữ liệu hồ sơ influencer (data layer)

**Description:**
Dựng/mở rộng các model và migration làm nền cho toàn bộ feature: mở rộng `user-social`, tạo `user-social-partner`, `influencer-profile`.

**Functional Requirements:** FR-007, FR-008, FR-009

**Story Count Estimate:** 4–6

**Priority:** Must Have

**Business Value:** Mọi mảnh còn lại phụ thuộc data layer; làm trước để các epic sau triển khai song song.

---

### EPIC-002: Đăng ký & xác minh kênh (creator-facing)

**Description:**
Luồng creator liên kết kênh + xác minh quyền sở hữu theo từng nền tảng, tạo quan hệ user-social-partner.

**Functional Requirements:** FR-001, FR-002, FR-008, FR-013, FR-014

**Story Count Estimate:** 6–9

**Priority:** Must Have

**Business Value:** Cửa ngõ đưa kênh sạch (đã xác minh) vào hệ thống.

---

### EPIC-003: Khai báo hồ sơ (demographics wizard)

**Description:**
Wizard creator nhập thông tin định tính, lưu vào influencer-profile.

**Functional Requirements:** FR-003, FR-009

**Story Count Estimate:** 2–4

**Priority:** Must Have

**Business Value:** Bổ sung dữ liệu chỉ creator biết, làm giàu hồ sơ.

---

### EPIC-004: Làm giàu dữ liệu qua AT-Core (enrich pipeline)

**Description:**
Tích hợp AT-Core: gửi enrich, nhận webhook, lưu enriched data, cron vớt job treo.

**Functional Requirements:** FR-004, FR-005, FR-006, FR-010

**Story Count Estimate:** 6–9

**Priority:** Must Have

**Business Value:** Mảnh giá trị nhất — biến link thành hồ sơ giàu dữ liệu, tự động.

---

### EPIC-005: Hiển thị trạng thái cho creator (UI)

**Description:**
Cổng creator hiển thị danh sách kênh, trạng thái xác minh và số liệu enrich.

**Functional Requirements:** FR-011

**Story Count Estimate:** 3–5

**Priority:** Must Have

**Business Value:** Creator thấy được kết quả, minh bạch trạng thái kênh.

---

### EPIC-006: Bảo toàn luồng đăng bài (regression guard)

**Description:**
Đảm bảo việc port không thay đổi điều kiện đăng bài; xây regression test phủ cả nhánh require và không-require theo nguồn.

**Functional Requirements:** FR-012

**Story Count Estimate:** 2–3

**Priority:** Must Have

**Business Value:** Chặn rủi ro cao nhất của dự án — gãy luồng đăng bài đang chạy.

---

## User Stories (High-Level)

- **EPIC-002:** "Là một creator, tôi muốn đăng nhập TikTok để liên kết kênh và được xác minh tự động, để không phải làm thủ công."
- **EPIC-002:** "Là một creator YouTube, tôi muốn dán link kênh + thêm hashtag định danh, để chứng minh kênh là của tôi."
- **EPIC-003:** "Là một creator, tôi muốn khai báo lĩnh vực nội dung và khán giả, để hồ sơ của tôi đầy đủ hơn."
- **EPIC-004:** "Là hệ thống, tôi muốn tự gửi kênh đi enrich và nhận kết quả về, để creator có số liệu mà không cần thao tác."
- **EPIC-005:** "Là một creator, tôi muốn thấy kênh của mình đang ở trạng thái nào và số liệu ra sao, để biết mình đã đủ điều kiện chưa."
- **EPIC-006:** "Là một creator hiện hữu, tôi muốn tiếp tục đăng bài như trước, để không bị gián đoạn bởi tính năng mới."

*Chi tiết story sẽ được tạo ở sprint planning (Phase 4).*

---

## User Personas

- **Creator/Influencer (Ambassador):** người dùng cuối, đăng ký kênh, khai báo hồ sơ, đăng bài tham gia chiến dịch. Đối tượng chính của PRD này.
- **Hệ thống AT-Core (bên ngoài):** dịch vụ enrich; Ambassador là bên gọi và nhận webhook.
- *(Ngoài scope: Admin/Ops xem dữ liệu trên dashboard — không thuộc PRD này.)*

---

## User Flows

1. **Đăng ký kênh → xác minh → enrich:** Creator chọn nền tảng → OAuth/URL+hashtag → hệ thống xác minh ownership → lưu user-social + user-social-partner → tự gửi AT-Core enrich → webhook trả về → lưu enriched data → creator thấy trạng thái + số liệu.
2. **Khai báo hồ sơ:** Sau liên kết → wizard nhập categories/khán giả → lưu influencer-profile.
3. **Đăng bài (giữ nguyên):** Creator đăng bài như hiện tại — nguồn require thì chọn social, nguồn khác thì không. Không thay đổi.

---

## Dependencies

### Internal Dependencies

- Model/collection `user-social` hiện có của Ambassador (`ambassabor/backend/internal/model/mg/user_social.go`).
- Luồng đăng bài hiện tại (`ambassabor/backend/pkg/public/service/content.go`, `pkg/public/model/request/content.go`) — phụ thuộc kiểu "không được phá".
- Cơ chế i18n frontend creator (Umi/React).
- Cron/scheduler hiện có của Ambassador (cho FR-006).

### External Dependencies

- **AT-Core** (`/v1/partners/profiles/enrich`, `/v1/partners/jobs/{jobId}`, webhook callback) — credential dùng chung toàn nền tảng.
- API các nền tảng social (TikTok OAuth, YouTube/Facebook/Instagram) cho lấy dữ liệu & xác minh.

---

## Assumptions

- Ambassador và T-Fluencers cùng base code → pattern T-Fluencers áp dụng được sau khi đối chiếu khác biệt.
- AT-Core sẵn sàng nhận enrich từ Ambassador với 1 partner credential dùng chung (cần cấp credential).
- Danh sách nền tảng hỗ trợ kế thừa T-Fluencers (TikTok, YouTube, Facebook, Instagram), chốt cuối ở tech-spec theo thực tế Ambassador.
- Collection `user-social` của Ambassador đủ tương thích để mở rộng thêm trường (không cần tái cấu trúc lớn).

---

## Out of Scope

- **Màn hình admin xem/duyệt dữ liệu hồ sơ trên dashboard** — loại trừ rõ ràng theo yêu cầu.
- **Báo cáo/thống kê/xếp hạng** dựa trên dữ liệu hồ sơ.
- **Thay đổi logic chấm điểm/tính toán của AT-Core** — Ambassador chỉ gọi và nhận.
- **Thay đổi luồng đăng bài** (chuẩn hóa lại quy tắc bài đăng ↔ hồ sơ) — để giai đoạn sau.
- **Tách partner credential AT-Core theo từng tenant** — giai đoạn này dùng chung.

---

## Open Questions

1. **Danh sách nền tảng:** Ambassador thực tế hỗ trợ đúng những nền tảng nào (có Threads/Shopee như user_social hiện liệt kê không)? Cần chốt để xác định phạm vi enrich/ownership.
2. **Credential dùng chung & tách số liệu tenant:** dùng chung 1 credential AT-Core có ảnh hưởng tới khả năng tách/báo cáo số liệu enrich theo từng tenant về sau không? Team AT-Core/infra xác nhận.
3. **Ngưỡng & SLA enrich:** thời gian tối đa kỳ vọng cho 1 job enrich (để chốt metric "X phút") và ngưỡng "treo" của cron.
4. **Quy ước unlink:** gỡ kênh thì xử lý influencer-profile/user-social-partner liên quan thế nào (giữ/ẩn/xóa) — chốt ở tech-spec.
5. **Nguồn nào đang require chọn social khi đăng bài:** xác nhận chính xác danh sách nguồn require hiện tại của Ambassador để viết regression test FR-012 cho đúng.

---

## Stakeholders

| Vai trò | Liên quan |
|---|---|
| Product/PM (DISO) | Chốt scope, ưu tiên |
| Backend (Go) | Data model, AT-Core integration, webhook, cron |
| Frontend (creator) | Đăng ký kênh, wizard, hiển thị trạng thái |
| AT-Core team | Cấp credential, đảm bảo enrich API/webhook |
| QA | Sinh test case từ FR/AC, đặc biệt regression đăng bài |

---

## Next Steps

### Phase 3: Tech Spec / Architecture

Tạo **tech-spec** cho feature (qua `/bmad:tech-spec`): bảng đối chiếu schema Ambassador ↔ T-Fluencers, AT-Core API contract & webhook, migration plan, và điểm bảo toàn luồng đăng bài. Đây là bước "how".

### Phase 4: Sprint Planning

Sau tech-spec, chạy `/bmad:sprint-planning` để bẻ epic thành story chi tiết, ước lượng, và xếp sprint.

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|--------------------|
| EPIC-001 | Nền tảng dữ liệu hồ sơ | FR-007, FR-008, FR-009 | 4–6 |
| EPIC-002 | Đăng ký & xác minh kênh | FR-001, FR-002, FR-008, FR-013, FR-014 | 6–9 |
| EPIC-003 | Khai báo hồ sơ (wizard) | FR-003, FR-009 | 2–4 |
| EPIC-004 | Làm giàu qua AT-Core | FR-004, FR-005, FR-006, FR-010 | 6–9 |
| EPIC-005 | Hiển thị trạng thái creator | FR-011 | 3–5 |
| EPIC-006 | Bảo toàn luồng đăng bài | FR-012 | 2–3 |

---

## Appendix B: Prioritization Details

**Functional Requirements:** 14 tổng
- **Must Have (12):** FR-001 → FR-012
- **Should Have (2):** FR-013 (unlink), FR-014 (token expired/relink)
- **Could Have (0)**

**Non-Functional Requirements:** 7 tổng
- **Must Have (5):** NFR-001 → NFR-005
- **Should Have (2):** NFR-006 (maintainability), NFR-007 (localization)

**Tổng story ước lượng:** ~23–36 stories (6 epics).
