import json

# Coordinate fixes for books with wrong London default coordinates
coordinate_fixes = {
    # US Locations
    "The Corrections": {
        "location": "Midwest, New York, New York City, Pennsylvania, United States",
        "new_coords": [40.0, -89.0]  # Central US/Midwest
    },
    "One Flew Over the Cuckoo's Nest": {
        "location": "Oregon, United States", 
        "new_coords": [44.0, -120.5]  # Oregon
    },
    "Light in August": {
        "location": "Jefferson, Mississippi, United States",
        "new_coords": [32.3547, -90.1848]  # Mississippi
    },
    "Rabbit, Run": {
        "location": "Mount Judge, Pennsylvania, Suburbia, United States",
        "new_coords": [40.4406, -79.9959]  # Pennsylvania
    },
    "A Good Man Is Hard to Find": {
        "location": "Georgia, Southern US, United States",
        "new_coords": [32.6781, -83.2229]  # Georgia
    },
    "Portnoy's Complaint": {
        "location": "New Jersey, New York, Newark, United States",
        "new_coords": [40.7357, -74.1724]  # Newark, NJ
    },
    "My Antonia": {
        "location": "Nebraska, United States",
        "new_coords": [41.4925, -99.9018]  # Nebraska
    },
    
    # European Locations
    "The Prince": {
        "location": "Florence, Italy",
        "new_coords": [43.7696, 11.2558]  # Florence
    },
    "The Prime of Miss Jean Brodie": {
        "location": "Edinburgh, Scotland",
        "new_coords": [55.9533, -3.1883]  # Edinburgh
    },
    "The Good Soldier Svejk": {
        "location": "Austria-Hungary, Czech Republic, Prague",
        "new_coords": [50.0755, 14.4378]  # Prague
    },
    "Austerlitz": {
        "location": "Europe",
        "new_coords": [48.8566, 2.3522]  # Paris (central Europe)
    },
    
    # Caribbean/South American
    "Love in the Time of Cholera": {
        "location": "Caribbean, Colombia",
        "new_coords": [10.3910, -75.4794]  # Cartagena, Colombia
    },
    
    # African/Mediterranean
    "Confessions": {
        "location": "Algeria, Hippo (Ancient City), Italy, Rome",
        "new_coords": [36.9, 7.7667]  # Hippo (Annaba, Algeria)
    },
    
    # Pacific/Island
    "Robinson Crusoe": {
        "location": "Tropical Island",
        "new_coords": [-20.0, -70.0]  # Juan Fernández Islands (inspiration)
    },
    
    # Galapagos
    "On the Origin of Species": {
        "location": "Ecuador, Galapagos Islands, United Kingdom",
        "new_coords": [-0.9538, -90.9656]  # Galapagos Islands
    },
    
    # Mixed locations - keep as is for now
    "The Hitchhiker's Guide to the Galaxy": {
        "location": "Fictional Location, Space, United States",
        "new_coords": [42.3601, -71.0589]  # Boston (Douglas Adams lived there)
    },
    
    # Keep these as London (publication location for fictional/metaphysical)
    "Paradise Lost": {
        "location": "Multiple Settings (Heaven, Hell, Eden)",
        "new_coords": [51.5074, -0.1278]  # Keep London (Milton's location)
    },
    "Brave New World": {
        "location": "Dystopian Future Society",
        "new_coords": [51.5074, -0.1278]  # Keep London (Huxley's location)
    }
}

# Additional fixes for non-London mismatches
other_fixes = {
    "The Possessed": {
        "location": "Provincial Russia",
        "new_coords": [55.7558, 37.6173]  # Moscow region
    },
    "Candide": {
        "location": "Europe and South America",
        "new_coords": [48.8566, 2.3522]  # Paris (Voltaire's location)
    },
    "Giovanni's Room": {
        "location": "France, Paris, United States",
        "new_coords": [48.8566, 2.3522]  # Paris (primary setting)
    },
    "Tender Is the Night": {
        "location": "France, French riviera, Paris, Switzerland, United States",
        "new_coords": [43.5528, 7.0174]  # French Riviera
    },
    "Democracy in America": {
        "location": "France, United States",
        "new_coords": [38.9072, -77.0369]  # Washington DC (focus on America)
    },
    "Tropic of Cancer": {
        "location": "France, New York, Paris",
        "new_coords": [48.8566, 2.3522]  # Paris (primary setting)
    },
    "Siddhartha": {
        "location": "Fictional Location, Germany, India",
        "new_coords": [26.9124, 75.7873]  # India (story setting)
    },
    "The Power and the Glory": {
        "location": "Mexico, Tabasco, United States",
        "new_coords": [17.9892, -92.9475]  # Tabasco, Mexico
    },
    "Naked Lunch": {
        "location": "Fictional Location, Mexico, Morocco, Tangier, United States",
        "new_coords": [35.7595, -5.8340]  # Tangier, Morocco
    },
    "The Lover": {
        "location": "France, Vietnam",
        "new_coords": [10.8231, 106.6297]  # Saigon/Ho Chi Minh City, Vietnam
    }
}

# Load the JSON
with open('data/books.json', 'r') as f:
    data = json.load(f)

books = data['books']
fixes_applied = 0

# Apply coordinate fixes
for i, book in enumerate(books):
    title = book['title']
    
    # Check if this book needs fixing
    if title in coordinate_fixes:
        old_coords = book['location']['coordinates']
        new_coords = coordinate_fixes[title]['new_coords']
        book['location']['coordinates'] = new_coords
        fixes_applied += 1
        print(f"Fixed: {title}")
        print(f"  Old coords: {old_coords} → New coords: {new_coords}")
    
    elif title in other_fixes:
        old_coords = book['location']['coordinates']
        new_coords = other_fixes[title]['new_coords']
        book['location']['coordinates'] = new_coords
        fixes_applied += 1
        print(f"Fixed: {title}")
        print(f"  Old coords: {old_coords} → New coords: {new_coords}")

# Save the updated JSON
data['books'] = books
with open('data/books.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✓ Fixed coordinates for {fixes_applied} books")
print("Saved updated data/books.json")