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
# THEME (pure CSS, minimal, fast)
# Warmer, home-services palette + softer motion (no JS)
# -----------------------
CSS = """
:root{
  /* Warm, home-services feel */
  --bg:#fbf7f1;        /* warm off-white */
  --surface:#ffffff;
  --ink:#1f2937;       /* slate-800 */
  --muted:#5b6472;     /* softer slate */
  --line:#eadfce;      /* warm border */
  --shadow: 0 10px 30px rgba(17, 24, 39, 0.08);

  /* Primary brand accent (sage/green) */
  --accent:#2f6f4e;
  --accent2:#24563c;

  /* Subtle highlight */
  --tint:#f2efe9;
  --tint2:#f7f1e6;

  --max:980px;
  --radius:16px;
}

*{box-sizing:border-box}
html{color-scheme:light}
body{
  margin:0;
  font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;
  color:var(--ink);
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(47,111,78,0.10), rgba(47,111,78,0.00) 55%),
    radial-gradient(900px 500px at 95% -20%, rgba(139,94,60,0.10), rgba(139,94,60,0.00) 60%),
    var(--bg);
  line-height:1.6;
}

a{color:inherit}
a:focus{outline:2px solid var(--accent); outline-offset:2px}

.topbar{
  position:sticky;
  top:0;
  z-index:50;
  background:rgba(251,247,241,0.92);
  backdrop-filter:saturate(140%) blur(10px);
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
  font-weight:900;
  letter-spacing:-0.02em;
  text-decoration:none;
  display:flex;
  align-items:center;
  gap:10px;
}

.brand:before{
  content:"";
  width:12px;
  height:12px;
  border-radius:999px;
  background:linear-gradient(180deg, var(--accent), var(--accent2));
  box-shadow:0 6px 14px rgba(47,111,78,0.18);
}

.nav{
  display:flex;
  align-items:center;
  gap:12px;
  flex-wrap:wrap;
  justify-content:flex-end;
}

.nav a{
  text-decoration:none;
  font-size:13px;
  color:var(--muted);
  padding:7px 10px;
  border-radius:999px;
  border:1px solid transparent;
  transition:transform .12s ease, background .12s ease, border-color .12s ease, color .12s ease;
}

.nav a:hover{
  background:var(--tint2);
  border-color:var(--line);
  color:var(--ink);
  transform:translateY(-1px);
}

.nav a[aria-current="page"]{
  color:var(--ink);
  background:var(--tint2);
  border:1px solid var(--line);
}

.btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  padding:10px 13px;
  background:linear-gradient(180deg, var(--accent), var(--accent2));
  color:#fff;
  border-radius:999px;
  text-decoration:none;
  font-weight:900;
  font-size:13px;
  border:1px solid rgba(255,255,255,0.18);
  box-shadow:0 12px 22px rgba(47,111,78,0.16);
  transition:transform .12s ease, box-shadow .12s ease, filter .12s ease;
}

.btn:hover{
  transform:translateY(-1px);
  box-shadow:0 14px 26px rgba(47,111,78,0.20);
  filter:saturate(110%);
}

.btn:focus{outline:2px solid var(--accent2); outline-offset:2px}

header{
  border-bottom:1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.65), rgba(255,255,255,0.00)),
    var(--bg);
}

.hero{
  max-width:var(--max);
  margin:0 auto;
  padding:34px 18px 24px;
  display:grid;
  gap:10px;
  text-align:left;
}

.hero h1{
  margin:0;
  font-size:30px;
  letter-spacing:-0.03em;
  line-height:1.15;
}

.sub{margin:0; color:var(--muted); max-width:74ch; font-size:14px}

main{
  max-width:var(--max);
  margin:0 auto;
  padding:22px 18px 46px;
}

.card{
  background:rgba(255,255,255,0.92);
  border:1px solid var(--line);
  border-radius:var(--radius);
  padding:18px;
  box-shadow:var(--shadow);
}

.pill{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:5px 11px;
  border-radius:999px;
  font-size:12px;
  font-weight:900;
  background:var(--tint2);
  border:1px solid var(--line);
  color:var(--muted);
}

.pill:before{
  content:"";
  width:7px;
  height:7px;
  border-radius:999px;
  background:var(--accent);
}

.img{
  margin-top:12px;
  border-radius:14px;
  overflow:hidden;
  border:1px solid var(--line);
  background:#f6f1e7;
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

.city-grid{
  list-style:none;
  padding:0;
  margin:10px 0 0;
  display:grid;
  gap:10px;
  grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
}

.city-grid a{
  display:block;
  text-decoration:none;
  color:var(--ink);
  background:rgba(255,255,255,0.96);
  border:1px solid var(--line);
  border-radius:14px;
  padding:11px 12px;
  font-weight:800;
  font-size:14px;
  box-shadow:0 10px 18px rgba(17,24,39,0.05);
  transition:transform .12s ease, box-shadow .12s ease, background .12s ease;
}

.city-grid a:hover{
  transform:translateY(-2px);
  box-shadow:0 14px 22px rgba(17,24,39,0.07);
  background:#fff;
}

/* High-impact conversion callout (used on city pages) */
.callout{
  margin:14px 0 6px;
  padding:14px 14px;
  border-radius:14px;
  border:1px solid rgba(47,111,78,0.22);
  background:
    linear-gradient(180deg, rgba(47,111,78,0.10), rgba(47,111,78,0.04));
}

.callout strong{
  display:block;
  font-size:13px;
  letter-spacing:-0.01em;
  margin-bottom:6px;
}

.callout .row{
  display:flex;
  flex-wrap:wrap;
  align-items:center;
  justify-content:space-between;
  gap:10px;
}

.callout .range{
  font-weight:950;
  font-size:18px;
  letter-spacing:-0.02em;
}

.callout .note{
  color:var(--muted);
  font-size:13px;
  max-width:70ch;
}

.callout .cta{
  display:inline-flex;
  align-items:center;
  gap:8px;
  text-decoration:none;
  font-weight:950;
  font-size:13px;
  padding:9px 12px;
  border-radius:999px;
  color:var(--accent2);
  background:rgba(255,255,255,0.7);
  border:1px solid rgba(47,111,78,0.22);
  transition:transform .12s ease, background .12s ease;
}

.callout .cta:hover{
  transform:translateY(-1px);
  background:rgba(255,255,255,0.92);
}

/* Footer */
footer{
  border-top:1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.45), rgba(255,255,255,0.00)),
    var(--bg);
}

.footer-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:26px 18px;
  display:grid;
  gap:10px;
  text-align:left;
}

.footer-inner h2{margin:0; font-size:18px}

.footer-links{display:flex; gap:12px; flex-wrap:wrap}

.footer-links a{
  color:var(--muted);
  text-decoration:none;
  font-size:13px;
  padding:6px 0;
}

.footer-links a:hover{color:var(--ink)}

.small{color:var(--muted); font-size:12px; margin-top:8px}
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
    # title == h1 is enforced by callers; keep this thin.
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
      <a class="brand" href="/">{esc(CONFIG.brand_name)}</a>
      {nav_html(current_nav)}
    </div>
  </div>
{body}
</body>
</html>
"""


