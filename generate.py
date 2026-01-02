#!/usr/bin/env python3
"""
Static site generator (no JS) for a single-service, multi-city site
+ Main page
+ City pages
+ How-to page
+ Cost page

Cloudflare Pages:
- Build command: (empty)
- Output directory: public

URL structure:
- /                       (main service page)
- /<city>-<state>/        (city pages)
- /how-to/                (how-to page)
- /cost/                  (cost page)

SEO rules enforced:
- Exactly one H1 per page
- <title> == H1
- Title <= 70 characters (clamped)
- Controlled H2 sets per page type (5–7 each)
- City pages use CITY_H2 only
- Avoid over-repeating city name in body copy
- Natural CTA at the bottom (exact CTA text required)

Ahrefs MCP (US) terms used to build headings:

SERVICE keyword: "wasp nest removal"
also_rank_for (samples used here):
- wasp nest removal, wasp control, wasp exterminator, wasp exterminator near me
- wasp nest removal near me, wasp control services, wasp removal, wasp nest
- paper wasp nest, ground wasp nest, inside wasp nest, wasp hive
- start of a wasp nest, ground wasp nest identification
also_talk_about (co-occurring; filtered to relevant):
- wasp, wasps, pest control, spray bottle, dish soap, spray, wasp stings, bee hive

COST keyword: "wasp nest removal cost"
also_rank_for (samples used here):
- wasp nest removal cost, wasp removal cost, hornet nest removal cost
- wasp extermination, professional wasp removal, wasp pest control near me

HOW-TO keyword: "how to get rid of wasp nest"
also_rank_for (samples used here):
- how to get rid of wasp nest, how to get rid of a wasp nest
- how to remove wasp nest, remove wasp nest
- best time to spray wasp nest, wasp spray
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import html
import re


# -----------------------
# CONFIG
# -----------------------
@dataclass(frozen=True)
class SiteConfig:
    # Must include “Services” and be <= 70 chars via clamp_title().
    service_name: str = "Wasp Nest Removal & Wasp Control Services"
    brand_name: str = "Wasp Nest Removal Company"
    cta_text: str = "Get Free Estimate"
    cta_href: str = "mailto:hello@example.com?subject=Free%20Quote%20Request"
    output_dir: Path = Path("public")

    # Optional: keep ranges generic unless you feed your own pricing data.
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

# Prefer local images so it always works on Cloudflare Pages.
LOCAL_IMAGE_CITY = "/assets/wasp-nest.jpg"
LOCAL_IMAGE_HOME = "/assets/house-eaves.jpg"
LOCAL_IMAGE_HOWTO = "/assets/wasp-spray.jpg"
LOCAL_IMAGE_COST = "/assets/pest-control.jpg"


# -----------------------
# H2 SETS (STRICT: 5–7 each, no duplicates across page types)
# -----------------------

# MAIN (service keyword: wasp nest removal)
MAIN_H2 = [
    "Wasp Nest Removal",
    "Wasp Control",
    "Wasp Exterminator",
    "Wasp Exterminator Near Me",
    "Wasp Nest Removal Near Me",
    "Wasp Control Services",
]

# CITY (service keyword: wasp nest removal) — different intent bucket, no repeats from MAIN
CITY_H2 = [
    "Paper Wasp Nest",
    "Ground Wasp Nest",
    "Inside Wasp Nest",
    "Start of a Wasp Nest",
    "Ground Wasp Nest Identification",
    "Wasp Hive",
]

# HOW-TO (how-to keyword: how to get rid of wasp nest)
HOWTO_H2 = [
    "How to Get Rid of Wasp Nest",
    "How to Get Rid of a Wasp Nest",
    "How to Remove Wasp Nest",
    "Remove Wasp Nest",
    "Best Time to Spray Wasp Nest",
    "Wasp Spray",
]

# COST (cost keyword: wasp nest removal cost)
COST_H2 = [
    "Wasp Nest Removal Cost",
    "Wasp Removal Cost",
    "Hornet Nest Removal Cost",
    "Wasp Extermination",
    "Professional Wasp Removal",
    "Wasp Pest Control Near Me",
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


def make_city_h1(service: str, city: str, state: str) -> str:
    # City pages intentionally include location (requested by “city pages”).
    return clamp_title(f"{service} in {city}, {state}", 70)


def toolbar_html() -> str:
    return f"""
