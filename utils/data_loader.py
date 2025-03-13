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

        # Extract coordinates into separate columns and ensure they're float type
        df["latitude"] = df["location"].apply(lambda x: float(x["coordinates"][0]))
        df["longitude"] = df["location"].apply(lambda x: float(x["coordinates"][1]))
        df["location_name"] = df["location"].apply(lambda x: x["name"])

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