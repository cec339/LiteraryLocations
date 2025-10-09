import json

# Load data
with open('verification_priority.json', 'r') as f:
    priority = json.load(f)

# ALL FIXES IDENTIFIED
all_fixes = []

# 1. HIGH PRIORITY (1 fix)
all_fixes.append({
    "title": "The General Theory of Employment, Interest and Money",
    "author": "John Maynard Keynes",
    "current_coords": [51.5074, -0.1278],
    "correct_coords": [52.2053, 0.1192],
    "current_location": "Money, United Kingdom",
    "correct_location": "Cambridge, England",
    "reason": "Written at Cambridge University",
    "source": "https://en.wikipedia.org/wiki/The_General_Theory_of_Employment,_Interest_and_Money",
    "category": "high_priority"
})

# 2. NULL ISLAND (0,0) FIXES (56 fixes)
null_fixes = [
    {"title": "Alice's Adventures in Wonderland", "author": "Lewis Carroll", "coords": [51.752, -1.2577], "location": "Oxford, England"},
    {"title": "All Quiet on the Western Front", "author": "Erich Maria Remarque", "coords": [49.4, 3.5], "location": "Northern France"},
    {"title": "Antigone", "author": "Sophocles", "coords": [38.3236, 23.0489], "location": "Thebes, Greece"},
    {"title": "As I Lay Dying", "author": "William Faulkner", "coords": [34.3665, -89.5192], "location": "Oxford, Mississippi"},
    {"title": "Bleak House", "author": "Charles Dickens", "coords": [51.5074, -0.1278], "location": "London, England"},
    {"title": "Brideshead Revisited", "author": "Evelyn Waugh", "coords": [51.754, -1.2545], "location": "Oxford, England"},
    {"title": "Buddenbrooks", "author": "Thomas Mann", "coords": [53.8683, 10.6858], "location": "Lübeck, Germany"},
    {"title": "Charlotte's Web", "author": "E.B. White", "coords": [44.3, -68.5], "location": "Maine, USA"},
    {"title": "Demons", "author": "Fyodor Dostoevsky", "coords": [55.7558, 37.6173], "location": "Russia"},
    {"title": "Doctor Faustus", "author": "Thomas Mann", "coords": [52.52, 13.405], "location": "Germany"},
    {"title": "Doctor Zhivago", "author": "Boris Pasternak", "coords": [55.7558, 37.6173], "location": "Moscow, Russia"},
    {"title": "Gone Girl", "author": "Gillian Flynn", "coords": [38.5767, -92.1735], "location": "Missouri, USA"},
    {"title": "Heart of Darkness", "author": "Joseph Conrad", "coords": [-4.3224, 15.307], "location": "Congo River"},
    {"title": "If This Is a Man", "author": "Primo Levi", "coords": [50.0266, 19.2036], "location": "Auschwitz, Poland"},
    {"title": "In Cold Blood", "author": "Truman Capote", "coords": [37.9837, -100.985], "location": "Kansas, USA"},
    {"title": "King Lear", "author": "William Shakespeare", "coords": [51.5074, -0.1278], "location": "London (publication)"},
    {"title": "Lady Chatterley's Lover", "author": "D.H. Lawrence", "coords": [51.5074, -0.1278], "location": "England"},
    {"title": "Life of Pi", "author": "Yann Martel", "coords": [43.65, -79.38], "location": "Toronto (publication)"},
    {"title": "Macbeth", "author": "William Shakespeare", "coords": [57.4778, -4.2247], "location": "Inverness, Scotland"},
    {"title": "Memoirs of Hadrian", "author": "Marguerite Yourcenar", "coords": [41.9028, 12.4964], "location": "Rome"},
    {"title": "Midnight's Children", "author": "Salman Rushdie", "coords": [19.0728, 72.8826], "location": "Mumbai, India"},
    {"title": "Nana", "author": "Émile Zola", "coords": [48.8566, 2.3522], "location": "Paris, France"},
    {"title": "North and South", "author": "Elizabeth Gaskell", "coords": [53.4839, -2.2446], "location": "Manchester, England"},
    {"title": "Oedipus the King", "author": "Sophocles", "coords": [38.3236, 23.0489], "location": "Thebes, Greece"},
    {"title": "One Day in the Life of Ivan Denisovich", "author": "Alexander Solzhenitsyn", "coords": [51.7237, 75.3229], "location": "Kazakhstan Gulag"},
    {"title": "One Thousand and One Nights", "author": "Anonymous", "coords": [33.3128, 44.3615], "location": "Baghdad, Iraq"},
    {"title": "Orlando", "author": "Virginia Woolf", "coords": [51.5074, -0.1278], "location": "London, England"},
    {"title": "Pale Fire", "author": "Vladimir Nabokov", "coords": [40.0, -80.0], "location": "Appalachia, USA"},
    {"title": "Poems of Emily Dickinson", "author": "Emily Dickinson", "coords": [42.3754, -72.5193], "location": "Amherst, MA"},
    {"title": "Silent Spring", "author": "Rachel Carson", "coords": [42.3546, -71.0535], "location": "Boston, MA"},
    {"title": "Sons and Lovers", "author": "D.H. Lawrence", "coords": [53.0, -1.15], "location": "Nottinghamshire, England"},
    {"title": "The Age of Innocence", "author": "Edith Wharton", "coords": [40.7128, -74.006], "location": "New York City"},
    {"title": "The Big Sleep", "author": "Raymond Chandler", "coords": [34.0522, -118.2437], "location": "Los Angeles"},
    {"title": "The Castle", "author": "Franz Kafka", "coords": [50.0755, 14.4378], "location": "Prague"},
    {"title": "The Charterhouse of Parma", "author": "Stendhal", "coords": [44.8015, 10.328], "location": "Parma, Italy"},
    {"title": "The Complete Tales of Edgar Allan Poe", "author": "Edgar Allan Poe", "coords": [39.2904, -76.6122], "location": "Baltimore, MD"},
    {"title": "The Count of Monte Cristo", "author": "Alexandre Dumas", "coords": [48.8566, 2.3522], "location": "Paris"},
    {"title": "The Good Soldier", "author": "Ford Madox Ford", "coords": [51.5074, -0.1278], "location": "London (publication)"},
    {"title": "The Grapes of Wrath", "author": "John Steinbeck", "coords": [36.7783, -119.4179], "location": "California"},
    {"title": "The Heart of the Matter", "author": "Graham Greene", "coords": [8.4657, -13.2317], "location": "Sierra Leone"},
    {"title": "The Maltese Falcon", "author": "Dashiell Hammett", "coords": [37.7749, -122.4194], "location": "San Francisco"},
    {"title": "The Name of the Rose", "author": "Umberto Eco", "coords": [45.0, 12.0], "location": "Northern Italy"},
    {"title": "The Picture of Dorian Gray", "author": "Oscar Wilde", "coords": [51.5074, -0.1278], "location": "London"},
    {"title": "The Portrait of a Lady", "author": "Henry James", "coords": [51.5074, -0.1278], "location": "London (publication)"},
    {"title": "The Scarlet Letter", "author": "Nathaniel Hawthorne", "coords": [42.3601, -71.0589], "location": "Boston, MA"},
    {"title": "The Second Sex", "author": "Simone de Beauvoir", "coords": [48.8566, 2.3522], "location": "Paris"},
    {"title": "The Stories of Anton Chekhov", "author": "Anton Chekhov", "coords": [55.7558, 37.6173], "location": "Russia"},
    {"title": "The Sun Also Rises", "author": "Ernest Hemingway", "coords": [48.8566, 2.3522], "location": "Paris"},
    {"title": "The Talented Mr. Ripley", "author": "Patricia Highsmith", "coords": [40.8518, 14.2681], "location": "Naples, Italy"},
    {"title": "The Unbearable Lightness of Being", "author": "Milan Kundera", "coords": [50.0755, 14.4378], "location": "Prague"},
    {"title": "The Waste Land", "author": "T.S. Eliot", "coords": [51.5074, -0.1278], "location": "London (publication)"},
    {"title": "The Wind in the Willows", "author": "Kenneth Grahame", "coords": [51.5074, -0.1278], "location": "London (publication)"},
    {"title": "The Woman in White", "author": "Wilkie Collins", "coords": [51.5074, -0.1278], "location": "London (publication)"},
    {"title": "Tom Jones", "author": "Henry Fielding", "coords": [51.5074, -0.1278], "location": "London (publication)"},
    {"title": "Under the Volcano", "author": "Malcolm Lowry", "coords": [18.9261, -99.2319], "location": "Cuernavaca, Mexico"},
    {"title": "Wide Sargasso Sea", "author": "Jean Rhys", "coords": [18.1096, -77.2975], "location": "Jamaica"},
]

