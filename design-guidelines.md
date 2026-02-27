# Design Guidelines - Ambassador Influencer Platform

**Version:** 1.0
**Last Updated:** 2026-02-06
**Status:** Production Standard
**Applies To:** Ambassador Platform, AT Core, Partner Instances

---

## 📋 Purpose

This document establishes the official design standards for the Ambassador Influencer Platform ecosystem. All designers, developers, and stakeholders MUST follow these guidelines to ensure consistency, accessibility, and brand integrity across all touchpoints.

---

## 🎨 Design Philosophy

### Core Principles

1. **AI-First, Human-Centered**
   - AI features are powerful but never overwhelming
   - Confidence indicators build trust
   - Transparency in AI decision-making

2. **Dark Mode by Default**
   - Reduces eye strain for long sessions
   - Modern, tech-forward aesthetic
   - OLED-optimized color choices

3. **Data as Storytelling**
   - Visualizations communicate insights, not just numbers
   - Progressive disclosure of complexity
   - Context-aware information hierarchy

4. **Performance as Feature**
   - <300ms transitions for perceived speed
   - Skeleton loading states for async content
   - Optimistic UI updates

5. **Accessibility is Mandatory**
   - WCAG 2.1 AA minimum, AAA target
   - Keyboard navigation always
   - Screen reader friendly from day one

---

## 🎨 Visual Identity

### Brand Colors

#### Primary Palette (AI-First Tech Brand)

```css
Electric Blue:   #0066FF  /* Primary actions, links, AI features */
Cyber Purple:    #9D00FF  /* Secondary, premium, advanced features */
Deep Teal:       #00A8A8  /* Tertiary, data insights, analytics */
```

**Usage Rules:**
- Electric Blue: Primary CTAs, active states, AI matching indicators
- Cyber Purple: Premium features, advanced AI, subscription tiers
- Deep Teal: Data visualization, analytics charts, insights

#### Background Colors (Dark Mode Optimized)

```css
Dark Background: #0F0F0F  /* Pure black areas, sidebars */
Soft Black:      #1A1A1A  /* Main canvas (reduces eye strain) */
Surface Card:    #2A2A2A  /* Elevated cards, lifted surfaces */
```

