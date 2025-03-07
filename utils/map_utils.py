
import folium
from folium import plugins
import streamlit as st
import pandas as pd

def create_base_map():
    """Create the base world map using Mapbox."""
    # Use Mapbox tiles instead of CartoDB
    mapbox_token = "pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA"
    mapbox_url = f"https://api.mapbox.com/styles/v1/mapbox/light-v10/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_token}"
    
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles=None,
        min_zoom=2
    )
    
    # Add Mapbox tiles with attribution
    folium.TileLayer(
        tiles=mapbox_url,
        attr='Map data © Mapbox contributors',
        name='Mapbox Light',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add satellite view option
    mapbox_satellite_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_token}"
    folium.TileLayer(
        tiles=mapbox_satellite_url,
        attr='Satellite data © Mapbox contributors',
        name='Mapbox Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    # Add layer control and fullscreen option with more visible styling
    folium.LayerControl().add_to(m)
    plugins.Fullscreen(
        position="topright",
        title="Expand map",
        title_cancel="Exit fullscreen",
        force_separate_button=True,
        fullscreen_icon=True
    ).add_to(m)
    
    # Add custom CSS to make buttons more visible
    folium.Element("""
    <style>
    /* Make fullscreen button more visible */
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
    
    /* Make all controls more visible */
    .leaflet-control {
        box-shadow: 0 1px 5px rgba(0,0,0,0.65) !important;
    }
    
    /* Make markers stand out more */
    .leaflet-marker-icon {
        filter: drop-shadow(0 0 5px white) !important;
    }
    </style>
    """).add_to(m)

    return m

def add_book_markers(m, books_df):
    """Add book markers to the map with enhanced visibility."""
    # Create feature groups for different marker types
    book_markers = folium.FeatureGroup(name="Book Locations")
    circle_markers = folium.FeatureGroup(name="Book Highlights")
    
    # Debug count for successful markers
    successful_markers = 0
    
    # Process each book
    for _, book in books_df.iterrows():
        # Skip if coordinates are missing or invalid
        if pd.isna(book['latitude']) or pd.isna(book['longitude']):
            continue

        # Convert coordinates to float explicitly
        try:
            lat = float(book['latitude'])
            lng = float(book['longitude'])
        except (ValueError, TypeError):
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

        # Add a large circle marker first for better visibility
        folium.CircleMarker(
            location=[lat, lng],
            radius=15,
            color="#FF5733",
            fill=True,
            fill_color="#FF5733",
            fill_opacity=0.7,
            popup=folium.Popup(html, max_width=300),
            tooltip=book['title']
        ).add_to(circle_markers)
        
        # Add standard marker with custom icon
        icon = folium.features.CustomIcon(
            icon_image="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png",
            icon_size=(30, 30),
            icon_anchor=(15, 30),
            popup_anchor=(0, -30)
        )
        
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(html, max_width=300),
            tooltip=book['title'],
            icon=icon
        ).add_to(book_markers)
        
        successful_markers += 1

    # Add the feature groups to the map
    circle_markers.add_to(m)
    book_markers.add_to(m)
    
    # Debug information
    if successful_markers == 0:
        st.error("❌ No markers could be added to the map. Please check your data.")
    else:
        st.success(f"✅ Successfully added {successful_markers} book markers to the map")

    return successful_markers > 0

def create_literature_map(books_df):
    """Create the complete literature map with markers."""
    try:
        # Create base map
        m = create_base_map()

        # Add markers
        markers_added = add_book_markers(m, books_df)
        
        # Add a marker cluster for when there are many books
        if len(books_df) > 10:
            marker_cluster = plugins.MarkerCluster().add_to(m)
            
            for _, book in books_df.iterrows():
                if pd.isna(book['latitude']) or pd.isna(book['longitude']):
                    continue
                    
                try:
                    lat = float(book['latitude'])
                    lng = float(book['longitude'])
                    folium.Marker(
                        [lat, lng],
                        tooltip=book['title']
                    ).add_to(marker_cluster)
                except:
                    continue

        # Fit map to markers if there are any
        if markers_added:
            valid_coords = books_df[~pd.isna(books_df['latitude']) & ~pd.isna(books_df['longitude'])]
            if not valid_coords.empty:
                sw = valid_coords[['latitude', 'longitude']].min().values.tolist()
                ne = valid_coords[['latitude', 'longitude']].max().values.tolist()
                m.fit_bounds([sw, ne], padding=(50, 50))

        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None
