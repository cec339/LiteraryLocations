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
        'primary': 'red',      # Primary story setting
        'publication': 'blue', # Publication location
        'fictional': 'green'   # Fictional setting, showing publication location
    }
    return folium.Icon(
        icon='book',
        prefix='fa',
        color=icon_colors.get(location_type, 'gray')
    )

def create_literature_map(books_df):
    """
    Create an interactive map showing literary locations

    Args:
        books_df: DataFrame containing book data with latitude and longitude
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
            # Determine location type and coordinates to use
            location_type = 'primary'  # default
            if pd.isna(book['setting_latitude']) or pd.isna(book['setting_longitude']):
                if pd.notna(book['publication_latitude']) and pd.notna(book['publication_longitude']):
                    location_type = 'publication'
                    coordinates = [float(book['publication_latitude']), float(book['publication_longitude'])]
                    location_name = book['publication_name']
                else:
                    continue  # Skip if no valid coordinates
            else:
                coordinates = [book['setting_latitude'], book['setting_longitude']]
                location_name = book['setting_name']

                # Check if it's a fictional setting
                if book.get('is_fictional', False):
                    location_type = 'fictional'

            popup_html = f"""
                <div style='width: 250px'>
                    <h4>{book['title']}</h4>
                    <p><b>Author:</b> {book['author']}</p>
                    <p><b>Year:</b> {book['year']}</p>
                    <p><b>Location:</b> {location_name}</p>
                    <p><b>Location Type:</b> {location_type.title()}</p>
                    <p><b>Summary:</b> {book['summary']}</p>
                    <p><b>Historical Context:</b> {book['historical_context']}</p>
                </div>
            """

            # Add marker with appropriate icon
            folium.Marker(
                location=coordinates,
                popup=folium.Popup(popup_html, max_width=300),
                icon=get_marker_icon(location_type)
            ).add_to(marker_cluster)

        # Add legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; 
                    padding: 10px; border: 2px solid grey; border-radius: 5px">
            <h4>Legend</h4>
            <p><i class="fa fa-book" style="color: red"></i> Primary Setting</p>
            <p><i class="fa fa-book" style="color: green"></i> Fictional Setting (Publication Location shown)</p>
        </div>
        '''
        literary_map.get_root().html.add_child(folium.Element(legend_html))

        return literary_map
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None