import folium
from folium import plugins
import streamlit as st

def create_base_map():
    """Create the base world map."""
    return folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="CartoDB positron",
        min_zoom=2
    )

def add_book_markers(m, books_df):
    """Add book markers to the map."""
    for _, book in books_df.iterrows():
        html = f"""
            <div style='width: 250px'>
                <h4>{book['title']}</h4>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Year:</strong> {book['year']}</p>
                <p><strong>Location:</strong> {book['location_name']}</p>
                <p><strong>Summary:</strong> {book['summary']}</p>
                <p><strong>Historical Context:</strong> {book['historical_context']}</p>
            </div>
        """
        
        folium.CircleMarker(
            location=[book['latitude'], book['longitude']],
            radius=8,
            color='#1f77b4',
            fill=True,
            popup=folium.Popup(html, max_width=300),
            tooltip=book['title']
        ).add_to(m)

def create_literature_map(books_df):
    """Create the complete literature map with markers."""
    try:
        m = create_base_map()
        add_book_markers(m, books_df)
        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None
