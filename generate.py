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
H1_TITLE = "Wasp Nest/Wasp Hive Removal & Wasp Control Services"


H2_SHARED = [
    "What Is Wasp Nest Removal and Why It’s Necessary",
    "Where Wasps Commonly Build Nests Around Homes",
    "Are Wasp Nests Dangerous?",
    "Professional Wasp Nest Removal vs DIY Methods",
    "How Much Does Wasp Nest Removal Cost?",
    "How a Local Wasp Exterminator Removes a Nest",
    "When to Call a Professional for Wasp Nest Removal",
]

P_SHARED = [
    "Wasp nest removal is the process of safely eliminating an active wasp nest or hive and preventing the insects from returning. A nest indicates an established colony that will aggressively defend its territory. Unlike bees, wasps can sting multiple times and often attack in groups. Removing a nest is not just about comfort. In many cases, it’s necessary to prevent injuries, allergic reactions, and ongoing wasp activity around your home.",

    "Wasps look for sheltered, undisturbed areas close to food sources. Around residential properties, nests are commonly found under roof eaves and soffits, inside wall voids or behind siding, in attics, garages, and sheds, on trees, fences, and outdoor structures, and in the ground near foundations or yards. The nest’s location plays a major role in how dangerous removal can be.",

    "Yes — especially when the nest is active. Wasps will aggressively defend their nest if they feel threatened. Vibrations, lawn equipment, or improper spraying can trigger attacks. Multiple stings are common, and for individuals with allergies, even a single sting can become a medical emergency. The closer the nest is to high-traffic areas, the higher the risk.",

    "DIY wasp nest removal can seem simple, but it carries real risks. Many over-the-counter sprays only kill surface-level wasps, leaving the colony intact and aggressive. Professional wasp control focuses on protective equipment and proper timing, correct treatment methods based on species, complete elimination of the colony, and reducing the risk of wasps returning. DIY methods may work in limited situations, but they are not appropriate for every nest.",

    "The cost of wasp nest removal depends on factors such as nest size, location, and accessibility. Some nests can be handled quickly, while others require specialized equipment and safety measures. For a full breakdown of pricing and cost factors, see our Wasp Nest Removal Cost Guide.",

    "Professional wasp removal typically involves identifying the wasp species and nest type, treating the nest when wasps are least active, eliminating the colony safely, removing or sealing the nest area, and providing guidance to help prevent future nests. This process minimizes risk and ensures the problem is fully resolved.",

    "You should strongly consider professional help if the nest is inside a wall, attic, or roof, the nest is in the ground, someone has already been stung, you’re unsure what type of wasps are present, or the nest is large or difficult to access. When safety is uncertain, professional wasp control is the safest option."
]


H2_HOWTO = [
    "Can You Remove a Wasp Nest Yourself?",
    "Best Time of Day to Remove or Spray a Wasp Nest",
    "How to Get Rid of a Wasp Nest on a House or Roof",
    "How to Remove a Small or Paper Wasp Nest",
    "How to Kill a Wasp Nest in the Ground Safely",
    "Common Mistakes to Avoid During DIY Wasp Nest Removal",
    "When DIY Wasp Nest Removal Is Not Recommended",
]

P_HOWTO = [
    "Sometimes — but not always. DIY wasp nest removal may be possible for very small, early-stage nests that are clearly visible and easy to access. However, many nests grow quickly and contain dozens or even hundreds of wasps. In those cases, attempting removal yourself significantly increases the risk of being stung. For larger or hard-to-reach nests, professional {wasp nest and hive removal services} are often the safer option.",

    "Late evening or early night is the safest time. Most wasps return to their nest at night and are far less active. Attempting removal during the day increases the chance of disturbing foraging wasps and triggering aggressive behavior. Good timing reduces risk, but it does not eliminate it.",

    "For exposed nests on siding or eaves, wear thick protective clothing, keep your distance and plan an exit route, use products specifically labeled for wasps, apply treatment at night, and do not knock down the nest until activity has stopped. If the nest is inside the roof or structure, DIY removal is not recommended.",

    "Small paper nests early in the season may be removable if wasp activity is minimal, the nest is fully exposed, and you can maintain safe distance. If wasps remain active or begin rebuilding, professional help may be needed.",

    "Ground nests are among the most dangerous to handle. Wasps can emerge from multiple openings and attack in large numbers with little warning. Because of the high risk involved, ground nests are best handled by professionals.",

    "Common DIY mistakes include attempting removal during the day, standing too close to the nest, blocking your escape route, assuming wasps are gone after spraying, and leaving nest remnants behind. These mistakes cause most DIY injuries.",

    "Do not attempt DIY removal if the nest is large or hidden, the nest is inside a wall or attic, you lack proper protective gear, or children or pets are nearby. When safety is a concern, contacting a provider that offers {wasp control services} is the safest next step."
]


