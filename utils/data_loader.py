import pandas as pd
import json
from pathlib import Path

def load_book_data():
    """Load book data from JSON file."""
    try:
        # Check if the data directory and file exist
        file_path = Path("data/books.json")
        if not file_path.exists():
            print("Warning: books.json file not found")
            return pd.DataFrame(columns=["title", "author", "year", "century", "location_name", "latitude", "longitude", "summary", "historical_context"])

        # Load the JSON data
        with open(file_path, "r") as f:
            data = json.load(f)

        # Create DataFrame from the books list
        if "books" not in data or not data["books"]:
            print("Warning: No books found in JSON file")
            return pd.DataFrame(columns=["title", "author", "year", "century", "location_name", "latitude", "longitude", "summary", "historical_context"])

        # Process books data
        books = []
        for book in data["books"]:
            # Extract location coordinates
            latitude = book["location"]["coordinates"][0] if "location" in book and "coordinates" in book["location"] else None
            longitude = book["location"]["coordinates"][1] if "location" in book and "coordinates" in book["location"] else None
            location_name = book["location"]["name"] if "location" in book and "name" in book["location"] else None

            # Create a book entry with flattened structure
            books.append({
                "title": book.get("title", ""),
                "author": book.get("author", ""),
                "year": book.get("year", 0),
                "century": book.get("century", 0),
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "summary": book.get("summary", ""),
                "historical_context": book.get("historical_context", "")
            })

        return pd.DataFrame(books)

    except Exception as e:
        print(f"Error loading book data: {str(e)}")
        return pd.DataFrame(columns=["title", "author", "year", "century", "location_name", "latitude", "longitude", "summary", "historical_context"])

def get_century_range():
    """Get the range of centuries in the dataset."""
    df = load_book_data()
    if df.empty or "century" not in df.columns:
        return None, None
    return df["century"].min(), df["century"].max()

def filter_books_by_century(century):
    """
    Filter books by century.
    If no books exist for the selected century, include books from adjacent centuries.
    """
    df = load_book_data()
    filtered = df[df["century"] == century]
    
    # If no books in this century, try to get books from adjacent centuries
    if filtered.empty:
        # First try ±1 century
        adjacent = df[(df["century"] == century - 1) | (df["century"] == century + 1)]
        if not adjacent.empty:
            return adjacent.sort_values("year")
        
        # If still empty, get all books and sort by century proximity
        all_books = df.copy()
        all_books['century_distance'] = abs(all_books['century'] - century)
        return all_books.sort_values('century_distance').head(3)
    
    return filtered

def search_books(query):
    """Search books by title or author."""
    df = load_book_data()
    if df.empty:
        return df
    return df[
        df["title"].str.contains(query, case=False) |
        df["author"].str.contains(query, case=False)
    ]