# Tech Spec: Popup hiển thị đúng đối tác đã chọn

**Ngày:** 2026-07-09 · **Branch đề xuất:** `fix/popup-partner-targeting` (từ `origin/develop`)
**PRD (bản gửi Sếp):** `prd-popup-partner-targeting-2026-07-08.md` · **Phân tích đầy đủ:** `tech-analysis-popup-partner-targeting.md` (lưu tại repo vcreator)
**Trạng thái:** Sẵn sàng implement FR-001/FR-002 (Must). FR-003/FR-004 chờ Sếp duyệt đề xuất 2/3 (PRD §7).

---

## 1. Phạm vi theo PRD

| FR | Thay đổi | File | Điều kiện |
|----|----------|------|-----------|
| FR-001 | FE truyền id partner + đổi thời điểm gọi + reset cờ `isShowPopup` | `frontend-green/src/pages/partner-home/index.tsx`, `main-home/index.tsx` | Làm ngay |
| FR-002 | Không sửa code — hành vi có được từ FR-001 + logic BE sẵn có | — | Verify bằng test matrix §4 |
| FR-003 | BE sort popup riêng lên trước | `backend/pkg/public/service/news.go` | Chỉ khi duyệt đề xuất 2 |
| FR-004 | Cooldown key theo scope trang | `frontend-green/src/utils/storage.ts` + 2 trang | Chỉ khi duyệt đề xuất 3 |

Root cause tóm tắt: `partner-home/index.tsx:146-156` fetch `{type:'popup'}` không kèm partner → BE (`public/service/news.go:84-87` + `mgquery/common.go:117-131`) chỉ match `$or:[{isAllPartner:true}]`. Chi tiết: tech-analysis §2.

---

## 2. Chi tiết implement

### 2.1 FR-001 — partner-home (`partner-home/index.tsx`)

**(a)** `getPopupNews` nhận `partnerId` (hiện tại: L146-156):

```ts
const getPopupNews = async (partnerId: string, callback?) => {
  dispatch({
    type: 'mainState/getPopupNews',
    payload: { query: { type: 'popup', partner: partnerId } },
    callback,
  });
};
```

⚠️ `partnerId` là `_id` ObjectID 24-hex từ callback saga `getDetailPartner` (`models/main.ts:254`) — **không phải slug**. BE bỏ qua im lặng giá trị không phải hex (`mgquery/common.go:125`) → gửi slug là bug tái diễn không báo lỗi.

**(b)** Xóa `useEffect([])` fetch popup (L158-174), chuyển logic vào callback `getPartnerDetail` (L88-94), kèm **reset cờ trước fetch** (chống bẫy SPA — cờ chỉ bật không tắt, dispatch `true` trùng giá trị không trigger `useEffect([isShowPopup])` của `PopupBanner`):

```ts
const showPopupIfEligible = (partnerId: string) => {
  const previousTimeAccess = storage.getLastShowBanner();
  if (!previousTimeAccess || helper.getHourCount(previousTimeAccess) > 0) {
    dispatch({ type: 'mainState/updateState', payload: { isShowPopup: false } }); // reset TRƯỚC fetch
    getPopupNews(partnerId, () => {
      dispatch({ type: 'mainState/updateState', payload: { isShowPopup: true } });
      setTimeout(() => storage.saveLastShowBanner(moment()), 2000);
    });
  }
};
// trong callback getPartnerDetail: showPopupIfEligible(partnerId);
```

### 2.2 FR-001 — main-home (`main-home/index.tsx` L131-147)

Giữ nguyên query (không partner). Chỉ thêm reset cờ trước fetch, cùng pattern (a)/(b) — ~3 dòng.

### 2.3 FR-003 — BE sort popup riêng trước (chỉ khi duyệt đề xuất 2)

`backend/pkg/public/service/news.go` — `GetList`. `NewsAppResponse` không có field partner (`news.go:105-132`) → build map từ `docs` rồi sort 2 khóa:

```go
// sau vòng loop build result, thay sort hiện tại (L98-100) cho type popup:
hasPartner := make(map[modelmg.AppID]bool, len(docs))
for _, d := range docs {
    hasPartner[d.ID] = d.Partner != nil
}
sort.SliceStable(result, func(i, j int) bool {
    pi, pj := hasPartner[result[i].ID], hasPartner[result[j].ID]
    if pi != pj { return pi } // popup riêng đối tác lên trước
    return result[i].Order > result[j].Order
})
```

