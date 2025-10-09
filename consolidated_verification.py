import json

# Load data
with open('verification_priority.json', 'r') as f:
    priority = json.load(f)

# Track fixes and verified
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
    "reason": "Non-fiction written at Cambridge University, not London",
    "source": "https://en.wikipedia.org/wiki/The_General_Theory_of_Employment,_Interest_and_Money"
})

# MEDIUM PRIORITY FIXES
fixes.append({
    "title": "The Odyssey",
    "author": "Homer",
    "current_coords": [37.9838, 23.7275],
    "correct_coords": [38.453, 20.643],
    "current_location": "Mediterranean Sea",
    "correct_location": "Ithaca, Greece",
    "reason": "Primary setting is Ithaca (Odysseus's homeland), not Athens/general Mediterranean",
    "source": "https://en.wikipedia.org/wiki/Ithaca_(island)"
})

fixes.append({
    "title": "The Mahabharata",
    "author": "Vyasa",
    "current_coords": [28.6139, 77.209],
    "correct_coords": [29.97, 76.88],
    "current_location": "Ancient India",
    "correct_location": "Kurukshetra, India",
    "reason": "Primary setting is Kurukshetra battlefield, not Delhi",
    "source": "https://kurukshetra.gov.in/geography-location/"
})

fixes.append({
    "title": "Beowulf",
    "author": "Anonymous",
    "current_coords": [52.3555, 1.1743],
    "correct_coords": [55.6761, 12.5683],
    "current_location": "Anglo-Saxon England",
    "correct_location": "Denmark (Lejre/Copenhagen area)",
    "reason": "Story set in Denmark (Heorot hall), not England where it was written",
    "source": "https://en.wikipedia.org/wiki/Beowulf"
})

# VERIFIED CORRECT
verified_correct.extend([
    "Paradise Lost",  # London publication for fictional setting
    "Gulliver's Travels",  # London publication for fictional setting
    "The Iliad",  # Troy coordinates correct
    "Nineteen Eighty-Four",  # London publication for dystopian
    "Ulysses",  # Dublin correct
    "The Sound and the Fury",  # Oxford, MS correct
    "The Book of the Dead",  # Luxor/Thebes coords very close
    "The Canterbury Tales",  # Canterbury correct
    "The Decameron",  # Florence correct
    "The Tale of the Heike",  # Kyoto correct
    "The Dream of the Red Chamber",  # Beijing correct
    "War and Peace",  # Moscow primary setting
])

# Books needing more analysis (for next batch)
needs_review = [
    "The Divine Comedy",  # Florence coords, written in exile at Ravenna
    "Dead Souls",  # Rural Russia - unnamed location
    "Fathers and Sons",  # Rural Russia - based on Orel
    "The Brothers Karamazov",  # Fictional town based on Staraya Russa
    "The Aeneid",  # Mediterranean/Rome
    "Great Expectations",  # Kent and London
    "A Tale of Two Cities",  # London and Paris
    "The Lord of the Rings",  # Fictional, Oxford coords
]

print(f"\n=== VERIFICATION PROGRESS ===")
print(f"Fixes identified: {len(fixes)}")
print(f"Verified correct: {len(verified_correct)}")
print(f"Needs review: {len(needs_review)}")
print(f"Total processed: {len(fixes) + len(verified_correct) + len(needs_review)}")
print(f"Remaining: {414 - (len(fixes) + len(verified_correct) + len(needs_review))}")

print(f"\n=== FIXES ===")
for fix in fixes:
    print(f"  {fix['title']}: {fix['current_location']} → {fix['correct_location']}")

# Save progress
output = {
    "fixes": fixes,
    "verified_correct": verified_correct,
    "needs_review": needs_review,
    "progress": {
        "fixes": len(fixes),
        "verified": len(verified_correct),
        "reviewed": len(fixes) + len(verified_correct) + len(needs_review),
        "total": 414
    }
}

with open('coordinate_fixes.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved to coordinate_fixes.json")
