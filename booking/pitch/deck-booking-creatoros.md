# PITCH DECK — Booking cho AccessTrade trên nền CreatorOS

> **Bản nháp v1 · 2026-07-22 · Người đọc: BIZ + TECH của AT (cùng buổi).**
> 🎤 = ghi chú người trình bày (**NỘI BỘ — xoá trước khi gửi bản PDF/slide cho AT**).
> Tag mỗi slide: 🟦 BIZ-weighted · 🟩 TECH-weighted · ⬜ cả hai.
> Kỷ luật: KHÔNG nói "gộp 3 hệ về 1" · KHÔNG "onboard ADV rẻ hơn" · KHÔNG dùng con số xây-lại như "giá trị".

---

## Slide 1 — Bìa ⬜

# Booking cho AccessTrade
### Làm được booking ngay — trên một nền đã sửa đúng chỗ hệ hiện tại đang vỡ.

*Diso · 2026*

> 🎤 Một câu, không hứa hẹn to. "Booking ngay" (biz) + "sửa chỗ đang vỡ" (tech) — cả hai cùng thấy phần của mình ngay từ bìa.

---

## Slide 2 — Diso đã đọc kỹ đề bài. Và booking KHÔNG phải "thêm một loại chiến dịch". ⬜

Booking chạm **4 tầng nền**, không phải một tính năng bề mặt:

| Tầng | Booking đòi gì |
|---|---|
| 💰 **Tiền** | Chốt giá riêng từng KOC · chi theo video/gói · phí phụ · đối soát đúng |
| 🎬 **Duyệt trước khi đăng** | Gửi demo → duyệt → mới cho e-clip (ngược với creator thường) |
| 📡 **Đa kênh + đàm phán** | Apply & duyệt theo từng kênh · admin final-giá |
| 🤝 **Agency / Vendor** | Pool KOC · khoán quota · hoa hồng · phạt vi phạm |

> **Vì chạm nền, booking không thể "làm nhanh cho xong" — nó đòi phần nền phải đúng trước.**

> 🎤 Đây là slide **chống commoditize**: chặn suy nghĩ "booking = thêm 1 campaign type, làm tuần là xong". Đặt kỳ vọng đúng cho cả scope lẫn giá. Nguồn: meeting 0714 với đội chị Vui.

---

## Slide 3 — Nỗi đau hôm nay: một nửa công sức mỗi tháng đang đi để ĐỨNG YÊN 🔥 ⬜

> ## ~50% workload mỗi tháng đổ vào **đối soát · cấn trừ · ngân sách** — không mua thêm một tính năng nào.

- 🟦 **Với kinh doanh:** file đối soát đưa **advertiser** bị sai → mất thời gian giải trình, rủi ro niềm tin với **người trả tiền**.
- 🟩 **Với kỹ thuật:** sửa chỗ này vỡ chỗ kia, không ai biết cho tới khi khách kêu — vì **gốc lỗi nằm ở nền**, không phải ở người.

> 🎤 Đây là **MỘT nỗi đau** của cả deck. Đừng thêm nỗi đau thứ hai ở đây. Con số 50% là do chính đội AT ước.

---

## Slide 4 — Vì sao KHÔNG thể vá trên hệ hiện tại 🟩

Không phải "code cũ" — là **3 lỗ ở nền**, càng vá càng vỡ:

| Lỗ nền | Vì sao vá không dứt | Hệ quả kinh doanh 🟦 |
|---|---|---|
| **Đối soát sai từ gốc** | Tiền & view lưu ở 2 nơi rời, hệ **chưa từng ràng** "1 đồng ↔ đúng view sinh ra nó" → sửa ở tầng report là **bất khả** | Số đưa advertiser mãi không khớp |
| **Cách ly ADV mong manh** | Phân biệt ADV bằng field ở tầng app — **một câu truy vấn quên điều kiện là rò dữ liệu ADV này sang ADV khác** | Rủi ro lộ dữ liệu khách |
| **Không tự động kiểm thử** | Không có lưới an toàn → mỗi lần sửa là **gieo xúc xắc** | Chậm, hay cháy, khó thêm cái mới |