Type khác giữ sort `Order` desc như cũ. Trang chủ không ảnh hưởng (chỉ nhận popup all-partner).

### 2.4 FR-004 — cooldown theo scope (chỉ khi duyệt đề xuất 3)

`utils/storage.ts:72-77`:

```ts
function getLastShowBanner(scope = 'home') {
  return localStorage.getItem(`${AppConst.localStorage.lastShowBanner}:${scope}`);
}
function saveLastShowBanner(scope = 'home', time) {
  return localStorage.setItem(`${AppConst.localStorage.lastShowBanner}:${scope}`, time);
}
```

Caller: `main-home` scope `'home'`; `partner-home` scope `params.partner` (slug — chỉ làm key localStorage, không gửi BE). Giữ ngữ nghĩa cooldown "sang khung giờ mới" (`helper.ts:271-277` so sánh `startOf('hour')`) — không đổi.

Cách làm dừng ở mức này: không cooldown theo từng popup `_id`, không luân phiên chung/riêng, không thêm key nào ngoài `lastShowBanner:<scope>`.

### 2.5 Không sửa

- BE filter/handler/cache: param `partner` đã hỗ trợ (`public/model/request/news.go:11`); cache key theo full URL tự tách theo đối tác (`handler/news.go:61-65`); admin `clearCache` đã có.
- Admin form + admin service: lưu `partner`/`isAllPartner` đúng (`admin/model/request/news.go:79-90`).
- `PopupBanner` component: giữ nguyên (render `news[0]`).

---

## 3. Thứ tự thực thi

1. FR-001 (a)+(b) partner-home → 2.2 main-home → verify build: `cd frontend-green && yarn build`
2. (Nếu duyệt) FR-004 storage + callers → yarn build
3. (Nếu duyệt) FR-003 backend → `cd backend && go build ./...`

## 4. Verify & test matrix

**API (máy có mạng, trước/sau fix):**
```bash
curl 'https://api.viewboost.vn/news?type=popup'                       # trước fix: không có popup gắn đối tác
curl 'https://api.viewboost.vn/news?type=popup&partner=<greensm-id>'  # sau fix FE sẽ gọi dạng này: có popup Green SM
```

**UI — 5 case PRD FR-002** (mỗi lượt: tab ẩn danh hoặc xóa key `lastShowBanner*`), chạy trên `/`, `/greensm`, `/vinwonders`, desktop + mobile viewport:

| Case | Setup popup | Kỳ vọng |
|---|---|---|
| 1 | 1 riêng Green SM | Chỉ `/greensm` hiện |
| 2 | 1 chung | Cả 3 trang hiện (theo đề xuất 1) |
| 3 | 1 chung + 1 riêng Green SM | `/greensm` hiện popup riêng (FR-003); trang khác hiện chung |
| 4 | 2 riêng Green SM | `/greensm` hiện popup `order` cao hơn |
| 5 | Riêng Green SM + riêng VinWonders | Mỗi trang hiện popup của mình |

**SPA flow (bẫy cờ):** `/` thấy popup → đóng → sang khung giờ mới → điều hướng nội bộ sang `/greensm` (không reload) → popup đối tác hiện.

**Network tab:** request popup ở `/greensm` phải có `partner=` 24-hex.

**Regression:** banner `home_banner` trang đối tác, profile-completion popup, home notice.

## 5. Lưu ý cho dev/QA (edge cases — chi tiết tech-analysis §7/§8)

- E2: user owner-partner vào `/` bị redirect sang trang đối tác — verify popup không dính cooldown do fetch của main-home stamp trước.
- E3: popup thiếu `startAt`/`endAt` không bao giờ hiện (`IsAvailable`, `model/mg/news.go:44-47`) — nhắc Ops set đủ thời gian.
- E6: QA phải xóa `lastShowBanner*` mỗi lượt test.
- Cache Redis TTL 2' — thay đổi từ admin có thể trễ tối đa 2 phút.

## Unresolved

- Đề xuất 1/2/3 chờ Sếp duyệt (PRD §7) → quyết định FR-003/FR-004 có làm không.
- Sau deploy: Ops cần gắn lại đúng đối tác cho các popup đang chạy theo kiểu workaround.
