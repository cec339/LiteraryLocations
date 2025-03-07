import folium
from folium import plugins
import streamlit as st
import pandas as pd

def create_base_map():
    """Create the base world map."""
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="CartoDB positron",
        min_zoom=2
    )
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def add_book_markers(m, books_df):
    """Add book markers to the map."""
    # Create a feature group for book markers
    book_markers = folium.FeatureGroup(name="Book Locations")
    
    for _, book in books_df.iterrows():
        # Skip if coordinates are missing or invalid
        if pd.isna(book['latitude']) or pd.isna(book['longitude']):
            continue
            
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
        
        # Some coordinates might be reversed in the data, let's handle both cases
        try:
            folium.CircleMarker(
                location=[float(book['latitude']), float(book['longitude'])],
                radius=8,
                color='#1f77b4',
                fill=True,
                fill_opacity=0.8,
                weight=2,
                popup=folium.Popup(html, max_width=300),
                tooltip=book['title']
            ).add_to(book_markers)
        except Exception as e:
            # Try with reversed coordinates as a fallback
            try:
                folium.CircleMarker(
                    location=[float(book['longitude']), float(book['latitude'])],
                    radius=8,
                    color='#1f77b4',
                    fill=True,
                    fill_opacity=0.8,
                    weight=2,
                    popup=folium.Popup(html, max_width=300),
                    tooltip=book['title']
                ).add_to(book_markers)
            except:
                # If both attempts fail, log but don't crash
                st.warning(f"Could not add marker for {book['title']}")
    
    # Add the feature group to the map
    book_markers.add_to(m)

def create_literature_map(books_df):
    """Create the complete literature map with markers."""
    try:
        m = create_base_map()
        
        # Add book markers
        add_book_markers(m, books_df)
        
        # Add fullscreen control AFTER adding markers
        folium.plugins.Fullscreen(
            position="topright",
            title="Expand map",
            title_cancel="Exit fullscreen",
            force_separate_button=True
        ).add_to(m)
        
        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None
        return None