> **Đổ booking — phần phức tạp tiền nhất — lên nền này = nhân nỗi đau lên, đúng chỗ đối diện khách.**

> 🎤 Slide **thuyết phục TECH** (việc move). Nói ở mức "nền", không sa đà thuật ngữ. Mỗi dòng có cột hệ quả để BIZ không rớt. Nếu tech hỏi sâu → có tài liệu kỹ thuật kèm.

---

## Slide 5 — CreatorOS: nền đã được dựng lại, sửa đúng 3 lỗ đó ⬜

Ba trụ giá trị:

| Trụ | Nghĩa | Bằng chứng |
|---|---|---|
| 💰 **Tiền đúng** | Mỗi dòng tiền **mang theo view sinh ra nó** → tổng tiền & tổng view đọc từ cùng dữ liệu → **không thể lệch** | Đối soát khớp by-construction |
| 🔒 **Khách an toàn** | Cách ly ADV ở **tầng dữ liệu** — hệ **từ chối** rò chéo, không dựa "lập trình viên nhớ" | Cách ly cưỡng chế |
| 🚀 **Ra nhanh + mở rộng** | Đổi nhà cung cấp / thêm năng lực = **cắm thêm, không đụng lõi** | Booking + vendor swap |

> **Scale vững chắc:** 1 nền code + **theme riêng từng ADV** → thêm ADV là thêm **cấu hình**, không nhân bản clone, không nhân chi phí bảo trì. Nền đa-tenant **đang chạy nhiều tenant thật**.

> **Không phải thiết kế trên giấy — nó đang chạy thật, và đo được.**

> 🎤 Chuyển từ "vấn đề" sang "lời giải". 3 trụ = phiên bản BIZ của các trục kỹ thuật. Giữ 3, đừng bày 5.

---

## Slide 6 — Booking cần gì → CreatorOS đáp ứng tới đâu 🟦

*(Đây là phần BIZ verify khả năng đáp ứng — nói thẳng cái đã có và cái phải xây)*

| Booking cần | Trạng thái | |
|---|---|---|
| Duyệt demo **trước khi đăng** | **Đã có** (đang chạy) | ✅ |
| Apply & duyệt **theo từng kênh** | **Đã có** | ✅ |
| Thể lệ **đóng băng** khi ADV đổi giữa chừng | **Đã có** | ✅ |
| Trao đổi creator ↔ người duyệt trên hệ thống | **Đã có** (thay Zalo) | ✅ |
| Nền tiền: sổ cái · ngân sách · giữ/chi | **Đã có** | ✅ |
| Chốt giá riêng từng KOC · chi theo gói · phí phụ | **Thêm lớp deal lên nền** | 🔨 |
| Agency / vendor (pool · quota · hoa hồng · phạt) | **Phase sau** (theo đề nghị hoãn của AT) | ⏭️ |

> **Phần khó (tiền + duyệt-trước-đăng) đã xong. Booking chỉ còn thêm lớp deal lên trên.**

> 🎤 Trung thực là vũ khí ở đây: nói rõ cái nào có / cái nào xây / cái nào hoãn. BIZ tin bảng dám ghi "phải xây" hơn bảng toàn ✅.

---

## Slide 7 — DEMO: không cần tin — nhìn ⬜ 🔥 *(đỉnh chung của cả hai bên)*

**Demo 1 — Đối soát khớp:** bộ dữ liệu **tái hiện đúng kiểu lệch tiền/view** → cách lưu cũ ra file **không khớp**, cùng dữ liệu đó qua CreatorOS ra file **khớp**. Đặt cạnh nhau.

**Demo 2 — Luồng booking chạy thật:** creator apply theo kênh → nộp demo → duyệt trước khi đăng → e-clip → nghiệm thu → chi.

> 🟦 BIZ thấy: **nó làm được việc.** 🟩 TECH thấy: **bằng chứng, không phải lời.**

