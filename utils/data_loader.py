import json
import re
import pandas as pd
import streamlit as st
from pathlib import Path

def determine_location_type_and_coordinates(book):
    """
    Determine location type and coordinates based on improved logic:
    1. Primary setting -> RED marker (actual story location)
    2. Publication location for fictional/metaphysical -> BLUE marker
    """

    title = book.get('title', '')
    author = book.get('author', '')
    year = book.get('year', 0)
    location_name = book.get('location', {}).get('name', '')
    coordinates = book.get('location', {}).get('coordinates', [None, None])

    # Handle null/missing location data
    if not location_name or location_name == "null" or (coordinates and (coordinates[0] is None or coordinates[1] is None)):
        coords, loc_type = get_publication_coordinates(author, year)
        return coords, "publication"

    # Classify location types based on content
    # Use word-boundary matching to avoid false positives (e.g. "eden" in "Sweden")
    fictional_keywords = ["fictional", "multiple settings", "various", "heaven", "hell", "paradise", "purgatory", "eden", "atlantis", "utopia", "dystopia", "wonderland", "neverland", "camelot"]

    loc_lower = location_name.lower()
    if any(re.search(r'\b' + re.escape(keyword) + r'\b', loc_lower) for keyword in fictional_keywords):
        # Use publication location for fictional/metaphysical settings
        pub_coords, _ = get_publication_coordinates(author, year)
        return pub_coords, "publication"

    # Check for invalid coordinates (0,0 or near 0,0 which places books in the ocean off Africa)
    if (coordinates and coordinates[0] is not None and coordinates[1] is not None and
        (abs(coordinates[0]) < 0.1 and abs(coordinates[1]) < 0.1)):
        # These are likely invalid coordinates, use publication location instead
        pub_coords, _ = get_publication_coordinates(author, year)
        return pub_coords, "publication"

    # If valid coordinates exist and location seems real, use primary setting
    if coordinates and coordinates[0] is not None and coordinates[1] is not None:
        return coordinates, "primary"

    # Fallback to publication location
    pub_coords, _ = get_publication_coordinates(author, year)
    return pub_coords, "publication"

