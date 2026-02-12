import streamlit as st
import numpy as np
import pandas as pd
import pickle
import requests
from fpdf import FPDF
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AgriSmart Pro | Intelligence Dashboard",
    page_icon="🌿",
    layout="wide"
)

# --- CONFIG & API KEYS ---
WEATHER_API_KEY = "c39514d4a14765b3dae51ceaa920491c"
DATA_GOV_API_KEY = "579b464db66ec23bdd000001f73c7b1106ca46aa508a971af69425e2" 

# --- PROFESSIONAL DARK UI CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, h4, h5, p, label, .stMarkdown {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D;
    }
    .stNumberInput input, .stSlider {
        background-color: #1c2128 !important;
        color: white !important;
        border: 1px solid #30363D !important;
    }
    .green-text { color: #4CAF50 !important; font-weight: bold; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2E7D32 0%, #4CAF50 100%);
        color: white !important;
        border: none;
        padding: 15px 0px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
    }
    .result-card {
        background-color: #1c2128;
        border-left: 5px solid #4CAF50;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #30363D;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER KNOWLEDGE BASE (22 CROPS) ---
CROP_IDEALS = {
    "RICE": {"N": 80, "P": 40, "K": 40, "pH": "5.5-6.5", "Rain": "1000mm+", "Tip": "Maintain standing water."},
    "MAIZE": {"N": 100, "P": 50, "K": 30, "pH": "6.0-7.0", "Rain": "500-800mm", "Tip": "Ensure good drainage."},
    "CHICKPEA": {"N": 40, "P": 60, "K": 80, "pH": "6.0-9.0", "Rain": "600-950mm", "Tip": "Avoid waterlogging."},
    "KIDNEYBEANS": {"N": 20, "P": 60, "K": 20, "pH": "5.5-6.0", "Rain": "600-1000mm", "Tip": "Requires moderate temp."},
    "PIGEONPEAS": {"N": 20, "P": 70, "K": 20, "pH": "5.0-8.5", "Rain": "600-1100mm", "Tip": "Drought resistant crop."},
    "MOTHBEANS": {"N": 20, "P": 40, "K": 20, "pH": "4.0-9.0", "Rain": "300-600mm", "Tip": "Thrives in arid regions."},
    "MUNGBEAN": {"N": 20, "P": 40, "K": 20, "pH": "6.2-7.2", "Rain": "600-900mm", "Tip": "Quick growing legume."},
    "BLACKGRAM": {"N": 40, "P": 60, "K": 20, "pH": "5.0-8.5", "Rain": "600-1000mm", "Tip": "Rich in protein."},
    "LENTIL": {"N": 20, "P": 60, "K": 20, "pH": "5.9-6.8", "Rain": "400-600mm", "Tip": "Winter season crop."},
    "POMEGRANATE": {"N": 20, "P": 10, "K": 40, "pH": "5.5-7.5", "Rain": "500-800mm", "Tip": "High export value."},
    "BANANA": {"N": 100, "P": 75, "K": 50, "pH": "6.5-7.5", "Rain": "1500-2500mm", "Tip": "Needs lots of water."},
    "MANGO": {"N": 20, "P": 20, "K": 30, "pH": "4.5-7.0", "Rain": "750-1000mm", "Tip": "Thrives in tropical climate."},
    "GRAPES": {"N": 50, "P": 30, "K": 80, "pH": "6.5-7.5", "Rain": "400-600mm", "Tip": "Potassium helps sweetness."},
    "WATERMELON": {"N": 100, "P": 10, "K": 50, "pH": "6.0-7.0", "Rain": "400-500mm", "Tip": "Requires sandy soil."},
    "MUSKMELON": {"N": 100, "P": 10, "K": 50, "pH": "6.0-6.7", "Rain": "400-600mm", "Tip": "Sunlight is critical."},
    "APPLE": {"N": 20, "P": 120, "K": 200, "pH": "5.5-6.5", "Rain": "1000-1500mm", "Tip": "Needs cool winters."},
    "ORANGE": {"N": 20, "P": 10, "K": 10, "pH": "5.5-6.5", "Rain": "1000-1500mm", "Tip": "Citrus needs well-drained soil."},
    "PAPAYA": {"N": 50, "P": 50, "K": 50, "pH": "5.5-6.5", "Rain": "1500-2000mm", "Tip": "Fast growing, needs warmth."},
    "COCONUT": {"N": 20, "P": 10, "K": 30, "pH": "5.0-8.0", "Rain": "1500-2500mm", "Tip": "Coastal soil is best."},
    "COTTON": {"N": 100, "P": 50, "K": 50, "pH": "5.5-7.5", "Rain": "500-1000mm", "Tip": "Avoid excess late N."},
    "JUTE": {"N": 80, "P": 40, "K": 40, "pH": "6.0-7.0", "Rain": "1200-1500mm", "Tip": "Golden fiber needs humid heat."},
    "COFFEE": {"N": 100, "P": 20, "K": 30, "pH": "6.0-7.0", "Rain": "1500-2000mm", "Tip": "Requires shade."}
}

CROP_MAPPER = {
    "RICE": "Paddy(Dhan)(Common)", "MAIZE": "Maize", "CHICKPEA": "Gram Raw(Whole)",
    "KIDNEYBEANS": "Rajmah", "PIGEONPEAS": "Arhar (Tur/Red Gram)", "MOTHBEANS": "Bhallar",
    "MUNGBEAN": "Moong(Green Gram)(Whole)", "BLACKGRAM": "Black Gram (Urd Beans)(Whole)",
    "LENTIL": "Masur Dal", "POMEGRANATE": "Pomegranate", "BANANA": "Banana",
    "MANGO": "Mango", "GRAPES": "Grapes", "WATERMELON": "Watermelon",
    "MUSKMELON": "Muskmelon", "APPLE": "Apple", "ORANGE": "Orange",
    "PAPAYA": "Papaya", "COCONUT": "Coconut", "COTTON": "Cotton",
    "JUTE": "Jute", "COFFEE": "Coffee"
}

FALLBACK_PRICES = {
    "RICE": 2183, "MAIZE": 2090, "CHICKPEA": 5335, "KIDNEYBEANS": 8500,
    "PIGEONPEAS": 7000, "MOTHBEANS": 6000, "MUNGBEAN": 7755, "BLACKGRAM": 6950,
    "LENTIL": 6000, "POMEGRANATE": 7500, "BANANA": 2500, "MANGO": 4000,
    "GRAPES": 8500, "WATERMELON": 1500, "MUSKMELON": 2000, "APPLE": 9000,
    "ORANGE": 4500, "PAPAYA": 2500, "COCONUT": 3000, "COTTON": 6620,
    "JUTE": 5050, "COFFEE": 12500
}

# --- HELPER FUNCTIONS ---
def get_live_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("cod") == 200:
            return {
                "temp": response["main"]["temp"],
                "hum": response["main"]["humidity"],
                "desc": response["weather"][0]["description"].title()
            }
    except: return None

@st.cache_data(ttl=3600)
def fetch_live_market_data(crop_name):
    commodity = CROP_MAPPER.get(crop_name)
    if not commodity:
        return {"price": FALLBACK_PRICES.get(crop_name, "N/A"), "market": "Standard Market", "state": "National Average", "date": "N/A", "is_live": False}

    resource_id = "9ef273d1-c141-414e-b246-e0e64332305c"
    url = f"https://api.data.gov.in/resource/{resource_id}?api-key={DATA_GOV_API_KEY}&format=json&filters[commodity]={commodity}"
    
    try:
        response = requests.get(url).json()
        if response.get('records') and len(response['records']) > 0:
            data = response['records'][0]
            return {"price": data['modal_price'], "market": data['market'], "state": data['state'], "date": data['arrival_date'], "is_live": True}
    except: pass
    
    return {"price": FALLBACK_PRICES.get(crop_name, "N/A"), "market": "Standard Market", "state": "National Average", "date": datetime.now().strftime("%d/%m/%Y"), "is_live": False}

def generate_pdf(crop_list, data_dict, fert_advice, market_info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AgriSmart Pro - Comprehensive Farm Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Primary Recommendation: {crop_list[0]}", ln=True)
    if market_info:
        pdf.cell(200, 10, txt=f"Market Price: Rs. {market_info['price']} / Quintal", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    for key, val in data_dict.items():
        pdf.cell(200, 8, txt=f"{key}: {val}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

@st.cache_resource
def load_assets():
    try:
        model = pickle.load(open("crop_model.pkl", "rb"))
        scaler = pickle.load(open("scaler.pkl", "rb"))
        return model, scaler
    except: return None, None

model, scaler = load_assets()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2942/2942544.png", width=80)
    st.title("Control Panel")
    app_mode = st.radio("Select Application Mode:", ["Predict Crop", "Crop Intelligence"])

# --- MODE 1: PREDICTION ---
if app_mode == "Predict Crop":
    st.markdown("<h1 style='color: #4CAF50;'>🌾 Precision Crop Prediction</h1>", unsafe_allow_html=True)
    
    with st.expander("📍 Auto-fill Weather Data via City"):
        city_input = st.text_input("Enter City Name")
        if st.button("Fetch Live Weather"):
            w_data = get_live_weather(city_input)
            if w_data:
                st.session_state['temp'], st.session_state['hum'] = w_data['temp'], w_data['hum']
                st.success(f"Weather in {city_input}: {w_data['desc']}")
            else: st.error("City not found.")

    st.write("---")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("🧪 Soil Nutrients")
        N = st.number_input("Nitrogen (N)", 0, 200, 90)
        P = st.number_input("Phosphorus (P)", 0, 200, 42)
        K = st.number_input("Potassium (K)", 0, 200, 43)
        ph = st.slider("Soil pH Level", 0.0, 14.0, 6.5)

    with col2:
        st.subheader("☁️ Environmental Metrics")
        t_val = float(st.session_state.get('temp', 25.0))
        h_val = float(st.session_state.get('hum', 80.0))
        temp = st.slider("Temperature (°C)", 0.0, 50.0, t_val)
        hum = st.slider("Humidity (%)", 0.0, 100.0, h_val)
        rain = st.number_input("Rainfall (mm)", 0.0, 1500.0, 200.0)

    if st.button("🚀 RUN ANALYSIS"):
        if model and scaler:
            features = np.array([[N, P, K, temp, hum, ph, rain]])
            scaled_features = scaler.transform(features)
            
            probs = model.predict_proba(scaled_features)[0]
            top_indices = np.argsort(probs)[-3:][::-1]
            top_crops = [model.classes_[i].upper() for i in top_indices]
            top_probs = [probs[i] for i in top_indices]

            st.markdown("### 🏆 Top Recommendations")
            for i, (crop, prob) in enumerate(zip(top_crops, top_probs)):
                st.markdown(f"""<div class="result-card">
                    <p style="color: #4CAF50; font-size: 14px; font-weight: bold;">OPTION {i+1} ({prob*100:.1f}% Match)</p>
                    <h2 style="color: #FFFFFF; margin: 0;">{crop}</h2></div>""", unsafe_allow_html=True)

            primary_crop = top_crops[0]
            market_info = fetch_live_market_data(primary_crop)
            
            if market_info:
                status_label = "🟢 LIVE MARKET DATA" if market_info['is_live'] else "🟡 ESTIMATED PRICE (Live Offline)"
                st.markdown(f"### {status_label}")
                m1, m2 = st.columns(2)
                m1.metric("Market Price", f"Rs. {market_info['price']} / Quintal")
                m2.info(f"📍 **Source:** {market_info['market']}, {market_info['state']}\n📅 **Updated:** {market_info['date']}")

            fert_advice = []
            if primary_crop in CROP_IDEALS:
                st.markdown("### 🛠️ Fertilizer Gap Analysis")
                ideal = CROP_IDEALS[primary_crop]
                gaps = {"N": ideal['N']-N, "P": ideal['P']-P, "K": ideal['K']-K}
                cols = st.columns(3)
                for i, (nut, gap) in enumerate(gaps.items()):
                    with cols[i]:
                        if gap > 0:
                            msg = f"{nut} Deficit: {gap} units."
                            st.error(msg); fert_advice.append(msg)
                        else:
                            st.success(f"{nut}: Optimal"); fert_advice.append(f"{nut}: Optimal")

            report_dict = {"N": N, "P": P, "K": K, "Temp": temp, "Hum": hum, "pH": ph, "Rain": rain}
            pdf_bytes = generate_pdf(top_crops, report_dict, fert_advice, market_info)
            st.download_button("📥 Download Report (PDF)", data=pdf_bytes, file_name=f"{primary_crop}_report.pdf")
        else: st.error("Model assets missing.")

else:
    st.markdown("<h1 style='color: #4CAF50;'>📖 Crop Intelligence Base</h1>", unsafe_allow_html=True)
    selected_crop = st.selectbox("Search for a crop:", list(CROP_IDEALS.keys()))
    data = CROP_IDEALS[selected_crop]
    st.write("---")
    st.markdown(f"### Ideal Conditions for <span class='green-text'>{selected_crop}</span>", unsafe_allow_html=True)
    st.info(f"**Growth Tip:** {data['Tip']}")

st.markdown("---")
st.caption(f"© {datetime.now().year} AgriSmart Systems | Sustainable Agriculture Data")
