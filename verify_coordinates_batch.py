import json

# Load verification priority data
with open('verification_priority.json', 'r') as f:
    priority_data = json.load(f)

# Initialize tracking
fixes = []
verified_correct = []

# Track the first fix: The General Theory of Employment, Interest and Money
fixes.append({
    "title": "The General Theory of Employment, Interest and Money",
    "author": "John Maynard Keynes",
    "current_coords": [51.5074, -0.1278],
    "correct_coords": [52.2053, 0.1192],
    "current_location": "Money, United Kingdom",
    "correct_location": "Cambridge, England",
    "reason": "Book was written at Cambridge University, not London. Non-fiction work should use author's location.",
    "source": "https://en.wikipedia.org/wiki/The_General_Theory_of_Employment,_Interest_and_Money"
})

print(f"High priority book processed: 1/1")
print(f"Medium priority books to process: {len(priority_data['medium_priority'])}")
print(f"\nCurrent fixes tracked: {len(fixes)}")
print(f"Verified correct: {len(verified_correct)}")

# Save progress
output = {
    "fixes": fixes,
    "verified_correct": verified_correct,
    "progress": {
        "high_priority_complete": 1,
        "medium_priority_complete": 0,
        "total_processed": 1,
        "total_books": 414
    }
}

with open('coordinate_fixes.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nSaved progress to coordinate_fixes.json")
