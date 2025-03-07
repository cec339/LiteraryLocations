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

def create_literature_map(books_df):
    """Create the complete literature map with markers."""
    try:
        m = create_base_map()
        add_book_markers(m, books_df)
        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None
