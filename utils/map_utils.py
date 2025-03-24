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
    """
    Create an interactive map showing literary locations

    Args:
        books_df: DataFrame containing book data with latitude and longitude

    Returns:
        folium.Map object
    """
    try:
        # Make sure latitude and longitude are float type
        books_df['setting_latitude'] = books_df['setting_latitude'].astype(float)
        books_df['setting_longitude'] = books_df['setting_longitude'].astype(float)

        # Create base map centered on average coordinates
        avg_lat = books_df['setting_latitude'].mean()
        avg_lon = books_df['setting_longitude'].mean()

        # Create a map
        literary_map = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=3,
            tiles='CartoDB positron'
        )

        # Add marker cluster
        marker_cluster = MarkerCluster().add_to(literary_map)

        # Add markers for each book
        for _, book in books_df.iterrows():
            popup_html = f"""
                <div style='width: 250px'>
                    <h4>{book['title']}</h4>
                    <p><b>Author:</b> {book['author']}</p>
                    <p><b>Year:</b> {book['year']}</p>
                    <p><b>Location:</b> {book['location_name']}</p>
                    <p><b>Summary:</b> {book['summary']}</p>
                    <p><b>Historical Context:</b> {book['historical_context']}</p>
                </div>
            """

            # Add setting location marker
            setting_location = [float(book['setting_latitude']), float(book['setting_longitude'])]
            folium.Marker(
                location=setting_location,
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(icon='book', prefix='fa', color='red')
            ).add_to(marker_cluster)

            # Add publication location marker if exists
            if pd.notna(book['publication_latitude']) and pd.notna(book['publication_longitude']):
                pub_location = [float(book['publication_latitude']), float(book['publication_longitude'])]
                folium.Marker(
                    location=pub_location,
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(icon='book', prefix='fa', color='blue')
                ).add_to(marker_cluster)

        # Add legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; 
                    padding: 10px; border: 2px solid grey; border-radius: 5px">
            <h4>Legend</h4>
            <p><i class="fa fa-book" style="color: red"></i> Primary Setting</p>
            <p><i class="fa fa-book" style="color: blue"></i> Publication Location</p>
        </div>
        '''
        literary_map.get_root().html.add_child(folium.Element(legend_html))

        return literary_map
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None