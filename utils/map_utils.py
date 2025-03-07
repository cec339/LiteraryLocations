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

    # Add layer control and fullscreen option with more visible styling
    folium.LayerControl().add_to(m)
    plugins.Fullscreen(
        position="topright",
        title="Expand map",
        title_cancel="Exit fullscreen",
        force_separate_button=True,
        fullscreen_icon=True
    ).add_to(m)
    
    # Add custom CSS to make fullscreen button more visible
    folium.Element("""
    <style>
    .leaflet-control-fullscreen a {
        background-color: #1f77b4 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: 2px solid rgba(0,0,0,0.4) !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.65) !important;
        padding: 6px !important;
        border-radius: 4px !important;
    }
    </style>
    """).add_to(m)

    return m

def add_book_markers(m, books_df):
    """Add book markers to the map."""
    # Create a feature group for book markers
    book_markers = folium.FeatureGroup(name="Book Locations")
    
    # Add larger circle markers as a background layer first
    circle_markers = folium.FeatureGroup(name="Book Highlights")

    # Debug count for successful markers
    successful_markers = 0
    
    # Print debug info to help diagnose issues
    st.write(f"Total books in dataframe: {len(books_df)}")
    st.write("Sample coordinates:")
    if not books_df.empty:
        st.write(books_df[['title', 'latitude', 'longitude']].head())

    for _, book in books_df.iterrows():
        # Skip if coordinates are missing or invalid
        if pd.isna(book['latitude']) or pd.isna(book['longitude']):
            st.warning(f"Missing coordinates for: {book['title']}")
            continue

        # Convert coordinates to float explicitly
        try:
            lat = float(book['latitude'])
            lng = float(book['longitude'])
        except (ValueError, TypeError):
            st.warning(f"Invalid coordinates for {book['title']}: {book['latitude']}, {book['longitude']}")
            continue

        # Create marker popup content with styled HTML
        html = f"""
            <div style='width: 250px; padding: 10px;'>
                <h4 style='color: #1f77b4; margin-bottom: 10px;'>{book['title']}</h4>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Year:</strong> {book['year']}</p>
                <p><strong>Location:</strong> {book['location_name']}</p>
                <div style='margin-top: 10px;'>
                    <p><strong>Summary:</strong><br/>{book['summary'][:150]}...</p>
                </div>
            </div>
        """

        # Add a circle marker for better visibility
        folium.CircleMarker(
            location=[lat, lng],
            radius=12,
            color="#1f77b4",
            fill=True,
            fill_color="#1f77b4",
            fill_opacity=0.7,
            popup=folium.Popup(html, max_width=300),
            tooltip=book['title']
        ).add_to(circle_markers)
        
        # Create marker with Icon
        try:
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(html, max_width=300),
                tooltip=book['title'],
                icon=folium.Icon(
                    color='blue',
                    icon='book',
                    prefix='fa',
                    icon_color='white'
                )
            ).add_to(book_markers)
            successful_markers += 1
        except Exception as e:
            st.warning(f"Could not add marker for {book['title']}: {str(e)}")

    # Add the feature groups to the map
    circle_markers.add_to(m)
    book_markers.add_to(m)

    # Print success or failure message
    if successful_markers == 0:
        st.error("No markers could be added to the map. Please check your data.")
    else:
        st.success(f"Successfully added {successful_markers} book markers to the map")
        
    # Add a note about the markers
    st.info("If markers are not visible, try zooming in or out on the map. Circle markers (blue dots) should be visible at all zoom levels.")

def create_literature_map(books_df):
    """Create the complete literature map with markers."""
    try:
        # Create base map
        m = create_base_map()

        # Add markers
        add_book_markers(m, books_df)

        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None