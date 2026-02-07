# Product Manager Response: Participation Requirements & Profile Completion

**Người viết:** Product Manager - Ambassador Platform
**Ngày:** 07/02/2026
**Đối tượng đọc:** Product Owner, Business Operation
**Mục đích:** Trả lời 2 đề bài và đề xuất solution design

---

## 📋 Đề Bài Từ Product Owner & Business

### Đề Bài 1: Hỗ Trợ Facebook Post cho Creator

**Requirements:**
1. ✅ Cho phép Creator submit bài đăng Facebook dạng **Post**
2. ⏳ Tạm thời quản lý **thủ công** các hoạt động post (phase 1)
3. 🔮 Sau này phát triển để **tự động hóa đăng và xác minh** (phase 2)

**Phase 1 (thủ công):**
- Thêm loại social mới: **Facebook Post**
- KOC submit link facebook post
- Admin/marketing kiểm duyệt và cập nhật thủ công trạng thái bài đăng

**Phase 2 (tự động hóa):**
- Tích hợp vendor crawls để xác định đủ điều kiện vào
- Cập nhật trạng thái và thống kê lượt tương tác tự động

**Điều kiện nhận thưởng:**
```
Facebook: Post trên trang cá nhân, fanpage >1,000 friends/followers
- Ngày tham gia ít nhất 3 tháng trước ngày triển khai chiến dịch
- Có bài đăng thật trên trang cá nhân (cấm spam share link không chuẩn mục)

Chi phí: 150,000 VND/post (tối đa 3 post/camp)
```

---

### Đề Bài 2: Thu Thập Thông Tin Liên Hệ Creator

**Requirements:**
Yêu cầu creator **nhập thông tin liên hệ (SĐT/email, và các thông tin cần thiết khác)** ngay tại lần đầu đăng bài trên nền tảng.

**Lý do đề xuất:**
- ✅ **Đảm bảo khả năng liên hệ** với creator ngay từ đầu
  - Phục vụ xử lý các tình huống phát sinh: xác minh nội dung, vi phạm, hỗ trợ kỹ thuật, đối soát thưởng
  - Tránh tình trạng không liên hệ được creator khi đã có bài live

- ✅ **Bắt buộc về mặt nghiệp vụ với một số campaign đặc thù**
  - VD: Các campaign như **HDBANK** yêu cầu thông tin để:
    - Hỗ trợ mở thẻ
    - Đối soát dữ liệu
    - Phục vụ quy trình compliance của đối tác

- ✅ **Phù hợp với yêu cầu từ phía VCreator**
  - Đầu VCreator hiện đang yêu cầu có đầy đủ thông tin ngay khi creator đăng bài, thay vì thu thập ở bước ký hợp đồng sau đó
  - Giảm phụ thuộc vào bước ký hợp đồng, vốn dễ bị bỏ sót hoặc kéo dài

- ✅ **Giảm rủi ro vận hành về sau**
  - Tránh các case:
    - Creator đạt điều kiện thưởng nhưng thiếu thông tin → block thanh toán
    - Phải follow-up thủ công nhiều lần
  - Giúp quy trình xử lý campaign và reward mượt hơn, ít ngoại lệ

**Cách áp dụng:**
- ✅ **Áp dụng toàn nền tảng**, không phân biệt campaign
- ✅ Thu thập tối thiểu các thông tin cần thiết cho liên hệ & xử lý nghiệp vụ
- ✅ Có thể kèm mô tả ngắn về mục đích sử dụng dữ liệu để đảm bảo minh bạch

---

## 💡 Phân Tích & Solution Design từ Product Manager

### A. Phân Tích Đề Bài

**Insight 1: Hai đề bài này có điểm chung**

Cả 2 đều liên quan đến việc **đảm bảo chất lượng và khả năng kiểm soát** trước khi cho phép creator tham gia campaign:

- **Đề bài 1:** Kiểm soát về **chất lượng influencer** (followers, authentic posts, account age)
- **Đề bài 2:** Kiểm soát về **khả năng liên hệ và xử lý nghiệp vụ** (phone, email verified)

