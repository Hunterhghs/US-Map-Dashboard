#!/usr/bin/env python3
"""
US Map Dashboard — HTML Builder
Assembles the complete self-contained index.html with embedded data and GeoJSON.
"""

import json, os, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Load economic data
with open(DATA_DIR / "us_economy_compact.json") as f:
    econ_data = json.load(f)

# Fetch and process GeoJSON
import urllib.request
geojson_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
print(f"Fetching GeoJSON from {geojson_url}...")
with urllib.request.urlopen(geojson_url) as resp:
    geojson = json.loads(resp.read().decode())

# Filter to 50 states + DC, add postal codes
NAME_TO_POSTAL = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}

features_out = []
for feat in geojson["features"]:
    name = feat["properties"]["name"]
    postal = NAME_TO_POSTAL.get(name)
    if postal and postal in econ_data["states"]:
        feat["properties"]["postal"] = postal
        # Simplify coordinates by rounding to 4 decimal places
        if feat["geometry"]["type"] == "Polygon":
            feat["geometry"]["coordinates"] = [
                [[round(c[0], 4), round(c[1], 4)] for c in ring]
                for ring in feat["geometry"]["coordinates"]
            ]
        elif feat["geometry"]["type"] == "MultiPolygon":
            feat["geometry"]["coordinates"] = [
                [[[round(c[0], 4), round(c[1], 4)] for c in ring] for ring in poly]
                for poly in feat["geometry"]["coordinates"]
            ]
        features_out.append(feat)

geojson_out = {"type": "FeatureCollection", "features": features_out}
geojson_str = json.dumps(geojson_out, separators=(",", ":"))
print(f"  GeoJSON: {len(features_out)} states, {len(geojson_str):,} chars")

# ── Build complete index.html ──
print("Building index.html...")

# The HTML is built from parts
HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Interactive US Map Dashboard — Economy & Development 2000–2025. Explore GDP, income, unemployment, poverty, housing, and education across all 50 states with animated timeline.">
<meta name="keywords" content="US economy, GDP by state, economic development, interactive map, data visualization, H Heuristics">
<meta name="author" content="H Heuristics">
<meta property="og:title" content="US Map Dashboard — Economy & Development 2000–2025">
<meta property="og:description" content="Interactive multidimensional economic dashboard covering GDP, income, unemployment, poverty, housing, and education across all 50 US states.">
<meta property="og:type" content="website">
<title>US Map Dashboard — Economy & Development 2000–2025 | H Heuristics</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script src="https://unpkg.com/leaflet.fullscreen@3.0.0/Control.FullScreen.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet.fullscreen@3.0.0/Control.FullScreen.css">
<style>
:root {{
  --bg-deep: #080e14;
  --bg-panel: #0d1520;
  --bg-card: #111a27;
  --bg-hover: #162231;
  --text-primary: #e8ecf1;
  --text-secondary: #8a95a5;
  --text-tertiary: #5a6577;
  --accent-gold: #e8c76a;
  --accent-gold-dim: #8a7235;
  --accent-blue: #4da8da;
  --accent-teal: #2dbda8;
  --accent-coral: #e8734a;
  --accent-purple: #9b7ec4;
  --accent-green: #4caf7d;
  --accent-red: #e0555a;
  --border: #1c2a3a;
  --border-light: #243447;
  --shadow: 0 2px 12px rgba(0,0,0,0.4);
  --radius: 10px;
  --radius-sm: 6px;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --font-display: 'Playfair Display', Georgia, 'Times New Roman', serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', monospace;
  --sidebar-w: 380px;
  --header-h: 56px;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%;overflow:hidden;font-family:var(--font-sans);background:var(--bg-deep);color:var(--text-primary);font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}}

/* Header */
#header{{position:fixed;top:0;left:0;right:0;height:var(--header-h);z-index:1001;background:var(--bg-panel);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 18px;gap:12px;backdrop-filter:blur(16px)}}
#header .logo{{font-family:var(--font-display);font-size:17px;font-weight:600;color:var(--accent-gold);white-space:nowrap;letter-spacing:-0.3px}}
#header .logo span{{color:var(--text-secondary);font-weight:400;font-size:13px;margin-left:6px;font-family:var(--font-sans)}}
#header .header-stats{{display:flex;gap:20px;margin-left:auto;align-items:center}}
#header .header-stat{{text-align:center}}
#header .header-stat .val{{font-size:15px;font-weight:700;color:var(--text-primary);font-family:var(--font-mono)}}
#header .header-stat .lbl{{font-size:10px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.8px}}
#header .header-year{{font-family:var(--font-display);font-size:28px;font-weight:700;color:var(--accent-gold);min-width:56px;text-align:center;line-height:1}}

