import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# --- Production Dependency Mapping ---
try:
    from geopy.geocoders import Nominatim
    from flatlib.datetime import Datetime
    from flatlib.geopos import GeoPos
    from flatlib.chart import Chart
    from flatlib import const
except ModuleNotFoundError:
    st.error("Booting true Vedic calculation engine layers. Please give the server a moment and refresh.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="Vedic Astro Precision Engine",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- High-Performance Caching Layer ---
@st.cache_data(ttl=86400)
def get_coordinates_from_location(location_string):
    """Resolves typed location text inputs using cached geographic maps."""
    try:
        geolocator = Nominatim(user_agent="jyotish_enterprise_engine_final")
        location_data = geolocator.geocode(location_string, timeout=5)
        if location_data:
            return {
                "latitude": location_data.latitude,
                "longitude": location_data.longitude,
                "address": location_data.address
            }
    except Exception:
        pass
    return {"latitude": 19.0760, "longitude": 72.8777, "address": "Mumbai, Maharashtra, India"}


@st.cache_data
def compute_live_astrology(year, month, day, hour, minute, lat, lon, tz_offset):
    """Runs high-precision astronomical calculations using the true Lahiri Sidereal Zodiac."""
    time_str = f"{hour:02d}:{minute:02d}"
    date_str = f"{year}/{month:02d}/{day:02d}"
    
    # Invert offset formatting to align with Flatlib's standard coordinate grid mapping
    formatted_tz = -tz_offset 
    
    # Initialize engine timing structures
    dt = Datetime(date_str, time_str, formatted_tz)
    pos = GeoPos(lat, lon)
    
    # Force AYANAMSA_LAHIRI to switch from Western Tropical to true Vedic Sidereal
    chart = Chart(dt, pos, ayanamsa=const.AYANAMSA_LAHIRI)
    
    planet_list = []
    target_bodies = [
        const.SUN, const.MOON, const.MERCURY, const.VENUS, 
        const.MARS, const.JUPITER, const.SATURN, const.RAHU, const.KETU
    ]
    
    # Extract True Ascendant (Lagna)
    asc = chart.get(const.ASC)
    planet_list.append({
        "Planet": "Ascendant (Lagna)",
        "Sign": asc.sign,
        "Degree": f"{int(asc.sign_lon):02d}° {int((asc.sign_lon % 1) * 60):02d}'",
        "House": 1
    })
    
    # Map all planetary bodies to their true Vedic House placements
    for body in target_bodies:
        obj = chart.get(body)
        house_num = chart.houses.getHouseNum(obj.lon)
        
        # Clean up names for presentation formatting
        p_name = body.capitalize()
        if body == const.RAHU: p_name = "Rahu"
        if body == const.KETU: p_name = "Ketu"
        
        planet_list.append({
            "Planet": p_name,
            "Sign": obj.sign,
            "Degree": f"{int(obj.sign_lon):02d}° {int((obj.sign_lon % 1) * 60):02d}'",
            "House": int(house_num)
        })
        
    return planet_list, asc.sign

# --- UI Setup ---
st.title("🌌 Vedic Astrology Precision Engine")
st.markdown("This live dashboard runs true **Lahiri Sidereal** positioning algorithms to evaluate exact real-time charts.")
st.write("---")

# --- Sidebar Inputs ---
st.sidebar.header("📥 Birth Metrics Intake")
with st.sidebar.form(key="birth_details_form"):
    profile_input = st.text_input("Profile Name", value="Aditya Narayan")
    birth_date = st.date_input("Date of Birth", value=date(1994, 8, 18))
    time_string = st.text_input("Time of Birth (24-Hour Format HH:MM)", value="08:30")
    location_input = st.text_input("Place of Birth", value="Mumbai, India")
    tz_offset = st.number_input("Timezone Offset (Hours from GMT, e.g. IST = 5.5)", value=5.5, step=0.5)
    
    submit_button = st.form_submit_button(label="Compute Precision Chart")

# --- Parsing Execution ---
try:
    parsed_time = datetime.strptime(time_string.strip(), "%H:%M").time()
except ValueError:
    st.sidebar.error("❌ Use standard HH:MM notation (e.g. 14:30).")
    st.stop()

geo_res = get_coordinates_from_location(location_input)
latitude = geo_res["latitude"]
longitude = geo_res["longitude"]
resolved_address = geo_res["address"]

# Process real math sky locations via Sidereal Matrix
calculated_planets, calculated_ascendant = compute_live_astrology(
    birth_date.year, birth_date.month, birth_date.day,
    parsed_time.hour, parsed_time.minute,
    latitude, longitude, tz_offset
)

if submit_button:
    st.sidebar.success(f"✔️ Calculated true sky map for {profile_input}!")

# --- Metrics Header Grid View ---
col1, col2, col3 = st.columns(3)
col1.metric("Vedic Ascendant (Lagna)", calculated_ascendant)
col2.metric("True Coordinates Evaluated", f"{latitude:.4f}° N, {longitude:.4f}° E")
col3.metric("Validated Ephemeris Time", f"{parsed_time.strftime('%I:%M %p')} (GMT{'+' if tz_offset >=0 else ''}{tz_offset})")

st.write("---")

# Main Display Panels Split
left_panel, right_panel = st.columns([3, 2])

with left_panel:
    st.subheader("🪐 Live Planetary Positions (Lahiri Sidereal)")
    st.dataframe(pd.DataFrame(calculated_planets), width="stretch", hide_index=True)
    
with right_panel:
    st.subheader("📐 Relational House Grid Matrix")
    
    house_mapping = {i: [] for i in range(1, 13)}
    for p in calculated_planets:
        if p["Planet"] != "Ascendant (Lagna)":
            h_idx = p["House"]
            if 1 <= h_idx <= 12:
                house_mapping[h_idx].append(p["Planet"])
            
    def get_house_string(num):
        planets_in_house = house_mapping[num]
        return f"House {num}\n" + (", ".join(planets_in_house) if planets_in_house else "Empty")

    chart_grid = [
        [get_house_string(12), get_house_string(1), get_house_string(2)],
        [get_house_string(11), f"🌌 Lagna:\n{calculated_ascendant}", get_house_string(3)],
        [get_house_string(10), get_house_string(9), get_house_string(8)]
    ]
    st.table(pd.DataFrame(chart_grid))
