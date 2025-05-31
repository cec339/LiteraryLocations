import json
import pandas as pd
from pathlib import Path

def load_book_data():
    """Load and process book data from JSON files."""
    try:
        # Load main books data
        with open(Path("data/books.json"), "r") as f:
            main_data = json.load(f)
        
        # Load extended books data
        extended_data = {"books": []}
        try:
            with open(Path("attached_assets/books_extended.json"), "r") as f:
                extended_data = json.load(f)
        except FileNotFoundError:
            print("Extended books file not found, using main data only")
        
        # Combine the datasets
        all_books = main_data["books"] + extended_data["books"]
        data = {"books": all_books}

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data["books"])
        
        # Clean the data - remove entries with null titles or authors
        df = df.dropna(subset=['title', 'author'])
        
        # Clean up malformed entries (where title/author got split incorrectly)
        df = df[df['title'].str.len() > 1]  # Remove single character titles
        df = df[df['author'].str.len() > 1]  # Remove single character authors
        
        # Remove duplicates keeping first occurrence
        df = df.drop_duplicates(subset=['title', 'author'])

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
        df["title"].str.contains(query, case=False, na=False) |
        df["author"].str.contains(query, case=False, na=False)
    ]

def get_dataset_stats():
    """Get statistics about the integrated dataset."""
    df = load_book_data()
    stats = {
        "total_books": len(df),
        "unique_authors": df['author'].nunique(),
        "century_range": (df['century'].min(), df['century'].max()),
        "books_with_coordinates": len(df.dropna(subset=['setting_latitude', 'setting_longitude'])),
        "fictional_settings": len(df[df['is_fictional'] == True]),
        "real_settings": len(df[df['is_fictional'] == False])
    }
    return stats