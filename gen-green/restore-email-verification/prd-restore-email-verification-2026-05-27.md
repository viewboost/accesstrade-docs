# Product Requirements Document: Mở lại tính năng xác thực email (vCreator)

**Date:** 27/05/2026
**Author:** Team vCreator
**Version:** 1.0
**Project Type:** Feature restoration (Frontend)
**Project Level:** Level 2
**Status:** Draft

---

## Document Overview

PRD này định nghĩa functional requirements (FR) và non-functional requirements (NFR) cho việc **bật lại tính năng xác thực email** trên trang Tài khoản của vCreator frontend. Tính năng này trước đây bị tạm ẩn do chưa có API key của dịch vụ gửi email; nay key đã sẵn sàng nên team khôi phục lại UI hiển thị trạng thái + luồng xác thực OTP qua email.

Tài liệu là nguồn truy vết yêu cầu → test case: mỗi FR/AC ánh xạ trực tiếp thành ca kiểm thử.

**Related Documents:**
- Overview (business): [`overview.md`](./overview.md)
- Code liên quan: `vcreator/frontend/src/pages/account/components/form/index.tsx`

---

## Executive Summary

Trên trang Tài khoản, ô email hiện chỉ là một input đơn giản — hệ thống không biết email creator nhập có thật và thuộc về họ hay không. Phần xác thực email (gửi mã OTP qua hộp thư → nhập mã → đánh dấu "đã xác minh") đã được xây dựng trước đây nhưng bị **tạm ẩn vì chưa có API key của dịch vụ gửi email**.

Key đã được cấu hình, dịch vụ gửi email hoạt động trở lại. Đợt này team bật lại: hiển thị nhãn (pill) trạng thái "Đã xác minh" (xanh) / "Chưa xác minh" (vàng) bên cạnh ô email, và cho phép creator chủ động xác minh email qua mã OTP. Backend đã sẵn sàng phía cung cấp API; phạm vi PRD này tập trung vào frontend.

---

## Product Goals

### Business Objectives

1. **Tăng độ tin cậy dữ liệu liên hệ** — phân biệt được email đã xác minh (đáng tin) và chưa xác minh, phục vụ liên hệ / gửi thông báo / đối soát danh tính.
2. **Khôi phục tính năng đã đầu tư** — bật lại phần xác thực email đã xây dựng, khớp giao diện với backend sẵn sàng, loại bỏ phần "chết" bị ẩn.
3. **Trải nghiệm tự phục vụ** — creator tự xác minh email một cách đơn giản, không cần can thiệp thủ công từ Ops.

### Success Metrics

- Tỉ lệ creator có email đã xác minh trên tổng số creator có nhập email (mục tiêu định hướng, chốt số sau khi release).
- Tỉ lệ gửi mã OTP thành công tới hộp thư (delivery rate) > 95%.
- Số lượt xác minh thất bại do hết hạn / sai mã ở mức chấp nhận được (theo dõi để tinh chỉnh thời gian hiệu lực và giới hạn thử).

---

## Functional Requirements

Mỗi FR có ID, priority (MoSCoW) và acceptance criteria (AC) testable.

---

### FR-001: Hiển thị trạng thái xác minh email

**Priority:** Must Have

**Description:**
Bên cạnh ô email trên trang Tài khoản, hiển thị một nhãn (pill) cho biết email hiện tại đã xác minh hay chưa, dựa trên trạng thái `emailVerified` lấy từ thông tin user.

**Acceptance Criteria:**
- [ ] Khi `emailVerified = true`: hiển thị pill xanh với chữ "Đã xác minh".
- [ ] Khi `emailVerified = false`: hiển thị pill vàng với chữ "Chưa xác minh".
- [ ] Khi email rỗng (chưa nhập): không hiển thị pill nào.
- [ ] Pill nằm ở vị trí `rightContent` của ô email, không che/đè lên icon hoặc text input.

**Dependencies:** FR-006 (field `emailVerified` trong dữ liệu user)

---