> 🎤 Đây là khoảnh khắc thắng của cả deck. **Demo dùng dữ liệu của Diso** (kiểm soát được, không phụ thuộc AT chuẩn bị). Đòn "trên chính số của các anh" để dành **bước tiếp** (Slide 12) — mạnh hơn khi làm follow-up trên dữ liệu thật AT.

---

## Slide 8 — Vì sao move sang CreatorOS là move sang nền KHÔNG tái phát bug 🟩

*(Phần TECH cân nhắc "có đáng move không")*

- **1.184 kiểm thử tự động, chạy hết trong ~2 phút.**
- **15 "chốt kiến trúc" do máy tự canh** — quên bật cách ly, tính tiền sai chỗ, dùng dữ liệu ảo… đều bị chặn **trước khi lên**, không đợi review nhớ.
- Chạy trên **cơ sở dữ liệu thật, cách ly thật** — xanh trên máy = chạy được thật.
- **Bản cũ bug đi bug lại vì không thể auto-test. Bản này sửa xong là ở yên.**

> **Với đội quen nghiệm thu: "không cần tin tôi — clone về, chạy 2 phút."**

> 🎤 Slide này TECH tự gật. ⚠️ Nói thật: test **chưa chạy trong CI** (chặn ở bước push). Nếu tech hỏi → "đó là hạng mục cấu hình, không phải xây lại". Đừng nói "có CI test".

---

## Slide 9 — Triển khai KHÔNG rủi ro: booking trước, migrate sau ⬜

```
GĐ1: Booking chạy trên CreatorOS   ──►   GĐ2: Thấy ổn → migrate Ambassador sang
     (mới, không đụng Ambassador)          (đo được rồi mới cam kết chuyển)
```

- **GĐ1 không rủi ro:** booking là sân mới, hỏng cũng không đụng hệ đang chạy.
- **AT không phải TIN — chỉ cần NHÌN** nền chạy thật trên việc thật vài tháng.
- Booking chạy trên **chính cái nền tiền** sẽ dùng cho Ambassador → vài tháng đối soát khớp sạch **chính là bằng chứng** cho bước migrate.

> 🎤 Đây là điểm de-risk mạnh nhất cho cả 2 bên. Nhấn: **không đòi AT đặt cược tất cả.**

---

## Slide 10 — Cách hợp tác: về cùng một phía ⬜

Diso đề xuất **thuê nền**, không phải hợp đồng theo task — và đây là lý do **vì lợi ích của AT**, không phải của Diso.

**Hợp đồng theo task có một động cơ ngược, không ai muốn nhưng ai cũng dính:**
- Bên làm phải **khai task trước** → có task mới có tiền, hết task là hết tiền.
- Fix **rốt ráo** thì tháng sau hết việc; fix **nửa vời** thì còn task → **chữa cháy trở thành nguồn thu**, nên đám cháy **không bao giờ được dập hẳn**.
- Việc **chủ động** — hiểu nhu cầu kinh doanh, đề xuất cải tiến, làm cái mới — **không nằm trong task nào**, nên không xảy ra.

**Thuê nền lật ngược động cơ:**
- Diso được trả để **nền chạy tốt** → bug tái phát thành **chi phí của Diso**, không phải nguồn thu → **fix dứt điểm mới có lợi**.
- Nền càng tốt càng giữ được hợp đồng → Diso **chủ động cải tiến & tìm hiểu nhu cầu biz**, không đợi được giao task.

> **Trả theo task: bên làm lời khi việc KÉO DÀI. Trả theo nền: bên làm lời khi nền CHẠY TỐT.**
> Mô hình task thật ra **có lợi cho bên làm dịch vụ hơn** — nhưng nó không dập được đám cháy cho các anh. Diso đề xuất đổi sang mô hình mà **hai bên cùng thắng ở một chỗ: nền chạy tốt.**

