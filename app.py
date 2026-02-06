import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

st.set_page_config(page_title="Intervention Planner - Neemba", layout="wide")

st.title("🚜 Intervention Planner - Optimisation Logistique")

# 1. Sidebar pour l'importation des données
with st.sidebar:
    st.header("Données Source")
    file_vl = st.file_uploader("Base Vision Link (Localisation)", type=['xlsx', 'csv'])
    file_tasks = st.file_uploader("Programmes (SOS, PSSR, Remote)", type=['xlsx', 'csv'])
    
    rayon_km = st.slider("Rayon d'optimisation (km)", 5, 50, 20)

# 2. Simulation de données (à remplacer par vos extractions)
if file_vl and file_tasks:
    # Lecture des données
    df_geo = pd.read_excel(file_vl) # Doit contenir S/N, Client, LAT, LONG
    df_tasks = pd.read_excel(file_tasks) # Doit contenir S/N, Type_Intervention
    
    # Jointure
    df_master = pd.merge(df_geo, df_tasks, on="S/N", how="inner")
    
    # 3. Interface de Planification
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Planifier une mission")
        client_selection = st.selectbox("Sélectionner un Client", df_master['Client'].unique())
        machine_selection = st.selectbox("Machine cible", df_master[df_master['Client'] == client_selection]['S/N'])
        
        target_coords = (df_master[df_master['S/N'] == machine_selection]['LATITUDE'].iloc[0], 
                         df_master[df_master['S/N'] == machine_selection]['LONGITUDE'].iloc[0])
        
        if st.button("Calculer Optimisation"):
            # Logique d'optimisation
            df_master['Distance'] = df_master.apply(
                lambda row: geodesic(target_coords, (row['LATITUDE'], row['LONGITUDE'])).km, axis=1
            )
            
            suggestions = df_master[(df_master['Distance'] <= rayon_km) & (df_master['S/N'] != machine_selection)]
            
            st.success(f"Trouvé {len(suggestions)} opportunités à proximité !")
            st.dataframe(suggestions[['Client', 'S/N', 'Type_Intervention', 'Distance']])

    with col2:
        # Carte interactive
        m = folium.Map(location=[target_coords[0], target_coords[1]], zoom_start=9)
        folium.Marker(target_coords, tooltip="Intervention Principale", icon=folium.Icon(color='red')).add_to(m)
        
        for idx, row in suggestions.iterrows():
            folium.Marker(
                [row['LATITUDE'], row['LONGITUDE']],
                tooltip=f"{row['Client']} - {row['Type_Intervention']}",
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)
            
        st_folium(m, width=700, height=500)