/* Map Container */
#map-container{{position:fixed;top:var(--header-h);left:0;right:0;bottom:0;z-index:1;transition:right .3s cubic-bezier(.4,0,.2,1)}}
body.sidebar-open #map-container{{right:var(--sidebar-w)}}
#map{{width:100%;height:100%;background:var(--bg-deep)}}
#map .leaflet-control-zoom{{border:none!important;box-shadow:var(--shadow)!important}}
#map .leaflet-control-zoom a{{background:var(--bg-card)!important;color:var(--text-primary)!important;border:1px solid var(--border)!important;font-family:var(--font-sans)!important}}
#map .leaflet-control-zoom a:hover{{background:var(--bg-hover)!important}}
#map .leaflet-control-attribution{{background:rgba(8,14,20,.85)!important;color:var(--text-tertiary)!important;font-size:10px!important;padding:3px 8px!important}}
#map .leaflet-control-attribution a{{color:var(--text-secondary)!important}}
#map .leaflet-popup-content-wrapper{{background:var(--bg-card)!important;color:var(--text-primary)!important;border-radius:var(--radius)!important;box-shadow:0 8px 32px rgba(0,0,0,.6)!important;border:1px solid var(--border)!important}}
#map .leaflet-popup-tip{{background:var(--bg-card)!important}}
#map .leaflet-popup-close-button{{color:var(--text-secondary)!important;font-size:20px!important;padding:6px 10px!important}}

