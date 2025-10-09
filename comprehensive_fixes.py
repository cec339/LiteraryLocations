import json

# Load verification data
with open('verification_priority.json', 'r') as f:
    priority = json.load(f)

fixes = []
verified_correct = []

# HIGH PRIORITY FIX
fixes.append({
    "title": "The General Theory of Employment, Interest and Money",
    "author": "John Maynard Keynes",
    "current_coords": [51.5074, -0.1278],
    "correct_coords": [52.2053, 0.1192],
    "current_location": "Money, United Kingdom",
    "correct_location": "Cambridge, England",
    "reason": "Written at Cambridge University where Keynes was professor",
    "source": "https://en.wikipedia.org/wiki/The_General_Theory_of_Employment,_Interest_and_Money"
})

# ALL 56 NULL ISLAND (0,0) FIXES
null_fixes = [
    {"title": "Alice's Adventures in Wonderland", "author": "Lewis Carroll", "coords": [51.752, -1.2577], "location": "Oxford, England", "reason": "Fictional setting - use Oxford where Carroll wrote it"},
    {"title": "All Quiet on the Western Front", "author": "Erich Maria Remarque", "coords": [49.4, 3.5], "location": "Northern France, Western Front", "reason": "WWI Western Front setting"},
    {"title": "Antigone", "author": "Sophocles", "coords": [38.3236, 23.0489], "location": "Thebes, Ancient Greece", "reason": "Set in ancient Thebes"},
    {"title": "As I Lay Dying", "author": "William Faulkner", "coords": [34.3665, -89.5192], "location": "Oxford, Mississippi", "reason": "Fictional Yoknapatawpha County based on Oxford, MS"},
    {"title": "Bleak House", "author": "Charles Dickens", "coords": [51.5074, -0.1278], "location": "London, England", "reason": "Primary London setting"},
    {"title": "Brideshead Revisited", "author": "Evelyn Waugh", "coords": [51.754, -1.2545], "location": "Oxford, England", "reason": "Oxford setting, Hertford College"},
    {"title": "Buddenbrooks", "author": "Thomas Mann", "coords": [53.8683, 10.6858], "location": "Lübeck, Germany", "reason": "Set in Lübeck"},
    {"title": "Charlotte's Web", "author": "E.B. White", "coords": [44.3, -68.5], "location": "Rural Maine, USA", "reason": "Written at White's farm in North Brooklin, Maine"},
    {"title": "Demons", "author": "Fyodor Dostoevsky", "coords": [55.7558, 37.6173], "location": "Provincial Russia", "reason": "Russian setting - use Moscow"},
    {"title": "Doctor Faustus", "author": "Thomas Mann", "coords": [52.52, 13.405], "location": "Germany", "reason": "German setting - use Berlin"},
    {"title": "Doctor Zhivago", "author": "Boris Pasternak", "coords": [55.7558, 37.6173], "location": "Russia", "reason": "Primary setting Moscow"},
    {"title": "Gone Girl", "author": "Gillian Flynn", "coords": [38.5767, -92.1735], "location": "Missouri, USA", "reason": "Set in Missouri"},
    {"title": "Heart of Darkness", "author": "Joseph Conrad", "coords": [-4.3224, 15.307], "location": "Congo River, Africa", "reason": "Congo River setting, Kinshasa"},
    {"title": "If This Is a Man", "author": "Primo Levi", "coords": [50.0266, 19.2036], "location": "Auschwitz, Poland", "reason": "Auschwitz concentration camp memoir"},
    {"title": "In Cold Blood", "author": "Truman Capote", "coords": [37.9837, -100.985], "location": "Holcomb, Kansas", "reason": "Set in Holcomb, Kansas"},
    {"title": "King Lear", "author": "William Shakespeare", "coords": [51.5074, -0.1278], "location": "Ancient Britain", "reason": "Written in London - use publication location"},
    {"title": "Lady Chatterley's Lover", "author": "D.H. Lawrence", "coords": [51.5074, -0.1278], "location": "England", "reason": "English setting - use London"},
    {"title": "Life of Pi", "author": "Yann Martel", "coords": [43.65, -79.38], "location": "Pacific Ocean", "reason": "Published in Toronto - use for ocean setting"},
    {"title": "Macbeth", "author": "William Shakespeare", "coords": [57.4778, -4.2247], "location": "Inverness, Scotland", "reason": "Set in Inverness, Scotland"},
    {"title": "Memoirs of Hadrian", "author": "Marguerite Yourcenar", "coords": [41.9028, 12.4964], "location": "Roman Empire", "reason": "Roman Empire - use Rome"},
    {"title": "Midnight's Children", "author": "Salman Rushdie", "coords": [19.0728, 72.8826], "location": "Mumbai, India", "reason": "Set in Bombay/Mumbai"},
    {"title": "Nana", "author": "Émile Zola", "coords": [48.8566, 2.3522], "location": "Paris, France", "reason": "Set in Paris"},
    {"title": "North and South", "author": "Elizabeth Gaskell", "coords": [53.4839, -2.2446], "location": "Manchester, England", "reason": "Fictional Milton is Manchester"},
    {"title": "Oedipus the King", "author": "Sophocles", "coords": [38.3236, 23.0489], "location": "Thebes, Ancient Greece", "reason": "Set in ancient Thebes"},
    {"title": "One Day in the Life of Ivan Denisovich", "author": "Alexander Solzhenitsyn", "coords": [51.7237, 75.3229], "location": "Ekibastuz, Kazakhstan", "reason": "Based on Ekibastuz Gulag camp"},
    {"title": "One Thousand and One Nights", "author": "Anonymous", "coords": [33.3128, 44.3615], "location": "Baghdad, Iraq", "reason": "Primary setting Baghdad"},
    {"title": "Orlando", "author": "Virginia Woolf", "coords": [51.5074, -0.1278], "location": "London, England", "reason": "Primary English setting, London publication"},
    {"title": "Pale Fire", "author": "Vladimir Nabokov", "coords": [40.0, -80.0], "location": "Appalachia, USA", "reason": "Fictional Appalachian town New Wye"},
    {"title": "Poems of Emily Dickinson", "author": "Emily Dickinson", "coords": [42.3754, -72.5193], "location": "Amherst, Massachusetts", "reason": "Dickinson wrote in Amherst"},
    {"title": "Silent Spring", "author": "Rachel Carson", "coords": [42.3546, -71.0535], "location": "Boston, Massachusetts", "reason": "Published in Boston"},
    {"title": "Sons and Lovers", "author": "D.H. Lawrence", "coords": [53.0, -1.15], "location": "Nottinghamshire, England", "reason": "Set in Nottinghamshire mining district"},
    {"title": "The Age of Innocence", "author": "Edith Wharton", "coords": [40.7128, -74.006], "location": "New York City", "reason": "Set in NYC high society"},
    {"title": "The Big Sleep", "author": "Raymond Chandler", "coords": [34.0522, -118.2437], "location": "Los Angeles, USA", "reason": "Set in LA"},
    {"title": "The Castle", "author": "Franz Kafka", "coords": [50.0755, 14.4378], "location": "Prague, Bohemia", "reason": "Kafka's Prague publication"},
    {"title": "The Charterhouse of Parma", "author": "Stendhal", "coords": [44.8015, 10.3280], "location": "Parma, Italy", "reason": "Set in Parma"},
    {"title": "The Complete Tales of Edgar Allan Poe", "author": "Edgar Allan Poe", "coords": [39.2904, -76.6122], "location": "Baltimore, Maryland", "reason": "Poe's primary residence"},
    {"title": "The Count of Monte Cristo", "author": "Alexandre Dumas", "coords": [48.8566, 2.3522], "location": "Paris & Mediterranean", "reason": "Paris publication"},
    {"title": "The Good Soldier", "author": "Ford Madox Ford", "coords": [51.5074, -0.1278], "location": "Europe", "reason": "London publication"},
    {"title": "The Grapes of Wrath", "author": "John Steinbeck", "coords": [36.7783, -119.4179], "location": "California", "reason": "Primary setting California"},
    {"title": "The Heart of the Matter", "author": "Graham Greene", "coords": [8.4657, -13.2317], "location": "Freetown, Sierra Leone", "reason": "Set in Sierra Leone"},
    {"title": "The Maltese Falcon", "author": "Dashiell Hammett", "coords": [37.7749, -122.4194], "location": "San Francisco, USA", "reason": "Set in SF"},
    {"title": "The Name of the Rose", "author": "Umberto Eco", "coords": [45.0, 12.0], "location": "Northern Italy", "reason": "Italian monastery setting"},
    {"title": "The Picture of Dorian Gray", "author": "Oscar Wilde", "coords": [51.5074, -0.1278], "location": "London, England", "reason": "Set in London"},
    {"title": "The Portrait of a Lady", "author": "Henry James", "coords": [51.5074, -0.1278], "location": "England & Italy", "reason": "London publication"},
    {"title": "The Scarlet Letter", "author": "Nathaniel Hawthorne", "coords": [42.3601, -71.0589], "location": "Boston, Massachusetts", "reason": "Set in Boston"},
    {"title": "The Second Sex", "author": "Simone de Beauvoir", "coords": [48.8566, 2.3522], "location": "France", "reason": "Published in Paris"},
    {"title": "The Stories of Anton Chekhov", "author": "Anton Chekhov", "coords": [55.7558, 37.6173], "location": "Russia", "reason": "Russian settings - use Moscow"},
    {"title": "The Sun Also Rises", "author": "Ernest Hemingway", "coords": [48.8566, 2.3522], "location": "Paris & Pamplona", "reason": "Primary Paris setting"},
    {"title": "The Talented Mr. Ripley", "author": "Patricia Highsmith", "coords": [40.8518, 14.2681], "location": "Naples, Italy", "reason": "Set in Italy"},
    {"title": "The Unbearable Lightness of Being", "author": "Milan Kundera", "coords": [50.0755, 14.4378], "location": "Prague, Czech Republic", "reason": "Set in Prague"},
    {"title": "The Waste Land", "author": "T.S. Eliot", "coords": [51.5074, -0.1278], "location": "Europe", "reason": "London publication"},
    {"title": "The Wind in the Willows", "author": "Kenneth Grahame", "coords": [51.5074, -0.1278], "location": "English Countryside", "reason": "London publication"},
    {"title": "The Woman in White", "author": "Wilkie Collins", "coords": [51.5074, -0.1278], "location": "England", "reason": "London publication"},
    {"title": "Tom Jones", "author": "Henry Fielding", "coords": [51.5074, -0.1278], "location": "England", "reason": "London publication"},
    {"title": "Under the Volcano", "author": "Malcolm Lowry", "coords": [18.9261, -99.2319], "location": "Cuernavaca, Mexico", "reason": "Set in Cuernavaca"},
    {"title": "Wide Sargasso Sea", "author": "Jean Rhys", "coords": [18.1096, -77.2975], "location": "Jamaica", "reason": "Set in Jamaica"},
]

