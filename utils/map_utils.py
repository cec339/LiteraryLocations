import folium
from folium.plugins import MarkerCluster


def create_base_map_html():
    """
    Create base map HTML with MarkerCluster JS/CSS dependencies loaded but no markers.
    Returns the raw inner HTML document, not an iframe-wrapped version.
    """
    m = folium.Map(
        location=[20, 0],
        zoom_start=3,
        tiles="CartoDB positron",
        world_copy_jump=True,
    )
    MarkerCluster().add_to(m)
    html = m.get_root().render()
    return html.replace(
        "</head>",
        "<style>.leaflet-top.leaflet-left{left:auto!important;right:10px!important;}</style></head>",
    )
