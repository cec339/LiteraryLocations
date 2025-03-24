import json
import pandas as pd
from pathlib import Path

def load_book_data():
    """Load and process book data from JSON file."""
    try:
        with open(Path("data/books.json"), "r") as f:
            data = json.load(f)

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data["books"])

        # Safer extraction with error handling
        def safe_extract_coordinate(location, index):
            try:
                if location and "coordinates" in location and isinstance(location["coordinates"], list):
                    coord = location["coordinates"][index]
                    return float(coord) if coord is not None else 0.0
                return 0.0
            except (IndexError, ValueError, TypeError) as e:
                print(f"Error extracting coordinate: {e}, location: {location}")
                return 0.0
                
        # Extract coordinates with safer function
        df["latitude"] = df["location"].apply(lambda x: safe_extract_coordinate(x, 0))
        df["longitude"] = df["location"].apply(lambda x: safe_extract_coordinate(x, 1))
        df["location_name"] = df["location"].apply(lambda x: x.get("name", "Unknown") if x else "Unknown")

        # Keep original location for settings
        df["publication_location"] = df["location"]  # Store full location object
        
        # Print debugging info
        print("Data types after extraction:")
        print(df[["latitude", "longitude"]].dtypes)

        return df
    except Exception as e:
        raise Exception(f"Error loading book data: {str(e)}")

def get_century_range():
    """Get the range of centuries in the dataset."""
    df = load_book_data()
    return df["century"].min(), df["century"].max()

def filter_books_by_century(century):
    """Filter books by century"""
    books_df = load_book_data()
    # Ensure century is treated as an integer for comparison
    return books_df[books_df['century'] == int(century)]

def search_books(query):
    """Search books by title or author."""
    df = load_book_data()
    return df[
        df["title"].str.contains(query, case=False) |
        df["author"].str.contains(query, case=False)
    ]