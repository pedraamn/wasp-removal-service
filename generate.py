#!/usr/bin/env python3
"""
Static site generator (no JS) for a single-service, multi-city site.

Cloudflare Pages:
- Build command: (empty)
- Output directory: public

URL structure:
- /<city>-<state>/   e.g. /los-angeles-ca/
- /cost/
- /how-to/

SEO rules enforced:
- Exactly one H1 per page
- <title> == H1
- Title <= 70 characters
- Main + City pages use the exact same H2 set (Ahrefs-driven)
- Cost and How-To use distinct H2 sets (no reused headings across them)
- Pure CSS, barebones, fast
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import html
import re
import shutil


# -----------------------
# CONFIG
# -----------------------
@dataclass(frozen=True)
class SiteConfig:
    service_name: str = "Wasp Nest/Wasp Hive Removal & Wasp Control Services"
    brand_name: str = "Wasp Nest Removal Company"
    cta_text: str = "Get Free Estimate"
    cta_href: str = "mailto:hello@example.com?subject=Free%20Quote%20Request"
    output_dir: Path = Path("public")
    image_filename: str = "picture.png"  # sits next to generate.py
    cost_low: int = 150
    cost_high: int = 450


CONFIG = SiteConfig()

CITIES: list[tuple[str, str]] = [
    ("Los Angeles", "CA"),
    ("New York", "NY"),
    ("Chicago", "IL"),
    ("Houston", "TX"),
    ("Phoenix", "AZ"),
    ("Philadelphia", "PA"),
    ("San Antonio", "TX"),
    ("San Diego", "CA"),
    ("Dallas", "TX"),
    ("San Jose", "CA"),
    ("Austin", "TX"),
    ("Jacksonville", "FL"),
    ("Fort Worth", "TX"),
    ("Columbus", "OH"),
    ("Charlotte", "NC"),
    ("San Francisco", "CA"),
    ("Indianapolis", "IN"),
    ("Seattle", "WA"),
    ("Denver", "CO"),
    ("Washington", "DC"),
]

# -----------------------
# Ahrefs-driven headings (US) — grouped
# -----------------------
H2_SHARED = [
    "Wasp Nest Removal",
    "Wasp Control",
    "Wasp Exterminator",
    "Paper Wasp Nest Removal",
    "Ground Wasp Nest Removal",
    "Wasp Removal",
]

H2_COST = [
    "Wasp Nest Removal Cost",
    "How Much Does It Cost to Remove a Wasp Nest",
    "Cost of Wasp Nest Removal",
    "Wasp Removal Cost",
    "Wasp Nest Removal Price",
    "Hornet Nest Removal Cost",
]

H2_HOWTO = [
    "How to Get Rid of Wasp Nest",
    "How to Remove Wasp Nest",
    "Remove Wasp Nest",
    "Best Time to Spray Wasp Nest",
    "Wasp Spray",
    "What Kills Wasps",
]

ALSO_MENTIONED = [
    "pest control",
    "spray",
    "spray bottle",
    "dish soap",
    "wasp stings",
    "price",
    "removal",
    "nest",
    "wasp",
]


# -----------------------
# HELPERS
# -----------------------
def esc(s: str) -> str:
    return html.escape(s, quote=True)


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"&", " and ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def city_state_slug(city: str, state: str) -> str:
    return f"{slugify(city)}-{slugify(state)}"


def clamp_title(title: str, max_chars: int = 70) -> str:
    if len(title) <= max_chars:
        return title
    return title[: max_chars - 1].rstrip() + "…"


def city_h1(service: str, city: str, state: str) -> str:
    return clamp_title(f"{service} in {city}, {state}", 70)


def write_text(out_path: Path, content: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")


def reset_output_dir(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)


def copy_site_image(*, src_dir: Path, out_dir: Path, filename: str) -> None:
    src = src_dir / filename
    if not src.exists():
        raise FileNotFoundError(f"Missing image next to generate.py: {src}")
    shutil.copyfile(src, out_dir / filename)


# -----------------------
# THEME (pure CSS, minimal, fast — upgraded look)
# -----------------------
CSS = """
:root{
  /* Core */
  --bg: #0b1220;
  --bg2:#070b14;
  --surface: rgba(255,255,255,0.06);
  --surface2: rgba(255,255,255,0.085);
  --card: rgba(255,255,255,0.075);
  --ink: #e8eefc;
  --muted: rgba(232,238,252,0.72);
  --muted2: rgba(232,238,252,0.62);
  --line: rgba(232,238,252,0.12);

  /* Brand accent */
  --accent: #38bdf8;
  --accent2:#22c55e;
  --accent3:#a78bfa;

  /* Layout */
  --max: 980px;
  --radius: 16px;
  --radius2: 22px;
  --shadow: 0 16px 45px rgba(0,0,0,0.40);
  --shadow2: 0 10px 26px rgba(0,0,0,0.28);
}

