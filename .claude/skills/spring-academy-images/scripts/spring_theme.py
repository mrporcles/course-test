"""Spring Academy image renderer.

Renders HTML/SVG snippets to trimmed 2x PNGs in the Spring Academy (penguin) look,
using headless Chrome. Palette, font and radii come from vmware-tanzu-learning/penguin
(tailwind.config.js, spring-light-theme/instructions.css, resources/fonts/metropolis).

Usage (from a script that lives anywhere):
    import sys; sys.path.insert(0, "<skill>/scripts")
    from spring_theme import *
    render(code(SRC, callouts, arrows) , "out.png")
"""
import html, json, os, re, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "assets", "fonts")

CHROME = os.environ.get("CHROME_BIN") or next((p for p in [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chrome") or "",
] if p and os.path.exists(p)), None)

# --- palette (see references/palette.md) ---
GREEN, GREEN_DARK, GREEN_LIGHT = "#6db33f", "#325c14", "#e1efd8"
INK, TEXT, MUTED, LINE, PANEL = "#18181b", "#52525b", "#71717a", "#e4e4e7", "#f4f4f5"
INFO, INFO_BG, INFO_BORDER, INFO_INK = "#0063cc", "#edf6ff", "#b1d7ff", "#00346b"
ARROW = "#52525b"

# code metrics (px at 1x): used to position callouts by (line, column)
FS, LH, PADX, PADY = 22, 34, 24, 20
CW = FS * 0.602  # Menlo advance width


def _fonts():
    out = ""
    for name, w in (("Regular", 400), ("Medium", 500), ("SemiBold", 600)):
        p = os.path.abspath(os.path.join(FONT_DIR, f"Metropolis-{name}.woff2"))
        out += f"@font-face{{font-family:'Metropolis';font-weight:{w};src:url('file://{p}') format('woff2')}}"
    return out


CSS = _fonts() + f"""
*{{box-sizing:border-box;margin:0}}
body{{width:1280px;background:#fff;color:{INK};font-family:'Metropolis',sans-serif;font-weight:500;padding:28px 40px}}
.code{{position:relative;background:{PANEL};border-radius:4px;box-shadow:0 3px 8px -1px rgba(0,0,0,.05);padding:{PADY}px {PADX}px;
 font-family:Menlo,monospace;font-size:{FS}px;line-height:{LH}px;white-space:pre;color:{TEXT}}}
.k{{color:{GREEN_DARK};font-weight:700}}.s{{color:{INFO}}}.c{{color:{MUTED};font-style:italic}}.a{{color:#a16207;font-weight:700}}
.em{{background:{GREEN_LIGHT};color:{INK};font-weight:700;border-radius:3px}}
.call{{position:absolute;background:#fff;border:1.5px solid #6aae3d;border-radius:8px;box-shadow:0 3px 8px -1px rgba(0,0,0,.08);
 padding:8px 16px;font:600 20px/1.3 'Metropolis',sans-serif;text-align:center;color:{INK};white-space:nowrap}}
.note{{display:flex;gap:18px;align-items:center;background:{INFO_BG};border:1px solid {INFO_BORDER};border-radius:6px;padding:14px 24px;
 font:500 24px/1.4 'Metropolis',sans-serif;color:{INFO_INK};margin-top:22px}}
.note:before{{content:'i';flex:none;width:34px;height:34px;border-radius:50%;background:{INFO};color:#fff;font:italic 700 22px Georgia,serif;text-align:center;line-height:34px}}
.note code{{font-family:Menlo,monospace;font-weight:700;font-size:.9em}}
ul.b{{list-style:none;padding:0;font-size:36px;line-height:1.3}}
ul.b>li{{position:relative;padding:18px 24px 18px 64px;margin-bottom:14px;background:#fafafa;border:1px solid {LINE};border-radius:6px}}
ul.b>li:before{{content:'';position:absolute;left:26px;top:30px;width:16px;height:16px;border-radius:50%;background:{GREEN}}}
.box{{position:absolute;display:flex;align-items:center;justify-content:center;text-align:center;font:600 25px/1.25 'Metropolis',sans-serif;
 color:#fff;border-radius:6px;box-shadow:0 3px 8px -1px rgba(0,0,0,.15)}}
.box.primary{{background:{GREEN}}}.box.dark{{background:{GREEN_DARK}}}.box.ink{{background:{INK}}}.box.info{{background:{INFO}}}
.box.outline{{background:#fff;color:{INK};border:1.5px solid {GREEN};box-shadow:none}}
.lbl{{position:absolute;font:500 26px 'Metropolis',sans-serif;color:{TEXT}}}
svg{{position:absolute;left:0;top:0;overflow:visible}}
svg text{{font-family:'Metropolis',sans-serif!important;fill:{INK}}}
"""

ARROWDEF = (f'<defs><marker id="ah" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">'
            f'<path d="M0,0L12,6L0,12z" fill="{ARROW}"/></marker></defs>')


def X(col): return PADX + col * CW      # px x of a code column inside a code() block
def Y(line): return PADY + line * LH    # px y of a code line's top


