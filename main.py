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

century_options = list(range(-20, 0)) + list(range(1, 22))

query_params = st.query_params
if 'nav' in query_params:
    nav_action = query_params.get('nav', '')
    if isinstance(nav_action, list):
        nav_action = nav_action[0] if nav_action else ''
    
    try:
        current_index = century_options.index(st.session_state.selected_century)
    except ValueError:
        current_index = century_options.index(19)
    
    if nav_action == 'prev' and current_index > 0:
        st.session_state.selected_century = century_options[current_index - 1]
    elif nav_action == 'next' and current_index < len(century_options) - 1:
        st.session_state.selected_century = century_options[current_index + 1]
    
    st.query_params.clear()
    st.rerun()

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

    prev_century = century_options[current_index - 1] if can_go_prev else None
    next_century = century_options[current_index + 1] if can_go_next else None
    
    # Build button HTML outside f-string to avoid backslash issues
    if can_go_prev:
        prev_btn = '<button class="nav-btn" onclick="navigate(&quot;prev&quot;)">◀ Prev</button>'
    else:
        prev_btn = '<button class="nav-btn disabled">◀ Prev</button>'
    
    if can_go_next:
        next_btn = '<button class="nav-btn" onclick="navigate(&quot;next&quot;)">Next ▶</button>'
    else:
        next_btn = '<button class="nav-btn disabled">Next ▶</button>'
    
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
                bottom: 0;
                left: 0;
                right: 0;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                pointer-events: none;
            }}
            
            .button-row {{
                display: flex;
                gap: 4px;
                padding: 4px 4px 4px 4px;
                pointer-events: auto;
            }}
            
            .nav-btn {{
                flex: 1;
                height: 32px;
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
        
        /* Make iframe fill entire viewport */
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
        }}
        
        iframe {{
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
        }}
        
        /* Hide default button container styling */
        div[data-testid="column"] > div {{
            padding: 0 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    components.html(map_only_html, height=2000, scrolling=False)
    
    # Navigation buttons using anchor tags for reliable navigation
    prev_class = "disabled" if not can_go_prev else ""
    next_class = "disabled" if not can_go_next else ""
    
    nav_html = f"""
    <style>
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 10001;
            background: linear-gradient(transparent, rgba(0,0,0,0.5));
            padding: 8px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .nav-buttons {{
            display: flex;
            flex-direction: row;
            gap: 6px;
        }}
        .nav-btn {{
            flex: 1;
            height: 44px;
            border: none;
            border-radius: 22px;
            background: rgba(40, 40, 40, 0.85);
            color: white;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .nav-btn:hover {{
            background: rgba(40, 40, 40, 0.95);
        }}
        .nav-btn:disabled,
        .nav-btn.disabled {{
            opacity: 0.4;
            cursor: not-allowed;
            pointer-events: none;
        }}
        a.nav-btn {{
            text-decoration: none;
        }}
        .info-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 4px 0 8px 0;
        }}
        .century-label {{
            color: white;
            font-size: 16px;
            font-weight: 600;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
        }}
        .book-badge {{
            background: rgba(66, 133, 244, 0.9);
            color: white;
            padding: 4px 12px;
            border-radius: 14px;
            font-size: 13px;
            font-weight: 500;
        }}
    </style>
    <div class="bottom-nav">
        <div class="nav-buttons">
            <a class="nav-btn {prev_class}" href="?nav=prev">◀ Prev</a>
            <a class="nav-btn" href="#" title="Red markers = Story Setting, Blue markers = Publication Location">ℹ️</a>
            <a class="nav-btn {next_class}" href="?nav=next">Next ▶</a>
        </div>
        <div class="info-row">
            <span class="century-label">{century_display}</span>
            <span class="book-badge">{book_count_text}</span>
        </div>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check the data files and try again.")
