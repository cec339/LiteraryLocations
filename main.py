import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from utils.data_loader import DataLoadError, get_dataset_stats, load_book_data, search_books
from utils.map_utils import create_base_map_html


BASE_DIR = Path(__file__).resolve().parent
STYLES_DIR = BASE_DIR / "styles"
STATIC_DIR = BASE_DIR / "static"


st.set_page_config(
    page_title="Great Books World Map",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _read_text(path):
    return path.read_text(encoding="utf-8")


def _inject_css(path):
    st.markdown(f"<style>{_read_text(path)}</style>", unsafe_allow_html=True)


def _query_century():
    try:
        return int(st.query_params.get("century"))
    except (TypeError, ValueError):
        return None


def _default_century(centuries):
    if 20 in centuries:
        return 20
    if centuries:
        return max(centuries)
    return 1


def _book_location_desc(location_type):
    if location_type == "primary":
        return "Primary Story Setting"
    if location_type == "publication":
        return "Publication Location (Fictional/Multiple Settings)"
    return "Story Location"


def _serialize_books(books_df):
    books = []
    for _, bk in books_df.iterrows():
        summary = str(bk.get("summary", ""))
        hist = str(bk.get("historical_context", ""))
        loc_type = bk.get("location_type", "primary")
        books.append(
            {
                "title": str(bk["title"]),
                "author": str(bk["author"]),
                "year": int(bk["year"]),
                "century": int(bk.get("century", 0)),
                "lat": float(bk["setting_latitude"]),
                "lng": float(bk["setting_longitude"]),
                "setting_name": str(bk["setting_name"]),
                "location_type": loc_type,
                "location_desc": _book_location_desc(loc_type),
                "summary": summary[:300] + ("..." if len(summary) > 300 else ""),
                "hist": hist[:300] + ("..." if len(hist) > 300 else ""),
            }
        )
    return json.dumps(books).replace("</", "<\\/")


def _render_map(base_map_html, books_json, is_search_mode, century_data, selected_century, label_centuries):
    map_css = _read_text(STATIC_DIR / "map.css")
    map_js = _read_text(STATIC_DIR / "map.js")
    replacements = {
        "__BOOKS_JSON__": books_json,
        "__IS_SEARCH_MODE__": "true" if is_search_mode else "false",
        "__CENTURY_DATA__": century_data,
        "__SELECTED_CENTURY__": str(int(selected_century)),
        "__LABEL_CENTURIES__": json.dumps(sorted(label_centuries)),
    }
    for placeholder, value in replacements.items():
        map_js = map_js.replace(placeholder, value)

    inject_css = (
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, '
        'maximum-scale=1.0, user-scalable=no">\n'
        f"<style>\n{map_css}\n</style>"
    )
    overlay_html = """
        <div id="splash" class="splash">
            <div class="splash-content">
                <div class="splash-title">4,000 Years of Great Books</div>
                <div class="splash-subtitle">Explore the world's greatest works on the map</div>
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
                Most books drawn from thegreatestbooks.org top 500 list. Centuries without a top-500 entry are filled with at least one notable work.
            </div>
        </div>
    """
    inject_body = f"{overlay_html}\n<script>\n{map_js}\n</script>"
    map_only_html = base_map_html.replace("</head>", inject_css + "\n</head>").replace(
        "</body>",
        inject_body + "\n</body>",
    )
    components.html(map_only_html, height=800, scrolling=False)


_inject_css(STYLES_DIR / "custom.css")
_inject_css(STATIC_DIR / "streamlit.css")

try:
    all_books = load_book_data()
except DataLoadError as exc:
    st.error("No book data available. Check that data/books.json exists and is valid.")
    st.caption(str(exc))
    st.stop()

if all_books.empty:
    st.error("No book data available. Check that data/books.json contains valid book records.")
    st.stop()

century_counts = all_books.groupby("century").size().to_dict()
centuries_with_books = sorted(century_counts.keys())
default_century = _default_century(centuries_with_books)

if "selected_century" not in st.session_state:
    st.session_state.selected_century = default_century

requested_century = _query_century()
if requested_century in century_counts:
    st.session_state.selected_century = requested_century
elif st.session_state.selected_century not in century_counts:
    st.session_state.selected_century = default_century

if "last_search_query" not in st.session_state:
    st.session_state.last_search_query = ""
if "century_updated" not in st.session_state:
    st.session_state.century_updated = False

century_data_json = json.dumps(
    [{"c": int(c), "n": int(century_counts[c])} for c in centuries_with_books]
)
search_results = None

with st.sidebar:
    st.header("🔍 Search Books")
    search_query = st.text_input("Search by title or author")

    if search_query:
        search_results = search_books(search_query, all_books)
        if not search_results.empty:
            st.success(f"Found {len(search_results)} matching books")
            st.info("Clear the search box and press Enter to return to century view")

            if (
                search_query != st.session_state.last_search_query
                and not st.session_state.century_updated
                and "century" in search_results.columns
            ):
                most_common_century = int(search_results["century"].mode()[0])
                st.session_state.selected_century = most_common_century
                st.query_params["century"] = str(most_common_century)
                st.session_state.last_search_query = search_query
                st.session_state.century_updated = True
                st.rerun()
        else:
            st.warning("No books found matching your search")
    else:
        st.session_state.last_search_query = ""
        st.session_state.century_updated = False

    stats = get_dataset_stats(all_books)
    st.header("📊 Dataset Info")
    st.metric("Total Books", stats.get("total_books", 0))
    st.metric("Unique Authors", stats.get("unique_authors", 0))
    st.metric("Century Range", stats.get("century_range", ""))

try:
    is_search_mode = bool(search_query and search_results is not None and not search_results.empty)
    books_for_map = search_results if is_search_mode else all_books
    books_json_str = _serialize_books(books_for_map)
    base_map_html = create_base_map_html()

    label_centuries_set = set()
    if centuries_with_books:
        label_centuries_set.add(centuries_with_books[0])
        label_centuries_set.add(centuries_with_books[-1])
    for century in [-20, -10, -5, -1, 1, 5, 10, 15, 20, 21]:
        if century in century_counts:
            label_centuries_set.add(century)

    _render_map(
        base_map_html,
        books_json_str,
        is_search_mode,
        century_data_json,
        st.session_state.selected_century,
        label_centuries_set,
    )
except Exception as exc:
    st.error(f"An error occurred: {str(exc)}")
    st.info("Please check the data files and try again.")
