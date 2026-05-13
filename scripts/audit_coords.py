"""Audit `data/books.json` for coordinate vs. named-place mismatches.

For each book, scans `location.name` and `location.why_here` for any
canonical place name (cities, towns, specific landmarks). For every
match, computes the haversine distance from the book's coordinates
to that place's canonical coordinates. A book passes if its coords
sit within THRESHOLD_KM of *any* mentioned canonical place.

Books with no canonical-place mention are skipped — broad pins like
"Mediterranean Sea" or "rural Mississippi" are intentionally vague
and out of scope.

Run:  python scripts/audit_coords.py
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

THRESHOLD_KM = 100
BOOKS_PATH = Path(__file__).resolve().parent.parent / "data" / "books.json"

# Canonical places: each key is the EXACT phrase to match (case-insensitive,
# word-boundary), value is (lat, lng). Use multi-word phrases for ambiguous
# names (e.g., "Cambridge, England" vs "Cambridge, Massachusetts").
CANONICAL: dict[str, tuple[float, float]] = {
    # ---- Europe: UK & Ireland ----
    "London": (51.5074, -0.1278),
    "Oxford, England": (51.7520, -1.2577),
    "Oxford University": (51.7520, -1.2577),
    "Oxford, Mississippi": (34.3668, -89.5186),
    "Cambridge, England": (52.2053, 0.1218),
    "Cambridge, UK": (52.2053, 0.1218),
    "Bath": (51.3811, -2.3590),
    "Edinburgh": (55.9533, -3.1883),
    "Glasgow": (55.8642, -4.2518),
    "Dublin": (53.3498, -6.2603),
    "Manchester": (53.4808, -2.2426),
    "Stratford-upon-Avon": (52.1919, -1.7082),
    "Wallington, Hertfordshire": (51.957, -0.143),
    "Brighton": (50.8225, -0.1372),
    "Canterbury": (51.2802, 1.0789),
    "Whitby": (54.4858, -0.6206),
    "Wessex": (50.7156, -2.4389),  # Hardy's Dorset
    "Dorchester": (50.7156, -2.4389),
    "Casterbridge": (50.7156, -2.4389),
    "Haworth": (53.8315, -1.9560),
    "Yorkshire Moors": (53.8315, -1.9560),
    "Stoke-on-Trent": (53.0027, -2.1794),
    "Burslem": (53.0500, -2.1850),
    "Newbury": (51.4015, -1.3232),
    "Wakefield": (53.6833, -1.4977),
    "Lincolnshire": (53.2307, -0.5406),
    "Gainsborough": (53.4000, -0.7700),
    "Nottinghamshire": (53.0000, -1.1500),
    "Eastwood, Nottinghamshire": (53.0168, -1.305),
    "Surrey": (51.3148, -0.5599),
    "Sussex": (50.9097, -0.4750),
    "Hertfordshire": (51.8000, -0.2167),

    # ---- Europe: France ----
    "Paris": (48.8566, 2.3522),
    "Wetzlar": (50.5553, 8.5019),  # Goethe (DE actually but place is French border-ish)
    "Croisset": (49.4431, 1.0993),
    "Rouen": (49.4431, 1.0993),
    "Normandy": (49.4431, 1.0993),
    "Marseille": (43.2965, 5.3698),
    "Lyon": (45.7640, 4.8357),
    "Geneva": (46.2044, 6.1432),
    "Roche, Ardennes": (49.7040, 4.5100),

    # ---- Europe: Germany / Austria / Switzerland ----
    "Berlin": (52.5200, 13.4050),
    "Munich": (48.1351, 11.5820),
    "Hamburg": (53.5511, 9.9937),
    "Frankfurt": (50.1109, 8.6821),
    "Lübeck": (53.8683, 10.6858),
    "Dresden": (51.0504, 13.7373),
    "Kassel": (51.3127, 9.4797),
    "Königsberg": (54.7104, 20.4522),
    "Vienna": (48.2082, 16.3738),
    "Bern": (46.9480, 7.4474),
    "Zurich": (47.3769, 8.5417),
    "Davos": (46.8043, 9.8336),
    "Sils Maria": (46.4329, 9.7625),
    "Bad Nauheim": (50.3637, 8.7376),

    # ---- Europe: Italy / Spain / Portugal ----
    "Rome": (41.9028, 12.4964),
    "Florence": (43.7696, 11.2558),
    "Milan": (45.4642, 9.1900),
    "Venice": (45.4408, 12.3155),
    "Naples": (40.8518, 14.2681),
    "Trieste": (45.6495, 13.7768),
    "Pavia": (45.1847, 9.1582),
    "Lecco": (45.8566, 9.3973),
    "Parma": (44.8015, 10.3279),
    "Brindisi": (40.6327, 17.9418),
    "Brundisium": (40.6327, 17.9418),
    "Sicily": (37.5994, 14.0154),
    "Madrid": (40.4168, -3.7038),
    "Barcelona": (41.3851, 2.1734),
    "Lisbon": (38.7223, -9.1393),

    # ---- Europe: north / east ----
    "Stockholm": (59.3293, 18.0686),
    "Copenhagen": (55.6761, 12.5683),
    "Oslo": (59.9139, 10.7522),
    "Christiania": (59.9139, 10.7522),
    "Helsinki": (60.1699, 24.9384),
    "Reykjavik": (64.1466, -21.9426),
    "Reykholt": (64.6608, -21.2944),
    "Amsterdam": (52.3676, 4.9041),
    "Antwerp": (51.2194, 4.4025),
    "Brussels": (50.8503, 4.3517),
    "Moscow": (55.7558, 37.6173),
    "St. Petersburg": (59.9311, 30.3609),
    "St Petersburg": (59.9311, 30.3609),
    "Petersburg": (59.9311, 30.3609),
    "Staraya Russa": (57.9944, 31.3544),
    "Sirmium": (44.9700, 19.6100),
    "Sremska Mitrovica": (44.9700, 19.6100),
    "Warsaw": (52.2297, 21.0122),
    "Prague": (50.0755, 14.4378),
    "Špindlerův Mlýn": (50.7260, 15.6090),
    "Spindlermühle": (50.7260, 15.6090),
    "Athens": (37.9755, 23.7348),
    "Chaeronea": (38.4920, 22.8440),
    "Thebes, Ancient Greece": (38.3236, 23.0489),
    "Corinth": (37.9057, 22.8796),
    "Lesbos": (39.1667, 26.3333),
    "Volos": (39.3617, 22.9458),
    "Iolcus": (39.3617, 22.9458),
    "Crete": (35.2401, 24.4709),
    "Istanbul": (41.0082, 28.9784),

    # ---- Americas ----
    "New York": (40.7128, -74.0060),
    "Manhattan": (40.7831, -73.9712),
    "Brooklyn": (40.6782, -73.9442),
    "Harlem": (40.8075, -73.9411),
    "Boston": (42.3601, -71.0589),
    "Cambridge, Massachusetts": (42.3736, -71.1097),
    "Wellesley": (42.2965, -71.2926),
    "Concord, Massachusetts": (42.4604, -71.3489),
    "Philadelphia": (39.9526, -75.1652),
    "Washington, D.C.": (38.9072, -77.0369),
    "Washington DC": (38.9072, -77.0369),
    "Silver Spring": (38.9924, -77.0827),
    "Baltimore": (39.2904, -76.6122),
    "Atlanta": (33.7490, -84.3880),
    "Clayton County": (33.5215, -84.3538),
    "Cincinnati": (39.1031, -84.5120),
    "Chicago": (41.8781, -87.6298),
    "Detroit": (42.3314, -83.0458),
    "Newark": (40.7357, -74.1724),
    "Eatonville, Florida": (28.6158, -81.3831),
    "Eatonville": (28.6158, -81.3831),
    "Hannibal, Missouri": (39.7083, -91.3585),
    "Cape Girardeau": (37.3059, -89.5181),
    "St. Louis": (38.6270, -90.1994),
    "Webster Groves": (38.5926, -90.3573),
    "New Orleans": (29.9511, -90.0715),
    "Las Vegas": (36.1699, -115.1398),
    "Los Angeles": (34.0522, -118.2437),
    "Hollywood": (34.0928, -118.3287),
    "Glendale, California": (34.1425, -118.2551),
    "Manhattan Beach": (33.8847, -118.4109),
    "San Francisco": (37.7749, -122.4194),
    "Berkeley": (37.8715, -122.2730),
    "Salinas": (36.6777, -121.6555),
    "Salinas Valley": (36.4247, -121.3263),
    "Estes Park": (40.3772, -105.5217),
    "Boulder, Colorado": (40.0150, -105.2705),
    "Walden Pond": (42.4401, -71.3378),
    "Knoxville, Tennessee": (35.9606, -83.9207),
    "Asheville": (35.5951, -82.5515),
    "Stamps, Arkansas": (33.3554, -93.4944),
    "Lorain, Ohio": (41.4528, -82.1824),
    "Ithaca, New York": (42.4534, -76.4735),
    "Westport, Connecticut": (41.1415, -73.3579),
    "Hartford, Connecticut": (41.7658, -72.6734),
    "Big Moose Lake": (43.8199, -74.8650),
    "Adirondacks": (43.8199, -74.8650),
    "Grand View-on-Hudson": (41.0790, -73.9007),
    "Rockland County": (41.1490, -74.0235),
    "Havana": (23.1136, -82.3666),
    "Mexico City": (19.4326, -99.1332),
    "Cuernavaca": (18.9242, -99.2216),
    "Buenos Aires": (-34.6037, -58.3816),
    "Rio de Janeiro": (-22.9068, -43.1729),
    "Bogotá": (4.7110, -74.0721),
    "Cartagena": (10.3910, -75.4794),
    "Aracataca": (10.5920, -74.1880),
    "Macondo": (10.5920, -74.1880),
    "Comala": (19.3193, -103.7555),  # real Comala in Colima
    "Santiago": (-33.4489, -70.6693),
    "Lima": (-12.0464, -77.0428),

    # ---- Africa / Middle East ----
    "Cairo": (30.0444, 31.2357),
    "Giza": (29.9792, 31.1342),
    "Algiers": (36.7538, 3.0588),
    "Oran": (35.6976, -0.6337),
    "Annaba": (36.9000, 7.7667),
    "Hippo Regius": (36.9000, 7.7667),
    "Lagos": (6.5244, 3.3792),
    "Nairobi": (-1.2921, 36.8219),
    "Cape Town": (-33.9249, 18.4241),
    "Johannesburg": (-26.2041, 28.0473),
    "Ixopo": (-30.1554, 30.0573),
    "Eastern Cape": (-33.3106, 26.5256),
    "Freetown": (8.4657, -13.2317),
    "Jerusalem": (31.7683, 35.2137),
    "Tehran": (35.6892, 51.3890),
    "Baghdad": (33.3152, 44.3661),
    "Damascus": (33.5138, 36.2765),
    "Beirut": (33.8938, 35.5018),
    "Byblos": (34.1236, 35.6517),
    "Ugarit": (35.6003, 35.7850),
    "Ashur": (35.4567, 43.2592),
    "Tangier": (35.7595, -5.8340),
    "Auschwitz": (50.0347, 19.1783),
    "Oświęcim": (50.0347, 19.1783),

    # ---- Asia / Pacific ----
    "Tokyo": (35.6762, 139.6503),
    "Kyoto": (35.0116, 135.7681),
    "Osaka": (34.6937, 135.5023),
    "Hakone": (35.2329, 139.1063),
    "Beijing": (39.9042, 116.4074),
    "Shanghai": (31.2304, 121.4737),
    "Mumbai": (19.0760, 72.8777),
    "Bombay": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Calcutta": (22.5726, 88.3639),
    "Kolkata": (22.5726, 88.3639),
    "Bankipore": (25.5941, 85.1376),
    "Patna": (25.5941, 85.1376),
    "Aymanam": (9.6308, 76.5483),
    "Ayemenem": (9.6308, 76.5483),
    "Kerala": (9.5916, 76.5222),
    "Lahore": (31.5204, 74.3587),
    "Ayodhya": (26.7922, 82.1998),
    "Saigon": (10.8231, 106.6297),
    "Chatham Islands": (-43.9523, -176.5612),
    "Sydney": (-33.8688, 151.2093),
}


def haversine_km(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    R = 6371.0
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# Author/work names that contain a city-name substring; strip these
# from the haystack before matching so e.g. "Jack London" doesn't
# count as a London reference.
NAME_STOPLIST = (
    "Jack London",
)


def find_mentioned_places(text: str) -> list[tuple[str, tuple[float, float]]]:
    """Return all canonical (phrase, coords) tuples whose phrase appears in text."""
    cleaned = text
    for name in NAME_STOPLIST:
        cleaned = re.sub(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", " ", cleaned, flags=re.IGNORECASE)
    out: list[tuple[str, tuple[float, float]]] = []
    for phrase, coords in CANONICAL.items():
        pattern = r"(?<![A-Za-z])" + re.escape(phrase) + r"(?![A-Za-z])"
        if re.search(pattern, cleaned, flags=re.IGNORECASE):
            out.append((phrase, coords))
    return out


def main() -> int:
    with open(BOOKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    books = data["books"]

    flagged: list[dict] = []
    checked = 0

    for book in books:
        loc = book.get("location") or {}
        coords = loc.get("coordinates")
        if not (isinstance(coords, list) and len(coords) == 2):
            continue
        try:
            book_pt = (float(coords[0]), float(coords[1]))
        except (TypeError, ValueError):
            continue

        haystack = " ".join(
            str(loc.get(k, "") or "") for k in ("name", "why_here")
        )
        mentions = find_mentioned_places(haystack)
        if not mentions:
            continue
        checked += 1

        # Distance to each mentioned place; pass if any within threshold
        distances = [(phrase, ref, haversine_km(book_pt, ref)) for phrase, ref in mentions]
        closest = min(distances, key=lambda x: x[2])
        if closest[2] > THRESHOLD_KM:
            flagged.append(
                {
                    "title": book["title"],
                    "author": book["author"],
                    "coords": coords,
                    "name": loc.get("name"),
                    "why_here": (loc.get("why_here") or "")[:120],
                    "mentioned": [m[0] for m in mentions],
                    "closest": closest[0],
                    "distance_km": round(closest[2], 1),
                }
            )

    print(f"Audit: {len(books)} books, {checked} mentioned a canonical place, {len(flagged)} flagged (>{THRESHOLD_KM}km).")
    print()
    for f in flagged:
        print(f"  {f['title']!r} by {f['author']}")
        print(f"    coords: {f['coords']}")
        print(f"    name:   {f['name']}")
        print(f"    why:    {f['why_here']}...")
        print(f"    mentioned: {', '.join(f['mentioned'])}")
        print(f"    closest mentioned: {f['closest']} ({f['distance_km']} km away)")
        print()

    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
