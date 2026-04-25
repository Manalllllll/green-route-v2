import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from influxdb_client import InfluxDBClient
from fpdf import FPDF
import os

st.set_page_config(page_title="Green Route", page_icon="🌱", layout="wide")
st.title("🌱 Green Route — Logistique Durable")
st.markdown("**Industrie 5.0 · Optimisation CO₂ · IoT en temps réel**")
st.divider()

points = [
    {"nom": "Entrepôt Central",           "lat": 33.5731, "lon": -7.5898},
    {"nom": "Livraison 1 — Casa Centre",  "lat": 33.5892, "lon": -7.6031},
    {"nom": "Livraison 2 — Ain Diab",     "lat": 33.5950, "lon": -7.6700},
    {"nom": "Livraison 3 — Hay Hassani",  "lat": 33.5500, "lon": -7.6500},
    {"nom": "Livraison 4 — Sidi Maarouf", "lat": 33.5300, "lon": -7.6200},
    {"nom": "Livraison 5 — Bouskoura",    "lat": 33.4500, "lon": -7.6400},
]

def lire_donnees():
    try:
        url    = st.secrets["INFLUX_URL"]
        token  = st.secrets["INFLUX_TOKEN"]
        org    = st.secrets["INFLUX_ORG"]
        bucket = st.secrets["INFLUX_BUCKET"]
        client = InfluxDBClient(url=url, token=token, org=org)
        query = f'''
        from(bucket: "{bucket}")
        |> range(start: -1m)
        |> filter(fn: (r) => r._measurement == "camion")
        |> last()
        '''
        tables = client.query_api().query(query, org=org)
        result = {}
        for table in tables:
            for record in table.records:
                result[record.get_field()] = record.get_value()
        if result:
            return result
    except Exception as e:
        st.error(f"Erreur : {e}")
    return {"vitesse": 0, "co2": 0, "carburant": 100, "stop": 1}

with st.spinner("📡 Connexion InfluxDB..."):
    donnees = lire_donnees()

co2_val     = donnees.get("co2", 0)
vitesse_val = donnees.get("vitesse", 0)
carb_val    = donnees.get("carburant", 100)
stop_val    = donnees.get("stop", 1)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Carte des livraisons")
    carte = folium.Map(location=[33.5731, -7.5898], zoom_start=11)
    stop_actuel = int(stop_val)
    for i, p in enumerate(points):
        if i == 0:
            couleur = "blue"
        elif i == stop_actuel:
            couleur = "red"
        elif i < stop_actuel:
            couleur = "gray"
        else:
            couleur = "green"
        folium.Marker(
            location=[p["lat"], p["lon"]],
            popup=p["nom"], tooltip=p["nom"],
            icon=folium.Icon(color=couleur)
        ).add_to(carte)
    folium.PolyLine([(p["lat"], p["lon"]) for p in points], color="green", weight=3).add_to(carte)
    st_folium(carte, width=700, height=400)

with col2:
    st.subheader("📡 Données du camion")
    if co2_val >= 9:
        st.error(f"🔴 ALERTE CO₂ ÉLEVÉ : {co2_val:.2f} kg")
    elif co2_val >= 6:
        st.warning(f"🟡 CO₂ Moyen : {co2_val:.2f} kg")
    elif co2_val > 0:
        st.success(f"🟢 CO₂ Faible : {co2_val:.2f} kg")
    else:
        st.info("⏳ En attente des données...")
    st.metric("🚛 Vitesse",     f"{vitesse_val:.0f} km/h")
    st.metric("⛽ Carburant",   f"{carb_val:.1f} L")
    st.metric("📍 Stop actuel", f"Livraison {int(stop_val)}")
    if co2_val > 0:
        arbres = round((10 - co2_val) * 0.3, 1)
        if arbres > 0:
            st.info(f"🌳 Économise **{arbres} arbres** vs route rapide !")

st.divider()
st.subheader("📊 Comparaison CO₂ — Route rapide vs Route verte")
df = pd.DataFrame({
    "Stop": ["Stop 1", "Stop 2", "Stop 3", "Stop 4", "Stop 5"],
    "CO2 Route Rapide (kg)": [10.2, 9.8, 11.1, 10.5, 9.9],
    "CO2 Route Verte (kg)":  [7.1,  6.8,  7.5,  6.9,  7.2],
})
st.bar_chart(df.set_index("Stop"))

st.divider()
st.subheader("💬 Assistant Green Route")
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt := st.chat_input("Pose une question sur la tournée..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    reponse = f"""🤖 Analyse de la tournée :
- Vitesse : **{vitesse_val:.0f} km/h**
- CO₂ émis : **{co2_val:.2f} kg**"""
    if co2_val >= 9:
        reponse += "\n- ⚠️ CO₂ trop élevé — réduire la vitesse !"
    elif co2_val >= 6:
        reponse += "\n- 🟡 CO₂ moyen — route optimisable"
    else:
        reponse += "\n- 🟢 Excellente conduite écologique !"
    reponse += f"\n- 🌳 Économise **{round((10-co2_val)*0.3,1)} arbres** vs route rapide !"
    with st.chat_message("assistant"):
        st.markdown(reponse)
    st.session_state.messages.append({"role": "assistant", "content": reponse})

st.divider()
st.subheader("📄 Rapport PDF")
if st.button("📥 Générer le rapport PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Green Route - Rapport de Tournee", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Vitesse : {vitesse_val:.0f} km/h", ln=True)
    pdf.cell(200, 10, f"CO2 emis : {co2_val:.2f} kg", ln=True)
    pdf.cell(200, 10, f"Carburant restant : {carb_val:.1f} L", ln=True)
    pdf.cell(200, 10, f"Stop actuel : Livraison {int(stop_val)}", ln=True)
    pdf.ln(10)
    if co2_val >= 9:
        pdf.cell(200, 10, "ALERTE : CO2 trop eleve !", ln=True)
    elif co2_val >= 6:
        pdf.cell(200, 10, "Attention : CO2 moyen", ln=True)
    else:
        pdf.cell(200, 10, "Excellent : CO2 faible !", ln=True)
    pdf.ln(10)
    arbres = round((10 - co2_val) * 0.3, 1)
    pdf.cell(200, 10, f"Economies : {arbres} arbres vs route rapide", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, "Green Route - Industrie 5.0 - Manal Fartah", ln=True, align="C")
    pdf.output("rapport_green_route.pdf")
    st.success("✅ Rapport PDF généré !")

st.divider()
st.markdown("🌱 **Green Route** · Industrie 5.0 · Manal FARTAH")
if st.button("🔄 Rafraîchir"):
    st.rerun()