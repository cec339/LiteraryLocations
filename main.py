import json
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

    literary_map = None
    folium_html = ""
    if not filtered_books.empty:
        literary_map = create_literature_map(filtered_books)
        if literary_map:
            folium_html = literary_map._repr_html_()
            # Move zoom controls to top-right so timeline doesn't cover them
            folium_html = folium_html.replace('&lt;/head&gt;', '&lt;style&gt;.leaflet-top.leaflet-left{left:auto!important;right:10px!important;}&lt;/style&gt;&lt;/head&gt;')

    book_count_text = f"{book_count} book" + ("s" if book_count != 1 else "")

    # Key centuries to show labels for
    label_centuries_set = set()
    if centuries_with_books:
        label_centuries_set.add(centuries_with_books[0])
        label_centuries_set.add(centuries_with_books[-1])
    for c in [-20, -10, -5, -1, 1, 5, 10, 15, 20, 21]:
        if c in century_counts:
            label_centuries_set.add(c)

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

            /* ===== Floating Pills Timeline (Desktop) ===== */
            .timeline {{
                position: fixed;
                top: 0;
                left: 0;
                height: 100vh;
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
                width: 100vw; height: 100vh;
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
            .splash-tips {{
                list-style: none;
                padding: 0;
                margin: 28px 0 0 0;
                text-align: left;
                display: inline-block;
            }}
            .splash-tips li {{
                color: rgba(255,255,255,0.7);
                font-size: 16px;
                margin: 10px 0;
                opacity: 0;
                transform: translateY(10px);
                animation: splashIn 0.4s ease-out forwards;
            }}
            .splash-tips li:nth-child(1) {{ animation-delay: 0.5s; }}
            .splash-tips li:nth-child(2) {{ animation-delay: 0.7s; }}
            .splash-tips li:nth-child(3) {{ animation-delay: 0.9s; }}
            .splash-tips .tip-icon {{
                display: inline-block;
                width: 20px;
                margin-right: 8px;
                text-align: center;
                opacity: 0.8;
            }}
            .splash-hint {{
                margin-top: 32px;
                font-size: 14px;
                color: rgba(255,255,255,0.3);
                opacity: 0;
                animation: splashIn 0.4s ease-out 1.2s forwards;
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
                .tl-legend-btn {{ display: none !important; }}
                .legend {{ display: none !important; }}
                .splash-title {{ font-size: 34px; }}
                .splash-subtitle {{ font-size: 16px; }}
                .splash-tips li {{ font-size: 14px; }}
            }}

            @media (max-height: 500px) and (min-width: 769px) {{
                .tl-pill {{ height: 22px; padding: 2px 8px; }}
                .tl-pill .tl-pill-label {{ font-size: 9px; }}
                .tl-dot-wrap {{ height: 12px; }}
                .tl-divider {{ height: 8px; }}
            }}
        </style>
    </head>
    <body>
        <div class="map-container">
            {folium_html if folium_html else '<div class="no-books"><div class="no-books-icon">&#128218;</div><h2>No books found for this century</h2></div>'}
        </div>

        <div id="splash" class="splash" style="display:none;">
            <div class="splash-content">
                <div class="splash-title">4,000 Years of Great Books</div>
                <div class="splash-subtitle">Explore the world's greatest works on the map</div>
                <ul class="splash-tips">
                    <li><span class="tip-icon">&#128205;</span>Tap a dot to explore a book</li>
                    <li><span class="tip-icon">&#9202;</span>Use the timeline to travel through centuries</li>
                    <li><span class="tip-icon">&#127758;</span>Pinch to zoom, drag to explore</li>
                </ul>
                <div class="splash-hint">Tap anywhere to begin</div>
            </div>
        </div>

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
                Most books drawn from The Greatest Books top 500 list. Centuries without a top-500 entry are filled with at least one notable work.
            </div>
        </div>

        <script>
            var CENTURY_DATA = {century_data_json};
            var SELECTED_CENTURY = {int(st.session_state.selected_century)};
            var LABEL_CENTURIES = {json.dumps(sorted(label_centuries_set))};

            function toggleLegend() {{
                document.getElementById('legend').classList.toggle('show');
            }}

            // Compact label: "20 BC", "1 AD", "5th", "19th", "21st"
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

            // Long label for tooltip: "20th Century", "5 BC"
            function formatCenturyLong(c) {{
                if (c < 0) return Math.abs(c) + ' BC';
                if (c === 1) return '1st Century';
                return formatCentury(c) + ' Century';
            }}

            // Inject navigation listener into parent
            (function() {{
                try {{
                    var parentDoc = window.parent.document;
                    if (!parentDoc._litLocNavInstalled) {{
                        var parentScript = parentDoc.createElement('script');
                        parentScript.textContent = 'window.addEventListener("message", function(e) {{ if (e.data && e.data.type === "navigateCentury") {{ window.location.href = "?century=" + e.data.century; }} }});';
                        parentDoc.head.appendChild(parentScript);
                        parentDoc._litLocNavInstalled = true;
                    }}
                }} catch(e) {{}}
            }})();

            function navigateToCentury(c) {{
                window.parent.postMessage({{ type: 'navigateCentury', century: c }}, '*');
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

                    // Era divider between BCE and CE
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

                        // Hover tooltip (desktop only)
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

                        // Hover tooltip (desktop only)
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

                // On mobile, scroll selected into view
                if (isMobile()) {{
                    setTimeout(function() {{
                        var sel = track.querySelector('.selected');
                        if (sel) sel.scrollIntoView({{ inline: 'center', behavior: 'auto' }});
                    }}, 50);
                }}
            }}

            buildTimeline();

            // Debounced resize → rebuild
            var _resizeTimer;
            window.addEventListener('resize', function() {{
                clearTimeout(_resizeTimer);
                _resizeTimer = setTimeout(function() {{
                    buildTimeline();
                }}, 200);
            }});

            // Splash overlay (once per session via parent sessionStorage)
            (function() {{
                try {{
                    var storage = window.parent.sessionStorage;
                    if (!storage.getItem('litloc_splash_shown')) {{
                        var splash = document.getElementById('splash');
                        splash.style.display = 'flex';

                        function dismissSplash() {{
                            splash.classList.add('fade-out');
                            setTimeout(function() {{ splash.style.display = 'none'; }}, 850);
                            splash.removeEventListener('click', dismissSplash);
                        }}

                        splash.addEventListener('click', dismissSplash);
                        setTimeout(dismissSplash, 8000);

                        storage.setItem('litloc_splash_shown', '1');
                    }}
                }} catch(e) {{
                    // sessionStorage unavailable — just skip splash
                }}
            }})();

            // Ensure Leaflet maps resize
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

        /* Hide default Streamlit padding */
        section[data-testid="stMain"] > div {{
            padding-bottom: 0 !important;
            padding-top: 0 !important;
        }}

        section[data-testid="stMain"] {{
            height: 100vh !important;
            overflow: hidden !important;
        }}

        div[data-testid="stMainBlockContainer"] {{
            height: 100vh !important;
            padding: 0 !important;
            max-width: none !important;
        }}

        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {{
            height: 100vh !important;
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