def get_publication_coordinates(author, year):
    """Get publication coordinates based on author and time period."""

    # Author nationality/publication location mapping
    author_locations = {
        # British/Irish authors
        "Emily Brontë": [53.8008, -1.5491],  # West Yorkshire
        "Charlotte Brontë": [53.8008, -1.5491],
        "Anne Brontë": [53.8008, -1.5491],
        "Jane Austen": [50.9097, -1.4044],  # Hampshire
        "Charles Dickens": [51.5074, -0.1278],  # London
        "George Eliot": [52.4797, -1.8951],  # Warwickshire
        "Thomas Hardy": [50.7156, -2.4389],  # Dorset
        "Oscar Wilde": [53.3498, -6.2603],  # Dublin
        "James Joyce": [53.3498, -6.2603],  # Dublin
        "Virginia Woolf": [51.5074, -0.1278],  # London
        "John Milton": [51.5074, -0.1278],  # London
        "Geoffrey Chaucer": [51.5074, -0.1278],  # London
        "William Shakespeare": [52.1919, -1.7082],  # Stratford-upon-Avon
        "Jonathan Swift": [53.3498, -6.2603],  # Dublin
        "Lewis Carroll": [51.7520, -1.2577],  # Oxford
        "Arthur Conan Doyle": [55.9533, -3.1883],  # Edinburgh
        "Robert Louis Stevenson": [55.9533, -3.1883],  # Edinburgh
        "H.G. Wells": [51.5074, -0.1278],  # London
        "Joseph Conrad": [51.5074, -0.1278],  # London

        # American authors
        "Herman Melville": [40.7128, -74.0060],  # New York
        "Nathaniel Hawthorne": [42.3601, -71.0589],  # Boston
        "Edgar Allan Poe": [39.2904, -76.6122],  # Baltimore
        "Mark Twain": [39.1031, -94.5826],  # Missouri
        "Henry James": [40.7128, -74.0060],  # New York
        "Louisa May Alcott": [42.3601, -71.0589],  # Massachusetts
        "Jack London": [37.7749, -122.4194],  # San Francisco
        "F. Scott Fitzgerald": [44.9778, -93.2650],  # Minnesota
        "Ernest Hemingway": [41.8781, -87.6298],  # Chicago
        "William Faulkner": [34.3015, -89.5010],  # Mississippi
        "John Steinbeck": [36.6777, -121.6555],  # California
        "J.D. Salinger": [40.7128, -74.0060],  # New York
        "Harper Lee": [32.3668, -86.3000],  # Alabama
        "Toni Morrison": [39.9612, -82.9988],  # Ohio

        # French authors
        "Gustave Flaubert": [48.8566, 2.3522],  # Paris
        "Victor Hugo": [48.8566, 2.3522],  # Paris
        "Marcel Proust": [48.8566, 2.3522],  # Paris
        "Alexandre Dumas": [48.8566, 2.3522],  # Paris
        "Jules Verne": [48.8566, 2.3522],  # Paris
        "Albert Camus": [48.8566, 2.3522],  # Paris

        # German authors
        "Johann Wolfgang von Goethe": [50.1109, 8.6821],  # Frankfurt
        "Thomas Mann": [48.1351, 11.5820],  # Munich
        "Hermann Hesse": [48.7758, 9.1829],  # Stuttgart
        "Franz Kafka": [50.0755, 14.4378],  # Prague

        # Russian authors
        "Leo Tolstoy": [55.7558, 37.6173],  # Moscow
        "Fyodor Dostoevsky": [59.9311, 30.3609],  # St. Petersburg
        "Anton Chekhov": [55.7558, 37.6173],  # Moscow
        "Ivan Turgenev": [55.7558, 37.6173],  # Moscow
        "Nikolai Gogol": [55.7558, 37.6173],  # Moscow
        "Alexander Pushkin": [59.9311, 30.3609],  # St. Petersburg
        "Mikhail Bulgakov": [55.7558, 37.6173],  # Moscow

        # Italian authors
        "Dante Alighieri": [43.7696, 11.2558],  # Florence
        "Giovanni Boccaccio": [43.7696, 11.2558],  # Florence
        "Italo Calvino": [45.4642, 9.1900],  # Milan
        "Umberto Eco": [45.4642, 9.1900],  # Milan
        "Giuseppe Tomasi di Lampedusa": [37.5994, 14.0154],  # Sicily

        # Spanish/Latin American authors
        "Miguel de Cervantes": [40.4168, -3.7038],  # Madrid
        "Jorge Luis Borges": [-34.6118, -58.3960],  # Buenos Aires
        "Gabriel García Márquez": [10.3910, -75.4794],  # Cartagena, Colombia
        "Juan Rulfo": [19.3193, -103.7555],  # Mexico

        # Japanese authors
        "Murasaki Shikibu": [35.0116, 135.7681],  # Kyoto
        "Yasunari Kawabata": [35.6762, 139.6503],  # Tokyo
        "Junichiro Tanizaki": [34.6937, 135.5023],  # Osaka
        "Haruki Murakami": [35.6762, 139.6503],  # Tokyo

        # Chinese authors
        "Cao Xueqin": [39.9042, 116.4074],  # Beijing

        # Indian authors
        "Kālidāsa": [20.5937, 78.9629],  # India
        "Vyasa": [28.6139, 77.2090],  # Delhi region

        # Other authors
        "Homer": [37.9755, 23.7348],  # Athens (traditional)
        "Virgil": [41.9028, 12.4964],  # Rome
        "Anonymous": [51.5074, -0.1278],  # London as default
        "Various": [51.5074, -0.1278],  # London as default
        "Various Authors": [51.5074, -0.1278],  # London as default
        "J.R.R. Tolkien": [51.7520, -1.2577],  # Oxford
        "Vladimir Nabokov": [40.7128, -74.0060],  # New York (American period)
        "George Orwell": [51.5074, -0.1278],  # London
        "Chinua Achebe": [6.5244, 3.3792],  # Nigeria
        "Ferdowsi": [35.6892, 51.389],  # Iran
        "Fernando Pessoa": [38.7223, -9.1393],  # Lisbon
        "Cormac McCarthy": [31.7619, -106.485],  # Southwest US
        "Tayeb Salih": [15.5007, 32.5599],  # Sudan
        "Doris Lessing": [51.5074, -0.1278],  # London
        "Willa Cather": [40.8136, -96.7026],  # Nebraska
        "Flannery O'Connor": [32.1656, -82.9001],  # Georgia
        "W.G. Sebald": [48.1351, 11.5820],  # Munich
        "Nguyễn Du": [21.0285, 105.8542],  # Vietnam
        "Robert Musil": [48.2082, 16.3738],  # Vienna
        "Laurence Sterne": [54.0, -1.54],  # Yorkshire
        "Günter Grass": [54.352, 18.6466],  # Gdansk region
    }

    if author in author_locations:
        return author_locations[author], "publication"

    # Default fallback based on time period
    if year and year < 1400:
        return [41.9028, 12.4964], "publication"  # Rome for ancient/medieval
    elif year and year < 1800:
        return [51.5074, -0.1278], "publication"  # London for early modern
    else:
        return [40.7128, -74.0060], "publication"  # New York for modern

