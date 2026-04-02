# Brainstorming: Budget + Ky Thanh Toan (Payment Cycle) — Gen-Green

**Date:** 2026-04-02
**Objective:** Thiet ke budget system cho Gen-Green khi event chay xuyen suot (khong co ngay ket thuc) va thanh toan tung dot (monthly/bi-weekly)
**Context:** Gen-Green khac Ambassador o cho: event thuong khong co ngay ket thuc, chay lien tuc, thanh toan tung ky. Cap tuyet doi (nhu Ambassador) khong phu hop vi se het som va creator mat dong luc. Can tim cach ket hop budget + ky thanh toan.

## Techniques Used
1. **Starbursting** — Phoi bay het complexity qua cau hoi 6W
2. **Reverse Brainstorming** — "Lam sao de that bai?" → lat nguoc thanh giai phap
3. **SCAMPER** — Bien doi tu Ambassador approach

---

## 1. Boi Canh Dac Biet Gen-Green

### Event chay xuyen suot
- Event co `EndAt` nhung thuc te nhieu event chay lien tuc (EndAt rat xa hoac duoc gia han)
- Khac Ambassador: event co thoi han ro rang (campaign 30-90 ngay)

### Thanh toan tung dot
- Admin tao Reconciliation voi `Conditions.FromAt → ToAt` (khoanh thoi gian)
- Khong co cycle co dinh — admin tao thu cong moi dot
- Flow: Crawl → Reward (pending) → Doi soat → Transfer → Rut tien

### 3 Model cap tu business (tu screenshot)

| Model | Don gia | Cap/Ky | Gioi han video |
|-------|---------|--------|----------------|
| **A** | 0.5d/view | Toi da 1 trieu view/video/ky | Khong gioi han so video |
| **B** | 10d/view | Toi da 1 trieu view/video/ky | Toi da 10 video/ky |
| **C** | 15d/view | Toi da 50 trieu VND/ky | Khong ro gioi han video |

### Cau hoi trung tam
> **"Cap gan theo ky thanh toan thi enforce luc nao? Luc Doi soat (Reconciliation) hay luc Thanh toan (Transfer)? Hay realtime luc crawl?"**

---

## 2. Starbursting — 6W Analysis

### WHO
- **Ai quyet dinh ky?** Hien tai: Admin (tao Reconciliation thu cong). Can: System (calendar-based)
- **Ai bi anh huong boi cap/ky?** Creator — cap reset → co them quota ky moi
- **Ai chiu rui ro tai chinh?** Doi tac — event vo han + cap/ky = tong chi co the vo han
- **Ai can nhin cap con lai?** Creator: "ky nay con kiem bao nhieu". Admin: "tong chi tat ca ky"

### WHAT
- **Cap theo gi?** View (Model A,B) hay tien (Model C) hay ca hai?
- **Ky thanh toan la gi chinh xac?** Calendar period? Khoang giua 2 lan doi soat? Custom?
- **"1 trieu view/video/ky" nghia la gi?** View tich luy tu luc dang? Hay chi delta view trong ky?

### WHEN
- **Enforce luc nao?** 3 thoi diem: (1) Realtime luc crawl, (2) Luc Doi soat, (3) Luc Transfer
- **Ky bat dau/ket thuc khi nao?** Calendar (1-30)? Admin quyet dinh? Auto?
- **View tinh cho ky nao?** Video dang ky truoc nhung view tang ky nay → tinh ky nao?

### WHERE
- **Cap luu o dau?** EventRaw (config event) + PaymentCycle entity moi?
- **Tracking "da dung trong ky" luu o dau?** Tinh realtime tu EventReward + date range (stateless)?
- **Ky thanh toan luu o dau?** Entity moi hay dung Reconciliation.Conditions?

### WHY
- **Tai sao can cap/ky thay vi cap tuyet doi?** Event chay vo han → cap tuyet doi het som → creator bo
- **Tai sao Model A cap view thay vi tien?** Don gian cho business: "1 trieu view" de hieu
- **Tai sao Model B gioi han so video?** Tranh spam 100 video rac de farm view

### HOW
- **Lam sao biet "ky hien tai"?** Neu admin chua tao Reconciliation?
- **Lam sao reset cap giua cac ky?** Stateless (tinh tu reward.date range) hay stateful (ghi used/ky)?
- **Lam sao handle ranh gioi ky?** Video crawl ngay 31 nhung ky chi den 30?

