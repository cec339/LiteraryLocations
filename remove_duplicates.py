import json

# Read the current JSON
with open('data/books.json', 'r') as f:
    data = json.load(f)

books = data['books']
print(f"Original count: {len(books)}")

# Track duplicates to remove (keeping first occurrence)
duplicates_to_remove = []

# Check for Gulliver's Travels duplicates
gulliver_indices = [i for i, book in enumerate(books) if book['title'] == "Gulliver's Travels"]
if len(gulliver_indices) > 1:
    duplicates_to_remove.extend(gulliver_indices[1:])
    print(f"Removing duplicate Gulliver's Travels at indices: {gulliver_indices[1:]}")

# Check for A Wrinkle in Time duplicates (case-insensitive)
wrinkle_indices = [i for i, book in enumerate(books) if book['title'].lower() == "a wrinkle in time"]
if len(wrinkle_indices) > 1:
    duplicates_to_remove.extend(wrinkle_indices[1:])
    print(f"Removing duplicate A Wrinkle in Time at indices: {wrinkle_indices[1:]}")

# Check for Epic of Gilgamesh duplicates (case-insensitive)
gilgamesh_indices = [i for i, book in enumerate(books) if book['title'].lower() == "the epic of gilgamesh"]
if len(gilgamesh_indices) > 1:
    duplicates_to_remove.extend(gilgamesh_indices[1:])
    print(f"Removing duplicate Epic of Gilgamesh at indices: {gilgamesh_indices[1:]}")

# Remove duplicates (in reverse order to maintain indices)
for idx in sorted(set(duplicates_to_remove), reverse=True):
    removed_book = books.pop(idx)
    print(f"Removed: {removed_book['title']} by {removed_book['author']}")

print(f"New count: {len(books)}")

# Save the cleaned JSON
data['books'] = books
with open('data/books.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Successfully removed duplicates and saved the file.")