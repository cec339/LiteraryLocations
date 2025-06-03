import json
import pandas as pd
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
    fictional_keywords = ["fictional", "multiple settings", "various", "heaven", "hell", "paradise", "purgatory", "eden", "atlantis", "utopia", "dystopia", "wonderland", "neverland", "camelot"]
    
    if any(keyword in location_name.lower() for keyword in fictional_keywords):
        # Use publication location for fictional/metaphysical settings
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
        "E.M. Forster": [51.5074, -0.1278],  # London
        "D.H. Lawrence": [53.0000, -1.0000],  # Nottinghamshire
        "Rudyard Kipling": [51.5074, -0.1278],  # London
        "J.M. Barrie": [55.9533, -3.1883],  # Edinburgh
        "Kenneth Grahame": [51.5074, -0.1278],  # London
        "Frances Hodgson Burnett": [40.7128, -74.0060],  # New York (American-British)
        "Bram Stoker": [53.3498, -6.2603],  # Dublin
        
        # American authors
        "Herman Melville": [40.7128, -74.0060],  # New York
        "Nathaniel Hawthorne": [42.3601, -71.0589],  # Boston
        "Edgar Allan Poe": [39.2904, -76.6122],  # Baltimore
        "Mark Twain": [39.1031, -94.5826],  # Missouri
        "Henry James": [40.7128, -74.0060],  # New York
        "Louisa May Alcott": [42.3601, -71.0589],  # Massachusetts
        "Jack London": [37.7749, -122.4194],  # San Francisco
        "L.M. Montgomery": [46.5107, -63.4168],  # Prince Edward Island
        
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
        
        # Italian authors
        "Dante Alighieri": [43.7696, 11.2558],  # Florence
        "Giovanni Boccaccio": [43.7696, 11.2558],  # Florence
        "Italo Calvino": [45.4642, 9.1900],  # Milan
        "Umberto Eco": [45.4642, 9.1900],  # Milan
        
        # Spanish/Latin American authors
        "Miguel de Cervantes": [40.4168, -3.7038],  # Madrid
        "Jorge Luis Borges": [-34.6118, -58.3960],  # Buenos Aires
        "Gabriel García Márquez": [10.3910, -75.4794],  # Cartagena, Colombia
        
        # Other authors
        "Homer": [37.9755, 23.7348],  # Athens (traditional)
        "Virgil": [41.9028, 12.4964],  # Rome
        "Kālidāsa": [20.5937, 78.9629],  # India
        "Murasaki Shikibu": [35.0116, 135.7681],  # Kyoto
        "Cao Xueqin": [39.9042, 116.4074],  # Beijing
        "Vyasa": [28.6139, 77.2090],  # Delhi region
        "Anonymous": [51.5074, -0.1278],  # London as default
        "Various": [51.5074, -0.1278],  # London as default
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

def load_book_data():
    """Load and process book data with improved location logic."""
    try:
        # Load corrected books data first
        corrected_data = {"books": []}
        try:
            with open(Path("data/books_corrected.json"), "r") as f:
                corrected_data = json.load(f)
        except FileNotFoundError:
            print("Corrected books file not found, using original data")
        
        # Load main books data
        main_data = {"books": []}
        try:
            with open(Path("data/books.json"), "r") as f:
                main_data = json.load(f)
        except FileNotFoundError:
            print("Main books file not found")
        
        # Load extended books data (filtered)
        extended_data = {"books": []}
        try:
            with open(Path("attached_assets/books_extended.json"), "r") as f:
                extended_data = json.load(f)
        except FileNotFoundError:
            print("Extended books file not found")
        
        # Combine datasets, prioritizing corrected data
        all_books = []
        
        # Add corrected books first
        for book in corrected_data["books"]:
            if (book.get('title') and book.get('author') and 
                book.get('title') != 'null' and book.get('author') != 'null' and
                book.get('year') is not None):
                all_books.append(book)
        
        # Get titles already added to avoid duplicates
        added_titles = {(book['title'], book['author']) for book in all_books}
        
        # Add from main data if not already present
        for book in main_data["books"]:
            if ((book.get('title'), book.get('author')) not in added_titles and
                book.get('title') and book.get('author') and 
                book.get('title') != 'null' and book.get('author') != 'null' and
                book.get('year') is not None):
                all_books.append(book)
                added_titles.add((book['title'], book['author']))
        
        # Add from extended data if not already present and valid
        for book in extended_data["books"]:
            if ((book.get('title'), book.get('author')) not in added_titles and
                book.get('title') and book.get('author') and 
                book.get('title') != 'null' and book.get('author') != 'null' and
                book.get('year') is not None and book.get('summary') is not None):
                all_books.append(book)
                added_titles.add((book['title'], book['author']))
        
        # Process each book with the improved location logic
        processed_books = []
        for book in all_books:
            # Determine coordinates and location type using the new logic
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
        
        print(f"Loaded {len(df)} books with improved location classification")
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
    """Get statistics about the integrated dataset."""
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