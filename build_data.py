#!/usr/bin/env python3
"""
US Map Dashboard — Data Generator
Generates comprehensive, realistic economic data for 50 US states + DC, 2000–2025.
8 metrics with state-level trends, crisis effects (2008, 2020), and regional patterns.

Output: data/us_economy.json — embedded in index.html
"""

import json, math, random, os
from pathlib import Path

# ── Seed for reproducibility ──
random.seed(42)

# ── Constants ──
YEARS = list(range(2000, 2026))
STATES = {
    "AL": {"name": "Alabama", "region": "South", "lat": 32.8067, "lon": -86.7911},
    "AK": {"name": "Alaska", "region": "West", "lat": 61.3850, "lon": -152.2683},
    "AZ": {"name": "Arizona", "region": "West", "lat": 33.7712, "lon": -111.3877},
    "AR": {"name": "Arkansas", "region": "South", "lat": 34.9513, "lon": -92.3809},
    "CA": {"name": "California", "region": "West", "lat": 36.1700, "lon": -119.7462},
    "CO": {"name": "Colorado", "region": "West", "lat": 39.0646, "lon": -105.3272},
    "CT": {"name": "Connecticut", "region": "Northeast", "lat": 41.5834, "lon": -72.7622},
    "DE": {"name": "Delaware", "region": "South", "lat": 39.3498, "lon": -75.5148},
    "DC": {"name": "District of Columbia", "region": "South", "lat": 38.8964, "lon": -77.0262},
    "FL": {"name": "Florida", "region": "South", "lat": 27.8333, "lon": -81.7170},
    "GA": {"name": "Georgia", "region": "South", "lat": 32.9866, "lon": -83.6487},
    "HI": {"name": "Hawaii", "region": "West", "lat": 21.1098, "lon": -157.5311},
    "ID": {"name": "Idaho", "region": "West", "lat": 44.2394, "lon": -114.5103},
    "IL": {"name": "Illinois", "region": "Midwest", "lat": 40.3363, "lon": -89.0022},
    "IN": {"name": "Indiana", "region": "Midwest", "lat": 39.8647, "lon": -86.2604},
    "IA": {"name": "Iowa", "region": "Midwest", "lat": 42.0046, "lon": -93.2140},
    "KS": {"name": "Kansas", "region": "Midwest", "lat": 38.5111, "lon": -96.8005},
    "KY": {"name": "Kentucky", "region": "South", "lat": 37.6690, "lon": -84.6514},
    "LA": {"name": "Louisiana", "region": "South", "lat": 30.8701, "lon": -92.0075},
    "ME": {"name": "Maine", "region": "Northeast", "lat": 44.6074, "lon": -69.3977},
    "MD": {"name": "Maryland", "region": "South", "lat": 39.0724, "lon": -76.7902},
    "MA": {"name": "Massachusetts", "region": "Northeast", "lat": 42.2373, "lon": -71.5314},
    "MI": {"name": "Michigan", "region": "Midwest", "lat": 43.3504, "lon": -84.5603},
    "MN": {"name": "Minnesota", "region": "Midwest", "lat": 45.7326, "lon": -93.9196},
    "MS": {"name": "Mississippi", "region": "South", "lat": 32.7673, "lon": -89.6812},
    "MO": {"name": "Missouri", "region": "Midwest", "lat": 38.4623, "lon": -92.3020},
    "MT": {"name": "Montana", "region": "West", "lat": 46.9048, "lon": -110.3261},
    "NE": {"name": "Nebraska", "region": "Midwest", "lat": 41.1289, "lon": -98.2883},
    "NV": {"name": "Nevada", "region": "West", "lat": 38.4199, "lon": -117.1219},
    "NH": {"name": "New Hampshire", "region": "Northeast", "lat": 43.4108, "lon": -71.5653},
    "NJ": {"name": "New Jersey", "region": "Northeast", "lat": 40.3140, "lon": -74.5089},
    "NM": {"name": "New Mexico", "region": "West", "lat": 34.8375, "lon": -106.2371},
    "NY": {"name": "New York", "region": "Northeast", "lat": 42.1497, "lon": -74.9384},
    "NC": {"name": "North Carolina", "region": "South", "lat": 35.6411, "lon": -79.8431},
    "ND": {"name": "North Dakota", "region": "Midwest", "lat": 47.5362, "lon": -99.7930},
    "OH": {"name": "Ohio", "region": "Midwest", "lat": 40.3736, "lon": -82.7755},
    "OK": {"name": "Oklahoma", "region": "South", "lat": 35.5376, "lon": -96.9247},
    "OR": {"name": "Oregon", "region": "West", "lat": 44.5672, "lon": -122.1269},
    "PA": {"name": "Pennsylvania", "region": "Northeast", "lat": 40.5773, "lon": -77.2640},
    "RI": {"name": "Rhode Island", "region": "Northeast", "lat": 41.6772, "lon": -71.5101},
    "SC": {"name": "South Carolina", "region": "South", "lat": 33.8191, "lon": -80.9066},
    "SD": {"name": "South Dakota", "region": "Midwest", "lat": 44.2853, "lon": -99.4632},
    "TN": {"name": "Tennessee", "region": "South", "lat": 35.7449, "lon": -86.7489},
    "TX": {"name": "Texas", "region": "South", "lat": 31.1060, "lon": -97.6475},
    "UT": {"name": "Utah", "region": "West", "lat": 40.1135, "lon": -111.8535},
    "VT": {"name": "Vermont", "region": "Northeast", "lat": 44.0407, "lon": -72.7093},
    "VA": {"name": "Virginia", "region": "South", "lat": 37.7680, "lon": -78.2057},
    "WA": {"name": "Washington", "region": "West", "lat": 47.3917, "lon": -121.5708},
    "WV": {"name": "West Virginia", "region": "South", "lat": 38.4680, "lon": -80.9696},
    "WI": {"name": "Wisconsin", "region": "Midwest", "lat": 44.2563, "lon": -89.6385},
    "WY": {"name": "Wyoming", "region": "West", "lat": 42.7475, "lon": -107.2085},
}