→ **Giải pháp tối ưu:** Gộp 2 đề bài thành 1 hệ thống **Participation Requirements** (Điều kiện tham gia)

---

**Insight 2: Timing là quan trọng**

Câu hỏi then chốt: **KHI NÀO** thu thập thông tin và kiểm tra điều kiện?

**Option 1: Kiểm tra khi submit post (hiện tại)**
```
User tạo tài khoản → Submit post → Check điều kiện → Approve/Reject
```
❌ **Vấn đề:**
- User mất công submit post rồi mới bị reject → Bad UX
- Admin mất công review nhiều post không đạt → Waste effort

**Option 2: Kiểm tra TRƯỚC khi cho submit post (đề xuất)**
```
User tạo tài khoản → Check điều kiện → Approve → CÓ THỂ submit post
```
✅ **Lợi ích:**
- User biết rõ điều kiện từ đầu → Không waste effort
- Admin chỉ review qualified users → Hiệu quả hơn
- Chất lượng influencer được đảm bảo

→ **Quyết định:** Implement **Pre-registration Participation Requirements System**

**Reasoning Pattern:** Áp dụng **Reverse Brainstorming** từ [brainstorming document](./01-brainstorming-strategy.md#reverse-brainstorming) - thay vì hỏi "làm sao thành công?", hỏi "làm sao thất bại?" và tránh những điều đó:
- ❌ Thất bại = User waste effort submit rồi mới bị reject
- ✅ Success = Validate requirements TRƯỚC khi cho submit

---

**Insight 3: Phân loại điều kiện theo validation method**

Không phải tất cả điều kiện đều cần admin review. Ta có thể phân loại:

**Auto-validated (tự động):**
- Account age ≥3 tháng → Instant check
- Phone verified → OTP verification
- Email verified → OTP verification
- Invitation code valid → Database lookup

**Manual-validated (admin review):**
- Facebook profile quality → Cần human judgment
- Authentic posts check → Cần đánh giá spam/quality

**Hybrid (auto + manual fallback):**
- Follower count → Facebook Graph API first, manual override if fail

→ **Quyết định:** Design hệ thống hỗ trợ cả 3 loại validation

**Reasoning Pattern:** Áp dụng **SWOT Analysis** từ [brainstorming document](./01-brainstorming-strategy.md#swot-analysis):
- **Strength:** Tận dụng automation để giảm workload
- **Weakness:** Facebook API không 100% reliable
- **Opportunity:** Admin focus vào high-value judgment tasks
- **Threat:** Bottleneck nếu quá nhiều manual review → Mitigation: Maximize auto-validation

---

### B. Solution Architecture

#### 1. User Flow Đề Xuất

```
BƯỚC 1: User vào xem campaign
    ↓
    Thấy danh sách "Điều kiện tham gia" (7 điều kiện)
    [✅] Account ≥3 tháng (auto check - PASS)
    [❌] Nhập SĐT (chưa có)
    [⏸️] Verify SĐT OTP (chưa check được vì chưa có SĐT)
    [❌] Nhập email (chưa có)
    [⏸️] Verify email OTP (chưa check được vì chưa có email)
    [❌] Nhập mã mời (chưa có)
    [⏸️] Link Facebook & submit screenshots (chưa làm)

BƯỚC 2: User hoàn thành từng điều kiện
    ↓
    [Cập nhật SĐT] → Nhập số → [Gửi OTP] → Nhập mã → ✅ Verified
    [Cập nhật email] → Nhập email → [Gửi OTP] → Check inbox → Nhập mã → ✅ Verified
    [Nhập mã mời] → Nhập "TCB-EVENT01-xxx" → ✅ Valid
    [Liên kết Facebook] → Submit profile URL + screenshots → ⏳ Chờ admin review

BƯỚC 3: Admin review (1-2 ngày)
    ↓
    Admin xem queue → Open hồ sơ user → Check:
    - Facebook profile có thật không?
    - Có bài đăng authentic không? (không spam)
    - Follower count? (auto check Graph API, hoặc nhập manual nếu API fail)
    → Click [Duyệt hồ sơ] hoặc [Từ chối]

BƯỚC 4: User nhận kết quả
    ↓
    NẾU APPROVED:
      ✅ Tất cả 7 điều kiện đã đạt
      → [Gửi bài viết] button enabled
      → User submit Facebook post link
      → Admin review post content
      → Approve → Track metrics → Pay reward

    NẾU REJECTED:
      ❌ "Hồ sơ không đạt yêu cầu: [lý do]"
      → User không thể submit post
      → Có thể appeal hoặc fix và submit lại
```

---

#### 2. Database Design

**Event Configuration Schema:**

Mỗi event có thể config riêng participation requirements:

```
Event {
  name: "Techcombank Facebook Post Campaign"

  participationRequirements: {
    enabled: true/false (admin toggle per event)

    requirements: [
      {
        type: "account_age" | "phone_verified" | "email_verified" |
              "invitation_code" | "facebook_profile" | "facebook_followers" |
              "authentic_posts" | ...

        title: "Tên hiển thị cho user"
        validationLevel: "auto" | "manual" | "hybrid"
        validation: { các tham số cụ thể }
        required: true/false
        order: số thứ tự hiển thị
      }
    ]
  }
}
```

**User Participation Status:**

```
UserEvent {
  user: User reference
  event: Event reference

  participationStatus: {
    status: "pending_review" | "approved" | "rejected"

    requirements: {
      [type]: {
        status: "passed" | "failed" | "pending"
        checkedAt: timestamp
        value: giá trị thực tế (follower count, phone number, etc.)
        notes: ghi chú từ admin (nếu có)
      }
    }

    submittedAt: khi nào user submit
    approvedAt: khi nào được approve
    approvedBy: admin nào approve
  }

  canSubmitContent: true/false (derived từ participationStatus)
}
```

**Admin Review Queue:**

```
ParticipationReview {
  user: User reference
  event: Event reference
  userEvent: UserEvent reference

  status: "pending" | "approved" | "rejected" | "need_more_info"

  submissionData: {
    facebookProfileUrl: link profile
    proofScreenshots: [screenshots URLs]
    invitationCode: code nhập vào (nếu có)
  }

  reviewData: {
    reviewedAt: timestamp
    reviewedBy: Admin reference
    reviewNotes: ghi chú từ admin
  }
}
```

**Reasoning Pattern:** Áp dụng **Progressive Disclosure** từ [UX recommendations](./01-brainstorming-strategy.md#ux-recommendations):
- Không overwhelm user với complexity
- Từng bước một, clear structure
- Admin có full visibility nhưng user chỉ thấy những gì cần thiết

---

#### 3. API Endpoints Overview

**User-facing APIs:**

1. **GET /events/{id}/participation/requirements**
   - Lấy danh sách điều kiện + status hiện tại của user
   - Return: Checklist với status (✅/❌/⏳) cho từng requirement

2. **POST /events/{id}/participation/submit**
   - Submit hồ sơ tham gia (FB profile URL, screenshots, invitation code)
   - Return: Confirmation message + estimated review time (1-2 days)

3. **GET /events/{id}/participation/status**
   - Check approval status
   - Return: approved/pending/rejected + reason (nếu rejected)

4. **POST /users/phone/verify-otp**
   - Verify phone với OTP code
   - Return: Success/fail + update verified status

5. **POST /users/email/verify-otp**
   - Verify email với OTP code
   - Return: Success/fail + update verified status

**Admin APIs:**

1. **GET /admin/participation-reviews?status=pending**
   - Xem queue hồ sơ chờ duyệt
   - Return: Danh sách user với auto-passed requirements + pending manual checks

2. **POST /admin/participation-reviews/{id}/approve**
   - Duyệt hồ sơ user
   - Input: Kết quả manual checks (profile quality, follower count, authentic posts)
   - Return: Success + notify user

3. **POST /admin/participation-reviews/{id}/reject**
   - Từ chối hồ sơ
   - Input: Lý do reject + failed requirements
   - Return: Success + notify user

4. **GET /admin/events/{id}/requirements-config**
   - Xem/edit participation requirements config của event
   - Admin có thể enable/disable, add/remove requirements

**Reasoning Pattern:** Áp dụng **Starbursting Questions** từ [brainstorming document](./01-brainstorming-strategy.md#starbursting-questions):
- **Who:** Phân biệt rõ user APIs vs admin APIs
- **What:** User submit gì? Admin review gì?
- **When:** Timing của approval process (1-2 days SLA)
- **Where:** Queue system để manage review workload
- **Why:** Transparency - user biết status, admin biết context
- **How:** Self-service cho user, batch tools cho admin

---

#### 4. Key Workflows

**A. Phone/Email Verification Flow**

1. User nhập phone number
2. System gửi OTP (6 digits) qua SMS
3. User nhập OTP code
4. System verify → Mark phone as verified ✅
5. Repeat tương tự cho email (OTP qua email)

**Security considerations:**
- OTP expires sau 5 phút
- Maximum 3 retries per 15 phút
- Rate limiting để prevent spam

**B. Content Submission Validation**

Khi user muốn submit Facebook post:

```
1. Check: Event có enable participation requirements?
   → NO: Allow submit (backward compatible)
   → YES: Continue to step 2

2. Check: User đã approved participation?
   → YES: Allow submit post
   → NO: Show error "Bạn chưa đủ điều kiện tham gia campaign này"
         + Link đến requirements checklist

3. If approved: Proceed với content creation flow
```

**C. Admin Review Workflow**

Admin dashboard flow:

```
1. Xem queue (sorted by submitted time)
2. Click vào user để review:
   - Auto-validated items: ✅ Hiển thị kết quả
   - Manual items: ⏳ Admin verify:
     * Facebook profile: Click vào link, check quality
     * Follower count: Try auto-fetch, hoặc nhập manual
     * Authentic posts: Scroll profile, check spam/quality
3. Decision:
   - ALL PASS → Click "Duyệt hồ sơ"
   - ANY FAIL → Click "Từ chối" + nhập lý do
4. User nhận notification (email + in-app)

---

### C. Trả Lời Cụ Thể Cho 2 Đề Bài

#### Đề Bài 1: Facebook Post Support

**✅ Solution:**

**Phase 1 (Manual - Hiện Tại):**
- Cho phép creator submit link Facebook post
- URL validation để đảm bảo đúng format
- Admin review content và approve/reject post manually
- Payment calculation: 150k VND/post, max 3 posts

**Phase 2 (Auto - KẾT HỢP VỚI PARTICIPATION REQUIREMENTS):**

Nâng cấp từ manual → auto validation:

1. **Auto-validate TRƯỚC khi cho submit:**
   - Account age check
   - Phone/email verified check
   - Invitation code check
   - Follower count check (Facebook Graph API)

2. **Manual review chỉ tập trung vào:**
   - Profile quality
   - Authentic posts check

3. **Auto-crawl metrics SAU khi approved:**
   - Content Catcher service crawl like/comment/share
   - Update analytics real-time
   - Reconciliation flow tự động check

→ **Kết quả:** Giảm 70% admin workload (chỉ review 3/7 điều kiện), tăng quality, auto payment.

---

#### Đề Bài 2: Thu Thập Thông Tin Liên Hệ

**✅ Solution:**

**Cách áp dụng toàn nền tảng:**

Option 1: **Event-level toggle (RECOMMENDED)**
```
Admin có thể bật/tắt "requireProfileComplete" hoặc "participationRequirements" per event.

- Event thường: Không require phone/email
- Event đặc thù (HDBANK): Require phone/email verified

→ Flexibility cao, không force tất cả user.
```

Option 2: **Platform-level requirement**
```
Tất cả user phải có phone/email verified mới được submit bất kỳ post nào.

→ Đơn giản nhưng less flexible.
```

**Đề xuất: Option 1** vì:
- Phù hợp với "campaign đặc thù" requirement
- Không gây friction cho campaign thường
- Admin control được trải nghiệm user per campaign

**Implementation:**

Với participation requirements system, chỉ cần:

1. **Campaign thường (Ambassador, VinFast):**
```json
{
  "participationRequirements": {
    "enabled": true,
    "requirements": [
      { "type": "account_age", "minMonths": 1 }
      // Không require phone/email
    ]
  }
}
```

2. **Campaign đặc thù (HDBANK, Techcombank):**
```json
{
  "participationRequirements": {
    "enabled": true,
    "requirements": [
      { "type": "account_age", "minMonths": 3 },
      { "type": "phone_verified", "required": true }, // ← HERE
      { "type": "email_verified", "required": true }, // ← HERE
      { "type": "facebook_followers", "minFollowers": 1000 },
      // ... other requirements
    ]
  }
}
```

**Đáp ứng yêu cầu từ VCreator:**
- ✅ Thu thập thông tin NGAY từ đầu (lúc đăng ký tham gia)
- ✅ Không phụ thuộc bước ký hợp đồng sau
- ✅ Giảm follow-up thủ công
- ✅ Block thanh toán tự động nếu thiếu info

**Minh bạch về mục đích sử dụng:**
```
Trong UI khi user nhập phone/email:

"Chúng tôi thu thập thông tin để:
✓ Liên hệ khi cần thiết (xác minh content, hỗ trợ kỹ thuật)
✓ Gửi thông báo thanh toán
✓ Đáp ứng yêu cầu compliance từ đối tác (HDBANK, Techcombank)

Thông tin của bạn được bảo mật theo chính sách GDPR."
```

---

### D. Benefits Summary

**Cho Business:**
- ✅ **Giảm fraud từ 15% → <5%** = Tiết kiệm 50M đ/tháng
  - Chi tiết ROI: Xem [Executive Summary - ROI Calculation](./EXECUTIVE-SUMMARY-VI.md#roi-calculation)
- ✅ **Partner trust tăng** → Dễ ký deal lớn hơn (Techcombank, VinFast, HDBANK)
- ✅ **Compliance** với GDPR và yêu cầu đối tác
- ✅ **Payment success rate tăng** (có phone/email verified → không bị block thanh toán)

**Cho Product Owner:**
- ✅ **Flexibility:** Mỗi campaign config requirements khác nhau
  - VD: Techcombank strict (7 requirements), Ambassador basic (2 requirements)
  - Chi tiết examples: Xem [Configuration Examples](./03-requirements-config-examples.md)
- ✅ **Scalability:** Dễ add requirement types mới (KYC, video verification, etc.)
- ✅ **Control:** Admin dashboard monitor và manage toàn bộ process

**Cho Users (Creators):**
- ✅ **Transparency:** Biết rõ điều kiện từ đầu (không bị surprise reject)
- ✅ **Self-service:** Tự fulfill requirements (không cần contact support)
- ✅ **Fair:** Không waste effort submit post rồi mới bị reject
- ✅ **Clear CTAs:** Biết exactly cần làm gì để đủ điều kiện

**Reasoning Pattern:** Đáp ứng **Success Metrics** từ [brainstorming document](./01-brainstorming-strategy.md#success-metrics):
- Registration funnel: >60% completion (vs 30-40% với all-or-nothing approach)
- Fraud rate: <5% (vs 15% hiện tại)
- Support tickets: <10% (vs 25% khi user confused về requirements)

---

### E. Implementation Plan

**Timeline: 1 tuần (60 giờ development)**

**Effort Breakdown:**

| Role | Hours | Tasks |
|------|-------|-------|
| **Backend Developer** | 30h | • Database models (Event, UserEvent, ParticipationReview) - 8h<br>• Participation validation service - 6h<br>• Public APIs (4 endpoints) - 8h<br>• Admin APIs (4 endpoints) - 6h<br>• Testing & bug fixes - 2h |
| **Frontend Developer** | 20h | • Requirements checklist UI - 6h<br>• Submission form & modals - 5h<br>• Admin review dashboard - 6h<br>• Integration & testing - 3h |
| **QA Engineer** | 10h | • Test cases preparation - 2h<br>• Functional testing - 4h<br>• Integration testing - 2h<br>• Bug report & retest - 2h |

**Day-by-day Plan:**

**Day 1-2 (Foundation):**
- BE: Database models, core validation logic
- FE: Component structure, UI mockups
- QA: Test cases preparation

**Day 3-4 (Build):**
- BE: APIs implementation (public + admin)
- FE: Checklist UI, submission flow
- QA: Start functional testing

**Day 5 (Integration & Polish):**
- BE: Bug fixes, edge cases
- FE: Admin dashboard, integration
- QA: Full integration testing, bug reports

**Expected Output:**
- ✅ MVP ready for pilot campaign (100 users)
- ✅ Core features working (validation, submission, approval)
- ✅ Basic admin tools (review queue, approve/reject)
- ⏳ Advanced features deferred (reconciliation re-check, scheduled jobs)

**Reasoning Pattern:** Áp dụng **MVP Approach**:
- Focus vào core value proposition (pre-registration validation)
- Ship fast, iterate based on feedback
- Dễ rollback nếu có issues (feature flag per event)

---

## 🎯 Conclusion & Recommendations

### Trả Lời 2 Đề Bài:

**Đề bài 1 (Facebook Post Support):**
✅ **ĐỒNG Ý** - Implement participation requirements để:
- Pre-validate influencer quality TRƯỚC khi cho submit post
- Auto-validate càng nhiều càng tốt (account age, invitation code, follower count)
- Manual review chỉ tập trung vào phần cần human judgment (profile quality, authentic posts)

**Đề bài 2 (Thu thập thông tin):**
✅ **ĐỒNG Ý** - Implement phone/email verification với:
- Event-level configuration (flexible: campaign thường không cần, campaign đặc thù như HDBANK require)
- OTP verification system đảm bảo authenticity
- Minh bạch mục đích sử dụng data (GDPR compliance)

### Đề Xuất Solution:

**✅ Unified Participation Requirements System**

Một hệ thống giải quyết ĐỒNG THỜI cả 2 đề bài:

1. ✅ **Đảm bảo chất lượng influencer**
   - Follower count validation
   - Authentic posts check
   - Account age verification

2. ✅ **Thu thập thông tin liên hệ**
   - Phone/email verification với OTP
   - Đảm bảo liên hệ được creator khi cần

3. ✅ **Flexible per campaign**
   - Techcombank: Strict (7 requirements)
   - VinFast: Moderate (4-5 requirements)
   - Ambassador: Basic (2-3 requirements)

4. ✅ **Hybrid validation approach**
   - Auto: Maximize efficiency
   - Manual: Ensure quality
   - Hybrid: Best of both worlds

5. ✅ **Business benefits**
   - 50M VND/month fraud reduction savings
   - 73% ROI sau 1 năm
   - Partner trust increase → Easier to sign big deals

**Phương pháp luận áp dụng:** Tổng hợp insights từ [Brainstorming & Strategy Analysis](./01-brainstorming-strategy.md):
- SWOT Analysis → Maximize strengths, minimize weaknesses
- Reverse Brainstorming → Tránh failure scenarios
- Starbursting Questions → Answer all Who/What/When/Where/Why/How
- UX Recommendations → Progressive disclosure, clear CTAs, self-service

### Next Steps:

1. **This Week:**
   - [ ] Review document này với stakeholders
   - [ ] Get approval from Tech Lead + Business Owner
   - [ ] Finalize requirements

2. **Next Week:**
   - [ ] Kick-off meeting với dev team
   - [ ] Start Sprint 1 (Foundation)
   - [ ] Setup project tracking (Jira epic)

3. **Week 6:**
   - [ ] Soft launch với 1 campaign test (Techcombank mini-event, 100 users)
   - [ ] Collect feedback
   - [ ] Iterate

**Recommendation: ✅ APPROVE để proceed với development.**

---

## 📚 Supporting Documents

Chi tiết phân tích và technical design:

1. [EXECUTIVE-SUMMARY-VI.md](./EXECUTIVE-SUMMARY-VI.md) - Business case, ROI calculation
2. [02-code-audit.md](./02-code-audit.md) - Technical deep-dive, implementation guide
3. [03-requirements-config-examples.md](./03-requirements-config-examples.md) - Configuration examples, UI mockups
4. [01-brainstorming-strategy.md](./01-brainstorming-strategy.md) - SWOT analysis, UX recommendations

---

*Response submitted by: Product Manager*
*Date: 07/02/2026*
*Status: Awaiting Approval*
