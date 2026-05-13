import json
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BOOKS_PATH = DATA_DIR / "books.json"

REQUIRED_COLUMNS = [
    "title",
    "author",
    "year",
    "century",
    "setting_latitude",
    "setting_longitude",
    "setting_name",
    "why_here",
    "summary",
    "historical_context",
]


class DataLoadError(RuntimeError):
    """Raised when required app data cannot be loaded."""


def _file_mtime(path):
    try:
        return path.stat().st_mtime
    except OSError as exc:
        raise DataLoadError(f"Cannot read required data file: {path}") from exc


def _empty_books_df():
    return pd.DataFrame(columns=REQUIRED_COLUMNS)


def _ordinal(n):
    """Return ordinal string for an integer century."""
    value = int(n)
    absolute = abs(value)
    if 11 <= (absolute % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(absolute % 10, 4)]
    era = " BCE" if value < 0 else ""
    return f"{absolute}{suffix}{era}"


def _missing_text(value):
    return value is None or str(value).strip() == "" or str(value).strip().lower() == "null"


def _coerce_coordinate_pair(coordinates):
    if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 2:
        return None
    try:
        lat = float(coordinates[0])
        lng = float(coordinates[1])
    except (TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None
    return [lat, lng]


def _process_book(book):
    if not isinstance(book, dict):
        return None

    title = book.get("title")
    author = book.get("author")
    if _missing_text(title) or _missing_text(author) or book.get("year") is None or book.get("century") is None:
        return None

    location = book.get("location") or {}
    if not isinstance(location, dict):
        return None

    coordinates = _coerce_coordinate_pair(location.get("coordinates"))
    if coordinates is None:
        return None

    try:
        year = int(book.get("year"))
        century = int(book.get("century"))
    except (TypeError, ValueError):
        return None

    return {
        "title": str(title),
        "author": str(author),
        "year": year,
        "century": century,
        "setting_latitude": coordinates[0],
        "setting_longitude": coordinates[1],
        "setting_name": location.get("name", "") or "",
        "why_here": str(location.get("why_here", "") or ""),
        "summary": book.get("summary", "Summary not available"),
        "historical_context": book.get("historical_context", "Historical context not available"),
    }


@st.cache_data
def _load_book_data(mtime):
    del mtime
    try:
        with open(BOOKS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataLoadError(f"Cannot load book data from {BOOKS_PATH}") from exc

    books = data.get("books") if isinstance(data, dict) else None
    if not isinstance(books, list):
        raise DataLoadError(f"{BOOKS_PATH} must contain a 'books' list")

    processed_books = []
    for book in books:
        try:
            processed_book = _process_book(book)
        except DataLoadError:
            raise
        except Exception:
            processed_book = None
        if processed_book:
            processed_books.append(processed_book)

    if not processed_books:
        return _empty_books_df()

    df = pd.DataFrame(processed_books, columns=REQUIRED_COLUMNS)
    df = df.drop_duplicates(subset=["title", "author"], keep="first")
    df = df[df["title"].astype(str).str.len() > 0]
    df = df[df["author"].astype(str).str.len() > 0]
    return df


def load_book_data():
    """Load and process book data from the consolidated JSON file."""
    return _load_book_data(_file_mtime(BOOKS_PATH))


def search_books(query, books_df=None):
    """Search books by title or author."""
    df = load_book_data() if books_df is None else books_df
    if df.empty or not query:
        return df

    query_lower = str(query).lower()
    mask = (
        df["title"].str.lower().str.contains(query_lower, na=False, regex=False)
        | df["author"].str.lower().str.contains(query_lower, na=False, regex=False)
    )
    return df[mask]


def get_dataset_stats(books_df=None):
    """Get statistics about the dataset."""
    df = load_book_data() if books_df is None else books_df
    if df.empty:
        return {}

    return {
        "total_books": len(df),
        "unique_authors": df["author"].nunique(),
        "century_range": f"{_ordinal(df['century'].min())} to {_ordinal(df['century'].max())}",
    }
