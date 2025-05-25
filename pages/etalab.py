import streamlit as st

st.title("Visualisation des données DVF")

if st.button("Ouvrir l'application DVF officielle"):
    js = "window.open('https://app.dvf.etalab.gouv.fr/', '_blank').focus();"
    st.components.v1.html(f"<script>{js}</script>")


import streamlit as st
import pandas as pd

st.title("Exploration des données foncières DVF 🏠")

st.markdown("""
Cette page permet d'explorer les transactions immobilières enregistrées dans la base publique **DVF (Demandes de Valeurs Foncières)**.
""")

# ----------- Téléchargement d'un fichier local exemple ----------- #
@st.cache_data
def charger_donnees(departement):
    """
    Charge un fichier CSV DVF pour un département donné.
    Exemple : 'DVF_Paris.csv'
    """
    try:
        df = pd.read_csv(f"data/DVF_{departement}.csv", delimiter='|')
        return df
    except FileNotFoundError:
        st.error(f"Fichier DVF pour le département {departement} introuvable dans le dossier 'data/'.")
        return pd.DataFrame()


# ----------- Sélecteur de département ----------- #
departement = st.selectbox("Choisir un département :", ["75", "13", "33", "69", "59"], format_func=lambda x: f"{x} - {x}")

# Chargement des données
df = charger_donnees(departement)

if not df.empty:
    # Affichage des 100 premières lignes
    st.subheader("Aperçu des transactions foncières")
    st.dataframe(df.head(100))

    # Filtrage par année si colonne 'date_mutation' présente
    if "date_mutation" in df.columns:
        df["date_mutation"] = pd.to_datetime(df["date_mutation"], errors='coerce')
        annees_disponibles = df["date_mutation"].dt.year.dropna().unique()
        annee = st.selectbox("Filtrer par année :", sorted(annees_disponibles, reverse=True))
        df_filtré = df[df["date_mutation"].dt.year == annee]

        st.write(f"Nombre de transactions en {annee} : {len(df_filtré)}")
        st.dataframe(df_filtré.head(50))

else:
    st.warning("Aucune donnée à afficher.")