### FR-002: Kích hoạt luồng xác minh từ pill "Chưa xác minh"

**Priority:** Must Have

**Description:**
Khi email chưa xác minh, creator có thể bấm vào hành động xác minh (nút/link gắn với pill vàng) để bắt đầu luồng gửi mã OTP.

**Acceptance Criteria:**
- [ ] Pill/khu vực "Chưa xác minh" có một hành động xác minh bấm được (nút hoặc link "Xác minh").
- [ ] Bấm hành động khi email hợp lệ → mở giao diện nhập mã OTP và kích hoạt gửi mã (FR-003).
- [ ] Bấm hành động khi ô email rỗng hoặc sai định dạng → hiển thị thông báo yêu cầu nhập email hợp lệ trước, KHÔNG gửi mã.
- [ ] Khi `emailVerified = true` → không hiển thị hành động xác minh.

**Dependencies:** FR-003

---

### FR-003: Gửi mã OTP qua email

**Priority:** Must Have

**Description:**
Hệ thống gửi một mã OTP tới địa chỉ email creator đang nhập, thông qua API backend (dùng dịch vụ gửi email đã có key).

**Acceptance Criteria:**
- [ ] Khi luồng xác minh được kích hoạt, frontend gọi API gửi OTP kèm địa chỉ email.
- [ ] Gọi thành công → hiển thị thông báo "Đã gửi mã tới {email}, kiểm tra hộp thư (kể cả mục spam)".
- [ ] Trong lúc chờ phản hồi API, nút gửi ở trạng thái loading và không cho bấm trùng.
- [ ] API trả lỗi → hiển thị thông báo lỗi rõ ràng (FR-008) và cho phép thử lại.

**Dependencies:** FR-002, DEP (API gửi OTP từ backend)

---

### FR-004: Nhập mã và xác minh

**Priority:** Must Have

**Description:**
Creator nhập mã OTP nhận được; frontend gửi mã lên backend để xác thực và cập nhật trạng thái email khi đúng.

**Acceptance Criteria:**
- [ ] Có ô nhập mã OTP với độ dài và định dạng theo quy ước backend (số/ký tự, độ dài cố định).
- [ ] Nhập đúng mã → API xác nhận thành công → pill chuyển sang "Đã xác minh" (xanh) mà không cần tải lại trang.
- [ ] Nhập sai mã → hiển thị thông báo "Mã không đúng", không đóng giao diện nhập mã, cho phép nhập lại.
- [ ] Nhập mã đã hết hạn → hiển thị thông báo "Mã đã hết hạn, vui lòng gửi lại mã" (liên kết FR-005, NFR-001).
- [ ] Nút xác nhận bị vô hiệu khi ô mã chưa đủ ký tự.

**Dependencies:** FR-003

---

### FR-005: Gửi lại mã OTP

**Priority:** Must Have

**Description:**
Creator có thể yêu cầu gửi lại mã OTP nếu không nhận được hoặc mã đã hết hạn.

**Acceptance Criteria:**
- [ ] Có nút "Gửi lại mã" trong giao diện nhập mã.
- [ ] Nút "Gửi lại mã" bị khóa trong một khoảng đếm ngược (countdown) sau mỗi lần gửi (theo NFR-002), hiển thị số giây còn lại.
- [ ] Hết countdown → nút mở lại; bấm → gửi mã mới và reset đếm ngược.
- [ ] Mã mới được gửi làm vô hiệu mã cũ (theo quy ước backend).

**Dependencies:** FR-003, NFR-002

---

### FR-006: Bổ sung trạng thái `emailVerified` vào dữ liệu user

**Priority:** Must Have

**Description:**
Interface `IUser` (frontend) hiện chưa có field thể hiện email đã xác minh. Cần bổ sung field trạng thái xác minh email để FR-001 hiển thị đúng.