H2_COST = [
    "How Much Does Wasp Nest Removal Cost on Average?",
    "What Affects the Cost of Wasp Nest Removal?",
    "Cost Differences by Nest Location",
    "Professional Wasp Extermination vs DIY Costs",
    "Is Wasp Nest Removal Covered by Home Insurance?",
    "When Professional Wasp Nest Removal Is Worth the Cost",
]

P_COST = [
    "On average, wasp nest removal costs between $100 and $400. Simple, accessible nests typically fall on the lower end, while complex or hazardous removals cost more. Many homeowners compare DIY options against professional {wasp nest removal services} before deciding how to proceed.",

    "Several factors influence the final cost, including nest size and wasp species, location such as roof, wall, ground, or tree, accessibility and height, level of risk involved, and emergency or after-hours service. These variables explain why pricing can vary significantly.",

    "Roof or attic nests often cost more due to height and access challenges. Wall or siding nests may require sealing or partial removal. Ground nests are higher risk and labor-intensive. Tree or shed nests vary depending on size and proximity to people. Nest location is one of the biggest pricing factors.",

    "DIY removal may appear cheaper upfront, but it comes with risks such as incomplete colony removal, repeat infestations, and potential medical expenses. Professional services focus on full elimination and long-term prevention.",

    "Usually, no. Most homeowners insurance policies consider wasp nest removal routine maintenance and do not cover it. Coverage may only apply if the nest causes additional covered damage, which is uncommon. Always review your specific policy for confirmation.",

    "Professional removal is worth it when the nest poses a clear safety risk, DIY removal could result in injury, the nest is difficult to reach, or you want long-term peace of mind. In higher-risk situations, professional {wasp control services} often provide the safest and most reliable solution."
]


