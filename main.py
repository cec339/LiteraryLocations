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

query_params = st.query_params
if 'century' in query_params:
    try:
        requested_century = int(query_params['century'])
        if requested_century in list(range(-20, 0)) + list(range(1, 22)):
            st.session_state.selected_century = requested_century
    except (ValueError, TypeError):
        pass

if 'selected_century' not in st.session_state:
    st.session_state.selected_century = 19
if 'last_search_query' not in st.session_state:
    st.session_state.last_search_query = ""
if 'century_updated' not in st.session_state:
    st.session_state.century_updated = False

century_options = list(range(-20, 0)) + list(range(1, 22))

def go_prev():
    try:
        current_index = century_options.index(st.session_state.selected_century)
    except ValueError:
        current_index = century_options.index(19)
    if current_index > 0:
        st.session_state.selected_century = century_options[current_index - 1]

def go_next():
    try:
        current_index = century_options.index(st.session_state.selected_century)
    except ValueError:
        current_index = century_options.index(19)
    if current_index < len(century_options) - 1:
        st.session_state.selected_century = century_options[current_index + 1]

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
                st.query_params["century"] = str(int(most_common_century))
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
    prev_century = century_options[current_index - 1] if can_go_prev else None
    next_century = century_options[current_index + 1] if can_go_next else None

    literary_map = None
    folium_html = ""
    if not filtered_books.empty:
        literary_map = create_literature_map(filtered_books)
        if literary_map:
            folium_html = literary_map._repr_html_()

    # Build book count text
    book_count_text = f"{book_count} book" + ("s" if book_count != 1 else "")
    
    map_only_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html, body {{ 
                width: 100vw; 
                height: 100vh; 
                overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            .map-container {{ 
                position: absolute;
                top: 0;
                left: 0;
                width: 100vw; 
                height: 100vh;
            }}
            
            .map-container > div,
            .map-container iframe,
            .map-container .folium-map,
            .leaflet-container {{ 
                width: 100vw !important; 
                height: 100vh !important; 
                border: none !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
            }}
            
            .no-books {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                color: #666;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }}
            .no-books-icon {{ font-size: 64px; margin-bottom: 16px; }}
            .no-books h2 {{ color: #555; font-weight: 500; }}
            
            /* Bottom control bar */
            .controls {{
                position: fixed;
                bottom: calc(env(safe-area-inset-bottom, 0px) + 8px);
                left: 50%;
                transform: translateX(-50%);
                width: min(400px, calc(100% - 16px));
                z-index: 10000;
                display: flex;
                flex-direction: column;
                pointer-events: none;
            }}
            
            .button-row {{
                display: flex;
                gap: 8px;
                pointer-events: auto;
            }}
            
            .nav-btn {{
                flex: 1 1 0;
                min-width: 0;
                height: 44px;
                border: none;
                border-radius: 16px;
                background: rgba(40, 40, 40, 0.75);
                color: white;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 4px;
                transition: background 0.2s;
                text-decoration: none;
            }}
            
            .nav-btn:hover {{
                background: rgba(40, 40, 40, 0.9);
                color: white;
            }}
            
            .nav-btn:disabled,
            .nav-btn.disabled {{
                opacity: 0.4;
                cursor: not-allowed;
                pointer-events: none;
            }}
            
            .info-bar {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                padding: 6px 12px;
                background: rgba(30, 30, 30, 0.8);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                pointer-events: auto;
            }}
            
            .century-label {{
                color: white;
                font-size: 14px;
                font-weight: 600;
            }}
            
            .book-count {{
                background: rgba(31, 119, 180, 0.9);
                color: white;
                font-size: 11px;
                padding: 2px 8px;
                border-radius: 10px;
            }}
            
            /* Legend popup */
            .legend {{
                display: none;
                position: fixed;
                bottom: 80px;
                left: 8px;
                background: rgba(30, 30, 30, 0.85);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                border-radius: 8px;
                padding: 10px 14px;
                z-index: 10001;
                pointer-events: auto;
            }}
            
            .legend.show {{
                display: block;
            }}
            
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                color: white;
                font-size: 12px;
                margin: 4px 0;
            }}
            
            .legend-dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
            }}
            
            .legend-dot.red {{ background: #d63384; }}
            .legend-dot.blue {{ background: #38A3D1; }}
        </style>
    </head>
    <body>
        <div class="map-container">
            {folium_html if folium_html else '<div class="no-books"><div class="no-books-icon">📚</div><h2>No books found for this century</h2></div>'}
        </div>
        
        <div id="legend" class="legend">
            <div class="legend-item"><div class="legend-dot red"></div><span>Story Setting</span></div>
            <div class="legend-item"><div class="legend-dot blue"></div><span>Publication Location</span></div>
        </div>
        
        <script>
            function toggleLegend() {{
                document.getElementById('legend').classList.toggle('show');
            }}
            
            // Make sure the map fills the container
            setTimeout(function() {{
                var maps = document.querySelectorAll('.leaflet-container');
                maps.forEach(function(map) {{
                    map.style.width = '100vw';
                    map.style.height = '100vh';
                    if (map._leaflet_map) {{
                        map._leaflet_map.invalidateSize();
                    }}
                }});
            }}, 100);
        </script>
    </body>
    </html>
    """

    st.markdown(f"""
    <style>
        /* Hide ALL Streamlit chrome */
        header[data-testid="stHeader"],
        .stDeployButton,
        #MainMenu,
        footer,
        .stApp > header {{
            display: none !important;
        }}
        
        /* Reset ALL Streamlit containers */
        .stApp,
        .main,
        section.main,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        [data-testid="block-container"],
        .block-container,
        div[data-testid="stVerticalBlock"] {{
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            width: 100% !important;
            background: transparent !important;
        }}
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background: rgba(255,255,255,0.98);
            z-index: 10000 !important;
        }}
        
        /* Make iframe fill entire viewport but allow clicks through to controls */
        [data-testid="stHtml"],
        .stHtml {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 1 !important;
            padding: 0 !important;
            margin: 0 !important;
            pointer-events: auto;
        }}
        
        iframe {{
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            pointer-events: auto;
        }}
        
        /* Hide default button container styling */
        div[data-testid="column"] > div {{
            padding: 0 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    components.html(map_only_html, height=2000, scrolling=False)
    
    st.markdown(f"""
    <style>
        /* Navigation controls container */
        .stElementContainer:has(.nav-wrapper) {{
            position: fixed !important;
            bottom: 8px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: min(400px, calc(100% - 16px)) !important;
            z-index: 10001 !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        
        .nav-wrapper {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        
        .info-bar {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 6px 12px;
            background: rgba(30, 30, 30, 0.85);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-radius: 16px;
        }}
        
        .century-label {{
            color: white;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .book-count {{
            background: rgba(31, 119, 180, 0.9);
            color: white;
            font-size: 12px;
            padding: 3px 10px;
            border-radius: 12px;
        }}
        
        /* Force buttons to stay in horizontal row on all screen sizes */
        div[data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 8px !important;
            width: 100% !important;
        }}
        
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            flex: 1 1 0 !important;
            min-width: 0 !important;
            width: auto !important;
        }}
        
        /* Style buttons */
        .stButton button {{
            width: 100% !important;
            height: 44px !important;
            border-radius: 22px !important;
            background: rgba(40, 40, 40, 0.85) !important;
            color: white !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            border: none !important;
            backdrop-filter: blur(8px) !important;
        }}
        
        .stButton button:hover {{
            background: rgba(60, 60, 60, 0.95) !important;
            color: white !important;
        }}
        
        .stButton button:disabled {{
            opacity: 0.4 !important;
        }}
    </style>
    <div class="nav-wrapper">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if can_go_prev:
            if st.button("◀ Prev", use_container_width=True):
                st.query_params["century"] = str(prev_century)
                st.rerun()
        else:
            st.button("◀ Prev", disabled=True, use_container_width=True)
    with col2:
        with st.popover("ℹ️ Legend", use_container_width=True):
            st.markdown("""
            <div style="color: #333; font-size: 14px;">
                <div style="display: flex; align-items: center; gap: 8px; margin: 4px 0;">
                    <div style="width: 12px; height: 12px; background: #d63384; border-radius: 50%;"></div>
                    <span>Story Setting</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; margin: 4px 0;">
                    <div style="width: 12px; height: 12px; background: #38A3D1; border-radius: 50%;"></div>
                    <span>Publication Location</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    with col3:
        if can_go_next:
            if st.button("Next ▶", use_container_width=True):
                st.query_params["century"] = str(next_century)
                st.rerun()
        else:
            st.button("Next ▶", disabled=True, use_container_width=True)
    
    st.markdown(f"""
        <div class="info-bar">
            <span class="century-label">{century_display}</span>
            <span class="book-count">{book_count_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check the data files and try again.")
