# Literary Locations

An interactive web app that maps the geographical settings of classic literature across 4,000 years of history. Explore where stories take place, navigate through centuries, and discover connections between books, places, and eras.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.43+-red)
![Folium](https://img.shields.io/badge/Folium-0.19+-green)

## Features

- **Interactive World Map** — Full-screen Folium/Leaflet map with marker clustering
- **Timeline Navigation** — Browse centuries from 2000 BCE to the present; vertical sidebar on desktop, horizontal bar on mobile
- **Book Search** — Filter by title or author with real-time results
- **Color-Coded Markers** — Red for primary story settings, blue for publication locations (used when settings are fictional)
- **Guided Tour** — Onboarding walkthrough for first-time visitors
- **Mobile Optimised** — Responsive layout with touch-friendly controls and dynamic viewport handling

## Quick Start

```bash
# Install dependencies
pip install streamlit folium pandas

# Run the app
streamlit run main.py
```

The app will open at **http://localhost:8501**.

## Project Structure

```
literarylocations/
├── main.py                 # Streamlit entry point
├── data/
│   └── books.json          # Book database (titles, authors, years, coordinates, summaries)
├── utils/
│   ├── data_loader.py      # Data loading, filtering, search, location classification
│   └── map_utils.py        # Base map creation and marker icons
├── styles/
│   └── custom.css          # Custom styling for Streamlit components
├── .streamlit/
│   └── config.toml         # Streamlit server and theme config
└── pyproject.toml          # Project metadata and dependencies
```

## Data Format

Each entry in `books.json` contains:

| Field                | Description                                    |
| -------------------- | ---------------------------------------------- |
| `title`              | Book title                                     |
| `author`             | Author name                                    |
| `year`               | Publication or composition year                |
| `century`            | Century number (negative for BCE)              |
| `location.name`      | Setting name                                   |
| `location.coordinates` | `[latitude, longitude]`                      |
| `summary`            | Brief plot summary                             |
| `historical_context` | Historical background and literary significance |

## How It Works

Books are loaded from JSON and cached with Streamlit. The Folium map is rendered inside a Streamlit `components.html()` iframe with custom JavaScript injected for the timeline, coach tour, splash screen, and century navigation. Clicking a timeline century updates the URL query parameter, which Streamlit reads to filter and display the relevant books.

Fictional or metaphysical settings (e.g. Paradise, Atlantis) are detected automatically and fall back to the author's known publication location, shown with a blue marker.

## Requirements

- Python 3.11+
- Dependencies: `streamlit`, `folium`, `pandas`

## License

All rights reserved.
