# ============================================================
# AGRISMART PRO - COMPLETE UPDATED CODE
# Voice Assistant Removed
# PDF Unicode Error Fixed
# ============================================================

# FIX FOR PYTHON 3.13 CGI ERROR
import sys

try:
    import cgi
except ImportError:
    import types

    cgi = types.ModuleType("cgi")
    cgi.parse_header = lambda x: (x, {})
    sys.modules["cgi"] = cgi

# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import numpy as np
import pandas as pd
import pickle
import requests

from fpdf import FPDF
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AgriSmart Pro | Intelligence Dashboard",
    page_icon="🌿",
    layout="wide"
)

# ============================================================
# API KEYS
# ============================================================

WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

# ============================================================
# MULTI LANGUAGE SUPPORT
# ============================================================

LANG_MAP = {

    "English": {
        "welcome": "Precision Crop Prediction",
        "sync_btn": "Sync Real-time Satellite Data",
        "soil": "Soil Nutrients",
        "predict": "RUN ANALYSIS",
        "insurance_head": "Financial Security & Government Schemes",
        "lat_label": "Farm Latitude",
        "lon_label": "Farm Longitude"
    },

    "Hindi": {
        "welcome": "सटीक फसल भविष्यवाणी",
        "sync_btn": "रियल-टाइम सैटेलाइट डेटा सिंक करें",
        "soil": "मिट्टी के पोषक तत्व",
        "predict": "विश्लेषण करें",
        "insurance_head": "वित्तीय सुरक्षा और सरकारी योजनाएं",
        "lat_label": "अक्षांश",
        "lon_label": "देशांतर"
    },

    "Kannada": {
        "welcome": "ನಿಖರ ಬೆಳೆ ಭವಿಷ್ಯವಾಣಿ",
        "sync_btn": "ರಿಯಲ್ ಟೈಮ್ ಸ್ಯಾಟಲೈಟ್ ಡೇಟಾ ಸಿಂಕ್ ಮಾಡಿ",
        "soil": "ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು",
        "predict": "ವಿಶ್ಲೇಷಣೆ ಪ್ರಾರಂಭಿಸಿ",
        "insurance_head": "ಆರ್ಥಿಕ ಭದ್ರತೆ ಮತ್ತು ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು",
        "lat_label": "ಅಕ್ಷಾಂಶ",
        "lon_label": "ರೇಖಾಂಶ"
    }
}

# ============================================================
# PROFESSIONAL DARK UI
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
}

h1, h2, h3, h4, h5, p, label, .stMarkdown {
    color: white !important;
    font-family: 'Inter', sans-serif;
}

.stMetric {
    background-color: #1c2128;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #30363D;
}

.result-card {
    background-color: #1c2128;
    border-left: 5px solid #4CAF50;
    padding: 25px;
    border-radius: 10px;
    border: 1px solid #30363D;
    margin-bottom: 20px;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #2E7D32 0%, #4CAF50 100%);
    color: white !important;
    font-weight: bold;
    border-radius: 8px;
    height: 3.5em;
    border: none;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# WEATHER FUNCTION
# ============================================================

def get_satellite_weather(lat, lon):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}"
        f"&appid={WEATHER_API_KEY}&units=metric"
    )

    try:

        response = requests.get(url).json()

        if response.get("cod") == 200:

            return {
                "temp": response["main"]["temp"],
                "hum": response["main"]["humidity"],
                "rain": response.get("rain", {}).get("1h", 0) * 24,
                "desc": response["weather"][0]["description"].title()
            }

    except:
        return None

# ============================================================
# INSURANCE CALCULATOR
# ============================================================

def calculate_insurance(crop_name, rainfall, temp):

    base_val = 50000
    rate = 0.02

    if rainfall < 300 or rainfall > 2000:
        rate += 0.015

    if temp > 40:
        rate += 0.01

    return (base_val * rate), base_val

# ============================================================
# LOAD ML MODEL
# ============================================================

@st.cache_resource
def load_assets():

    try:

        model = pickle.load(open("crop_model.pkl", "rb"))
        scaler = pickle.load(open("scaler.pkl", "rb"))

        return model, scaler

    except Exception:
        return None, None

