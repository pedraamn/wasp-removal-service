#!/usr/bin/env python3
"""
Static site generator (no JS) for a single-service, multi-city home-services site.

Cloudflare Pages:
- Build command: (empty)
- Output directory: public

URL structure:
- /                    (home)
- /<city>-<state>/      e.g. /los-angeles-ca/

SEO rules enforced:
- Exactly one H1 per page
- <title> == H1
- Title <= 70 characters
- Main + City pages use the exact same H2 set (Ahrefs-driven)
- Pure CSS, barebones, fast

Changes in this version:
- Removed Cost + How-To pages and related nav/footer links
- Added a subtle cost range callout box on city pages (conversion element)
- Updated color system to feel less “techy/videogame” and more “home services”
- Topbar CTA button is WHITE with readable dark text
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
# THEME (pure CSS, minimal, warm, home-services vibe)
# -----------------------
CSS = """
:root{
  /* Warm, home-services palette (less "techy") */
  --bg: #fbfaf7;
  --surface: #ffffff;
  --ink: #1f2937;       /* slate-800 */
  --muted: #5b6777;     /* warm slate */
  --line: #e6e1d8;      /* warm border */
  --soft: #f4f1ea;      /* warm panel */
  --accent: #2f6f4e;    /* calm green */
  --accent2:#24573d;    /* darker green */
  --accent3:#b45309;    /* subtle amber (sparingly) */
  --max: 980px;
  --radius: 16px;
  --shadow: 0 10px 26px rgba(17,24,39,.08);
  --shadow2: 0 6px 18px rgba(17,24,39,.07);
}

*{box-sizing:border-box}
html{color-scheme:light}
body{
  margin:0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
  color:var(--ink);
  background:
    radial-gradient(900px 500px at 15% -10%, rgba(47,111,78,.10), rgba(47,111,78,0) 60%),
    radial-gradient(900px 500px at 95% 0%, rgba(180,83,9,.08), rgba(180,83,9,0) 60%),
    var(--bg);
  line-height:1.6;
}

a{color:inherit}
a:focus{outline:2px solid rgba(47,111,78,.45); outline-offset:2px}

.topbar{
  position:sticky;
  top:0;
  z-index:50;
  background: rgba(251,250,247,.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}
.topbar-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:12px 18px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
}
.brand{
  font-weight:900;
  letter-spacing:-0.02em;
  text-decoration:none;
  display:flex;
  align-items:center;
  gap:10px;
}
.brand-mark{
  width:34px;
  height:34px;
  border-radius:12px;
  background: linear-gradient(135deg, rgba(47,111,78,.16), rgba(180,83,9,.10));
  border:1px solid var(--line);
  box-shadow: var(--shadow2);
  display:inline-flex;
  align-items:center;
  justify-content:center;
  font-weight:900;
  color: var(--accent2);
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
  padding:7px 9px;
  border-radius:12px;
  border:1px solid transparent;
}
.nav a:hover{
  background: rgba(244,241,234,.9);
  border-color: var(--line);
  color: var(--ink);
}

/* Topbar CTA = white button with readable text */
.btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  padding:9px 12px;
  border-radius:12px;
  text-decoration:none;
  font-weight:900;
  font-size:13px;
  border:1px solid var(--line);
  box-shadow: var(--shadow2);
  transition: transform .08s ease, box-shadow .12s ease, background .12s ease;
}
.btn:active{transform: translateY(1px)}
.btn:focus{outline:2px solid rgba(47,111,78,.45); outline-offset:2px}

.btn-cta{
  background:#ffffff;
  color: var(--ink);
}
.btn-cta:hover{
  background: #fdfcf9;
  box-shadow: var(--shadow);
}

