import json
import pandas as pd
from pathlib import Path

def get_coordinate_mapping():
    """Return mapping of locations to coordinates for books missing them."""
    return {
        # Major cities and regions commonly referenced in literature
        "Ancient Greece": [37.9755, 23.7348],
        "Ancient Rome": [41.9028, 12.4964],
        "Ancient Egypt": [26.8206, 30.8025],
        "Ancient Mesopotamia": [33.0955, 44.0996],
        "Ancient India": [20.5937, 78.9629],
        "Ancient China": [35.8617, 104.1954],
        "Medieval Europe": [50.1109, 8.6821],
        "Renaissance Italy": [43.7696, 11.2558],
        "Victorian England": [51.5074, -0.1278],
        "19th Century Russia": [55.7558, 37.6173],
        "19th Century France": [48.8566, 2.3522],
        "19th Century Germany": [52.5200, 13.4050],
        "Colonial America": [39.7392, -75.1419],
        "American South": [33.7490, -84.3880],
        "American West": [39.7392, -104.9903],
        "Modern Japan": [35.6762, 139.6503],
        "Soviet Union": [55.7558, 37.6173],
        "Ireland": [53.1424, -7.6921],
        "Scotland": [56.4907, -4.2026],
        "Wales": [52.1307, -3.7837],
        "Scandinavia": [60.1282, 18.6435],
        "Spain": [40.4637, -3.7492],
        "Portugal": [39.3999, -8.2245],
        "Poland": [51.9194, 19.1451],
        "Czech Republic": [49.8175, 15.4730],
        "Hungary": [47.1625, 19.5033],
        "Austria": [47.5162, 14.5501],
        "Switzerland": [46.8182, 8.2275],
        "Netherlands": [52.1326, 5.2913],
        "Belgium": [50.5039, 4.4699],
        "Turkey": [38.9637, 35.2433],
        "Middle East": [29.2985, 42.5510],
        "North Africa": [26.3351, 17.2283],
        "Sub-Saharan Africa": [1.6508, 18.6094],
        "South America": [-8.7832, -55.4915],
        "Argentina": [-38.4161, -63.6167],
        "Brazil": [-14.2350, -51.9253],
        "Mexico": [23.6345, -102.5528],
        "Canada": [56.1304, -106.3468],
        "Australia": [-25.2744, 133.7751],
        "New Zealand": [-40.9006, 174.8860],
        "India": [20.5937, 78.9629],
        "China": [35.8617, 104.1954],
        "Korea": [35.9078, 127.7669],
        "Southeast Asia": [4.2105, 101.9758],
        "Central Asia": [48.0196, 66.9237],
        "Eastern Europe": [52.2297, 21.0122],
        "Balkans": [44.0165, 21.0059],
        "Nordic Countries": [64.9631, 19.0208],
        "Caribbean": [21.4691, -78.6569],
        "Pacific Islands": [-8.7832, 125.7275],
        "Arctic": [66.5039, -153.7705]
    }

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
        
        # Get coordinate mapping for missing locations
        coord_mapping = get_coordinate_mapping()

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data["books"])
        
        # Clean the data - remove entries with null titles or authors
        df = df.dropna(subset=['title', 'author'])
        
        # Clean up malformed entries (where title/author got split incorrectly)
        df = df[df['title'].str.len() > 1]  # Remove single character titles
        df = df[df['author'].str.len() > 1]  # Remove single character authors
        
        # Remove duplicates keeping first occurrence
        df = df.drop_duplicates(subset=['title', 'author'])

        # Enhanced coordinate extraction with intelligent mapping
        def safe_extract_coordinate(location, index):
            try:
                if location and "coordinates" in location and isinstance(location["coordinates"], list):
                    coord = location["coordinates"][index]
                    if coord is not None and coord != 0.0:  # Avoid null and zero coordinates
                        return float(coord)
                return None
            except (IndexError, ValueError, TypeError) as e:
                print(f"Error extracting coordinate: {e}, location: {location}")
                return None

        def get_mapped_coordinates(location_name, lat, lon):
            """Get coordinates from mapping if current ones are missing or invalid."""
            if lat is not None and lon is not None and lat != 0.0 and lon != 0.0:
                return lat, lon
            
            if not location_name or location_name == "Unknown":
                return None, None
            
            # Try exact match first
            if location_name in coord_mapping:
                return coord_mapping[location_name]
            
            # Try partial matching for common patterns
            location_lower = location_name.lower()
            for key, coords in coord_mapping.items():
                if any(word in location_lower for word in key.lower().split()):
                    return coords
            
            # Special handling for common location patterns
            if "london" in location_lower:
                return [51.5074, -0.1278]
            elif "paris" in location_lower:
                return [48.8566, 2.3522]
            elif "new york" in location_lower:
                return [40.7128, -74.0060]
            elif "rome" in location_lower:
                return [41.9028, 12.4964]
            elif "athens" in location_lower:
                return [37.9755, 23.7348]
            elif "moscow" in location_lower:
                return [55.7558, 37.6173]
            elif "dublin" in location_lower:
                return [53.3498, -6.2603]
            elif "berlin" in location_lower:
                return [52.5200, 13.4050]
            elif "madrid" in location_lower:
                return [40.4168, -3.7038]
            elif "vienna" in location_lower:
                return [48.2082, 16.3738]
            elif "prague" in location_lower:
                return [50.0755, 14.4378]
            elif "amsterdam" in location_lower:
                return [52.3676, 4.9041]
            elif "florence" in location_lower:
                return [43.7696, 11.2558]
            elif "venice" in location_lower:
                return [45.4408, 12.3155]
            elif "saint petersburg" in location_lower or "st petersburg" in location_lower:
                return [59.9311, 30.3609]
            elif "constantinople" in location_lower or "istanbul" in location_lower:
                return [41.0082, 28.9784]
            elif "jerusalem" in location_lower:
                return [31.7683, 35.2137]
            elif "cairo" in location_lower:
                return [30.0444, 31.2357]
            elif "tokyo" in location_lower:
                return [35.6762, 139.6503]
            elif "beijing" in location_lower or "peking" in location_lower:
                return [39.9042, 116.4074]
            elif "mumbai" in location_lower or "bombay" in location_lower:
                return [19.0760, 72.8777]
            elif "calcutta" in location_lower or "kolkata" in location_lower:
                return [22.5726, 88.3639]
            
            return None, None

        # Extract setting coordinates and determine location type
        df["setting_latitude"] = df["location"].apply(lambda x: safe_extract_coordinate(x, 0))
        df["setting_longitude"] = df["location"].apply(lambda x: safe_extract_coordinate(x, 1))
        df["setting_name"] = df["location"].apply(lambda x: x.get("name", "Unknown") if x else "Unknown")
        
        # Apply coordinate mapping for missing coordinates
        coord_results = df.apply(lambda row: get_mapped_coordinates(
            row["setting_name"], 
            row["setting_latitude"], 
            row["setting_longitude"]
        ), axis=1)
        
        # Update coordinates with mapped values
        for i, (lat, lon) in enumerate(coord_results):
            if lat is not None and lon is not None:
                df.iloc[i, df.columns.get_loc("setting_latitude")] = lat
                df.iloc[i, df.columns.get_loc("setting_longitude")] = lon

        # Enhanced coordinate mapping for more books
        def enhance_coordinates(row):
            """Enhanced coordinate assignment based on various book attributes."""
            if pd.notna(row['setting_latitude']) and pd.notna(row['setting_longitude']):
                return row['setting_latitude'], row['setting_longitude']
            
            # Map based on author nationality or common book settings
            title = str(row['title']).lower()
            author = str(row['author']).lower()
            
            # English/British authors
            if any(name in author for name in ['shakespeare', 'dickens', 'austen', 'bronte', 'wilde', 'carroll', 'woolf', 'orwell', 'tolkien']):
                return 51.5074, -0.1278  # London
            
            # American authors
            if any(name in author for name in ['twain', 'hemingway', 'faulkner', 'steinbeck', 'fitzgerald', 'salinger', 'morrison']):
                return 40.7128, -74.0060  # New York
            
            # Russian authors
            if any(name in author for name in ['tolstoy', 'dostoevsky', 'chekhov', 'gogol', 'pushkin', 'turgenev']):
                return 55.7558, 37.6173  # Moscow
            
            # French authors
            if any(name in author for name in ['hugo', 'dumas', 'flaubert', 'proust', 'camus', 'sartre']):
                return 48.8566, 2.3522  # Paris
            
            # German authors
            if any(name in author for name in ['goethe', 'mann', 'kafka', 'hesse', 'grass']):
                return 52.5200, 13.4050  # Berlin
            
            # Italian authors
            if any(name in author for name in ['dante', 'boccaccio', 'calvino', 'eco']):
                return 41.9028, 12.4964  # Rome
            
            # Spanish/Latin American authors
            if any(name in author for name in ['cervantes', 'garcía márquez', 'borges', 'rulfo', 'allende']):
                if 'márquez' in author or 'garcia' in author:
                    return 10.4806, -73.2531  # Colombia
                return 40.4168, -3.7038  # Madrid
            
            # Japanese authors
            if any(name in author for name in ['kawabata', 'mishima', 'murakami', 'tanizaki', 'soseki']):
                return 35.6762, 139.6503  # Tokyo
            
            # Ancient/Classical works
            if any(name in author for name in ['homer', 'sophocles', 'euripides', 'aristophanes']):
                return 37.9755, 23.7348  # Athens
            
            if any(name in author for name in ['virgil', 'ovid', 'apuleius']):
                return 41.9028, 12.4964  # Rome
            
            # Title-based mapping for famous works
            if 'arabian nights' in title or 'thousand and one nights' in title:
                return 33.3152, 44.3661  # Baghdad
            
            if 'bible' in title or 'torah' in title:
                return 31.7683, 35.2137  # Jerusalem
            
            if 'gilgamesh' in title:
                return 31.3236, 45.6367  # Ancient Mesopotamia
            
            if 'mahabharata' in title or 'ramayana' in title:
                return 28.6139, 77.2090  # Delhi
            
            # Default to a neutral location if nothing else matches
            return None, None
        
        # Apply enhanced coordinate mapping
        enhanced_coords = df.apply(enhance_coordinates, axis=1)
        for i, (lat, lon) in enumerate(enhanced_coords):
            if lat is not None and lon is not None and (pd.isna(df.iloc[i]['setting_latitude']) or pd.isna(df.iloc[i]['setting_longitude'])):
                df.iloc[i, df.columns.get_loc("setting_latitude")] = lat
                df.iloc[i, df.columns.get_loc("setting_longitude")] = lon

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