# Overview

The Literary World Map is a Streamlit-based web application that visualizes the geographical settings of classic literature through an interactive world map. The application allows users to explore literary works by time period (century) and search for specific books or authors. Each book is represented as a marker on the map, with different colors indicating whether the coordinates represent the actual story setting or the publication location for works with fictional/metaphysical settings.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit for web interface
- **Styling**: Custom CSS for responsive design and improved user experience
- **Components**: Sidebar for search functionality, main area for map display and century selection
- **Map Visualization**: Folium library for interactive mapping with marker clusters

## Data Management
- **Data Storage**: JSON file (`data/books.json`) containing book metadata including title, author, year, location coordinates, and historical context
- **Data Processing**: Custom utilities for loading, filtering, and transforming book data
- **Location Classification**: Smart algorithm to determine whether to show story setting or publication location based on content analysis

## Core Features
- **Century-based Filtering**: Slider interface to explore literature from different time periods (20th century BCE through 21st century CE)
- **Search Functionality**: Text-based search across book titles and authors
- **Interactive Mapping**: Color-coded markers (red for primary settings, blue for publication locations) with detailed popups
- **Mobile-First Design**: Full-screen map with overlay controls, no scrolling needed to see the map
- **Dataset**: 524 books with continuous coverage across all centuries from ancient to modern times

## Mobile UI Features
- **Full-Screen Map**: Map fills the viewport with overlay controls on top
- **Top Overlay Bar**: Semi-transparent title bar ("📚 Literary World Map")
- **Bottom Control Panel**: Century display, navigation slider, prev/next buttons, book count badge
- **Legend Button**: "i" icon that toggles marker color legend (Story Setting vs Publication Location)
- **Slide-Up Books Panel**: Tap book count to see full book list
- **Touch-Friendly**: All buttons are 44-48px minimum for accessibility
- **Landscape Support**: Controls reposition for landscape orientation

## Data Structure
- **Book Records**: Each book contains title, author, publication year, century, geographical coordinates, plot summary, and historical context
- **Location Intelligence**: Sophisticated logic to handle fictional settings, multiple locations, and invalid coordinates by falling back to publication locations
- **Coordinate Validation**: System to detect and correct invalid (0,0) coordinates and other geographic inconsistencies

# External Dependencies

## Core Libraries
- **Streamlit**: Web application framework for the user interface
- **Folium**: Interactive mapping library for geographic visualization
- **Pandas**: Data manipulation and analysis
- **JSON**: Data storage and parsing

## Styling and UI
- **Custom CSS**: Responsive design and map container styling
- **Folium Plugins**: MarkerCluster for better performance with multiple markers
- **Font Awesome**: Icons for map markers

## Data Sources
- **Literary Dataset**: Curated collection of classic literature with geographical metadata
- **Coordinate Data**: Geographic coordinates for both story settings and publication locations
- **Historical Context**: Cultural and historical background for each literary work

## Development Tools
- **Python Scripts**: Utilities for data validation, coordinate fixing, and quality assurance
- **Text Processing**: Regular expressions for pattern matching and data cleaning