> 🎤 **Slide tế nhị nhất — đọc kỹ giọng.** Nói *"hợp đồng theo task NÓI CHUNG có động cơ này"* — cấu trúc, KHÔNG "mô hình của các anh sai". Đòn tin cậy nằm ở việc Diso **tự nêu động cơ của chính mình** và tự nguyện rời mô hình đang có lợi cho mình. Nếu trong phòng có người lập ra mô hình hiện tại → giọng là "cùng nhìn ra", tuyệt đối không phán xét. Cân nhắc: slide này hợp **founder-to-founder / với người quyết**, có thể nhẹ tay hơn nếu phòng đông.

---

## Slide 11 — Thương mại: cùng mức chi, nhưng tiêu TỚI TRƯỚC 💰 ⬜

| Dòng chi/tháng | Hôm nay | GĐ1 (booking trước) | GĐ2 (migrate) |
|---|---|---|---|
| 2 hệ còn lại | 50m | 50m | 50m |
| **Dòng 80m** | vá hệ cũ | vá hệ cũ | **thuê nền mới** |
| Booking | — | 50m | 50m |
| **Tổng** | 130m | **180m** | **180m** |

> **Dòng 80m của các anh không tăng một đồng — chỉ đổi từ *vá cái cũ* sang *thuê cái mới*, và chỉ đổi khi thấy ổn.**

- Tiền **mới** duy nhất: **50m cho booking** — thứ hôm nay **chưa làm được**.
- So cách làm cũ (vá hệ cũ + tự dựng booking ≈ 250m): **rẻ hơn ~70m/tháng.**

**Phí khởi tạo một lần: 500m** (Diso gánh toàn bộ chi phí phát triển — vài sprint) — **chia 3 đợt theo cam kết, trả tới đâu giao tới đó:**

| Đợt | Mốc | Số |
|---|---|---|
| 1 | Khởi động (nối SSO/eKYC/cổng chi AT, dựng nền) | **200m** |
| 2 | **Booking chạy được** | **150m** |
| 3 | **Migrate Ambassador xong** | **150m** |

> Đợt 3 chỉ trả **khi migrate thật sự xong** → AT không đặt cược trước cho việc chưa chắc chạy.

> 🎤 180m/tháng là **đích**, không phải điểm mở — đừng tự hạ dưới. 500m phí khởi tạo tách 3 đợt bám đúng 3 mốc cam kết. "Gồm gì / chưa gồm gì" (số tenant, SLA, số yêu cầu đổi/tháng) để phụ lục B.

---

## Slide 12 — Bước tiếp ⬜

1. **AT đưa dữ liệu THẬT của họ** → Diso tái chạy đối soát **trên chính số của AT**, chứng minh nó khớp (follow-up sau buổi).
2. Chốt phạm vi **GĐ1 (booking)** + timeline go-live.
3. Đặt **mốc đánh giá** để quyết migrate Ambassador (vd sau 6 tháng chạy booking).

> 🎤 Kết bằng hành động nhỏ, đo được — không đòi cam kết lớn ngay. Điểm 1 là đòn "tự kiểm trên số của chính các anh" — mạnh hơn khi để làm follow-up, vì lúc đó đã có thời gian lấy dữ liệu thật.

---

## Phụ lục (chỉ mở khi được hỏi sâu)

- **A. Kỹ thuật** (cho TECH): cơ chế đối soát khớp by-construction · cách ly tầng dữ liệu · danh sách 15 chốt kiến trúc · hạ tầng test đo 9,4×.
- **B. Ma trận limit** (cho BIZ/hợp đồng): số tenant trong 80m · SLA · số yêu cầu thay đổi/tháng · phạm vi bảo trì vs nâng cấp.
- **C. Phí khởi tạo chi tiết**: KT-1 (nối 3 dịch vụ AT + go-live booking) · KT-2 (migrate + chuyển dữ liệu).
- **D. Nợ đã biết & kế hoạch**: hạng mục social-accounts cần nâng trước migrate · cấn-trừ tự động là hạng mục build.

> 🎤 Phụ lục để **thủ**, không bày. Chỉ rút ra khi bị hỏi đúng chỗ. D là phần **chủ động khai nợ** — nếu bị hỏi "có gì chưa xong không", mở D ra là ghi điểm minh bạch.
