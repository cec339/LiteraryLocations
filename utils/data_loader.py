import json
import pandas as pd
from pathlib import Path

def determine_location_type_and_coordinates(book):
    """
    Determine location type and coordinates based on improved logic:
    1. Primary setting -> RED marker (actual story location)
    2. Publication location for fictional/metaphysical -> BLUE marker 
    3. Publication location for real settings -> GREEN marker
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
    fictional_keywords = ["fictional", "multiple settings", "various", "heaven", "hell", "paradise", "purgatory", "eden", "atlantis", "utopia", "dystopia"]
    
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
        "Daniel Defoe": [51.5074, -0.1278],  # London
        "Henry Fielding": [51.5074, -0.1278],  # London
        "Laurence Sterne": [54.0000, -1.5400],  # Yorkshire
        "Samuel Richardson": [51.5074, -0.1278],  # London
        "Tobias Smollett": [55.9533, -3.1883],  # Edinburgh
        "Walter Scott": [55.9533, -3.1883],  # Edinburgh
        "Lord Byron": [51.5074, -0.1278],  # London
        "Percy Shelley": [51.5074, -0.1278],  # London
        "Mary Shelley": [51.5074, -0.1278],  # London
        "John Keats": [51.5074, -0.1278],  # London
        "William Wordsworth": [54.4609, -3.0886],  # Lake District
        "Samuel Coleridge": [51.5074, -0.1278],  # London
        "Robert Burns": [55.9533, -3.1883],  # Edinburgh
        "Arthur Conan Doyle": [55.9533, -3.1883],  # Edinburgh
        "Robert Louis Stevenson": [55.9533, -3.1883],  # Edinburgh
        "H.G. Wells": [51.5074, -0.1278],  # London
        "Joseph Conrad": [51.5074, -0.1278],  # London
        "E.M. Forster": [51.5074, -0.1278],  # London
        "D.H. Lawrence": [53.0000, -1.0000],  # Nottinghamshire
        "Aldous Huxley": [51.5074, -0.1278],  # London
        "George Orwell": [51.5074, -0.1278],  # London
        "Graham Greene": [51.5074, -0.1278],  # London
        "Evelyn Waugh": [51.5074, -0.1278],  # London
        "Somerset Maugham": [51.5074, -0.1278],  # London
        
        # American authors
        "Herman Melville": [40.7128, -74.0060],  # New York
        "Nathaniel Hawthorne": [42.3601, -71.0589],  # Boston
        "Edgar Allan Poe": [39.2904, -76.6122],  # Baltimore
        "Mark Twain": [39.1031, -94.5826],  # Missouri
        "Henry James": [40.7128, -74.0060],  # New York
        "Edith Wharton": [40.7128, -74.0060],  # New York
        "Theodore Dreiser": [41.8781, -87.6298],  # Chicago
        "Sinclair Lewis": [44.9537, -93.0900],  # Minnesota
        "F. Scott Fitzgerald": [44.9537, -93.0900],  # Minnesota
        "Ernest Hemingway": [41.8781, -87.6298],  # Chicago
        "William Faulkner": [34.3015, -89.5010],  # Mississippi
        "John Steinbeck": [36.6002, -121.8947],  # California
        "J.D. Salinger": [40.7128, -74.0060],  # New York
        "Harper Lee": [32.3668, -86.3000],  # Alabama
        "Toni Morrison": [39.9612, -82.9988],  # Ohio
        "Saul Bellow": [41.8781, -87.6298],  # Chicago
        "Philip Roth": [40.0583, -74.4057],  # New Jersey
        "Cormac McCarthy": [35.6870, -105.9378],  # New Mexico
        "Don DeLillo": [40.7128, -74.0060],  # New York
        "Thomas Pynchon": [40.7128, -74.0060],  # New York
        "Kurt Vonnegut": [39.7684, -86.1581],  # Indiana
        "Ray Bradbury": [34.0522, -118.2437],  # California
        "Ursula K. Le Guin": [45.5152, -122.6784],  # Oregon
        "Flannery O'Connor": [32.1656, -82.9001],  # Georgia
        "Willa Cather": [40.8136, -96.7026],  # Nebraska
        "Jack Kerouac": [42.3601, -71.0589],  # Massachusetts
        "Ralph Ellison": [35.4676, -97.5164],  # Oklahoma
        "Zora Neale Hurston": [28.5383, -81.3792],  # Florida
        "Langston Hughes": [39.0458, -94.5795],  # Missouri
        
        # French authors
        "Gustave Flaubert": [48.8566, 2.3522],  # Paris
        "Victor Hugo": [48.8566, 2.3522],  # Paris
        "Marcel Proust": [48.8566, 2.3522],  # Paris
        "Honoré de Balzac": [48.8566, 2.3522],  # Paris
        "Émile Zola": [48.8566, 2.3522],  # Paris
        "Stendhal": [48.8566, 2.3522],  # Paris
        "George Sand": [48.8566, 2.3522],  # Paris
        "Alexandre Dumas": [48.8566, 2.3522],  # Paris
        "Jules Verne": [48.8566, 2.3522],  # Paris
        "André Gide": [48.8566, 2.3522],  # Paris
        "Jean-Paul Sartre": [48.8566, 2.3522],  # Paris
        "Simone de Beauvoir": [48.8566, 2.3522],  # Paris
        "Albert Camus": [48.8566, 2.3522],  # Paris
        "Marguerite Duras": [48.8566, 2.3522],  # Paris
        "Marguerite Yourcenar": [48.8566, 2.3522],  # Paris
        "Voltaire": [48.8566, 2.3522],  # Paris
        "Denis Diderot": [48.8566, 2.3522],  # Paris
        "Jean-Jacques Rousseau": [46.2044, 6.1432],  # Geneva
        "Molière": [48.8566, 2.3522],  # Paris
        "Pierre Corneille": [49.4431, 1.0993],  # Rouen
        "Jean Racine": [48.8566, 2.3522],  # Paris
        
        # German authors
        "Johann Wolfgang von Goethe": [50.1109, 8.6821],  # Frankfurt
        "Friedrich Schiller": [48.7758, 9.1829],  # Stuttgart
        "Heinrich Heine": [51.2277, 6.7735],  # Düsseldorf
        "Thomas Mann": [48.1351, 11.5820],  # Munich
        "Hermann Hesse": [48.7758, 9.1829],  # Stuttgart
        "Franz Kafka": [50.0755, 14.4378],  # Prague
        "Rainer Maria Rilke": [50.0755, 14.4378],  # Prague
        "Günter Grass": [53.5511, 9.9937],  # Hamburg
        "Heinrich Böll": [50.9375, 6.9603],  # Cologne
        "Christa Wolf": [52.5200, 13.4050],  # Berlin
        "Bertolt Brecht": [48.3705, 10.8978],  # Augsburg
        "Robert Musil": [48.2082, 16.3738],  # Vienna
        "Arthur Schnitzler": [48.2082, 16.3738],  # Vienna
        "Stefan Zweig": [48.2082, 16.3738],  # Vienna
        
        # Russian authors
        "Leo Tolstoy": [55.7558, 37.6173],  # Moscow
        "Fyodor Dostoevsky": [59.9311, 30.3609],  # St. Petersburg
        "Anton Chekhov": [55.7558, 37.6173],  # Moscow
        "Ivan Turgenev": [55.7558, 37.6173],  # Moscow
        "Nikolai Gogol": [55.7558, 37.6173],  # Moscow
        "Alexander Pushkin": [59.9311, 30.3609],  # St. Petersburg
        "Mikhail Lermontov": [55.7558, 37.6173],  # Moscow
        "Ivan Goncharov": [59.9311, 30.3609],  # St. Petersburg
        "Maxim Gorky": [56.3287, 44.0020],  # Nizhny Novgorod
        "Boris Pasternak": [55.7558, 37.6173],  # Moscow
        "Alexander Solzhenitsyn": [55.7558, 37.6173],  # Moscow
        "Vladimir Nabokov": [59.9311, 30.3609],  # St. Petersburg
        "Mikhail Bulgakov": [55.7558, 37.6173],  # Moscow
        "Anna Akhmatova": [59.9311, 30.3609],  # St. Petersburg
        "Osip Mandelstam": [59.9311, 30.3609],  # St. Petersburg
        "Marina Tsvetaeva": [55.7558, 37.6173],  # Moscow
        
        # Spanish/Latin American authors
        "Miguel de Cervantes": [40.4168, -3.7038],  # Madrid
        "Federico García Lorca": [37.1773, -3.5986],  # Granada
        "Jorge Luis Borges": [-34.6118, -58.3960],  # Buenos Aires
        "Gabriel García Márquez": [10.3910, -75.4794],  # Cartagena, Colombia
        "Mario Vargas Llosa": [-12.0464, -77.0428],  # Lima, Peru
        "Julio Cortázar": [-34.6118, -58.3960],  # Buenos Aires
        "Octavio Paz": [19.4326, -99.1332],  # Mexico City
        "Carlos Fuentes": [19.4326, -99.1332],  # Mexico City
        "Juan Rulfo": [19.4326, -99.1332],  # Mexico City
        "Isabel Allende": [-33.4489, -70.6693],  # Santiago, Chile
        "Pablo Neruda": [-33.4489, -70.6693],  # Santiago, Chile
        "Gabriela Mistral": [-33.4489, -70.6693],  # Santiago, Chile
        "Rubén Darío": [12.1328, -86.2504],  # Managua, Nicaragua
        
        # Italian authors
        "Dante Alighieri": [43.7696, 11.2558],  # Florence
        "Giovanni Boccaccio": [43.7696, 11.2558],  # Florence
        "Niccolò Machiavelli": [43.7696, 11.2558],  # Florence
        "Italo Calvino": [45.4642, 9.1900],  # Milan
        "Umberto Eco": [45.4642, 9.1900],  # Milan
        "Giuseppe Tomasi di Lampedusa": [38.1157, 13.3613],  # Palermo, Sicily
        "Alberto Moravia": [41.9028, 12.4964],  # Rome
        "Primo Levi": [45.0703, 7.6869],  # Turin
        "Cesare Pavese": [45.0703, 7.6869],  # Turin
        "Luigi Pirandello": [37.3000, 13.5833],  # Sicily
        "Carlo Levi": [45.0703, 7.6869],  # Turin
        
        # Japanese authors
        "Murasaki Shikibu": [35.0116, 135.7681],  # Kyoto
        "Sei Shōnagon": [35.0116, 135.7681],  # Kyoto
        "Matsuo Bashō": [35.6762, 139.6503],  # Tokyo
        "Natsume Sōseki": [35.6762, 139.6503],  # Tokyo
        "Yukio Mishima": [35.6762, 139.6503],  # Tokyo
        "Yasunari Kawabata": [35.6762, 139.6503],  # Tokyo
        "Kenzaburō Ōe": [35.6762, 139.6503],  # Tokyo
        "Haruki Murakami": [35.6762, 139.6503],  # Tokyo
        "Junichiro Tanizaki": [34.6937, 135.5023],  # Osaka
        "Akutagawa Ryūnosuke": [35.6762, 139.6503],  # Tokyo
        "Kawabata Yasunari": [35.6762, 139.6503],  # Tokyo
        "Mishima Yukio": [35.6762, 139.6503],  # Tokyo
        
        # Other notable authors
        "Chinua Achebe": [6.5244, 3.3792],  # Lagos, Nigeria
        "Wole Soyinka": [6.5244, 3.3792],  # Lagos, Nigeria
        "Salman Rushdie": [19.0760, 72.8777],  # Mumbai, India
        "R.K. Narayan": [12.9716, 77.5946],  # Bangalore, India
        "Rabindranath Tagore": [22.5726, 88.3639],  # Kolkata, India
        "Mo Yan": [39.9042, 116.4074],  # Beijing, China
        "Lu Xun": [39.9042, 116.4074],  # Beijing, China
        "Lao She": [39.9042, 116.4074],  # Beijing, China
        "Cao Xueqin": [39.9042, 116.4074],  # Beijing, China
        "Milan Kundera": [50.0755, 14.4378],  # Prague
        "Václav Havel": [50.0755, 14.4378],  # Prague
        "Czesław Miłosz": [52.2297, 21.0122],  # Warsaw
        "Wisława Szymborska": [50.0647, 19.9450],  # Krakow
        "Isak Dinesen": [55.6761, 12.5683],  # Copenhagen
        "August Strindberg": [59.3293, 18.0686],  # Stockholm
        "Selma Lagerlöf": [59.3293, 18.0686],  # Stockholm
        "Knut Hamsun": [59.9139, 10.7522],  # Oslo
        "Henrik Ibsen": [59.9139, 10.7522],  # Oslo
        "Fernando Pessoa": [38.7223, -9.1393],  # Lisbon
        "José Saramago": [38.7223, -9.1393],  # Lisbon
        "Machado de Assis": [-22.9068, -43.1729],  # Rio de Janeiro
        "Clarice Lispector": [-22.9068, -43.1729],  # Rio de Janeiro
        "Jorge Amado": [-12.9714, -38.5014],  # Salvador, Brazil
        "Margaret Atwood": [43.6532, -79.3832],  # Toronto, Canada
        "Alice Munro": [43.6532, -79.3832],  # Toronto, Canada
        "Mordecai Richler": [45.5017, -73.5673],  # Montreal, Canada
        "Patrick White": [-33.8688, 151.2093],  # Sydney, Australia
        "Christina Stead": [-33.8688, 151.2093],  # Sydney, Australia
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
    """Load and process book data from JSON files with improved location logic."""
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
        
        # Combine the datasets and filter out null entries
        all_books = []
        for book in main_data["books"] + extended_data["books"]:
            if (book.get('title') and book.get('author') and 
                book.get('title') != 'null' and book.get('author') != 'null' and
                book.get('year') is not None):
                all_books.append(book)
        
        data = {"books": all_books}
        
        # Get coordinate mapping for missing locations
        coord_mapping = get_coordinate_mapping()

        # Process each book with the improved location logic
        processed_books = []
        for book in data["books"]:
            # Determine coordinates and location type using the new logic
            coordinates, location_type = determine_location_type_and_coordinates(book)
            
            # Create processed book entry
            processed_book = {
                'title': book.get('title', ''),
                'author': book.get('author', ''),
                'year': book.get('year', 0),
                'century': book.get('century', 0),
                'setting_latitude': coordinates[0],
                'setting_longitude': coordinates[1],
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
        
        print(f"Data types after extraction:")
        print(df[['setting_latitude', 'setting_longitude']].dtypes)
        
        return df

    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def legacy_coordinate_extraction():
    """Legacy function for coordinate extraction - kept for reference."""
    try:
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
            setting_name = str(row.get('setting_name', '')).lower()
            
            # English/British authors and locations
            if any(name in author for name in ['shakespeare', 'dickens', 'austen', 'bronte', 'wilde', 'carroll', 'woolf', 'orwell', 'tolkien', 'conrad', 'defoe', 'swift', 'milton']):
                return 51.5074, -0.1278  # London
            
            # American authors
            if any(name in author for name in ['twain', 'hemingway', 'faulkner', 'steinbeck', 'fitzgerald', 'salinger', 'morrison', 'melville', 'hawthorne', 'poe', 'whitman', 'cather', 'o\'connor', 'mccarthy']):
                return 40.7128, -74.0060  # New York
            
            # Russian authors
            if any(name in author for name in ['tolstoy', 'dostoevsky', 'chekhov', 'gogol', 'pushkin', 'turgenev', 'bulgakov']):
                return 55.7558, 37.6173  # Moscow
            
            # French authors
            if any(name in author for name in ['hugo', 'dumas', 'flaubert', 'proust', 'camus', 'sartre', 'balzac', 'stendhal', 'voltaire']):
                return 48.8566, 2.3522  # Paris
            
            # German authors
            if any(name in author for name in ['goethe', 'mann', 'kafka', 'hesse', 'grass', 'hoffmann', 'musil']):
                return 52.5200, 13.4050  # Berlin
            
            # Italian authors
            if any(name in author for name in ['dante', 'boccaccio', 'calvino', 'eco', 'lampedusa']):
                return 41.9028, 12.4964  # Rome
            
            # Spanish/Latin American authors
            if any(name in author for name in ['cervantes', 'garcía márquez', 'borges', 'rulfo', 'allende', 'márquez', 'garcia']):
                if 'márquez' in author or 'garcia' in author:
                    return 10.4806, -73.2531  # Colombia
                return 40.4168, -3.7038  # Madrid
            
            # Japanese authors
            if any(name in author for name in ['kawabata', 'mishima', 'murakami', 'tanizaki', 'soseki']):
                return 35.6762, 139.6503  # Tokyo
            
            # Chinese authors
            if any(name in author for name in ['cao', 'xueqin', 'lu xun', 'mo yan']):
                return 39.9042, 116.4074  # Beijing
            
            # Indian authors
            if any(name in author for name in ['kālidāsa', 'vyasa', 'tagore', 'rushdie']):
                return 28.6139, 77.2090  # Delhi
            
            # Irish authors
            if any(name in author for name in ['joyce', 'wilde', 'yeats', 'beckett']):
                return 53.3498, -6.2603  # Dublin
            
            # Portuguese/Brazilian authors
            if any(name in author for name in ['pessoa', 'saramago', 'machado']):
                return 38.7223, -9.1393  # Lisbon
            
            # Norwegian/Scandinavian authors
            if any(name in author for name in ['ibsen', 'hamsun', 'knausgård']):
                return 59.9139, 10.7522  # Oslo
            
            # Czech authors
            if any(name in author for name in ['kafka', 'kundera', 'havel']):
                return 50.0755, 14.4378  # Prague
            
            # Austrian authors
            if any(name in author for name in ['musil', 'zweig']):
                return 48.2082, 16.3738  # Vienna
            
            # Ancient/Classical works
            if any(name in author for name in ['homer', 'sophocles', 'euripides', 'aristophanes']):
                return 37.9755, 23.7348  # Athens
            
            if any(name in author for name in ['virgil', 'ovid', 'apuleius']):
                return 41.9028, 12.4964  # Rome
            
            # Anonymous works by region/culture
            if 'anonymous' in author:
                if any(term in title for term in ['arabian', 'nights', 'thousand']):
                    return 33.3152, 44.3661  # Baghdad
                elif any(term in title for term in ['sundiata', 'mali']):
                    return 12.6392, -8.0029  # Mali
                elif any(term in title for term in ['dede', 'korkut', 'turkish']):
                    return 39.7753, 64.4232  # Central Asia
                elif any(term in title for term in ['job', 'hebrew']):
                    return 31.7683, 35.2137  # Jerusalem
                elif any(term in title for term in ['dead', 'egypt']):
                    return 25.6872, 32.6396  # Egypt
                elif any(term in title for term in ['heike', 'japan']):
                    return 35.0116, 135.7681  # Kyoto
            
            # Title-based mapping for famous works
            if 'arabian nights' in title or 'thousand and one nights' in title:
                return 33.3152, 44.3661  # Baghdad
            
            if 'bible' in title or 'torah' in title:
                return 31.7683, 35.2137  # Jerusalem
            
            if 'gilgamesh' in title:
                return 31.3236, 45.6367  # Ancient Mesopotamia
            
            if 'mahabharata' in title or 'ramayana' in title:
                return 28.6139, 77.2090  # Delhi
            
            # Setting-based mapping
            if setting_name and setting_name != 'unknown':
                if 'london' in setting_name:
                    return 51.5074, -0.1278
                elif 'paris' in setting_name:
                    return 48.8566, 2.3522
                elif 'new york' in setting_name:
                    return 40.7128, -74.0060
                elif 'dublin' in setting_name:
                    return 53.3498, -6.2603
                elif 'moscow' in setting_name:
                    return 55.7558, 37.6173
                elif 'rome' in setting_name:
                    return 41.9028, 12.4964
                elif 'berlin' in setting_name:
                    return 52.5200, 13.4050
                elif 'madrid' in setting_name:
                    return 40.4168, -3.7038
                elif 'vienna' in setting_name:
                    return 48.2082, 16.3738
                elif 'tokyo' in setting_name:
                    return 35.6762, 139.6503
                elif 'beijing' in setting_name:
                    return 39.9042, 116.4074
            
            # Default to a central location for unmapped books
            return 48.8566, 2.3522  # Paris as default
        
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