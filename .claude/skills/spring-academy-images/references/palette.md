# Spring Academy theme reference

Source: `vmware-tanzu-learning/penguin` (private; read with `gh api repos/vmware-tanzu-learning/penguin/contents/<path> -H 'Accept: application/vnd.github.raw'`).
`resources/css/spring.css` itself only sets hero backgrounds and icon SVGs; the actual tokens live in:

| File | What it gives |
|---|---|
| `tailwind.config.js` | font `metropolis-web`, `success` (green), `info` (blue), `warning`, `error` scales, shadows |
| `public/educates/spring-light-theme/instructions.css` | lesson content styling: code blocks, inline code, blockquote, `img` |
| `resources/fonts/metropolis/*.woff2` | Metropolis (copied to `assets/fonts/`) |
| `resources/img/spring/*.svg` | brand art; `logo-icon.svg` = `#6aae3d`, hero art uses `#80ea6e`, `#ceed7a`, `#c9a7ff`, `#9dfeef`, ink `#18181b` |

## Tokens used by `spring_theme.py`

| Role | Value | Origin |
|---|---|---|
| Spring green (primary boxes, bullets) | `#6db33f` (`#6aae3d` for outlines) | logo / success-500 |
| Dark green (secondary boxes, keywords) | `#325c14` | success-700 |
| Light green (highlight bg) | `#e1efd8` | success-100 |
| Ink (headings, labels) | `#18181b` | zinc-900 |
| Body / code text, arrows | `#52525b` | gray-600 |
| Muted (comments) | `#71717a` | zinc-500 |
| Borders | `#e4e4e7` | gray-200 |
| Code / panel bg | `#f4f4f5` | gray-100 (instructions.css `pre`) |
| Info note | bg `#edf6ff`, border `#b1d7ff`, text `#00346b`, icon `#0063cc` | info scale |
| Radius | 4px (`0.25rem`); notes 6px, callouts 8px | instructions.css |
| Image shadow | `0 3px 8px -1px rgb(0 0 0 / .05)` | `.rendered-content img` |
| Font | Metropolis 400/500/600; code in Menlo | tailwind + fonts dir |

Optional accent pastels for extra series colors in busy diagrams: `#ceed7a`, `#c9a7ff`, `#9dfeef` (use sparingly, with ink text).
Warnings `#ca8a04`, errors `#b2223b` (from instructions.css) for exception/failure arrows.
