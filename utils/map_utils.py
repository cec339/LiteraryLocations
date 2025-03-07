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
    
    # Debug count for successful markers
    successful_markers = 0
    
    for _, book in books_df.iterrows():
        # Skip if coordinates are missing or invalid
        if pd.isna(book['latitude']) or pd.isna(book['longitude']):
            continue
        
        # Try to convert coordinates to float explicitly
        try:
            lat = float(book['latitude'])
            lng = float(book['longitude'])
        except (ValueError, TypeError):
            st.warning(f"Invalid coordinates for {book['title']}")
            continue
            
        # Make sure coordinates are within valid range
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            # Try to swap coordinates if they might be reversed
            if (-180 <= lat <= 180) and (-90 <= lng <= 90):
                lat, lng = lng, lat
            else:
                st.warning(f"Coordinates out of range for {book['title']}")
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
        
        # Now create the marker with validated coordinates
        try:
            marker = folium.CircleMarker(
                location=[lat, lng],
                radius=8,
                color='#1f77b4',
                fill=True,
                fill_opacity=0.8,
                weight=2,
                popup=folium.Popup(html, max_width=300),
                tooltip=book['title']
            )
            marker.add_to(book_markers)
            successful_markers += 1
        except Exception as e:
            st.warning(f"Could not add marker for {book['title']}: {str(e)}")
    
    # Add the feature group to the map
    book_markers.add_to(m)
    
    # Log marker count to help with debugging
    st.info(f"Successfully added {successful_markers} book markers to the map")

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
