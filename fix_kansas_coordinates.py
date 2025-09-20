
import json

# Coordinate fixes for books incorrectly using generic Kansas coordinates
kansas_coordinate_fixes = {
    # American Literature - Specific US Locations
    "On the Road": {
        "location": "Across United States",
        "new_coords": [39.8283, -98.5795],  # Actually correct - cross-country journey
        "reason": "Cross-country journey, Kansas center is appropriate"
    },
    "The Poems of Robert Frost": {
        "location": "New England, United States", 
        "new_coords": [44.2619, -72.5806],  # Vermont (Frost's primary residence)
        "reason": "Frost lived primarily in Vermont and New Hampshire"
    },
    "The Year of Magical Thinking": {
        "location": "New York City, United States",
        "new_coords": [40.7128, -74.0060],  # New York City
        "reason": "Joan Didion lived in NYC when writing this"
    },
    "The Structure of Scientific Revolutions": {
        "location": "United States",
        "new_coords": [41.8781, -87.6298],  # Chicago (University of Chicago)
        "reason": "Thomas Kuhn was at University of Chicago"
    },
    "Infinite Jest": {
        "location": "Fictional Location",
        "new_coords": [42.3601, -71.0589],  # Boston area
        "reason": "Set in Boston area, Wallace taught at nearby universities"
    },
    "Fear and Loathing in Las Vegas": {
        "location": "Las Vegas, Nevada, United States",
        "new_coords": [36.1699, -115.1398],  # Las Vegas
        "reason": "Story takes place in Las Vegas"
    },
    "I Know Why the Caged Bird Sings": {
        "location": "Arkansas, Stamps, United States",
        "new_coords": [33.3668, -93.7085],  # Stamps, Arkansas
        "reason": "Maya Angelou's childhood in Stamps, Arkansas"
    },
    "The God of Small Things": {
        "location": "India, Kerala, United States",
        "new_coords": [10.8505, 76.2711],  # Kerala, India
        "reason": "Story is set in Kerala, India"
    },
    "The Road": {
        "location": "United States",
        "new_coords": [35.0, -85.0],  # Southeastern US
        "reason": "Post-apocalyptic journey through southeastern US"
    },
    "East of Eden": {
        "location": "California, Massachusetts, Salinas, San Francisco, United States",
        "new_coords": [36.6777, -121.6555],  # Salinas Valley, California
        "reason": "Primary setting is Salinas Valley, California"
    },
    "A Wizard of Earthsea": {
        "location": "Fictional Location",
        "new_coords": [45.5152, -122.6784],  # Portland, Oregon (Le Guin's home)
        "reason": "Ursula K. Le Guin lived in Portland, Oregon"
    },
    "The Haunting of Hill House": {
        "location": "Fictional Location, New England",
        "new_coords": [42.3601, -71.0589],  # New England
        "reason": "Shirley Jackson set this in New England"
    },
    "The Secret History": {
        "location": "United States, Vermont",
        "new_coords": [44.2619, -72.5806],  # Vermont
        "reason": "Story takes place at fictional Vermont college"
    },
    "The World According to Garp": {
        "location": "Fictional Location, United States",
        "new_coords": [41.2033, -77.1945],  # Pennsylvania (Irving taught there)
        "reason": "John Irving taught in Pennsylvania"
    },
    "The Stand": {
        "location": "Boulder, Colorado, Las Vegas, United States",
        "new_coords": [40.0150, -105.2705],  # Boulder, Colorado
        "reason": "Boulder is major setting in the novel"
    },
    "Gilead": {
        "location": "Gilead, Iowa, United States",
        "new_coords": [42.0308, -93.6319],  # Iowa
        "reason": "Story is set in fictional Iowa town"
    },
    "The Things They Carried": {
        "location": "United States, Vietnam, Vietnam War",
        "new_coords": [16.0678, 108.2208],  # Central Vietnam
        "reason": "War stories primarily set in Vietnam"
    },
    "Housekeeping": {
        "location": "Fingerbone, United States",
        "new_coords": [47.6062, -117.4260],  # Idaho/Washington border
        "reason": "Fictional town based on Pacific Northwest"
    },
    "A Tree Grows in Brooklyn": {
        "location": "Brooklyn, New York, United States",
        "new_coords": [40.6782, -73.9442],  # Brooklyn, NY
        "reason": "Story takes place in Brooklyn"
    },
    "Ragtime": {
        "location": "New Rochelle, New York, New York City, United States",
        "new_coords": [40.9115, -73.7823],  # New Rochelle, NY
        "reason": "Primary setting is New Rochelle, NY"
    },
    "Play It As It Lays": {
        "location": "California, Hollywood, Los Angeles, United States",
        "new_coords": [34.0522, -118.2437],  # Los Angeles
        "reason": "Story set in Los Angeles"
    },
    "The World According to Garp": {
        "location": "Fictional Location, United States",
        "new_coords": [41.2033, -77.1945],  # Pennsylvania
        "reason": "Irving's fictional New England setting"
    },
    "The Amazing Adventures of Kavalier and Clay": {
        "location": "New York, New York City, United States",
        "new_coords": [40.7128, -74.0060],  # New York City
        "reason": "Story takes place in NYC"
    },
    "Bonfire of the Vanities": {
        "location": "Media, New York, New York City, United States",
        "new_coords": [40.7128, -74.0060],  # New York City
        "reason": "Story takes place in NYC"
    },
    "American Pastoral": {
        "location": "New Jersey, Newark, United States, Vietnam War",
        "new_coords": [40.7357, -74.1724],  # Newark, New Jersey
        "reason": "Story centers on Newark, New Jersey"
    },
    "The Joy Luck Club": {
        "location": "California, China, San Francisco, United States",
        "new_coords": [37.7749, -122.4194],  # San Francisco
        "reason": "Story takes place in San Francisco"
    }
}

# Load the JSON data
with open('data/books.json', 'r') as f:
    data = json.load(f)

books = data['books']
fixes_applied = 0

print("Fixing Kansas coordinate issues...\n")

# Apply coordinate fixes
for i, book in enumerate(books):
    title = book['title']
    
    if title in kansas_coordinate_fixes:
        old_coords = book['location']['coordinates']
        new_coords = kansas_coordinate_fixes[title]['new_coords']
        reason = kansas_coordinate_fixes[title]['reason']
        
        # Only apply fix if currently using Kansas coordinates
        if (abs(old_coords[0] - 39.8283) < 0.001 and 
            abs(old_coords[1] - (-98.5795)) < 0.001):
            
            book['location']['coordinates'] = new_coords
            fixes_applied += 1
            print(f"Fixed: {title}")
            print(f"  Location: {book['location']['name']}")
            print(f"  Old coords: {old_coords}")
            print(f"  New coords: {new_coords}")
            print(f"  Reason: {reason}")
            print()

# Save the updated JSON
data['books'] = books
with open('data/books.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✓ Fixed coordinates for {fixes_applied} books")
print("Saved updated data/books.json")
