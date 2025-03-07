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

    # Load book data
    all_books = load_book_data()
    if all_books.empty:
        st.error("No book data available.")
        st.stop()

    # Search & Filter section at the top
    st.header("Search & Filter")
    search_query = st.text_input("Search by title or author", key="search_input")

    # Get century range for the slider
    min_century, max_century = get_century_range()
    logger.info(f"Century range: {min_century} to {max_century}")

    # Handle case when min and max centuries are the same
    if min_century == max_century:
        st.subheader("Time Period")
        st.markdown(f"**Currently showing: {min_century}th Century**")
        selected_century = min_century
    else:
        # Century selector with clear labeling
        st.subheader("Time Period")
        selected_century = st.slider(
            "Select Century",
            min_value=int(min_century),
            max_value=int(max_century),
            value=int(min_century),
            step=1,
            help="Slide to explore different time periods",
            key="century_slider"
        )
        suffix = "th"
        if selected_century == 1:
            suffix = "st"
        elif selected_century == 2:
            suffix = "nd"
        elif selected_century == 3:
            suffix = "rd"
        st.markdown(f"**Selected: {selected_century}{suffix} Century**")
    
    # Filter books based on search and century
    if search_query:
        filtered_books = search_books(search_query)
        logger.info(f"Search query '{search_query}' returned {len(filtered_books)} results")
        search_mode = True
    else:
        filtered_books = filter_books_by_century(selected_century)
        logger.info(f"Century filter {selected_century} returned {len(filtered_books)} books")
        search_mode = False
    
    # Check if books are from other centuries (when selected century has no books)
    showing_adjacent = False
    # Create two columns for the main layout (map and info)
    col1, col2 = st.columns([3, 1])

    with col1:  # Main content area - Map
        # Create and display map
        if not filtered_books.empty:
            literary_map = create_literature_map(filtered_books)
            if literary_map:
                st.markdown('<div class="map-container">', unsafe_allow_html=True)
                folium_html = literary_map._repr_html_()
                components.html(folium_html, height=600)
                
                # Add fullscreen toggle button
                st.markdown("""
                <button id="fullscreen-btn" title="Toggle fullscreen">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
                    </svg>
                </button>
                
                <script>
                    // Add fullscreen functionality
                    const mapContainer = document.querySelector('.map-container');
                    const fullscreenBtn = document.getElementById('fullscreen-btn');
                    
                    fullscreenBtn.addEventListener('click', () => {
                        mapContainer.classList.toggle('fullscreen-map');
                        
                        // Update button icon based on state
                        if (mapContainer.classList.contains('fullscreen-map')) {
                            fullscreenBtn.innerHTML = `
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M4 14h6m0 0v6m0-6l-7 7m17-11h-6m0 0V4m0 6l7-7"></path>
                                </svg>
                            `;
                        } else {
                            fullscreenBtn.innerHTML = `
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
                                </svg>
                            `;
                        }
                    });
                </script>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                logger.info("Map created and displayed successfully")
    
    with col2:  # Side info
        if not filtered_books.empty:
            st.subheader("Book Count")
            st.markdown(f"**{len(filtered_books)} books** from the {selected_century}{suffix} Century")
        else:
            st.subheader("Book Count")
            st.info(f"No books available from the {selected_century}{suffix} Century.")
    
    # Display book list below the map
    if not filtered_books.empty:
        st.subheader("Featured Books")
        for _, book in filtered_books.iterrows():
            century_suffix = "th"
            if book['century'] == 1:
                century_suffix = "st"
            elif book['century'] == 2:
                century_suffix = "nd"
            elif book['century'] == 3:
                century_suffix = "rd"
            with st.expander(f"{book['title']} by {book['author']} ({book['year']}, {book['century']}{century_suffix} century)"):
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