/* Metric Pills */
#metric-bar{{position:fixed;top:var(--header-h);left:50%;transform:translateX(-50%);z-index:1000;display:flex;gap:6px;padding:10px 0;flex-wrap:wrap;justify-content:center;pointer-events:none}}
body.sidebar-open #metric-bar{{left:calc(50% - var(--sidebar-w)/2)}}
#metric-bar > *{{pointer-events:auto}}
.metric-pill{{padding:7px 14px;border-radius:20px;border:1px solid var(--border);background:var(--bg-card);color:var(--text-secondary);font-size:11.5px;font-weight:500;cursor:pointer;transition:all .18s;white-space:nowrap;letter-spacing:0.2px;user-select:none;backdrop-filter:blur(8px)}}
.metric-pill:hover{{background:var(--bg-hover);color:var(--text-primary);border-color:var(--border-light)}}
.metric-pill.active{{background:var(--accent-gold);color:#0a1018;border-color:var(--accent-gold);font-weight:600;box-shadow:0 0 16px rgba(232,199,106,.25)}}

/* Timeline */
#timeline-bar{{position:fixed;bottom:28px;left:50%;transform:translateX(-50%);z-index:1000;display:flex;align-items:center;gap:10px;background:var(--bg-card);border:1px solid var(--border);border-radius:28px;padding:8px 16px;box-shadow:var(--shadow);backdrop-filter:blur(16px)}}
body.sidebar-open #timeline-bar{{left:calc(50% - var(--sidebar-w)/2)}}
#timeline-bar button{{background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:16px;padding:4px 8px;border-radius:4px;transition:all .15s;line-height:1}}
#timeline-bar button:hover{{color:var(--text-primary);background:var(--bg-hover)}}
#timeline-bar button.active{{color:var(--accent-gold)}}
#timeline-bar .year-label{{font-family:var(--font-display);font-size:20px;font-weight:700;color:var(--accent-gold);min-width:42px;text-align:center}}
#timeline-bar input[type=range]{{-webkit-appearance:none;width:140px;height:4px;background:var(--border-light);border-radius:2px;outline:none}}
#timeline-bar input[type=range]::-webkit-slider-thumb{{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:var(--accent-gold);cursor:pointer;border:2px solid var(--bg-deep);box-shadow:0 0 8px rgba(232,199,106,.4)}}
#timeline-bar .speed-btn{{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;padding:3px 8px;border-radius:10px;color:var(--text-tertiary)}}
#timeline-bar .speed-btn.active{{color:var(--text-primary);background:var(--bg-hover)}}

/* Sidebar */
#sidebar{{position:fixed;top:var(--header-h);right:0;bottom:0;width:var(--sidebar-w);z-index:1000;background:var(--bg-panel);border-left:1px solid var(--border);transform:translateX(100%);transition:transform .3s cubic-bezier(.4,0,.2,1);display:flex;flex-direction:column;overflow:hidden}}
body.sidebar-open #sidebar{{transform:translateX(0)}}
#sidebar-toggle{{position:fixed;top:calc(var(--header-h) + 10px);right:10px;z-index:1002;background:var(--bg-card);border:1px solid var(--border);color:var(--text-secondary);width:36px;height:36px;border-radius:8px;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;transition:all .2s}}
#sidebar-toggle:hover{{color:var(--text-primary);background:var(--bg-hover)}}
body.sidebar-open #sidebar-toggle{{right:calc(var(--sidebar-w) + 10px)}}

.sidebar-section{{padding:16px 18px;border-bottom:1px solid var(--border)}}
.sidebar-section h3{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;color:var(--text-tertiary);margin-bottom:10px}}
.sidebar-scroll{{flex:1;overflow-y:auto;overflow-x:hidden}}

/* KPI Cards */
.kpi-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.kpi-card{{background:var(--bg-card);border-radius:var(--radius-sm);padding:12px 14px;border:1px solid var(--border);cursor:pointer;transition:all .18s}}
.kpi-card:hover{{border-color:var(--border-light);background:var(--bg-hover)}}
.kpi-card.selected{{border-color:var(--accent-gold);box-shadow:0 0 12px rgba(232,199,106,.15)}}
.kpi-card .kpi-val{{font-family:var(--font-mono);font-size:18px;font-weight:700;color:var(--text-primary)}}
.kpi-card .kpi-lbl{{font-size:10px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.6px;margin-top:2px}}
.kpi-card .kpi-delta{{font-size:11px;font-weight:500;margin-top:3px}}
.kpi-card .kpi-delta.up{{color:var(--accent-green)}}
.kpi-card .kpi-delta.down{{color:var(--accent-red)}}

/* Region Filter */
.region-chips{{display:flex;flex-wrap:wrap;gap:5px}}
.region-chip{{padding:4px 10px;border-radius:14px;font-size:10.5px;font-weight:500;cursor:pointer;border:1px solid var(--border);background:var(--bg-card);color:var(--text-secondary);transition:all .15s;white-space:nowrap}}
.region-chip:hover{{border-color:var(--border-light);color:var(--text-primary)}}
.region-chip.active{{background:var(--accent-blue);color:#fff;border-color:var(--accent-blue)}}

/* Chart */
#bar-chart-wrapper{{height:220px;position:relative}}
#bar-chart-wrapper canvas{{width:100%!important;height:100%!important}}

/* State List */
.state-list{{max-height:280px;overflow-y:auto}}
.state-item{{display:flex;align-items:center;justify-content:space-between;padding:7px 10px;cursor:pointer;border-radius:var(--radius-sm);transition:all .12s;font-size:12.5px;gap:8px}}
.state-item:hover{{background:var(--bg-hover)}}
.state-item.selected{{background:var(--bg-hover);border-left:3px solid var(--accent-gold);padding-left:7px}}
.state-item .st-name{{font-weight:500;flex:1}}
.state-item .st-code{{font-size:10px;color:var(--text-tertiary);font-family:var(--font-mono);font-weight:500;width:22px}}
.state-item .st-val{{font-family:var(--font-mono);font-size:11.5px;color:var(--text-secondary);font-weight:500;text-align:right;min-width:60px}}
.state-item .st-rank{{font-size:10px;color:var(--text-tertiary);width:18px;text-align:right}}
.state-search{{width:100%;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-sm);color:var(--text-primary);padding:7px 10px;font-size:12px;outline:none;margin-bottom:8px;font-family:var(--font-sans)}}
.state-search::placeholder{{color:var(--text-tertiary)}}
.state-search:focus{{border-color:var(--accent-gold)}}

/* Legend */
#legend{{position:fixed;bottom:120px;right:16px;z-index:999;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:10px 14px;box-shadow:var(--shadow);min-width:150px;font-size:11px}}
body.sidebar-open #legend{{right:calc(var(--sidebar-w) + 16px)}}
#legend .legend-title{{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-tertiary);margin-bottom:6px}}
#legend .legend-gradient{{height:10px;border-radius:3px;margin-bottom:4px}}
#legend .legend-labels{{display:flex;justify-content:space-between;font-family:var(--font-mono);font-size:10px;color:var(--text-secondary)}}

/* Loading */
#loading{{position:fixed;inset:0;z-index:9999;background:var(--bg-deep);display:flex;flex-direction:column;align-items:center;justify-content:center;transition:opacity .4s}}
#loading.hidden{{opacity:0;pointer-events:none}}
#loading .spinner{{width:40px;height:40px;border:3px solid var(--border);border-top-color:var(--accent-gold);border-radius:50%;animation:spin .8s linear infinite;margin-bottom:16px}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
#loading .load-text{{font-family:var(--font-display);font-size:18px;color:var(--text-secondary)}}

/* Bottom bar */
#info-bar{{position:fixed;bottom:0;left:0;right:0;height:24px;z-index:1001;background:var(--bg-panel);border-top:1px solid var(--border);display:flex;align-items:center;padding:0 14px;gap:16px;font-size:9.5px;color:var(--text-tertiary)}}
#info-bar span{{white-space:nowrap}}
#info-bar .sep{{color:var(--border-light)}}

/* Responsive */
@media(max-width:1024px){{
  :root{{--sidebar-w:340px}}
  #metric-bar{{left:50%!important;padding:6px 10px;gap:4px}}
  .metric-pill{{padding:5px 10px;font-size:10.5px}}
}}
@media(max-width:768px){{
  :root{{--sidebar-w:100vw}}
  #sidebar{{width:100vw}}
  #sidebar-toggle{{right:10px!important}}
  body.sidebar-open #map-container{{right:0!important}}
  #metric-bar{{top:46px;padding:4px;gap:2px}}
  .metric-pill{{padding:4px 8px;font-size:10px}}
  #header .header-stats{{display:none}}
  #timeline-bar{{bottom:32px;padding:6px 10px;gap:6px}}
  #timeline-bar input[type=range]{{width:80px}}
  #legend{{bottom:100px;right:8px}}
}}

/* Tooltip override */
.leaflet-tooltip{{background:var(--bg-card)!important;color:var(--text-primary)!important;border:1px solid var(--border)!important;border-radius:6px!important;padding:6px 10px!important;font-size:12px!important;font-family:var(--font-sans)!important;box-shadow:0 4px 16px rgba(0,0,0,.5)!important}}
.leaflet-tooltip::before{{border-top-color:var(--bg-card)!important}}

/* State popup content */
.popup-content{{font-family:var(--font-sans);min-width:260px}}
.popup-content h2{{font-family:var(--font-display);font-size:18px;margin-bottom:4px;color:var(--accent-gold)}}
.popup-content .popup-region{{font-size:11px;color:var(--text-tertiary);margin-bottom:12px;text-transform:uppercase;letter-spacing:0.8px}}
.popup-grid{{display:grid;grid-template-columns:1fr 1fr;gap:6px 16px}}
.popup-metric{{margin-bottom:4px}}
.popup-metric .pm-label{{font-size:10px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.5px}}
.popup-metric .pm-value{{font-family:var(--font-mono);font-size:14px;font-weight:600;color:var(--text-primary)}}
.popup-metric .pm-change{{font-size:10px;margin-left:4px}}
.popup-metric .pm-change.positive{{color:var(--accent-green)}}
.popup-metric .pm-change.negative{{color:var(--accent-red)}}

/* Sparkline container in popup */
.popup-sparkline{{margin-top:10px}}
.popup-sparkline canvas{{width:100%!important;height:60px!important}}
</style>
</head>
<body>

<!-- Loading -->
<div id="loading"><div class="spinner"></div><div class="load-text">Loading US Economic Data…</div></div>

<!-- Header -->
<div id="header">
  <div class="logo">US Map Dashboard <span>Economy & Development 2000–2025</span></div>
  <div class="header-stats">
    <div class="header-stat"><div class="val" id="hdr-gdp">—</div><div class="lbl">GDP ($Bn)</div></div>
    <div class="header-stat"><div class="val" id="hdr-growth">—</div><div class="lbl">Growth (%)</div></div>
    <div class="header-stat"><div class="val" id="hdr-income">—</div><div class="lbl">Income ($)</div></div>
    <div class="header-stat"><div class="val" id="hdr-unemp">—</div><div class="lbl">Unemp (%)</div></div>
    <div class="header-year" id="hdr-year">2025</div>
  </div>
</div>

<!-- Metric Pills -->
<div id="metric-bar" role="tablist" aria-label="Economic indicators">
  <button class="metric-pill active" data-metric="gdp" role="tab" aria-selected="true">GDP</button>
  <button class="metric-pill" data-metric="gdp_growth" role="tab">GDP Growth</button>
  <button class="metric-pill" data-metric="gdppc" role="tab">GDP per Capita</button>
  <button class="metric-pill" data-metric="pop" role="tab">Population</button>
  <button class="metric-pill" data-metric="unemp" role="tab">Unemployment</button>
  <button class="metric-pill" data-metric="income" role="tab">Median Income</button>
  <button class="metric-pill" data-metric="poverty" role="tab">Poverty Rate</button>
  <button class="metric-pill" data-metric="hpi" role="tab">Housing Index</button>
  <button class="metric-pill" data-metric="edu" role="tab">Education</button>
</div>

<!-- Map -->
<div id="map-container"><div id="map"></div></div>

<!-- Legend -->
<div id="legend">
  <div class="legend-title" id="legend-title">GDP ($Bn)</div>
  <div class="legend-gradient" id="legend-gradient"></div>
  <div class="legend-labels"><span id="legend-min">0</span><span id="legend-max">4,000</span></div>
</div>

<!-- Sidebar Toggle -->
<button id="sidebar-toggle" title="Toggle sidebar (B)" aria-label="Toggle sidebar">☰</button>

<!-- Sidebar -->
<div id="sidebar">
  <div class="sidebar-scroll">
    <!-- KPIs -->
    <div class="sidebar-section">
      <h3>National Overview — <span id="sb-kpi-year">2025</span></h3>
      <div class="kpi-grid">
        <div class="kpi-card selected" data-metric="gdp">
          <div class="kpi-val" id="kpi-gdp">—</div>
          <div class="kpi-lbl">GDP ($Bn)</div>
          <div class="kpi-delta" id="kpi-gdp-delta"></div>
        </div>
        <div class="kpi-card" data-metric="gdp_growth">
          <div class="kpi-val" id="kpi-growth">—</div>
          <div class="kpi-lbl">GDP Growth (%)</div>
          <div class="kpi-delta" id="kpi-growth-delta"></div>
        </div>
        <div class="kpi-card" data-metric="income">
          <div class="kpi-val" id="kpi-income">—</div>
          <div class="kpi-lbl">Median Income ($)</div>
          <div class="kpi-delta" id="kpi-income-delta"></div>
        </div>
        <div class="kpi-card" data-metric="unemp">
          <div class="kpi-val" id="kpi-unemp">—</div>
          <div class="kpi-lbl">Unemployment (%)</div>
          <div class="kpi-delta" id="kpi-unemp-delta"></div>
        </div>
      </div>
    </div>

    <!-- Region Filter -->
    <div class="sidebar-section">
      <h3>Region Filter</h3>
      <div class="region-chips" id="region-chips">
        <button class="region-chip active" data-region="all">All Regions</button>
        <button class="region-chip" data-region="Northeast">Northeast</button>
        <button class="region-chip" data-region="Midwest">Midwest</button>
        <button class="region-chip" data-region="South">South</button>
        <button class="region-chip" data-region="West">West</button>
      </div>
    </div>

    <!-- Bar Chart -->
    <div class="sidebar-section">
      <h3>Top States — <span id="chart-metric-label">GDP ($Bn)</span> — <span id="chart-year">2025</span></h3>
      <div id="bar-chart-wrapper"><canvas id="bar-chart"></canvas></div>
    </div>

    <!-- State List -->
    <div class="sidebar-section">
      <h3>All States</h3>
      <input type="text" class="state-search" id="state-search" placeholder="Search states…" aria-label="Search states">
      <div class="state-list" id="state-list"></div>
    </div>
  </div>
</div>

<!-- Timeline -->
<div id="timeline-bar">
  <button id="btn-step-back" title="Previous year (←)">⏮</button>
  <button id="btn-play" title="Play/Pause (Space)">▶</button>
  <button id="btn-step-fwd" title="Next year (→)">⏭</button>
  <span class="year-label" id="timeline-year">2025</span>
  <input type="range" id="year-slider" min="0" max="25" value="25" title="Year slider (← →)">
  <button class="speed-btn" data-speed="500">0.5s</button>
  <button class="speed-btn active" data-speed="250">1×</button>
  <button class="speed-btn" data-speed="100">2×</button>
  <button class="speed-btn" data-speed="40">5×</button>
</div>

<!-- Bottom Info Bar -->
<div id="info-bar">
  <span>Data: BEA · Census Bureau · BLS · FHFA</span>
  <span class="sep">|</span>
  <span>2000–2025</span>
  <span class="sep">|</span>
  <span>51 States + DC</span>
  <span class="sep">|</span>
  <span>H Heuristics · US Map Dashboard v1.0</span>
</div>

<script>
// ══════════════════════════════════════════════════
// EMBEDDED DATA
// ══════════════════════════════════════════════════
const GEOJSON = {json.dumps(geojson_out, separators=(",", ":"))};
const ECON_DATA = {json.dumps(econ_data, separators=(",", ":"))};

// ══════════════════════════════════════════════════
// CONSTANTS
// ══════════════════════════════════════════════════
const YEARS = ECON_DATA.years;
const METRICS = ECON_DATA.metrics;
const META = ECON_DATA.meta;
const REGIONS = META.regions;
const COLORS = {{
  gdp:          "var(--accent-gold)",
  gdp_growth:   "var(--accent-green)",
  gdppc:        "var(--accent-blue)",
  pop:          "var(--accent-purple)",
  unemp:        "var(--accent-coral)",
  income:       "var(--accent-teal)",
  poverty:      "var(--accent-red)",
  hpi:          "var(--accent-gold)",
  edu:          "var(--accent-blue)",
}};
const METRIC_LABELS = {{
  gdp: "GDP ($Bn)", gdp_growth: "GDP Growth (%)", gdppc: "GDP per Capita ($)",
  pop: "Population (M)", unemp: "Unemployment (%)", income: "Median Income ($)",
  poverty: "Poverty Rate (%)", hpi: "Housing Price Index", edu: "Education (% Bachelor's+)",
}};
const METRIC_FORMATS = {{
  gdp: v => "$" + v.toFixed(1) + "Bn", gdp_growth: v => v.toFixed(1) + "%",
  gdppc: v => "$" + v.toLocaleString(), pop: v => v.toFixed(2) + "M",
  unemp: v => v.toFixed(1) + "%", income: v => "$" + v.toLocaleString(),
  poverty: v => v.toFixed(1) + "%", hpi: v => v.toFixed(1), edu: v => v.toFixed(1) + "%",
}};
const METRIC_INVERTED = new Set(["unemp", "poverty"]); // lower is better
const CHOROPLETH_COLORS = {{
  gdp: ["#1a2a1a","#2d4a2d","#4a7a3a","#7aad4a","#b5d84a","#e8c76a"],
  gdp_growth: ["#4a1a1a","#7a2a2a","#aa4a2a","#da7a2a","#e8a84a","#4caf7d"],
  gdppc: ["#0d1a2a","#1a3350","#2a5580","#4a80b0","#7ab0dd","#b5d8f0"],
  pop: ["#1a0d2a","#2a1a50","#4a2a80","#7a4ab0","#a87add","#d0b5f0"],
  unemp: ["#2a2a0d","#50501a","#80802a","#b0b04a","#ddd87a","#f0e8b5"],
  income: ["#0d2a1a","#1a5030","#2a8050","#4ab07a","#7adda8","#b5f0d0"],
  poverty: ["#0d2a1a","#1a5030","#2a8050","#4ab07a","#7adda8","#e0555a"],
  hpi: ["#2a1a0d","#50301a","#80502a","#b07a4a","#dda87a","#e8c76a"],
  edu: ["#0d1a2a","#1a3050","#2a5080","#4a70b0","#7a9add","#b5c8f0"],
}};

// ══════════════════════════════════════════════════
// STATE
// ══════════════════════════════════════════════════
let currentMetric = "gdp";
let currentYearIndex = 25; // 2025
let currentRegion = "all";
let isPlaying = false;
let playSpeed = 250;
let playTimer = null;
let selectedState = null;
let choroplethLayer = null;
let barChart = null;

// ══════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════
function getStateValue(code, metric, yrIdx) {{
  const st = ECON_DATA.states[code];
  if (!st) return null;
  return st[metric][yrIdx];
}}

function getMinMax(metric, yrIdx, region) {{
  let min = Infinity, max = -Infinity;
  for (const [code, st] of Object.entries(ECON_DATA.states)) {{
    if (code === "US") continue;
    if (region !== "all" && st.region !== region) continue;
    const v = st[metric][yrIdx];
    if (v < min) min = v;
    if (v > max) max = v;
  }}
  return {{min, max}};
}}

function getChoroplethColor(value, min, max, metric) {{
  if (value == null || isNaN(value)) return "#1c2a3a";
  const colors = CHOROPLETH_COLORS[metric] || CHOROPLETH_COLORS.gdp;
  const range = max - min;
  if (range === 0) return colors[0];
  let t = (value - min) / range;
  // Invert for metrics where lower is better
  if (METRIC_INVERTED.has(metric)) t = 1 - t;
  const idx = Math.min(colors.length - 1, Math.floor(t * colors.length));
  return colors[Math.max(0, idx)];
}}

function getDelta(code, metric, yrIdx) {{
  if (yrIdx === 0) return null;
  const curr = getStateValue(code, metric, yrIdx);
  const prev = getStateValue(code, metric, yrIdx - 1);
  if (curr == null || prev == null || prev === 0) return null;
  return ((curr - prev) / Math.abs(prev)) * 100;
}}

// ══════════════════════════════════════════════════
// MAP
// ══════════════════════════════════════════════════
const map = L.map("map", {{
  center: [39.8, -98.5],
  zoom: 4,
  minZoom: 3,
  maxZoom: 8,
  zoomControl: true,
  attributionControl: true,
  renderer: L.canvas({{padding:0.5}}),
  fullscreenControl: true,
}});

// Dark basemap
L.tileLayer("https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png", {{
  attribution: '&copy; <a href="https://carto.com/">CARTO</a> | <a href="https://www.openstreetmap.org/">OSM</a>',
  subdomains: "abcd",
  maxZoom: 19,
}}).addTo(map);

function buildPopupContent(code, yrIdx) {{
  const st = ECON_DATA.states[code];
  if (!st) return "";
  const metricOrder = ["gdp","gdp_growth","gdppc","pop","unemp","income","poverty","hpi","edu"];
  let rows = metricOrder.map(m => {{
    const v = st[m][yrIdx];
    const d = getDelta(code, m, yrIdx);
    const cls = d != null ? (d >= 0 ? "positive" : "negative") : "";
    const arrow = d != null ? (d >= 0 ? "▲" : "▼") : "";
    const label = METRIC_LABELS[m].split(" (")[0];
    return `<div class="popup-metric">
      <div class="pm-label">${{label}}</div>
      <div class="pm-value">${{METRIC_FORMATS[m](v)}}
        <span class="pm-change ${{cls}}">${{arrow}}${{d != null ? Math.abs(d).toFixed(1) + "%" : ""}}</span>
      </div>
    </div>`;
  }}).join("");
  const yrLabel = YEARS[yrIdx];
  return `<div class="popup-content">
    <h2>${{st.name}}</h2>
    <div class="popup-region">${{st.region}} · ${{yrLabel}}</div>
    <div class="popup-grid">${{rows}}</div>
  </div>`;
}}

function updateChoropleth() {{
  if (choroplethLayer) map.removeLayer(choroplethLayer);
  const {{min, max}} = getMinMax(currentMetric, currentYearIndex, currentRegion);
  const yr = YEARS[currentYearIndex];

  choroplethLayer = L.geoJSON(GEOJSON, {{
    style: feature => {{
      const code = feature.properties.postal;
      const v = getStateValue(code, currentMetric, currentYearIndex);
      const color = getChoroplethColor(v, min, max, currentMetric);
      return {{
        fillColor: color,
        weight: 1,
        opacity: 0.6,
        color: "#1c2a3a",
        fillOpacity: 0.85,
      }};
    }},
    onEachFeature: (feature, layer) => {{
      const code = feature.properties.postal;
      layer.bindTooltip(feature.properties.name, {{sticky: true, opacity: 0.9}});
      layer.on({{
        click: () => {{
          selectedState = code;
          updateSidebar();
          highlightStateList();
        }},
      }});
      layer.bindPopup(() => buildPopupContent(code, currentYearIndex), {{maxWidth: 320}});
    }},
    filter: feature => {{
      if (currentRegion === "all") return true;
      const code = feature.properties.postal;
      const st = ECON_DATA.states[code];
      return st && st.region === currentRegion;
    }},
  }}).addTo(map);

  updateLegend(min, max);
}}

function updateLegend(min, max) {{
  document.getElementById("legend-title").textContent = METRIC_LABELS[currentMetric];
  const colors = CHOROPLETH_COLORS[currentMetric] || CHOROPLETH_COLORS.gdp;
  const gradient = document.getElementById("legend-gradient");
  gradient.style.background = `linear-gradient(to right, ${{colors.join(", ")}})`;
  document.getElementById("legend-min").textContent = METRIC_FORMATS[currentMetric](min);
  document.getElementById("legend-max").textContent = METRIC_FORMATS[currentMetric](max);
}}

// ══════════════════════════════════════════════════
// HEADER & KPIs
// ══════════════════════════════════════════════════
function updateHeaderStats() {{
  const us = ECON_DATA.states["US"];
  const yr = currentYearIndex;
  document.getElementById("hdr-year").textContent = YEARS[yr];
  document.getElementById("hdr-gdp").textContent = "$" + us.gdp[yr].toFixed(0) + "Bn";
  document.getElementById("hdr-growth").textContent = us.gdp_growth[yr].toFixed(1) + "%";
  document.getElementById("hdr-income").textContent = "$" + (us.income[yr]/1000).toFixed(1) + "K";
  document.getElementById("hdr-unemp").textContent = us.unemp[yr].toFixed(1) + "%";
  document.getElementById("sb-kpi-year").textContent = YEARS[yr];
  document.getElementById("timeline-year").textContent = YEARS[yr];
  document.getElementById("year-slider").value = yr;

  // KPI cards
  const kpiMap = {{gdp:"gdp", gdp_growth:"growth", income:"income", unemp:"unemp"}};
  for (const [m, id] of Object.entries(kpiMap)) {{
    const el = document.getElementById("kpi-" + id);
    if (el) el.textContent = METRIC_FORMATS[m](us[m][yr]);
    const deltaEl = document.getElementById("kpi-" + id + "-delta");
    if (deltaEl) {{
      const d = getDelta("US", m, yr);
      if (d != null) {{
        const cls = d >= 0 ? "up" : "down";
        const arrow = d >= 0 ? "▲" : "▼";
        deltaEl.textContent = arrow + " " + Math.abs(d).toFixed(1) + "% YoY";
        deltaEl.className = "kpi-delta " + cls;
      }} else {{
        deltaEl.textContent = "";
      }}
    }}
  }}
}}

// ══════════════════════════════════════════════════
// BAR CHART
// ══════════════════════════════════════════════════
function updateBarChart() {{
  const yr = currentYearIndex;
  const states = Object.entries(ECON_DATA.states)
    .filter(([code, st]) => code !== "US" && (currentRegion === "all" || st.region === currentRegion))
    .map(([code, st]) => ({{code, name: st.name, value: st[currentMetric][yr], region: st.region}}))
    .sort((a, b) => b.value - a.value)
    .slice(0, 12);

  document.getElementById("chart-metric-label").textContent = METRIC_LABELS[currentMetric];
  document.getElementById("chart-year").textContent = YEARS[yr];

  const labels = states.map(s => s.code);
  const data = states.map(s => s.value);
  const colors = states.map(s => s.region === "Northeast" ? "#4da8da" :
    s.region === "Midwest" ? "#9b7ec4" : s.region === "South" ? "#e8734a" : "#2dbda8");

  const ctx = document.getElementById("bar-chart").getContext("2d");
  if (barChart) barChart.destroy();
  barChart = new Chart(ctx, {{
    type: "bar",
    data: {{labels, datasets: [{{data, backgroundColor: colors, borderRadius: 3, borderSkipped: false}}]}},
    options: {{
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{display: false}},
        tooltip: {{
          callbacks: {{
            label: ctx => METRIC_FORMATS[currentMetric](ctx.raw),
          }},
        }},
      }},
      scales: {{
        x: {{
          grid: {{color: "#1c2a3a"}},
          ticks: {{
            color: "#5a6577",
            font: {{size: 10}},
            callback: v => METRIC_FORMATS[currentMetric](v),
          }},
        }},
        y: {{
          grid: {{display: false}},
          ticks: {{color: "#8a95a5", font: {{size: 11, weight: "bold"}}}},
        }},
      }},
    }},
  }});
}}

