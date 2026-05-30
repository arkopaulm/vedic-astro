import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# --- Defensive Dependency Handling ---
# Ensures the app doesn't crash on Streamlit Cloud if the container hot-reloads
try:
    from geopy.geocoders import Nominatim
except ModuleNotFoundError:
    st.rerun()

# --- Page Configuration ---
st.set_page_config(
    page_title="Vedic Astro & Dasha Analytics POC",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Geolocator with a dedicated user agent to prevent rate limits
geolocator = Nominatim(user_agent="jyotish_enterprise_poc_v2")

st.title("🌌 Vedic Astrology & Timeline Advisory Dashboard")
st.markdown("This revised POC features dynamic text location resolution, clean keyboard time entry, and updated layout constraints.")
st.write("---")

# --- Sidebar: Birth Data Input Configuration ---
st.sidebar.header("📥 Birth Metrics Intake")
with st.sidebar.form(key="birth_details_form"):
    profile_name = st.text_input("Profile Name", value="Aditya Narayan")
    
    # Calendar Date Picker
    birth_date = st.date_input("Date of Birth", value=date(1994, 8, 18))
    
    # 🕒 Keyboard-Driven Time Input (Avoids long scrollable picklists)
    time_string = st.text_input(
        "Time of Birth (24-Hour Format HH:MM)", 
        value="08:30", 
        help="Type directly using your keyboard. Example: 08:30 for AM, 20:45 for PM"
    )
    
    # 📍 Text-based Location Input (Replaces manual coordinates entry)
    location_input = st.text_input("Place of Birth", value="Mumbai, India", help="Type City/Town name clearly.")
    
    # Form submission anchor
    submit_button = st.form_submit_button(label="Generate Horoscope Matrix")

# --- Geocoding & Validation Processing Layer ---
# Default safe fallbacks (Mumbai)
latitude, longitude, resolved_address = 19.0760, 72.8777, "Mumbai, Maharashtra, India"
time_error = False

# Validate and parse the typed time string safely before calculation execution
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
                st.sidebar.warning("⚠️ Geocoding service busy or timed out. Using default coordinates.")

# --- Mock Calculation Data Factory ---
def get_mock_astrology_payload(lat, lon):
    return {
        "ascendant": "Leo (Simha)",
        "panchanga": {"Bakshatra": "Purva Phalguni", "Tithi": "Shukla Dwadashi", "Yogi Planet": "Venus"},
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

# --- UI Render Workspace Matrix ---
if not time_error:
    data = get_mock_astrology_payload(latitude, longitude)
    
    # KPI Metrics Header Bar
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ascendant (Lagna)", data["ascendant"])
    col2.metric("Birth Star (Nakshatra)", data["panchanga"]["Nakshatra"])
    col3.metric("Resolved Location Coordinates", data["coordinates_used"])
    col4.metric("Calculated Time Asset", f"{parsed_time.strftime('%I:%M %p')}")
    
    st.write("---")
    
    # Main Panels Split
    left_panel, right_panel = st.columns([3, 2])
    
    with left_panel:
        st.subheader("🪐 Planetary Positions")
        # Fixed: Replaced use_container_width=True with width="stretch" to resolve deprecation
        st.dataframe(pd.DataFrame(data["planets"]), width="stretch", hide_index=True)
        
    with right_panel:
        st.subheader("📐 Chart Grid Preview")
        chart_grid = [
            ["House 12\n(Cancer)\nMercury", "House 1\n(Leo)\nAsc, Moon", "House 2\n(Virgo)\nVenus"],
            ["House 11\n(Gemini)\nMars", "🌌 D1 Kundali", "House 3\n(Libra)\nJupiter, Rahu"],
            ["House 10\n(Taurus)\nSun", "House 9\n(Aries)\nKetu", "House 8\n(Pisces)\nEmpty"]
        ]
        st.table(pd.DataFrame(chart_grid))

    st.write("---")

    # Timeline Section
    st.subheader("⏳ Life-Timeline Dynamic Period Analytics")
    df_dashas = pd.DataFrame(data["dashas"])
    
    selected_year = st.slider("Target Analysis Year", min_value=2015, max_value=2065, value=2026, step=1)
    active_row = df_dashas[(selected_year >= df_dashas["Start Year"]) & (selected_year <= df_dashas["End Year"])]
    
    if not active_row.empty:
        active_lord = active_row["Dasha Lord"].values[0]
        active_theme = active_row["Theme"].values[0]
        end_year = active_row["End Year"].values[0]
        
        st.info(f"👉 **Active Mahadasha in {selected_year}: {active_lord} Period** (Ends in {end_year})")
        
        st.write("#### 🎯 Contextual Strategic Advisories")
        focus_area = st.tabs(["💼 Career & Enterprise", "🌱 Wellness & Vitality", "⚖️ Risk Mitigation"])
        
        with focus_area[0]:
            if active_lord == "Jupiter":
                st.success("**Expansion Window:** Favorable alignment for tech architecture design, leading cross-functional squads, or scaling commercial side projects.")
            elif active_lord == "Saturn":
                st.warning("**Consolidation Window:** Focus on systems optimization, code debt cleanup, and process refactoring rather than aggressive hyper-scaling.")
                
        with focus_area[1]:
            st.write(f"**Holistic Focus:** This {active_lord} cycle emphasizes balancing professional output with restorative longevity habits.")
            
        with focus_area[2]:
            st.markdown(f"> 💡 **Strategic Operational Guardrail:** During the {active_lord} cycle, pay special attention to the foundational core themes (*{active_theme}*).")
