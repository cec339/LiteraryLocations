import json
import streamlit as st
from utils.data_loader import (
    load_book_data,
    search_books,
    get_dataset_stats
)
from utils.map_utils import create_base_map_html
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Great Books World Map",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with open("styles/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if 'selected_century' not in st.session_state:
    st.session_state.selected_century = 20

query_params = st.query_params
if 'century' in query_params:
    try:
        requested_century = int(query_params['century'])
        if requested_century in list(range(-20, 0)) + list(range(1, 22)):
            st.session_state.selected_century = requested_century
    except (ValueError, TypeError):
        pass
if 'last_search_query' not in st.session_state:
    st.session_state.last_search_query = ""
if 'century_updated' not in st.session_state:
    st.session_state.century_updated = False

# Compute century book counts for the timeline
all_books = load_book_data()
century_counts = all_books.groupby('century').size().to_dict()
centuries_with_books = sorted(century_counts.keys())
century_data_json = json.dumps([{"c": int(c), "n": int(century_counts[c])} for c in centuries_with_books])

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
    is_search_mode = bool(search_query and search_results is not None and not search_results.empty)
    if is_search_mode:
        books_for_map = search_results
    else:
        books_for_map = all_books

    # Serialize books to JSON for client-side filtering
    books_json_list = []
    for _, bk in books_for_map.iterrows():
        loc_type = bk.get('location_type', 'primary')
        if loc_type == 'primary':
            loc_desc = "Primary Story Setting"
        elif loc_type == 'publication':
            loc_desc = "Publication Location (Fictional/Multiple Settings)"
        else:
            loc_desc = "Story Location"
        summary = str(bk.get('summary', ''))
        hist = str(bk.get('historical_context', ''))
        books_json_list.append({
            "title": str(bk['title']),
            "author": str(bk['author']),
            "year": int(bk['year']),
            "century": int(bk.get('century', 0)),
            "lat": float(bk['setting_latitude']),
            "lng": float(bk['setting_longitude']),
            "setting_name": str(bk['setting_name']),
            "location_type": loc_type,
            "location_desc": loc_desc,
            "summary": summary[:300] + ('...' if len(summary) > 300 else ''),
            "hist": hist[:300] + ('...' if len(hist) > 300 else ''),
        })
    # Escape </ to prevent breaking out of script tags
    books_json_str = json.dumps(books_json_list).replace("</", "<\\/")

    base_map_html = create_base_map_html()

    display_century = st.session_state.selected_century

    # Key centuries to show labels for
    label_centuries_set = set()
    if centuries_with_books:
        label_centuries_set.add(centuries_with_books[0])
        label_centuries_set.add(centuries_with_books[-1])
    for c in [-20, -10, -5, -1, 1, 5, 10, 15, 20, 21]:
        if c in century_counts:
            label_centuries_set.add(c)

    # Build CSS to inject into Folium's <head>
    inject_css = f"""
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            :root {{ --real-vh: 100vh; }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html, body {{
                width: 100vw;
                height: var(--real-vh);
                overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}

            .folium-map {{
                width: 100vw !important;
                height: var(--real-vh) !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
            }}

            /* ===== Floating Pills Timeline (Desktop) ===== */
            .timeline {{
                position: fixed;
                top: 0;
                left: 0;
                height: var(--real-vh);
                z-index: 10000;
                display: flex;
                flex-direction: column;
                pointer-events: none;
            }}

            .timeline-track {{
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 2px;
                padding: 12px 8px;
                overflow-y: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }}
            .timeline-track::-webkit-scrollbar {{ display: none; }}

            /* Pill buttons (key centuries) */
            .tl-pill {{
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 4px 10px;
                height: 28px;
                border-radius: 14px;
                background: rgba(20,20,30,0.7);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                cursor: pointer;
                pointer-events: auto;
                white-space: nowrap;
                transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .tl-pill:hover {{
                transform: translateX(2px);
                box-shadow: 0 4px 14px rgba(0,0,0,0.4);
                background: rgba(30,30,45,0.85);
            }}
            .tl-pill .tl-pill-label {{
                color: rgba(255,255,255,0.85);
                font-size: 11px;
                font-weight: 500;
                line-height: 1;
            }}
            .tl-pill.selected {{
                background: rgba(31,119,180,0.9);
                box-shadow: 0 0 12px rgba(31,119,180,0.5), 0 2px 8px rgba(0,0,0,0.3);
                border-color: rgba(31,119,180,0.6);
            }}
            .tl-pill.selected:hover {{
                background: rgba(31,119,180,0.95);
                box-shadow: 0 0 16px rgba(31,119,180,0.6), 0 4px 14px rgba(0,0,0,0.4);
            }}
            .tl-pill .tl-pill-label.selected {{
                color: white;
            }}
            .tl-pill .tl-badge {{
                display: none;
                font-size: 9px;
                color: white;
                background: rgba(255,255,255,0.25);
                padding: 1px 6px;
                border-radius: 8px;
                line-height: 1.2;
            }}
            .tl-pill.selected .tl-badge {{
                display: inline-block;
            }}

            /* Dot buttons (remaining centuries) */
            .tl-dot-wrap {{
                display: flex;
                align-items: center;
                justify-content: center;
                width: 28px;
                height: 16px;
                cursor: pointer;
                pointer-events: auto;
                margin-left: 2px;
            }}
            .tl-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: rgba(255,255,255,0.55);
                box-shadow: 0 1px 4px rgba(0,0,0,0.3);
                transition: transform 0.2s, background 0.2s;
            }}
            .tl-dot-wrap:hover .tl-dot {{
                transform: scale(1.4);
                background: rgba(31,119,180,0.8);
            }}
            .tl-dot-wrap.selected .tl-dot {{
                background: #1f77b4;
                box-shadow: 0 0 8px rgba(31,119,180,0.6);
                width: 12px;
                height: 12px;
            }}

            /* Era divider */
            .tl-divider {{
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-left: 2px;
                pointer-events: none;
            }}
            .tl-divider-line {{
                width: 24px;
                height: 1px;
                background: rgba(255,255,255,0.25);
            }}

            /* Hover tooltip */
            .timeline-info {{
                position: fixed;
                display: none;
                align-items: center;
                gap: 8px;
                padding: 6px 12px;
                background: rgba(30,30,30,0.92);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-radius: 8px;
                z-index: 10001;
                pointer-events: none;
                white-space: nowrap;
                box-shadow: 0 2px 10px rgba(0,0,0,0.4);
            }}
            .timeline-info.show {{
                display: flex;
            }}
            .tl-century {{
                color: white;
                font-size: 13px;
                font-weight: 600;
            }}
            .tl-count {{
                background: rgba(31,119,180,0.9);
                color: white;
                font-size: 11px;
                padding: 2px 8px;
                border-radius: 10px;
            }}

            /* Legend button (floating circle, bottom-left) */
            .tl-legend-btn {{
                position: fixed;
                bottom: 16px;
                right: 16px;
                width: 34px;
                height: 34px;
                border-radius: 50%;
                border: 1px solid rgba(255,255,255,0.2);
                background: rgba(20,20,30,0.7);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                color: rgba(255,255,255,0.85);
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s, box-shadow 0.2s;
                z-index: 10000;
                pointer-events: auto;
            }}
            .tl-legend-btn:hover {{
                background: rgba(30,30,45,0.85);
                box-shadow: 0 4px 14px rgba(0,0,0,0.4);
            }}

            /* Legend popup */
            .legend {{
                display: none;
                position: fixed;
                bottom: 56px;
                right: 16px;
                background: rgba(20,20,30,0.85);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-radius: 10px;
                padding: 10px 14px;
                z-index: 10001;
                box-shadow: 0 4px 16px rgba(0,0,0,0.4);
                border: 1px solid rgba(255,255,255,0.1);
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

            /* ===== Splash Overlay ===== */
            .splash {{
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: var(--real-vh);
                z-index: 20000;
                background: radial-gradient(ellipse at center, rgba(15,15,30,0.92) 0%, rgba(5,5,15,0.97) 100%);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                opacity: 1;
                transition: opacity 0.8s ease-out;
            }}
            .splash.fade-out {{
                opacity: 0;
                pointer-events: none;
            }}
            .splash-content {{
                text-align: center;
                opacity: 0;
                transform: translateY(20px);
                animation: splashIn 0.6s ease-out 0.2s forwards;
            }}
            @keyframes splashIn {{
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .splash-title {{
                font-family: Georgia, 'Times New Roman', serif;
                font-size: 48px;
                font-weight: 700;
                color: rgba(255,255,255,0.95);
                margin-bottom: 12px;
                letter-spacing: -0.5px;
            }}
            .splash-subtitle {{
                font-size: 18px;
                color: rgba(255,255,255,0.55);
                font-weight: 400;
            }}
            .splash-hint {{
                margin-top: 32px;
                font-size: 14px;
                color: rgba(255,255,255,0.3);
                opacity: 0;
                animation: splashIn 0.4s ease-out 1.0s forwards;
            }}

            /* ===== Coach Tour ===== */
            .coach-spotlight {{
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: var(--real-vh);
                z-index: 19000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.4s ease;
            }}
            .coach-spotlight.visible {{
                opacity: 1;
            }}
            .coach-spotlight.fade-out {{
                opacity: 0;
            }}
            .coach-tooltip {{
                position: fixed;
                z-index: 19001;
                background: rgba(20,20,30,0.92);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border-radius: 12px;
                padding: 16px 20px;
                max-width: 280px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.5);
                border: 1px solid rgba(255,255,255,0.12);
                opacity: 0;
                transform: translateY(8px);
                transition: opacity 0.35s ease, transform 0.35s ease;
                pointer-events: auto;
            }}
            .coach-tooltip.visible {{
                opacity: 1;
                transform: translateY(0);
            }}
            .coach-tooltip.fade-out {{
                opacity: 0;
                transform: translateY(8px);
                pointer-events: none;
            }}
            .coach-arrow {{
                position: absolute;
                width: 12px;
                height: 12px;
                background: rgba(20,20,30,0.92);
                transform: rotate(45deg);
                border: 1px solid rgba(255,255,255,0.12);
            }}
            .coach-arrow.arrow-up {{
                top: -7px;
                left: 24px;
                border-right: none;
                border-bottom: none;
            }}
            .coach-arrow.arrow-down {{
                bottom: -7px;
                left: 24px;
                border-left: none;
                border-top: none;
            }}
            .coach-arrow.arrow-left {{
                left: -7px;
                top: 16px;
                border-top: none;
                border-right: none;
            }}
            .coach-arrow.arrow-right {{
                right: -7px;
                top: 16px;
                border-bottom: none;
                border-left: none;
            }}
            .coach-title {{
                color: rgba(255,255,255,0.95);
                font-size: 15px;
                font-weight: 600;
                margin-bottom: 6px;
            }}
            .coach-text {{
                color: rgba(255,255,255,0.65);
                font-size: 13px;
                line-height: 1.4;
                margin-bottom: 14px;
            }}
            .coach-footer {{
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            .coach-step-indicator {{
                color: rgba(255,255,255,0.35);
                font-size: 11px;
            }}
            .coach-actions {{
                display: flex;
                gap: 8px;
            }}
            .coach-btn {{
                padding: 6px 16px;
                border-radius: 6px;
                border: none;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                background: rgba(31,119,180,0.9);
                color: white;
                transition: background 0.2s;
            }}
            .coach-btn:hover {{
                background: rgba(31,119,180,1);
            }}
            .coach-skip {{
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid rgba(255,255,255,0.2);
                background: transparent;
                color: rgba(255,255,255,0.6);
                font-size: 12px;
                cursor: pointer;
                transition: border-color 0.2s, color 0.2s;
            }}
            .coach-skip:hover {{
                border-color: rgba(255,255,255,0.4);
                color: rgba(255,255,255,0.85);
            }}

            /* ===== Mobile: Horizontal Bottom Bar ===== */
            @media (max-width: 768px) {{
                .timeline {{
                    top: auto;
                    bottom: 56px;
                    left: 0;
                    height: auto;
                    width: 100vw;
                    flex-direction: row;
                    pointer-events: auto;
                }}
                .timeline-track {{
                    flex-direction: row;
                    align-items: center;
                    gap: 6px;
                    padding: 8px 10px;
                    padding-bottom: calc(8px + env(safe-area-inset-bottom));
                    height: 66px;
                    overflow-x: auto;
                    overflow-y: hidden;
                    background: transparent;
                    backdrop-filter: none;
                    -webkit-backdrop-filter: none;
                    justify-content: flex-start;
                }}
                .tl-pill {{
                    min-width: 44px;
                    min-height: 48px;
                    height: 48px;
                    justify-content: center;
                    flex-shrink: 0;
                }}
                .tl-pill:hover {{
                    transform: none;
                }}
                .tl-dot-wrap {{
                    width: 28px;
                    height: 66px;
                    min-width: 28px;
                    flex-shrink: 0;
                    margin-left: 0;
                }}
                .tl-divider {{
                    height: auto;
                    width: 1px;
                    min-width: 1px;
                    margin-left: 0;
                    flex-shrink: 0;
                    padding: 4px 0;
                }}
                .tl-divider-line {{
                    width: 1px;
                    height: 24px;
                }}
                .timeline-info {{ display: none !important; }}
                .tl-legend-btn {{
                    bottom: 130px !important;
                    right: 12px !important;
                }}
                .legend {{
                    bottom: 170px !important;
                    right: 12px !important;
                }}
                .coach-tooltip {{ max-width: 240px; }}
                .splash-title {{ font-size: 34px; }}
                .splash-subtitle {{ font-size: 16px; }}
            }}

            @media (max-height: 500px) and (min-width: 769px) {{
                .tl-pill {{ height: 22px; padding: 2px 8px; }}
                .tl-pill .tl-pill-label {{ font-size: 9px; }}
                .tl-dot-wrap {{ height: 12px; }}
                .tl-divider {{ height: 8px; }}
            }}
        </style>
    """

    # Build overlay HTML + JS to inject before </body>
    inject_body = f"""
        <div id="splash" class="splash">
            <div class="splash-content">
                <div class="splash-title">4,000 Years of Great Books</div>
                <div class="splash-subtitle">Explore the world's greatest works on the map</div>
                <div class="splash-hint">Tap anywhere to begin</div>
            </div>
        </div>
        <script>
            // Immediately hide splash if already shown this session
            try {{
                if (window.parent.sessionStorage.getItem('litloc_splash_shown')) {{
                    document.getElementById('splash').style.display = 'none';
                }}
            }} catch(e) {{}}
        </script>

        <div id="timeline" class="timeline">
            <div class="timeline-track" id="timeline-track"></div>
        </div>

        <button class="tl-legend-btn" id="legend-btn" onclick="toggleLegend()" title="Legend">i</button>

        <div class="timeline-info" id="timeline-info">
            <span class="tl-century" id="tl-century"></span>
            <span class="tl-count" id="tl-count"></span>
        </div>

        <div id="legend" class="legend">
            <div class="legend-item"><div class="legend-dot red"></div><span>Story Setting</span></div>
            <div class="legend-item"><div class="legend-dot blue"></div><span>Publication Location</span></div>
            <div style="border-top: 1px solid rgba(255,255,255,0.15); margin: 8px 0;"></div>
            <div style="color: rgba(255,255,255,0.55); font-size: 10px; line-height: 1.4; max-width: 200px;">
                Most books drawn from thegreatestbooks.org top 500 list. Centuries without a top-500 entry are filled with at least one notable work.
            </div>
        </div>

        <script>
            var ALL_BOOKS = {books_json_str};
            var IS_SEARCH_MODE = {'true' if is_search_mode else 'false'};
            var CENTURY_DATA = {century_data_json};
            var SELECTED_CENTURY = {int(st.session_state.selected_century)};
            var LABEL_CENTURIES = {json.dumps(sorted(label_centuries_set))};

            // Get the REAL visible viewport height (not the iframe's 2000px)
            function getVisibleHeight() {{
                // Collect all candidate heights
                var candidates = [];
                // 1. visualViewport is the most accurate on mobile
                if (window.visualViewport) candidates.push(window.visualViewport.height);
                // 2. Parent's visualViewport
                try {{
                    if (window.parent && window.parent !== window && window.parent.visualViewport) {{
                        candidates.push(window.parent.visualViewport.height);
                    }}
                }} catch(e) {{}}
                // 3. Parent's innerHeight
                try {{
                    if (window.parent && window.parent !== window) {{
                        candidates.push(window.parent.innerHeight);
                    }}
                }} catch(e) {{}}
                // 4. Parent's documentElement.clientHeight (excludes scrollbar)
                try {{
                    if (window.parent && window.parent !== window) {{
                        candidates.push(window.parent.document.documentElement.clientHeight);
                    }}
                }} catch(e) {{}}
                // 5. Screen as last resort
                candidates.push(screen.availHeight || screen.height);
                // Pick the smallest reasonable value (> 300px) — that's the actual visible area
                var h = window.innerHeight;
                for (var i = 0; i < candidates.length; i++) {{
                    if (candidates[i] > 300 && candidates[i] < h) {{
                        h = candidates[i];
                    }}
                }}
                return h;
            }}

            // Set the CSS variable immediately so CSS heights are correct from the start
            document.documentElement.style.setProperty('--real-vh', getVisibleHeight() + 'px');

            var _leafletMap = null;
            var _clusterGroup = null;
            var _isFirstLoad = true;

            function toggleLegend() {{
                document.getElementById('legend').classList.toggle('show');
            }}

            function formatCentury(c) {{
                if (c < 0) return Math.abs(c) + ' BC';
                if (c === 1) return '1 AD';
                var s = String(c);
                var last2 = c % 100;
                var last1 = c % 10;
                var suffix = 'th';
                if (last2 >= 11 && last2 <= 13) suffix = 'th';
                else if (last1 === 1) suffix = 'st';
                else if (last1 === 2) suffix = 'nd';
                else if (last1 === 3) suffix = 'rd';
                return s + suffix;
            }}

            function formatCenturyLong(c) {{
                if (c < 0) return Math.abs(c) + ' BC';
                if (c === 1) return '1st Century';
                return formatCentury(c) + ' Century';
            }}

            function getLeafletMap() {{
                if (_leafletMap) return _leafletMap;
                for (var key in window) {{
                    try {{
                        if (window[key] instanceof L.Map) {{
                            _leafletMap = window[key];
                            return _leafletMap;
                        }}
                    }} catch(e) {{}}
                }}
                // Fallback: scan leaflet containers
                var containers = document.querySelectorAll('.leaflet-container');
                for (var i = 0; i < containers.length; i++) {{
                    if (containers[i]._leaflet_map) {{
                        _leafletMap = containers[i]._leaflet_map;
                        return _leafletMap;
                    }}
                }}
                // Folium stores map refs as map_<hash>
                for (var key in window) {{
                    if (key.indexOf('map_') === 0 && window[key] && typeof window[key].addLayer === 'function') {{
                        _leafletMap = window[key];
                        return _leafletMap;
                    }}
                }}
                return null;
            }}

            function getMarkerIcon(locationType) {{
                var color = locationType === 'publication' ? 'blue' : 'red';
                return L.AwesomeMarkers.icon({{
                    icon: 'book',
                    prefix: 'fa',
                    markerColor: color
                }});
            }}

            function escapeHtml(s) {{
                var div = document.createElement('div');
                div.appendChild(document.createTextNode(s));
                return div.innerHTML;
            }}

            function createPopupHtml(book) {{
                var yearStr = Math.abs(book.year) + (book.year < 0 ? ' BCE' : '');
                var centuryStr = formatCentury(book.century);
                if (book.century < 0) centuryStr += ' Century BCE';
                else centuryStr += ' Century';
                return '<div style="width:280px;font-family:Arial,sans-serif;">' +
                    '<h4 style="margin-bottom:10px;color:#2E4057;">' + escapeHtml(book.title) + '</h4>' +
                    '<p><b>Author:</b> ' + escapeHtml(book.author) + '</p>' +
                    '<p><b>Year:</b> ' + yearStr + '</p>' +
                    '<p><b>Century:</b> ' + centuryStr + '</p>' +
                    '<p><b>Location:</b> ' + escapeHtml(book.setting_name) + '</p>' +
                    '<p><b>Type:</b> ' + escapeHtml(book.location_desc) + '</p>' +
                    '<p><b>Summary:</b> ' + escapeHtml(book.summary) + '</p>' +
                    '<p><b>Historical Context:</b> ' + escapeHtml(book.hist) + '</p>' +
                    '</div>';
            }}

            function showCentury(century) {{
                var map = getLeafletMap();
                if (!map) return;
                if (_clusterGroup) {{
                    _clusterGroup.clearLayers();
                }} else {{
                    _clusterGroup = L.markerClusterGroup();
                    map.addLayer(_clusterGroup);
                }}
                // Remove any existing Folium-added cluster layers
                map.eachLayer(function(layer) {{
                    if (layer !== _clusterGroup && layer._group && layer.getAllChildMarkers) {{
                        map.removeLayer(layer);
                    }}
                }});

                var books = IS_SEARCH_MODE ? ALL_BOOKS : ALL_BOOKS.filter(function(b) {{ return b.century === century; }});
                for (var i = 0; i < books.length; i++) {{
                    var b = books[i];
                    var marker = L.marker([b.lat, b.lng], {{ icon: getMarkerIcon(b.location_type) }});
                    marker.bindPopup(createPopupHtml(b), {{ maxWidth: 320 }});
                    _clusterGroup.addLayer(marker);
                }}

                // Smart viewport: reframe only when most markers are off-screen
                if (books.length > 0) {{
                    var bounds = L.latLngBounds(books.map(function(b) {{ return [b.lat, b.lng]; }}));
                    var _mob = window.innerWidth < 768;
                    var _pad = _mob ? [10, 10] : [40, 40];
                    var _maxZ = _mob ? 10 : 6;
                    if (_isFirstLoad) {{
                        map.fitBounds(bounds, {{ padding: _pad, maxZoom: _maxZ }});
                        // On tall mobile screens, fitBounds optimizes for width leaving grey
                        // above/below. Zoom in 2 levels so the map fills the vertical space.
                        if (_mob) {{
                            var z = map.getZoom();
                            map.setZoom(Math.min(z + 2, _maxZ));
                        }}
                        _isFirstLoad = false;
                    }} else {{
                        var viewBounds = map.getBounds();
                        var visibleCount = 0;
                        for (var j = 0; j < books.length; j++) {{
                            if (viewBounds.contains(L.latLng(books[j].lat, books[j].lng))) visibleCount++;
                        }}
                        if (visibleCount < books.length * 0.25) {{
                            map.flyToBounds(bounds, {{ padding: _pad, maxZoom: _maxZ, duration: 0.8 }});
                        }}
                    }}
                }}

                SELECTED_CENTURY = century;
            }}

            function updateTimelineSelection(c) {{
                var track = document.getElementById('timeline-track');
                var items = track.querySelectorAll('[data-century]');
                for (var i = 0; i < items.length; i++) {{
                    var el = items[i];
                    var elC = parseInt(el.getAttribute('data-century'));
                    if (elC === c) {{
                        el.classList.add('selected');
                        var lbl = el.querySelector('.tl-pill-label');
                        if (lbl) lbl.classList.add('selected');
                    }} else {{
                        el.classList.remove('selected');
                        var lbl2 = el.querySelector('.tl-pill-label');
                        if (lbl2) lbl2.classList.remove('selected');
                    }}
                }}
                // Mobile: scroll selected into view
                if (isMobile()) {{
                    var sel = track.querySelector('.selected');
                    if (sel) sel.scrollIntoView({{ inline: 'center', behavior: 'smooth' }});
                }}
            }}

            function navigateToCentury(c) {{
                showCentury(c);
                updateTimelineSelection(c);
            }}

            function isMobile() {{
                return window.innerWidth <= 768;
            }}

            function buildTimeline() {{
                var track = document.getElementById('timeline-track');
                track.innerHTML = '';

                var lastWasNeg = false;
                var firstPos = true;
                var infoEl = document.getElementById('timeline-info');

                for (var i = 0; i < CENTURY_DATA.length; i++) {{
                    var item = CENTURY_DATA[i];
                    var c = item.c;
                    var n = item.n;

                    if (lastWasNeg && c > 0 && firstPos) {{
                        var divider = document.createElement('div');
                        divider.className = 'tl-divider';
                        divider.innerHTML = '<div class="tl-divider-line"></div>';
                        track.appendChild(divider);
                        firstPos = false;
                    }}
                    if (c < 0) lastWasNeg = true;

                    var isPill = LABEL_CENTURIES.indexOf(c) !== -1;

                    if (isPill) {{
                        var pill = document.createElement('div');
                        pill.className = 'tl-pill' + (c === SELECTED_CENTURY ? ' selected' : '');
                        pill.setAttribute('data-century', c);
                        pill.setAttribute('data-count', n);

                        var lbl = document.createElement('span');
                        lbl.className = 'tl-pill-label' + (c === SELECTED_CENTURY ? ' selected' : '');
                        lbl.textContent = formatCentury(c);
                        pill.appendChild(lbl);

                        var badge = document.createElement('span');
                        badge.className = 'tl-badge';
                        badge.textContent = n;
                        pill.appendChild(badge);

                        pill.addEventListener('click', (function(century) {{
                            return function() {{ navigateToCentury(century); }};
                        }})(c));

                        pill.addEventListener('mouseenter', (function(century, count) {{
                            return function(e) {{
                                if (isMobile()) return;
                                var rect = e.currentTarget.getBoundingClientRect();
                                document.getElementById('tl-century').textContent = formatCenturyLong(century);
                                var bw = count === 1 ? 'book' : 'books';
                                document.getElementById('tl-count').textContent = count + ' ' + bw;
                                infoEl.style.top = (rect.top + rect.height / 2 - 16) + 'px';
                                infoEl.style.left = (rect.right + 8) + 'px';
                                infoEl.classList.add('show');
                            }};
                        }})(c, n));
                        pill.addEventListener('mouseleave', function() {{
                            infoEl.classList.remove('show');
                        }});

                        track.appendChild(pill);
                    }} else {{
                        var wrap = document.createElement('div');
                        wrap.className = 'tl-dot-wrap' + (c === SELECTED_CENTURY ? ' selected' : '');
                        wrap.setAttribute('data-century', c);
                        wrap.setAttribute('data-count', n);

                        var dot = document.createElement('div');
                        dot.className = 'tl-dot';
                        wrap.appendChild(dot);

                        wrap.addEventListener('click', (function(century) {{
                            return function() {{ navigateToCentury(century); }};
                        }})(c));

                        wrap.addEventListener('mouseenter', (function(century, count) {{
                            return function(e) {{
                                if (isMobile()) return;
                                var rect = e.currentTarget.getBoundingClientRect();
                                document.getElementById('tl-century').textContent = formatCenturyLong(century);
                                var bw = count === 1 ? 'book' : 'books';
                                document.getElementById('tl-count').textContent = count + ' ' + bw;
                                infoEl.style.top = (rect.top + rect.height / 2 - 16) + 'px';
                                infoEl.style.left = (rect.right + 8) + 'px';
                                infoEl.classList.add('show');
                            }};
                        }})(c, n));
                        wrap.addEventListener('mouseleave', function() {{
                            infoEl.classList.remove('show');
                        }});

                        track.appendChild(wrap);
                    }}
                }}

                if (isMobile()) {{
                    setTimeout(function() {{
                        var sel = track.querySelector('.selected');
                        if (sel) sel.scrollIntoView({{ inline: 'center', behavior: 'auto' }});
                    }}, 50);
                }}
            }}

            buildTimeline();

            var _resizeTimer;
            window.addEventListener('resize', function() {{
                clearTimeout(_resizeTimer);
                _resizeTimer = setTimeout(function() {{
                    buildTimeline();
                }}, 200);
            }});

            // Coach Tour (once per session via parent sessionStorage)
            var CoachTour = (function() {{
                var steps = [];
                var currentStep = 0;
                var spotlightEl = null;
                var tooltipEl = null;
                var autoDismissTimer = null;
                var resizeTimer = null;

                function _isMobile() {{
                    return window.innerWidth <= 768;
                }}

                function buildSteps() {{
                    steps = [
                        {{
                            target: null,
                            title: 'Tap a pin to explore a book',
                            text: 'Each dot is a great work. Tap to see details.',
                            position: 'below'
                        }},
                        {{
                            target: '#timeline',
                            title: 'Travel through 4,000 years',
                            text: 'Jump between centuries using the timeline.',
                            desktopPos: 'right',
                            mobilePos: 'above'
                        }}
                    ];
                    if (!_isMobile()) {{
                        steps.push({{
                            target: '#legend-btn',
                            title: 'What do the colors mean?',
                            text: 'Tap info to see the legend.',
                            position: 'above-left'
                        }});
                    }}
                }}

                function createElements() {{
                    spotlightEl = document.createElement('div');
                    spotlightEl.className = 'coach-spotlight';
                    document.body.appendChild(spotlightEl);

                    tooltipEl = document.createElement('div');
                    tooltipEl.className = 'coach-tooltip';
                    document.body.appendChild(tooltipEl);

                }}

                function showStep(idx) {{
                    if (idx < 0 || idx >= steps.length) {{ dismiss(); return; }}
                    currentStep = idx;
                    var step = steps[idx];

                    // Determine cutout rect
                    var rect;
                    if (step.target) {{
                        var el = document.querySelector(step.target);
                        if (el) {{
                            rect = el.getBoundingClientRect();
                            // Add padding around target
                            var pad = 8;
                            rect = {{
                                left: rect.left - pad,
                                top: rect.top - pad,
                                right: rect.right + pad,
                                bottom: rect.bottom + pad,
                                width: rect.width + pad * 2,
                                height: rect.height + pad * 2
                            }};
                        }} else {{
                            rect = _centerRect();
                        }}
                    }} else {{
                        rect = _centerRect();
                    }}

                    // Spotlight with box-shadow cutout
                    var rx = Math.min(rect.width, rect.height) > 60 ? 12 : 8;
                    var _vh = getVisibleHeight() + 'px';
                    spotlightEl.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:' + _vh + ';z-index:19000;pointer-events:none;opacity:0;transition:opacity 0.4s ease;';
                    spotlightEl.innerHTML = '<svg style="position:absolute;top:0;left:0;width:100%;height:100%"><defs><mask id="coach-mask"><rect width="100%" height="100%" fill="white"/><rect x="' + rect.left + '" y="' + rect.top + '" width="' + rect.width + '" height="' + rect.height + '" rx="' + rx + '" fill="black"/></mask></defs><rect width="100%" height="100%" fill="rgba(5,5,15,0.75)" mask="url(#coach-mask)"/></svg>';
                    spotlightEl.className = 'coach-spotlight';
                    void spotlightEl.offsetWidth;
                    spotlightEl.classList.add('visible');

                    // Tooltip content
                    var pos = step.position || (_isMobile() ? step.mobilePos : step.desktopPos) || 'below';
                    var isLast = idx === steps.length - 1;
                    var arrowClass = _arrowClass(pos);

                    tooltipEl.innerHTML =
                        '<div class="coach-arrow ' + arrowClass + '"></div>' +
                        '<div class="coach-title">' + step.title + '</div>' +
                        '<div class="coach-text">' + step.text + '</div>' +
                        '<div class="coach-footer">' +
                            '<span class="coach-step-indicator">' + (idx + 1) + ' of ' + steps.length + '</span>' +
                            '<div class="coach-actions">' +
                                '<button class="coach-skip" id="coach-skip-btn">Skip</button>' +
                                '<button class="coach-btn" id="coach-next-btn">' + (isLast ? 'Got it!' : 'Next') + '</button>' +
                            '</div>' +
                        '</div>';

                    positionTooltip(rect, pos);
                    tooltipEl.className = 'coach-tooltip';
                    void tooltipEl.offsetWidth;
                    tooltipEl.classList.add('visible');

                    document.getElementById('coach-next-btn').addEventListener('click', advance);
                    document.getElementById('coach-skip-btn').addEventListener('click', dismiss);

                    // Auto-dismiss after 15s
                    clearTimeout(autoDismissTimer);
                    autoDismissTimer = setTimeout(dismiss, 15000);
                }}

                function _centerRect() {{
                    var cw = window.innerWidth;
                    var ch = getVisibleHeight();
                    var size = Math.min(cw, ch) * 0.25;
                    return {{
                        left: (cw - size) / 2,
                        top: (ch - size) / 2,
                        width: size,
                        height: size,
                        right: (cw + size) / 2,
                        bottom: (ch + size) / 2
                    }};
                }}

                function _arrowClass(pos) {{
                    if (pos === 'below') return 'arrow-up';
                    if (pos === 'above' || pos === 'above-left') return 'arrow-down';
                    if (pos === 'right') return 'arrow-left';
                    if (pos === 'left') return 'arrow-right';
                    return 'arrow-up';
                }}

                function positionTooltip(rect, pos) {{
                    var gap = 14;
                    var tw = 280;
                    if (_isMobile()) tw = 240;

                    tooltipEl.style.width = tw + 'px';

                    // Reset positioning
                    tooltipEl.style.top = '';
                    tooltipEl.style.bottom = '';
                    tooltipEl.style.left = '';
                    tooltipEl.style.right = '';

                    if (pos === 'below') {{
                        tooltipEl.style.left = Math.max(8, Math.min(rect.left, window.innerWidth - tw - 8)) + 'px';
                        tooltipEl.style.top = (rect.bottom + gap) + 'px';
                    }} else if (pos === 'above') {{
                        tooltipEl.style.left = Math.max(8, Math.min(rect.left, window.innerWidth - tw - 8)) + 'px';
                        tooltipEl.style.top = Math.max(8, rect.top - gap - 150) + 'px';
                    }} else if (pos === 'above-left') {{
                        tooltipEl.style.left = Math.max(8, rect.right - tw) + 'px';
                        tooltipEl.style.top = Math.max(8, rect.top - gap - 150) + 'px';
                        // Adjust arrow to right side
                        var arrow = tooltipEl.querySelector('.coach-arrow');
                        if (arrow) {{ arrow.style.left = 'auto'; arrow.style.right = '24px'; }}
                    }} else if (pos === 'right') {{
                        tooltipEl.style.left = (rect.right + gap) + 'px';
                        tooltipEl.style.top = rect.top + 'px';
                    }}
                }}

                function advance() {{
                    clearTimeout(autoDismissTimer);
                    if (currentStep + 1 >= steps.length) {{
                        dismiss();
                    }} else {{
                        tooltipEl.classList.remove('visible');
                        tooltipEl.classList.add('fade-out');
                        setTimeout(function() {{
                            showStep(currentStep + 1);
                        }}, 300);
                    }}
                }}

                function dismiss() {{
                    clearTimeout(autoDismissTimer);
                    spotlightEl.classList.remove('visible');
                    spotlightEl.classList.add('fade-out');
                    tooltipEl.classList.remove('visible');
                    tooltipEl.classList.add('fade-out');
                    setTimeout(function() {{
                        if (spotlightEl.parentNode) spotlightEl.parentNode.removeChild(spotlightEl);
                        if (tooltipEl.parentNode) tooltipEl.parentNode.removeChild(tooltipEl);
                    }}, 500);
                    try {{
                        window.parent.sessionStorage.setItem('litloc_tour_shown', '1');
                    }} catch(e) {{}}
                    window.removeEventListener('resize', _onResize);
                    var _map = getLeafletMap();
                    if (_map) _map.invalidateSize();
                }}

                function _onResize() {{
                    clearTimeout(resizeTimer);
                    resizeTimer = setTimeout(function() {{
                        if (spotlightEl && spotlightEl.parentNode) {{
                            showStep(currentStep);
                        }}
                    }}, 200);
                }}

                function start() {{
                    try {{
                        if (window.parent.sessionStorage.getItem('litloc_tour_shown')) return;
                        // Mark as shown immediately so page reloads don't restart the tour
                        window.parent.sessionStorage.setItem('litloc_tour_shown', '1');
                    }} catch(e) {{}}
                    buildSteps();
                    createElements();
                    showStep(0);
                    window.addEventListener('resize', _onResize);
                }}

                return {{ start: start }};
            }})();

            // Wait for Leaflet map to be ready, then init markers
            (function() {{
                var attempts = 0;
                var maxAttempts = 50; // 5 seconds at 100ms intervals
                var timer = setInterval(function() {{
                    attempts++;
                    var map = getLeafletMap();
                    if (map) {{
                        clearInterval(timer);
                        // Remove the empty MarkerCluster Folium added
                        map.eachLayer(function(layer) {{
                            if (layer._group || (layer.getAllChildMarkers && typeof layer.getAllChildMarkers === 'function')) {{
                                map.removeLayer(layer);
                            }}
                        }});
                        function forceMapSize() {{
                            var h = getVisibleHeight();
                            // Set CSS variable so all elements (map, timeline, spotlight) use real height
                            document.documentElement.style.setProperty('--real-vh', h + 'px');
                            var mapEl = map.getContainer();
                            if (mapEl) {{
                                mapEl.style.height = h + 'px';
                                mapEl.style.width = '100%';
                            }}
                            document.body.style.height = h + 'px';
                            document.documentElement.style.height = h + 'px';
                            map.invalidateSize();
                        }}
                        forceMapSize();
                        window.addEventListener('resize', function() {{
                            forceMapSize();
                        }});
                        showCentury(SELECTED_CENTURY);
                        // Second pass: after the browser has laid out the iframe fully,
                        // re-force size and re-fit so mobile doesn't show a tiny globe
                        setTimeout(function() {{
                            forceMapSize();
                            // Re-fit to current markers
                            var books = ALL_BOOKS.filter(function(b) {{ return b.century === SELECTED_CENTURY; }});
                            if (books.length > 0) {{
                                var bounds = L.latLngBounds(books.map(function(b) {{ return [b.lat, b.lng]; }}));
                                var _mob = window.innerWidth < 768;
                                map.fitBounds(bounds, {{ padding: _mob ? [10, 10] : [40, 40], maxZoom: _mob ? 10 : 6 }});
                                if (_mob) map.setZoom(Math.min(map.getZoom() + 2, 10));
                            }}
                            // Show splash, then launch coach tour after dismiss
                            setTimeout(function() {{
                                showSplashThenTour();
                            }}, 300);
                        }}, 300);
                    }} else if (attempts >= maxAttempts) {{
                        clearInterval(timer);
                    }}
                }}, 100);
            }})();

            // Splash overlay — already visible from HTML if not previously shown
            function showSplashThenTour() {{
                var splash = document.getElementById('splash');
                // If splash is hidden (already shown this session), go straight to tour
                if (!splash || splash.style.display === 'none') {{
                    CoachTour.start();
                    return;
                }}
                // Splash is visible — wire up dismiss
                function dismissSplash() {{
                    splash.classList.add('fade-out');
                    setTimeout(function() {{
                        splash.style.display = 'none';
                        CoachTour.start();
                    }}, 850);
                    splash.removeEventListener('click', dismissSplash);
                }}
                splash.addEventListener('click', dismissSplash);
                setTimeout(dismissSplash, 8000);
                try {{
                    window.parent.sessionStorage.setItem('litloc_splash_shown', '1');
                }} catch(e) {{}}
            }}
        </script>
    """

    # Inject CSS into <head> and overlay HTML+JS before </body> of the Folium base map
    map_only_html = base_map_html.replace('</head>', inject_css + '</head>').replace('</body>', inject_body + '</body>')

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
            height: 100dvh !important;
            z-index: 1 !important;
            padding: 0 !important;
            margin: 0 !important;
            pointer-events: auto;
        }}

        iframe {{
            width: 100vw !important;
            height: 100vh !important;
            height: 100dvh !important;
            border: none !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            pointer-events: auto;
        }}

        /* Hide default Streamlit padding */
        section[data-testid="stMain"] > div {{
            padding-bottom: 0 !important;
            padding-top: 0 !important;
        }}

        section[data-testid="stMain"] {{
            height: 100vh !important;
            height: 100dvh !important;
            overflow: hidden !important;
        }}

        div[data-testid="stMainBlockContainer"] {{
            height: 100vh !important;
            height: 100dvh !important;
            padding: 0 !important;
            max-width: none !important;
        }}

        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {{
            height: 100vh !important;
            height: 100dvh !important;
            position: relative !important;
        }}

        /* Hide sidebar on mobile */
        @media (max-width: 768px) {{
            section[data-testid="stSidebar"] {{
                display: none !important;
            }}
            button[data-testid="stSidebarCollapsedControl"] {{
                display: none !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

    components.html(map_only_html, height=2000, scrolling=False)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check the data files and try again.")