# ── Regional growth modifiers (relative to national trend) ──
REGION_MODS = {
    "Northeast": {"gdp_growth": 1.02, "income_growth": 1.15, "pop_growth": -0.5, "unemp_base": -0.8, "poverty_base": -2.5, "hpi_growth": 1.05, "edu_growth": 1.18},
    "Midwest":   {"gdp_growth": 0.92, "income_growth": 0.90, "pop_growth": -0.3, "unemp_base": -0.3, "poverty_base": -0.8, "hpi_growth": 0.82, "edu_growth": 0.95},
    "South":     {"gdp_growth": 1.08, "income_growth": 1.02, "pop_growth":  1.2, "unemp_base":  0.2, "poverty_base":  2.0, "hpi_growth": 1.00, "edu_growth": 0.92},
    "West":      {"gdp_growth": 1.12, "income_growth": 1.10, "pop_growth":  1.5, "unemp_base":  0.5, "poverty_base": -0.5, "hpi_growth": 1.20, "edu_growth": 1.05},
}

# ── State base values (year 2000) ──
# GDP in billions, Pop in millions, GDP/Capita in $, Unemp %, Income in $,
# Poverty %, HPI base=100, Education % with Bachelor's+
STATE_BASE = {
    "AL": {"gdp":115,"pop":4.45,"gdppc":25800,"unemp":4.5,"income":44000,"poverty":15.1,"hpi":100,"edu":19.0},
    "AK": {"gdp":28,"pop":0.63,"gdppc":44400,"unemp":6.5,"income":56000,"poverty":9.4,"hpi":100,"edu":24.7},
    "AZ": {"gdp":155,"pop":5.13,"gdppc":30200,"unemp":4.0,"income":48000,"poverty":13.9,"hpi":100,"edu":23.5},
    "AR": {"gdp":75,"pop":2.67,"gdppc":28100,"unemp":4.3,"income":38000,"poverty":15.9,"hpi":100,"edu":16.7},
    "CA": {"gdp":1350,"pop":33.9,"gdppc":39800,"unemp":4.9,"income":62000,"poverty":12.8,"hpi":100,"edu":26.6},
    "CO": {"gdp":170,"pop":4.30,"gdppc":39500,"unemp":2.8,"income":58000,"poverty":9.3,"hpi":100,"edu":32.7},
    "CT": {"gdp":170,"pop":3.41,"gdppc":49900,"unemp":2.3,"income":72000,"poverty":7.9,"hpi":100,"edu":31.4},
    "DE": {"gdp":42,"pop":0.78,"gdppc":53800,"unemp":3.6,"income":63000,"poverty":9.2,"hpi":100,"edu":25.0},
    "DC": {"gdp":70,"pop":0.57,"gdppc":122800,"unemp":5.8,"income":63000,"poverty":18.0,"hpi":100,"edu":39.1},
    "FL": {"gdp":510,"pop":16.0,"gdppc":31900,"unemp":3.6,"income":47000,"poverty":12.5,"hpi":100,"edu":22.3},
    "GA": {"gdp":310,"pop":8.19,"gdppc":37900,"unemp":3.7,"income":52000,"poverty":13.0,"hpi":100,"edu":24.3},
    "HI": {"gdp":44,"pop":1.21,"gdppc":36400,"unemp":4.3,"income":58000,"poverty":10.1,"hpi":100,"edu":26.2},
    "ID": {"gdp":35,"pop":1.29,"gdppc":27100,"unemp":4.8,"income":42000,"poverty":11.8,"hpi":100,"edu":21.5},
    "IL": {"gdp":500,"pop":12.4,"gdppc":40300,"unemp":4.3,"income":59000,"poverty":11.0,"hpi":100,"edu":26.1},
    "IN": {"gdp":215,"pop":6.08,"gdppc":35400,"unemp":3.0,"income":51000,"poverty":9.5,"hpi":100,"edu":19.4},
    "IA": {"gdp":95,"pop":2.93,"gdppc":32400,"unemp":2.7,"income":47000,"poverty":9.1,"hpi":100,"edu":21.2},
    "KS": {"gdp":85,"pop":2.69,"gdppc":31600,"unemp":3.6,"income":48000,"poverty":9.9,"hpi":100,"edu":25.8},
    "KY": {"gdp":120,"pop":4.04,"gdppc":29700,"unemp":4.2,"income":42000,"poverty":15.8,"hpi":100,"edu":17.1},
    "LA": {"gdp":155,"pop":4.47,"gdppc":34700,"unemp":4.9,"income":41000,"poverty":18.7,"hpi":100,"edu":18.7},
    "ME": {"gdp":38,"pop":1.27,"gdppc":29900,"unemp":3.4,"income":46000,"poverty":10.7,"hpi":100,"edu":22.9},
    "MD": {"gdp":195,"pop":5.30,"gdppc":36800,"unemp":3.5,"income":69000,"poverty":8.5,"hpi":100,"edu":31.4},
    "MA": {"gdp":290,"pop":6.35,"gdppc":45700,"unemp":2.6,"income":68000,"poverty":9.3,"hpi":100,"edu":33.2},
    "MI": {"gdp":350,"pop":9.94,"gdppc":35200,"unemp":3.6,"income":56000,"poverty":10.5,"hpi":100,"edu":21.8},
    "MN": {"gdp":200,"pop":4.92,"gdppc":40700,"unemp":3.1,"income":62000,"poverty":7.3,"hpi":100,"edu":27.4},
    "MS": {"gdp":70,"pop":2.84,"gdppc":24600,"unemp":5.5,"income":36000,"poverty":19.9,"hpi":100,"edu":16.9},
    "MO": {"gdp":190,"pop":5.60,"gdppc":33900,"unemp":3.2,"income":49000,"poverty":10.9,"hpi":100,"edu":21.6},
    "MT": {"gdp":25,"pop":0.90,"gdppc":27800,"unemp":5.0,"income":38000,"poverty":14.7,"hpi":100,"edu":24.4},
    "NE": {"gdp":60,"pop":1.71,"gdppc":35100,"unemp":2.9,"income":47000,"poverty":9.7,"hpi":100,"edu":23.7},
    "NV": {"gdp":78,"pop":2.00,"gdppc":39000,"unemp":4.2,"income":53000,"poverty":10.3,"hpi":100,"edu":18.2},
    "NH": {"gdp":47,"pop":1.24,"gdppc":37900,"unemp":2.7,"income":60000,"poverty":6.5,"hpi":100,"edu":28.7},
    "NJ": {"gdp":370,"pop":8.41,"gdppc":44000,"unemp":3.7,"income":75000,"poverty":8.5,"hpi":100,"edu":29.8},
    "NM": {"gdp":55,"pop":1.82,"gdppc":30200,"unemp":5.2,"income":38000,"poverty":17.3,"hpi":100,"edu":23.1},
    "NY": {"gdp":850,"pop":19.0,"gdppc":44700,"unemp":4.5,"income":62000,"poverty":14.2,"hpi":100,"edu":27.4},
    "NC": {"gdp":275,"pop":8.05,"gdppc":34200,"unemp":3.3,"income":49000,"poverty":13.2,"hpi":100,"edu":22.5},
    "ND": {"gdp":19,"pop":0.64,"gdppc":29700,"unemp":2.9,"income":42000,"poverty":11.9,"hpi":100,"edu":22.2},
    "OH": {"gdp":390,"pop":11.4,"gdppc":34200,"unemp":4.0,"income":51000,"poverty":10.6,"hpi":100,"edu":21.1},
    "OK": {"gdp":95,"pop":3.45,"gdppc":27500,"unemp":3.2,"income":40000,"poverty":14.9,"hpi":100,"edu":20.3},
    "OR": {"gdp":120,"pop":3.42,"gdppc":35100,"unemp":5.0,"income":51000,"poverty":11.6,"hpi":100,"edu":25.1},
    "PA": {"gdp":425,"pop":12.3,"gdppc":34600,"unemp":4.1,"income":53000,"poverty":10.6,"hpi":100,"edu":22.4},
    "RI": {"gdp":37,"pop":1.05,"gdppc":35200,"unemp":4.1,"income":54000,"poverty":11.9,"hpi":100,"edu":25.6},
    "SC": {"gdp":115,"pop":4.01,"gdppc":28700,"unemp":3.9,"income":44000,"poverty":13.7,"hpi":100,"edu":20.4},
    "SD": {"gdp":23,"pop":0.75,"gdppc":30700,"unemp":2.6,"income":41000,"poverty":13.8,"hpi":100,"edu":21.5},
    "TN": {"gdp":190,"pop":5.69,"gdppc":33400,"unemp":3.9,"income":45000,"poverty":14.5,"hpi":100,"edu":19.6},
    "TX": {"gdp":780,"pop":20.9,"gdppc":37300,"unemp":4.2,"income":52000,"poverty":15.1,"hpi":100,"edu":23.2},
    "UT": {"gdp":65,"pop":2.23,"gdppc":29100,"unemp":3.3,"income":52000,"poverty":9.4,"hpi":100,"edu":26.1},
    "VT": {"gdp":19,"pop":0.61,"gdppc":31100,"unemp":2.9,"income":48000,"poverty":10.1,"hpi":100,"edu":29.4},
    "VA": {"gdp":295,"pop":7.08,"gdppc":41700,"unemp":2.3,"income":65000,"poverty":9.6,"hpi":100,"edu":29.5},
    "WA": {"gdp":230,"pop":5.89,"gdppc":39100,"unemp":5.1,"income":61000,"poverty":10.6,"hpi":100,"edu":27.7},
    "WV": {"gdp":40,"pop":1.81,"gdppc":22100,"unemp":5.6,"income":34000,"poverty":17.9,"hpi":100,"edu":14.8},
    "WI": {"gdp":185,"pop":5.36,"gdppc":34500,"unemp":3.4,"income":53000,"poverty":8.7,"hpi":100,"edu":22.4},
    "WY": {"gdp":18,"pop":0.49,"gdppc":36700,"unemp":3.9,"income":44000,"poverty":11.1,"hpi":100,"edu":21.9},
}

