---
name: spring-academy-images
description: Render diagrams, annotated code cards, bullet cards and info notes as PNGs in the Spring Academy (penguin) visual style - Spring green palette, zinc greys, Metropolis font, 4px radii, soft shadows. Use when creating or restyling course images/diagrams/slides for Spring Academy lessons, replacing VMware slide screenshots, or when asked to match the spring.academy / penguin theme.
---

# Spring Academy image rendering

Renders HTML/SVG to trimmed 2x PNGs via headless Chrome with the look taken from `vmware-tanzu-learning/penguin` (see `references/palette.md` for exact tokens and where they came from; note `spring.css` itself only has hero backgrounds - the palette is in `tailwind.config.js` and `spring-light-theme/instructions.css`).

## Requirements
- Only external requirements: Python 3 (standard library only, no pip packages) and Google Chrome/Chromium (macOS path and `google-chrome`/`chromium` on PATH auto-detected; otherwise set `CHROME_BIN`).
- Everything else is bundled in this folder: `scripts/` (renderer + example), `assets/fonts/` (Metropolis from the penguin repo) and `references/palette.md`. No network access or penguin repo access is needed to use it.

## Workflow
1. **Decide whether the image should exist.** Diagrams, sequence/flow charts, timelines, architecture and tables are worth an image. Slides that only show code or bullets already in the lesson's markdown should be deleted (remove the `![](images/x.png)` line too) rather than restyled. Real IDE/console/browser screenshots: leave alone.
2. **Write a small script** (keep it outside the course folder, e.g. in a scratch dir) that does `sys.path.insert(0, "<this skill>/scripts")`, `from spring_theme import *`, and calls `render(html, dest)`. Start from `scripts/example.py` (diagram, code card with callout, bullet list).
3. **Keep the original filename and path** when replacing an image so markdown links still resolve.
4. **Read every render back** (view the PNG) and fix clipped text, overlapping labels, and arrows that miss their target. Re-render.
5. After deleting or renaming images, check every `images/` link in the lesson's `.md` files still resolves.

## Building blocks (`scripts/spring_theme.py`)
- `diagram(w, h, parts, svg_parts)` + `box(text, x, y, w, h, kind)` + `line(x1,y1,x2,y2)`: absolute-positioned box-and-arrow canvas. `kind`: `primary` (Spring green), `dark` (dark green), `ink`, `info` (blue), `outline`.
- `code(src, calls, arrows)`: grey code card with Java highlighting. Wrap text in `[[ ]]` to highlight. Position callouts/arrows by code coordinates with `X(col)` / `Y(line)`. Callout tuple: `(html, x, y, width)`; arrow tuple: `(x1, y1, x2, y2)`. Make callout width generous (text does not wrap).
- `bullets("a", ("b", ["sub1", "sub2"]))`, `note("html")` (blue info box).
- `render(body, dest, scale=2)`: measures the content in Chrome, then screenshots cropped to it with a 40px margin. Compose several blocks by concatenating HTML strings (e.g. `code(...) + note(...)`).
- For sequence diagrams, build with `diagram()`: lifelines as dashed `line()`s (extend by writing raw SVG into `svg_parts`), header `box(..., "dark")`, arrows in the default grey, return arrows dashed. Keep labels above their arrow.

## Style rules
- White background, no slide title/footer/slide number, no VMware branding; crop tight.
- Primary elements Spring green, supporting elements dark green or ink; use blue only for info/notes; arrows `#52525b`.
- Text in Metropolis; code in Menlo; never use pure black borders or hard 1px black outlines.
- Don't invent content: reproduce the labels and relationships from the source slide/lesson text.

## Gotchas
- Fonts are loaded via `file://` URLs, so keep `assets/fonts/` next to `scripts/`.
- `--window-size` height is fixed at 2400px; very tall images need a bump in `render()`.