<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="/">{esc(CONFIG.brand_name)}</a>
    <div class="topbar-actions">
      <a class="toplink" href="/">Home</a>
      <a class="toplink" href="/how-to/">How To</a>
      <a class="toplink" href="/cost/">Cost</a>
      <a class="btn btn-top" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    </div>
  </div>
</div>
""".rstrip()


CSS = """
:root {
  --bg: #0b1b33;
  --bg2: #102a4d;
  --text: #0f172a;
  --muted: #475569;
  --card: #ffffff;
  --line: #e2e8f0;
  --cta: #f97316;
  --cta-hover: #ea580c;
  --max: 980px;
  --radius: 14px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
  color: var(--text);
  background: #f8fafc;
  line-height: 1.55;
  padding-top: 58px;
}

.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 58px;
  background: rgba(255,255,255,0.98);
  border-bottom: 1px solid var(--line);
  z-index: 999;
  backdrop-filter: blur(8px);
}

.topbar-inner {
  max-width: var(--max);
  margin: 0 auto;
  height: 100%;
  padding: 0 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.brand {
  font-weight: 800;
  text-decoration: none;
  color: #0b1b33;
  letter-spacing: -0.01em;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.toplink {
  text-decoration: none;
  color: #0f172a;
  font-size: 13px;
}

header {
  background: linear-gradient(135deg, var(--bg), var(--bg2));
  color: white;
  padding: 44px 18px 34px;
}

.wrap { max-width: var(--max); margin: 0 auto; }

.hero {
  display: grid;
  gap: 14px;
  justify-items: center;
  text-align: center;
}

.hero h1 {
  margin: 0;
  font-size: 26px;
  letter-spacing: -0.01em;
}

.sub {
  margin: 0;
  color: rgba(255,255,255,0.86);
  max-width: 70ch;
  font-size: 14px;
}

.btn {
  display: inline-block;
  padding: 10px 14px;
  background: var(--cta);
  color: white;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 800;
  font-size: 13px;
  border: 0;
}

.btn:hover { background: var(--cta-hover); }

.btn-top { padding: 9px 12px; }

main { padding: 24px 18px 42px; }

.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: 0 8px 20px rgba(2, 6, 23, 0.05);
}

.grid { display: grid; gap: 16px; }

.img {
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid var(--line);
}

.img img { display: block; width: 100%; height: auto; }

h2 {
  font-size: 16px;
  margin: 18px 0 8px;
  letter-spacing: -0.01em;
}

p { margin: 0 0 10px; color: var(--text); }
ul { margin: 10px 0 14px 18px; color: var(--text); }
li { margin: 6px 0; }

hr { border: none; border-top: 1px solid var(--line); margin: 18px 0; }

.muted { color: var(--muted); font-size: 13px; }

footer {
  background: linear-gradient(135deg, var(--bg), var(--bg2));
  color: rgba(255,255,255,0.9);
  padding: 34px 18px;
}

.footer-card { max-width: var(--max); margin: 0 auto; text-align: center; }

.footer-card h2 { color: white; margin: 0 0 10px; font-size: 18px; }

.footer-card p { color: rgba(255,255,255,0.85); }

.small { margin-top: 18px; font-size: 12px; color: rgba(255,255,255,0.7); }

.links a {
  color: rgba(255,255,255,0.9);
  text-decoration: underline;
  margin: 0 10px;
  font-size: 13px;
}

.pill {
  display: inline-block;
  padding: 4px 10px;
  background: #eef2ff;
  border: 1px solid #e0e7ff;
  color: #1e3a8a;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 14px;
}

.table th, .table td {
  text-align: left;
  padding: 10px 10px;
  border-top: 1px solid var(--line);
  vertical-align: top;
}

.table th {
  color: #0f172a;
  background: #f1f5f9;
  border-top: 1px solid var(--line);
}

.city-grid {
  list-style: none;
  padding: 0;
  margin: 10px 0 0;
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.city-grid a {
  display: block;
  text-decoration: none;
  color: #0f172a;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 700;
  font-size: 14px;
}

.city-grid a:hover {
  border-color: #cbd5e1;
}
""".strip()


# -----------------------
# HTML SHELL
# -----------------------
def base_html(*, title: str, canonical_path: str, description: str, body_inner: str) -> str:
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
{toolbar_html()}
{body_inner}
</body>
</html>
"""


# -----------------------
# CONTENT BLOCKS
# -----------------------
def main_sections_html() -> str:
    # Also-mentioned terms sprinkled: wasp/wasps, pest control, spray, wasp stings
    return f"""
<h2>{esc(MAIN_H2[0])}</h2>
<p>
  We remove a wasp nest by identifying the nest location, treating it, and taking it down once activity drops.
  If you’ve got wasps coming and going from one spot, that’s usually the nest’s main entrance.
</p>

<h2>{esc(MAIN_H2[1])}</h2>
<p>
  Wasp control focuses on stopping repeat activity after the nest is dealt with.
  That can include checking nearby eaves and gaps where wasps keep trying to rebuild.
</p>

<h2>{esc(MAIN_H2[2])}</h2>
<p>
  A wasp exterminator handles nests that are hard to reach or risky to approach.
  If you’re worried about wasp stings, especially around kids or pets, it’s smarter to get help.
</p>

<h2>{esc(MAIN_H2[3])}</h2>
<p>
  Looking for a wasp exterminator near me usually means you want fast scheduling and the right tools for the job.
  If the nest is high up or inside a wall void, don’t poke it—get it handled safely.
</p>

<h2>{esc(MAIN_H2[4])}</h2>
<p>
  Wasp nest removal near me searches spike when a nest shows up near doors, patios, or play areas.
  If you can see steady wasp traffic, avoid spraying randomly—you can agitate the nest and make it worse.
</p>

<h2>{esc(MAIN_H2[5])}</h2>
<p>
  Wasp control services are usually a mix of removal plus targeted follow-up.
  The goal is fewer wasps around your home and fewer surprise nests in the same spot.
</p>
""".rstrip()


def city_sections_html(*, city: str, state: str) -> str:
    # Keep city mentions light to avoid repetition.
    local_line = f'<span class="muted">Serving {esc(city)}, {esc(state)}.</span>'

    return f"""
<h2>{esc(CITY_H2[0])}</h2>
<p>
  A paper wasp nest is often the open-cell type you see under eaves or ledges.
  If it’s near a walkway, removal is usually the safer move. {local_line}
</p>

<h2>{esc(CITY_H2[1])}</h2>
<p>
  A ground wasp nest is typically hidden, with a small entrance hole and steady wasp traffic.
  Don’t flood it with water—disturbed wasps can rush out fast.
</p>

<h2>{esc(CITY_H2[2])}</h2>
<p>
  An inside wasp nest can mean wasps are using a gap and building in a wall void or attic area.
  If you see wasps indoors, treat it as urgent and avoid sealing openings before removal.
</p>

<h2>{esc(CITY_H2[3])}</h2>
<p>
  The start of a wasp nest is usually small, but it can grow quickly once activity ramps up.
  If you catch it early, removal is typically simpler than waiting.
</p>

<h2>{esc(CITY_H2[4])}</h2>
<p>
  Ground wasp nest identification usually comes down to the entrance location and the pattern of wasp movement.
  If you see repeated landings in the same patch of lawn, that’s your clue.
</p>

<h2>{esc(CITY_H2[5])}</h2>
<p>
  “Wasp hive” is a common way people describe a nest, especially when it’s large or active.
  The safest approach is still the same: confirm location, treat it, then remove it.
</p>
""".rstrip()


def howto_sections_html() -> str:
    # Question-style H2 rule: answer immediately in first 1–2 sentences.
    return f"""
<h2>{esc(HOWTO_H2[0])}</h2>
<p>
  You get rid of a wasp nest by treating the nest when wasp activity is low, then removing it once activity drops.
  If you can’t reach the nest safely, don’t try—this is when a pro is the right call.
</p>
<ul>
  <li>Locate the nest entrance and note wasp traffic.</li>
  <li>Keep distance and don’t hit or block the nest opening.</li>
  <li>If you use a spray, follow the label and keep an exit path.</li>
  <li>After activity drops, remove the nest and clean the area.</li>
</ul>

<h2>{esc(HOWTO_H2[1])}</h2>
<p>
  Same approach: treat first, remove second.
  The biggest mistake is knocking the nest down while it’s active.
</p>

<h2>{esc(HOWTO_H2[2])}</h2>
<p>
  To remove a wasp nest, you need low activity, safe access, and a plan to avoid stings.
  If the nest is high up, inside a wall, or near a doorway, removal can turn risky fast.
</p>

<h2>{esc(HOWTO_H2[3])}</h2>
<p>
  Yes, you can remove a wasp nest yourself if it’s small, reachable, and you can keep distance.
  If you’re guessing, that’s a sign to stop and get help.
</p>

<h2>{esc(HOWTO_H2[4])}</h2>
<p>
  The best time to spray a wasp nest is when activity is lowest.
  That usually means you’ll see fewer wasps flying in and out compared to daytime.
</p>

<h2>{esc(HOWTO_H2[5])}</h2>
<p>
  Wasp spray is commonly used for nests that are reachable without climbing or squeezing into tight spaces.
  Don’t mix DIY liquids in a spray bottle near an active nest—stick to products labeled for the job or call a pro.
</p>
""".rstrip()


def cost_sections_html() -> str:
    # Question-style H2 rule: some of these are not questions, but still keep answers direct.
    low = CONFIG.cost_low
    high = CONFIG.cost_high

    return f"""
<h2>{esc(COST_H2[0])}</h2>
<p>
  Wasp nest removal cost usually depends on where the nest is and how hard it is to access.
  A common range for many jobs is ${low}–${high}, with higher pricing when access is difficult.
</p>
<ul>
  <li>Height and access (eaves vs inside a wall)</li>
  <li>Nest size and activity level</li>
  <li>Follow-up visits or repeat activity</li>
</ul>

<h2>{esc(COST_H2[1])}</h2>
<p>
  Wasp removal cost is often similar to nest removal when the wasps are tied to a visible nest.
  If you’re seeing wasps but can’t find the nest, inspection time can affect pricing.
</p>

<h2>{esc(COST_H2[2])}</h2>
<p>
  Hornet nest removal cost can run higher when nests are larger or placed in tougher spots.
  If you’re not sure whether it’s hornets or wasps, treat it the same: keep distance and get it identified.
</p>

<h2>{esc(COST_H2[3])}</h2>
<p>
  Wasp extermination is usually priced by the complexity of the situation, not just the idea of “spraying.”
  Hard access and higher sting risk are common cost drivers.
</p>

<h2>{esc(COST_H2[4])}</h2>
<p>
  Professional wasp removal makes the most sense when the nest is high up, inside a structure, or near daily foot traffic.
  You’re paying for safe access, correct treatment, and fewer repeat issues.
</p>

<h2>{esc(COST_H2[5])}</h2>
<p>
  Wasp pest control near me pricing varies by response time and whether the job includes follow-up.
  If you want a tight quote, you’ll usually need to share nest location (eaves, yard, wall) and approximate size.
</p>

<hr />

<p class="muted">
  Typical range (many projects): ${low}–${high}. Final pricing depends on access, nest location, and follow-up needs.
</p>
""".rstrip()


# -----------------------
# PAGES
# -----------------------
def homepage(*, cities: list[tuple[str, str]]) -> str:
    h1 = clamp_title(CONFIG.service_name, 70)
    title = h1  # EXACT match

    description = clamp_title(
        "Straight answers on wasp nest removal, wasp control, and what affects typical cost.",
        155,
    )

    city_links = "\n".join(
        f'<li><a href="{esc("/" + city_state_slug(city, state) + "/")}">{esc(city)}, {esc(state)}</a></li>'
        for city, state in cities
    )

    body_inner = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      Clear, practical info on getting rid of wasps and removing the nest without making the problem worse.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <section class="card">
    <div class="pill">Main service page</div>

    <div class="img" style="margin-top:12px;">
      <img src="{esc(LOCAL_IMAGE_HOME)}" alt="House eaves where wasps often build nests" loading="lazy" />
    </div>

    {main_sections_html()}

    <hr />

    <h2>Choose your city</h2>
    <p class="muted">Local pages focus on common nest types and what to look for in your area.</p>

    <ul class="city-grid">
      {city_links}
    </ul>
  </section>
</main>

<footer>
  <div class="footer-card">
    <h2>Next steps</h2>
    <p>Ready to move forward? Request a free quote</p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    <div class="small">© {esc(CONFIG.brand_name)}. All rights reserved.</div>
  </div>
</footer>
""".rstrip()

    return base_html(title=title, canonical_path="/", description=description, body_inner=body_inner)


def city_page(*, city: str, state: str) -> str:
    h1 = make_city_h1(CONFIG.service_name, city, state)
    title = h1  # EXACT match

    description = clamp_title(
        f"Nest-type guidance and what to look for in {city}, {state}, plus removal basics.",
        155,
    )

    canonical = f"/{city_state_slug(city, state)}/"

    body_inner = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      Local context without fluff: common nest types, warning signs, and safer next steps.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <div class="grid">
    <section class="card">
      <div class="pill">City page</div>

      <div class="img" style="margin-top:12px;">
        <img src="{esc(LOCAL_IMAGE_CITY)}" alt="Wasp nest on an exterior surface" loading="lazy" />
      </div>

      {city_sections_html(city=city, state=state)}
    </section>
  </div>
</main>

<footer>
  <div class="footer-card">
    <h2>Next steps</h2>
    <p>Ready to move forward? Request a free quote</p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    <div class="small">
      © {esc(CONFIG.brand_name)}. All rights reserved.
      <div class="links" style="margin-top:10px;">
        <a href="/">Home</a>
        <a href="/how-to/">How To</a>
        <a href="/cost/">Cost</a>
      </div>
    </div>
  </div>
</footer>
""".rstrip()

    return base_html(title=title, canonical_path=canonical, description=description, body_inner=body_inner)


def howto_page() -> str:
    # Must include “Services” in H1 by your global rule — but this is a how-to page.
    # To keep strict compliance, we keep H1 aligned to the service scope while the H2s carry the how-to intent.
    h1 = clamp_title(CONFIG.service_name, 70)
    title = h1

    description = clamp_title(
        "How-to guidance for wasp nest situations: when to spray, when to remove, and when to stop.",
        155,
    )

    canonical = "/how-to/"

    body_inner = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      How-to answers pulled into one place: steps, timing, and when it’s not worth the risk.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <section class="card">
    <div class="pill">How-to page</div>

    <div class="img" style="margin-top:12px;">
      <img src="{esc(LOCAL_IMAGE_HOWTO)}" alt="Wasp spray used outdoors" loading="lazy" />
    </div>

    {howto_sections_html()}
  </section>
</main>

<footer>
  <div class="footer-card">
    <h2>Next steps</h2>
    <p>Ready to move forward? Request a free quote</p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    <div class="small">
      © {esc(CONFIG.brand_name)}. All rights reserved.
      <div class="links" style="margin-top:10px;">
        <a href="/">Home</a>
        <a href="/cost/">Cost</a>
      </div>
    </div>
  </div>
</footer>
""".rstrip()

    return base_html(title=title, canonical_path=canonical, description=description, body_inner=body_inner)


def cost_page() -> str:
    # Same strict H1 rule as above: keep H1 service-scoped; cost intent lives in H2s.
    h1 = clamp_title(CONFIG.service_name, 70)
    title = h1

    description = clamp_title(
        "Cost drivers for wasp nest removal: access, nest location, follow-up, and common ranges.",
        155,
    )

    canonical = "/cost/"

    body_inner = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      Cost breakdowns without the sales pitch: what actually moves the number up or down.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <section class="card">
    <div class="pill">Cost page</div>

    <div class="img" style="margin-top:12px;">
      <img src="{esc(LOCAL_IMAGE_COST)}" alt="Pest control gear and inspection" loading="lazy" />
    </div>

    {cost_sections_html()}
  </section>
</main>

<footer>
  <div class="footer-card">
    <h2>Next steps</h2>
    <p>Ready to move forward? Request a free quote</p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    <div class="small">
      © {esc(CONFIG.brand_name)}. All rights reserved.
      <div class="links" style="margin-top:10px;">
        <a href="/">Home</a>
        <a href="/how-to/">How To</a>
      </div>
    </div>
  </div>
</footer>
""".rstrip()

    return base_html(title=title, canonical_path=canonical, description=description, body_inner=body_inner)


# -----------------------
# GENERATION
# -----------------------
def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    CONFIG.output_dir.mkdir(parents=True, exist_ok=True)

    # Main page
    write_file(CONFIG.output_dir / "index.html", homepage(cities=CITIES))

    # How-to + Cost pages
    write_file(CONFIG.output_dir / "how-to" / "index.html", howto_page())
    write_file(CONFIG.output_dir / "cost" / "index.html", cost_page())

    # City pages
    for city, state in CITIES:
        slug = city_state_slug(city, state)
        out = CONFIG.output_dir / slug / "index.html"
        write_file(out, city_page(city=city, state=state))

    total = 1 + 2 + len(CITIES)
    print(f"✅ Generated {total} pages into: {CONFIG.output_dir.resolve()}")


if __name__ == "__main__":
    main()