"""
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
"""


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
# Home-services vibe: warmer neutrals + trustworthy green CTA.
# -----------------------
CSS = """
:root{
  --bg:#fafaf9;
  --surface:#ffffff;
  --ink:#111827;
  --muted:#4b5563;
  --line:#e7e5e4;
  --soft:#f5f5f4;

  --cta:#16a34a;
  --cta2:#15803d;

  --max:980px;
  --radius:16px;
  --shadow:0 10px 30px rgba(17,24,39,0.06);
  --shadow2:0 10px 24px rgba(17,24,39,0.08);
}
*{box-sizing:border-box}
html{color-scheme:light}
body{
  margin:0;
  font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;
  color:var(--ink);
  background:var(--bg);
  line-height:1.6;
}
a{color:inherit}
a:focus{outline:2px solid var(--cta); outline-offset:2px}

.topbar{
  position:sticky;
  top:0;
  z-index:50;
  background:rgba(250,250,249,0.92);
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
  border-radius:12px;
  border:1px solid transparent;
}
.nav a:hover{
  background:var(--soft);
  border-color:var(--line);
}
.nav a[aria-current="page"]{
  color:var(--ink);
  background:var(--soft);
  border:1px solid var(--line);
}

.btn{
  display:inline-block;
  padding:9px 12px;
  background:var(--cta);
  color:#fff;
  border-radius:12px;
  text-decoration:none;
  font-weight:900;
  font-size:13px;
  border:1px solid rgba(0,0,0,0.04);
  box-shadow:0 8px 18px rgba(22,163,74,0.18);
}
.btn:hover{background:var(--cta2)}
.btn:focus{outline:2px solid var(--cta2); outline-offset:2px}

/* IMPORTANT: nav links apply grey text; ensure CTA stays white in the toolbar */
.nav a.btn{
  color:#fff;
  background:var(--cta);
  border-color:rgba(0,0,0,0.04);
}
.nav a.btn:hover{background:var(--cta2)}
.nav a.btn:focus{outline:2px solid var(--cta2); outline-offset:2px}

header{
  border-bottom:1px solid var(--line);
  background:
    radial-gradient(1200px 380px at 10% -20%, rgba(22,163,74,0.08), transparent 55%),
    radial-gradient(900px 320px at 95% -25%, rgba(17,24,39,0.06), transparent 50%),
    #fbfbfa;
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
  line-height:1.18;
}
.sub{margin:0; color:var(--muted); max-width:78ch; font-size:14px}

main{
  max-width:var(--max);
  margin:0 auto;
  padding:22px 18px 46px;
}
.card{
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:var(--radius);
  padding:18px;
  box-shadow:var(--shadow);
}
.img{
  margin-top:14px;
  border-radius:14px;
  overflow:hidden;
  border:1px solid var(--line);
  background:var(--soft);
  box-shadow:var(--shadow2);
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
  background:#fff;
  border:1px solid var(--line);
  border-radius:14px;
  padding:12px 12px;
  font-weight:800;
  font-size:14px;
  box-shadow:0 10px 24px rgba(17,24,39,0.05);
}
.city-grid a:hover{
  transform:translateY(-1px);
  box-shadow:0 14px 28px rgba(17,24,39,0.08);
}

.callout{
  margin:16px 0 12px;
  padding:14px 14px;
  border-radius:14px;
  border:1px solid rgba(22,163,74,0.22);
  background:linear-gradient(180deg, rgba(22,163,74,0.08), rgba(22,163,74,0.03));
}
.callout-title{
  display:flex;
  align-items:center;
  gap:10px;
  font-weight:900;
  letter-spacing:-0.01em;
  margin:0 0 6px;
}
.badge{
  display:inline-block;
  padding:3px 10px;
  border-radius:999px;
  background:rgba(22,163,74,0.14);
  border:1px solid rgba(22,163,74,0.22);
  color:var(--ink);
  font-size:12px;
  font-weight:900;
}
.callout p{margin:0; color:var(--muted); font-size:13px}

footer{
  border-top:1px solid var(--line);
  background:#fbfbfa;
}
.footer-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:28px 18px;
  display:grid;
  gap:10px;
  text-align:left;
}
.footer-inner h2{margin:0; font-size:18px}
.footer-links{display:flex; gap:12px; flex-wrap:wrap}
.footer-links a{color:var(--muted); text-decoration:none; font-size:13px; padding:6px 0}
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


def page_shell(*, h1: str, sub: str, inner_html: str) -> str:
    # Single image used everywhere. Since we copy picture.png into /public/,
    # it can be referenced as "/picture.png" from any route.
    img_src = f"/{CONFIG.image_filename}"
    return (
        header_block(h1=h1, sub=sub)
        + f"""
<main>
  <section class="card">
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
<p>{esc(P_SHARED[0])}</</p>

<h2>{esc(H2_SHARED[1])}</h2>
<p>{esc(P_SHARED[1])}</</p>

<h2>{esc(H2_SHARED[2])}</h2>
<p>{esc(P_SHARED[2])}</</p>

<h2>{esc(H2_SHARED[3])}</h2>
<p>{esc(P_SHARED[3])}</</p>

<h2>{esc(H2_SHARED[4])}</h2>
<p>{esc(P_SHARED[4])}</</p>

<h2>{esc(H2_SHARED[5])}</h2>
<p>{esc(P_SHARED[5])}</</p>
""".rstrip()


def cost_sections_html() -> str:
    return f"""
<h2>{esc(H2_COST[0])}</h2>
<p>{esc(P_COST[0])}</p>

<h2>{esc(H2_COST[1])}</h2>
<p>{esc(P_COST[1])}</p>

