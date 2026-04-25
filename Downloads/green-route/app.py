import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import json
import os
import time

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
        chemin = r"C:\Users\Manal Fartah\Downloads\green-route\donnees.json"
        if os.path.exists(chemin):
            with open(chemin, "r") as f:
                return json.load(f)
    except:
        pass
    return {"vitesse": 0, "co2": 0, "carburant": 100, "stop": 1}

donnees = lire_donnees()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Carte des livraisons")
    carte = folium.Map(location=[33.5731, -7.5898], zoom_start=11)
    stop_actuel = int(donnees.get("stop", 1))

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
    co2_val     = donnees.get("co2", 0)
    vitesse_val = donnees.get("vitesse", 0)
    carb_val    = donnees.get("carburant", 100)
    stop_val    = donnees.get("stop", 1)

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
st.caption("Route verte = moins de CO₂ à chaque livraison")
st.divider()
st.markdown("🌱 **Green Route** · Industrie 5.0 · Manal FARTAH")

if st.button("🔄 Rafraîchir les données"):
    st.rerun()

# Rafraîchissement automatique toutes les 3 secondes
time.sleep(3)
st.rerun()