# Design — Clary (AskFirst design language)

## Product context
- **What:** Cross-conversation health pattern reasoner for the Ask First platform.
- **Reference:** askfirst.co/main — adopting their visual language so this submission feels native to their brand.
- **Project type:** Streamlit web app.

## Memorable thing
The reasoner should feel like a piece of AskFirst's own product, not a third-party tool bolted on.

## Aesthetic direction
**AskFirst consumer-modern.** Bright, friendly, trustworthy. Pure white surfaces, cobalt-blue accent, black for strong CTAs, fully-rounded pill controls. Warm but professional.

## Typography
- **Display + body:** `DM Sans` — geometric humanist sans, friendly and modern. Matches the AskFirst wordmark feel. Loaded from Google Fonts.
- **Data / code / reasoning traces:** `JetBrains Mono` — tabular numerals for week offsets and session IDs.

## Color tokens
| Token | Hex | Where it appears |
|---|---|---|
| `--bg` | `#FFFFFF` | Page background |
| `--surface` | `#FFFFFF` | Cards, metrics, chat bubbles |
| `--surface-alt` | `#F7F8FA` | Code blocks, expanders |
| `--border` | `#E5E7EB` | All hairline dividers |
| `--text` | `#0F1729` | Primary text (deep navy, not pure black) |
| `--muted` | `#6B7280` | Captions, labels |
| `--accent` | `#1A6CFF` | Cobalt blue. Sidebar logo, active tab, links, primary-button hover |
| `--accent-soft` | `#EEF2FF` | Session-ID chips, info card backgrounds |
| `--cta` | `#0A0A0A` | Primary "Run pattern analysis" button (matches AskFirst Logout button) |
| `--high` | `#059669` on `#D1FAE5` | Confidence badge — high |
| `--med` | `#D97706` on `#FEF3C7` | Confidence badge — medium |
| `--low` | `#DC2626` on `#FEE2E2` | Confidence badge — low |

## Shape language
- **Buttons:** fully rounded pills (border-radius: 999px). Matches AskFirst's "Logout" / "Ask AI" / "Join" buttons.
- **Cards:** 16px rounded corners with 1px borders and a subtle 0 1px 3px shadow. Hover lifts the shadow and shifts border to soft-blue.
- **Chips / session IDs:** fully rounded pills with cobalt-soft backgrounds (`#EEF2FF` bg, `#1A6CFF` text).
- **Chat input:** fully rounded pill with cobalt focus ring.

## Layout
- Sidebar: white with hairline right border. Logo "Clary" rendered in cobalt italic to echo the AskFirst wordmark.
- Main: max-width 1280px, 2.5rem top padding.
- Pattern cards: vertical stack, 12px gap.
- Chat: 2:1 split (conversation : reasoning trace drawer).

## Spacing
- Base unit: 8px. Card padding: 24–28px. Card radius: 16px. Pill radius: 999px.

## Motion
Streamlit-owned. The only custom transitions are the pattern-card hover (border + shadow, 150ms) and button hover (background + border, 150ms).

## Risks / departures
1. **Cobalt blue instead of clinical blue.** Differentiates from EHR aesthetics while staying brand-consistent with AskFirst.
2. **Black primary CTA** instead of the more common blue. Matches AskFirst's Logout button — visually punchy, demands attention without competing with the cobalt accent.
3. **Pure white background** instead of off-white. Higher visual contrast for the data-dense pattern cards; matches AskFirst's main feed.

## Implementation
- `.streamlit/config.toml` — `primaryColor = "#1A6CFF"`, `backgroundColor = "#FFFFFF"`, `textColor = "#0F1729"`.
- `app.py` — single `<style>` injection block at top after `set_page_config`. DM Sans + JetBrains Mono via Google Fonts `@import`.

## Decisions log
| Date | Decision | Rationale |
|---|---|---|
| 2026-04-25 | Initial clinic aesthetic (sage on cream) | Generic clinic feel |
| 2026-04-25 | **Switched to AskFirst design language** | Reviewer screenshot of askfirst.co/main showed cobalt + black + white + DM Sans + pill buttons. Design now native to the host brand |