*{box-sizing:border-box}
html{color-scheme:dark}
body{
  margin:0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
  color:var(--ink);
  background:
    radial-gradient(900px 450px at 18% -10%, rgba(56,189,248,0.22), transparent 60%),
    radial-gradient(800px 420px at 92% 0%, rgba(167,139,250,0.18), transparent 55%),
    radial-gradient(900px 520px at 40% 110%, rgba(34,197,94,0.12), transparent 60%),
    linear-gradient(180deg, var(--bg), var(--bg2));
  line-height:1.6;
}

a{color:inherit}
a:focus{outline:2px solid var(--accent); outline-offset:3px}

/* Topbar */
.topbar{
  position:sticky;
  top:0;
  z-index:50;
  background: rgba(7,11,20,0.70);
  backdrop-filter: blur(10px);
  border-bottom:1px solid var(--line);
}
.topbar-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:12px 18px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
}
.brand{
  display:flex;
  align-items:center;
  gap:10px;
  font-weight:900;
  letter-spacing:-0.02em;
  text-decoration:none;
  white-space:nowrap;
}
.brand-mark{
  width:26px;
  height:26px;
  border-radius:9px;
  background:
    radial-gradient(circle at 30% 20%, rgba(255,255,255,0.30), transparent 45%),
    linear-gradient(135deg, rgba(56,189,248,0.85), rgba(167,139,250,0.65));
  box-shadow: 0 10px 26px rgba(0,0,0,0.30);
  border:1px solid rgba(255,255,255,0.18);
}
.nav{
  display:flex;
  align-items:center;
  gap:10px;
  flex-wrap:wrap;
  justify-content:flex-end;
}
.nav a{
  text-decoration:none;
  font-size:13px;
  color:var(--muted);
  padding:8px 10px;
  border-radius:12px;
  border:1px solid transparent;
  transition: transform .14s ease, background .14s ease, border-color .14s ease, color .14s ease;
}
.nav a:hover{
  color:var(--ink);
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,255,255,0.10);
  transform: translateY(-1px);
}
.nav a[aria-current="page"]{
  color:var(--ink);
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.14);
}

/* Buttons */
.btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  padding:10px 13px;
  background:
    linear-gradient(135deg, rgba(56,189,248,0.95), rgba(167,139,250,0.75));
  color:#04101f;
  border-radius:13px;
  text-decoration:none;
  font-weight:900;
  font-size:13px;
  border:1px solid rgba(255,255,255,0.22);
  box-shadow: 0 14px 30px rgba(0,0,0,0.35);
  transition: transform .14s ease, box-shadow .14s ease, filter .14s ease;
}
.btn:hover{ transform: translateY(-1px); filter: brightness(1.02); box-shadow: 0 18px 40px rgba(0,0,0,0.42); }
.btn:focus{ outline:2px solid var(--accent); outline-offset:3px; }

/* Hero */
header{
  border-bottom:1px solid var(--line);
  background:
    radial-gradient(850px 260px at 12% 10%, rgba(56,189,248,0.18), transparent 60%),
    radial-gradient(700px 280px at 96% 25%, rgba(167,139,250,0.14), transparent 58%),
    rgba(255,255,255,0.02);
}
.hero{
  max-width:var(--max);
  margin:0 auto;
  padding:30px 18px 22px;
  display:grid;
  gap:12px;
}
.kicker{
  display:flex;
  align-items:center;
  gap:10px;
  flex-wrap:wrap;
}
.pill{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:6px 11px;
  border-radius:999px;
  font-size:12px;
  font-weight:900;
  background: rgba(255,255,255,0.06);
  border:1px solid rgba(255,255,255,0.14);
  color:var(--muted);
}
.pill-dot{
  width:8px;
  height:8px;
  border-radius:99px;
  background: linear-gradient(135deg, var(--accent), var(--accent3));
  box-shadow: 0 0 0 3px rgba(56,189,248,0.12);
}
.hero h1{
  margin:0;
  font-size:30px;
  letter-spacing:-0.03em;
  line-height:1.14;
}
.sub{
  margin:0;
  color:var(--muted);
  max-width:76ch;
  font-size:14px;
}
.hero-cta{
  display:flex;
  align-items:center;
  gap:10px;
  flex-wrap:wrap;
  margin-top:6px;
}
.ghost{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:10px 12px;
  border-radius:13px;
  border:1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.04);
  color:var(--ink);
  text-decoration:none;
  font-weight:800;
  font-size:13px;
  transition: transform .14s ease, background .14s ease, border-color .14s ease;
}
.ghost:hover{ transform: translateY(-1px); background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.18); }

