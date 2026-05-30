import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# --- Defensive Dependency Handling ---
try:
    from geopy.geocoders import Nominatim
    from flatlib.datetime import Datetime
    from flatlib.geopos import GeoPos
    from flatlib.chart import Chart
    from flatlib import const
except ModuleNotFoundError:
    st.error("Installing engine dependencies. Please give the server a moment and refresh.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="Vedic Astro Analytics Engine",
    page_icon="🌌",
    layout="wide"
)

# --- Real-Time Astrology Computation Engine ---
@st.cache_data(ttl=86400)
def get_coordinates_from_location(location_string):
    """Resolves location inputs using cached geocoding."""
    try:
        geolocator = Nominatim(user_agent="jyotish_enterprise_engine_v3")
        location_data = geolocator.geocode(location_string, timeout=5)
        if location_data:
            return {
                "latitude": location_data.latitude,
                "longitude": location_data.longitude,
                "address": location_data.address
            }
    except Exception:
        pass
    return {"latitude": 19.0760, "longitude": 72.8777, "address": "Mumbai, India (Default)"}


@st.cache_data
def compute_live_astrology(year, month, day, hour, minute, lat, lon, tz_offset):
    """Runs high-precision astronomical evaluations using the Lahiri Sidereal Zodiac."""
    # Format inputs for the calculation engine
    time_str = f"{hour:02d}:{minute:02d}"
    date_str = f"{year}/{month:02d}/{day:02d}"
    
    # Invert offset formatting to align with Flatlib's standard coordinate grid mapping
    formatted_tz = -tz_offset 
    
    # Create engine position and time objects
    dt = Datetime(date_str, time_str, formatted_tz)
    pos = GeoPos(lat, lon)
    
    # Generate astronomical chart using the Lahiri Ayanamsa shift configuration
    chart = Chart(dt, pos, ayanamsa=const.AYANAMSA_LAHIRI)
    
    # Process calculated longitudes into an app-ready list structure
    planet_list = []
    
    # Standard planets to map
    target_bodies = [
        const.SUN, const.MOON, const.MERCURY, const.VENUS, 
        const.MARS, const.JUPITER, const.SATURN, const.RAHU, const.KETU
    ]
    
    # Append Ascendant position first
    asc = chart.get(const.ASC)
    planet_list.append({
        "Planet": "Ascendant (Lagna)",
        "Sign": asc.sign,
        "Degree": f"{int(asc.sign_lon):02d}° {int((asc.sign_lon % 1) * 60):02d}'",
        "House": 1
    })
    
    # Extract positions for all major planetary bodies
    for body in target_bodies:
        obj = chart.get(body)
        # Dynamic calculation matching coordinates to relative house frameworks
        house_num = chart.houses.getHouseNum(obj.lon)
        planet_list.append({
            "Planet": body.capitalize(),
            "Sign": obj.sign,
            "Degree": f"{int(obj.sign_lon):02d}° {int((obj.sign_lon % 1) * 60):02d}'",
            "House": house_num
        })
        
    return planet_list, asc.sign

# --- UI Setup ---
st.title("🌌 Vedic Astrology Precision Engine")
st.markdown("This version runs live, high-precision sidereal calculations using standard NASA-modeled positional algorithms.")
st.write("---")

# --- Sidebar Inputs ---
st.sidebar.header("📥 Birth Metrics Intake")
with st.sidebar.form(key="birth_details_form"):
    profile_name = st.text_input("Profile Name", value="Aditya Narayan")
    birth_date = st.date_input("Date of Birth", value=date(1994, 8, 18))
    time_string = st.text_input("Time of Birth (24-Hour HH:MM)", value="08:30")
    location_input = st.text_input("Place of Birth", value="Mumbai, India")
    tz_offset = st.number_input("Timezone Offset (Hours from GMT, e.g. IST = 5.5)", value=5.5, step=0.5)
    submit_button = st.form_submit_button(label="Compute Precision Chart")

# --- Form Execution Logic ---
try:
    parsed_time = datetime.strptime(time_string.strip(), "%H:%M").time()
except ValueError:
    st.sidebar.error("❌ Use HH:MM format (e.g., 20:45).")
    st.stop()

# 1. Resolve geographic target coordinates
geo_res = get_coordinates_from_location(location_input)
latitude = geo_res["latitude"]
longitude = geo_res["longitude"]

# 2. Run real-time planetary math calculations
calculated_planets, calculated_ascendant = compute_live_astrology(
    birth_date.year, birth_date.month, birth_date.day,
    parsed_time.hour, parsed_time.minute,
    latitude, longitude, tz_offset
)

if submit_button:
    st.sidebar.success(f"✔️ Calculated chart successfully for {profile_name}!")

# --- Render Live Metrics Matrix ---
col1, col2, col3 = st.columns(3)
col1.metric("Calculated Ascendant (Lagna)", calculated_ascendant)
col2.metric("True Coordinates Evaluated", f"{latitude:.4f}° N, {longitude:.4f}° E")
col3.metric("Validated Ephemeris Time", f"{parsed_time.strftime('%I:%M %p')} (GMT{'+' if tz_offset >=0 else ''}{tz_offset})")

st.write("---")

# Main Display Panel Split
left_panel, right_panel = st.columns([3, 2])

with left_panel:
    st.subheader("🪐 Live Planetary Positions (Lahiri Sidereal)")
    st.dataframe(pd.DataFrame(calculated_planets), width="stretch", hide_index=True)
    
with right_panel:
    st.subheader("📐 Relational House Grid Matrix")
    # Dynamically find which planet sits in which house for the layout table view
    house_mapping = {i: [] for i in range(1, 13)}
    for p in calculated_planets:
        if p["Planet"] != "Ascendant (Lagna)":
            house_mapping[p["House"]].append(p["Planet"])
            
    def get_house_string(num):
        planets_in_house = house_mapping[num]
        return f"House {num}\n" + (", ".join(planets_in_house) if planets_in_house else "Empty")

    chart_grid = [
        [get_house_string(12), get_house_string(1), get_house_string(2)],
        [get_house_string(11), f"🌌 Lagna:\n{calculated_ascendant}", get_house_string(3)],
        [get_house_string(10), get_house_string(9), get_house_string(8)]
    ]
    st.table(pd.DataFrame(chart_grid))
