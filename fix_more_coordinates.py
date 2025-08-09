import json

# More coordinate fixes for remaining books with wrong coordinates
more_fixes = {
    # Books with mixed England/US locations - choose primary setting
    "The Remains of the Day": {
        "location": "England, United States",
        "new_coords": [51.5074, -0.1278]  # Keep England (primary setting)
    },
    "The Turn of the Screw": {
        "location": "England, United States", 
        "new_coords": [51.5074, -0.1278]  # Keep England (primary setting)
    },
    "The Double Helix": {
        "location": "Cambridge, England, United States",
        "new_coords": [52.2053, 0.1218]  # Cambridge, England (where discovery happened)
    },
    "Four Quartets": {
        "location": "England, United States",
        "new_coords": [51.5074, -0.1278]  # Keep England (Eliot in England)
    },
    
    # Austria-Hungary
    "The Confusions of Young Törless": {
        "location": "Austria-Hungary",
        "new_coords": [48.2082, 16.3738]  # Vienna
    },
    
    # Balkans/Yugoslavia
    "Black Lamb and Grey Falcon": {
        "location": "Balkans, Yugoslavia",
        "new_coords": [44.7866, 20.4489]  # Belgrade (former Yugoslavia)
    },
    
    # Mixed India/England - choose primary
    "The Moonstone": {
        "location": "England, Great Britain, India, Yorkshire",
        "new_coords": [53.9591, -1.0815]  # Yorkshire, England (primary setting)
    },
    
    # Money/UK - keep UK
    "The General Theory of Employment, Interest and Money": {
        "location": "Money, United Kingdom",
        "new_coords": [51.5074, -0.1278]  # Keep London (Keynes' location)
    },
    
    # Cloud Atlas - multiple locations, use primary
    "Cloud Atlas": {
        "location": "Belgium, Fictional Location, Korea, Pacific Ocean, United Kingdom, United States",
        "new_coords": [-8.7832, -124.5085]  # Pacific Ocean (central to story)
    },
    
    # Fix books with Europe/America listed but wrong coordinates
    "Candide": {
        "location": "Europe and South America",
        "new_coords": [48.8566, 2.3522]  # Keep Paris (Voltaire/European focus)
    },
    "Giovanni's Room": {
        "location": "France, Paris, United States",
        "new_coords": [48.8566, 2.3522]  # Keep Paris (primary setting)
    },
    "Tender Is the Night": {
        "location": "France, French riviera, Paris, Switzerland, United States",
        "new_coords": [43.5528, 7.0174]  # Keep French Riviera (primary setting)
    },
    
    # Paradise Lost and Brave New World - metaphysical/fictional, keep as author location
    "Paradise Lost": {
        "location": "Multiple Settings (Heaven, Hell, Eden)",
        "new_coords": [51.5074, -0.1278]  # Keep London (Milton)
    },
    "Brave New World": {
        "location": "Dystopian Future Society",
        "new_coords": [51.5074, -0.1278]  # Keep London (Huxley) 
    }
}

# Load additional books that need fixing
additional_fixes = {
    "The Pilgrim's Progress": {
        "location": "Allegorical Journey",
        "new_coords": [52.0629, -0.7589]  # Bedford, England (Bunyan's location)
    },
    "The Divine Comedy": {
        "location": "Hell, Purgatory, Paradise",
        "new_coords": [43.7696, 11.2558]  # Florence (Dante's location)
    },
    "Gargantua and Pantagruel": {
        "location": "France",
        "new_coords": [47.4739, -0.5515]  # Loire Valley, France
    },
    "The Leopard": {
        "location": "Sicily",
        "new_coords": [37.5994, 14.0154]  # Sicily
    },
    "The Man Without Qualities": {
        "location": "Vienna",
        "new_coords": [48.2082, 16.3738]  # Vienna
    },
    "The Red Badge of Courage": {
        "location": "American Civil War Battlefield",
        "new_coords": [38.8977, -77.0365]  # Virginia/Maryland (Civil War region)
    },
    "Go Tell It on the Mountain": {
        "location": "Harlem, New York",
        "new_coords": [40.8116, -73.9465]  # Harlem, NYC
    },
    "The Crying of Lot 49": {
        "location": "California",
        "new_coords": [37.7749, -122.4194]  # San Francisco area
    },
    "The Age of Innocence": {
        "location": "New York City, 1870s",
        "new_coords": [40.7128, -74.0060]  # NYC
    },
    "All Quiet on the Western Front": {
        "location": "Western Front, WWI",
        "new_coords": [50.3667, 3.0667]  # Western Front (France/Belgium border)
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
    if title in more_fixes:
        old_coords = book['location']['coordinates']
        new_coords = more_fixes[title]['new_coords']
        if old_coords != new_coords:  # Only fix if different
            book['location']['coordinates'] = new_coords
            fixes_applied += 1
            print(f"Fixed: {title}")
            print(f"  Location: {book['location']['name']}")
            print(f"  Old coords: {old_coords} → New coords: {new_coords}")
    
    elif title in additional_fixes:
        # Check if coordinates need updating based on location
        location_name = book['location']['name'].lower()
        expected = additional_fixes[title]
        if expected['location'].lower() in location_name:
            old_coords = book['location']['coordinates']
            new_coords = expected['new_coords']
            if old_coords != new_coords:
                book['location']['coordinates'] = new_coords
                fixes_applied += 1
                print(f"Fixed: {title}")
                print(f"  Location: {book['location']['name']}")
                print(f"  Old coords: {old_coords} → New coords: {new_coords}")

# Save the updated JSON
data['books'] = books
with open('data/books.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✓ Fixed coordinates for {fixes_applied} books")
print("Saved updated data/books.json")