---

## 3. Reverse Brainstorming — "Lam sao de that bai?"

### Failure #1: Khong ai biet "ky" la gi
> Admin tao Reconciliation ngay 5/4 cho "1/3→31/3". Crawl ngay 1/4 tao reward date=1/4. Thuoc ky nao?

**→ Insight:** Ky phai la **system concept co dinh nghia ro rang**, khong phu thuoc Reconciliation.

### Failure #2: Enforce realtime nhung ky chua duoc tao
> Crawl ngay 1/4. Admin chua close ky 3. System khong biet ky moi bat dau chua.

**→ Insight:** Ky phai **calendar-based tu dong**, KHONG phu thuoc admin tao Reconciliation.

### Failure #3: Cap theo view nhung view tich luy qua nhieu ky
> Video 500k view ky 1. Ky 2 tang len 1.5M. Cap = 1M/video/ky. Ky 2 delta = 1M → vuot cap?

**→ Insight:** **Nen cap theo tien** (VND) vi tien = delta_view × don_gia, tu nhien gan voi ky. Cap theo view phuc tap hon.

### Failure #4: Enforce luc Doi soat → chi qua nhieu truoc do
> Crawl thoai mai. Cuoi thang doi soat → phat hien vuot cap → phai cat → creator khieu nai.

**→ Insight:** **Enforce phai cang som cang tot** (realtime/crawl). Doi soat chi confirm, khong enforce.

### Failure #5: Event vo han + cap/ky = tong chi vo han
> 12 thang × 5 trieu × 10,000 creator = 600 ty!

**→ Insight:** Van can **Bpe (tong budget event)** lam "van khoa cuoi cung". Cap/ky la "van dieu tiet".

### Failure #6: Creator khong biet ky reset khi nao
> Creator dat cap → dung dang video. Khong biet ky moi bat dau ngay nao.

**→ Insight:** Ky phai **hien thi ro rang**: "Ky 1/4→30/4. Da nhan 3/5 trieu. Reset 1/5."

---

## 4. SCAMPER — Bien doi tu Ambassador

### Substitute
Ambassador: cap tuyet doi → Gen-Green: cap **theo ky**
Ambassador: cashValid = sum all → Gen-Green: cashValid = sum **trong ky**

**Idea S1:** Giu 3 tang nhung them dimension "ky": Bpe_per_cycle, Bpu_per_cycle, Bpc_per_cycle

### Combine
**Idea C1:** Hai lop cap:
- `Bpe` (tong, KHONG reset) = van khoa cuoi
- `Bpu_cycle` / `Bpc_cycle` (theo ky, reset) = van dieu tiet

### Adapt
**Idea A1:** Tao entity **PaymentCycle** tren Event — config cycle type + start day. System tu tinh "ky hien tai".

### Modify
**Idea M1:** Admin cau hinh cap bang view, system **auto-convert sang tien** (view × cashPerView). Enforce bang tien. Hien thi cho creator bang view.

### Put to other uses
**Idea P1:** PaymentCycle auto-trigger Reconciliation khi ky ket thuc.

### Eliminate
**Idea E1:** Rolling window 30 ngay thay vi fixed cycle. `userCashInLast30Days <= Bpu`. Khong can PaymentCycle entity.

### Reverse
**Idea R1:** System suggest cap/ky: `total_budget / expected_cycles / expected_creators`.

---

## 5. Ba Approach Kha Thi

### Approach A: Fixed Cycle + Realtime Enforce ⭐ RECOMMENDED

```
Event Config:
  ├── Bpe: 500 trieu (tong budget, KHONG reset)
  ├── CycleType: "monthly" | "bi-weekly" | "custom"
  ├── CycleStartDay: 1
  └── Per-Cycle Caps:
        ├── Bpu_cycle: 5 trieu/creator/ky
        ├── Bpc_cycle: 2 trieu/video/ky
        └── MaxVideos_cycle: 10 video/ky (optional)
```

**Enforce:**
```
Crawl → Tinh ky hien tai (CycleType + ngay hom nay)
     → cashValid_cycle = sum(rewards trong ky nay)
     → Check: min(Bpe_remain, Bpu_cycle_remain, Bpc_cycle_remain)
     → Enforce
```