**Science:**
- Soft Black (#1A1A1A) reduces eye strain vs pure black (#000000)
- OLED displays: minimal power difference, better readability
- Surface elevation communicates information hierarchy

#### Accent Colors (Strategic Use Only)

```css
Neon Cyan:       #00FFFF  /* Highlights, live indicators, active states */
Magenta Neon:    #FF00FF  /* Warnings, urgent actions */
Toxic Green:     #39FF14  /* Success, positive growth, gains */
Orange Thermal:  #FF6600  /* Alerts, negative trends, losses */
```

**Usage Rules:**
- Use sparingly (max 10% of UI)
- Never as primary background colors
- Always with sufficient contrast

### Gradients

#### Primary Gradient (Brand Hero)

```css
background: linear-gradient(135deg, #0066FF 0%, #9D00FF 100%);
```

**Use Cases:**
- Hero sections
- Premium feature badges
- CTAs for conversion-critical actions
- Loading progress bars

#### Thermal Gradient (Data Ranges)

```css
background: linear-gradient(90deg, #FF6600 0%, #0066FF 50%, #00A8A8 100%);
```

**Use Cases:**
- Heatmaps (low to high performance)
- Score ranges (poor → average → good)
- Trend indicators

#### Bioluminescent Gradient (AI Features)

```css
background: linear-gradient(135deg, #00FFFF 0%, #9D00FF 50%, #FF00FF 100%);
```

**Use Cases:**
- AI-powered feature backgrounds
- Neural network visualizations
- Machine learning indicators

#### Mesh Gradients (Immersive Backgrounds)

```css
background:
  radial-gradient(circle at 20% 30%, rgba(0, 102, 255, 0.3) 0%, transparent 50%),
  radial-gradient(circle at 80% 70%, rgba(157, 0, 255, 0.3) 0%, transparent 50%),
  radial-gradient(circle at 50% 50%, rgba(0, 168, 168, 0.2) 0%, transparent 50%);
```

**Use Cases:**
- Hero sections
- Empty states
- Section dividers

---

## 🔤 Typography

### Font Stack

```css
/* Primary (UI, Data) */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace (Code, IDs) */
font-family: 'IBM Plex Mono', 'SF Mono', Monaco, monospace;
```

**Rationale:**
- **Inter:** Designed for UI, excellent legibility at small sizes
- **Apple System:** Native look on macOS/iOS
- **Segoe UI:** Native Windows 10+ experience

### Type Scale (8px-Based Rhythm)

| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--font-size-xs` | 12px | 1.5 (18px) | Metadata, timestamps, labels |
| `--font-size-sm` | 14px | 1.5 (21px) | Secondary text, table cells |
| `--font-size-base` | 16px | 1.5 (24px) | Body text, inputs |
| `--font-size-lg` | 18px | 1.6 (28.8px) | Emphasized text |
| `--font-size-xl` | 20px | 1.3 (26px) | Subtitles, card titles |
| `--font-size-2xl` | 24px | 1.3 (31.2px) | Section headers |
| `--font-size-3xl` | 32px | 1.2 (38.4px) | Page titles |
| `--font-size-4xl` | 40px | 1.2 (48px) | Hero titles |

### Font Weights

| Token | Weight | Usage |
|-------|--------|-------|
| `--font-weight-regular` | 400 | Body text, descriptions |
| `--font-weight-medium` | 500 | Labels, metadata |
| `--font-weight-semibold` | 600 | Buttons, emphasis |
| `--font-weight-bold` | 700 | Headings, titles |

### Typography Rules

1. **Never use font-size < 12px** (except for legal text with zoom option)
2. **Line length: 50-75 characters** for optimal readability
3. **Letter spacing:** Default for body, -0.02em for large headings
4. **All caps:** Only for labels <14px, max 2-3 words
5. **Italic:** Sparingly, never for UI (use color/weight for emphasis)

---

## 📏 Spacing & Layout

### Spacing Scale (8px-Based)

```css
--spacing-xs:   4px    /* Tight elements (icon + text) */
--spacing-sm:   8px    /* Form field gaps, small components */
--spacing-md:   16px   /* Default component spacing */
--spacing-lg:   24px   /* Section gaps within cards */
--spacing-xl:   32px   /* Card padding, form sections */
--spacing-2xl:  48px   /* Page sections */
--spacing-3xl:  64px   /* Hero sections, major dividers */
```

### Grid System

#### Desktop (1024px+)

```css
display: grid;
grid-template-columns: repeat(12, 1fr);
gap: 24px;
padding: 0 48px;
max-width: 1400px;
```

#### Tablet (640px - 1023px)

```css
grid-template-columns: repeat(8, 1fr);
gap: 16px;
padding: 0 32px;
```

#### Mobile (320px - 639px)

```css
grid-template-columns: repeat(4, 1fr);
gap: 12px;
padding: 0 16px;
```

### Responsive Breakpoints

| Name | Min Width | Max Width | Columns | Gap | Padding |
|------|-----------|-----------|---------|-----|---------|
| Mobile | 320px | 639px | 4 | 12px | 16px |
| Tablet | 640px | 1023px | 8 | 16px | 32px |
| Desktop | 1024px | 1399px | 12 | 24px | 48px |
| Wide | 1400px+ | - | 12 | 24px | 64px |

---

## 🎯 Components Standards

### Buttons

#### Variants

```css
/* Primary - Main actions */
.btn-primary {
  background: var(--gradient-primary);
  color: #FFFFFF;
}

/* Secondary - Supporting actions */
.btn-secondary {
  background: var(--color-surface-card);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

/* Outline - Tertiary actions */
.btn-outline {
  background: transparent;
  color: var(--color-electric-blue);
  border: 1px solid var(--color-electric-blue);
}

/* Ghost - Low-emphasis actions */
.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}

/* Danger - Destructive actions */
.btn-danger {
  background: var(--color-error);
  color: #FFFFFF;
}
```

#### Sizes

| Size | Height | Padding | Font Size |
|------|--------|---------|-----------|
| Small | 32px | 12px 16px | 14px |
| Medium | 40px | 12px 24px | 16px |
| Large | 48px | 16px 32px | 18px |

#### States

```css
/* Hover */
.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 102, 255, 0.3);
  transition: all 150ms ease;
}

/* Active */
.btn:active {
  transform: translateY(0);
}