model, scaler = load_assets()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/2942/2942544.png",
        width=80
    )

    lang_choice = st.selectbox(
        "Language",
        list(LANG_MAP.keys())
    )

    texts = LANG_MAP[lang_choice]

    app_mode = st.radio(
        "Menu",
        ["Predict Crop", "Crop Intelligence"]
    )

# ============================================================
# MAIN APP
# ============================================================

if app_mode == "Predict Crop":

    st.markdown(
        f"<h1 style='color:#4CAF50;'>"
        f"AgriSmart Pro - {texts['welcome']}"
        f"</h1>",
        unsafe_allow_html=True
    )

    # ========================================================
    # SATELLITE DATA SECTION
    # ========================================================

    st.markdown(f"## {texts['sync_btn']}")

    col_lat, col_lon = st.columns(2)

    with col_lat:

        lat_in = st.number_input(
            texts['lat_label'],
            value=19.0760,
            format="%.4f"
        )

    with col_lon:

        lon_in = st.number_input(
            texts['lon_label'],
            value=72.8777,
            format="%.4f"
        )

    if st.button("Get Satellite Weather Data"):

        with st.spinner("Fetching live weather data..."):

            weather = get_satellite_weather(lat_in, lon_in)

            if weather:

                st.session_state['temp'] = weather['temp']
                st.session_state['hum'] = weather['hum']
                st.session_state['rain'] = weather['rain']

                st.success(
                    f"Weather Synced Successfully | "
                    f"{weather['desc']} | "
                    f"{weather['temp']} C"
                )

            else:

                st.error(
                    "Failed to fetch weather data. "
                    "Check API key or coordinates."
                )

    st.write("---")

    # ========================================================
    # INPUT SECTION
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(texts['soil'])

        N = st.number_input(
            "Nitrogen (N)",
            0,
            200,
            90
        )

        P = st.number_input(
            "Phosphorus (P)",
            0,
            200,
            42
        )

        K = st.number_input(
            "Potassium (K)",
            0,
            200,
            43
        )

        ph = st.slider(
            "Soil pH",
            0.0,
            14.0,
            6.5
        )

    with col2:

        st.subheader("Environmental Conditions")

        temp = st.slider(
            "Temperature",
            0.0,
            50.0,
            float(st.session_state.get('temp', 25.0))
        )

        hum = st.slider(
            "Humidity",
            0.0,
            100.0,
            float(st.session_state.get('hum', 80.0))
        )

        rain = st.number_input(
            "Rainfall",
            0.0,
            3000.0,
            float(st.session_state.get('rain', 200.0))
        )

    # ========================================================
    # PREDICT BUTTON
    # ========================================================

    if st.button(texts['predict']):

        if model and scaler:

            features = scaler.transform(
                np.array([[N, P, K, temp, hum, ph, rain]])
            )

            probabilities = model.predict_proba(features)[0]

            top_idx = np.argsort(probabilities)[-3:][::-1]

            st.session_state['results'] = [

                (
                    model.classes_[i].upper(),
                    probabilities[i]
                )

                for i in top_idx
            ]

            st.session_state['prediction_ready'] = True

        else:

            st.error(
                "Model or scaler file missing."
            )

    # ========================================================
    # RESULTS SECTION
    # ========================================================

    if st.session_state.get('prediction_ready'):

        st.markdown("## Recommended Crops")

        result_cols = st.columns(3)

        for i, (crop, prob) in enumerate(
            st.session_state['results']
        ):

            with result_cols[i]:

                st.markdown(
                    f"""
                    <div class="result-card">
                        <h3>{crop}</h3>
                        <p>{prob*100:.1f}% Match</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # ====================================================
        # INSURANCE SECTION
        # ====================================================

        st.markdown(
            f"## {texts['insurance_head']}"
        )

        selected_crop = st.session_state['results'][0][0]

        premium, insured_amount = calculate_insurance(
            selected_crop,
            rain,
            temp
        )

        metric1, metric2 = st.columns(2)

        with metric1:

            st.metric(
                "Annual Premium",
                f"Rs. {int(premium)}"
            )

        with metric2:

            st.metric(
                "Sum Insured",
                f"Rs. {int(insured_amount)}"
            )

        st.info(
            "Government Scheme: "
            "Pradhan Mantri Fasal Bima Yojana"
        )

        # ====================================================
        # PDF DOWNLOAD SECTION
        # ====================================================

        st.markdown("## Download Complete Report")

        if st.button("Generate PDF Report"):

            pdf = FPDF()

            pdf.add_page()

            # TITLE
            pdf.set_font("Arial", 'B', 18)

            pdf.cell(
                200,
                10,
                txt="AgriSmart Pro - Crop Analysis Report",
                ln=True,
                align='C'
            )

            pdf.ln(10)

            # DATE
            pdf.set_font("Arial", '', 12)

            current_time = datetime.now().strftime(
                '%d-%m-%Y %H:%M'
            )

            pdf.cell(
                200,
                10,
                txt=f"Generated on: {current_time}",
                ln=True
            )

            pdf.ln(5)

            # SOIL DATA
            pdf.set_font("Arial", 'B', 14)

            pdf.cell(
                200,
                10,
                txt="Soil Parameters",
                ln=True
            )

            pdf.set_font("Arial", '', 12)

            pdf.cell(
                200,
                8,
                txt=f"Nitrogen: {N}",
                ln=True
            )

            pdf.cell(
                200,
                8,
                txt=f"Phosphorus: {P}",
                ln=True
            )

            pdf.cell(
                200,
                8,
                txt=f"Potassium: {K}",
                ln=True
            )

            pdf.cell(
                200,
                8,
                txt=f"Soil pH: {ph}",
                ln=True
            )

            pdf.ln(5)

            # ENVIRONMENT
            pdf.set_font("Arial", 'B', 14)

            pdf.cell(
                200,
                10,
                txt="Environmental Conditions",
                ln=True
            )

            pdf.set_font("Arial", '', 12)

            pdf.cell(
                200,
                8,
                txt=f"Temperature: {temp} C",
                ln=True
            )

            pdf.cell(
                200,
                8,
                txt=f"Humidity: {hum} percent",
                ln=True
            )

            pdf.cell(
                200,
                8,
                txt=f"Rainfall: {rain} mm",
                ln=True
            )

            pdf.ln(5)

            # PREDICTIONS
            pdf.set_font("Arial", 'B', 14)

            pdf.cell(
                200,
                10,
                txt="Top Crop Predictions",
                ln=True
            )

            pdf.set_font("Arial", '', 12)

            for crop, probability in st.session_state['results']:

                pdf.cell(
                    200,
                    8,
                    txt=f"{crop} - {probability*100:.1f}% Match",
                    ln=True
                )

            pdf.ln(5)

            # INSURANCE
            pdf.set_font("Arial", 'B', 14)

            pdf.cell(
                200,
                10,
                txt="Insurance Recommendation",
                ln=True
            )

            pdf.set_font("Arial", '', 12)

            pdf.cell(
                200,
                8,
                txt=f"Annual Premium: Rs. {int(premium)}",
                ln=True
            )

            pdf.cell(
                200,
                8,
                txt=f"Sum Insured: Rs. {int(insured_amount)}",
                ln=True
            )

            pdf.ln(10)

            pdf.multi_cell(
                0,
                8,
                txt=(
                    "Recommended Government Scheme: "
                    "Pradhan Mantri Fasal Bima Yojana"
                )
            )

            # SAVE PDF
            pdf_output = "AgriSmart_Report.pdf"

            pdf.output(pdf_output)

            # DOWNLOAD BUTTON
            with open(pdf_output, "rb") as pdf_file:

                st.download_button(
                    label="Download Complete Report",
                    data=pdf_file,
                    file_name="AgriSmart_Report.pdf",
                    mime="application/pdf"
                )

            st.success(
                "PDF Report Generated Successfully!"
            )

# ============================================================
# CROP INTELLIGENCE PAGE
# ============================================================

else:

    st.markdown(
        "<h1 style='color:#4CAF50;'>"
        "Crop Intelligence Base"
        "</h1>",
        unsafe_allow_html=True
    )

    st.info(
        "Search crop growth tips and historical "
        "crop information here."
    )

# ============================================================
# FOOTER
# ============================================================

st.caption(
    f"© {datetime.now().year} AgriSmart Pro"
)
