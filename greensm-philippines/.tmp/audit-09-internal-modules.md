# Audit 09: Internal Modules (format/util/locale/constants)

**Files audited:**
- `internal/format/string.go` (192 dòng) — phone util + slug + accent removal
- `internal/util/time.go` (294 dòng) — timezone util cũ
- `internal/util/ptime/` (helper.go, parse.go, constant.go, ...) — timezone util mới
- `internal/locale/locale.go` — i18n bundle setup
- `internal/constants/constants.go` (lines 40, 72, 226, 227)
- `internal/constants/contract.go` (219 dòng — Bahasa Indonesia)
- `internal/service/otp.go` — OTP gửi qua AccessTrade SMS

---

## 1. internal/format/string.go (CRITICAL — Phone Util)

### Functions
- `FormatPhoneCommon(phone)` — line 20 (default add `+84`)
- `PhoneNumberFormatFromPhone(phone)` — line 55 (return PhoneNumber struct)
- `PhoneNumberIsValid(phone)` — line 157 (regex match `RegexPhoneNumber`)
- `NonAccentVietnamese(str)` — line 115
- `RemoveAccentVietnamese(str)` — line 129
- `ConvertSlugProvince/Find` — line 99/107 (hardcode `ho-chi-minh`)

### Country issues 🔴 CRITICAL

| Line | Code | Issue |
|---|---|---|
| **31** | `phone = strings.Replace(phone, "0", "+84", 1)` | Hardcode `+84` |
| **35** | `if phone[0:2] == "84"` | Check `84` prefix |
| **70-73** | `case "+84"` + `case "84"` switch | Hardcode VN code |
| **77** | `phoneNumber.CountryCode = "+84"` | **Hardcode VN code in struct** |
| **100-103** | `if slug == "ho-chi-minh"` ⇄ `"tp-ho-chi-minh"` | VN province slug |
| **115** | NonAccentVietnamese — replaces `đ`, removes Vietnamese marks | VN-specific |
| **129** | RemoveAccentVietnamese — same | VN-specific |

→ **Phone util TOÀN VN** mặc dù regex constants.go đã update sang `+62` (Indonesia).
→ Conflict: Validate accept `+62` nhưng format/parse return `+84`.

### Vietnamese accent functions usage
38 occurrences trong codebase — used cho:
- search string indexing (event/partner/article/news/segment titles)
- bank search
- export filename

→ Functions dùng cho **non-Vietnamese text** vẫn work (just lowercase + remove diacritics + remove punctuation), nhưng **tên gây confusing**.

---

## 2. internal/util/time.go + internal/util/ptime/

### Hai timezone utility paths

| Path | Functions | Status |
|---|---|---|
| `util/time.go` | TimezoneHCM constant + TimeLocationHCM var + 15 HCM functions | LEGACY (vẫn dùng) |
| `util/ptime/` | timezoneHCM constant + GetHCMLocation/TimeOfDayInHCM/TimeStartOfDayInHCM | NEW (modular) |

→ **Cả 2 path đều hardcode `Asia/Ho_Chi_Minh`**.

### Tổng count

```
TimeOfDayInHCM/TimeStartOfDayInHCM/Asia/Ho_Chi_Minh: 91 occurrences toàn backend
```

### Functions trong util/time.go (line numbers in file)

| Function | Line | Purpose |
|---|---|---|
| TimeParseWithHCMLocation | 60 | Parse time với HCM tz |
| TimeOfDayInHCM | 109 | Convert time → HCM tz |
| GetDateInHCM | 116 | Date components in HCM |
| GetStartEndDayOfMonthByTime | 122 | Month range in HCM |
| TimeEndDayNextMonthInHCM | 132 | End next month |
| TimeStartDayMonthInHCM | 140 | Start of month |
| TimeEndDayMonthInHCM | 154 | End of month |
| TimeStartOfDayInHCM | 161 | Start of day |
| TimeStartOfDayInHCMByDate | 169 | Start of day by Y/M/D |
| TimeEndOfDayInHCM | 177 | End of day |
| GetCustomTimeHCMString | 73 | Format string in HCM |