**Acceptance Criteria:**
- [ ] Interface `IUser` (`src/interfaces/user.ts`) có field thể hiện trạng thái xác minh email (ví dụ `emailVerified: boolean` hoặc trong `Info`), khớp với dữ liệu backend trả về.
- [ ] Sau khi xác minh thành công (FR-004), state user trên frontend cập nhật field này thành `true`.
- [ ] Khi tải trang Tài khoản, trạng thái pill (FR-001) phản ánh đúng giá trị field từ API user detail.

**Dependencies:** DEP (backend trả field trạng thái xác minh trong user detail)

---

### FR-007: Khôi phục component xác thực vào đúng vị trí trang Tài khoản

**Priority:** Must Have

**Description:**
Khôi phục phần UI xác thực (pill + luồng nhập OTP) vào ô email trong form trang Tài khoản, nơi trước đây đã bị gỡ/ẩn.

**Acceptance Criteria:**
- [ ] Ô email trong `src/pages/account/components/form/index.tsx` hiển thị pill trạng thái (FR-001) và hành động xác minh (FR-002).
- [ ] Các trường khác trên form (tên hiển thị, giới tính, ngày sinh, ảnh đại diện) hoạt động không thay đổi.
- [ ] Việc lưu thông tin tài khoản ("Lưu thay đổi") vẫn hoạt động bình thường, không bị chặn bởi trạng thái xác minh email.

**Dependencies:** FR-001, FR-002

---

### FR-008: Thông báo lỗi và hướng dẫn người dùng

**Priority:** Should Have

**Description:**
Hiển thị thông báo rõ ràng cho các tình huống lỗi/biên trong luồng xác thực.

**Acceptance Criteria:**
- [ ] Gửi mã thất bại (lỗi mạng/API) → thông báo "Không gửi được mã, vui lòng thử lại".
- [ ] Có hướng dẫn kiểm tra mục spam trong thông báo sau khi gửi mã.
- [ ] Vượt quá số lần thử cho phép (NFR-001) → thông báo "Bạn đã thử quá số lần cho phép, vui lòng gửi lại mã / thử lại sau".
- [ ] Các thông báo dùng tiếng Việt, rõ ràng, không lộ chi tiết kỹ thuật (status code, stack trace).

**Dependencies:** FR-003, FR-004, FR-005

---

## Non-Functional Requirements

---

### NFR-001: Bảo mật — Thời gian hiệu lực và giới hạn thử mã OTP

**Priority:** Must Have

**Description:**
Mã OTP có thời gian hiệu lực giới hạn và số lần nhập sai bị giới hạn để chống dò mã.

**Acceptance Criteria:**
- [ ] Mã OTP hết hiệu lực sau một khoảng thời gian xác định (ví dụ 5 phút — chốt theo backend); nhập sau đó báo hết hạn.
- [ ] Số lần nhập sai mã liên tiếp bị giới hạn (ví dụ tối đa 5 lần — chốt theo backend); vượt quá yêu cầu gửi lại mã.
- [ ] Frontend phản ánh đúng phản hồi giới hạn/hết hạn từ backend, không tự ý bỏ qua.

**Rationale:** Tránh brute-force OTP và lạm dụng.

---

### NFR-002: Chống lạm dụng — Giới hạn tần suất gửi lại mã

**Priority:** Must Have

**Description:**
Việc gửi lại mã OTP bị giới hạn tần suất (rate limit) để tránh spam hộp thư và lạm dụng dịch vụ gửi email.

**Acceptance Criteria:**
- [ ] Sau mỗi lần gửi mã, nút "Gửi lại mã" bị khóa trong một khoảng đếm ngược (ví dụ 60 giây — chốt theo backend).
- [ ] Frontend tôn trọng phản hồi rate-limit từ backend (nếu backend từ chối do gửi quá nhanh, hiển thị thông báo phù hợp).

**Rationale:** Tránh tốn chi phí dịch vụ email và tránh người dùng spam chính hộp thư của họ.

---

### NFR-003: Khả năng giám sát dịch vụ gửi email

**Priority:** Should Have