def header_block(*, h1: str, sub: str) -> str:
    return f"""
<header>
  <div class="hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">{esc(sub)}</p>
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
      <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
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


def page_shell(*, h1: str, sub: str, pill: str, inner_html: str) -> str:
    # Single image used everywhere. Since we copy picture.png into /public/,
    # it can be referenced as "/picture.png" from any route.
    img_src = f"/{CONFIG.image_filename}"
    return (
        header_block(h1=h1, sub=sub)
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


# -----------------------
# PAGE FACTORY
# -----------------------
def make_page(*, h1: str, canonical: str, description: str, nav_key: str, pill: str, sub: str, inner: str) -> str:
    h1 = clamp_title(h1, 70)
    title = h1  # enforce title == h1
    return base_html(
        title=title,
        canonical_path=canonical,
        description=clamp_title(description, 155),
        current_nav=nav_key,
        body=page_shell(h1=h1, sub=sub, pill=pill, inner_html=inner),
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
<h2>Choose your city</h2>
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
    )


def city_page_html(city: str, state: str) -> str:
    # High-impact callout box for conversion (subtle, warm)
    callout = f"""
<div class="callout" role="note" aria-label="Typical cost range">
  <strong>Typical cost range in {esc(city)}, {esc(state)}</strong>
  <div class="row">
    <div class="range">${CONFIG.cost_low}–${CONFIG.cost_high}</div>
    <a class="cta" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
  <p class="note">
    Access and nest location drive most pricing. For a full breakdown, see the <a href="/cost/">cost page</a>.
  </p>
</div>
""".rstrip()

    inner = (
        shared_sections_html(local_line=f"Serving {city}, {state}.")
        + "\n"
        + callout
        + """
<hr />
<h2>Wasp Nest Removal Cost</h2>
<p class="muted">
  Typical installed range for one nest often falls around """
        + f"${CONFIG.cost_low}–${CONFIG.cost_high}"
        + """. Access and nest location drive most pricing.
  See the <a href="/cost/">cost page</a> for details.
</p>
"""
    )

    return make_page(
        h1=city_h1(CONFIG.service_name, city, state),
        canonical=f"/{city_state_slug(city, state)}/",
        description=f"Wasp nest removal and wasp control guide with local context for {city}, {state}.",
        nav_key="home",
        pill="City service page",
        sub="Same core guide, plus a quick local note and cost pointer.",
        inner=inner,
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