// ══════════════════════════════════════════════════
// STATE LIST
// ══════════════════════════════════════════════════
function updateStateList() {{
  const yr = currentYearIndex;
  const search = document.getElementById("state-search").value.toLowerCase();
  let states = Object.entries(ECON_DATA.states)
    .filter(([code, st]) => code !== "US" && (currentRegion === "all" || st.region === currentRegion))
    .map(([code, st]) => ({{code, name: st.name, region: st.region, value: st[currentMetric][yr]}}));

  if (search) {{
    states = states.filter(s => s.name.toLowerCase().includes(search) || s.code.toLowerCase().includes(search));
  }}

  // Sort: descending by value (or ascending for inverted metrics)
  const invert = METRIC_INVERTED.has(currentMetric);
  states.sort((a, b) => invert ? a.value - b.value : b.value - a.value);

  const container = document.getElementById("state-list");
  container.innerHTML = states.map((s, i) => {{
    const sel = s.code === selectedState ? " selected" : "";
    return `<div class="state-item${{sel}}" data-code="${{s.code}}" data-lat="${{ECON_DATA.states[s.code].lat}}" data-lon="${{ECON_DATA.states[s.code].lon}}">
      <span class="st-rank">#${{i+1}}</span>
      <span class="st-code">${{s.code}}</span>
      <span class="st-name">${{s.name}}</span>
      <span class="st-val">${{METRIC_FORMATS[currentMetric](s.value)}}</span>
    </div>`;
  }}).join("");

  // Click handlers
  container.querySelectorAll(".state-item").forEach(el => {{
    el.addEventListener("click", () => {{
      const code = el.dataset.code;
      const lat = parseFloat(el.dataset.lat);
      const lon = parseFloat(el.dataset.lon);
      selectedState = code;
      map.flyTo([lat, lon], 7, {{duration: 0.8}});
      // Open popup after fly
      setTimeout(() => {{
        choroplethLayer.eachLayer(layer => {{
          if (layer.feature.properties.postal === code) {{
            layer.openPopup();
          }}
        }});
      }}, 900);
      highlightStateList();
    }});
  }});
}}

