
import json

def find_kansas_coordinate_books():
    """Find books with generic Kansas coordinates (39.8283, -98.5795)"""
    
    with open('data/books.json', 'r') as f:
        data = json.load(f)
    
    kansas_coords = [39.8283, -98.5795]
    kansas_books = []
    
    for i, book in enumerate(data['books']):
        coords = book['location']['coordinates']
        if (abs(coords[0] - kansas_coords[0]) < 0.001 and 
            abs(coords[1] - kansas_coords[1]) < 0.001):
            kansas_books.append({
                'index': i,
                'title': book['title'],
                'author': book['author'],
                'location_name': book['location']['name'],
                'coordinates': coords
            })
    
    return kansas_books

# Find the problematic books
kansas_books = find_kansas_coordinate_books()
print(f"Found {len(kansas_books)} books with generic Kansas coordinates:")
print()

for book in kansas_books:
    print(f"Index {book['index']}: {book['title']} by {book['author']}")
    print(f"  Location: {book['location_name']}")
    print(f"  Coordinates: {book['coordinates']}")
    print()