### Functions trong util/ptime/parse.go

| Function | Line | Purpose |
|---|---|---|
| TimeOfDayInHCM | parse.go (line 13) | Same as util/time.go |
| TimeStartOfDayInHCM | parse.go (line 18) | Same |

→ **Duplicate code** giữa `util/time.go` và `util/ptime/parse.go`.

---

## 3. internal/locale/locale.go

### Country/lang constants

```go
IPCountryCodeVN = "VN"
IPCountryCodeUS = "US"
IPCountryCodeUK = "UK"
IPCountryCodeKO = "KP"   // Note: KP = North Korea, not South Korea
IPCountryCodeID = "ID"   // Indonesia

LangEn = "en"
LangVi = "vi"
LangId = "id"
```

→ Không có `IPCountryCodePH` hay `LangFil` (Filipino/Tagalog).

### i18n bundle

- Dùng `nicksnyder/go-i18n/v2`
- Load JSON files từ `locale/properties/{en,vi,id}/*.json`
- ⚠️ Không có folder `fil/` hoặc `tl/` (Filipino)

---

## 4. internal/constants/constants.go (key lines)

```go
// line 40
RegexPhoneNumber = `^(?:\+62|62|0)[2-9][1-9][0-9]{6,11}$`  // Indonesia regex

// line 72
timezoneHCM = "Asia/Ho_Chi_Minh"  // VN

// line 226-227
PercentTaxIndonesia float64 = 12
PercentTaxVietNam   float64 = 10  // VN leftover
```

→ Mix VN + ID hardcode. PH chưa có.

---

## 5. internal/constants/contract.go (219 dòng)

Toàn bộ **Bahasa Indonesia** — hợp đồng PT. Interspace Indonesia (Jakarta Selatan).

Key references:
- "Pihak A: PT. Interspace Indonesia"
- "Menara Anugrah, Lantai 11, Jl. Dr. Ide Anak Agung Gde Agung Lot 8.6 - 8.7, Kawasan Mega Kuningan, Jakarta Selatan 12950, Indonesia"
- "Perwakilan: Usman, Jabatan: CEO"
- "Pihak B bertanggung jawab penuh atas kewajiban pajak sesuai hukum Indonesia"
- 5 điều khoản về advertising rules theo luật ID

→ Cần rewrite hoàn toàn cho PH (luật + tên công ty + địa chỉ + ngôn ngữ).

---

## 6. internal/service/otp.go (OTP via AccessTrade SMS)

### Flow
1. Build body: `phone = strings.Replace(payload.Recipient, "+84", "0", 1)` (line 108) — VN replacement
2. POST tới AccessTrade SMS endpoint
3. Track request vào DB
4. Verify OTP qua MongoDB lookup

### Country issues
- **Line 108**: `+84` hardcode — cùng pattern với các chỗ khác

### Notable
- Dùng AccessTrade SMS service (api proprietary của AccessTrade)
- Response có `channel` field — phụ thuộc provider config
- Comment line 100: `//"channel": config.GetENV().AccessTradeSMS.Channel` — channel commented out

---

## Đề xuất Phone Util config-driven design

### Vấn đề hiện tại
- `format/string.go` hardcode `+84` toàn bộ
- `constants.go:40` hardcode regex `+62` (Indonesia)
- Conflict: validate accept `+62` nhưng format return `+84`

### Design đề xuất