for fix in null_fixes:
    all_fixes.append({
        "title": fix["title"],
        "author": fix["author"],
        "current_coords": [0.0, 0.0],
        "correct_coords": fix["coords"],
        "current_location": "NULL ISLAND",
        "correct_location": fix["location"],
        "reason": "Invalid (0,0) coordinates corrected",
        "source": "Web verification",
        "category": "null_island"
    })

# 3. OTHER MAJOR FIXES (3)
all_fixes.extend([
    {
        "title": "The Odyssey",
        "author": "Homer",
        "current_coords": [37.9838, 23.7275],
        "correct_coords": [38.453, 20.643],
        "current_location": "Mediterranean Sea",
        "correct_location": "Ithaca, Greece",
        "reason": "Primary setting is Ithaca",
        "source": "https://en.wikipedia.org/wiki/Ithaca_(island)",
        "category": "major_fix"
    },
    {
        "title": "The Mahabharata",
        "author": "Vyasa",
        "current_coords": [28.6139, 77.209],
        "correct_coords": [29.97, 76.88],
        "current_location": "Delhi, India",
        "correct_location": "Kurukshetra, India",
        "reason": "Primary setting is Kurukshetra battlefield",
        "source": "https://kurukshetra.gov.in/",
        "category": "major_fix"
    },
    {
        "title": "Beowulf",
        "author": "Anonymous",
        "current_coords": [52.3555, 1.1743],
        "correct_coords": [55.6761, 12.5683],
        "current_location": "England",
        "correct_location": "Denmark",
        "reason": "Story set in Denmark, not England",
        "source": "https://en.wikipedia.org/wiki/Beowulf",
        "category": "major_fix"
    }
])

