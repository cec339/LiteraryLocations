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
        
        # Remove duplicates keeping first occurrence
        df = df.drop_duplicates(subset=['title'])

        # Safer extraction with error handling
        def safe_extract_coordinate(location, index):
            try:
                if location and "coordinates" in location and isinstance(location["coordinates"], list):
                    coord = location["coordinates"][index]
                    return float(coord) if coord is not None else None
                return None
            except (IndexError, ValueError, TypeError) as e:
                print(f"Error extracting coordinate: {e}, location: {location}")
                return None

        # Extract setting coordinates and determine location type
        df["setting_latitude"] = df["location"].apply(lambda x: safe_extract_coordinate(x, 0))
        df["setting_longitude"] = df["location"].apply(lambda x: safe_extract_coordinate(x, 1))
        df["setting_name"] = df["location"].apply(lambda x: x.get("name", "Unknown") if x else "Unknown")

        # Determine if setting is fictional or metaphysical
        df["is_fictional"] = df["setting_name"].apply(
            lambda x: any(keyword in str(x) for keyword in 
                ["Various", "Fictional", "Unknown", "Multiple Settings", "Heaven", "Hell", "Paradise", "Purgatory"])
        )

        # For books with fictional/metaphysical settings, use publication location
        df["publication_latitude"] = df.apply(
            lambda row: row["setting_latitude"] if not row["is_fictional"] else None, 
            axis=1
        )
        df["publication_longitude"] = df.apply(
            lambda row: row["setting_longitude"] if not row["is_fictional"] else None,
            axis=1
        )
        df["publication_name"] = df.apply(
            lambda row: row["setting_name"] if not row["is_fictional"] else "Publication Location",
            axis=1
        )

        # Print debugging info
        print("Data types after extraction:")
        print(df[["setting_latitude", "setting_longitude"]].dtypes)

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