/* Disabled */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Focus (Keyboard) */
.btn:focus-visible {
  outline: 2px solid var(--color-electric-blue);
  outline-offset: 2px;
}
```

### Cards

#### Base Card

```css
.card {
  background: var(--color-surface-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
}
```

#### Glassmorphism Card (Premium Features)

```css
.card-glass {
  background: rgba(42, 42, 42, 0.7);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

#### Interactive Card

```css
.card-interactive:hover {
  border-color: var(--color-electric-blue);
  box-shadow: 0 8px 32px rgba(0, 102, 255, 0.2);
  transform: translateY(-2px);
  transition: all 200ms ease;
}
```

### Forms

#### Input Fields

```css
.form-input {
  background: var(--color-soft-black);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
  color: var(--color-text-primary);
}

/* Focus State */
.form-input:focus {
  border-color: var(--color-electric-blue);
  outline: 2px solid rgba(0, 102, 255, 0.2);
  outline-offset: 0;
}

/* Error State */
.form-input.error {
  border-color: var(--color-error);
}
```

#### Labels

```css
.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
  display: block;
}
```

### Tables

#### Responsive Table

```css
.table {
  width: 100%;
  border-collapse: collapse;
}

.table thead {
  background: var(--color-surface-card);
  border-bottom: 2px solid var(--color-border);
}

.table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.table td {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
}

.table tbody tr:hover {
  background: rgba(0, 102, 255, 0.05);
}
```

---

## 🎬 Motion & Animation

### Timing Functions

```css
/* Fast Out, Slow In - Default for UI */
--ease-default: cubic-bezier(0.4, 0, 0.2, 1);

/* Ease Out - Entering elements */
--ease-out: cubic-bezier(0, 0, 0.2, 1);

/* Ease In - Exiting elements */
--ease-in: cubic-bezier(0.4, 0, 1, 1);
```

### Duration Standards

| Duration | Usage |
|----------|-------|
| 100ms | Icon rotations, simple state changes |
| 150ms | Button hovers, tooltip appear |
| 200ms | Card hovers, focus indicators |
| 300ms | Modal open/close, page transitions |
| 500ms | Complex animations (charts, graphs) |

### Animation Rules

1. **Never animate > 300ms** for UI interactions
2. **Use GPU-accelerated properties:** `transform`, `opacity`
3. **Avoid animating:** `width`, `height`, `margin`, `padding`
4. **Respect user preferences:**

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## ♿ Accessibility Standards

### WCAG 2.1 Compliance

#### Color Contrast (AA Minimum, AAA Target)

| Text Size | AA Ratio | AAA Ratio | Our Standard |
|-----------|----------|-----------|--------------|
| <18px normal | 4.5:1 | 7:1 | **7:1** ✅ |
| <14px bold | 4.5:1 | 7:1 | **7:1** ✅ |
| ≥18px normal | 3:1 | 4.5:1 | **4.5:1** ✅ |
| ≥14px bold | 3:1 | 4.5:1 | **4.5:1** ✅ |
| UI Components | 3:1 | - | **3:1** ✅ |

#### Keyboard Navigation

**Focus Indicators:**
```css
*:focus-visible {
  outline: 2px solid var(--color-electric-blue);
  outline-offset: 2px;
}
```

**Tab Order:**
- Logical flow (top → bottom, left → right)
- Skip links for main content
- Modal traps focus when open

#### Screen Reader Support

```html
<!-- Good Examples -->
<button aria-label="Close modal">×</button>
<img src="chart.png" alt="Monthly revenue chart showing 20% growth">
<input aria-describedby="email-error" aria-invalid="true">

<!-- Icons with labels -->
<span aria-hidden="true">🔍</span>
<span class="sr-only">Search</span>
```

---

## 📊 Data Visualization

### Chart Color Coding

```css
/* Positive Metrics (Growth, Success) */
--chart-positive: #39FF14;

/* Negative Metrics (Decline, Issues) */
--chart-negative: #FF6600;

/* Neutral Metrics */
--chart-neutral: #00A8A8;

/* Comparison Series */
--chart-series-1: #0066FF;
--chart-series-2: #9D00FF;
--chart-series-3: #00FFFF;
```

### Chart Typography

```css
/* Chart Title */
font-size: 18px;
font-weight: 600;
color: var(--color-text-primary);

/* Axis Labels */
font-size: 12px;
font-weight: 400;
color: var(--color-text-secondary);

/* Data Labels */
font-size: 14px;
font-weight: 500;
color: var(--color-text-primary);
```

---

## 🚀 Performance Guidelines

### Critical CSS (Inline in `<head>`)

```css
/* Design tokens, layout, above-fold components */
/* Target: <15KB */
```

### Deferred CSS (Load after initial render)

```css
/* Below-fold components, animations, extras */
```

### Image Optimization

1. **Format Priority:** WebP → PNG → JPG
2. **Compression:** 80-90% quality
3. **Responsive:** Use `<picture>` with breakpoints
4. **Lazy Loading:** `loading="lazy"` for below-fold
5. **Dimensions:** Always specify `width` and `height`

### Font Loading Strategy

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preload" as="font" href="/fonts/inter-var.woff2" type="font/woff2" crossorigin>
<style>
  @font-face {
    font-family: 'Inter';
    src: url('/fonts/inter-var.woff2') format('woff2');
    font-display: swap;
  }
</style>
```

---

## 🧪 Testing Standards

### Pre-Launch Checklist

#### Visual
- [ ] All colors meet WCAG AA contrast ratios
- [ ] Typography scale applied consistently
- [ ] Spacing follows 8px grid
- [ ] Responsive across all breakpoints (320px - 1920px)
- [ ] Dark mode optimized

#### Interaction
- [ ] All buttons have hover/active/focus states
- [ ] Forms show validation states
- [ ] Loading states for async actions
- [ ] Error states with helpful messages
- [ ] Success confirmations

#### Accessibility
- [ ] Keyboard navigation works end-to-end
- [ ] Screen reader tested (NVDA, JAWS, VoiceOver)
- [ ] ARIA labels for all icons
- [ ] Focus indicators visible
- [ ] Alt text for all images

#### Performance
- [ ] Lighthouse score 90+ (all categories)
- [ ] First Contentful Paint <1.5s
- [ ] Time to Interactive <3.5s
- [ ] No layout shifts (CLS <0.1)
- [ ] Images optimized and lazy-loaded

#### Cross-Browser
- [ ] Chrome latest
- [ ] Firefox latest
- [ ] Safari latest (macOS & iOS)
- [ ] Edge latest

---

## 📚 Resources & Tools

### Design Tools

- **Figma:** [Ambassador Platform Design System](link-to-figma)
- **Color Contrast Checker:** [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- **Accessibility Testing:** [axe DevTools](https://www.deque.com/axe/devtools/)
- **Performance Audit:** Chrome Lighthouse

### Documentation

- [Full Design Specification (92 pages)](/plans/20260205-api-logging-trace-id/reports/design-260206-ambassador-platform-ui-spec.md)
- [Research Report (AI Design Trends)](/plans/reports/researcher-260206-ai-influencer-platform-design-spec.md)
- [Component Showcase](/accesstrade-projects/ambassabor/design-showcase/index.html)

### Code References

- **Design System CSS:** `/ambassabor/design-showcase/assets/css/design-system.css`
- **Components CSS:** `/ambassabor/design-showcase/assets/css/components.css`
- **Example HTML:** `/ambassabor/design-showcase/index.html`

---

## 🔄 Updates & Versioning

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-06 | Initial guidelines established |

### Change Request Process

1. **Propose Change:** Create issue with rationale
2. **Design Review:** Design team evaluates impact
3. **Approval:** Requires 2+ design leads sign-off
4. **Update Guidelines:** Increment version, document changes
5. **Notify Teams:** Announce via Slack/Email

### Breaking Changes

Changes that require code updates across projects:
- Color token renaming
- Component API changes
- Spacing scale modifications

**Process:** Minimum 2-week notice + migration guide

---

## ✅ Quick Reference

### Must-Haves
✅ Use design tokens (never hard-coded colors/sizes)
✅ Follow 8px spacing grid
✅ WCAG AA minimum (AAA target)
✅ Test keyboard navigation
✅ Optimize images (WebP, lazy load)

### Never Do
❌ Pure black backgrounds (#000000)
❌ Font sizes <12px (except legal w/ zoom)
❌ Animations >300ms for UI
❌ Hard-coded colors (use CSS variables)
❌ Skip accessibility testing

---

**Document Owner:** Diso Design Team
**Maintained By:** AccessTrade Product
**Last Review:** 2026-02-06
**Next Review:** 2026-03-06

---

© 2026 AccessTrade. Internal use only.