for fix in null_fixes:
    fixes.append({
        "title": fix["title"],
        "author": fix["author"],
        "current_coords": [0.0, 0.0],
        "correct_coords": fix["coords"],
        "current_location": "NULL ISLAND (0,0)",
        "correct_location": fix["location"],
        "reason": fix["reason"],
        "source": "https://en.wikipedia.org/wiki/" + fix["title"].replace(" ", "_")
    })

# OTHER MAJOR FIXES
other_fixes = [
    {
        "title": "The Odyssey",
        "author": "Homer",
        "current_coords": [37.9838, 23.7275],
        "correct_coords": [38.453, 20.643],
        "current_location": "Mediterranean Sea",
        "correct_location": "Ithaca, Greece",
        "reason": "Primary setting is Ithaca (Odysseus's homeland)",
        "source": "https://en.wikipedia.org/wiki/Ithaca_(island)"
    },
    {
        "title": "The Mahabharata",
        "author": "Vyasa",
        "current_coords": [28.6139, 77.209],
        "correct_coords": [29.97, 76.88],
        "current_location": "Ancient India",
        "correct_location": "Kurukshetra, India",
        "reason": "Primary setting is Kurukshetra battlefield",
        "source": "https://kurukshetra.gov.in/"
    },
    {
        "title": "Beowulf",
        "author": "Anonymous",
        "current_coords": [52.3555, 1.1743],
        "correct_coords": [55.6761, 12.5683],
        "current_location": "Anglo-Saxon England",
        "correct_location": "Denmark (Copenhagen area)",
        "reason": "Story set in Denmark (Heorot hall), not England where written",
        "source": "https://en.wikipedia.org/wiki/Beowulf"
    },
]

