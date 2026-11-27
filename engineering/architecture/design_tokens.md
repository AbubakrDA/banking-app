# Design Tokens Specification — BankingAIPlatform

**Phase:** Phase 1 — UI Foundation  
**Task:** Task 1.2 — Design Tokens  
**Status:** ESTABLISHED & VERIFIED  

---

## 1. Aesthetic Baseline

The BankingAIPlatform design system adheres to the approved enterprise visual direction:
- **Application Canvas:** Light-grey background (`#F8FAFC`) providing gentle contrast.
- **Surfaces:** Clean white cards (`#FFFFFF`) with `12px` (`rounded-xl` / `rounded-card`) border radius.
- **Typography:** Deep Navy primary text (`#0B1D33`) with secondary slate (`#334E68`) and muted grey (`#627D98`).
- **Primary Accent:** Professional Teal (`#0D9488` with hover `#0F766E` and light tint `#F0FDFA`).
- **Secondary Accent:** Royal Blue (`#2563EB` with hover `#1D4ED8` and light tint `#EFF6FF`).
- **Restraint:** Subtle borders (`#E2E8F0`) and light shadows (`rgba(11, 29, 51, 0.06)`).
- **Icons:** Standardized on `lucide-react`.

---

## 2. Token Dictionary

### 2.1 Color Tokens (Light & Dark)

| Semantic Token | Light Mode Value | Dark Mode Value | Usage |
|---|---|---|---|
| `--color-canvas` | `#F8FAFC` | `#0B132B` | Application root background |
| `--color-surface` | `#FFFFFF` | `#1C2541` | Cards, tables, sidebars, panels |
| `--color-surface-subdued` | `#F1F5F9` | `#243054` | Table headers, secondary blocks |
| `--color-surface-hover` | `#F8FAFC` | `#29375F` | Interactive row/button hover |
| `--color-surface-selected`| `#F0FDFA` | `#133D48` | Active navigation item |
| `--color-text-primary` | `#0B1D33` (Navy) | `#F8FAFC` | Headings, primary text |
| `--color-text-secondary` | `#334E68` | `#CBD5E1` | Body paragraphs, labels |
| `--color-text-muted` | `#627D98` | `#94A3B8` | Timestamps, metadata, footnotes |
| `--color-accent-teal` | `#0D9488` | `#14B8A6` | Primary action buttons, active indicators |
| `--color-accent-teal-hover`| `#0F766E` | `#2DD4BF` | Primary button hover |
| `--color-accent-teal-light`| `#F0FDFA` | `#134E48` | Badge background, icon backgrounds |
| `--color-accent-blue` | `#2563EB` | `#3B82F6` | Secondary links, analytics highlights |
| `--color-accent-blue-light`| `#EFF6FF` | `#1E3A8A` | Secondary badges, active filters |
| `--color-status-success` | `#059669` | `#10B981` | Connected status, resolved tickets |
| `--color-status-warning` | `#D97706` | `#F59E0B` | In-progress, pending approval |
| `--color-status-danger` | `#DC2626` | `#EF4444` | Quarantined, errors, alerts |
| `--color-status-info` | `#2563EB` | `#3B82F6` | Informational callouts |
| `--color-border-subtle` | `#E2E8F0` | `#2D3748` | Card borders, dividers |
| `--color-border-default` | `#CBD5E1` | `#4A5568` | Form inputs, button outlines |

### 2.2 Border Radii Tokens

| Token | CSS Value | Visual Standard |
|---|---|---|
| `--radius-sm` | `0.375rem` (6px) | Badges, small pills, tags |
| `--radius-md` | `0.5rem` (8px) | Buttons, form inputs, dropdowns |
| `--radius-card` | `0.75rem` (12px) | Standard BankingAIPlatform rounded card |
| `--radius-xl` | `1.0rem` (16px) | Modals, drawers, hero banners |
| `--radius-full` | `9999px` | Circular avatars, status pills |

### 2.3 Shadow Tokens

| Token | CSS Shadow Specification | Visual Standard |
|---|---|---|
| `--shadow-subtle` | `0 1px 2px 0 rgba(11, 29, 51, 0.04)` | Flat surface boundary |
| `--shadow-card` | `0 1px 3px 0 rgba(11, 29, 51, 0.06), 0 1px 2px -1px rgba(11, 29, 51, 0.04)` | Standard card elevation |
| `--shadow-card-hover` | `0 4px 6px -1px rgba(11, 29, 51, 0.08), 0 2px 4px -2px rgba(11, 29, 51, 0.04)` | Hover lift state |
| `--shadow-elevation` | `0 10px 15px -3px rgba(11, 29, 51, 0.08), 0 4px 6px -4px rgba(11, 29, 51, 0.04)` | Modal & popover elevation |

---

## 3. Reference Image Inspection Notice

- **Workspace Inspection:** Conducted search across workspace and local paths. No reference image files were found.
- **Formal Status:** The user has been notified to supply the approved UI reference images if they wish to refine specific module layouts beyond this agreed baseline before Task 1.3 execution.