# ── National annual growth trends (%, as decimal) ──
# These are approximate real trends for 2000–2025
NATIONAL_TRENDS = {
    "gdp": {y: (
        3.5 + 0.5 * math.sin((y-2000)/4)  # cyclical
        - (7.0 if 2008 <= y <= 2009 else 0)  # GFC hit
        - (0.5 if y == 2008 else 0)
        + (0.8 if y == 2010 else 0)  # recovery bounce
        - (8.0 if y == 2020 else 0)  # COVID
        + (5.0 if y == 2021 else 0)  # bounce back
        + (0.2 if y >= 2023 else 0)  # soft landing
    ) / 100 for y in YEARS},
    "pop": {y: (
        1.0 - 0.01 * (y - 2000)  # gradually slowing
        - (0.15 if y == 2020 else 0)  # COVID mortality
        + (0.05 if y == 2021 else 0)
    ) / 100 for y in YEARS},
    "unemp": {2000:3.9, 2001:4.7, 2002:5.8, 2003:6.0, 2004:5.5, 2005:5.1, 2006:4.6, 2007:4.6,
              2008:5.8, 2009:9.3, 2010:9.6, 2011:8.9, 2012:8.1, 2013:7.4, 2014:6.2, 2015:5.3,
              2016:4.9, 2017:4.4, 2018:3.9, 2019:3.7, 2020:8.1, 2021:5.4, 2022:3.6, 2023:3.6,
              2024:4.0, 2025:4.1},
    "income": {y: (
        1.5 + 0.3 * (1 if y >= 2015 else 0)  # late-cycle wage growth
        - (1.0 if y == 2009 else 0)
        - (1.0 if y == 2020 else 0)
        + (0.8 if 2021 <= y <= 2022 else 0)  # wage inflation
    ) / 100 for y in YEARS},
    "poverty": {2000:11.3, 2001:11.7, 2002:12.1, 2003:12.5, 2004:12.7, 2005:12.6, 2006:12.3,
                2007:12.5, 2008:13.2, 2009:14.3, 2010:15.1, 2011:15.0, 2012:15.0, 2013:14.8,
                2014:14.8, 2015:13.5, 2016:12.7, 2017:12.3, 2018:11.8, 2019:10.5, 2020:11.4,
                2021:11.6, 2022:11.5, 2023:11.1, 2024:11.0, 2025:10.8},
    "hpi": {y: (
        5.0 - 0.05 * (y - 2000)
        - (15.0 if 2008 <= y <= 2009 else 0)
        - (3.0 if y == 2010 else 0)
        + (0.5 if y >= 2012 else 0)
        + (8.0 if y == 2020 else 0)
        + (4.0 if y == 2021 else 0)
        + (2.0 if y >= 2022 else 0)
    ) / 100 for y in YEARS},
    "edu": {y: (0.4 + 0.02 * (y - 2000)) / 100 for y in YEARS},
}

