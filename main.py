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

# Add custom JavaScript for creating notches
notch_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Function to add notches to the slider
    function addNotchesToSlider() {
        const sliderContainer = document.querySelector('[data-testid="stSelectSlider"]');
        if (!sliderContainer) return;
        
        // Remove any existing notches div to avoid duplicates
        const existingNotches = document.getElementById('slider-notches');
        if (existingNotches) existingNotches.remove();
        
        // Create new notches container
        const notchesContainer = document.createElement('div');
        notchesContainer.id = 'slider-notches';
        notchesContainer.style.position = 'absolute';
        notchesContainer.style.bottom = '0';
        notchesContainer.style.left = '0';
        notchesContainer.style.right = '0';
        notchesContainer.style.height = '20px';
        notchesContainer.style.pointerEvents = 'none';
        
        // Add 41 notches (for centuries from -20 to 21, excluding 0)
        const totalNotches = 41;
        for (let i = 0; i < totalNotches; i++) {
            const notch = document.createElement('div');
            notch.style.position = 'absolute';
            notch.style.bottom = '0';
            notch.style.left = `${(i / (totalNotches-1)) * 100}%`;
            notch.style.width = '2px';
            notch.style.height = '10px';
            notch.style.backgroundColor = '#1f77b4';
            notchesContainer.appendChild(notch);
            
            // Add major notches (every 5 centuries)
            if (i % 5 === 0) {
                notch.style.height = '15px';
                notch.style.width = '3px';
            }
        }
        
        sliderContainer.appendChild(notchesContainer);
    }
    
    // Initial call
    setTimeout(addNotchesToSlider, 1000);
    
    // Set up a mutation observer to detect DOM changes and add notches when slider appears
    const observer = new MutationObserver(function(mutations) {
        addNotchesToSlider();
    });
    
    // Start observing the document body for changes
    observer.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
});
</script>
"""
st.components.v1.html(notch_js, height=0)

# Header (more compact)
st.markdown("<h1 style='margin-bottom:0.5rem;'>📚 Literary World Map</h1>", unsafe_allow_html=True)
st.markdown("<p style='margin-bottom:0.5rem;'>Explore the geographical settings of classic literature through time</p>", unsafe_allow_html=True)

# Sidebar for search
# Create session state to store the selected century between reruns
if 'selected_century' not in st.session_state:
    st.session_state.selected_century = 19
# Create a flag to track if we've already processed this search
if 'last_search_query' not in st.session_state:
    st.session_state.last_search_query = ""
if 'century_updated' not in st.session_state:
    st.session_state.century_updated = False

with st.sidebar:
    st.header("Search Books")
    search_query = st.text_input("Search by title or author")
    
    if search_query:
        search_results = search_books(search_query)
        if not search_results.empty:
            st.success(f"Found {len(search_results)} matching books")
            st.info("Clear the search box and press Enter to return to century view")
            
            # Only update century and rerun if this is a new search
            if (search_query != st.session_state.last_search_query and 
                not st.session_state.century_updated and
                'century' in search_results.columns):
                # Get the most common century in search results to set the slider
                most_common_century = search_results['century'].mode()[0]
                st.session_state.selected_century = int(most_common_century)
                st.session_state.last_search_query = search_query
                st.session_state.century_updated = True
                # Force rerun to update the slider with the new century value
                st.rerun()
        else:
            st.warning("No books found matching your search")
    else:
        # Reset the flags when search is cleared
        st.session_state.last_search_query = ""
        st.session_state.century_updated = False
        st.info("Use the slider to explore books by century")

# Main content
try:
    # Add century label above slider
    # Ensure proper century label display - skip Century 0
    display_century = st.session_state.selected_century
    if display_century == 0:
        display_century = display_century + 1
        century_suffix = "CE"
    else:
        century_suffix = "BCE" if display_century < 0 else "CE"
    
    century_label = f"Century: {abs(display_century)} {century_suffix}"
    st.markdown(f"<h3 style='text-align: center;'>{century_label}</h3>", unsafe_allow_html=True)
    
    # Create a list of centuries that excludes 0
    century_options = list(range(-20, 0)) + list(range(1, 22))
    
    # Find the index of the current selected century in our options
    try:
        current_index = century_options.index(st.session_state.selected_century)
    except ValueError:
        # If the current value isn't in the list (shouldn't happen), default to 19th century
        current_index = century_options.index(19)
    
    # Century selector with custom range that excludes 0
    selected_century = st.select_slider(
            "",  # Empty label since we have the header above
            options=century_options,
            value=century_options[current_index],
            key="century_slider",
            help="Slide to explore literature through time"
        )
    
    # Update session state if changed
    if selected_century != st.session_state.selected_century:
        st.session_state.selected_century = selected_century
        st.rerun()
        
        # We don't need manual markers with select_slider as it already shows labels
    
    # Update session state only if the value has changed
    if st.session_state.century_slider != st.session_state.selected_century:
        st.session_state.selected_century = st.session_state.century_slider
        st.rerun()

    # Get the correct suffix for the century
    def get_century_suffix(century):
        if century <= 0:
            return f"{abs(century)}th century BCE"
        elif century == 21:
            return "21st century"
        elif century == 1:
            return "1st century"
        elif century == 2:
            return "2nd century"
        elif century == 3:
            return "3rd century"
        else:
            return f"{century}th century"

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
            century_text = get_century_suffix(selected_century)
            with st.expander(f"Books from the {century_text}", expanded=False):
                for _, book in filtered_books.iterrows():
                    st.markdown(f"### {book['title']} by {book['author']}")
                    st.markdown("---")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.write(f"**Location:** {book['setting_name']}")
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