main{
  max-width:var(--max);
  margin:0 auto;
  padding:22px 18px 46px;
}

/* Card / content */
.card{
  background: linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.05));
  border:1px solid rgba(255,255,255,0.14);
  border-radius:var(--radius2);
  padding:18px;
  box-shadow: var(--shadow);
}
.card-inner{
  padding-top:10px;
}
.img{
  margin-top:12px;
  border-radius:14px;
  overflow:hidden;
  border:1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.03);
  box-shadow: var(--shadow2);
}
.img img{display:block; width:100%; height:auto}

h2{
  margin:18px 0 8px;
  font-size:16px;
  letter-spacing:-0.01em;
}
p{margin:0 0 10px}
.muted{color:var(--muted2); font-size:13px}
hr{
  border:0;
  border-top:1px solid rgba(255,255,255,0.12);
  margin:18px 0;
}

/* City list */
.city-grid{
  list-style:none;
  padding:0;
  margin:10px 0 0;
  display:grid;
  gap:10px;
  grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
}
.city-grid a{
  display:block;
  text-decoration:none;
  color:var(--ink);
  background: rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.12);
  border-radius:14px;
  padding:11px 12px;
  font-weight:800;
  font-size:14px;
  transition: transform .14s ease, background .14s ease, border-color .14s ease;
}
.city-grid a:hover{
  transform: translateY(-1px);
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,255,255,0.18);
}

/* Conversion callout (city pages) */
.callout{
  margin-top:14px;
  padding:12px 12px;
  border-radius:16px;
  border:1px solid rgba(56,189,248,0.22);
  background:
    radial-gradient(500px 200px at 10% 20%, rgba(56,189,248,0.18), transparent 55%),
    rgba(255,255,255,0.04);
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:12px;
}
.callout strong{
  display:block;
  font-size:13px;
  letter-spacing:-0.01em;
  margin-bottom:2px;
}
.callout p{
  margin:0;
  color:var(--muted);
  font-size:13px;
}
.callout .btn{
  white-space:nowrap;
  box-shadow:none;
  border-color: rgba(255,255,255,0.22);
}

/* Footer */
footer{
  border-top:1px solid var(--line);
  background: rgba(255,255,255,0.02);
}
.footer-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:28px 18px;
  display:grid;
  gap:12px;
}
.footer-cta{
  background:
    radial-gradient(700px 220px at 12% 10%, rgba(34,197,94,0.14), transparent 55%),
    radial-gradient(700px 240px at 92% 30%, rgba(56,189,248,0.14), transparent 55%),
    rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.12);
  border-radius:18px;
  padding:16px;
  box-shadow: var(--shadow2);
}
.footer-cta h2{margin:0 0 6px; font-size:18px}
.footer-links{display:flex; gap:12px; flex-wrap:wrap}
.footer-links a{color:var(--muted); text-decoration:none; font-size:13px; padding:6px 0}
.footer-links a:hover{color:var(--ink)}
.small{color:var(--muted2); font-size:12px; margin-top:6px}

