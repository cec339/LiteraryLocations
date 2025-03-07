import json
import pandas as pd
from pathlib import Path

def load_book_data():
    """Load and process book data from JSON file."""
    try:
        file_path = Path("data/books.json")
        if not file_path.exists():
            raise FileNotFoundError(f"Book data file not found at {file_path}")
            
        with open(file_path, "r") as f:
            data = json.load(f)
        
        if not data or "books" not in data or not data["books"]:
            raise ValueError("Book data is empty or has incorrect format")
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data["books"])
        
        # Check if location column exists
        if "location" not in df.columns:
            raise ValueError("Book data missing 'location' field")
            
        # Extract coordinates into separate columns with validation
        df["latitude"] = df["location"].apply(lambda x: x.get("coordinates", [0, 0])[0] if isinstance(x, dict) and "coordinates" in x else 0)
        df["longitude"] = df["location"].apply(lambda x: x.get("coordinates", [0, 0])[1] if isinstance(x, dict) and "coordinates" in x else 0)
        df["location_name"] = df["location"].apply(lambda x: x.get("name", "Unknown") if isinstance(x, dict) else "Unknown")
        
        return df
    except Exception as e:
        print(f"Error loading book data: {str(e)}")
        # Return empty DataFrame instead of raising exception
        return pd.DataFrame(columns=["title", "author", "year", "century", "location", "summary", "historical_context", "latitude", "longitude", "location_name"])

def get_century_range():
    """Get the range of centuries in the dataset."""
    df = load_book_data()
    if df.empty or "century" not in df.columns:
        return None, None
    return df["century"].min(), df["century"].max()

def filter_books_by_century(century):
    """Filter books by century."""
    df = load_book_data()
    return df[df["century"] == century]

def search_books(query):
    """Search books by title or author."""
    df = load_book_data()
    return df[
        df["title"].str.contains(query, case=False) |
        df["author"].str.contains(query, case=False)
    ]
