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
import pandas as pd

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
        search_results = pd.DataFrame()

    st.header("📊 Dataset Info")
    stats = get_dataset_stats()
    st.metric("Total Books", stats.get("total_books", 0))
    st.metric("Unique Authors", stats.get("unique_authors", 0))

try:
    if search_query and 'search_results' in dir() and not search_results.empty:
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

    books_list_html = ""
    if not filtered_books.empty:
        for _, book in filtered_books.iterrows():
            books_list_html += f"""
            <div class="book-item">
                <div class="book-title">{book['title']}</div>
                <div class="book-author">by {book['author']}</div>
                <div class="book-details">
                    <span>📍 {book['setting_name']}</span>
                    <span>📅 {int(book['year'])}</span>
                </div>
            </div>
            """

    literary_map = None
    folium_html = ""
    if not filtered_books.empty:
        literary_map = create_literature_map(filtered_books)
        if literary_map:
            folium_html = literary_map._repr_html_()

    full_page_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            html, body {{
                width: 100%;
                height: 100%;
                overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            .map-fullscreen {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
            }}
            
            .map-fullscreen iframe,
            .map-fullscreen .folium-map {{
                width: 100% !important;
                height: 100% !important;
                border: none !important;
            }}
            
            .top-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 50px;
                background: rgba(0, 0, 0, 0.75);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                padding: 0 16px;
            }}
            
            .top-title {{
                color: white;
                font-size: 18px;
                font-weight: 600;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            }}
            
            .bottom-controls {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                z-index: 1000;
                padding: 12px 16px 20px;
                padding-bottom: max(20px, env(safe-area-inset-bottom));
            }}
            
            .century-display {{
                text-align: center;
                margin-bottom: 8px;
            }}
            
            .century-text {{
                color: white;
                font-size: 28px;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }}
            
            .nav-row {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 16px;
                margin-bottom: 8px;
            }}
            
            .nav-btn {{
                width: 48px;
                height: 48px;
                border-radius: 50%;
                border: 2px solid rgba(255,255,255,0.3);
                background: rgba(255,255,255,0.1);
                color: white;
                font-size: 20px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
                -webkit-tap-highlight-color: transparent;
            }}
            
            .nav-btn:hover {{
                background: rgba(255,255,255,0.2);
                border-color: rgba(255,255,255,0.5);
            }}
            
            .nav-btn:active {{
                transform: scale(0.95);
                background: rgba(255,255,255,0.3);
            }}
            
            .nav-btn:disabled {{
                opacity: 0.3;
                cursor: not-allowed;
            }}
            
            .slider-container {{
                flex: 1;
                max-width: 300px;
                padding: 0 8px;
            }}
            
            .century-slider {{
                width: 100%;
                height: 8px;
                -webkit-appearance: none;
                appearance: none;
                background: rgba(255,255,255,0.2);
                border-radius: 4px;
                outline: none;
            }}
            
            .century-slider::-webkit-slider-thumb {{
                -webkit-appearance: none;
                appearance: none;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                background: white;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }}
            
            .century-slider::-moz-range-thumb {{
                width: 28px;
                height: 28px;
                border-radius: 50%;
                background: white;
                cursor: pointer;
                border: none;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }}
            
            .book-count-btn {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                background: rgba(31, 119, 180, 0.9);
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                margin: 0 auto;
                transition: all 0.2s ease;
                -webkit-tap-highlight-color: transparent;
            }}
            
            .book-count-btn:hover {{
                background: rgba(31, 119, 180, 1);
                transform: translateY(-1px);
            }}
            
            .book-count-btn:active {{
                transform: scale(0.98);
            }}
            
            .legend-btn {{
                position: fixed;
                bottom: 140px;
                left: 16px;
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: rgba(0, 0, 0, 0.75);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 2px solid rgba(255,255,255,0.2);
                color: white;
                font-size: 18px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                transition: all 0.2s ease;
                -webkit-tap-highlight-color: transparent;
            }}
            
            .legend-btn:hover {{
                background: rgba(0, 0, 0, 0.85);
                border-color: rgba(255,255,255,0.4);
            }}
            
            .legend-panel {{
                position: fixed;
                bottom: 140px;
                left: 70px;
                background: rgba(0, 0, 0, 0.85);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 12px 16px;
                z-index: 999;
                transform: translateX(-20px);
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }}
            
            .legend-panel.show {{
                transform: translateX(0);
                opacity: 1;
                visibility: visible;
            }}
            
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                color: white;
                font-size: 13px;
                white-space: nowrap;
                margin: 4px 0;
            }}
            
            .legend-dot {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
            }}
            
            .legend-dot.red {{ background: #d63384; }}
            .legend-dot.blue {{ background: #38A3D1; }}
            
            .books-panel {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                height: 60vh;
                background: rgba(255, 255, 255, 0.98);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-radius: 20px 20px 0 0;
                z-index: 2000;
                transform: translateY(100%);
                transition: transform 0.3s ease;
                overflow: hidden;
                box-shadow: 0 -4px 20px rgba(0,0,0,0.2);
            }}
            
            .books-panel.show {{
                transform: translateY(0);
            }}
            
            .books-panel-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 16px 20px;
                border-bottom: 1px solid rgba(0,0,0,0.1);
                background: white;
                position: sticky;
                top: 0;
            }}
            
            .books-panel-title {{
                font-size: 18px;
                font-weight: 600;
                color: #333;
            }}
            
            .books-panel-close {{
                width: 36px;
                height: 36px;
                border-radius: 50%;
                border: none;
                background: rgba(0,0,0,0.05);
                color: #666;
                font-size: 18px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .books-list {{
                padding: 16px 20px;
                overflow-y: auto;
                height: calc(100% - 70px);
            }}
            
            .book-item {{
                padding: 12px 0;
                border-bottom: 1px solid rgba(0,0,0,0.08);
            }}
            
            .book-title {{
                font-size: 16px;
                font-weight: 600;
                color: #1f77b4;
                margin-bottom: 4px;
            }}
            
            .book-author {{
                font-size: 14px;
                color: #666;
                margin-bottom: 6px;
            }}
            
            .book-details {{
                display: flex;
                gap: 16px;
                font-size: 12px;
                color: #888;
            }}
            
            .no-books {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                color: #666;
                background: #f5f5f5;
            }}
            
            .no-books-icon {{
                font-size: 48px;
                margin-bottom: 16px;
            }}
            
            @media (max-width: 480px) {{
                .top-title {{
                    font-size: 16px;
                }}
                
                .century-text {{
                    font-size: 24px;
                }}
                
                .slider-container {{
                    max-width: 200px;
                }}
            }}
            
            @media (orientation: landscape) and (max-height: 500px) {{
                .bottom-controls {{
                    padding: 8px 16px 12px;
                }}
                
                .century-text {{
                    font-size: 20px;
                }}
                
                .nav-btn {{
                    width: 40px;
                    height: 40px;
                }}
                
                .legend-btn {{
                    bottom: 100px;
                }}
                
                .legend-panel {{
                    bottom: 100px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="map-fullscreen">
            {folium_html if folium_html else '<div class="no-books"><div class="no-books-icon">📚</div><h2>No books found for this century</h2></div>'}
        </div>
        
        <div class="top-overlay">
            <span class="top-title">📚 Literary World Map</span>
        </div>
        
        <button class="legend-btn" onclick="toggleLegend()" aria-label="Toggle legend">
            <i class="fas fa-info"></i>
        </button>
        
        <div class="legend-panel" id="legendPanel">
            <div class="legend-item">
                <div class="legend-dot red"></div>
                <span>Story Setting</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot blue"></div>
                <span>Publication Location</span>
            </div>
        </div>
        
        <div class="bottom-controls">
            <div class="century-display">
                <span class="century-text">{century_display}</span>
            </div>
            <div class="nav-row">
                <button class="nav-btn" id="prevBtn" {'disabled' if not can_go_prev else ''} onclick="navigateCentury(-1)" aria-label="Previous century">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <div class="slider-container">
                    <input type="range" class="century-slider" id="centurySlider" 
                           min="0" max="{len(century_options) - 1}" 
                           value="{current_index}"
                           onchange="updateSlider(this.value)">
                </div>
                <button class="nav-btn" id="nextBtn" {'disabled' if not can_go_next else ''} onclick="navigateCentury(1)" aria-label="Next century">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            <button class="book-count-btn" onclick="toggleBooksPanel()">
                <i class="fas fa-book"></i>
                <span>{book_count} book{'s' if book_count != 1 else ''}</span>
            </button>
        </div>
        
        <div class="books-panel" id="booksPanel">
            <div class="books-panel-header">
                <span class="books-panel-title">Books from the {get_century_suffix(st.session_state.selected_century)}</span>
                <button class="books-panel-close" onclick="toggleBooksPanel()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="books-list">
                {books_list_html if books_list_html else '<p style="text-align:center;color:#888;padding:20px;">No books found</p>'}
            </div>
        </div>
        
        <script>
            const centuryOptions = {century_options};
            let legendVisible = false;
            let booksPanelVisible = false;
            
            function toggleLegend() {{
                legendVisible = !legendVisible;
                document.getElementById('legendPanel').classList.toggle('show', legendVisible);
            }}
            
            function toggleBooksPanel() {{
                booksPanelVisible = !booksPanelVisible;
                document.getElementById('booksPanel').classList.toggle('show', booksPanelVisible);
            }}
            
            function navigateCentury(direction) {{
                const slider = document.getElementById('centurySlider');
                let newValue = parseInt(slider.value) + direction;
                if (newValue >= 0 && newValue < centuryOptions.length) {{
                    slider.value = newValue;
                    sendCenturyUpdate(centuryOptions[newValue]);
                }}
            }}
            
            function updateSlider(value) {{
                const centuryValue = centuryOptions[parseInt(value)];
                sendCenturyUpdate(centuryValue);
            }}
            
            function sendCenturyUpdate(century) {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: century
                }}, '*');
            }}
            
            document.addEventListener('click', function(e) {{
                if (!e.target.closest('.legend-btn') && !e.target.closest('.legend-panel')) {{
                    legendVisible = false;
                    document.getElementById('legendPanel').classList.remove('show');
                }}
            }});
        </script>
    </body>
    </html>
    """

    component_value = components.html(full_page_html, height=800, scrolling=False)

    st.markdown("""
    <style>
        .stApp > header { display: none !important; }
        .main .block-container { 
            padding: 0 !important; 
            max-width: 100% !important; 
        }
        section[data-testid="stSidebar"] {
            background: rgba(255,255,255,0.98);
        }
        .desktop-nav { 
            display: block; 
            padding: 0 1rem;
        }
        iframe { height: 500px !important; }
        @media (max-width: 768px) {
            iframe { height: 60vh !important; max-height: 450px !important; }
            .desktop-nav {
                background: rgba(0,0,0,0.85);
                border-radius: 12px;
                padding: 12px 16px;
                margin: 8px;
            }
            .desktop-nav h3 { color: white !important; font-size: 16px !important; margin: 0 0 10px 0 !important; text-align: center; }
            .desktop-nav p { color: white !important; text-align: center; }
            .desktop-nav button {
                min-height: 48px !important;
                font-size: 16px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="desktop-nav">', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Century Navigation")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Previous", key="prev_century", help="Go to previous century"):
            if current_index > 0:
                st.session_state.selected_century = century_options[current_index - 1]
                st.rerun()
    with col2:
        st.markdown(f"<p style='text-align:center; font-size:1.2em;'><strong>{century_display}</strong></p>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ▶", key="next_century", help="Go to next century"):
            if current_index < len(century_options) - 1:
                st.session_state.selected_century = century_options[current_index + 1]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    import traceback
    error_details = traceback.format_exc()
    st.error(f"An error occurred: {str(e)}")
    st.error(f"Error details: {error_details}")