@media (max-width:520px){
  .hero h1{font-size:26px}
  .topbar-inner{gap:10px}
  .nav{gap:6px}
  .nav a{padding:7px 9px}
  .callout{flex-direction:column; align-items:stretch}
  .callout .btn{width:100%}
}
""".strip()


# -----------------------
# HTML BUILDING BLOCKS
# -----------------------
def nav_html(current: str) -> str:
    def item(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if current == key else ""
        return f'<a href="{esc(href)}"{cur}>{esc(label)}</a>'

    return (
        '<nav class="nav" aria-label="Primary navigation">'
        + item("/", "Home", "home")
        + item("/cost/", "Cost", "cost")
        + item("/how-to/", "How-To", "howto")
        + f'<a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>'
        + "</nav>"
    )


def base_html(*, title: str, canonical_path: str, description: str, current_nav: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{esc(canonical_path)}" />
  <style>
{CSS}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner">
      <a class="brand" href="/">
        <span class="brand-mark" aria-hidden="true"></span>
        <span>{esc(CONFIG.brand_name)}</span>
      </a>
      {nav_html(current_nav)}
    </div>
  </div>
{body}
</body>
</html>
"""


def header_block(*, h1: str, sub: str, pill: str, show_secondary_cta: bool = True) -> str:
    secondary = (
        f'<a class="ghost" href="/cost/">See typical pricing</a>'
        if show_secondary_cta
        else ""
    )
    return f"""
<header>
  <div class="hero">
    <div class="kicker">
      <span class="pill"><span class="pill-dot" aria-hidden="true"></span>{esc(pill)}</span>
    </div>
    <h1>{esc(h1)}</h1>
    <p class="sub">{esc(sub)}</p>
    <div class="hero-cta">
      <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
      {secondary}
    </div>
  </div>
</header>
""".rstrip()


def footer_block() -> str:
    return f"""
<footer>
  <div class="footer-inner">
    <div class="footer-cta">
      <h2>Next steps</h2>
      <p class="sub">Ready to move forward? Request a free quote.</p>
      <div style="margin-top:10px">
        <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
      </div>
    </div>

    <div class="footer-links">
      <a href="/">Home</a>
      <a href="/cost/">Cost</a>
      <a href="/how-to/">How-To</a>
    </div>
    <div class="small">© {esc(CONFIG.brand_name)}. All rights reserved.</div>
  </div>
</footer>
""".rstrip()


def page_shell(*, h1: str, sub: str, pill: str, inner_html: str, show_secondary_cta: bool = True) -> str:
    img_src = f"/{CONFIG.image_filename}"
    return (
        header_block(h1=h1, sub=sub, pill=pill, show_secondary_cta=show_secondary_cta)
        + f"""
<main>
  <section class="card">
    <div class="img">
      <img src="{esc(img_src)}" alt="Service image" loading="lazy" />
    </div>
    <div class="card-inner">
      {inner_html}
    </div>
  </section>
</main>
"""
        + footer_block()
    ).rstrip()


# -----------------------
# CONTENT SECTIONS
# -----------------------
def shared_sections_html(*, local_line: str | None = None) -> str:
    local = f' <span class="muted">{esc(local_line)}</span>' if local_line else ""
    return f"""
<h2>{esc(H2_SHARED[0])}</h2>
<p>
  We remove a wasp nest by finding where the wasps enter, treating the nest, and taking it down once activity drops.
  If you see steady wasp traffic to one spot, that’s usually the nest’s main entrance.{local}
</p>
<p class="muted">
  If the nest is high up or you can’t confirm where it sits, don’t poke around—disturbing an active {esc(ALSO_MENTIONED[7])} is a fast way to get stung.
</p>

<h2>{esc(H2_SHARED[1])}</h2>
<p>
  Wasp control is about preventing repeat activity after the nest is handled. That usually means checking common rebuild spots
  and reducing easy access points—small gaps, sheltered ledges, and other places a new nest can get started.
</p>

<h2>{esc(H2_SHARED[2])}</h2>
<p>
  A wasp exterminator is the right call when access is risky or the nest is in a tight void. If you’re worried about {esc(ALSO_MENTIONED[4])},
  getting it handled safely is the smarter move.
</p>

<h2>{esc(H2_SHARED[3])}</h2>
<p>
  Paper wasp nest removal is often needed under eaves and overhangs where nests stay dry and protected. The nest can look small from the ground,
  but activity level is the better clue—heavy traffic usually means a larger colony than it appears.
</p>

<h2>{esc(H2_SHARED[4])}</h2>
<p>
  Ground wasp nest removal is different because the entrance can be a small hole and the nest can spread under the soil.
  Treating the wrong spot can make the area “hot” with defensive wasps, so approach and timing matter more here than almost anywhere else.
</p>

<h2>{esc(H2_SHARED[5])}</h2>
<p>
  Wasp removal is the hands-on work: locate the nest, treat it, and confirm activity drops. Spraying random surfaces doesn’t solve the problem—the nest does.
  If you keep seeing wasps returning to the same spot, you’re missing the actual entrance.
</p>
""".rstrip()