def hl(src):
    """Tiny Java highlighter. Wrap text in [[...]] to emphasise it (green highlight)."""
    kw = r'\b(public|class|implements|new|return|this|extends|interface|private|static|void|import|package|final|throws)\b'
    pat = re.compile(r'(//[^\n]*)|("(?:[^"\\]|\\.)*")|(@[A-Z]\w*)|' + kw + r'|(\[\[|\]\])')
    out, pos = [], 0
    for m in pat.finditer(src):
        out.append(html.escape(src[pos:m.start()])); t = m.group(0)
        if m.group(1): out.append(f'<span class="c">{html.escape(t)}</span>')
        elif m.group(2): out.append(f'<span class="s">{html.escape(t)}</span>')
        elif m.group(3): out.append(f'<span class="a">{html.escape(t)}</span>')
        elif m.group(4): out.append(f'<span class="k">{t}</span>')
        else: out.append('<span class="em">' if t == '[[' else '</span>')
        pos = m.end()
    out.append(html.escape(src[pos:]))
    return ''.join(out)


def code(src, calls=(), arrows=(), style=''):
    """Code card. calls: (html, x, y, width) callouts (x<0 => offset from right edge).
    arrows: (x1, y1, x2, y2) in px inside the card; use X(col)/Y(line) for positions."""
    n = src.replace('[[', '').replace(']]', '').count('\n') + 1
    h = n * LH + 2 * PADY
    svg = ''.join(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{ARROW}" stroke-width="2" marker-end="url(#ah)"/>' for a, b, c, d in arrows)
    cs = ''.join(f'<div class="call" style="{"right:%dpx" % -x if x < 0 else "left:%dpx" % x};top:{y}px;width:{w}px">{t}</div>' for t, x, y, w in calls)
    return f'<div class="code" style="height:{h}px;{style}"><svg width="100%" height="{h}">{ARROWDEF}{svg}</svg>{hl(src)}{cs}</div>'


def bullets(*items):
    """Bullet list card. An item may be a string or (string, [sub items])."""
    li = ''.join(f'<li>{i}</li>' if isinstance(i, str) else f'<li>{i[0]}<ul>{"".join(f"<li>{s}</li>" for s in i[1])}</ul></li>' for i in items)
    return f'<ul class="b">{li}</ul>'


def note(text):
    return f'<div class="note"><div>{text}</div></div>'


def box(text, x, y, w, h, kind="primary", extra=""):
    return f'<div class="box {kind}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra}">{text}</div>'


def line(x1, y1, x2, y2, arrow=True):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="2"'
            + (' marker-end="url(#ah)"' if arrow else '') + '/>')


def diagram(width, height, parts, svg_parts=""):
    """Absolute-positioned canvas: parts = html (box()/lbl divs), svg_parts = line()/rect strings."""
    return (f'<div style="position:relative;width:{width}px;height:{height}px"><svg width="{width}" height="{height}">'
            f'{ARROWDEF}{svg_parts}</svg>{parts}</div>')


_MEASURE = """<script>
document.fonts.ready.then(()=>{let l=1e9,r=0,b=0;
 for(const e of document.body.querySelectorAll('*')){
  if(e.tagName.toLowerCase()==='svg'||e.closest('defs,marker,script,pre#bb'))continue;
  const c=getComputedStyle(e),painted=c.backgroundColor!=='rgba(0, 0, 0, 0)'||parseFloat(c.borderTopWidth)>0||parseFloat(c.borderLeftWidth)>0||c.boxShadow!=='none';
  if(e.children.length&&!painted)continue;           // skip transparent layout containers
  const q=e.getBoundingClientRect();if(!q.width&&!q.height)continue;
  l=Math.min(l,q.left);r=Math.max(r,q.right);b=Math.max(b,q.bottom);}
 const o=document.createElement('pre');o.id='bb';o.textContent=JSON.stringify({l,r,b});document.body.appendChild(o);});
</script>"""


def _chrome(args, page_path):
    return subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                           *args, "file://" + page_path], check=True, capture_output=True, text=True)


def render(body, dest, scale=2):
    """Screenshot `body` HTML to dest (PNG), cropped to the content (no Pillow needed). Returns dest."""
    if not CHROME: raise RuntimeError("Chrome not found; set CHROME_BIN to a Chrome/Chromium binary")
    tmp = tempfile.mkdtemp()
    try:
        # pass 1: measure the content's bounding box
        p1 = os.path.join(tmp, "m.html")
        open(p1, "w").write(f"<!doctype html><meta charset=utf-8><style>{CSS}</style><body>{body}</body>{_MEASURE}")
        dom = _chrome(["--window-size=1280,4000", "--virtual-time-budget=3000", "--dump-dom"], p1).stdout
        bb = json.loads(re.search(r'<pre id="bb">(.*?)</pre>', dom, re.S).group(1).replace("&quot;", '"'))
        shift = bb["l"] - 40                      # keep 40px of left margin
        width = int(bb["r"] - bb["l"] + 80)       # 40px each side
        height = int(bb["b"] + 60)
        # pass 2: shift content left and screenshot at the exact size
        p2 = os.path.join(tmp, "r.html")
        open(p2, "w").write(f"<!doctype html><meta charset=utf-8><style>{CSS}html{{overflow:hidden}}body{{position:relative;left:-{shift}px}}</style><body>{body}</body>")
        _chrome([f"--force-device-scale-factor={scale}", f"--window-size={width},{height}", f"--screenshot={dest}"], p2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dest