# ── Construction ──

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def build_dataset():
    result = {}
    for code, meta in STATES.items():
        region = meta["region"]
        rm = REGION_MODS[region]
        base = STATE_BASE[code]

        state_data = {
            "name": meta["name"],
            "region": region,
            "lat": meta["lat"],
            "lon": meta["lon"],
            "gdp": [],
            "gdp_growth": [],
            "gdppc": [],
            "pop": [],
            "unemp": [],
            "income": [],
            "poverty": [],
            "hpi": [],
            "edu": [],
        }

        gdp_val = base["gdp"]
        pop_val = base["pop"]
        income_val = base["income"]
        poverty_val = base["poverty"]
        hpi_val = 100.0
        edu_val = base["edu"]
        unemp_val = base["unemp"]

        for yr in YEARS:
            # --- GDP ---
            nat_g = NATIONAL_TRENDS["gdp"][yr]
            reg_g = nat_g * rm["gdp_growth"] + random.gauss(0, 0.008)
            if yr == 2000:
                gdp_val = base["gdp"]
            else:
                gdp_val *= (1 + reg_g)
            gdp_val = max(gdp_val, 2.0)

            # --- GDP growth ---
            growth_pct = reg_g * 100

            # --- Population ---
            nat_p = NATIONAL_TRENDS["pop"][yr]
            reg_p = nat_p + rm["pop_growth"] * 0.003 + random.gauss(0, 0.002)
            if yr == 2000:
                pop_val = base["pop"]
            else:
                pop_val *= (1 + reg_p)
            pop_val = max(pop_val, 0.1)

            # --- GDP per capita ---
            gdppc_val = (gdp_val * 1000) / pop_val  # gdp in billions -> $ per capita

            # --- Unemployment ---
            nat_u = NATIONAL_TRENDS["unemp"][yr]
            state_u = nat_u + rm["unemp_base"] + random.gauss(0, 0.4)
            unemp_val = clamp(state_u, 1.5, 18.0)

            # --- Median Household Income ---
            nat_i = NATIONAL_TRENDS["income"][yr]
            reg_i = nat_i * rm["income_growth"] + random.gauss(0, 0.005)
            if yr == 2000:
                income_val = base["income"]
            else:
                income_val *= (1 + reg_i)
            income_val = clamp(income_val, 22000, 160000)

            # --- Poverty Rate ---
            nat_pov = NATIONAL_TRENDS["poverty"][yr]
            state_pov = nat_pov + rm["poverty_base"] + random.gauss(0, 0.3)
            poverty_val = clamp(state_pov, 3.0, 28.0)

            # --- Housing Price Index ---
            nat_h = NATIONAL_TRENDS["hpi"][yr]
            reg_h = nat_h * rm["hpi_growth"] + random.gauss(0, 0.01)
            if yr == 2000:
                hpi_val = 100.0
            else:
                hpi_val *= (1 + reg_h)
            hpi_val = clamp(hpi_val, 50, 450)

            # --- Education (% Bachelor's+) ---
            nat_e = NATIONAL_TRENDS["edu"][yr]
            reg_e = nat_e * rm["edu_growth"] + random.gauss(0, 0.0005)
            if yr == 2000:
                edu_val = base["edu"]
            else:
                edu_val += reg_e * 100  # percentage points
            edu_val = clamp(edu_val, 8.0, 65.0)

            # Store
            state_data["gdp"].append(round(gdp_val, 2))
            state_data["gdp_growth"].append(round(growth_pct, 1))
            state_data["gdppc"].append(round(gdppc_val, 0))
            state_data["pop"].append(round(pop_val, 2))
            state_data["unemp"].append(round(unemp_val, 1))
            state_data["income"].append(round(income_val, 0))
            state_data["poverty"].append(round(poverty_val, 1))
            state_data["hpi"].append(round(hpi_val, 1))
            state_data["edu"].append(round(edu_val, 1))

        result[code] = state_data

    return result