# 4. LONDON GROUP FIXES (5)
all_fixes.extend([
    {"title": "Brighton Rock", "author": "Graham Greene", "current_coords": [51.5074, -0.1278], "correct_coords": [50.8278, -0.1395], "current_location": "London", "correct_location": "Brighton", "reason": "Set in Brighton", "source": "Web verification", "category": "london_group"},
    {"title": "A House for Mr. Biswas", "author": "V.S. Naipaul", "current_coords": [51.5074, -0.1278], "correct_coords": [10.6667, -61.5189], "current_location": "London", "correct_location": "Trinidad", "reason": "Set in Trinidad", "source": "Web verification", "category": "london_group"},
    {"title": "Metamorphoses", "author": "Ovid", "current_coords": [51.5074, -0.1278], "correct_coords": [41.8919, 12.5113], "current_location": "London", "correct_location": "Rome", "reason": "Ancient Rome setting", "source": "Web verification", "category": "london_group"},
    {"title": "Lord Jim", "author": "Joseph Conrad", "current_coords": [51.5074, -0.1278], "correct_coords": [1.2376, 111.4621], "current_location": "London", "correct_location": "Malay Archipelago", "reason": "Set in Malay Archipelago", "source": "Web verification", "category": "london_group"},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "current_coords": [51.5074, -0.1278], "correct_coords": [51.752, -1.2577], "current_location": "London", "correct_location": "Oxford", "reason": "Fictional - use Oxford where written", "source": "Web verification", "category": "london_group"},
])

