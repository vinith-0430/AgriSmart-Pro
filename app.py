# FIX FOR PYTHON 3.13 CGI ERROR (Add this at the very top)
import sys
try:
    import cgi
except ImportError:
    import types
    cgi = types.ModuleType("cgi")
    cgi.parse_header = lambda x: (x, {}) 
    sys.modules["cgi"] = cgi

import streamlit as st
import numpy as np
import pandas as pd
import pickle
import requests
from fpdf import FPDF
from datetime import datetime
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AgriSmart Pro | Intelligence Dashboard",
    page_icon="🌿",
    layout="wide"
)

# --- CONFIG & API KEYS ---
WEATHER_API_KEY = "7e2b97bb80efdd6e97c83bfc3fa624fa"
DATA_GOV_API_KEY = "579b464db66ec23bdd000001f73c7b1106ca46aa508a971af69425e2" 
translator = Translator()

# --- 1. MULTI-LANGUAGE DICTIONARY ---
LANG_MAP = {
    "English": {
        "welcome": "Precision Crop Prediction", 
        "sync_btn": "Sync Real-time Satellite Data", 
        "soil": "Soil Nutrients", 
        "predict": "RUN ANALYSIS",
        "voice_tip": "Click to speak (e.g. 'Predict for Rice')",
        "insurance_head": "🏦 Financial Security & Government Schemes",
        "lat_label": "Farm Latitude",
        "lon_label": "Farm Longitude"
    },
    "Hindi": {
        "welcome": "सटीक फसल भविष्यवाणी", 
        "sync_btn": "रियल-टाइम सैटेलाइट डेटा सिंक करें", 
        "soil": "मिट्टी के पोषक तत्व", 
        "predict": "विश्लेषण करें",
        "voice_tip": "बोलने के लिए क्लिक करें (जैसे 'चावल के लिए भविष्यवाणी')",
        "insurance_head": "🏦 वित्तीय सुरक्षा और सरकारी योजनाएं",
        "lat_label": "अक्षांश (Latitude)",
        "lon_label": "देशांतर (Longitude)"
    },
    "Tamil": {
        "welcome": "துல்லியமான பயிர் கணிப்பு", 
        "sync_btn": "செயற்கைக்கோள் தரவை ஒத்திசைக்கவும்", 
        "soil": "மண் சத்துக்கள்", 
        "predict": "பகுப்பாய்வு செய்",
        "voice_tip": "பேச கிளிக் செய்யவும் (எ.கா. 'நெல்லுக்குக் கணிக்கவும்')",
        "insurance_head": "🏦 நிதி பாதுகாப்பு மற்றும் அரசு திட்டங்கள்",
        "lat_label": "அட்சரேகை",
        "lon_label": "தீர்க்கரேகை"
    },
    "Telugu": {
        "welcome": "ఖచ్చితమైన పంట అంచనా", 
        "sync_btn": "శాటిలైట్ డేటాను సమకాలీకరించండి", 
        "soil": "మట్టి పోషకాలు", 
        "predict": "విశ్లేషణను ప్రారంభించండి",
        "voice_tip": "మాట్లాడటానికి క్ளிక్ చేయండి",
        "insurance_head": "🏦 ఆర్థిక భద్రత మరియు ప్రభుత్వ పథకాలు",
        "lat_label": "అక్షాంశం",
        "lon_label": "రేఖాంశం"
    }
}