def cost_sections_html() -> str:
    return f"""
<h2>{esc(H2_COST[0])}</h2>
<p>
  Wasp nest removal cost depends mostly on access and nest location. A visible nest under an eave is typically quicker than one tucked into a structure.
</p>

<h2>{esc(H2_COST[1])}</h2>
<p>
  Most homeowners pay somewhere between ${CONFIG.cost_low} and ${CONFIG.cost_high} for a single nest removal.
  High nests, hidden nests, and extra time on site are what usually push the total higher.
</p>

<h2>{esc(H2_COST[2])}</h2>
<p>
  The cost of wasp nest removal moves with labor time and risk. Bigger nests, awkward rooflines, and repeated trips are common drivers behind a higher {esc(ALSO_MENTIONED[5])}.
</p>

<h2>{esc(H2_COST[3])}</h2>
<p>
  Wasp removal cost can be lower when the nest is small and easy to access, and higher when it’s established and defensive.
  If the nest has already been disturbed, the job can take longer because the wasps are more aggressive.
</p>

<h2>{esc(H2_COST[4])}</h2>
<p>
  Wasp nest removal price is basically the same question as “cost,” just phrased differently. What matters is whether the nest is simple to reach and remove,
  or whether it needs special handling for safety.
</p>

<h2>{esc(H2_COST[5])}</h2>
<p>
  Hornet nest removal cost is often higher because hornet nests can be larger and more defensive, and they’re frequently placed higher or deeper in sheltered areas.
</p>

<hr />

<p class="muted">
  Typical installed range (single nest, many homes): ${CONFIG.cost_low}–${CONFIG.cost_high}. Final pricing depends on access, nest location, and time on site.
</p>
""".rstrip()


def howto_sections_html() -> str:
    return f"""
<h2>{esc(H2_HOWTO[0])}</h2>
<p>
  To get rid of a wasp nest, don’t provoke it first. The safest plan is to identify the entrance, keep people and pets away, and treat the nest when activity is low.
  If you can’t clearly see the nest or it’s high up, skip this and call a pro.
</p>

<h2>{esc(H2_HOWTO[1])}</h2>
<p>
  To remove a wasp nest, you treat it first and only take it down once activity drops. Pulling down an active nest is what triggers defensive behavior and increases the risk of {esc(ALSO_MENTIONED[4])}.
</p>

<h2>{esc(H2_HOWTO[2])}</h2>
<p>
  “Remove wasp nest” really means removing the source of activity, not just spraying around. If wasps keep returning to the same spot, the nest entrance is still active.
</p>

<h2>{esc(H2_HOWTO[3])}</h2>
<p>
  The best time to spray a wasp nest is when activity is low and fewer wasps are flying in and out. Bad timing can make the nest more defensive and the situation worse.
</p>

<h2>{esc(H2_HOWTO[4])}</h2>
<p>
  Wasp spray only helps if you can safely hit the nest and follow directions. Improvising with a {esc(ALSO_MENTIONED[2])} or mixing products can create safety issues—don’t do that.
</p>

<h2>{esc(H2_HOWTO[5])}</h2>
<p>
  What kills wasps depends on the product and direct contact, but the bigger point is targeting the nest. If you can’t safely reach it,
  trying to “solve it from a distance” usually just spreads activity and increases sting risk.
</p>
""".rstrip()


def cost_callout_html(*, city: str, state: str) -> str:
    return f"""
<div class="callout" role="note" aria-label="Typical pricing callout">
  <div>
    <strong>Typical cost range in {esc(city)}, {esc(state)}</strong>
    <p>${CONFIG.cost_low}–${CONFIG.cost_high} for one nest in many homes. Access &amp; nest location drive the final total.</p>
  </div>
  <div>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</div>
""".rstrip()


# -----------------------
# PAGE FACTORY
# -----------------------
def make_page(*, h1: str, canonical: str, description: str, nav_key: str, pill: str, sub: str, inner: str, show_secondary_cta: bool = True) -> str:
    h1 = clamp_title(h1, 70)
    title = h1  # enforce title == h1
    return base_html(
        title=title,
        canonical_path=canonical,
        description=clamp_title(description, 155),
        current_nav=nav_key,
        body=page_shell(h1=h1, sub=sub, pill=pill, inner_html=inner, show_secondary_cta=show_secondary_cta),
    )