function highlightStateList() {{
  document.querySelectorAll(".state-item").forEach(el => {{
    el.classList.toggle("selected", el.dataset.code === selectedState);
  }});
}}

// ══════════════════════════════════════════════════
// UPDATE ALL
// ══════════════════════════════════════════════════
function updateAll() {{
  updateChoropleth();
  updateHeaderStats();
  updateBarChart();
  updateStateList();
  // Update metric pills
  document.querySelectorAll(".metric-pill").forEach(p => {{
    p.classList.toggle("active", p.dataset.metric === currentMetric);
    p.setAttribute("aria-selected", p.dataset.metric === currentMetric);
  }});
  // Update KPI selection
  document.querySelectorAll(".kpi-card").forEach(c => {{
    c.classList.toggle("selected", c.dataset.metric === currentMetric);
  }});
}}

// ══════════════════════════════════════════════════
// PLAYBACK
// ══════════════════════════════════════════════════
function togglePlay() {{
  if (isPlaying) {{
    stopPlay();
  }} else {{
    startPlay();
  }}
}}

function startPlay() {{
  isPlaying = true;
  document.getElementById("btn-play").textContent = "⏸";
  document.getElementById("btn-play").classList.add("active");
  playTimer = setInterval(() => {{
    if (currentYearIndex < YEARS.length - 1) {{
      currentYearIndex++;
    }} else {{
      currentYearIndex = 0;
    }}
    updateAll();
  }}, playSpeed);
}}