| Pro | Con |
|-----|-----|
| Enforce som, creator thay cap realtime | Can entity PaymentCycle moi |
| Bpe la van khoa cuoi | Phuc tap hon Ambassador |
| Calendar-based → khong phu thuoc admin | Ranh gioi ky can handle |
| Ho tro ca 3 model (A, B, C) | |

**Video xuyen ky:** Cap tinh tren **delta cash trong ky** (tu nhien vi reward ghi theo date).

### Approach B: Rolling Window + Realtime Enforce

```
Event Config:
  ├── Bpe: 500 trieu (tong)
  ├── WindowDays: 30
  └── Per-Window Caps:
        ├── Bpu_window: 5 trieu/creator/30 ngay
        └── Bpc_window: 2 trieu/video/30 ngay
```

| Pro | Con |
|-----|-----|
| Khong can ranh gioi ky | Creator kho hieu "30 ngay truot" |
| Khong phu thuoc calendar | Reconciliation khong align |
| Don gian concept | "Bao gio cap reset?" → khong ro |

### Approach C: Reconciliation-based Enforce

```
Crawl → Reward binh thuong (KHONG check cap)
Doi soat → Apply caps, cat reward vuot cap
```

| Pro | Con |
|-----|-----|
| Backend crawl khong thay doi | Creator thay tien roi bi cat → khieu nai |
| Align voi flow hien tai | Phat hien vuot budget muon |
| | Phu thuoc admin tao doi soat deu dan |

---

## 6. Key Insights

### Insight 1: "Enforce realtime, settle later"
**Impact:** Cao | **Effort:** Trung binh

Defer enforce toi doi soat = creator thay tien roi bi cat = drama. Enforce phai xay ra luc crawl. Doi soat chi confirm.

### Insight 2: "Cap theo tien, hien thi theo view"
**Impact:** Cao | **Effort:** Thap

Cap theo view phuc tap (view tich luy lien tuc). Cap theo tien tu nhien gan voi ky (cash = delta_view × don_gia). Admin cau hinh view → system convert thanh tien → enforce tien → hien thi view.

### Insight 3: "Can 2 lop cap — tong + ky"
**Impact:** Cao | **Effort:** Trung binh

Bpe (tong) = van khoa cuoi cung cho doi tac. Cap/ky = van dieu tiet cho phan bo deu. Ca hai deu can thiet.

### Insight 4: "Ky phai la system concept, khong phai hanh dong admin"
**Impact:** Cao | **Effort:** Trung binh

Ky calendar-based tu dong (monthly/bi-weekly). Reconciliation la hanh dong confirm cua admin, khong phai dinh nghia ky.

### Insight 5: "MaxVideos/ky la cap rieng biet"
**Impact:** Trung binh | **Effort:** Thap

Gioi han so video/ky (Model B) la quantity cap, khong phai budget cap. Da co precedent: EventSchemaQuantity. Extend thanh QuantityPerCycle.

### Insight 6: "Video xuyen ky → tinh delta trong ky"
**Impact:** Cao | **Effort:** Thap (quy uoc)

Video dang ky truoc, view tang ky nay. Cap tinh tren delta cash trong ky. Tu nhien vi EventReward.Date cho phep filter by date range.

---

## 7. Cau Hoi Can Tra Loi Truoc Khi Implement

1. **Ky co dinh hay flexible?** Monthly bat dau ngay 1? Hay admin chon ngay bat dau?
2. **Cap don vi gi?** Business muon cap view (Model A,B) hay tien (Model C) hay ca hai?
3. **Model B: gioi han so video — tat ca video hay chi video moi dang trong ky?**
4. **Bpe (tong budget) co can cho gen-green?** Hay chi can cap/ky la du?
5. **Khi creator dat cap ky — cho dang video khong?** (Ambassador: cho dang nhung khong tinh tien)
6. **Doi soat co bat buoc theo ky?** Hay admin van tao bat ky luc nao?

---

## 8. Recommended Next Steps

1. **Confirm approach voi Business:** Present 3 approaches, chon A/B/C
2. **Confirm 6 cau hoi o tren** voi Product Owner
3. **Viet PRD chi tiet** cho approach duoc chon (dua tren Ambassador PRD v2 + insights nay)
4. **Prototype PaymentCycle entity** va enforce flow

---

## Statistics
- Total ideas generated: 18
- Categories: 5 (Starbursting, Reverse, SCAMPER, Approaches, Insights)
- Key insights: 6
- Techniques applied: 3
- Approaches proposed: 3

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session date: 2026-04-02*
