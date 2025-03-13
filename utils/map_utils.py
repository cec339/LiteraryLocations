import folium
from folium.plugins import MarkerCluster
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
    """
    Create an interactive map showing literary locations

    Args:
        books_df: DataFrame containing book data with latitude and longitude

    Returns:
        folium.Map object
    """
    try:
        # Make sure latitude and longitude are float type
        books_df['latitude'] = books_df['latitude'].astype(float)
        books_df['longitude'] = books_df['longitude'].astype(float)

        # Create base map centered on average coordinates
        avg_lat = books_df['latitude'].mean()
        avg_lon = books_df['longitude'].mean()

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
                <div style='width: 200px'>
                    <h4>{book['title']}</h4>
                    <p><b>Author:</b> {book['author']}</p>
                    <p><b>Year:</b> {book['year']}</p>
                </div>
            """

            folium.Marker(
                location=[float(book['latitude']), float(book['longitude'])],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=book['title'],
                icon=folium.Icon(icon='book', prefix='fa')
            ).add_to(marker_cluster)

        return literary_map
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None