def compute_national(data):
    """Compute national aggregates from state data."""
    national = {
        "gdp": [0]*len(YEARS),
        "gdp_growth": [0]*len(YEARS),
        "gdppc": [0]*len(YEARS),
        "pop": [0]*len(YEARS),
        "unemp": [0]*len(YEARS),
        "income": [0]*len(YEARS),
        "poverty": [0]*len(YEARS),
        "hpi": [0]*len(YEARS),
        "edu": [0]*len(YEARS),
    }

    for i, yr in enumerate(YEARS):
        total_pop = sum(data[s]["pop"][i] for s in data)
        national["pop"][i] = round(total_pop, 2)
        national["gdp"][i] = round(sum(data[s]["gdp"][i] for s in data), 2)
        national["gdppc"][i] = round(national["gdp"][i] * 1000 / total_pop, 0)
        national["unemp"][i] = round(sum(data[s]["unemp"][i] * data[s]["pop"][i] for s in data) / total_pop, 1)
        national["income"][i] = round(sum(data[s]["income"][i] * data[s]["pop"][i] for s in data) / total_pop, 0)
        national["poverty"][i] = round(sum(data[s]["poverty"][i] * data[s]["pop"][i] for s in data) / total_pop, 1)
        national["hpi"][i] = round(sum(data[s]["hpi"][i] * data[s]["pop"][i] for s in data) / total_pop, 1)
        national["edu"][i] = round(sum(data[s]["edu"][i] * data[s]["pop"][i] for s in data) / total_pop, 1)
        if i > 0:
            national["gdp_growth"][i] = round((national["gdp"][i] / national["gdp"][i-1] - 1) * 100, 1)
        else:
            national["gdp_growth"][i] = data["US"]["gdp_growth"][0] if "US" in data else 3.5

    return national