<h2>{esc(H2_COST[2])}</h2>
<p>{esc(P_COST[2])}</p>

<h2>{esc(H2_COST[3])}</h2>
<p>{esc(P_COST[3])}</p>

<h2>{esc(H2_COST[4])}</h2>
<p>{esc(P_COST[4])}</p>

<h2>{esc(H2_COST[5])}</h2>
<p>{esc(P_COST[5])}</p>

<hr />

<p class="muted">
  Typical installed range (single nest, many homes): ${CONFIG.cost_low}–${CONFIG.cost_high}. Final pricing depends on access, nest location, and time on site.
</p>
""".rstrip()


def howto_sections_html() -> str:
    return f"""
<h2>{esc(H2_HOWTO[0])}</h2>
<p>{esc(P_HOWTO[0])}</p>

<h2>{esc(H2_HOWTO[1])}</h2>
<p>{esc(P_HOWTO[1])}</p>

<h2>{esc(H2_HOWTO[2])}</h2>
<p>{esc(P_HOWTO[2])}</p>

<h2>{esc(H2_HOWTO[3])}</h2>
<p>{esc(P_HOWTO[3])}</p>

<h2>{esc(H2_HOWTO[4])}</h2>
<p>{esc(P_HOWTO[4])}</p>

<h2>{esc(H2_HOWTO[5])}</h2>
<p>{esc(P_HOWTO[5])}</p>
""".rstrip()


def city_cost_callout_html(city: str, state: str) -> str:
    # Subtle, high-impact conversion element for city pages.
    return f"""
<div class="callout" role="note" aria-label="Typical cost range">
  <div class="callout-title">
    <span class="badge">Typical range</span>
    <span>${CONFIG.cost_low}–${CONFIG.cost_high} for one nest</span>
  </div>
  <p>
    In {esc(city)}, {esc(state)}, most pricing comes down to access and where the nest is located.
    If you want a fast, no-pressure estimate, use the “{esc(CONFIG.cta_text)}” button above.
  </p>
</div>
""".rstrip()


# -----------------------
# PAGE FACTORY
# -----------------------
def make_page(*, h1: str, canonical: str, description: str, nav_key: str, sub: str, inner: str) -> str:
    h1 = clamp_title(h1, 70)
    title = h1  # enforce title == h1
    return base_html(
        title=title,
        canonical_path=canonical,
        description=clamp_title(description, 155),
        current_nav=nav_key,
        body=page_shell(h1=h1, sub=sub, inner_html=inner),
    )


def homepage_html() -> str:
    h1 = H1_TITLE
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
        sub="How removal works, what prevents repeat activity, and when to call help.",
        inner=inner,
    )


def city_page_html(city: str, state: str) -> str:
    inner = (
        shared_sections_html(local_line=f"Serving {city}, {state}.")
        + city_cost_callout_html(city, state)
        + f"""
<hr />
<h2>Wasp Nest Removal Cost</h2>
<p class="muted">
  Typical installed range for one nest often falls around ${CONFIG.cost_low}–${CONFIG.cost_high}. Access and nest location drive most pricing.
  See the <a href="/cost/">cost page</a> for details.
</p>
"""
    )

    return make_page(
        h1=city_h1(H1_TITLE, city, state),
        canonical=f"/{city_state_slug(city, state)}/",
        description=f"Wasp nest removal and wasp control guide with local context for {city}, {state}.",
        nav_key="home",
        sub="Same core guide, plus a quick local note and a typical cost range.",
        inner=inner,
    )


def cost_page_html() -> str:
    return make_page(
        h1="Wasp Nest Removal Cost",
        canonical="/cost/",
        description="Typical wasp nest removal cost ranges and what changes pricing.",
        nav_key="cost",
        sub="Simple ranges and the factors that usually move the price.",
        inner=cost_sections_html(),
    )


def howto_page_html() -> str:
    return make_page(
        h1="How to Get Rid of Wasp Nests",
        canonical="/how-to/",
        description="Clear steps for dealing with a wasp nest without making it worse.",
        nav_key="howto",
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
