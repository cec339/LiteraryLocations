import folium
from folium.plugins import MarkerCluster
import streamlit as st
import pandas as pd

def _ordinal(n):
    """Return ordinal string for an integer (1 -> '1st', -5 -> '5th BCE')."""
    a = abs(n)
    if 11 <= (a % 100) <= 13:
        suffix = "th"
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(a % 10, 4)]
    era = " BCE" if n < 0 else ""
    return f"{a}{suffix}{era}"

def create_base_map():
    """Create the base world map."""
    return folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="CartoDB positron",
        min_zoom=2
    )

def create_base_map_html():
    """Create base map HTML with MarkerCluster JS/CSS dependencies loaded but no markers.
    Returns the raw inner HTML (not wrapped in iframe srcdoc)."""
    m = folium.Map(
        location=[20, 0],
        zoom_start=3,
        tiles='CartoDB positron',
        world_copy_jump=True
    )
    # Add an empty MarkerCluster so Folium includes the JS/CSS deps
    MarkerCluster().add_to(m)
    # get_root().render() gives us the raw HTML document, not the iframe-wrapped version
    html = m.get_root().render()
    # Move zoom controls to top-right so timeline doesn't cover them
    html = html.replace('</head>', '<style>.leaflet-top.leaflet-left{left:auto!important;right:10px!important;}</style></head>')
    return html

def get_marker_icon(location_type):
    """Get the appropriate marker icon based on location type."""
    icon_colors = {
        'primary': 'red',      # Primary story setting - real geographic location
        'publication': 'blue', # Publication location for fictional/metaphysical/multiple settings
        'fictional': 'green'   # Fictional setting, showing publication location
    }
    return folium.Icon(
        icon='book',
        prefix='fa',
        color=icon_colors.get(location_type, 'gray')
    )

def create_literature_map(books_df):
    """
    Create an interactive map showing literary locations with improved classification

    Args:
        books_df: DataFrame containing book data with latitude, longitude, and location_type
    """
    try:
        # Make sure coordinates are float type
        books_df['setting_latitude'] = books_df['setting_latitude'].astype(float)
        books_df['setting_longitude'] = books_df['setting_longitude'].astype(float)

        # Create base map centered on average coordinates
        avg_lat = books_df['setting_latitude'].mean()
        avg_lon = books_df['setting_longitude'].mean()

        literary_map = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=5,
            tiles='CartoDB positron',
            world_copy_jump=True
        )

        # Add marker cluster
        marker_cluster = MarkerCluster().add_to(literary_map)

        # Add markers for each book
        for _, book in books_df.iterrows():
            # Use the improved location classification
            location_type = book.get('location_type', 'primary')
            coordinates = [book['setting_latitude'], book['setting_longitude']]
            location_name = book['setting_name']

            # Create location description based on type
            if location_type == 'primary':
                location_desc = "Primary Story Setting"
            elif location_type == 'publication':
                location_desc = "Publication Location (Fictional/Multiple Settings)"
            else:
                location_desc = "Story Location"

            popup_html = f"""
                <div style='width: 280px; font-family: Arial, sans-serif;'>
                    <h4 style='margin-bottom: 10px; color: #2E4057;'>{book['title']}</h4>
                    <p><b>Author:</b> {book['author']}</p>
                    <p><b>Year:</b> {abs(book['year'])} {"BCE" if book['year'] < 0 else ""}</p>
                    <p><b>Century:</b> {_ordinal(book.get('century', 0))}</p>
                    <p><b>Location:</b> {location_name}</p>
                    <p><b>Type:</b> {location_desc}</p>
                    <p><b>Summary:</b> {book['summary'][:300]}{'...' if len(book['summary']) > 300 else ''}</p>
                    <p><b>Historical Context:</b> {book['historical_context'][:300]}{'...' if len(book['historical_context']) > 300 else ''}</p>
                </div>
            """

            # Add marker with appropriate icon
            folium.Marker(
                location=coordinates,
                popup=folium.Popup(popup_html, max_width=320),
                icon=get_marker_icon(location_type)
            ).add_to(marker_cluster)

        return literary_map
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None