
import json
import re

def find_generic_historical_context():
    """Find books with generic 'Published in X, reflecting...' historical context."""
    
    with open('data/books.json', 'r') as f:
        data = json.load(f)
    
    # Pattern to match the generic historical context
    generic_pattern = r"Published in -?\d+, reflecting the literary movements of the -?\d+th century\."
    
    generic_books = []
    total_books = len(data['books'])
    
    for book in data['books']:
        historical_context = book.get('historical_context', '')
        if re.match(generic_pattern, historical_context):
            generic_books.append({
                'title': book.get('title', ''),
                'author': book.get('author', ''),
                'year': book.get('year', ''),
                'historical_context': historical_context
            })
    
    print(f"Found {len(generic_books)} books with generic historical context out of {total_books} total books")
    print(f"That's {len(generic_books)/total_books*100:.1f}% of the dataset\n")
    
    print("Books with generic historical context:")
    print("=" * 80)
    
    for i, book in enumerate(generic_books, 1):
        print(f"{i}. \"{book['title']}\" by {book['author']} ({book['year']})")
        print(f"   Context: {book['historical_context']}")
        print()
    
    return generic_books

if __name__ == "__main__":
    generic_books = find_generic_historical_context()
