import os
import sys
import logging

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting Literary World Map application...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"PYTHONPATH: {sys.path}")

try:
    import streamlit as st
    from utils.data_loader import (
        load_book_data,
        get_century_range,
        filter_books_by_century,
        search_books
    )
    from utils.map_utils import create_literature_map
    import streamlit.components.v1 as components
    logger.info("Successfully imported all required modules")
except Exception as e:
    logger.error(f"Error importing modules: {str(e)}", exc_info=True)
    raise

try:
    # Page configuration
    st.set_page_config(
        page_title="Literary World Map",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    logger.info("Page configuration set successfully")

    # Load custom CSS
    try:
        with open("styles/custom.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        logger.info("Loaded custom CSS successfully")
    except Exception as e:
        logger.error(f"Error loading CSS: {str(e)}")

    # Header
    st.title("📚 Literary World Map")
    st.markdown("Explore the geographical settings of classic literature through time")

    # Sidebar for search
    with st.sidebar:
        st.header("Search Books")
        search_query = st.text_input("Search by title or author", key="search_input")

    # Main content
    logger.info("Loading book data and initializing map...")
    # Get century range for the slider
    min_century, max_century = get_century_range()
    logger.info(f"Century range: {min_century} to {max_century}")

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
    if 'search_query' in locals() and search_query:
        filtered_books = search_books(search_query)
        logger.info(f"Search query '{search_query}' returned {len(filtered_books)} results")
    else:
        filtered_books = filter_books_by_century(selected_century)
        logger.info(f"Century filter {selected_century} returned {len(filtered_books)} books")

    # Create and display map
    if not filtered_books.empty:
        literary_map = create_literature_map(filtered_books)
        if literary_map:
            folium_html = literary_map._repr_html_()
            components.html(folium_html, height=800)
            logger.info("Map created and displayed successfully")

            # Display book list
            st.subheader(f"Books from the {selected_century}{'st' if selected_century % 10 == 1 else 'th'} Century")
            for _, book in filtered_books.iterrows():
                with st.expander(f"{book['title']} by {book['author']}"):
                    st.write(f"**Location:** {book['location_name']}")
                    st.write(f"**Year:** {book['year']}")
                    st.write(f"**Summary:** {book['summary']}")
                    st.write(f"**Historical Context:** {book['historical_context']}")
    else:
        st.info("No books found for the selected criteria")
        logger.warning("No books found for the current filter criteria")

except Exception as e:
    logger.error(f"An error occurred: {str(e)}", exc_info=True)
    st.error(f"An error occurred: {str(e)}")
    st.info("Please try refreshing the page or contact support if the problem persists.")