function stopPlay() {{
  isPlaying = false;
  document.getElementById("btn-play").textContent = "▶";
  document.getElementById("btn-play").classList.remove("active");
  if (playTimer) {{ clearInterval(playTimer); playTimer = null; }}
}}

// ══════════════════════════════════════════════════
// SIDEBAR
// ══════════════════════════════════════════════════
function toggleSidebar() {{
  document.body.classList.toggle("sidebar-open");
}}

// ══════════════════════════════════════════════════
// EVENT HANDLERS
// ══════════════════════════════════════════════════

// Metric pills
document.querySelectorAll(".metric-pill").forEach(btn => {{
  btn.addEventListener("click", () => {{
    currentMetric = btn.dataset.metric;
    updateAll();
  }});
}});

// KPI cards
document.querySelectorAll(".kpi-card").forEach(card => {{
  card.addEventListener("click", () => {{
    currentMetric = card.dataset.metric;
    updateAll();
  }});
}});

// Region chips
document.querySelectorAll(".region-chip").forEach(chip => {{
  chip.addEventListener("click", () => {{
    currentRegion = chip.dataset.region;
    document.querySelectorAll(".region-chip").forEach(c => c.classList.remove("active"));
    chip.classList.add("active");
    updateAll();
  }});
}});

// Year slider
document.getElementById("year-slider").addEventListener("input", e => {{
  stopPlay();
  currentYearIndex = parseInt(e.target.value);
  updateAll();
}});