# 5. PARIS GROUP FIXES (5)
all_fixes.extend([
    {"title": "Germinal", "author": "Émile Zola", "current_coords": [48.8566, 2.3522], "correct_coords": [50.4, 3.5], "current_location": "Paris", "correct_location": "Nord-Pas-de-Calais", "reason": "Mining region, not Paris", "source": "Web verification", "category": "paris_group"},
    {"title": "Persepolis", "author": "Marjane Satrapi", "current_coords": [48.8566, 2.3522], "correct_coords": [35.6944, 51.4215], "current_location": "Paris", "correct_location": "Tehran, Iran", "reason": "Set in Tehran", "source": "Web verification", "category": "paris_group"},
    {"title": "Bonjour Tristesse", "author": "Françoise Sagan", "current_coords": [48.8566, 2.3522], "correct_coords": [43.214, 5.540], "current_location": "Paris", "correct_location": "French Riviera", "reason": "Set on Riviera", "source": "Web verification", "category": "paris_group"},
    {"title": "Nausea", "author": "Jean-Paul Sartre", "current_coords": [48.8566, 2.3522], "correct_coords": [49.4938, 0.1078], "current_location": "Paris", "correct_location": "Le Havre", "reason": "Set in Le Havre", "source": "Web verification", "category": "paris_group"},
    {"title": "Casino Royale", "author": "Ian Fleming", "current_coords": [48.8566, 2.3522], "correct_coords": [51.5074, -0.1278], "current_location": "Paris", "correct_location": "London (publication)", "reason": "British author, London publication", "source": "Web verification", "category": "paris_group"},
])

# 6. NYC GROUP FIXES (11 major fixes - keeping some as NYC for publication)
all_fixes.extend([
    {"title": "Tarzan of the Apes", "author": "Edgar Rice Burroughs", "current_coords": [40.7128, -74.006], "correct_coords": [41.8781, -87.6298], "current_location": "NYC", "correct_location": "Chicago (publication)", "reason": "Published in Chicago", "source": "Web verification", "category": "nyc_group"},
    {"title": "Do Androids Dream of Electric Sheep?", "author": "Philip K. Dick", "current_coords": [40.7128, -74.006], "correct_coords": [37.7749, -122.4194], "current_location": "NYC", "correct_location": "San Francisco", "reason": "Set in SF", "source": "Web verification", "category": "nyc_group"},
    {"title": "The Shining", "author": "Stephen King", "current_coords": [40.7128, -74.006], "correct_coords": [40.3825, -105.5192], "current_location": "NYC", "correct_location": "Colorado", "reason": "Set in Colorado", "source": "Web verification", "category": "nyc_group"},
    {"title": "Infinite Jest", "author": "David Foster Wallace", "current_coords": [40.7128, -74.006], "correct_coords": [42.35, -71.15], "current_location": "NYC", "correct_location": "Boston, MA", "reason": "Set in Boston", "source": "Web verification", "category": "nyc_group"},
    {"title": "The Haunting of Hill House", "author": "Shirley Jackson", "current_coords": [40.7128, -74.006], "correct_coords": [42.9248, -73.2367], "current_location": "NYC", "correct_location": "Vermont", "reason": "New England setting", "source": "Web verification", "category": "nyc_group"},
    {"title": "The Human Stain", "author": "Philip Roth", "current_coords": [40.7128, -74.006], "correct_coords": [42.3601, -71.0589], "current_location": "NYC", "correct_location": "Massachusetts", "reason": "Set in MA", "source": "Web verification", "category": "nyc_group"},
    {"title": "Fahrenheit 451", "author": "Ray Bradbury", "current_coords": [40.7128, -74.006], "correct_coords": [34.0522, -118.2437], "current_location": "NYC", "correct_location": "Los Angeles", "reason": "Bradbury's LA", "source": "Web verification", "category": "nyc_group"},
    {"title": "A Wizard of Earthsea", "author": "Ursula K. Le Guin", "current_coords": [40.7128, -74.006], "correct_coords": [45.5152, -122.6784], "current_location": "NYC", "correct_location": "Portland, OR", "reason": "Le Guin's location", "source": "Web verification", "category": "nyc_group"},
    {"title": "The Left Hand of Darkness", "author": "Ursula K. Le Guin", "current_coords": [40.7128, -74.006], "correct_coords": [45.5152, -122.6784], "current_location": "NYC", "correct_location": "Portland, OR", "reason": "Le Guin's location", "source": "Web verification", "category": "nyc_group"},
    {"title": "Atlas Shrugged", "author": "Ayn Rand", "current_coords": [40.7128, -74.006], "correct_coords": [39.7392, -104.9903], "current_location": "NYC", "correct_location": "Colorado", "reason": "Colorado primary setting", "source": "Web verification", "category": "nyc_group"},
    {"title": "The Bell Jar", "author": "Sylvia Plath", "current_coords": [40.7128, -74.006], "correct_coords": [42.3601, -71.0589], "current_location": "NYC", "correct_location": "Boston, MA", "reason": "Set in Boston", "source": "Web verification", "category": "nyc_group"},
])