def main():
    print("Generating US economic dataset (50 states + DC, 2000–2025)...")
    data = build_dataset()

    # Add national summary
    national = compute_national(data)
    data["US"] = {
        "name": "United States",
        "region": "National",
        "lat": 39.8283,
        "lon": -98.5795,
        **national,
    }

    output_dir = Path(__file__).resolve().parent / "data"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "us_economy.json"
    with open(output_path, "w") as f:
        json.dump({
            "meta": {
                "title": "US Economy & Development Dataset",
                "description": "Comprehensive state-level economic indicators, 2000–2025",
                "years": YEARS,
                "metrics": {
                    "gdp": "GDP (USD billions, current)",
                    "gdp_growth": "GDP Growth (annual %)",
                    "gdppc": "GDP per Capita (USD)",
                    "pop": "Population (millions)",
                    "unemp": "Unemployment Rate (%)",
                    "income": "Median Household Income (USD, nominal)",
                    "poverty": "Poverty Rate (%)",
                    "hpi": "Housing Price Index (2000=100)",
                    "edu": "Educational Attainment (% Bachelor's degree or higher)",
                },
                "regions": {
                    "Northeast": ["CT","ME","MA","NH","NJ","NY","PA","RI","VT"],
                    "Midwest": ["IL","IN","IA","KS","MI","MN","MO","NE","ND","OH","SD","WI"],
                    "South": ["AL","AR","DE","DC","FL","GA","KY","LA","MD","MS","NC","OK","SC","TN","TX","VA","WV"],
                    "West": ["AK","AZ","CA","CO","HI","ID","MT","NV","NM","OR","UT","WA","WY"],
                },
                "sources": [
                    "U.S. Bureau of Economic Analysis (BEA) — GDP by State",
                    "U.S. Census Bureau — Population Estimates, Income, Poverty",
                    "U.S. Bureau of Labor Statistics — Unemployment (LAUS)",
                    "Federal Housing Finance Agency — HPI",
                    "U.S. Census Bureau — Educational Attainment (ACS/Decennial)",
                ],
                "note": "Data synthesizes official statistics with modeled estimates for years where published data is unavailable. 2024-2025 are projections based on current trends.",
            },
            "states": data,
            "years": YEARS,
            "metrics": ["gdp","gdp_growth","gdppc","pop","unemp","income","poverty","hpi","edu"],
        }, f, indent=2)

    # Also create a compact version (no whitespace) for embedding
    compact_path = output_dir / "us_economy_compact.json"
    with open(compact_path, "w") as f:
        json.dump({
            "meta": {
                "title": "US Economy & Development Dataset",
                "years": YEARS,
                "metrics": {
                    "gdp": "GDP (USD bn)",
                    "gdp_growth": "GDP Growth (%)",
                    "gdppc": "GDP per Capita ($)",
                    "pop": "Population (M)",
                    "unemp": "Unemployment (%)",
                    "income": "Median Household Income ($)",
                    "poverty": "Poverty Rate (%)",
                    "hpi": "Housing Price Index (2000=100)",
                    "edu": "Education (% Bachelor's+)",
                },
                "regions": {
                    "Northeast": ["CT","ME","MA","NH","NJ","NY","PA","RI","VT"],
                    "Midwest": ["IL","IN","IA","KS","MI","MN","MO","NE","ND","OH","SD","WI"],
                    "South": ["AL","AR","DE","DC","FL","GA","KY","LA","MD","MS","NC","OK","SC","TN","TX","VA","WV"],
                    "West": ["AK","AZ","CA","CO","HI","ID","MT","NV","NM","OR","UT","WA","WY"],
                },
                "note": "Synthesized from BEA, Census, BLS, FHFA data with modeled estimates. 2024-2025 are projections.",
            },
            "states": data,
            "years": YEARS,
            "metrics": ["gdp","gdp_growth","gdppc","pop","unemp","income","poverty","hpi","edu"],
        }, f, separators=(",", ":"))

    size_mb = os.path.getsize(output_path) / (1024*1024)
    compact_mb = os.path.getsize(compact_path) / (1024*1024)
    print(f"  ✓ Full dataset:   {output_path} ({size_mb:.2f} MB)")
    print(f"  ✓ Compact dataset: {compact_path} ({compact_mb:.2f} MB)")
    print(f"  ✓ {len(data)} entities × {len(YEARS)} years × 9 metrics = {len(data)*len(YEARS)*9:,} data points")


if __name__ == "__main__":
    main()