**Description:**
Có cơ chế cảnh báo khi dịch vụ gửi email lỗi hoặc key hết hạn, để không lặp lại tình huống "tính năng chết âm thầm".

**Acceptance Criteria:**
- [ ] Khi tỉ lệ gửi OTP thất bại tăng bất thường hoặc API gửi mã trả lỗi xác thực (key invalid/expired) → có cảnh báo cho team kỹ thuật (qua log/monitoring đã có).
- [ ] Người dùng cuối nhận thông báo lỗi thân thiện (FR-008), không thấy chi tiết kỹ thuật.

**Rationale:** Bài học từ lần phải ẩn tính năng — cần phát hiện sớm sự cố dịch vụ email.

---

### NFR-004: Khả dụng — Trải nghiệm phản hồi nhanh

**Priority:** Should Have

**Description:**
Các thao tác trong luồng xác thực phản hồi đủ nhanh và có trạng thái loading rõ ràng.

**Acceptance Criteria:**
- [ ] Mọi nút gọi API (gửi mã, xác nhận mã, gửi lại) có trạng thái loading và chặn bấm trùng trong khi chờ.
- [ ] Phản hồi UI cho thao tác gửi/xác nhận trong vòng vài giây ở điều kiện mạng bình thường.

**Rationale:** Tránh người dùng bấm nhiều lần gây gửi trùng mã.

---

### NFR-005: Nhất quán giao diện và ngôn ngữ

**Priority:** Should Have

**Description:**
Giao diện xác thực email Việt hóa và đồng bộ với style hiện có của trang Tài khoản.

**Acceptance Criteria:**
- [ ] Toàn bộ text người dùng nhìn thấy bằng tiếng Việt (pill, thông báo, nút).
- [ ] Pill và component sử dụng đúng hệ màu/spacing nhất quán với UI hiện tại (xanh = thành công, vàng = cảnh báo).

**Rationale:** Đảm bảo nhất quán trải nghiệm vCreator.

---

## Epics

---

### EPIC-001: Hiển thị trạng thái xác minh email

**Description:**
Bổ sung dữ liệu trạng thái và hiển thị pill "Đã/Chưa xác minh" trên ô email trang Tài khoản.

**Functional Requirements:**
- FR-001
- FR-006
- FR-007

**Story Count Estimate:** 3-4 stories

**Priority:** Must Have

**Business Value:** Cho người dùng và hệ thống biết ngay email nào đáng tin; khớp UI với backend.

---

### EPIC-002: Luồng xác thực OTP qua email

**Description:**
Toàn bộ luồng creator tự xác minh email: kích hoạt → gửi mã → nhập mã → gửi lại → cập nhật trạng thái, kèm xử lý lỗi.

**Functional Requirements:**
- FR-002
- FR-003
- FR-004
- FR-005
- FR-008

**Story Count Estimate:** 4-6 stories

**Priority:** Must Have

**Business Value:** Trải nghiệm tự phục vụ, tăng tỉ lệ email đã xác minh, tận dụng dịch vụ email đã có key.

---

## User Stories (High-Level)

### EPIC-001

- "Là creator, tôi muốn nhìn thấy email của mình đã xác minh hay chưa ngay trên trang tài khoản, để biết tình trạng tài khoản của mình."
- "Là hệ thống, tôi muốn biết trạng thái xác minh email của creator, để phân biệt email đáng tin."

### EPIC-002

- "Là creator, tôi muốn bấm xác minh và nhận mã qua email, để xác nhận email là của tôi."
- "Là creator, tôi muốn gửi lại mã khi không nhận được, để hoàn tất xác minh."
- "Là creator, tôi muốn thấy thông báo rõ ràng khi nhập sai hoặc mã hết hạn, để biết cần làm gì tiếp theo."

Chi tiết story sẽ được tạo trong sprint planning (Phase 4).

---

## User Personas

- **Creator vCreator** — người dùng cuối, vào trang Tài khoản để quản lý thông tin cá nhân, là người thực hiện xác minh email.
- **Ops / CSKH** — hưởng lợi gián tiếp: email đã xác minh giúp liên hệ và đối soát tin cậy hơn.

