import json
import re

def check_location_mismatch(location_name, coordinates):
    """Check if coordinates match the stated location"""
    lat, lon = coordinates
    location_lower = location_name.lower()
    
    # Common coordinate patterns
    london_coords = (51.5074, -0.1278)
    
    mismatches = []
    
    # Check for London coordinates used incorrectly
    if abs(lat - london_coords[0]) < 0.01 and abs(lon - london_coords[1]) < 0.01:
        # These are London coordinates
        if not any(place in location_lower for place in ['london', 'england', 'britain', 'uk']):
            if 'fictional' not in location_lower:
                mismatches.append("Has London coordinates but location doesn't mention London/England")
    
    # Check for US locations with non-US coordinates
    us_indicators = ['united states', 'america', 'usa', 'u.s.', 'new york', 'california', 
                     'chicago', 'boston', 'midwest', 'texas', 'florida', 'pennsylvania',
                     'ohio', 'michigan', 'alabama', 'mississippi', 'georgia', 'virginia']
    if any(place in location_lower for place in us_indicators):
        # US locations should have negative longitude (west) and latitude between ~25-49
        if not (-130 < lon < -65):  # Continental US longitude range
            mismatches.append(f"US location but longitude {lon} is outside US range")
        if not (25 < lat < 49):  # Continental US latitude range  
            mismatches.append(f"US location but latitude {lat} is outside US range")
    
    # Check for European locations with wrong coordinates
    europe_indicators = ['france', 'paris', 'germany', 'berlin', 'italy', 'rome', 'spain', 
                        'madrid', 'russia', 'moscow', 'austria', 'vienna', 'prague']
    if any(place in location_lower for place in europe_indicators):
        # European locations should have positive longitude (mostly) and latitude 35-70
        if not (-10 < lon < 40):  # European longitude range
            mismatches.append(f"European location but longitude {lon} is outside Europe range")
    
    # Check for African locations
    africa_indicators = ['africa', 'egypt', 'nigeria', 'kenya', 'south africa', 'morocco']
    if any(place in location_lower for place in africa_indicators):
        if not (-20 < lon < 55):  # African longitude range
            mismatches.append(f"African location but longitude {lon} is outside Africa range")
    
    # Check for Asian locations
    asia_indicators = ['china', 'japan', 'india', 'afghanistan', 'pakistan', 'vietnam', 
                      'korea', 'thailand', 'indonesia', 'philippines', 'bangladesh']
    if any(place in location_lower for place in asia_indicators):
        if not (20 < lon < 150):  # Asian longitude range
            mismatches.append(f"Asian location but longitude {lon} is outside Asia range")
    
    # Check for Australian/Oceania locations
    oceania_indicators = ['australia', 'new zealand', 'sydney', 'melbourne']
    if any(place in location_lower for place in oceania_indicators):
        if not (110 < lon < 180 or -180 < lon < -170):  # Oceania longitude range
            mismatches.append(f"Oceania location but longitude {lon} is outside Oceania range")
    
    # Check for South American locations
    sa_indicators = ['brazil', 'argentina', 'chile', 'peru', 'colombia', 'venezuela']
    if any(place in location_lower for place in sa_indicators):
        if not (-85 < lon < -35):  # South American longitude range
            mismatches.append(f"South American location but longitude {lon} is outside SA range")
    
    return mismatches

# Load and analyze the data
with open('data/books.json', 'r') as f:
    data = json.load(f)

books = data['books']
print(f"Auditing {len(books)} books for coordinate mismatches...\n")

issues_found = []
london_default_issues = []

for i, book in enumerate(books):
    location_name = book['location']['name']
    coordinates = book['location']['coordinates']
    
    # Check for obvious mismatches
    mismatches = check_location_mismatch(location_name, coordinates)
    
    if mismatches:
        # Special case for London default coordinates
        if coordinates == [51.5074, -0.1278] and 'london' not in location_name.lower():
            london_default_issues.append({
                'index': i,
                'title': book['title'],
                'author': book['author'],
                'location_name': location_name,
                'coordinates': coordinates,
                'issues': mismatches
            })
        else:
            issues_found.append({
                'index': i,
                'title': book['title'],
                'author': book['author'],
                'location_name': location_name,
                'coordinates': coordinates,
                'issues': mismatches
            })

# Print books using London as default coordinates
if london_default_issues:
    print(f"=== BOOKS USING LONDON AS DEFAULT COORDINATES ({len(london_default_issues)} found) ===\n")
    for issue in london_default_issues[:20]:  # Limit output
        print(f"Index {issue['index']}: {issue['title']} by {issue['author']}")
        print(f"  Location: {issue['location_name']}")
        print(f"  Coordinates: {issue['coordinates']}")
        print(f"  Issue: {issue['issues'][0]}")
        print()

# Print other coordinate issues
if issues_found:
    print(f"\n=== OTHER COORDINATE MISMATCHES ({len(issues_found)} found) ===\n")
    for issue in issues_found[:10]:  # Limit output
        print(f"Index {issue['index']}: {issue['title']} by {issue['author']}")
        print(f"  Location: {issue['location_name']}")
        print(f"  Coordinates: {issue['coordinates']}")
        print(f"  Issues: {', '.join(issue['issues'])}")
        print()

print(f"\nSummary:")
print(f"  - {len(london_default_issues)} books incorrectly using London default coordinates")
print(f"  - {len(issues_found)} books with other coordinate mismatches")
print(f"  - Total issues: {len(london_default_issues) + len(issues_found)}")