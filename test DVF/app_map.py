import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.distance import geodesic
import io # Pour gérer le fichier CSV directement en mémoire

# --- Configuration de la page Streamlit ---
st.set_page_config(layout="wide")
st.title("Visualisation des Mutations Immobilières")

# --- Votre jeu de données (simulé ici, mais vous utiliserez votre fichier téléchargé) ---
# En temps normal, vous auriez déjà votre fichier 'full.csv' téléchargé
# Ici, je simule la lecture du CSV que vous avez fourni
csv_data = """id_mutation,date_mutation,numero_disposition,nature_mutation,valeur_fonciere,adresse_numero,adresse_suffixe,adresse_nom_voie,adresse_code_voie,code_postal,type_local,surface_reelle_bati,nombre_pieces_principales,code_nature_culture,nature_culture,code_nature_culture_speciale,nature_culture_speciale,surface_terrain,longitude,latitude
0,2024-1,2024-01-02,1,Vente,346.5,NaN,NaN,LE DELIVRE,B020,1230.0,,,NaN,NaN,NaN,P,prés,,,99.0,5.53095245,45.952439
1,2024-2,2024-01-03,2,Vente,10000.0,NaN,NaN,CHEVRY DESSOUS,B007,1170.0,,,NaN,NaN,NaN,NaN,Ssols,,,115.0,6.04333946,46.282256
2,2024-3,2024-01-08,1,Vente,249000.0,NaN,NaN,PIN HAMEAU,B086,1290.0,,,NaN,NaN,NaN,NaN,Ssols,,,497.0,4.91114346,46.247235
3,2024-4,2024-01-03,1,Vente,329500.0,9001.0,NaN,PL DU JURA,0500,1170.0,,,Dépendance,,,0.0,NaN,NaN,NaN,6.058695,46.332212
4,2024-4,2024-01-03,1,Vente,329500.0,29.0,NaN,PL DU JURA,0500,1170.0,,,Dépendance,,,0.0,NaN,NaN,NaN,6.058695,46.332212
3458638,2024-12,1806,2024-11-28,1,Vente,4550000.0,147.0,NaN,RUE DE CHARENTON,1794.0,75012.0,,Appartement,23.0,2.0,Ssols,,,NaN,NaN,323.0,2.382241,48.845284
3458639,2024-12,1806,2024-11-28,1,Vente,4550000.0,147.0,NaN,RUE DE CHARENTON,1794.0,75012.0,,Appartement,23.0,2.0,Ssols,,,NaN,NaN,323.0,2.382241,48.845284
3458640,2024-12,1806,2024-11-28,1,Vente,4550000.0,147.0,NaN,RUE DE CHARENTON,1794.0,75012.0,,Appartement,23.0,2.0,Ssols,,,NaN,NaN,323.0,2.382241,48.845284
3458641,2024-12,1806,2024-11-28,1,Vente,4550000.0,147.0,NaN,RUE DE CHARENTON,1794.0,75012.0,,Appartement,23.0,2.0,Ssols,,,NaN,NaN,323.0,2.382241,48.845284
3458642,2024-12,1806,2024-11-28,1,Vente,4550000.0,147.0,NaN,RUE DE CHARENTON,1794.0,75012.0,,Local industriel. commercial ou assimilé,42.0,0.0,Ssols,,,NaN,NaN,323.0,2.382241,48.845284
"""

# Utilisez StringIO pour simuler la lecture du fichier téléchargé 'full.csv'
# Dans votre cas réel, après le téléchargement, vous feriez :
# df_dvf = pd.read_csv('full.csv', sep=',') # ou le bon délimiteur
try:
    df_dvf = pd.read_csv(io.StringIO(csv_data), sep=',')
    
    # Nettoyage des colonnes de lat/lon (convertir en numérique et supprimer les NaN)
    df_dvf['latitude'] = pd.to_numeric(df_dvf['latitude'], errors='coerce')
    df_dvf['longitude'] = pd.to_numeric(df_dvf['longitude'], errors='coerce')
    df_dvf.dropna(subset=['latitude', 'longitude'], inplace=True)
    
    st.success("Données de mutations chargées avec succès !")
    # st.dataframe(df_dvf.head()) # Décommentez pour voir les premières lignes du DataFrame
except Exception as e:
    st.error(f"Erreur lors du chargement des données CSV : {e}")
    st.stop() # Arrête l'exécution si le chargement échoue

# --- Saisie des coordonnées par l'utilisateur ---
st.sidebar.header("Point Central de Recherche")
default_lat = 48.8566 # Latitude par défaut (Paris)
default_lon = 2.3522  # Longitude par défaut (Paris)

input_lat = st.sidebar.number_input("Latitude du point central :", value=default_lat, format="%.6f")
input_lon = st.sidebar.number_input("Longitude du point central :", value=default_lon, format="%.6f")
search_radius_meters = st.sidebar.slider("Rayon de recherche (mètres) :", min_value=50, max_value=2000, value=200, step=50)

# --- Filtrage des mutations ---
# Créer un point de référence à partir de l'entrée utilisateur
center_point = (input_lat, input_lon)

# Filtrer les mutations dans le rayon spécifié
mutations_in_radius = []
for index, row in df_dvf.iterrows():
    mutation_point = (row['latitude'], row['longitude'])
    distance = geodesic(center_point, mutation_point).meters
    if distance <= search_radius_meters:
        mutations_in_radius.append(row)

df_filtered = pd.DataFrame(mutations_in_radius)

st.subheader(f"Mutations trouvées dans un rayon de {search_radius_meters} mètres:")
st.write(f"Nombre de mutations trouvées : **{len(df_filtered)}**")

if not df_filtered.empty:
    st.dataframe(df_filtered[['date_mutation', 'valeur_fonciere', 'adresse_nom_voie', 'latitude', 'longitude']])
else:
    st.info("Aucune mutation trouvée dans ce rayon.")

# --- Affichage de la carte ---
st.subheader("Carte des Mutations")

# Créer une carte Folium centrée sur le point de recherche
m = folium.Map(location=[input_lat, input_lon], zoom_start=15)

# Ajouter le cercle de rayon
folium.Circle(
    location=center_point,
    radius=search_radius_meters,
    color='blue',
    fill=True,
    fill_color='blue',
    fill_opacity=0.1,
    tooltip=f"{search_radius_meters} mètres"
).add_to(m)

# Ajouter un marqueur pour le point central
folium.Marker(
    location=center_point,
    popup=f"Point central<br>Lat: {input_lat:.4f}<br>Lon: {input_lon:.4f}",
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(m)


# Ajouter les mutations filtrées sur la carte
if not df_filtered.empty:
    marker_cluster = MarkerCluster().add_to(m)
    for idx, row in df_filtered.iterrows():
        # Créer un popup avec les informations importantes
        popup_html = f"""
        <b>Date:</b> {row['date_mutation']}<br>
        <b>Valeur:</b> {row['valeur_fonciere']}<br>
        <b>Adresse:</b> {row['adresse_numero'] if pd.notna(row['adresse_numero']) else ''} {row['adresse_nom_voie']}<br>
        <b>Code Postal:</b> {row['code_postal']}<br>
        <b>Type Local:</b> {row['type_local'] if pd.notna(row['type_local']) else 'N/A'}<br>
        <b>Surface Terrain:</b> {row['surface_terrain'] if pd.notna(row['surface_terrain']) else 'N/A'} m²
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(marker_cluster)

# Afficher la carte dans Streamlit
from streamlit_folium import st_folium
st_folium(m, width=1000, height=600)