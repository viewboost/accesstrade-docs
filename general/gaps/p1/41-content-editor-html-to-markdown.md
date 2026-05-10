# Gap #41 — Đổi nội dung bài viết (article/news) từ HTML sang Markdown + upload ảnh

> **Priority**: 🟠 **P1** (initial 2026-05-10 — user self-listed gap)
> **Source**: User self-listed gap
> **Direction port**: Improvement cho cả 3 sản phẩm (vCr → TCB/Amb sau khi vCr xong, hoặc làm parallel)
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Admin/ops soạn bài viết (article, news, event description) hiện tại dùng **HTML rich-text editor** (vCreator dùng `braft-editor`).

User feedback (admin pain points):
1. **Soạn HTML rất tệ**: format tag rườm rà, dễ rối khi UI render
2. **Không copy paste được giữa các bài**: HTML format khác nhau, paste sang bài khác mất định dạng hoặc lỗi
3. **Khó dùng AI hỗ trợ soạn thảo**: AI (ChatGPT, Claude) trả về Markdown native — phải convert thủ công, mất công
4. **Preview cực**: phải save/refresh để xem rendering, không có live preview side-by-side

Giải pháp đề xuất: **đổi sang Markdown editor + upload ảnh inline** (vCreator đã cài sẵn `@uiw/react-md-editor` nhưng chưa wire vào article/news).

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Editor cho article/news | ❓ | `braft-editor` (HTML) | ❓ |
| Package `@uiw/react-md-editor` cài rồi? | ❓ | ✅ (chưa wire) | ❓ |
| Live preview side-by-side | ❌ | ❌ | ❌ |
| Upload ảnh inline trong editor | ❌ (HTML thuần) | ❌ | ❌ |
| Copy-paste giữa bài giữ format | ❌ (HTML mismatch) | ❌ | ❌ |

→ Cả 3 sản phẩm đều cần improvement này. vCreator đã có infrastructure (md-editor package) gần nhất với solution.

## Hệ quả

- **Ops productivity**: admin/marketing tốn nhiều thời gian fix format khi soạn bài, đặc biệt khi reuse content cũ
- **AI workflow**: AI ngày càng quan trọng cho copywriting → admin không tận dụng được
- **Content quality**: format lỗi → user thấy bài viết ugly → giảm trust platform

## Liên quan các gap khác

- **Gap #17 (Avatar cache MinIO)**: tương tự pattern upload ảnh → MinIO. Có thể reuse infrastructure
- **Gap #42 (Cache content cover)**: cũng pattern image hosting → MinIO. Có thể combo wave

## Giải pháp

### Phase 1: vCreator (~3-5 ngày, làm trước vì đã có md-editor cài sẵn)

1. **Wire MdEditor vào article + news** (~1-2 ngày):
   - Replace `BraftEditor` (HTML) bằng `@uiw/react-md-editor` (Markdown)
   - Live preview side-by-side mode
   - Toolbar: bold, italic, heading, link, image, list, code
2. **Migration data cũ** (~0.5 ngày):
   - Article/news đã save dạng HTML → convert sang Markdown bằng `turndown` (HTML → MD library)
   - Migration script + dry-run mode
3. **Image upload integration** (~1 ngày):
   - Drag & drop image vào editor → upload MinIO → insert markdown `![alt](url)`
   - Reuse upload service đã có (như avatar cache)
4. **Backend rendering** (~0.5 ngày):
   - Frontend (creator/user view): render markdown bằng `react-markdown` + `remark-gfm`
   - Sanitize XSS (markdown vẫn có thể inject HTML)
5. **Test** (~0.5 ngày):
   - Migration data cũ không corrupt
   - Image upload + display
   - Preview vs production rendering match

### Phase 2: TCB + Ambassador (~3-5 ngày mỗi sản phẩm)
- Tương tự Phase 1 nhưng tự cài md-editor package
- Pattern đã được vCreator validate

**Total**: ~2-3 tuần (3-5 ngày mỗi sản phẩm).

## Tại sao P1

- **Pain point cụ thể**: user complaint rõ ràng, không phải hypothetical
- **AI-driven workflow**: workflow content creation đang shift sang AI-assisted, không thể trễ
- **Effort vừa phải**: vCreator đã có md-editor package, chỉ cần wire + migration
- **Cross-product**: cả 3 đều cần
- **Compounds với #42**: cùng pattern image hosting → tận dụng infrastructure

→ Sprint tới phải làm vCreator trước (đã có infrastructure), TCB/Amb làm theo.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

vCreator article/news admin dùng `braft-editor` (HTML). Package `@uiw/react-md-editor` đã cài trong `package.json` nhưng chưa wire vào pages. Cần migrate sang Markdown + thêm upload ảnh inline. TCB/Amb tương tự (chưa verify chi tiết editor stack, có thể cần tự cài).

## Verify code

### vCreator (đã có infrastructure)

**Article model** — `internal/model/mg/article.go`:
```go
type ArticleRaw struct {
    ID           AppID
    Title        string
    SearchString string
    Content      string  // ← string field, có thể chứa HTML hoặc Markdown
    Covers       ListPhoto
    Statistic    ArticleStatistic
    Action       *ArticleAction
    Code         string
    ShowOn       string
    Partner      AppID
    // ... CreatedAt, UpdatedAt
}
```

**Frontend admin editor** — `admin/src/pages/article/components/modal.tsx`:
```tsx
import BraftEditor from 'braft-editor';  // ← HTML editor
```