def homepage_html() -> str:
    h1 = CONFIG.service_name
    city_links = "\n".join(
        f'<li><a href="{esc("/" + city_state_slug(city, state) + "/")}">{esc(city)}, {esc(state)}</a></li>'
        for city, state in CITIES
    )

    # IMPORTANT for SEO rule: keep H2 set identical to city pages (H2_SHARED only).
    # So this section uses a plain paragraph label instead of an H2.
    inner = (
        shared_sections_html()
        + """
<hr />
<p class="muted" style="margin-bottom:10px; font-weight:900; letter-spacing:-0.01em;">
  Choose your city
</p>
<p class="muted">Select a city page for the same guide with a light local line.</p>
<ul class="city-grid">
"""
        + city_links
        + """
</ul>
<hr />
<p class="muted">
  Also available: <a href="/cost/">Wasp Nest Removal Cost</a> and <a href="/how-to/">How to Get Rid of Wasp Nest</a>.
</p>
"""
    )

    return make_page(
        h1=h1,
        canonical="/",
        description="Straight answers on wasp nest removal and wasp control.",
        nav_key="home",
        pill="Main service page",
        sub="How removal works, what prevents repeat activity, and when to call help.",
        inner=inner,
        show_secondary_cta=True,
    )


def city_page_html(city: str, state: str) -> str:
    # Keep H2 set identical to homepage: H2_SHARED only.
    # Conversion element: subtle callout box (no extra headings).
    inner = (
        cost_callout_html(city=city, state=state)
        + "\n"
        + shared_sections_html(local_line=f"Serving {city}, {state}.")
        + f"""
<hr />
<p class="muted">
  Want the full breakdown? See the <a href="/cost/">cost page</a> for the factors that move pricing.
</p>
"""
    )

    return make_page(
        h1=city_h1(CONFIG.service_name, city, state),
        canonical=f"/{city_state_slug(city, state)}/",
        description=f"Wasp nest removal and wasp control guide with local context for {city}, {state}.",
        nav_key="home",
        pill="City service page",
        sub="Same core guide, plus a quick local note and a pricing snapshot.",
        inner=inner,
        show_secondary_cta=True,
    )


def cost_page_html() -> str:
    return make_page(
        h1="Wasp Nest Removal Cost Services",
        canonical="/cost/",
        description="Typical wasp nest removal cost ranges and what changes pricing.",
        nav_key="cost",
        pill="Cost page",
        sub="Simple ranges and the factors that usually move the price.",
        inner=cost_sections_html(),
        show_secondary_cta=False,
    )


def howto_page_html() -> str:
    return make_page(
        h1="How to Get Rid of Wasp Nest Services",
        canonical="/how-to/",
        description="Clear steps for dealing with a wasp nest without making it worse.",
        nav_key="howto",
        pill="How-to page",
        sub="A practical guide that prioritizes safety and reduces repeat activity.",
        inner=howto_sections_html(),
        show_secondary_cta=False,
    )


# -----------------------
# ROBOTS + SITEMAP
# -----------------------
def robots_txt() -> str:
    return "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"


def sitemap_xml(urls: list[str]) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>\n"
    )


# -----------------------
# MAIN
# -----------------------
def main() -> None:
    script_dir = Path(__file__).resolve().parent
    out = CONFIG.output_dir

    reset_output_dir(out)

    # Copy the single shared image into /public/ so all pages can reference "/picture.png".
    copy_site_image(src_dir=script_dir, out_dir=out, filename=CONFIG.image_filename)

    # Core pages
    write_text(out / "index.html", homepage_html())
    write_text(out / "cost" / "index.html", cost_page_html())
    write_text(out / "how-to" / "index.html", howto_page_html())

    # City pages
    for city, state in CITIES:
        write_text(out / city_state_slug(city, state) / "index.html", city_page_html(city, state))

    # robots + sitemap
    urls = ["/", "/cost/", "/how-to/"] + [f"/{city_state_slug(c, s)}/" for c, s in CITIES]
    write_text(out / "robots.txt", robots_txt())
    write_text(out / "sitemap.xml", sitemap_xml(urls))

    print(f"✅ Generated {len(urls)} pages into: {out.resolve()}")


if __name__ == "__main__":
    main()