header{
  border-bottom:1px solid var(--line);
  background: linear-gradient(180deg, rgba(255,255,255,.65), rgba(255,255,255,.25));
}
.hero{
  max-width:var(--max);
  margin:0 auto;
  padding:32px 18px 20px;
  display:grid;
  gap:10px;
}
.hero h1{
  margin:0;
  font-size:30px;
  letter-spacing:-0.03em;
  line-height:1.18;
}
.sub{
  margin:0;
  color:var(--muted);
  max-width:74ch;
  font-size:14px;
}
.hero-actions{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  margin-top:6px;
}
.btn-primary{
  background: var(--accent);
  color:#fff;
  border-color: rgba(0,0,0,0);
  box-shadow: var(--shadow);
}
.btn-primary:hover{background: var(--accent2)}
.btn-ghost{
  background: rgba(255,255,255,.7);
  color: var(--ink);
}
.btn-ghost:hover{background: rgba(255,255,255,.95)}

main{
  max-width:var(--max);
  margin:0 auto;
  padding:22px 18px 44px;
}
.card{
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:var(--radius);
  padding:18px;
  box-shadow: var(--shadow2);
}
.pill{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:6px 10px;
  border-radius:999px;
  font-size:12px;
  font-weight:900;
  background: rgba(244,241,234,.9);
  border:1px solid var(--line);
  color: var(--muted);
}

.img{
  margin-top:12px;
  border-radius:14px;
  overflow:hidden;
  border:1px solid var(--line);
  background: #fff;
  box-shadow: 0 10px 26px rgba(17,24,39,.06);
}
.img img{display:block; width:100%; height:auto}

h2{
  margin:18px 0 8px;
  font-size:16px;
  letter-spacing:-0.01em;
}
p{margin:0 0 10px}
.muted{color:var(--muted); font-size:13px}

hr{border:0; border-top:1px solid var(--line); margin:18px 0}

/* Conversion callout (city pages) */
.callout{
  margin-top:14px;
  border-radius: 14px;
  padding:12px 12px;
  border:1px solid var(--line);
  background:
    linear-gradient(135deg, rgba(47,111,78,.10), rgba(47,111,78,0) 55%),
    linear-gradient(135deg, rgba(180,83,9,.09), rgba(180,83,9,0) 55%),
    rgba(244,241,234,.75);
}
.callout strong{
  display:block;
  font-size:13px;
  letter-spacing:-0.01em;
}
.callout p{margin:6px 0 0}
.callout .callout-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  flex-wrap:wrap;
}
.callout .range{
  font-weight:900;
  color: var(--accent2);
}

.city-grid{
  list-style:none;
  padding:0;
  margin:12px 0 0;
  display:grid;
  gap:10px;
  grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
}
.city-grid a{
  display:block;
  text-decoration:none;
  color:var(--ink);
  background: #ffffff;
  border:1px solid var(--line);
  border-radius:14px;
  padding:10px 12px;
  font-weight:800;
  font-size:14px;
  box-shadow: 0 6px 18px rgba(17,24,39,.05);
  transition: transform .08s ease, box-shadow .12s ease;
}
.city-grid a:hover{
  transform: translateY(-1px);
  box-shadow: 0 10px 26px rgba(17,24,39,.08);
}
.city-grid a:active{transform: translateY(0px)}

footer{
  border-top:1px solid var(--line);
  background: rgba(255,255,255,.35);
}
.footer-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:26px 18px;
  display:grid;
  gap:10px;
}
.footer-inner h2{margin:0; font-size:18px; letter-spacing:-0.02em}
.footer-inner .sub{font-size:13px}
.small{color:var(--muted); font-size:12px; margin-top:8px}
""".strip()


# -----------------------
# HTML BUILDING BLOCKS
# -----------------------
def nav_html(current: str) -> str:
    # Minimal nav: Home + CTA only
    def item(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if current == key else ""
        return f'<a href="{esc(href)}"{cur}>{esc(label)}</a>'

    return (
        '<nav class="nav" aria-label="Primary navigation">'
        + item("/", "Home", "home")
        + f'<a class="btn btn-cta" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>'
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
        <span class="brand-mark" aria-hidden="true">W</span>
        <span>{esc(CONFIG.brand_name)}</span>
      </a>
      {nav_html(current_nav)}
    </div>
  </div>
{body}
</body>
</html>
"""