**Package cài sẵn** — `admin/package.json`:
```json
"@uiw/react-md-editor": "^3.11.3",  // ← Markdown editor có sẵn nhưng chưa wire
"braft-editor": "^2.3.9",            // ← cần replace
```

**News page**: tương tự article — `admin/src/pages/news/components/modal.tsx` cũng dùng `braft-editor`.

**Form-editor component**: `admin/src/components/form-editor/index.tsx` — wrapper component dùng braft.

### TCB status

```bash
grep -E "braft|md-editor|tiptap|tinymce" techcombank/dashboard/package.json → ❓ chưa verify
# Có thể TCB dùng tech stack khác (Next.js) — cần verify trong bước Phase 2
```

### Ambassador status

```bash
grep -E "braft|md-editor|tiptap|tinymce" ambassabor/admin/package.json → ❓ chưa verify
```

## Đề xuất implementation

### Phase 1: vCreator (~3-5 ngày)

1. **Component wrapper** (~0.5 ngày):
   ```tsx
   // admin/src/components/form-editor/markdown.tsx
   import MDEditor from '@uiw/react-md-editor';

   export function FormMarkdownEditor({ value, onChange, height = 400 }) {
       return (
           <MDEditor
               value={value}
               onChange={onChange}
               height={height}
               preview="live"  // side-by-side
               // toolbar customization
           />
       );
   }
   ```

2. **Image upload integration** (~1 ngày):
   ```tsx
   // Custom command for image upload
   const imageUploadCommand = {
       name: 'image-upload',
       keyCommand: 'image-upload',
       icon: <ImageIcon />,
       execute: async (state, api) => {
           const file = await pickFile();
           const url = await uploadToMinio(file); // reuse existing upload service
           api.replaceSelection(`![${file.name}](${url})`);
       }
   };
   ```

3. **Replace BraftEditor** (~1 ngày):
   - `admin/src/pages/article/components/modal.tsx`: replace
   - `admin/src/pages/news/components/modal.tsx`: replace
   - `admin/src/components/form-editor/index.tsx`: rewrite

4. **Migration data cũ** (~0.5 ngày):
   ```bash
   # Convert HTML → Markdown using turndown
   npm install turndown
   ```
   ```ts
   // scripts/migrate-html-to-markdown.ts
   import TurndownService from 'turndown';
   const turndown = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced' });
   // Loop through articles + news, convert content field
   ```
   - Dry-run mode trước khi commit
   - Backup data trước

5. **Frontend display** (~0.5 ngày):
   - Creator/user view: dùng `react-markdown` + `remark-gfm` để render
   - Sanitize XSS bằng `rehype-sanitize`

6. **Test** (~0.5 ngày):
   - Migration không corrupt data
   - Image upload flow
   - Preview match production rendering
   - Edge case: HTML phức tạp (table, embed) → Markdown fallback hoặc keep HTML inline

### Phase 2: TCB + Ambassador (~3-5 ngày mỗi)
- TCB dashboard (Next.js): cài `@uiw/react-md-editor` hoặc dùng `mdxeditor` (tương thích Next.js 16 tốt hơn)
- Ambassador (Umi): tương tự vCreator

**Total**: ~2-3 tuần.

## Risks + mitigations

1. **Migration HTML → Markdown loss data**: HTML phức tạp (table, custom div, inline style) có thể không convert được hoàn hảo
   - **Mitigation**: dry-run + diff sample bài viết trước khi commit. Fallback: cho phép Markdown chứa HTML inline (md-editor support)
2. **XSS injection**: Markdown vẫn cho phép HTML inline → attacker có thể inject script
   - **Mitigation**: sanitize bằng `rehype-sanitize` ở render side. Validate ở backend (strip dangerous tags)
3. **Image upload fail**: file lớn, format không hỗ trợ
   - **Mitigation**: validate size + format trước upload. Show progress + error message clear
4. **Preview vs production rendering mismatch**: editor preview dùng default md-editor, production có thể dùng custom plugins
   - **Mitigation**: dùng cùng renderer (react-markdown) ở cả 2 chỗ
5. **Backwards compatibility**: data cũ là HTML, migration chưa chạy → render lỗi
   - **Mitigation**: detect format (HTML vs Markdown) ở render, fallback dùng `dangerouslySetInnerHTML` cho HTML legacy

## Files referenced

**vCreator (đã có infrastructure)**:
- `admin/src/pages/article/components/modal.tsx` (BraftEditor — cần replace)
- `admin/src/pages/news/components/modal.tsx` (BraftEditor — cần replace)
- `admin/src/components/form-editor/index.tsx` (wrapper — cần rewrite)
- `admin/package.json` (`@uiw/react-md-editor` đã cài, `braft-editor` cần remove sau migration)
- `internal/model/mg/article.go` (Content field — string, không cần migration schema)

**TCB (cần verify chi tiết)**:
- `techcombank/dashboard/package.json` — chưa verify editor stack
- TCB dashboard là Next.js 16 → có thể cần `mdxeditor` hoặc tương đương

**Ambassador (cần verify chi tiết)**:
- `ambassabor/admin/package.json` — chưa verify

## Lịch sử phân loại

- **2026-05-10 (initial P1)**: User self-listed gap. Quote: "Đổi nội dung bài viết từ HTML sang markdown + upload ảnh / soạn bằng html rất tệ, không thể copy từ bài này qua bài kia mà giữ được định dạng / Lại khó dùng AI soạn thảo, preview cũng cực" + "P1".
  - Lý do P1: pain point rõ ràng, AI-driven workflow shift, vCreator có md-editor package sẵn, effort vừa phải. Pair tốt với #42 (cover image cache) cùng pattern image hosting.
