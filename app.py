
from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from pathlib import Path
import folium
from folium import plugins

app = Flask(__name__)

def load_book_data():
    """Load and process book data from JSON file."""
    try:
        with open(Path("data/books.json"), "r") as f:
            data = json.load(f)
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data["books"])
        
        # Extract coordinates into separate columns
        df["latitude"] = df["location"].apply(lambda x: x["coordinates"][0])
        df["longitude"] = df["location"].apply(lambda x: x["coordinates"][1])
        df["location_name"] = df["location"].apply(lambda x: x["name"])
        
        return df
    except Exception as e:
        raise Exception(f"Error loading book data: {str(e)}")

def get_century_range():
    """Get the range of centuries in the dataset."""
    df = load_book_data()
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

def create_literature_map(books_df):
    """Create the literature map with markers."""
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="CartoDB positron",
        min_zoom=2
    )
    
    for _, book in books_df.iterrows():
        html = f"""
            <div style='width: 100%; max-width: 300px; font-size: 14px;'>
                <h4 style='font-size: 16px; margin: 8px 0;'>{book['title']}</h4>
                <p style='margin: 5px 0;'><strong>Author:</strong> {book['author']}</p>
                <p style='margin: 5px 0;'><strong>Year:</strong> {book['year']}</p>
                <p style='margin: 5px 0;'><strong>Location:</strong> {book['location_name']}</p>
                <div style='margin: 5px 0;'><strong>Summary:</strong> 
                    <div style='font-size: 13px; margin-top: 3px;'>{book['summary']}</div>
                </div>
            </div>
        """
        
        folium.CircleMarker(
            location=[book['latitude'], book['longitude']],
            radius=8,
            color='#1f77b4',
            fill=True,
            popup=folium.Popup(html, max_width=250),
            tooltip=book['title']
        ).add_to(m)
    
    return m

@app.route('/')
def index():
    min_century, max_century = get_century_range()
    century = request.args.get('century', default=min_century, type=int)
    search_query = request.args.get('search', default='', type=str)
    
    if search_query:
        books = search_books(search_query)
    else:
        books = filter_books_by_century(century)
    
    map_html = ""
    if not books.empty:
        m = create_literature_map(books)
        map_html = m._repr_html_()
    
    return render_template('index.html', 
                          map_html=map_html, 
                          books=books.to_dict('records'),
                          min_century=min_century,
                          max_century=max_century,
                          current_century=century,
                          search_query=search_query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