def header_block(*, h1: str, sub: str, show_actions: bool = True) -> str:
    actions = ""
    if show_actions:
        actions = f"""
    <div class="hero-actions">
      <a class="btn btn-primary" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
      <a class="btn btn-ghost" href="#cities">Browse cities</a>
    </div>""".rstrip()

    return f"""
<header>
  <div class="hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">{esc(sub)}</p>{actions}
  </div>
</header>
""".rstrip()


def footer_block() -> str:
    return f"""
<footer>
  <div class="footer-inner">
    <h2>Next steps</h2>
    <p class="sub">Ready to move forward? Request a free quote.</p>
    <div>
      <a class="btn btn-primary" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    </div>
    <div class="small">© {esc(CONFIG.brand_name)}. All rights reserved.</div>
  </div>
</footer>
""".rstrip()


def page_shell(*, h1: str, sub: str, pill: str, inner_html: str, show_actions: bool = True) -> str:
    img_src = f"/{CONFIG.image_filename}"
    return (
        header_block(h1=h1, sub=sub, show_actions=show_actions)
        + f"""
<main>
  <section class="card">
    <div class="pill">{esc(pill)}</div>
    <div class="img">
      <img src="{esc(img_src)}" alt="Service image" loading="lazy" />
    </div>
    {inner_html}
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


def cost_callout_html(city: str, state: str) -> str:
    # Subtle but high-impact conversion element, no separate cost page
    return f"""
<div class="callout" role="note" aria-label="Typical cost range">
  <div class="callout-row">
    <strong>Typical cost range in {esc(city)}, {esc(state)}</strong>
    <div class="range">${CONFIG.cost_low}–${CONFIG.cost_high}</div>
  </div>
  <p class="muted">
    Most pricing depends on access and nest location (eaves vs. inside a structure, height, and how established it is).
    For an exact quote, use the estimate button.
  </p>
</div>
""".rstrip()


# -----------------------
# PAGE FACTORY
# -----------------------
def make_page(*, h1: str, canonical: str, description: str, nav_key: str, pill: str, sub: str, inner: str, show_actions: bool = True) -> str:
    h1 = clamp_title(h1, 70)
    title = h1  # enforce title == h1
    return base_html(
        title=title,
        canonical_path=canonical,
        description=clamp_title(description, 155),
        current_nav=nav_key,
        body=page_shell(h1=h1, sub=sub, pill=pill, inner_html=inner, show_actions=show_actions),
    )


def homepage_html() -> str:
    h1 = CONFIG.service_name
    city_links = "\n".join(
        f'<li><a href="{esc("/" + city_state_slug(city, state) + "/")}">{esc(city)}, {esc(state)}</a></li>'
        for city, state in CITIES
    )

    inner = (
        shared_sections_html()
        + """
<hr />
<h2 id="cities">Choose your city</h2>
<p class="muted">Select a city page for the same guide with a local note and a quick pricing callout.</p>
<ul class="city-grid">
"""
        + city_links
        + """
</ul>
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
        show_actions=True,
    )


def city_page_html(city: str, state: str) -> str:
    inner = (
        shared_sections_html(local_line=f"Serving {city}, {state}.")
        + cost_callout_html(city, state)
    )

    return make_page(
        h1=city_h1(CONFIG.service_name, city, state),
        canonical=f"/{city_state_slug(city, state)}/",
        description=f"Wasp nest removal and wasp control guide with local context for {city}, {state}.",
        nav_key="home",
        pill="City service page",
        sub="Same core guide, plus a quick local note and a typical cost range.",
        inner=inner,
        show_actions=False,
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

    # Core page
    write_text(out / "index.html", homepage_html())

    # City pages
    for city, state in CITIES:
        write_text(out / city_state_slug(city, state) / "index.html", city_page_html(city, state))

    # robots + sitemap
    urls = ["/"] + [f"/{city_state_slug(c, s)}/" for c, s in CITIES]
    write_text(out / "robots.txt", robots_txt())
    write_text(out / "sitemap.xml", sitemap_xml(urls))

    print(f"✅ Generated {len(urls)} pages into: {out.resolve()}")


if __name__ == "__main__":
    main()
