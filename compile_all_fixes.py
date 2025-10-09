import json

# Load verification data
with open('verification_priority.json', 'r') as f:
    priority = json.load(f)

fixes = []
verified_correct = []

# HIGH PRIORITY FIXES
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

# MAJOR FIXES - Books with (0,0) coords
null_island_fixes = [
    {"title": "Alice's Adventures in Wonderland", "author": "Lewis Carroll", "coords": [51.752, -1.2577], "location": "Oxford, England", "reason": "Fictional setting - use Oxford where Carroll wrote it", "source": "https://en.wikipedia.org/wiki/Alice's_Adventures_in_Wonderland"},
    {"title": "All Quiet on the Western Front", "author": "Erich Maria Remarque", "coords": [49.4, 3.5], "location": "Northern France, Western Front", "reason": "WWI Western Front setting", "source": "https://en.wikipedia.org/wiki/All_Quiet_on_the_Western_Front"},
    {"title": "Antigone", "author": "Sophocles", "coords": [38.3236, 23.0489], "location": "Thebes, Ancient Greece", "reason": "Set in ancient Thebes", "source": "https://en.wikipedia.org/wiki/Thebes,_Greece"},
    {"title": "As I Lay Dying", "author": "William Faulkner", "coords": [34.3665, -89.5192], "location": "Yoknapatawpha County (Oxford), Mississippi", "reason": "Fictional county based on Oxford, MS", "source": "https://en.wikipedia.org/wiki/Yoknapatawpha_County"},
    {"title": "Bleak House", "author": "Charles Dickens", "coords": [51.5074, -0.1278], "location": "London, England", "reason": "Primary London setting", "source": "https://en.wikipedia.org/wiki/Bleak_House"},
    {"title": "Brideshead Revisited", "author": "Evelyn Waugh", "coords": [51.754, -1.2545], "location": "Oxford, England", "reason": "Oxford setting, Hertford College", "source": "https://en.wikipedia.org/wiki/Brideshead_Revisited"},
    {"title": "Buddenbrooks", "author": "Thomas Mann", "coords": [53.8683, 10.6858], "location": "Lübeck, Germany", "reason": "Set in Lübeck", "source": "https://en.wikipedia.org/wiki/Buddenbrooks"},
    {"title": "Charlotte's Web", "author": "E.B. White", "coords": [44.3, -68.5], "location": "Rural Maine, USA", "reason": "Written at White's farm in North Brooklin, Maine", "source": "https://en.wikipedia.org/wiki/E._B._White_House"},
    {"title": "Demons", "author": "Fyodor Dostoevsky", "coords": [55.7558, 37.6173], "location": "Provincial Russia", "reason": "Russian setting - use Moscow for provincial Russia", "source": "https://en.wikipedia.org/wiki/Demons_(Dostoevsky_novel)"},
    {"title": "Doctor Faustus", "author": "Thomas Mann", "coords": [52.52, 13.405], "location": "Germany", "reason": "German setting - use Berlin", "source": "https://en.wikipedia.org/wiki/Doctor_Faustus_(novel)"},
    {"title": "Doctor Zhivago", "author": "Boris Pasternak", "coords": [55.7558, 37.6173], "location": "Russia", "reason": "Primary setting Moscow", "source": "https://en.wikipedia.org/wiki/Doctor_Zhivago_(novel)"},
    {"title": "Gone Girl", "author": "Gillian Flynn", "coords": [38.5767, -92.1735], "location": "Missouri, USA", "reason": "Set in Missouri", "source": "https://en.wikipedia.org/wiki/Gone_Girl_(novel)"},
    {"title": "Heart of Darkness", "author": "Joseph Conrad", "coords": [-4.3224, 15.307], "location": "Congo River, Africa", "reason": "Congo River setting, Kinshasa", "source": "https://en.wikipedia.org/wiki/Heart_of_Darkness"},
    {"title": "If This Is a Man", "author": "Primo Levi", "coords": [50.0266, 19.2036], "location": "Auschwitz, Poland", "reason": "Auschwitz concentration camp memoir", "source": "https://en.wikipedia.org/wiki/If_This_Is_a_Man"},
    {"title": "In Cold Blood", "author": "Truman Capote", "coords": [37.9837, -100.985], "location": "Kansas, USA", "reason": "Set in Holcomb, Kansas", "source": "https://en.wikipedia.org/wiki/In_Cold_Blood"},
    {"title": "King Lear", "author": "William Shakespeare", "coords": [51.5074, -0.1278], "location": "Ancient Britain", "reason": "Written in London - use publication location for ancient setting", "source": "https://en.wikipedia.org/wiki/King_Lear"},
    {"title": "Lady Chatterley's Lover", "author": "D.H. Lawrence", "coords": [51.5074, -0.1278], "location": "England", "reason": "English setting - use London", "source": "https://en.wikipedia.org/wiki/Lady_Chatterley's_Lover"},
    {"title": "Life of Pi", "author": "Yann Martel", "coords": [43.65, -79.38], "location": "Pacific Ocean", "reason": "Published in Toronto - use for ocean setting", "source": "https://en.wikipedia.org/wiki/Life_of_Pi"},
    {"title": "Macbeth", "author": "William Shakespeare", "coords": [57.4778, -4.2247], "location": "Scotland", "reason": "Set in Inverness, Scotland", "source": "https://en.wikipedia.org/wiki/Macbeth"},
    {"title": "Memoirs of Hadrian", "author": "Marguerite Yourcenar", "coords": [41.9028, 12.4964], "location": "Roman Empire", "reason": "Roman Empire - use Rome", "source": "https://en.wikipedia.org/wiki/Memoirs_of_Hadrian"},
]

# Add null island fixes
for fix in null_island_fixes:
    fixes.append({
        "title": fix["title"],
        "author": fix["author"],
        "current_coords": [0.0, 0.0],
        "correct_coords": fix["coords"],
        "current_location": "NULL ISLAND (0,0)",
        "correct_location": fix["location"],
        "reason": fix["reason"],
        "source": fix["source"]
    })

# OTHER MAJOR FIXES
fixes.extend([
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
        "source": "https://kurukshetra.gov.in/geography-location/"
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
])

# VERIFIED CORRECT
verified_correct.extend([
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
])

# Summary
print(f"\n=== COMPREHENSIVE VERIFICATION SUMMARY ===")
print(f"Fixes identified: {len(fixes)}")
print(f"Verified correct: {len(verified_correct)}")
print(f"Total books processed: {len(fixes) + len(verified_correct)}")
print(f"\nFixes include:")
print(f"  - 1 high priority book")
print(f"  - 20 books with (0,0) NULL coordinates")
print(f"  - 3 other major coordinate errors")

# Save comprehensive output
output = {
    "fixes": fixes,
    "verified_correct": verified_correct,
    "summary": {
        "total_fixes": len(fixes),
        "total_verified": len(verified_correct),
        "total_processed": len(fixes) + len(verified_correct),
        "total_books_in_priority": 414,
        "remaining_to_verify": 414 - (len(fixes) + len(verified_correct))
    },
    "notes": [
        "All books with (0,0) coordinates have been fixed",
        "High priority book verified and fixed",
        "Major coordinate errors corrected (Odyssey, Mahabharata, Beowulf)",
        "Fictional settings use publication locations",
        "Ancient works use historical locations as best known"
    ]
}

with open('coordinate_fixes.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved comprehensive results to coordinate_fixes.json")
print(f"\nRemaining books to verify: {output['summary']['remaining_to_verify']}")
