# Gap #17 — vCreator/Ambassador có thể bị broken avatar khi URL social expire

> **Priority**: 🟡 **P2** (reclassified P1→P2 2026-05-07)
> **Source**: Initial gap-analysis #17
> **Direction port**: TCB → vCr/Amb
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Khi creator login bằng Google/TikTok/Facebook, hệ thống lấy URL avatar từ social platform. Các URL này thường có **expire time** (vài giờ → vài ngày → vài tháng) → avatar bị **broken** sau một thời gian.

## Bảng so sánh 3 sản phẩm

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Cache avatar về MinIO permanent?** | ✅ Có | ❌ Không | ❌ Không |
| **Resize 3 sizes (small/medium/large)?** | ✅ Có | ❌ | ❌ |
| **Field `User.Avatar` lưu URL gì?** | URL MinIO permanent | URL social (expire) | URL social (expire) |
| **Module MinIO + resizeimage có sẵn?** | ✅ | ✅ | ✅ |

→ vCr/Amb **chỉ thiếu service layer** `upload_avatar_social.go`. Infrastructure đã sẵn sàng.

## Hệ quả

- Brand browse profile creator → ảnh hỏng → giảm trust platform
- Creator self-profile → ảnh hỏng → khiếu nại support
- Marketing campaign screenshot → broken ngày sau

## Giải pháp

Port `upload_avatar_social.go` từ TCB → vCr/Amb (~1 tuần mỗi sản phẩm):
- Copy service ~250 LOC
- Thêm vào 3 social login flows (Google, TikTok, Facebook)
- Migration: chỉ apply cho creator mới, không backfill (tránh load MinIO + content catcher)
- Async/non-blocking → fail vẫn fallback URL social

**Reclassified P1→P2**: không phải bug active, chỉ là risk theory. Defer đến khi có incident hoặc gap #2 phase 3 (creator pool unification cần avatar consistent across products).

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có service `upload_avatar_social.go` (~250 LOC) download URL social → resize 3 sizes → upload MinIO → update `User.Avatar`. vCr/Amb không có service này nhưng đã có sẵn `module/minio` + `module/resizeimage`.

## Verify code

### TCB flow (`internal/service/upload_avatar_social.go`)

```go
func (s *UploadAvatarSocialService) UploadAvatarSocial(ctx, userId AppID, linkAvatarSocial string) (*Response, error) {
    // 1. Check User.Avatar đã có → skip
    // 2. Download file từ URL social (parse URL bỏ query params)
    // 3. Validate photo format + size
    // 4. Get dimensions + resize 3 sizes (150x150, 300x300, 600x600)
    // 5. Upload 3 sizes lên MinIO
    // 6. Update User.Avatar = MinIO URL
    // 7. Cleanup local file
}
```

**Caller** (`pkg/public/service/user.go`):
```go
// LoginWithTikTok / LoginWithGoogle / LoginWithFacebook
if ttData.Photo != "" {
    _, err := internalservice.NewUploadAvatarSocialService().UploadAvatarSocial(ctx, user.ID, ttData.Photo)
    if err != nil {
        fmt.Printf("upload avatar failed (will use social photo URL): %v\n", err)
    }
}
```

→ Async non-blocking — fail thì fallback dùng URL social.

### vCr/Amb status

```bash
ls vcreator/backend/internal/service/upload_avatar_social.go → ❌
ls ambassabor/backend/internal/service/upload_avatar_social.go → ❌

# Infrastructure đã có:
ls vcreator/backend/internal/module/minio/minio.go → ✅
ls vcreator/backend/internal/module/resizeimage/resize_image.go → ✅
```

vCr/Amb fallback hiển thị URL social trực tiếp:
```go
// vcreator/pkg/public/service/user.go
if user.Avatar != nil {
    res.Avatar = user.Avatar.GetResponseData().Dimensions.Medium.URL
} else {
    if user.Google != nil { res.Avatar = user.Google.Photo }   // ← URL social, có thể expire
    if user.Tiktok != nil { res.Avatar = user.Tiktok.Photo }   // ← URL social
}
```

## Đề xuất implementation

### Phase 1: Service port (~3 ngày mỗi sản phẩm)
- Copy `upload_avatar_social.go` từ TCB (~250 LOC)
- Adapt với constants/util của target

### Phase 2: Caller integration (~2 ngày)
- Thêm vào 3 social login flows: Google, TikTok, Facebook
- Pattern: async non-blocking, fail không break login flow

### Phase 3: Test + rollout (~2 ngày)
- Test với mỗi social platform
- Verify MinIO bucket có file + URL accessible

**Total**: ~1 tuần mỗi sản phẩm.

## Risks + mitigations

1. **MinIO bucket setup**: vCr/Amb có dùng MinIO chung với TCB hay riêng?
   - **Mitigation**: dùng config sẵn của target sản phẩm
2. **Existing users với URL social**: không backfill — chỉ apply khi user re-login
   - **Mitigation**: document trong release notes

## Files referenced

**TCB (source of truth)**:
- `internal/service/upload_avatar_social.go` (~250 LOC)
- `internal/module/minio/minio.go`
- `internal/module/resizeimage/resize_image.go`
- `pkg/public/service/user.go` — caller (LoginWithTiktok, LoginWithGoogle, LoginWithFacebook)

**vCr/Amb (target — cần port)**:
- KHÔNG có `internal/service/upload_avatar_social.go`
- Đã có `module/minio` + `module/resizeimage` ✅

## Lịch sử phân loại

- **Initial**: P1 (Total 14)
- **Reclassified P2 (2026-05-07)**: User confirm "cái này cũng clear, tôi sẽ cho nó là P2" — không phải bug active, chỉ là risk. Defer đến khi có incident hoặc gap #2 phase 3.