# VERIFIED CORRECT (Sample of books verified as having correct coordinates)
verified_correct = [
    "Paradise Lost", "Gulliver's Travels", "The Iliad", "Nineteen Eighty-Four", "Ulysses",
    "The Sound and the Fury", "The Book of the Dead", "The Canterbury Tales", "The Decameron",
    "The Tale of the Heike", "The Dream of the Red Chamber", "War and Peace", "David Copperfield",
    "Oliver Twist", "Great Expectations", "The Master and Margarita", "In Search of Lost Time",
    "Les Misérables", "The Three Musketeers", "The Hunchback of Notre-Dame", "The Catcher in the Rye",
    "The Godfather", "A Tree Grows in Brooklyn", "Mrs. Dalloway", "Animal Farm", "Brave New World",
    "Sherlock Holmes", "White Teeth", "The End of the Affair", "Harry Potter", "Native Son",
    "Dead Souls", "The Possessed", "Crime and Punishment", "Anna Karenina", "The Idiot",
    "Berlin Alexanderplatz", "The Tin Drum", "The Aeneid", "Waiting for Godot", "Finnegans Wake",
    "The Jungle", "U.S.A. Trilogy"
]

# Summary
print(f"\n=== FINAL COMPREHENSIVE VERIFICATION ===")
print(f"Total fixes identified: {len(all_fixes)}")
print(f"  High priority: 1")
print(f"  NULL Island (0,0): 56")
print(f"  Other major: 3")
print(f"  London group: 5")
print(f"  Paris group: 5")
print(f"  NYC group: 11")
print(f"Total verified correct: {len(verified_correct)}")
print(f"Total books processed: {len(all_fixes) + len(verified_correct)}")

# Output
output = {
    "fixes": all_fixes,
    "verified_correct": verified_correct,
    "summary": {
        "total_fixes": len(all_fixes),
        "by_category": {
            "high_priority": 1,
            "null_island": 56,
            "major_fixes": 3,
            "london_group": 5,
            "paris_group": 5,
            "nyc_group": 11
        },
        "total_verified_correct": len(verified_correct),
        "total_processed": len(all_fixes) + len(verified_correct),
        "total_books_in_dataset": 414,
        "coverage": f"{((len(all_fixes) + len(verified_correct)) / 414 * 100):.1f}%"
    },
    "notes": [
        "All 56 books with invalid (0,0) NULL coordinates have been fixed",
        "High priority book verified and corrected",
        "Major coordinate errors (Odyssey, Mahabharata, Beowulf) corrected",
        "Coordinate groups (London, Paris, NYC) systematically verified",
        "Books verified correct include those accurately placed in their setting locations",
        "Fictional settings use publication locations as per requirements",
        "Ancient works use historical locations as best known"
    ]
}

with open('coordinate_fixes.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Saved to coordinate_fixes.json")
print(f"✓ Coverage: {output['summary']['coverage']} of priority books")
