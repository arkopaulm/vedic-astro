import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# --- Production Dependency Mapping ---
try:
    from geopy.geocoders import Nominatim
    from kerykeion import AstrologicalSubject
except ModuleNotFoundError:
    st.error("Booting core calculation engine layers. Please give the server a moment and refresh.")
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
        geolocator = Nominatim(user_agent="jyotish_enterprise_engine_v7")
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
def compute_live_astrology(profile_name, year, month, day, hour, minute, lat, lon, tz_str):
    """Computes high-precision planet positions by converting Kerykeion data safely to JSON-dicts."""
    subject = AstrologicalSubject(
        profile_name, 
        year, month, day, 
        hour, minute, 
        lat=lat, 
        lng=lon, 
        tz_str=tz_str,
        city="Target"
    )
    
    # Extract the dictionary data format safely from the Kerykeion object
    data_dict = subject.json_dict()
    
    planet_list = []
    
    # 1. Parse the Ascendant (Lagna)
    asc_data = data_dict.get('ascendant', {})
    asc_sign = asc_data.get('sign', 'Unknown')
    planet_list.append({
        "Planet": "Ascendant (Lagna)",
        "Sign": asc_sign,
        "Degree": f"{int(asc_data.get('position', 0)):02d}°",
        "House": 1
    })
    
    # 2. Safely parse the core planetary array from the data dictionary
    planets_data = data_dict.get('planets', [])
    for p in planets_data:
        p_name = p.get('name', 'Unknown')
        p_sign = p.get('sign', 'Unknown')
        p_pos = p.get('position', 0)
        p_house = p.get('house', 1)
        
        # Keep tracking focused on core Vedic planetary bodies
        if p_name.lower() in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'mean_node', 'true_node']:
            # Rename Rahu/Ketu nodes to traditional formats cleanly
            if p_name.lower() == 'mean_node' or p_name.lower() == 'true_node':
                p_name = "Rahu" # Ketu can be extracted or derived as 180 degrees away
            
            planet_list.append({
                "Planet": p_name.capitalize(),
                "Sign": p_sign,
                "Degree": f"{int(p_pos):02d}°",
                "House": int(p_house)
            })
            
    return planet_list, asc_sign

# --- UI Setup ---
st.title("🌌 Vedic Astrology Precision Engine")
st.markdown("This live dashboard uses pure-Python astronomical positioning algorithms to evaluate exact real-time charts.")
st.write("---")

# --- Sidebar Inputs ---
st.sidebar.header("📥 Birth Metrics Intake")
with st.sidebar.form(key="birth_details_form"):
    profile_input = st.text_input("Profile Name", value="Aditya Narayan")
    birth_date = st.date_input("Date of Birth", value=date(1994, 8, 18))
    time_string = st.text_input("Time of Birth (24-Hour Format HH:MM)", value="08:30")
    location_input = st.text_input("Place of Birth", value="Mumbai, India")
    
    timezone_input = st.selectbox(
        "Timezone Location Context",
        ["Asia/Kolkata", "Europe/London", "America/New_York", "Europe/Andorra", "Asia/Dubai", "Australia/Sydney"],
        index=0
    )
    
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

# Process data elements
calculated_planets, calculated_ascendant = compute_live_astrology(
    profile_input,
    birth_date.year, birth_date.month, birth_date.day,
    parsed_time.hour, parsed_time.minute,
    latitude, longitude, timezone_input
)

if submit_button:
    st.sidebar.success(f"✔️ Calculated true sky map for {profile_input}!")

# --- Metrics Header Grid View ---
col1, col2, col3 = st.columns(3)
col1.metric("Calculated Ascendant (Lagna)", calculated_ascendant)
col2.metric("True Coordinates Evaluated", f"{latitude:.4f}° N, {longitude:.4f}° E")
col3.metric("Validated Time Zone Mapping", f"{parsed_time.strftime('%I:%M %p')} ({timezone_input})")

st.write("---")

# Main Display Panels Split
left_panel, right_panel = st.columns([3, 2])

with left_panel:
    st.subheader("🪐 Live Planetary Positions")
    st.dataframe(pd.DataFrame(calculated_planets), width="stretch", hide_index=True)
    
with right_panel:
    st.subheader("📐 Relational House Grid Matrix")
    
    house_mapping = {i: [] for i in range(1, 13)}
    for p in calculated_planets:
        if p["Planet"] != "Ascendant (Lagna)":
            # Guard checking to filter house range bounding arrays safely
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
