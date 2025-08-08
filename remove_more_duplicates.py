import json

# Read the current JSON
with open('data/books.json', 'r') as f:
    data = json.load(f)

books = data['books']
print(f"Original count: {len(books)}")

# Track duplicates to remove (keeping first occurrence)
duplicates_to_remove = []

# Find Decameron duplicates
decameron_indices = []
for i, book in enumerate(books):
    if 'decameron' in book['title'].lower() and book['author'] == 'Giovanni Boccaccio':
        decameron_indices.append(i)
if len(decameron_indices) > 1:
    duplicates_to_remove.extend(decameron_indices[1:])
    print(f"Removing duplicate Decameron at indices: {decameron_indices[1:]}")

# Find One Flew Over the Cuckoo's Nest duplicates
cuckoo_indices = []
for i, book in enumerate(books):
    normalized_title = book['title'].lower().replace('\\', '').replace("'", "'")
    if 'one flew over the cuckoo' in normalized_title and book['author'] == 'Ken Kesey':
        cuckoo_indices.append(i)
if len(cuckoo_indices) > 1:
    duplicates_to_remove.extend(cuckoo_indices[1:])
    print(f"Removing duplicate One Flew Over the Cuckoo's Nest at indices: {cuckoo_indices[1:]}")

# Find Harry Potter duplicates
harry_indices = []
for i, book in enumerate(books):
    normalized_title = book['title'].lower().replace('\\', '')
    if 'harry potter' in normalized_title and 'philosopher' in normalized_title:
        harry_indices.append(i)
if len(harry_indices) > 1:
    duplicates_to_remove.extend(harry_indices[1:])
    print(f"Removing duplicate Harry Potter at indices: {harry_indices[1:]}")

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