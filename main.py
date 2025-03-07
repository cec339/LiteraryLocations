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

# Header
st.title("📚 Literary World Map")
st.markdown("Explore the geographical settings of classic literature through time")

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
    # Get century range for the slider
    min_century, max_century = get_century_range()
    
    # Handle case when min and max centuries are the same
    if min_century == max_century:
        st.subheader(f"Showing books from the {int(min_century)}{'st' if int(min_century) % 10 == 1 else 'th'} Century")
        selected_century = int(min_century)
    else:
        # Century selector
        selected_century = st.slider(
            "Select Century",
            min_value=int(min_century),
            max_value=int(max_century),
            value=int(min_century),
            step=1,
            format="%dst" if int(min_century) % 10 == 1 else "%dth"
        )

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
            components.html(folium_html, height=800)
            
            # Display book list
            st.subheader(f"Books from the {selected_century}{'st' if selected_century % 10 == 1 else 'th'} Century")
            for _, book in filtered_books.iterrows():
                with st.expander(f"{book['title']} by {book['author']}"):
                    st.write(f"**Location:** {book['location_name']}")
                    st.write(f"**Year:** {book['year']}")
                    st.write(f"**Summary:** {book['summary']}")
                    st.write(f"**Historical Context:** {book['historical_context']}")
    else:
        st.info("No books found for the selected century")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please try refreshing the page or contact support if the problem persists.")
