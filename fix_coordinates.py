
import json
from pathlib import Path

def fix_zero_coordinates():
    """Fix all books with (0,0) coordinates"""
    
    # Load the current data
    with open("data/books.json", "r") as f:
        data = json.load(f)
    
    # Coordinate fixes for books with (0,0)
    coordinate_fixes = {
        # Already fixed above, but including for completeness
        "The Lord of the Rings": [51.7520, -1.2577],  # Oxford (Tolkien's location)
        "A Clockwork Orange": [51.5074, -0.1278],     # London
        "A Farewell to Arms": [45.4642, 9.1900],      # Northern Italy (Milan area)
        "A Portrait of the Artist as a Young Man": [53.3498, -6.2603],  # Dublin
        "Absalom, Absalom!": [34.3668, -89.5186],     # Mississippi
        "Adventures of Huckleberry Finn": [35.1495, -90.0490],  # Mississippi River
        "Alice's Adventures in Wonderland": [51.7520, -1.2577],  # Oxford (Carroll's location)
        "All Quiet on the Western Front": [50.1109, 3.1040],    # Western Front, France
        "Antigone": [38.3172, 23.2066],               # Thebes, Greece
        "As I Lay Dying": [34.3668, -89.5186],        # Mississippi (Faulkner's Yoknapatawpha)
        "Bleak House": [51.5074, -0.1278],            # London
        "Brideshead Revisited": [51.7520, -1.2577],   # Oxford area
        "Buddenbrooks": [53.8654, 10.6865],           # Lübeck, Germany
        "Charlotte's Web": [44.3106, -69.7795],       # Maine
        "Demons": [55.7558, 37.6173],                 # Provincial Russia (Moscow area)
        "Doctor Faustus": [48.1351, 11.5820],         # Munich, Germany
        "Doctor Zhivago": [55.7558, 37.6173],         # Moscow, Russia
        "Gone Girl": [38.5767, -92.1735],             # Missouri
        "Heart of Darkness": [-4.0383, 21.7587],      # Congo River
        "If This Is a Man": [50.0270, 19.2044],       # Auschwitz, Poland
        "In Cold Blood": [38.5266, -96.7265],         # Kansas
        "King Lear": [52.2053, -0.1218],              # Ancient Britain (Cambridge area)
        "Lady Chatterley's Lover": [53.0000, -1.5000], # England (Nottinghamshire)
        "Life of Pi": [0.0000, -160.0000],            # Pacific Ocean (central)
        "Macbeth": [56.4907, -4.2026],                # Scotland (Stirling area)
        "Memoirs of Hadrian": [41.9028, 12.4964],     # Rome
        "Midnight's Children": [28.6139, 77.2090],    # New Delhi, India
        "Nana": [48.8566, 2.3522],                    # Paris
        "North and South": [53.4808, -2.2426],        # Manchester area (industrial England)
        "Oedipus the King": [38.3172, 23.2066],       # Thebes, Greece
        "One Day in the Life of Ivan Denisovich": [67.5000, 63.0000],  # Gulag (Siberia)
        "One Thousand and One Nights": [33.3152, 44.3661],  # Baghdad
        "Orlando": [51.5074, -0.1278],                # London
        "Pale Fire": [42.3601, -71.0589],             # New England (fictional New Wye)
        "Poems of Emily Dickinson": [42.3732, -72.5199],  # Amherst, Massachusetts
        "Silent Spring": [38.9072, -77.0369],         # Washington DC area
        "Sons and Lovers": [53.1581, -1.2649],        # Nottinghamshire
        "The Age of Innocence": [40.7128, -74.0060],  # New York City
        "The Big Sleep": [34.0522, -118.2437],        # Los Angeles
        "The Castle": [50.0755, 14.4378],             # Prague (Kafka's location)
        "The Charterhouse of Parma": [44.8015, 10.3279],  # Parma, Italy
        "The Complete Tales and Poems of Edgar Allan Poe": [39.2904, -76.6122],  # Baltimore
        "The Count of Monte Cristo": [43.2965, 5.3698],   # Marseille, France
        "The Good Soldier": [51.5074, -0.1278],       # London/Europe
        "The Grapes of Wrath": [35.2271, -101.8313],  # Oklahoma/California route
        "The Heart of the Matter": [8.4606, -11.7799], # Freetown, Sierra Leone
        "The Maltese Falcon": [37.7749, -122.4194],   # San Francisco
        "The Name of the Rose": [44.4949, 11.3426],   # Bologna area, Italy
        "The Picture of Dorian Gray": [51.5074, -0.1278],  # London
        "The Portrait of a Lady": [51.5074, -0.1278], # London
        "The Scarlet Letter": [42.3601, -71.0589],    # Boston
        "The Second Sex": [48.8566, 2.3522],          # Paris
        "The Stories of Anton Chekhov": [55.7558, 37.6173],  # Moscow area
        "The Sun Also Rises": [48.8566, 2.3522],      # Paris
        "The Talented Mr. Ripley": [40.8518, 14.2681], # Naples area, Italy
        "The Unbearable Lightness of Being": [50.0755, 14.4378],  # Prague
        "The Waste Land": [51.5074, -0.1278],         # London
        "The Wind in the Willows": [51.5074, -0.1278], # English countryside
        "The Woman in White": [51.5074, -0.1278],     # England
        "Tom Jones": [51.5074, -0.1278],              # England
        "Under the Volcano": [18.9061, -99.2337],     # Cuernavaca, Mexico
        "Wide Sargasso Sea": [18.1096, -77.2975]      # Jamaica
    }
    
    # Find and fix books with (0,0) coordinates
    books_fixed = 0
    for book in data["books"]:
        coords = book.get("location", {}).get("coordinates", [])
        if coords and len(coords) == 2 and coords[0] == 0.0 and coords[1] == 0.0:
            title = book.get("title", "")
            if title in coordinate_fixes:
                book["location"]["coordinates"] = coordinate_fixes[title]
                books_fixed += 1
                print(f"Fixed coordinates for: {title}")
    
    # Save the updated data
    with open("data/books.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Fixed {books_fixed} books with (0,0) coordinates")

if __name__ == "__main__":
    fix_zero_coordinates()
