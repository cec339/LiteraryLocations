
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
        
        # Convert coordinates to float explicitly
        try:
            lat = float(book['latitude'])
            lng = float(book['longitude'])
        except (ValueError, TypeError):
            st.warning(f"Invalid coordinates for {book['title']}")
            continue
        
        # Create marker popup content
        html = f"""
            <div style='width: 250px'>
                <h4>{book['title']}</h4>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Year:</strong> {book['year']}</p>
                <p><strong>Location:</strong> {book['location_name']}</p>
                <p><strong>Summary:</strong> {book['summary'][:100]}...</p>
            </div>
        """
        
        # Create marker with Icon for better visibility
        try:
            # Use a more visible marker type
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(html, max_width=300),
                tooltip=book['title'],
                icon=folium.Icon(color='blue', icon='book', prefix='fa')
            ).add_to(book_markers)
            successful_markers += 1
        except Exception as e:
            st.warning(f"Could not add marker for {book['title']}: {str(e)}")
    
    # Add the feature group to the map
    book_markers.add_to(m)
    
    if successful_markers == 0:
        st.error("No markers could be added to the map. Please check your data.")
    else:
        st.success(f"Successfully added {successful_markers} book markers to the map")

def create_literature_map(books_df):
    """Create the complete literature map with markers."""
    try:
        # Create base map
        m = create_base_map()
        
        # Add markers
        add_book_markers(m, books_df)
        
        # Add fullscreen control
        plugins.Fullscreen(
            position="topright",
            title="Expand map",
            title_cancel="Exit fullscreen",
            force_separate_button=True
        ).add_to(m)
        
        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None
