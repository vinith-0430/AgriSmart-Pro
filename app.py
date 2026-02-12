import streamlit as st
import numpy as np
import pandas as pd
import pickle
import requests
from fpdf import FPDF

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AgriSmart Pro | Intelligence Dashboard",
    page_icon="🌿",
    layout="wide"
)

# --- CONFIG & API KEYS ---
API_KEY = "c39514d4a14765b3dae51ceaa920491c"

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
    .requirement-box {
        background-color: #161B22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #4CAF50;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CROP KNOWLEDGE DATA (Updated with Price & Season) ---
CROP_DATA = {
    "RICE": {"N": 80, "P": 40, "K": 40, "pH": "5.5-6.5", "Rain": "1000mm+", "Price": 2183, "Season": "Kharif", "Tip": "Maintain standing water during vegetative stage."},
    "MAIZE": {"N": 100, "P": 50, "K": 30, "pH": "6.0-7.0", "Rain": "500-800mm", "Price": 2090, "Season": "Kharif", "Tip": "Ensure good drainage; avoid waterlogging."},
    "WHEAT": {"N": 120, "P": 60, "K": 40, "pH": "6.0-7.5", "Rain": "450-650mm", "Price": 2275, "Season": "Rabi", "Tip": "Requires cool weather during early growth."},
    "COTTON": {"N": 100, "P": 50, "K": 50, "pH": "5.5-7.5", "Rain": "500-1000mm", "Price": 6620, "Season": "Kharif", "Tip": "Avoid excess Nitrogen late in the season."},
    "GRAPES": {"N": 50, "P": 30, "K": 80, "pH": "6.5-7.5", "Rain": "400-600mm", "Price": 8500, "Season": "Perennial", "Tip": "High Potassium is key for sugar content."},
    "COFFEE": {"N": 100, "P": 20, "K": 30, "pH": "6.0-7.0", "Rain": "1500-2000mm", "Price": 12000, "Season": "Perennial", "Tip": "Requires shade and well-distributed rainfall."}
}

# --- HELPER FUNCTIONS ---
def get_live_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("cod") == 200:
            return {
                "temp": response["main"]["temp"],
                "hum": response["main"]["humidity"],
                "desc": response["weather"][0]["description"].title()
            }
    except: return None
    return None

def generate_pdf(crop_list, data_dict, fertilizer_advice):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AgriSmart Pro - Farm Analysis Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Primary Recommendation: {crop_list[0]}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    for key, val in data_dict.items():
        pdf.cell(200, 8, txt=f"{key}: {val}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(200, 10, txt="Fertilizer Gap Analysis (Top Crop):", ln=True)
    pdf.set_font("Arial", size=10)
    for line in fertilizer_advice:
        pdf.cell(200, 8, txt=line, ln=True)
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
    app_mode = st.radio("Select Application Mode:", ["Predict Crop", "Crop Requirements"], index=0)

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
        rain = st.number_input("Rainfall (mm)", 0.0, 500.0, 200.0)

    if st.button("🚀 RUN ANALYSIS"):
        if model and scaler:
            features = np.array([[N, P, K, temp, hum, ph, rain]])
            scaled_features = scaler.transform(features)
            
            # --- TOP 3 RECOMMENDATIONS LOGIC ---
            probs = model.predict_proba(scaled_features)[0]
            top_indices = np.argsort(probs)[-3:][::-1]
            top_crops = [model.classes_[i].upper() for i in top_indices]
            top_probs = [probs[i] for i in top_indices]

            st.markdown("### 🏆 Top Recommendations")
            for i, (crop, prob) in enumerate(zip(top_crops, top_probs)):
                st.markdown(f"""
                    <div class="result-card">
                        <p style="color: #4CAF50; font-size: 14px; font-weight: bold;">OPTION {i+1} ({prob*100:.1f}% Match)</p>
                        <h2 style="color: #FFFFFF; margin: 0;">{crop}</h2>
                    </div>
                """, unsafe_allow_html=True)

            # --- FINANCIAL FORECAST (Primary Crop) ---
            primary_crop = top_crops[0]
            if primary_crop in CROP_DATA:
                st.markdown("### 💰 Financial Forecast")
                c_data = CROP_DATA[primary_crop]
                f1, f2 = st.columns(2)
                f1.metric("Estimated Market Price", f"₹{c_data['Price']} / Quintal")
                f2.info(f"**Optimal Season:** {c_data['Season']}")

            # --- FERTILIZER LOGIC (Primary Crop) ---
            fert_advice = []
            if primary_crop in CROP_DATA:
                st.markdown("### 🛠️ Fertilizer Gap Analysis")
                ideal = CROP_DATA[primary_crop]
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
            pdf_bytes = generate_pdf(top_crops, report_dict, fert_advice)
            st.download_button("📥 Download Report (PDF)", data=pdf_bytes, file_name=f"{primary_crop}_report.pdf")
        else: st.error("Model assets missing.")

else:
    st.markdown("<h1 style='color: #4CAF50;'>📖 Crop Intelligence Base</h1>", unsafe_allow_html=True)
    selected_crop = st.selectbox("Search for a crop:", list(CROP_DATA.keys()))
    data = CROP_DATA[selected_crop]
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### Ideal Conditions for <span class='green-text'>{selected_crop}</span>", unsafe_allow_html=True)
        st.markdown(f"""<div class="requirement-box"><b>N-P-K:</b> {data['N']}-{data['P']}-{data['K']}<br><b>pH:</b> {data['pH']}<br><b>Rain:</b> {data['Rain']}</div>""", unsafe_allow_html=True)
    with c2:
        st.info(f"**Growth Tip:** {data['Tip']}")

st.markdown("---")
st.caption("© 2026 AgriSmart Systems | Sustainable Agriculture Data")