# --- PROFESSIONAL DARK UI CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, h4, h5, p, label, .stMarkdown { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    .stMetric { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363D; }
    .result-card { background-color: #1c2128; border-left: 5px solid #4CAF50; padding: 25px; border-radius: 10px; border: 1px solid #30363D; margin-bottom: 20px; }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #2E7D32 0%, #4CAF50 100%); color: white !important; font-weight: bold; border-radius: 8px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def get_satellite_weather(lat, lon):
    """LOGIC 1: Satellite-Based Environment Auto-Fill"""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("cod") == 200:
            return {
                "temp": response["main"]["temp"],
                "hum": response["main"]["humidity"],
                "rain": response.get("rain", {}).get("1h", 0) * 24,
                "desc": response["weather"][0]["description"].title()
            }
    except: return None

def calculate_insurance(crop_name, rainfall, temp):
    """LOGIC 3: Financial Risk Calculation"""
    base_val = 50000 
    rate = 0.02 
    if rainfall < 300 or rainfall > 2000: rate += 0.015
    if temp > 40: rate += 0.01
    return (base_val * rate), base_val

@st.cache_resource
def load_assets():
    try:
        model = pickle.load(open("crop_model.pkl", "rb"))
        scaler = pickle.load(open("scaler.pkl", "rb"))
        return model, scaler
    except Exception as e:
        return None, None

model, scaler = load_assets()

# --- APP LAYOUT ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2942/2942544.png", width=80)
    lang_choice = st.selectbox("🌐 Language / भाषा", list(LANG_MAP.keys()))
    texts = LANG_MAP[lang_choice]
    app_mode = st.radio("Menu", ["Predict Crop", "Crop Intelligence"])

if app_mode == "Predict Crop":
    st.markdown(f"<h1 style='color: #4CAF50;'>🌾 {texts['welcome']}</h1>", unsafe_allow_html=True)
    
    # --- LOGIC 2: VOICE UI ---
    st.subheader("🎙️ Voice Assistant")
    voice_input = speech_to_text(language='en-US', start_prompt=texts['voice_tip'], key='speech')
    if voice_input:
        st.info(f"Heard: {voice_input}")
        # Simple voice command logic
        if "rice" in voice_input.lower():
            st.session_state['temp'], st.session_state['hum'] = 27.0, 85.0
            st.success("Auto-filled environmental parameters for Rice.")

    # --- LOGIC 1: SATELLITE AUTO-FILL ---
    st.markdown(f"### 🛰️ {texts['sync_btn']}")
    col_lat, col_lon = st.columns(2)
    with col_lat: 
        lat_in = st.number_input(texts['lat_label'], value=19.0760, format="%.4f")
    with col_lon: 
        lon_in = st.number_input(texts['lon_label'], value=72.8777, format="%.4f")

    if st.button(f"🔗 {texts['sync_btn']}"):
        with st.spinner('Accessing satellite data...'):
            w = get_satellite_weather(lat_in, lon_in)
            if w:
                st.session_state['temp'] = w['temp']
                st.session_state['hum'] = w['hum']
                st.session_state['rain'] = w['rain']
                st.success(f"Synced: {w['desc']} | Temp: {w['temp']}°C")
            else:
                st.error("Connection failed. Check coordinates or API key.")

    st.write("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"🧪 {texts['soil']}")
        N = st.number_input("Nitrogen (N)", 0, 200, 90)
        P = st.number_input("Phosphorus (P)", 0, 200, 42)
        K = st.number_input("Potassium (K)", 0, 200, 43)
        ph = st.slider("Soil pH", 0.0, 14.0, 6.5)

    with c2:
        st.subheader("☁️ Environment")
        # Use Satellite data from session state
        temp = st.slider("Temp °C", 0.0, 50.0, float(st.session_state.get('temp', 25.0)))
        hum = st.slider("Humidity %", 0.0, 100.0, float(st.session_state.get('hum', 80.0)))
        rain = st.number_input("Rainfall mm", 0.0, 3000.0, float(st.session_state.get('rain', 200.0)))

    if st.button(f"🚀 {texts['predict']}"):
        if model and scaler:
            feats = scaler.transform(np.array([[N, P, K, temp, hum, ph, rain]]))
            probs = model.predict_proba(feats)[0]
            top_idx = np.argsort(probs)[-3:][::-1]
            st.session_state['res'] = [(model.classes_[i].upper(), probs[i]) for i in top_idx]
            st.session_state['ready'] = True

    if st.session_state.get('ready'):
        cols = st.columns(3)
        for i, (crop, p) in enumerate(st.session_state['res']):
            with cols[i]:
                st.markdown(f'<div class="result-card"><h4>{crop}</h4><p>{p*100:.1f}% Match</p></div>', unsafe_allow_html=True)
        
        # --- LOGIC 3: INSURANCE & LOAN CALCULATOR ---
        st.markdown(f"### {texts['insurance_head']}")
        sel_crop = st.session_state['res'][0][0]
        prem, total = calculate_insurance(sel_crop, rain, temp)
        
        ic1, ic2 = st.columns(2)
        with ic1: st.metric("Annual Premium", f"₹{int(prem)}")
        with ic2: st.metric("Sum Insured", f"₹{int(total)}")
        st.info("💡 **Scheme:** [Pradhan Mantri Fasal Bima Yojana](https://pmfby.gov.in/)")

else:
    st.markdown("<h1 style='color: #4CAF50;'>📖 Crop Intelligence Base</h1>", unsafe_allow_html=True)
    st.info("Search specialized growth tips and historical crop data here.")

st.caption(f"© {datetime.now().year} AgriSmart Pro | National Level Hackathon Module")
