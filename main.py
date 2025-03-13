import streamlit as st
from utils.data_loader import (
    load_book_data,
    get_century_range,
    filter_books_by_century,
    search_books
)
from utils.map_utils import create_literature_map
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="Literary World Map",
    page_icon="📚",
    layout="wide"
)

# Load custom CSS
with open("styles/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header (more compact)
st.markdown("<h1 style='margin-bottom:0.5rem;'>📚 Literary World Map</h1>", unsafe_allow_html=True)
st.markdown("<p style='margin-bottom:0.5rem;'>Explore the geographical settings of classic literature through time</p>", unsafe_allow_html=True)

# Sidebar for search
# Create session state to store the selected century between reruns
if 'selected_century' not in st.session_state:
    st.session_state.selected_century = 19

with st.sidebar:
    st.header("Search Books")
    search_query = st.text_input("Search by title or author")
    
    if search_query:
        search_results = search_books(search_query)
        if not search_results.empty:
            st.success(f"Found {len(search_results)} matching books")
            st.info("Clear the search box and press Enter to return to century view")
            
            # Update the session state with the century of the first found book
            if 'century' in search_results.columns and not search_results.empty:
                # Get the most common century in search results to set the slider
                most_common_century = search_results['century'].mode()[0]
                st.session_state.selected_century = most_common_century
        else:
            st.warning("No books found matching your search")
    else:
        st.info("Use the slider to explore books by century")

# Main content
try:
    # Century selector with fixed range
    selected_century = st.slider(
        "Select Century",
        min_value=14,
        max_value=21,
        value=st.session_state.selected_century,
        step=1,
        help="Slide to explore literature from different centuries"
    )
    
    # Update session state when slider is moved
    st.session_state.selected_century = selected_century

    # Get the correct suffix for the century
    def get_century_suffix(century):
        if century == 21:
            return "st"
        else:
            return "th"

    # Filter books by century or search results
    if search_query and not search_results.empty:
        filtered_books = search_results
    else:
        filtered_books = filter_books_by_century(selected_century)

    # Create and display map
    if not filtered_books.empty:
        literary_map = create_literature_map(filtered_books)
        if literary_map:
            folium_html = literary_map._repr_html_()
            
            # Custom HTML with fixed styling to ensure proper display
            html_content = f"""
            <div class="map-container" style="width:100%; height:600px; position:relative;">
                {folium_html}
            </div>
            <style>
                .map-container iframe {{
                    width: 100% !important;
                    height: 600px !important;
                    border: none !important;
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                }}
            </style>
            """
            
            # Use full HTML with embedded styles to control the iframe
            st.components.v1.html(
                html_content,
                height=610,  # Slightly larger than the map to avoid scrolling
                scrolling=False
            )

            # Display book list in a collapsible section
            century_suffix = get_century_suffix(selected_century)
            with st.expander(f"Books from the {selected_century}{century_suffix} Century", expanded=False):
                for _, book in filtered_books.iterrows():
                    st.markdown(f"### {book['title']} by {book['author']}")
                    st.markdown("---")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.write(f"**Location:** {book['location_name']}")
                        st.write(f"**Year:** {book['year']}")
                    with col2:
                        st.write(f"**Summary:** {book['summary']}")
                        st.write(f"**Historical Context:** {book['historical_context']}")
                    st.markdown("---")
    else:
        st.info("No books found for the selected century")

except Exception as e:
    import traceback
    error_details = traceback.format_exc()
    st.error(f"An error occurred: {str(e)}")
    st.error(f"Error details: {error_details}")
    st.info("Please try refreshing the page or contact support if the problem persists")