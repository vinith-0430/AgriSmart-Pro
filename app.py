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
        min-height: 120px;
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
    resource_id = "9ef273d1-c141-414e-b246-e0e64332305c"
    url = f"https://api.data.gov.in/resource/{resource_id}?api-key={DATA_GOV_API_KEY}&format=json&filters[commodity]={commodity}"
    
    try:
        response = requests.get(url).json()
        if response.get('records') and len(response['records']) > 0:
            data = response['records'][0]
            return {"price": data['modal_price'], "market": data['market'], "state": data['state'], "date": data['arrival_date'], "is_live": True}
    except: pass
    
    return {"price": FALLBACK_PRICES.get(crop_name, "N/A"), "market": "Standard Market", "state": "National Average", "date": datetime.now().strftime("%d/%m/%Y"), "is_live": False}

def generate_pdf(crop_name, input_data, fert_advice, market_info):
    pdf = FPDF()
    pdf.add_page()
    
    # --- STYLING ---
    PRIMARY_COLOR = (46, 125, 50)  # Dark Green
    SECONDARY_COLOR = (240, 242, 246) # Light Grey
    TEXT_COLOR = (40, 40, 40)
    
    # --- HEADER ---
    pdf.set_fill_color(*PRIMARY_COLOR)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, "AgriSmart Pro Analysis", ln=True, align='C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%d %b %Y | %H:%M')}", ln=True, align='C')
    pdf.ln(20)

    # --- MAIN CONTENT ---
    pdf.set_text_color(*TEXT_COLOR)
    
    # Crop Title
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, f"Analysis Report: {crop_name}", ln=True)
    pdf.set_draw_color(*PRIMARY_COLOR)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # --- MARKET INSIGHTS SECTION ---
    pdf.set_fill_color(*SECONDARY_COLOR)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "  Market Intelligence", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(95, 8, f"Price: Rs. {market_info['price']} / Quintal")
    pdf.cell(95, 8, f"Status: {'Live' if market_info['is_live'] else 'Estimated'}", ln=True)
    pdf.cell(95, 8, f"Market: {market_info['market']}")
    pdf.cell(95, 8, f"State: {market_info['state']}", ln=True)
    pdf.ln(8)

    # --- SOIL & ENVIRONMENT SECTION ---
    pdf.set_fill_color(*SECONDARY_COLOR)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "  Field Conditions & Input Data", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 11)
    col_width = 90
    items = list(input_data.items())
    for i in range(0, len(items), 2):
        k1, v1 = items[i]
        pdf.cell(col_width, 8, f"{k1}: {v1}")
        if i+1 < len(items):
            k2, v2 = items[i+1]
            pdf.cell(col_width, 8, f"{k2}: {v2}")
        pdf.ln(8)
    
    pdf.ln(8)

    # --- FERTILIZER ADVICE SECTION ---
    pdf.set_fill_color(*SECONDARY_COLOR)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "  Actionable Fertilizer Recommendations", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", 'I', 11)
    for line in fert_advice:
        if "Deficit" in line:
            pdf.set_text_color(200, 0, 0) 
            pdf.cell(0, 8, f"! {line}", ln=True)
        else:
            pdf.set_text_color(0, 128, 0) 
            pdf.cell(0, 8, f"Check: {line}", ln=True)
            
    pdf.set_text_color(*TEXT_COLOR)
    pdf.ln(10)

    # --- FOOTER ---
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, "AgriSmart Systems - Empowering Sustainable Agriculture", align='C')

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
        rain = st.number_input("Rainfall (mm)", 0.0, 2000.0, 200.0)

    if st.button("🚀 RUN ANALYSIS"):
        if model and scaler:
            features = np.array([[N, P, K, temp, hum, ph, rain]])
            scaled_features = scaler.transform(features)
            probs = model.predict_proba(scaled_features)[0]
            top_indices = np.argsort(probs)[-3:][::-1]
            
            st.session_state['top_crops'] = [model.classes_[i].upper() for i in top_indices]
            st.session_state['top_probs'] = [probs[i] for i in top_indices]
            st.session_state['ready'] = True

    if st.session_state.get('ready'):
        st.markdown("### 🏆 Top Recommendations")
        c1, c2, c3 = st.columns(3)
        for i, (crop, prob) in enumerate(zip(st.session_state['top_crops'], st.session_state['top_probs'])):
            with [c1, c2, c3][i]:
                st.markdown(f"""<div class="result-card">
                    <p style="color: #4CAF50; font-size: 12px; font-weight: bold;">OPTION {i+1}</p>
                    <h3 style="margin:0;">{crop}</h3>
                    <p style="font-size: 14px;">{prob*100:.1f}% Match</p></div>""", unsafe_allow_html=True)

        st.write("---")
        selected_crop = st.radio(
            "👉 **Select a crop below to view its Live Market Price & Fertilizer Needs:**",
            st.session_state['top_crops'], horizontal=True
        )

        market_info = fetch_live_market_data(selected_crop)
        
        if market_info:
            status = "🟢 LIVE" if market_info['is_live'] else "🟡 ESTIMATED"
            st.markdown(f"### {status} Market Insights for {selected_crop}")
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Current Market Price", f"Rs. {market_info['price']} / Quintal")
            m_col2.info(f"📍 **Market:** {market_info['market']}, {market_info['state']}\n📅 **Updated:** {market_info['date']}")

        if selected_crop in CROP_IDEALS:
            st.markdown(f"### 🛠️ Fertilizer Analysis for {selected_crop}")
            ideal = CROP_IDEALS[selected_crop]
            gaps = {"Nitrogen": ideal['N']-N, "Phosphorus": ideal['P']-P, "Potassium": ideal['K']-K}
            f_cols = st.columns(3)
            advice_list = []
            for i, (nut, gap) in enumerate(gaps.items()):
                with f_cols[i]:
                    if gap > 0:
                        msg = f"{nut} Deficit: {gap} units"
                        st.error(msg); advice_list.append(msg)
                    else:
                        msg = f"{nut}: Optimal"
                        st.success(msg); advice_list.append(msg)

            # PDF Download Logic
            report_dict = {
                "Nitrogen (N)": N, "Phosphorus (P)": P, "Potassium (K)": K, 
                "Temperature": f"{temp}°C", "Humidity": f"{hum}%", 
                "pH Level": ph, "Rainfall": f"{rain}mm"
            }
            pdf_bytes = generate_pdf(selected_crop, report_dict, advice_list, market_info)
            st.download_button(
                label=f"📥 Download {selected_crop} Intelligence Report (PDF)",
                data=pdf_bytes,
                file_name=f"{selected_crop}_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

else:
    st.markdown("<h1 style='color: #4CAF50;'>📖 Crop Intelligence Base</h1>", unsafe_allow_html=True)
    selected_crop = st.selectbox("Search for a crop:", list(CROP_IDEALS.keys()))
    data = CROP_IDEALS[selected_crop]
    st.write("---")
    st.markdown(f"### Ideal Conditions for <span class='green-text'>{selected_crop}</span>", unsafe_allow_html=True)
    st.info(f"**Growth Tip:** {data['Tip']}")

st.markdown("---")
st.caption(f"© {datetime.now().year} AgriSmart Systems | Sustainable Agriculture Data")
