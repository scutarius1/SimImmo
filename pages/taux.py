import requests
from bs4 import BeautifulSoup
import streamlit as st


# -------------------- Fonction de scraping -------------------- #
def get_meilleurtaux_rate():
    """
    Récupère le taux moyen immobilier sur 15 ans depuis le site Meilleurtaux.
    """
    url = "https://www.meilleurtaux.com/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        credit_immobilier_card = soup.find('a', class_='cards fc', href='/demande-simulation/credit-immobilier/')
        if credit_immobilier_card:
            foot_div = credit_immobilier_card.find('div', class_='foot')
            if foot_div:
                rate_tag = foot_div.find('b')
                if rate_tag:
                    rate_text = rate_tag.get_text(strip=True)
                    cleaned_rate = rate_text.replace(',', '.').replace('%', '').strip()
                    return cleaned_rate
                else:
                    st.error("Impossible de trouver la balise <b> contenant le taux.")
            else:
                st.error("Impossible de trouver le div 'foot' pour le crédit immobilier.")
        else:
            st.error("Impossible de trouver la carte 'Crédit immobilier'.")
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération de la page web : {e}")
    except Exception as e:
        st.error(f"Une erreur inattendue s'est produite : {e}")
    return None

# -------------------- Interface Streamlit -------------------- #

st.title("Taux Moyen Immobilier ")
st.write("Récupération du taux moyen affiché sur la page d'accueil de Meilleurtaux.com.")

if st.button("Afficher le taux sur Meilleurtaux.com"):
    with st.spinner("Récupération du taux en cours..."):
        taux = get_meilleurtaux_rate()
        if taux:
            st.success(f"Le taux moyen immobilier sur 15 ans est : **{taux} %**")
        else:
            st.warning("Le taux n'a pas pu être récupéré. Veuillez réessayer plus tard ou vérifier la structure du site.")



def get_empruntis_meilleurs_taux():
    """
    Récupère les meilleurs taux immobiliers (15, 20, 25 ans) depuis la page Empruntis.
    Retourne un dictionnaire avec les durées comme clés et les taux en float.
    """
    url = "https://www.empruntis.com/financement/actualites/barometres_regionaux.php"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        bloc_taux = soup.find("div", class_="blocs_meilleur_taux")
        if not bloc_taux:
            st.error("Bloc des meilleurs taux non trouvé sur Empruntis.")
            return None

        taux_dict = {}
        for taux_div in bloc_taux.find_all("div", class_="body_taux"):
            duree = taux_div.find("span", class_="txt_taux")
            taux = taux_div.find("span", class_="taux")
            if duree and taux:
                # Ex: "sur 15 ans(1)" → extraire juste "15 ans"
                duree_text = duree.get_text(strip=True).split('(')[0].replace("sur ", "")
                taux_text = taux.get_text(strip=True).replace('%', '').replace(',', '.')
                try:
                    taux_float = float(taux_text)
                    taux_dict[duree_text] = taux_float
                except ValueError:
                    st.warning(f"Taux non convertible en float : {taux_text}")
        return taux_dict if taux_dict else None

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération de la page Empruntis : {e}")
    except Exception as e:
        st.error(f"Une erreur inattendue s'est produite : {e}")

    return None

if st.button("Actualiser les taux Empruntis"):
    with st.spinner("Récupération des meilleurs taux Empruntis en cours..."):
        taux_empruntis = get_empruntis_meilleurs_taux()
        if taux_empruntis:
            for duree, taux in taux_empruntis.items():
                st.success(f"Meilleur taux immobilier {duree} : **{taux} %**")
        else:
            st.warning("Les taux Empruntis n'ont pas pu être récupérés.")


st.markdown("---")
st.markdown("Note : Le scraping web peut être affecté par les changements de structure du site web cible. Si le taux ne s'affiche plus, le code de scraping pourrait nécessiter une mise à jour :)")


