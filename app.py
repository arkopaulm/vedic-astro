import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# --- Page Configuration ---
st.set_page_config(
    page_title="Vedic Astro & Dasha Analytics POC",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Title and Description ---
st.title("🌌 Vedic Astrology & Timeline Advisory Dashboard")
st.markdown("This Proof of Concept (POC) acts as a high-fidelity playground to evaluate calculations, chart layouts, and timeline-based advisory components.")
st.write("---")

# --- Sidebar: Birth Data Input Configuration ---
st.sidebar.header("📥 Birth Metrics Intake")
with st.sidebar.form(key="birth_details_form"):
    profile_name = st.text_input("Profile Name", value="Aditya Narayan")
    
    # Combined date and time picker modules
    birth_date = st.date_input("Date of Birth", value=date(1994, 8, 18))
    birth_time = st.time_input("Time of Birth", value=time(8, 30))
    
    st.markdown("##### Geographic Coordinates")
    latitude = st.number_input("Latitude (e.g., Mumbai: 19.076)", value=19.0760, format="%.4f")
    longitude = st.number_input("Longitude (e.g., Mumbai: 72.877)", value=72.8777, format="%.4f")
    tz_offset = st.number_input("Timezone Offset (Hours from GMT, e.g., IST = 5.5)", value=5.5, step=0.5)
    
    # Form submission anchor
    submit_button = st.form_submit_form_button(label="Generate Horoscope Matrix")

# --- Mock Calculation Data Factory ---
# In a fully wired production app, this function connects to your backend FastAPI endpoints or native jyotish libraries.
def get_mock_astrology_payload():
    return {
        "ascendant": "Leo (Simha)",
        "panchanga": {"Nakshatra": "Purva Phalguni", "Tithi": "Shukla Dwadashi", "Yogi Planet": "Venus"},
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
            {"Dasha Lord": "Jupiter", "Start Year": 2015, "End Year": 2031, "Theme": "Expansion, Knowledge, & Asset Accumulation"},
            {"Dasha Lord": "Saturn", "Start Year": 2031, "End Year": 2050, "Theme": "Discipline, Organizational Structure, & Karmic Refinement"},
            {"Dasha Lord": "Mercury", "Start Year": 2050, "End Year": 2067, "Theme": "Commerce, Communication, & System Architecture"}
        ]
    }

# --- Main Dashboard Execution Workspace ---
if submit_button or 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    
    # Fetch computed dataset
    data = get_mock_astrology_payload()
    
    # --- Layout Split: Metrics Grid ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ascendant (Lagna)", data["ascendant"])
    col2.metric("Birth Star (Nakshatra)", data["panchanga"]["Nakshatra"])
    col3.metric("Lunar Phase (Tithi)", data["panchanga"]["Tithi"])
    col4.metric("Financial Yogi Planet", data["panchanga"]["Yogi Planet"])
    
    st.write("---")
    
    # --- Layout Split: Tabular Coordinates & Chart Layout Preview ---
    left_panel, right_panel = st.columns([3, 2])
    
    with left_panel:
        st.subheader("🪐 Planetary Longitudes & House Placements")
        df_planets = pd.DataFrame(data["planets"])
        st.dataframe(df_planets, use_container_width=True, hide_index=True)
        
    with right_panel:
        st.subheader("📐 Chart Layout Matrix Preview")
        # Creating a conceptual text-based 3x3 North/South style structural abstraction grid
        chart_grid = [
            ["House 12\n(Cancer)\nMercury", "House 1\n(Leo)\nAsc, Moon", "House 2\n(Virgo)\nVenus"],
            ["House 11\n(Gemini)\nMars", "🌌 D1 Kundali\nCore Chart", "House 3\n(Libra)\nJupiter, Rahu"],
            ["House 10\n(Taurus)\nSun", "House 9\n(Aries)\nKetu", "House 8\n(Pisces)\nEmpty"]
        ]
        df_grid = pd.DataFrame(chart_grid)
        st.table(df_grid)

    st.write("---")

    # --- Layout Split: Timeline Dasha Analytics & AI Advisory Layer ---
    st.subheader("⏳ Life-Timeline Dynamic Period Analytics")
    st.markdown("Adjust the dynamic slider to isolate your exact position across current or future major *Mahadasha* cycles.")
    
    # Convert data directly into dataframe for charting utilities
    df_dashas = pd.DataFrame(data["dashas"])
    
    # Interactive timeline range tracking component
    selected_year = st.slider("Target Analysis Year", min_value=2015, max_value=2065, value=2026, step=1)
    
    # Filter the active dasha based on the selected year slider configuration
    active_row = df_dashas[(selected_year >= df_dashas["Start Year"]) & (selected_year <= df_dashas["End Year"])]
    
    if not active_row.empty:
        active_lord = active_row["Dasha Lord"].values[0]
        active_theme = active_row["Theme"].values[0]
        end_year = active_row["End Year"].values[0]
        
        st.info(f"👉 **Active Mahadasha in {selected_year}: {active_lord} Period** (Ends in {end_year})")
        
        # UI Presentation Split for Focus Area Advisories
        st.write("#### 🎯 Contextual Strategic Advisories")
        focus_area = st.tabs(["💼 Career & Enterprise", "🌱 Wellness & Vitality", "⚖️ Risk Mitigation"])
        
        with focus_area[0]:
            if active_lord == "Jupiter":
                st.success("**Expansion Window:** Favorable alignment for tech architecture design, leading cross-functional squads, or scaling commercial side projects. Trust high-level abstract logic over rigid processes.")
            elif active_lord == "Saturn":
                st.warning("**Consolidation Window:** Focus on systems optimization, code debt cleanup, and process refactoring rather than aggressive hyper-scaling. Growth is driven through foundational discipline.")
                
        with focus_area[1]:
            st.write(f"**Holistic Focus:** This {active_lord} cycle emphasizes balancing professional output with restorative longevity habits. Keep nutritional guidelines aligned with internal energy trends during this phase.")
            
        with focus_area[2]:
            st.markdown(f"> 💡 **Strategic Operational Guardrail:** During the {active_lord} cycle, pay special attention to the foundational core themes (*{active_theme}*). Avoid high-risk, unvetted capital investments when transitioning between major planetary periods.")
