# SCAMPER Analysis: Fraud Detection cho TCB Creator Platform

**Ngay:** 2026-03-01
**Phuong phap:** SCAMPER Framework (Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse)
**Context:** TCB Creator - Influencer Marketing Platform cua Techcombank
**Dua tren:** brainstorming-fraud-detection-solutions-2026-02-08.md, feasibility-analysis-fraud-detection-2026-02-09.md

---

## MUC LUC

1. [S - Substitute (Thay The)](#s---substitute-thay-the)
2. [C - Combine (Ket Hop)](#c---combine-ket-hop)
3. [A - Adapt (Thich Nghi)](#a---adapt-thich-nghi)
4. [M - Modify/Magnify (Phong Dai)](#m---modifymagnify-phong-dai)
5. [P - Put to Other Uses (Lam Dung)](#p---put-to-other-uses-lam-dung)
6. [E - Eliminate (Loai Bo)](#e---eliminate-loai-bo)
7. [R - Reverse (Dao Nguoc)](#r---reverse-dao-nguoc)
8. [Tong Hop va Khuyen Nghi](#tong-hop-va-khuyen-nghi)

---

## HE THONG HIEN TAI - ATTACK SURFACE

Truoc khi phan tich SCAMPER, can hieu ro cac diem yeu cua he thong:

```
TCB Creator Attack Surface:
============================================
1. Reward Engine:
   - by-statistic: X views = Y tien (CPV model)
   - by-content-milestone: Video thu N duoc bonus
   - by-view-milestone: Dat 1M views bonus %

2. Content Sources (9 platforms):
   - TikTok, YouTube, YouTube Shorts
   - Facebook, Facebook Reels
   - Instagram, Instagram Reels
   - Threads, Shopee

3. Auto-Reject Conditions:
   - min-view, content-age, engagement, comment, like

4. Reconciliation Flow:
   - Processing -> Processed -> (manual review) -> Completed
   - 3 loai: event-reward, event-reward-statistic, event-reward-milestone

5. Content Flow:
   - waiting_approved -> approved/rejected
   - ContentAdjustView: positive/negative (manual adjustment)

6. Budget Thresholds: 75%, 95%, 100%
```

---

## S - SUBSTITUTE (THAY THE)

> Ke gian lan co the THAY THE yeu to that bang yeu to gia de qua mat he thong?

### S1. Thay the Real Views bang Purchased/Bot Views

**Mo ta:** Creator mua views tu dich vu bot farm (Indonesia, Philippines, India) de tang so luong views va nhan thuong theo CPV model.

**Muc do rui ro:** **CRITICAL**

**Cach thuc:**
- Mua views tu SMM panels (gia: $1-5 per 1,000 views)
- Su dung bot farms voi rotating IPs va device emulation
- Advanced bots ho tro proxy settings va user-agent randomisation

**Detection Signals:**
- View velocity bat thuong: >50K views/gio cho TikTok, >30K cho Facebook
- Engagement rate cuc thap: views cao nhung likes/comments < 0.5%
- Watch time phan bo bat thuong: bot views cluster tai 0% hoac 100% thay vi bell-curve 20-80%
- Geographic anomaly: 80%+ views tu 1 quoc gia khong phai VN
- Traffic source 100% direct, khong organic discovery
- Step-function growth: nhay dot ngot thay vi tang dan

**Ap dung vao TCB Creator:**
- Rule `by-statistic` (X views = Y tien) la muc tieu chinh
- Auto-reject condition `min-view` co the bi bypass neu bot views vuot threshold
- `ContentAdjustView.Positive` co the bi exploit neu staff bi social engineering

---

### S2. Thay the Original Content bang Stolen/AI-Generated Content

**Mo ta:** Creator su dung noi dung lay cap tu nguoi khac hoac dung AI tao content de tiet kiem cong suc nhung van nhan thuong.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Download viral video tu creator khac, re-upload voi chinh sua nho
- Dung AI tools (Sora, Runway, CapCut AI) tao video tu template
- Lay noi dung tu thi truong nuoc ngoai, dich va dang lai
- Re-upload video cu cua chinh minh (content recycling)
- Ghep nhieu clip ngan tu nhieu nguon thanh 1 video

**Detection Signals:**
- Video da ton tai truoc campaign start date
- Content hash matching voi database noi dung co
- Reverse image/video search co ket qua trung
- Brand mention khong tu nhien (text overlay them sau)
- AI content artifacts: lip-sync khong khop, anh sang bat thuong
- Engagement pattern cua recycled content khac fresh content

**Ap dung vao TCB Creator:**
- `by-content-milestone` thuong cho video thu N -> dong luc tao content "rac" de dat milestone
- Khong co content originality check hien tai
- Transcript analysis (hien co `TranscriptStatus`) co the mo rong de detect

---

### S3. Thay the Real Identity bang Fake/Multiple Identities

**Mo ta:** Mot nguoi tao nhieu tai khoan voi danh tinh gia de nhan thuong nhieu lan tu cung 1 campaign.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Tao nhieu tai khoan voi ten, email, SDT khac nhau
- Muon CCCD/CMND cua nguoi khac de xac minh
- Dung virtual phone numbers va temporary emails
- Tao nhieu profile social media (TikTok, Facebook) gia

**Detection Signals:**
- Cung bank account tren nhieu creator profiles
- Cung IP address cho submissions
- Cung device fingerprint
- Phong cach noi dung giong nhau (dia diem quay, giong noi, style)
- Thoi gian submit trung nhau
- So dien thoai cung dai mang/cung prefix
- Anh CCCD co dau hieu chinh sua

**Ap dung vao TCB Creator:**
- `IdentificationStatusApproved` chi check 1 lan, khong cross-check giua accounts
- `EventRewardRaw.User` va `EventRewardRaw.Partner` co the mapping nhieu-nhieu
- Reconciliation chi check per-user, khong detect multi-account cua 1 nguoi that

---

### S4. Thay the Organic Engagement bang Engagement Pods

**Mo ta:** Nhom creators thoa thuan like/comment/share cho nhau de tang engagement rate.

**Muc do rui ro:** **MEDIUM-HIGH**

**Cach thuc:**
- Tham gia nhom Telegram/Facebook/Zalo: "Like video toi, toi like video ban"
- Su dung engagement pod apps tu dong
- Rotate nhom thanh vien de tranh bi phat hien pattern

**Detection Signals:**
- Comments generic: "Nice video!", "Great content!", fire emojis
- Cung nhom users engage tren nhieu creators khac nhau
- Engagement spike dot ngot trong 10 phut dau sau khi post
- High engagement nhung low conversion (khong click brand link)
- Comment-to-view ratio bat thuong (>5%)
- Cau truc ngon ngu lap lai across posts

**Ap dung vao TCB Creator:**
- Auto-reject condition `engagement` va `comment` co the bi bypass vi engagement "nhin that"
- `like` threshold se bi vuot qua de dang
- Can phan biet engagement chat luong vs engagement so luong

---

### S5. Thay the Real Social Media Account bang Mua/Thue Account

**Mo ta:** Creator mua hoac thue account social media co san followers va engagement history de du dieu kien tham gia campaign.

**Muc do rui ro:** **MEDIUM**

**Cach thuc:**
- Mua account TikTok/Facebook co 100K+ followers
- Thue account trong thoi gian campaign
- Mua account tu thi truong nuoc ngoai va doi ten/bio

**Detection Signals:**
- Account age lon nhung content history khong lien tuc
- Thay doi dot ngot ve chu de noi dung
- Follower demographics khong match voi content hien tai
- Bio/username thay doi gan day
- Gap lon trong posting history

**Ap dung vao TCB Creator:**
- `AccountAgeRule` se KHONG detect vi account cu
- Follower count hien tai co the lon nhung engagement rate giam sau khi doi chu

---

### S6. Thay the Screenshots/Metrics That bang Metrics Gia

**Mo ta:** Creator gui screenshots/bao cao metrics da bi chinh sua de tang so lieu.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Photoshop screenshots insights/analytics
- Edit HTML truoc khi chup screenshot (Inspect Element)
- Fake URLs dang nhu tiktok.com nhung thuc te la trang gia
- Dung tool tao screenshot gia tu template

**Detection Signals:**
- Chenh lech >10% giua self-reported vs platform API data
- Screenshots co artifacts photoshop
- URL parameters bi alter
- Khong verify duoc qua official API
- Font/layout khong khop voi giao dien that cua platform

**Ap dung vao TCB Creator:**
- He thong hien tai co Content Catcher tu dong crawl -> giam rui ro nay
- Nhung van co khe ho neu crawl bi delay hoac fail

---

## C - COMBINE (KET HOP)

> Ke gian lan co the KET HOP nhieu chien thuat de tao ra attack phuc tap hon?

### C1. Multi-Account + View Farming (Combo Attack)

**Mo ta:** 1 nguoi van hanh nhieu accounts, moi account mua views rieng, tong hop reward tu tat ca accounts.

**Muc do rui ro:** **CRITICAL**

**Cach thuc:**
- Tao 5-10 tai khoan voi identity khac nhau
- Moi account tham gia cung campaign
- Mua view packages cho moi account (vua du de khong trigger alert)
- Tong reward = 5-10x so voi 1 account

**Detection Signals:**
- Cluster accounts co cung IP range
- Bank accounts lien quan (cung nguoi nhan, cung ngan hang, cung chi nhanh)
- Content upload tu cung thiet bi/location
- Video co style/location quay giong nhau
- Submission timing patterns giong nhau
- Cung view bot provider (traffic pattern tuong tu)

**Damage Multiplier:** 5-10x so voi single fraud

---

### C2. Content Theft + Engagement Manipulation

**Mo ta:** Lay cap noi dung chat luong + mua engagement de tao ra profile "hoan hao" qua moi kiem tra.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Download viral content tu nuoc ngoai (kho bi phat hien o VN)
- Re-edit voi brand elements cua Techcombank
- Mua engagement mix: views + likes + comments (ratio tu nhien)
- Gia lap organic growth pattern (tang dan, khong dot ngot)

**Detection Signals:**
- Content quality cao bat thuong so voi history cua creator
- Brand integration tron tru nhung creator profile khong co lich su brand work
- Engagement pattern "qua hoan hao" - ratio views:likes:comments deu dang
- Reverse search match voi content nuoc ngoai

**Damage Multiplier:** 3-5x (thuong cao hon vi "chat luong" content)

---

### C3. Insider + External Fraud (Collusion Attack)

**Mo ta:** Staff/admin cau ket voi creators de approve noi dung gian lan hoac dieu chinh metrics.

**Muc do rui ro:** **CRITICAL**

**Cach thuc:**
- Admin approve content that ra le bi reject
- Admin dung `ContentAdjustView.Positive` de tang views cho creator "than"
- Admin tao reconciliation va approve nhanh ma khong review
- Staff leak thong tin ve auto-reject thresholds cho creators

**Detection Signals:**
- Ty le approve/reject bat thuong cua 1 admin
- `ContentAdjustView` duoc su dung bat thuong nhieu cho 1 creator
- Reconciliation duoc approved qua nhanh
- Pattern: cung admin luon approve cung nhom creators
- `ReconciliationHistoryTypeChangeStatus` timestamps bat thuong (ngoai gio lam viec)

**Damage Multiplier:** Vo han (bypass moi lop bao ve)

---

### C4. Network Fraud Ring (Organized Fraud)

**Mo ta:** Mang luoi 20-50+ nguoi phoi hop, chia se resources va ky thuat de gian lan co to chuc.

**Muc do rui ro:** **CRITICAL**

**Cach thuc:**
- Chia se tai khoan view bot
- Cross-engage cho nhau (engagement pods quy mo lon)
- Chia se content templates va ky thuat
- Su dung cung dich vu fake identity
- Phoi hop timing de tranh trigger alerts dong thoi

**Detection Signals:**
- Graph analysis: cluster accounts co engagement lien ket
- Shared infrastructure: cung IP ranges, cung device types
- Content similarity across ring members
- Coordinated posting schedules
- Similar growth patterns trong cung khoang thoi gian
- Cung bank lien ket hoac cung dia chi

**Damage Multiplier:** 20-50x (quy mo to chuc)

---

### C5. View Milestone Gaming + Content Milestone Stacking

**Mo ta:** Ket hop gian lan views de dat `by-view-milestone` (1M views bonus) dong thoi san xuat nhieu content "rac" de dat `by-content-milestone`.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Tao `EventLimitVideo` (3) videos toi thieu de dat content milestone
- Mua views cho 1 video de dat view milestone
- Content cac video con lai chi can "vua du" qua auto-reject

**Detection Signals:**
- 1 video co views rat cao, cac video con lai thap
- Content quality chenh lech lon giua cac videos
- View distribution khong deu giua cac posts
- Creator chi active trong khoang thoi gian milestone

**Ap dung vao TCB Creator:**
- `EventSchemaTypeByContentMilestone` va `EventSchemaTypeByViewMilestone` co the bi game dong thoi
- `EventRewardStatistic.TotalCashMilestone` se tang bat thuong

---

## A - ADAPT (THICH NGHI)

> Ke gian lan THICH NGHI voi he thong phat hien nhu the nao?

### A1. Threshold Learning (Hoc Nguong Auto-Reject)

**Mo ta:** Creators hoc va chia se cac nguong auto-reject de duy tri metrics "vua du" ma khong bi flag.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Thu submit content bi reject -> hieu nguong
- Chia se thong tin ve cac dieu kien: min-view, content-age, engagement, comment, like
- Duy tri metrics nganh tren nguong 1 chut (vi du: min-view + 10%)
- Tham gia nhieu campaigns de tinh chinh strategy

**Detection Signals:**
- Cluster creators co metrics deu sat nguong (vi du: luon 105% cua min threshold)
- Metrics qua "hoan hao" - khong co su bien dong tu nhien
- Cac creators moi dat metrics gan giong nhau (copy strategy)
- Engagement patterns giong nhau giua nhom creators

**Ap dung vao TCB Creator:**
- `EventAutoRejectConditionType` (MinView, ContentAge, Engagement, Comment, Like) la cac nguong co the bi "hoc"
- Nguong co dinh de bi reverse-engineer

---

### A2. Slow Burn Fraud (Gian Lan Cham)

**Mo ta:** Thay vi gian lan nhieu va nhanh, ke gian lan thuc hien tu tu, gia tang dan de tranh bi phat hien.

**Muc do rui ro:** **MEDIUM-HIGH**

**Cach thuc:**
- Mua views tu tu: 100-200 views/ngay thay vi 10K/gio
- Tang followers dan dan: 50-100/ngay
- Mix real va fake engagement (70% real, 30% fake)
- Thay doi hanh vi theo mua (campaign season vs off-season)

**Detection Signals:**
- So sanh growth rate voi median cua platform
- Long-term trend analysis (3-6 thang)
- Engagement quality score giam dan theo thoi gian
- "Too consistent" growth (thieu natural variance)

---

### A3. Platform Hopping (Nhay Nen Tang)

**Mo ta:** Khi 1 platform bi giam sat chat, chuyen sang platform khac co detection yeu hon.

**Muc do rui ro:** **MEDIUM**

**Cach thuc:**
- Bat dau voi TikTok (de mua views nhat)
- Khi TikTok detection manh len -> chuyen sang Facebook Reels
- Roi sang Threads/Shopee (it duoc giam sat)
- Su dung YouTube Shorts (kho verify)

**Detection Signals:**
- Creator dot ngot chuyen platform giua campaign
- Tat ca submissions tu platform moi (noi khong co history)
- Platform moi co detection capability yeu hon
- Content quality khong match voi platform expertise

**Ap dung vao TCB Creator:**
- 9 content sources voi detection capability khac nhau
- `ContentSourceThreads` va `ContentSourceShopee` co the la diem yeu

---

### A4. Cyborg Accounts (Hybrid Human-Bot)

**Mo ta:** Ket hop bot automation voi hoat dong thu cong de qua mat ca automated va manual review.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Bot handle growth va view inflation
- Human reply DMs va comments (tu nhien)
- Human tao content that (co chat luong)
- Bot boost metrics len muc "an toan"
- Human negotiate voi brand/admin

**Detection Signals:**
- Activity patterns: hoat dong 24/7 (bot) xen ke voi gio "binh thuong" (human)
- Comment quality khac nhau: generic (bot) vs specific (human)
- Response time: instant (bot) vs delayed (human)
- Engagement sources: organic + inorganic mixed

---

### A5. Timing Manipulation (Thao Tung Thoi Gian)

**Mo ta:** Dieu chinh thoi diem submit va boost metrics de align voi crawl schedule cua he thong.

**Muc do rui ro:** **MEDIUM**

**Cach thuc:**
- Hoc schedule cua Content Catcher (khi nao crawl data)
- Boost views ngay truoc crawl time
- Giam bot activity sau crawl
- Submit content vao luc "tot nhat" de maximize metrics tai thoi diem crawl

**Detection Signals:**
- View spikes align voi crawl schedule
- Metrics giam sau crawl window
- "Sawtooth pattern": tang truoc crawl, giam sau crawl
- Content age mismatch: dang tu lau nhung views chi tang khi gan crawl

---

## M - MODIFY/MAGNIFY (PHONG DAI)

> Fraud nao co the duoc PHONG DAI quy mo?

### M1. Tu 1 Account -> Farm Accounts (Account Farming)

**Mo ta:** Tu gian lan don le, mo rong thanh van hanh hang chuc/tram accounts de nhan scale reward.

**Muc do rui ro:** **CRITICAL**

**Cach thuc:**
- Dau tu ban dau: mua 50-100 sim cards, tao email/accounts
- Setup: moi account 1 profile social media rieng
- Van hanh: 1 nguoi quan ly tat ca qua tools (Hootsuite, Buffer)
- Scale: moi account nhan 1-2M VND/campaign x 50 accounts = 50-100M VND

**Detection Signals:**
- Cluster registration: nhieu accounts dang ky trong thoi gian ngan
- Device sharing: cung IMEI/device ID
- Network overlap: cung WiFi/IP range
- Content similarity: dung chung template/filter/music
- Payout clustering: nhieu accounts chuyen tien ve cung nguoi

**Financial Impact:** 50-100M VND/campaign (thay vi 1-2M cho 1 account)

---

### M2. Tu Manual -> Automated Fraud (Bot Automation)

**Mo ta:** Tu viec thu cong mua views/engagement, chuyen sang he thong tu dong hoa toan bo quy trinh gian lan.

**Muc do rui ro:** **CRITICAL**

**Cach thuc:**
- Viet scripts tu dong tao account + submit content
- API integration voi view bot services
- Scheduled tasks: tu dong boost views theo lich
- Auto-monitor: theo doi metrics va dieu chinh real-time
- Dashboard quan ly tat ca accounts gian lan

**Detection Signals:**
- Submission patterns qua deu dan (cung gio, cung ngay)
- API-like behavior: actions qua nhanh cho human
- Identical time gaps giua actions
- Error patterns: bot retry same action
- Headers/user-agent bat thuong

**Financial Impact:** Unlimited (scale khong gioi han)

---

### M3. Tu Don Le -> To Chuc (Fraud-as-a-Service)

**Mo ta:** 1 nguoi/nhom chuyen nghiep hoa viec gian lan va ban dich vu cho nhieu creators.

**Muc do rui ro:** **CRITICAL**

**Cach thuc:**
- Tao "goi dich vu": Setup account + content + views + engagement
- Tinh gia: 30-50% commission tu reward
- Marketing: quang cao tren Telegram/Zalo groups cho creators
- Bao hanh: cam ket khong bi detect hoac hoan tien
- Mo rong: phuc vu 100+ creators dong thoi

**Detection Signals:**
- Nhieu creators co cung "style" gian lan
- Cung view bot provider (traffic fingerprint giong nhau)
- Content templates giong nhau across creators
- Coordinated onboarding: nhieu creators dang ky cung thoi diem
- Similar "success rates" across clients

**Financial Impact:** 500M-1B VND/campaign (to chuc chuyen nghiep)

---

### M4. Budget Drain Attack (Tan Cong Ngan Sach)

**Mo ta:** Gian lan nham nghi vao budget cua campaign de lam can kiet ngan sach truoc khi creators that duoc tra.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Nhieu accounts gian lan "race" de rut budget
- Trigger budget thresholds: 75% -> 95% -> 100% nhanh chong
- Creators that khong duoc tra vi budget het
- Lam giam uy tin cua platform voi creators that

**Detection Signals:**
- Budget consumption rate tang dot bien
- Nhieu claims tu new/suspicious accounts trong thoi gian ngan
- Budget hit 95% threshold som bat thuong
- Real creators khieu nai khong con budget

**Ap dung vao TCB Creator:**
- Budget threshold monitoring (75%, 95%, 100%) la diem yeu
- Reconciliation co the bi overwhelm voi volume gian lan

---

### M5. Cross-Campaign Exploitation

**Mo ta:** Ke gian lan tham gia tat ca campaigns co the de maximize total reward.

**Muc do rui ro:** **MEDIUM-HIGH**

**Cach thuc:**
- Dang ky moi campaign co san
- Dung cung content (thay doi nho) cho nhieu campaigns
- Leverage view bots across campaigns
- Focus vao campaigns co CPV cao nhat

**Detection Signals:**
- Creator tham gia 100% campaigns
- Content re-use across campaigns (hash similarity)
- Submission volume bat thuong (qua nhieu submissions/ngay)
- Khong co brand relevance giua creator va campaign

---

## P - PUT TO OTHER USES (LAM DUNG)

> He thong co the bi LAM DUNG cho muc dich nao khac ngoai fraud thong thuong?

### P1. Money Laundering (Rua Tien)

**Mo ta:** Su dung he thong TCB Creator de hop thuc hoa tien bat hop phap thong qua "reward" tu campaigns.

**Muc do rui ro:** **CRITICAL**

**Cach thuc:**
- Tao accounts voi identity gia
- Mua views/engagement bang tien "ban" (tien tu nguon bat hop phap)
- Nhan reward la tien "sach" tu Techcombank
- Rut tien ve tai khoan ngan hang hop phap
- Quay vong: dau tu lai vao mua views -> nhan reward

**Detection Signals:**
- Ty le dau tu mua views vs reward nhan duoc bat thuong
- Accounts khong quan tam den content quality
- Withdrawal pattern: rut tien ngay khi co the
- Large volumes tu new accounts
- Khong co social media presence that su

**Dac biet nguy hiem vi:**
- TCB la ngan hang -> AML (Anti-Money Laundering) regulations
- Reward chuyen thang vao bank account
- Co the bi dieu tra boi co quan phap luat

---

### P2. Competitive Sabotage (Pha Hoai Canh Tranh)

**Mo ta:** Doi thu canh tranh su dung he thong de pha hoai campaign cua Techcombank.

**Muc do rui ro:** **MEDIUM**

**Cach thuc:**
- Tao content tieu cuc/xau ve thuong hieu TCB
- Flood campaign voi content chat luong thap
- Drain budget bang gian lan de creators that bo di
- Tao scandal ve "TCB tra tien cho fake content"

**Detection Signals:**
- Content co sentiment tieu cuc ve brand
- Cluster submissions tu accounts khong co history voi TCB
- Content co the chua thong tin cua doi thu
- Pattern: nhieu accounts moi submit content chat luong thap cung luc

---

### P3. Data Harvesting (Thu Thap Du Lieu)

**Mo ta:** Dang ky lam creator de truy cap du lieu he thong, thong tin campaign, va du lieu creator khac.

**Muc do rui ro:** **MEDIUM**

**Cach thuc:**
- Dang ky account creator
- Truy cap danh sach campaigns, dieu kien, thuong
- Thu thap thong tin ve cac creators khac
- Scrape data ve chinh sach reward, thresholds, va metrics
- Ban data cho doi thu hoac dich vu fraud

**Detection Signals:**
- Account khong submit content nhung dang nhap thuong xuyen
- API calls bat thuong (crawl-like behavior)
- Truy cap nhieu campaign details nhung khong tham gia
- Download/export data bat thuong

---

### P4. Brand Damage (Ton Hai Thuong Hieu)

**Mo ta:** Su dung platform de tao content gay hai cho hinh anh Techcombank.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Tao content voi brand TCB trong boi canh tieu cuc
- Post content vi pham quy dinh (18+, bao luc, chinh tri)
- Link brand TCB voi noi dung controversy
- Tao content misleading ve san pham/dich vu cua TCB

**Detection Signals:**
- Content moderation flags
- Negative sentiment analysis
- Content categories khong phu hop (NSFW, violence)
- Brand safety score thap
- User reports tu cong dong

**Dac biet nguy hiem vi:**
- TCB la thuong hieu ngan hang lon
- Regulatory risk (NHNN, SBV regulations)
- Reputation damage kho phuc hoi

---

### P5. Tax Evasion Facilitation (Ho Tro Tron Thue)

**Mo ta:** Su dung reward income ma khong khai bao thue, hoac tao chi phi gia thong qua viec mua views.

**Muc do rui ro:** **MEDIUM**

**Cach thuc:**
- Nhan reward qua nhieu accounts nho (duoi nguong khai bao)
- Khong khai bao income tu influencer marketing
- Tao hoa don gia cho "dich vu marketing" de wash chi phi mua views

**Detection Signals:**
- Nhieu accounts nho cua 1 nguoi (deu duoi nguong thue)
- Tong reward cua 1 nguoi (qua nhieu accounts) vuot nguong khai bao
- Pattern: chia nho payments de tranh reporting

---

## E - ELIMINATE (LOAI BO)

> Ke gian lan LOAI BO gi de tranh bi phat hien?

### E1. Xoa Dau Vet Bot Activity

**Mo ta:** Sau khi mua views/engagement, xoa moi bang chung de khong bi trace nguon goc.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Mua views -> doi views on dinh -> xoa lich su mua tu SMM panel
- Su dung one-time payment methods (crypto, gift cards)
- Dung VPN/Tor de truy cap bot services
- Xoa browser history, cookies, app data
- Khong luu email xac nhan mua views

**Detection Signals:**
- Khong co direct evidence -> can dua vao pattern analysis
- View sources khong trace duoc (missing referrer)
- Sudden organic-looking traffic tu unknown sources
- Khong co tuong tac follow-up tu "viewers"

---

### E2. Tao Variation de Tranh Pattern Detection

**Mo ta:** Thay doi hanh vi thuong xuyen de he thong khong nhan ra pattern co dinh.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- Thay doi so luong views mua moi lan (random tu 5K-20K)
- Dung nhieu bot providers khac nhau
- Thay doi thoi gian boost (sang, chieu, toi, random)
- Mix real va fake engagement voi ty le thay doi
- Doi platforms thuong xuyen

**Detection Signals:**
- High variance trong metrics nhung medium/outcome van suspicious
- Cross-reference nhieu data points thay vi chi 1
- Statistical anomalies: phan phoi khong tu nhien du random
- Long-term behavioral analysis cho thay inconsistency

---

### E3. An Danh va Obfuscation

**Mo ta:** Su dung moi cach de an danh tinh that va lam mo moi lien ket giua cac accounts.

**Muc do rui ro:** **MEDIUM-HIGH**

**Cach thuc:**
- Moi account dung sim/email/bank account khac nhau
- Khong co connection giua cac accounts tren social media
- Dung VPN/proxy khac nhau cho moi account
- Post content tu cac dia diem khac nhau
- Timing khac nhau cho moi account

**Detection Signals:**
- Can deep analysis: behavioral biometrics
- Writing style analysis (NLP) cho descriptions/captions
- Video production style fingerprinting
- Device sensor data patterns (neu co app)
- Network graph analysis cho indirect connections

---

### E4. Social Engineering Staff

**Mo ta:** Thay vi cheat he thong, ke gian lan thao tung nhan vien de duoc approve.

**Muc do rui ro:** **MEDIUM**

**Cach thuc:**
- Lam quen/hoi lo staff review content
- Gia dang la "creator lon" hoac "doi tac"
- Goi dien/nhan tin truc tiep cho staff
- Complain nhieu lan de staff "chiu" approve
- Dua ra ly do hop ly cho metrics bat thuong

**Detection Signals:**
- Staff approve bat thuong (override auto-reject)
- Communication ngoai he thong giua staff va creator
- Complaints/escalations tu cung creator nhieu lan
- Staff action patterns thay doi khi lam viec voi creator cu the

---

### E5. Exploit Crawl Gaps (Loi Dung Khe Ho Crawl)

**Mo ta:** Loi dung thoi diem he thong khong crawl hoac khe ho giua cac lan crawl de thao tung metrics.

**Muc do rui ro:** **MEDIUM**

**Cach thuc:**
- Xoa comment/engagement xau sau khi da duoc count
- Tang views chi trong crawl window
- Thay doi content sau khi da duoc approved
- Delete va re-upload video de reset metrics

**Detection Signals:**
- Metrics giam giua cac lan crawl
- Content thay doi sau approval
- URL redirect hoac content swap
- Video duration/content hash thay doi

---

## R - REVERSE (DAO NGUOC)

> Neu DAO NGUOC vai tro: fraud den tu dau khac ngoai creators?

### R1. Admin/Staff Fraud (Gian Lan Tu Noi Bo)

**Mo ta:** Nhan vien he thong loi dung quyen han de gian lan tai chinh.

**Muc do rui ro:** **CRITICAL**

**Cach thuc:**
- **Ghost Creator Fraud:** Admin tao creator gia, submit content gia, tu approve va nhan reward
- **ContentAdjustView Abuse:** Su dung `ContentAdjustView.Positive` de tang views cho accounts ca nhan
- **Reconciliation Manipulation:** Admin dieu chinh reconciliation data de tang reward
- **Selective Approval:** Tu choi creators that, approve creators "cua minh"
- **Threshold Manipulation:** Thay doi auto-reject thresholds de cho phep content gian lan qua

**Detection Signals:**
- Audit trail bat thuong: cung admin thuc hien nhieu thao tac ngoai gio
- `ContentAdjustView` su dung qua thuong xuyen boi 1 staff
- Creators lien tuc duoc approve boi cung 1 admin
- Reconciliation amounts bat thuong
- `ReconciliationHistoryTypeChangeStatus` khong co review tu nguoi khac
- Staff co tai khoan bank trung voi creator accounts

**Ap dung vao TCB Creator:**
- `Processing()` function chay 3 goroutines parallel (Milestone, Content, Bonus) -> phuc tap, kho audit
- `createAudit()` chay trong goroutine -> co the miss audit log
- Khong co dual-approval cho reconciliation status changes

---

### R2. System-Level Fraud (Loi He Thong Bi Exploit)

**Mo ta:** Loi dung bugs hoac thiet ke yeu cua he thong de tu dong nhan reward khong xung dang.

**Muc do rui ro:** **HIGH**

**Cach thuc:**
- **Race Condition:** Submit nhieu requests dong thoi de nhan double reward
- **Integer Overflow:** Manipulate view counts de trigger calculation errors
- **API Abuse:** Truc tiep goi API de bypass UI validations
- **Reconciliation Race:** Submit trong luc reconciliation dang Processing
- **Status Manipulation:** Exploit status transitions (pending -> approved without proper checks)

**Detection Signals:**
- Duplicate rewards cho cung content
- Reward amounts vuot qua campaign budget
- API calls truc tiep khong qua UI
- Timing anomalies: actions xay ra qua nhanh
- Database inconsistencies: EventRewardRaw vs EventRewardTempRaw mismatch

**Ap dung vao TCB Creator:**
- `ProcessingMilestone`, `ProcessingContent`, `ProcessingBonus` chay parallel -> race condition risk
- `EventRewardTempRaw` la temp table -> co the bi exploit trong transition
- `wg.Add(3)` voi 3 goroutines -> error handling co the miss

---

### R3. Partner/AccessTrade-Side Fraud

**Mo ta:** Doi tac (AccessTrade hoac agency) gian lan tu phia partner.

**Muc do rui ro:** **MEDIUM-HIGH**

**Cach thuc:**
- **Phantom Campaign:** Tao campaign gia de rut budget
- **Inflated Budget:** Bao gia campaign cao hon thuc te
- **Kickback Scheme:** Nhan hoa hong tu creators de approve
- **Data Manipulation:** Bao cao metrics gia cho Techcombank
- **Double Billing:** Tinh phi 2 lan cho cung 1 service

**Detection Signals:**
- Campaign budget vs actual spend chenh lech lon
- Campaign performance bao cao vs thuc te khac nhau
- Invoices khong match voi system data
- Partner co ty le fraud creators cao bat thuong

---

### R4. Platform API Fraud (Platform Side)

**Mo ta:** Fraud den tu phia social media platforms: APIs tra ve data sai hoac bi manipulate.

**Muc do rui ro:** **LOW-MEDIUM**

**Cach thuc:**
- TikTok/Facebook API tra ve inflated metrics (platform muon giua creators)
- API data bi cache va outdated
- Platform thay doi counting methodology (vi du: TikTok thay doi cach dem views)
- Third-party API wrappers return fake data

**Detection Signals:**
- Cross-platform comparison: cung creator, metrics chenh lech lon giua platforms
- API data vs manual check khong khop
- Sudden metric changes sau platform update
- Historical data inconsistencies

---

### R5. Competitor Sabotage Through Fraud Reports (False Flagging)

**Mo ta:** Doi thu canh tranh bao cao gian lan gia ve creators that de lam gian doan campaign.

**Muc do rui ro:** **MEDIUM**

**Cach thuc:**
- Mass report creators chinh thong la "fake"
- Tao bang chung gia ve gian lan
- Lam quen voi staff de "leak" thong tin fraud
- Tao narrative "TCB Creator day gian lan" tren social media

**Detection Signals:**
- Spike trong fraud reports tu nguon khong ro
- Reports khong co bang chung cu the
- Pattern: chi target creators top-performing
- Timing: reports tang truoc/trong campaign lon

---

## TONG HOP VA KHUYEN NGHI

### Ma Tran Rui Ro (Risk Matrix)

| # | Pattern | Muc Do | Kha Nang | Impact | Priority |
|---|---------|--------|----------|--------|----------|
| S1 | Bot Views | CRITICAL | Cao | 30-50M/campaign | P0 |
| S2 | Stolen/AI Content | HIGH | Cao | 10-15M/campaign | P1 |
| S3 | Fake Identity/Multi-Account | HIGH | Trung binh | 10-20M/campaign | P1 |
| S4 | Engagement Pods | MEDIUM-HIGH | Cao | 20-30M/campaign | P1 |
| S5 | Mua/Thue Account | MEDIUM | Thap | 5-10M/campaign | P2 |
| S6 | Fake Metrics/Screenshots | HIGH | Trung binh | 40-60M/campaign | P1 |
| C1 | Multi-Account + View Farm | CRITICAL | Trung binh | 5-10x multiplier | P0 |
| C2 | Content Theft + Engagement | HIGH | Trung binh | 3-5x multiplier | P1 |
| C3 | Insider Collusion | CRITICAL | Thap | Unlimited | P0 |
| C4 | Fraud Ring/Network | CRITICAL | Thap | 20-50x multiplier | P0 |
| C5 | Milestone Stacking | HIGH | Cao | 2-3x multiplier | P1 |
| A1 | Threshold Learning | HIGH | Cao | Lam giam hieu qua detection | P1 |
| A2 | Slow Burn Fraud | MEDIUM-HIGH | Trung binh | Kho detect, tich luy lon | P2 |
| A3 | Platform Hopping | MEDIUM | Trung binh | Shift attack vector | P2 |
| A4 | Cyborg Accounts | HIGH | Trung binh | Bypass ca manual review | P1 |
| A5 | Timing Manipulation | MEDIUM | Trung binh | Exploit crawl gaps | P2 |
| M1 | Account Farming | CRITICAL | Trung binh | 50-100M/campaign | P0 |
| M2 | Automated Fraud | CRITICAL | Thap | Unlimited scale | P0 |
| M3 | Fraud-as-a-Service | CRITICAL | Thap | 500M-1B/campaign | P0 |
| M4 | Budget Drain | HIGH | Trung binh | 100% budget loss | P1 |
| M5 | Cross-Campaign | MEDIUM-HIGH | Cao | Multi-campaign loss | P1 |
| P1 | Money Laundering | CRITICAL | Thap | Legal/regulatory risk | P0 |
| P2 | Competitive Sabotage | MEDIUM | Thap | Brand reputation | P2 |
| P3 | Data Harvesting | MEDIUM | Trung binh | Competitive intelligence | P2 |
| P4 | Brand Damage | HIGH | Trung binh | Reputation risk | P1 |
| P5 | Tax Evasion | MEDIUM | Trung binh | Legal risk | P2 |
| E1 | Xoa Dau Vet | HIGH | Cao | Lam giam detection rate | P1 |
| E2 | Pattern Variation | HIGH | Trung binh | Bypass rules | P1 |
| E3 | An Danh/Obfuscation | MEDIUM-HIGH | Trung binh | Kho trace | P2 |
| E4 | Social Engineering | MEDIUM | Thap | Bypass human review | P2 |
| E5 | Crawl Gap Exploit | MEDIUM | Trung binh | Metrics manipulation | P2 |
| R1 | Admin/Staff Fraud | CRITICAL | Thap | Unlimited | P0 |
| R2 | System Bugs Exploit | HIGH | Thap | Race conditions, double pay | P1 |
| R3 | Partner Fraud | MEDIUM-HIGH | Thap | Budget manipulation | P1 |
| R4 | Platform API Fraud | LOW-MEDIUM | Thap | Data accuracy | P3 |
| R5 | False Flagging | MEDIUM | Thap | Disruption | P2 |

### TOP 10 PRIORITIES (P0)

1. **Bot Views (S1)** - Phong ngua bang View Velocity Rule + Engagement Rate check
2. **Multi-Account + View Farm (C1)** - Identity verification + cross-account analysis
3. **Insider Collusion (C3)** - Dual approval + audit trail + separation of duties
4. **Fraud Ring (C4)** - Network/graph analysis
5. **Account Farming (M1)** - Device fingerprinting + bank account cross-check
6. **Automated Fraud (M2)** - Rate limiting + behavioral analysis
7. **Fraud-as-a-Service (M3)** - Traffic fingerprinting + pattern correlation
8. **Money Laundering (P1)** - AML checks + transaction monitoring
9. **Admin Fraud (R1)** - Role-based access + dual control + immutable audit logs
10. **Budget Drain (M4)** - Real-time budget monitoring + velocity checks

### KHUYEN NGHI TRIEN KHAI THEO PHASE

**Phase 0 (Week 1-2): Foundation**
- Rule-based detection cho S1 (Bot Views)
- Cross-platform verification cho S6 (Fake Metrics)
- Bank account cross-check cho S3 (Multi-Account)
- Basic audit trail cho R1 (Admin Fraud)

**Phase 1 (Week 3-6): Automation**
- Identity verification strengthening (S3, C1, M1)
- Engagement quality scoring (S4, A4)
- Content similarity detection (S2, C2, C5)
- Dual approval workflow (C3, R1)
- Budget velocity monitoring (M4)

**Phase 2 (Week 7-12): Intelligence**
- Network/graph analysis (C4, M3)
- Behavioral analytics (A1, A2, A3)
- AML screening integration (P1)
- Automated pattern evolution (E1, E2)
- Content moderation cho brand safety (P4)

**Phase 3 (Ongoing): Advanced**
- ML-based anomaly detection
- Real-time fraud scoring
- Predictive fraud prevention
- Cross-campaign intelligence (M5)
- Partner audit framework (R3)

---

## REFERENCES

- [Brainstorming Fraud Detection Solutions (2026-02-08)](./brainstorming-fraud-detection-solutions-2026-02-08.md)
- [Feasibility Analysis Fraud Detection (2026-02-09)](./feasibility-analysis-fraud-detection-2026-02-09.md)
- [Tapfiliate: Influencer Fraud 2026](https://tapfiliate.com/blog/influencer-fraud-fake-engagement-gp)
- [Influencer Fraud Detection Evolution](https://deliveredsocial.com/influencer-fraud-detection-evolution-from-bots-to-deepfakes/)
- [Influencer Fraud Statistics 2025](https://www.amraandelma.com/influencer-fraud-statistics/)
- [TikTok Bot Farm Detection](https://influencermarketinghub.com/bot-farm-detection-checklist-for-instagram-tiktok/)
- [Social Media Money Laundering](https://www.sanctions.io/blog/money-laundering-and-social-media-influencers)
- [TikTok Money Laundering](https://medium.com/aml-watcher/the-underworld-of-tiktok-money-laundering-exposed-17ffe3066cfe)
- [Influencer Cartels (CEPR)](https://cepr.org/voxeu/columns/how-influencer-cartels-manipulate-social-media-fraudulent-behaviour-hidden-plain)