@st.cache_data
def load_book_data():
    """Load and process book data from single JSON file."""
    try:
        # Load books data from consolidated file
        with open(Path("data/books.json"), "r", encoding="utf-8") as f:
            data = json.load(f)

        # Process each book with the improved location logic
        processed_books = []
        for book in data["books"]:
            # Skip books with missing essential data
            if not (book.get('title') and book.get('author') and 
                   book.get('title') != 'null' and book.get('author') != 'null' and
                   book.get('year') is not None):
                continue

            # Determine coordinates and location type using the logic
            coordinates, location_type = determine_location_type_and_coordinates(book)

            # Create processed book entry
            processed_book = {
                'title': book.get('title', ''),
                'author': book.get('author', ''),
                'year': int(book.get('year', 0)),
                'century': int(book.get('century', 0)),
                'setting_latitude': float(coordinates[0]),
                'setting_longitude': float(coordinates[1]),
                'setting_name': book.get('location', {}).get('name', '') or 'Publication Location',
                'location_type': location_type,
                'summary': book.get('summary', 'Summary not available'),
                'historical_context': book.get('historical_context', 'Historical context not available')
            }
            processed_books.append(processed_book)

        # Convert to DataFrame
        df = pd.DataFrame(processed_books)

        # Remove duplicates and clean data
        df = df.drop_duplicates(subset=['title', 'author'], keep='first')
        df = df[df['title'].astype(str).str.len() > 0]
        df = df[df['author'].astype(str).str.len() > 0]

        print(f"Loaded {len(df)} books from consolidated JSON file")
        print(f"Primary settings: {len(df[df['location_type'] == 'primary'])}")
        print(f"Publication locations: {len(df[df['location_type'] == 'publication'])}")

        return df

    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def get_century_range():
    """Get the range of centuries in the dataset."""
    df = load_book_data()
    if df.empty:
        return []
    return sorted(df['century'].unique())

def filter_books_by_century(century):
    """Filter books by century"""
    df = load_book_data()
    if df.empty:
        return df
    return df[df['century'] == century]

def search_books(query):
    """Search books by title or author."""
    df = load_book_data()
    if df.empty or not query:
        return df

    query_lower = query.lower()
    mask = (df['title'].str.lower().str.contains(query_lower, na=False) | 
            df['author'].str.lower().str.contains(query_lower, na=False))
    return df[mask]

def get_dataset_stats():
    """Get statistics about the dataset."""
    df = load_book_data()
    if df.empty:
        return {}

    return {
        "total_books": len(df),
        "unique_authors": df['author'].nunique(),
        "century_range": f"{df['century'].min()}th to {df['century'].max()}th century",
        "locations_with_coordinates": len(df.dropna(subset=['setting_latitude', 'setting_longitude'])),
        "primary_settings": len(df[df['location_type'] == 'primary']),
        "publication_locations": len(df[df['location_type'] == 'publication'])
    }