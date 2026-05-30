import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from geopy.geocoders import Nominatim

# --- Page Configuration ---
st.set_page_config(
    page_title="Vedic Astro & Dasha Analytics POC",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Geolocator (Using an agent string to prevent rate-blocking)
geolocator = Nominatim(user_agent="jyotish_enterprise_poc")

st.title("🌌 Vedic Astrology & Timeline Advisory Dashboard")
st.markdown("This updated POC uses dynamic location string resolution instead of manual coordinate entries.")
st.write("---")

# --- Sidebar: Birth Data Input Configuration ---
st.sidebar.header("📥 Birth Metrics Intake")
with st.sidebar.form(key="birth_details_form"):
    profile_name = st.text_input("Profile Name", value="Aditya Narayan")
    
    # Date Input Matrix
    birth_date = st.date_input("Date of Birth", value=date(1994, 8, 18))
    
    # 🕒 Keyboard-Driven Time Input Instead of a Picklist
    # Instructs users to use standard keyboard entry to prevent scrolling dropdown menus
    time_string = st.text_input("Time of Birth (24-Hour Format HH:MM)", value="08:30", help="Type using your keyboard. Example: 08:30 for AM, 20:45 for PM")
    
    # 📍 Text-based Location Input Replacing Coordinates
    location_input = st.text_input("Place of Birth", value="Mumbai, India", help="Type City/Town name clearly.")
    
    # Form submission anchor (Fixed syntax typo)
    submit_button = st.form_submit_button(label="Generate Horoscope Matrix")

# --- Geocoding Processing Layer ---
latitude, longitude, resolved_address = 19.0760, 72.8777, "Mumbai, Maharashtra, India"
time_error = False

# Validate and parse the typed time string safely
try:
    parsed_time = datetime.strptime(time_string.strip(), "%H:%M").time()
except ValueError:
    time_error = True
    parsed_time = time(8, 30)

if submit_button:
    if time_error:
        st.sidebar.error("❌ Invalid Time Format. Please type using HH:MM format (e.g., 14:20).")
    else:
        with st.spinner("Resolving coordinates from location..."):
            try:
                # Call Geocoding service to process string input
                location_data = geolocator.geocode(location_input, timeout=10)
                if location_data:
                    latitude = location_data.latitude
                    longitude = location_data.longitude
                    resolved_address = location_data.address
                    st.sidebar.success(f"📍 Found: {resolved_address[:35]}...")
                else:
                    st.sidebar.error("⚠️ Location not found. Using default coordinates (Mumbai).")
            except Exception:
                st.sidebar.warning("⚠️ Geocoding service busy. Using default coordinates.")

# --- Mock Calculation Data Factory ---
def get_mock_astrology_payload(lat, lon):
    return {
        "ascendant": "Leo (Simha)",
        "panchanga": {"Nakshatra": "Purva Phalguni", "Tithi": "Shukla Dwadashi", "Yogi Planet": "Venus"},
        "coordinates_used": f"{lat:.4f}° N, {lon:.4f}° E",
        "planets": [
            {"Planet": "Ascendant", "Sign": "Leo", "Degree": "22° 40'", "House": 1},
            {"Planet": "Sun", "Sign": "Taurus", "Degree": "14° 25'", "House": 10},
            {"Planet": "Moon", "Sign": "Leo", "Degree": "18° 12'", "House": 1},
            {"Planet": "Mars", "Sign": "Gemini", "Degree": "05° 44'", "House": 11},
            {"Planet": "Mercury", "Sign": "Cancer", "Degree": "29° 10'", "House": 12},
            {"Planet": "Jupiter", "Sign": "Libra", "Degree": "11° 50'", "House": 3},
            {"Planet": "Venus", "Sign": "Virgo", "Degree": "02° 15'", "House": 2},
            {"Planet": "Saturn (R)", "Sign": "Aquarius", "Degree": "15° 30'", "House": 7},
            {"Planet": "Rahu", "Sign": "Libra", "Degree": "24° 08'", "House": 3},
            {"Planet": "Ketu", "Sign": "Aries", "Degree": "24° 08'", "House": 9}
        ],
        "dashas": [
            {"Dasha Lord": "Jupiter", "Start Year": 2015, "End Year": 2031, "Theme": "Expansion & Knowledge"},
            {"Dasha Lord": "Saturn", "Start Year": 2031, "End Year": 2050, "Theme": "Discipline & Structure"},
            {"Dasha Lord": "Mercury", "Start Year": 2050, "End Year": 2067, "Theme": "Commerce & Systems"}
        ]
    }

# --- UI Render Matrix ---
if not time_error:
    data = get_mock_astrology_payload(latitude, longitude)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ascendant (Lagna)", data["ascendant"])
    col2.metric("Birth Star (Nakshatra)", data["panchanga"]["Nakshatra"])
    col3.metric("Resolved Location Coordinates", data["coordinates_used"])
    col4.metric("Calculated Time Asset", f"{parsed_time.strftime('%I:%M %p')}")
    
    st.write("---")
    
    left_panel, right_panel = st.columns([3, 2])
    with left_panel:
        st.subheader("🪐 Planetary Positions")
        st.dataframe(pd.DataFrame(data["planets"]), use_container_width=True, hide_index=True)
        
    with right_panel:
        st.subheader("📐 Chart Grid Preview")
        chart_grid = [
            ["House 12\n(Cancer)\nMercury", "House 1\n(Leo)\nAsc, Moon", "House 2\n(Virgo)\nVenus"],
            ["House 11\n(Gemini)\nMars", "🌌 D1 Kundali", "House 3\n(Libra)\nJupiter, Rahu"],
            ["House 10\n(Taurus)\nSun", "House 9\n(Aries)\nKetu", "House 8\n(Pisces)\nEmpty"]
        ]
        st.table(pd.DataFrame(chart_grid))