---

## User Flows

1. **Xem trạng thái:** Creator mở trang Tài khoản → nhìn thấy pill "Đã/Chưa xác minh" cạnh email.
2. **Xác minh email:** Creator (email chưa xác minh) bấm "Xác minh" → hệ thống gửi mã → creator nhập mã từ hộp thư → đúng mã → pill chuyển "Đã xác minh".
3. **Gửi lại mã:** Creator không nhận được mã → chờ hết đếm ngược → bấm "Gửi lại mã" → nhận mã mới.

---

## Dependencies

### Internal Dependencies

- **Backend API xác thực email** — endpoint gửi OTP và endpoint verify OTP (hiện service frontend `src/services/user.ts` chưa có; cần backend cung cấp và frontend bổ sung lời gọi). Backend đã được xác nhận sẵn sàng phía cung cấp.
- **Field trạng thái xác minh trong user detail** — API user detail cần trả field thể hiện email đã xác minh (FR-006).
- **Trang Tài khoản** — `src/pages/account/components/form/index.tsx`, interface `src/interfaces/user.ts`.

### External Dependencies

- **Dịch vụ gửi email (đã có API key)** — dịch vụ gửi mã OTP tới hộp thư người dùng. Đây chính là dependency từng thiếu key khiến phải ẩn tính năng; nay đã sẵn sàng.

---

## Assumptions

- Backend đã hoặc sẽ cung cấp đầy đủ API gửi/verify OTP và field trạng thái xác minh trong user detail.
- Dịch vụ gửi email với key mới hoạt động ổn định (delivery rate đủ cao).
- Quy ước về độ dài mã OTP, thời gian hiệu lực, giới hạn thử và rate-limit gửi lại do backend quy định; frontend tuân theo.

---

## Out of Scope

- **Gate/chặn chức năng theo trạng thái email** — đợt này chỉ hiển thị trạng thái và cho phép xác minh, KHÔNG chặn bất kỳ chức năng nào theo email đã/chưa xác minh.
- **Xác minh số điện thoại** — phần điện thoại vẫn đang ẩn, không nằm trong phạm vi.
- **Thay đổi luồng đăng nhập/đăng ký** — không đụng tới.
- **Thiết kế lại backend OTP** — backend đã sẵn sàng; PRD này tập trung frontend.

---

## Open Questions

1. Field trạng thái xác minh email backend trả về tên chính xác là gì và nằm ở cấp nào (`emailVerified` ở root hay trong `info`)?
2. Endpoint gửi OTP và verify OTP đã tồn tại với contract cụ thể nào (URL, payload, response)? Có cần bổ sung vào `ApiConst` không?
3. Thông số chốt: thời gian hiệu lực OTP, độ dài mã, số lần thử tối đa, thời gian countdown gửi lại — lấy theo cấu hình backend nào?

---

## Approval & Sign-off

### Stakeholders

- Product Owner — Team vCreator
- Engineering Lead — vCreator frontend
- QA Lead — sinh test case từ FR/AC trong PRD này

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead
- [ ] Design Lead
- [ ] QA Lead

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 27/05/2026 | Team vCreator | Initial PRD — bật lại tính năng xác thực email |

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|-------------------|
| EPIC-001 | Hiển thị trạng thái xác minh email | FR-001, FR-006, FR-007 | 3-4 stories |
| EPIC-002 | Luồng xác thực OTP qua email | FR-002, FR-003, FR-004, FR-005, FR-008 | 4-6 stories |

---

## Appendix B: Prioritization Details

**Functional Requirements:** 8 tổng
- Must Have: 7 (FR-001 → FR-007)
- Should Have: 1 (FR-008)
- Could Have: 0

**Non-Functional Requirements:** 5 tổng
- Must Have: 2 (NFR-001, NFR-002)
- Should Have: 3 (NFR-003, NFR-004, NFR-005)

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**