fixes.extend(other_fixes)

# VERIFIED CORRECT
verified_correct = [
    "Paradise Lost",
    "Gulliver's Travels",
    "The Iliad",
    "Nineteen Eighty-Four",
    "Ulysses",
    "The Sound and the Fury",
    "The Book of the Dead",
    "The Canterbury Tales",
    "The Decameron",
    "The Tale of the Heike",
    "The Dream of the Red Chamber",
    "War and Peace",
    "David Copperfield",
    "Oliver Twist",
    "Great Expectations",
    "The Master and Margarita",
]

# Save comprehensive output
output = {
    "fixes": fixes,
    "verified_correct": verified_correct,
    "summary": {
        "total_fixes": len(fixes),
        "total_verified": len(verified_correct),
        "total_processed": len(fixes) + len(verified_correct),
        "high_priority_fixed": 1,
        "null_island_fixed": 56,
        "other_major_fixes": 3,
        "total_books_in_priority": 414,
        "remaining_to_verify": 414 - (len(fixes) + len(verified_correct))
    }
}

with open('coordinate_fixes.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"=== COMPREHENSIVE COORDINATE FIXES ===")
print(f"Total fixes identified: {len(fixes)}")
print(f"  - High priority: 1")
print(f"  - NULL Island (0,0) fixes: 56")
print(f"  - Other major fixes: 3")
print(f"\nVerified correct: {len(verified_correct)}")
print(f"\nTotal processed: {len(fixes) + len(verified_correct)}")
print(f"Remaining: {414 - (len(fixes) + len(verified_correct))}")
print(f"\nSaved to coordinate_fixes.json")
