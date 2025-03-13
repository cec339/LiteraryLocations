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
with st.sidebar:
    st.header("Search Books")
    search_query = st.text_input("Search by title or author")

    if search_query:
        search_results = search_books(search_query)
        if not search_results.empty:
            st.success(f"Found {len(search_results)} matching books")
        else:
            st.warning("No books found matching your search")

# Main content
try:
    # Century selector with fixed range
    selected_century = st.slider(
        "Select Century",
        min_value=14,
        max_value=21,
        value=19,
        step=1,
        help="Slide to explore literature from different centuries"
    )

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
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            # Set height to almost full viewport height with !important flag for mobile
            components.html(
                folium_html, 
                height=800,
                scrolling=False,
                width=None  # Let CSS control the width
            )
            st.markdown('</div>', unsafe_allow_html=True)

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
    st.error(f"An error occurred: {str(e)}")
    st.info("Please try refreshing the page or contact support if the problem persists.")