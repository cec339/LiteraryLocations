import folium
from folium.plugins import MarkerCluster
import streamlit as st
import pandas as pd

def create_base_map():
    """Create the base world map."""
    return folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="CartoDB positron",
        min_zoom=2
    )

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
            zoom_start=3,
            tiles='CartoDB positron'
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
                    <p><b>Year:</b> {book['year']}</p>
                    <p><b>Century:</b> {book.get('century', 'Unknown')}th</p>
                    <p><b>Location:</b> {location_name}</p>
                    <p><b>Type:</b> {location_desc}</p>
                    <p><b>Summary:</b> {book['summary'][:150]}{'...' if len(book['summary']) > 150 else ''}</p>
                    <p><b>Historical Context:</b> {book['historical_context'][:150]}{'...' if len(book['historical_context']) > 150 else ''}</p>
                </div>
            """

            # Add marker with appropriate icon
            folium.Marker(
                location=coordinates,
                popup=folium.Popup(popup_html, max_width=320),
                icon=get_marker_icon(location_type)
            ).add_to(marker_cluster)

        # Add improved legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; 
                    padding: 15px; border: 2px solid #2E4057; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    font-family: Arial, sans-serif;">
            <h4 style="margin-top: 0; color: #2E4057;">Location Types</h4>
            <p style="margin: 5px 0;"><i class="fa fa-book" style="color: red; margin-right: 8px;"></i> Primary Story Setting</p>
            <p style="margin: 5px 0;"><i class="fa fa-book" style="color: blue; margin-right: 8px;"></i> Publication Location</p>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">Blue markers show publication locations for books with fictional/metaphysical/multiple settings</p>
        </div>
        '''
        literary_map.get_root().html.add_child(folium.Element(legend_html))

        return literary_map
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None