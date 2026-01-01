import streamlit as st
from utils.data_loader import (
    load_book_data,
    get_century_range,
    filter_books_by_century,
    search_books,
    get_dataset_stats
)
from utils.map_utils import create_literature_map
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Literary World Map",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with open("styles/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if 'selected_century' not in st.session_state:
    st.session_state.selected_century = 19
if 'last_search_query' not in st.session_state:
    st.session_state.last_search_query = ""
if 'century_updated' not in st.session_state:
    st.session_state.century_updated = False
if 'show_legend' not in st.session_state:
    st.session_state.show_legend = False
if 'show_books' not in st.session_state:
    st.session_state.show_books = False

century_options = list(range(-20, 0)) + list(range(1, 22))

with st.sidebar:
    st.header("🔍 Search Books")
    search_query = st.text_input("Search by title or author")

    if search_query:
        search_results = search_books(search_query)
        if not search_results.empty:
            st.success(f"Found {len(search_results)} matching books")
            st.info("Clear the search box and press Enter to return to century view")

            if (search_query != st.session_state.last_search_query and 
                not st.session_state.century_updated and
                'century' in search_results.columns):
                most_common_century = search_results['century'].mode()[0]
                st.session_state.selected_century = int(most_common_century)
                st.session_state.last_search_query = search_query
                st.session_state.century_updated = True
                st.rerun()
        else:
            st.warning("No books found matching your search")
    else:
        st.session_state.last_search_query = ""
        st.session_state.century_updated = False
        search_results = None

    st.header("📊 Dataset Info")
    stats = get_dataset_stats()
    st.metric("Total Books", stats.get("total_books", 0))
    st.metric("Unique Authors", stats.get("unique_authors", 0))

try:
    if search_query and search_results is not None and not search_results.empty:
        filtered_books = search_results
    else:
        filtered_books = filter_books_by_century(st.session_state.selected_century)

    book_count = len(filtered_books) if not filtered_books.empty else 0

    display_century = st.session_state.selected_century
    if display_century < 0:
        century_display = f"{abs(display_century)} BCE"
    else:
        century_display = f"{display_century} CE"

    try:
        current_index = century_options.index(st.session_state.selected_century)
    except ValueError:
        current_index = century_options.index(19)
    
    can_go_prev = current_index > 0
    can_go_next = current_index < len(century_options) - 1

    literary_map = None
    folium_html = ""
    if not filtered_books.empty:
        literary_map = create_literature_map(filtered_books)
        if literary_map:
            folium_html = literary_map._repr_html_()

    map_only_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html, body {{ width: 100%; height: 100%; overflow: hidden; }}
            .map-container {{ width: 100%; height: 100%; }}
            .map-container iframe,
            .map-container .folium-map {{ width: 100% !important; height: 100% !important; border: none !important; }}
            .no-books {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                color: #666;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            .no-books-icon {{ font-size: 64px; margin-bottom: 16px; }}
            .no-books h2 {{ color: #555; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div class="map-container">
            {folium_html if folium_html else '<div class="no-books"><div class="no-books-icon">📚</div><h2>No books found for this century</h2></div>'}
        </div>
    </body>
    </html>
    """

    st.markdown("""
    <style>
        .stApp > header { display: none !important; }
        .main .block-container { 
            padding: 0 !important; 
            max-width: 100% !important;
            margin: 0 !important;
        }
        section[data-testid="stSidebar"] {
            background: rgba(255,255,255,0.98);
        }
        
        /* Make the HTML component fill the screen */
        .stHtml { width: 100% !important; }
        .stHtml > div { width: 100% !important; }
        .stHtml iframe { 
            width: 100% !important; 
            height: calc(100vh - 80px) !important;
            border: none !important;
        }
        
        /* Bottom control bar */
        .control-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(20, 20, 20, 0.4);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 8px 12px;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }
        
        .century-label {
            color: white;
            font-size: 18px;
            font-weight: 600;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
            min-width: 70px;
            text-align: center;
        }
        
        .book-count {
            color: rgba(255,255,255,0.9);
            font-size: 13px;
            background: rgba(31, 119, 180, 0.7);
            padding: 4px 10px;
            border-radius: 12px;
        }
        
        .legend-toggle {
            position: fixed;
            bottom: 70px;
            left: 12px;
            background: rgba(20, 20, 20, 0.4);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 8px;
            padding: 8px 12px;
            z-index: 1000;
        }
        
        .legend-content {
            color: white;
            font-size: 12px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 4px 0;
        }
        
        .legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        
        .legend-dot.red { background: #d63384; }
        .legend-dot.blue { background: #38A3D1; }
        
        /* Style Streamlit columns for control bar */
        div[data-testid="stHorizontalBlock"] {
            gap: 8px !important;
        }
        
        div[data-testid="column"] {
            padding: 0 !important;
        }
        
        /* Nav button styling */
        .nav-button button {
            background: rgba(255,255,255,0.15) !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
            color: white !important;
            min-height: 44px !important;
            min-width: 44px !important;
            padding: 0 16px !important;
            border-radius: 22px !important;
            font-weight: 600 !important;
        }
        
        .nav-button button:hover {
            background: rgba(255,255,255,0.25) !important;
            border-color: rgba(255,255,255,0.4) !important;
        }
        
        /* Hide default streamlit elements */
        .stDeployButton { display: none !important; }
        
        @media (max-width: 768px) {
            .stHtml iframe { 
                height: calc(100vh - 70px) !important;
            }
            
            .control-bar {
                padding: 6px 8px;
                gap: 8px;
            }
            
            .century-label {
                font-size: 16px;
                min-width: 60px;
            }
            
            .book-count {
                font-size: 12px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    components.html(map_only_html, height=700, scrolling=False)

    if st.session_state.show_legend:
        st.markdown("""
        <div class="legend-toggle">
            <div class="legend-content">
                <div class="legend-item"><div class="legend-dot red"></div><span>Story Setting</span></div>
                <div class="legend-item"><div class="legend-dot blue"></div><span>Publication Location</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="control-bar">
        <span class="century-label">{century_display}</span>
        <span class="book-count">{book_count} book{'s' if book_count != 1 else ''}</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("◀ Prev", key="prev_btn", disabled=not can_go_prev, use_container_width=True):
            st.session_state.selected_century = century_options[current_index - 1]
            st.rerun()
    
    with col2:
        if st.button("ℹ Legend", key="legend_btn", use_container_width=True):
            st.session_state.show_legend = not st.session_state.show_legend
            st.rerun()
    
    with col3:
        if st.button("📚 Books", key="books_btn", use_container_width=True):
            st.session_state.show_books = not st.session_state.show_books
            st.rerun()
    
    with col4:
        if st.button("Next ▶", key="next_btn", disabled=not can_go_next, use_container_width=True):
            st.session_state.selected_century = century_options[current_index + 1]
            st.rerun()

    if st.session_state.show_books and not filtered_books.empty:
        st.markdown("---")
        st.subheader(f"📚 Books from {century_display}")
        for _, book in filtered_books.iterrows():
            with st.expander(f"**{book['title']}** by {book['author']}"):
                st.write(f"**Year:** {int(book['year'])}")
                st.write(f"**Location:** {book['setting_name']}")
                st.write(f"**Summary:** {book['summary'][:200]}...")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check the data files and try again.")