// Play controls
document.getElementById("btn-play").addEventListener("click", togglePlay);
document.getElementById("btn-step-back").addEventListener("click", () => {{
  stopPlay();
  if (currentYearIndex > 0) currentYearIndex--;
  updateAll();
}});
document.getElementById("btn-step-fwd").addEventListener("click", () => {{
  stopPlay();
  if (currentYearIndex < YEARS.length - 1) currentYearIndex++;
  updateAll();
}});

// Speed buttons
document.querySelectorAll(".speed-btn").forEach(btn => {{
  btn.addEventListener("click", () => {{
    document.querySelectorAll(".speed-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    playSpeed = parseInt(btn.dataset.speed);
    if (isPlaying) {{ stopPlay(); startPlay(); }}
  }});
}});

// Sidebar toggle
document.getElementById("sidebar-toggle").addEventListener("click", toggleSidebar);

// State search
document.getElementById("state-search").addEventListener("input", updateStateList);

// Keyboard shortcuts
document.addEventListener("keydown", e => {{
  if (e.target.tagName === "INPUT" && e.target.type === "text") return;
  switch(e.key) {{
    case "ArrowLeft": stopPlay(); if (currentYearIndex > 0) {{ currentYearIndex--; updateAll(); }} break;
    case "ArrowRight": stopPlay(); if (currentYearIndex < YEARS.length - 1) {{ currentYearIndex++; updateAll(); }} break;
    case " ": e.preventDefault(); togglePlay(); break;
    case "b": case "B": toggleSidebar(); break;
    case "f": case "F": map.toggleFullscreen(); break;
    case "Home": stopPlay(); currentYearIndex = 0; updateAll(); break;
    case "End": stopPlay(); currentYearIndex = YEARS.length - 1; updateAll(); break;
  }}
}});

// Responsive: close sidebar on small screens when clicking map
map.on("click", () => {{
  if (window.innerWidth <= 768) {{
    document.body.classList.remove("sidebar-open");
  }}
}});

// ══════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════
window.addEventListener("load", () => {{
  updateAll();
  // Open sidebar by default on desktop
  if (window.innerWidth > 768) {{
    document.body.classList.add("sidebar-open");
  }}
  // Hide loading
  setTimeout(() => {{
    document.getElementById("loading").classList.add("hidden");
  }}, 400);
  // Invalidate map size after layout
  setTimeout(() => map.invalidateSize(), 500);
}});

// Handle resize
window.addEventListener("resize", () => map.invalidateSize());
</script>
</body>
</html>'''

# Write index.html
output_path = BASE_DIR / "index.html"
with open(output_path, "w") as f:
    f.write(HTML)

size_mb = os.path.getsize(output_path) / (1024*1024)
print(f"\n✅ index.html built: {output_path} ({size_mb:.2f} MB)")
print(f"   Self-contained — HTML + GeoJSON + Economic Data")
print(f"   Open with: open {output_path}")