```go
// internal/config/env.go — thêm:
type ENV struct {
    // ...
    Region struct {
        CountryCode    string `env:"COUNTRY_CODE,required"`     // "PH"
        PhoneCode      string `env:"PHONE_CODE,required"`        // "+63"
        PhoneRegex     string `env:"PHONE_REGEX,required"`       // "^(09|\\+639|639)\\d{9}$"
        Timezone       string `env:"TIMEZONE,required"`          // "Asia/Manila"
        Currency       string `env:"CURRENCY,required"`          // "PHP"
        TaxPercent     float64 `env:"TAX_PERCENT,required"`     // 0 hoặc tax rate PH
    } `env:",prefix=REGION_"`
}

// internal/format/string.go — refactor:
func FormatPhoneCommon(phone string) string {
    cfg := config.GetENV().Region
    // Logic dùng cfg.PhoneCode thay vì "+84" hardcode
}

func PhoneNumberFormatFromPhone(phone string) PhoneNumber {
    cfg := config.GetENV().Region
    // Use cfg.PhoneCode for CountryCode field
}

// internal/util/time.go — refactor:
func TimezoneLocation() *time.Location {
    cfg := config.GetENV().Region
    l, _ := time.LoadLocation(cfg.Timezone)
    return l
}

func TimeStartOfDayInRegion(t time.Time) time.Time {
    l := TimezoneLocation()
    y, m, d := t.In(l).Date()
    return time.Date(y, m, d, 0, 0, 0, 0, l).UTC()
}
```

### Migration strategy

1. **Phase 1**: Thêm config-driven utils mới (TimezoneLocation, TimeStartOfDayInRegion, FormatPhone với region) — **giữ legacy functions** không touch
2. **Phase 2**: Update callsites một-một, thay HCM functions → region functions
3. **Phase 3**: Delete legacy functions sau khi tất cả callsites migrated

→ Không "big bang refactor" — minimize merge conflict.

---

## Cleanup tasks Internal layer

| Task ID | File:Line | Description | Priority | Effort |
|---|---|---|---|---|
| INT-01 | format/string.go:20-40 | Refactor FormatPhoneCommon dùng config-driven country code | P0 | M |
| INT-02 | format/string.go:55-80 | Refactor PhoneNumberFormatFromPhone dùng config | P0 | M |
| INT-03 | format/string.go:99-112 | Remove ConvertSlugProvince logic VN-specific | P0 | S |
| INT-04 | format/string.go:115-138 | Rename `NonAccentVietnamese` → `NormalizeSearchString` (chức năng vẫn work cho non-VN) | P1 | S |
| INT-05 | constants.go:40 | Move RegexPhoneNumber → config-driven (env var) | P0 | S |
| INT-06 | constants.go:72 | Remove `timezoneHCM` constant | P0 | S |
| INT-07 | constants.go:226-227 | Replace `PercentTaxIndonesia/PercentTaxVietNam` → config-driven `Region.TaxPercent` | P0 | S |
| INT-08 | util/time.go (15 functions) | Refactor toàn bộ HCM functions → Region functions (giữ deprecated stub forward) | P0 | L |
| INT-09 | util/ptime/parse.go (2 funcs) | Same refactor | P0 | M |
| INT-10 | util/ptime/helper.go | Replace `GetHCMLocation` → `GetRegionLocation` | P0 | S |
| INT-11 | util/ptime/constant.go | Remove `timezoneHCM` constant | P0 | S |
| INT-12 | constants/contract.go (toàn file) | Rewrite contract template cho PH (legal + Bahasa → English/Filipino) | P0 | L |
| INT-13 | locale/locale.go | Add `IPCountryCodePH = "PH"` + `LangFil = "fil"` | P0 | S |
| INT-14 | locale/properties/ | Add `fil/` folder với JSON keys | P0 | M |
| INT-15 | service/otp.go:108 | Replace `+84` hardcode → config | P0 | S |
| INT-16 | env.go | Add `Region` struct với COUNTRY_CODE/PHONE_CODE/PHONE_REGEX/TIMEZONE/CURRENCY/TAX_PERCENT | P0 | M |

---

## Verdict — Internal layer

🔴 **Internal layer là CỘT SỐNG country leftover**:
- 91 occurrences HCM timezone trong toàn codebase **đều trace về** util/time.go + util/ptime/
- Phone util `+84` trong format/string.go — dùng bởi user/identification/schedule
- Tax constants — dùng bởi withdraw + schedule
- Contract template — Bahasa Indonesia
- i18n — không có `fil-PH`

→ **Fix internal trước**, các module dependent sẽ tự inherit. Effort tập trung 70% ở internal layer.

→ Nguyên tắc: **làm config-driven** thay vì hardcode `+63` thay `+84`. Cost effort tăng 30% nhưng future-proof khi mở thêm market khác.
