import json

# Load data
with open('verification_priority.json', 'r') as f:
    priority = json.load(f)

# Track fixes and verified
fixes = []
verified_correct = []

# HIGH PRIORITY - FIXES
fixes.append({
    "title": "The General Theory of Employment, Interest and Money",
    "author": "John Maynard Keynes",
    "current_coords": [51.5074, -0.1278],
    "correct_coords": [52.2053, 0.1192],
    "current_location": "Money, United Kingdom",
    "correct_location": "Cambridge, England",
    "reason": "Non-fiction economics book written at Cambridge University, not London. Should use author's writing location.",
    "source": "https://en.wikipedia.org/wiki/The_General_Theory_of_Employment,_Interest_and_Money"
})

# MEDIUM PRIORITY - FIXES
fixes.append({
    "title": "The Odyssey",
    "author": "Homer",
    "current_coords": [37.9838, 23.7275],
    "correct_coords": [38.453, 20.643],
    "current_location": "Mediterranean Sea",
    "correct_location": "Ithaca, Greece",
    "reason": "Primary setting is Ithaca, Odysseus's homeland, not Athens. Current coordinates point to Athens area.",
    "source": "https://en.wikipedia.org/wiki/Ithaca_(island)"
})

# VERIFIED CORRECT
verified_correct.extend([
    "Paradise Lost",  # London publication location for fictional setting
    "Gulliver's Travels",  # London publication location for fictional setting
    "The Iliad",  # Troy coordinates are correct (39.9571, 26.2387)
    "Nineteen Eighty-Four",  # London publication for dystopian setting
    "Ulysses",  # Dublin coordinates correct
    "The Sound and the Fury",  # Oxford, MS coordinates close enough (34.3668, -89.5186)
])

# The Divine Comedy - needs verification of Florence coordinates
# The Aeneid - Rome coords seem appropriate for destination
# A Tale of Two Cities - Paris coords (both cities equal, but Paris is where climax happens)
# Great Expectations - London coords (both Kent and London, but London dominant)
# The Lord of the Rings - Oxford coords (written there, fictional setting)

print(f"Fixes identified: {len(fixes)}")
print(f"Verified correct: {len(verified_correct)}")
print(f"\nFixes:")
for fix in fixes:
    print(f"  - {fix['title']}: {fix['current_location']} -> {fix['correct_location']}")

# Save progress
output = {
    "fixes": fixes,
    "verified_correct": verified_correct,
    "progress": {
        "books_processed": len(fixes) + len(verified_correct),
        "total_books": 414
    }
}

with open('coordinate_fixes.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved to coordinate_fixes.json")
