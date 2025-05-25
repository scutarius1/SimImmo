import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import re



def calculate_loan(principal, annual_interest_rate, duration_years):
    """
    Calcule les détails du prêt immobilier.

    Args:
        principal (float): Capital emprunté.
        annual_interest_rate (float): Taux d'intérêt annuel en pourcentage.
        duration_years (int): Durée du remboursement en années.

    Returns:
        tuple: (montant_mensualite, cout_total_credit, tableau_amortissement)
    """
    # Convertir le taux d'intérêt annuel en taux mensuel
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    # Convertir la durée en années en mois
    duration_months = duration_years * 12

    if monthly_interest_rate == 0:
        # Cas où le taux d'intérêt est de 0
        monthly_payment = principal / duration_months
        total_cost_of_credit = 0
    else:
        # Calcul de la mensualité (formule d'amortissement)
        monthly_payment = (principal * monthly_interest_rate) / (1 - (1 + monthly_interest_rate)**(-duration_months))
        # Calcul du coût total du crédit
        total_cost_of_credit = (monthly_payment * duration_months) - principal

    # Initialisation des listes pour le tableau d'amortissement
    months = []
    remaining_principal = []
    # Il faut initialiser ces listes pour les données mensuelles
    monthly_principal_paid = []
    monthly_interest_paid = []  
    cumulative_paid_principal = []
    cumulative_paid_interest = []

    current_principal = principal
    cumulative_principal = 0
    cumulative_interest = 0

    # Construction du tableau d'amortissement
    for month in range(1, duration_months + 1):
        interest_for_month = current_principal * monthly_interest_rate
        principal_for_month = monthly_payment - interest_for_month

        # Ajustement pour le dernier mois afin d'éviter un capital restant négatif ou trop faible
        if month == duration_months:
            principal_for_month = current_principal # Le dernier remboursement de capital est ce qui reste dû
            # Assurer que les intérêts ne sont pas négatifs à cause d'erreurs d'arrondi
            interest_for_month = max(0, monthly_payment - principal_for_month)

        current_principal -= principal_for_month
        cumulative_principal += principal_for_month
        cumulative_interest += interest_for_month

        months.append(month)
        remaining_principal.append(max(0, current_principal)) # Assurer que le capital restant ne soit pas négatif
        # ENREGISTRER LES VALEURS MENSUELLES ICI
        monthly_principal_paid.append(principal_for_month) # <--- AJOUTEZ CETTE LIGNE
        monthly_interest_paid.append(interest_for_month)  # <--- AJOUTEZ CETTE LIGNE
        cumulative_paid_principal.append(cumulative_principal)
        cumulative_paid_interest.append(cumulative_interest)

    # Création unique du DataFrame pour le tableau d'amortissement
 
    amortization_df = pd.DataFrame({
        'Mois': months,
        'Capital restant dû': remaining_principal,
        'Capital remboursé (cumulé)': cumulative_paid_principal,
        'Intérêts payés (cumulés)': cumulative_paid_interest,
        'Capital remboursé du mois': monthly_principal_paid, # <--- Ces colonnes sont maintenant définies
        'Intérêts du mois': monthly_interest_paid          # <--- Ces colonnes sont maintenant définies
    })

    return monthly_payment, total_cost_of_credit, amortization_df

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Simulateur de Prêt Immobilier",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏡 Simulateur de Prêt Immobilier")
st.markdown("Calculez les détails de votre prêt et visualisez l'évolution de votre remboursement.")

# Section des entrées utilisateur
st.sidebar.header("Paramètres du Prêt")
principal_loan = st.sidebar.number_input("Capital emprunté (€)", min_value=10000, max_value=10000000, value=250000, step=10000)
interest_rate = st.sidebar.number_input("Taux d'intérêt annuel (%)", min_value=0.1, max_value=10.0, value=1.5, step=0.01)
loan_duration_years = st.sidebar.slider("Durée du remboursement (années)", min_value=1, max_value=30, value=20)

# --- Nouvelle section pour les taux Empruntis ---
st.sidebar.markdown("---")
st.sidebar.header("Taux Actuels du Marché (Empruntis)")

if st.sidebar.button("Récupérer les taux Empruntis 📊"):
    with st.spinner("Récupération des taux Empruntis en cours..."):
        empruntis_rates = get_empruntis_rates()
        if empruntis_rates:
            st.sidebar.subheader("Taux Moyens Empruntis :")
            # Affiche chaque taux trouvé pour les durées spécifiées
            for duration in sorted(empruntis_rates.keys()): # Pour un affichage ordonné
                st.sidebar.success(f"**{duration} ans : {empruntis_rates[duration]} %**")
            
            # Optionnel : Vous pourriez utiliser ces taux pour pré-remplir un champ
            # ou les afficher dans le corps principal de l'application si pertinent.
        else:
            st.sidebar.error("Les taux Empruntis n'ont pas pu être récupérés.")

# Calcul des résultats
if st.sidebar.button("Calculer le Prêt 🚀"):
    monthly_payment, total_credit_cost, amortization_table = calculate_loan(
        principal_loan, interest_rate, loan_duration_years
    )

    st.subheader("Résultats du Prêt")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Montant de la mensualité", f"{monthly_payment:,.2f} €")
    with col2:
        st.metric("Coût total du crédit", f"{total_credit_cost:,.2f} €")
    with col3:
        st.metric("Capital total remboursé", f"{principal_loan + total_credit_cost:,.2f} €")

    st.markdown("---")

    st.subheader("Graphique d'Amortissement")

    # Création du graphique Plotly
    fig = go.Figure()

    # Capital restant dû
    fig.add_trace(go.Scatter(
        x=amortization_table['Mois'],
        y=amortization_table['Capital restant dû'],
        mode='lines',
        name='Capital restant dû',
        line=dict(color='black', width=2)
    ))

    # Capital remboursé (cumulé)
    fig.add_trace(go.Scatter(
        x=amortization_table['Mois'],
        y=amortization_table['Capital remboursé (cumulé)'],
        mode='lines',
        name='Capital remboursé',
        fill='tozeroy', # Remplir la zone sous la ligne
        fillcolor='rgba(173, 216, 230, 0.6)', # Bleu clair transparent
        line=dict(color='skyblue', width=0) # Ligne invisible pour le remplissage
    ))

    # Intérêts payés (cumulés)
    fig.add_trace(go.Scatter(
        x=amortization_table['Mois'],
        y=amortization_table['Intérêts payés (cumulés)'] + amortization_table['Capital remboursé (cumulé)'], # Empiler les intérêts au-dessus du capital remboursé
        mode='lines',
        name='Intérêts',
        fill='tonexty', # Remplir la zone jusqu'à la trace précédente
        fillcolor='rgba(255, 165, 0, 0.6)', # Orange transparent
        line=dict(color='orange', width=0) # Ligne invisible pour le remplissage
    ))

    fig.update_layout(
        title="Évolution du Capital Restant Dû, Capital Remboursé et Intérêts",
        xaxis_title="Durée en mois",
        yaxis_title="Montant en euros",
        hovermode="x unified",
        legend_title="Légende",
        height=500,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # ##### Composition Mensuelle de la Mensualité (Intérêts vs Capital) ---
    st.markdown("##### Composition Mensuelle de la Mensualité (Intérêts vs Capital)")
    fig_monthly = go.Figure()

    # Part d'intérêts mensuels
    fig_monthly.add_trace(go.Scatter(
        x=amortization_table['Mois'],
        y=amortization_table['Intérêts du mois'],
        mode='none', # Pas de ligne visible pour les aires
        stackgroup='one', # Empile les traces dans ce groupe
        name='Intérêts du mois',
        fill='tozeroy',
        fillcolor='rgba(255, 99, 71, 0.7)' # Un rouge orangé pour les intérêts
    ))

    # Part de capital remboursé mensuel
    fig_monthly.add_trace(go.Scatter(
        x=amortization_table['Mois'],
        y=amortization_table['Capital remboursé du mois'],
        mode='none', # Pas de ligne visible pour les aires
        stackgroup='one', # Empile les traces dans ce groupe
        name='Capital remboursé du mois',
        fill='tonexty', # Empile au-dessus de la trace précédente
        fillcolor='rgba(60, 179, 113, 0.7)' # Un vert pour le capital
    ))

    fig_monthly.update_layout(
        xaxis_title="Durée en mois",
        yaxis_title="Montant de la mensualité (€)",
        hovermode="x unified",
        legend_title="Légende",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.subheader("Tableau d'Amortissement")
    st.dataframe(amortization_table.style.format({
        'Capital restant dû': "{:,.2f} €",
        'Capital remboursé (cumulé)': "{:,.2f} €",
        'Intérêts payés (cumulés)': "{:,.2f} €"
    }))

else:
    st.info("Veuillez entrer les paramètres de votre prêt et cliquer sur 'Calculer le Prêt' pour voir les résultats.")

st.markdown("---")
st.markdown("Développé en binôme avec Gemini ;)")

def get_empruntis_rates():
    """
    Récupère les taux moyens immobiliers pour 15, 20 et 25 ans depuis le site Empruntis.
    Retourne un dictionnaire {durée: taux_moyen}.
    """
    url = "https://www.empruntis.com/financement/actualites/barometre-national.php"
    
    # Dictionnaire pour stocker les taux par durée
    rates = {} 
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP erreurs (4xx ou 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')
        all_text = soup.get_text() # Récupère tout le texte de la page

        # Regex pour trouver une durée (15, 20, 25 ans) suivie de deux pourcentages.
        # Le deuxième pourcentage est généralement le "Taux Moyen" sur ces baromètres.
        # Exemple de motif recherché dans le texte : "15 ans. 2,25 % (stable) 2,65 % (stable)"
        # On capture la durée, puis le premier pourcentage (mini), et enfin le second (moyen).
        pattern = re.compile(r'(\d{2})\s*ans\D*([\d,\.]+\s*%)(\s*\(\w+\))?\s*([\d,\.]+\s*%)')
        
        # Parcourir toutes les correspondances trouvées dans le texte
        for match in pattern.finditer(all_text):
            duration = int(match.group(1)) # Capture la durée (ex: 15, 20, 25)
            raw_average_rate = match.group(4) # Capture le deuxième pourcentage, qui est le taux moyen
            
            # Si la durée est parmi celles que nous cherchons
            if duration in [15, 20, 25]:
                # Nettoyer le texte du taux (remplacer ',' par '.', supprimer '%', espaces)
                cleaned_rate = raw_average_rate.replace(',', '.').replace('%', '').strip()
                rates[duration] = float(cleaned_rate) # Convertir en float et stocker dans le dictionnaire
                
        # Vérifier si des taux ont été trouvés
        if rates:
            return rates
        else:
            st.warning("Impossible de trouver les taux moyens pour 15, 20 et 25 ans sur Empruntis. La structure du site a peut-être changé ou le motif de recherche est incorrect.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération de la page web Empruntis : {e}")
        return None
    except Exception as e:
        st.error(f"Une erreur inattendue s'est produite lors du scraping Empruntis : {e}")
        return None


def get_meilleurtaux_rate():
    """
    Récupère le taux moyen immobilier sur 15 ans depuis le site Meilleurtaux.
    """
    url = "https://www.meilleurtaux.com/" # L'URL de la page à scraper
    try:
        # Envoyer une requête GET à l'URL
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP erreurs (4xx ou 5xx)

        # Parser le contenu HTML de la page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Trouver l'élément qui contient le taux.
        # Basé sur l'extrait de code fourni, le taux est dans un <b>
        # à l'intérieur d'un div avec la classe 'foot', qui est lui-même
        # à l'intérieur d'un <a> avec la classe 'cards fc'.
        # Nous allons chercher le div 'foot' qui contient le texte "Taux moyen ... sur 15 ans".
        
        # Trouver le lien du crédit immobilier
        credit_immobilier_card = soup.find('a', class_='cards fc', href='/demande-simulation/credit-immobilier/')

        if credit_immobilier_card:
            # À l'intérieur de cette carte, trouver le div avec la classe 'foot'
            foot_div = credit_immobilier_card.find('div', class_='foot')
            if foot_div:
                # À l'intérieur du div 'foot', trouver la balise <b> qui contient le taux
                rate_tag = foot_div.find('b')
                if rate_tag:
                    rate_text = rate_tag.get_text(strip=True)
                    # Nettoyer le texte pour ne garder que le pourcentage numérique
                    # Par exemple, "2,90 %" deviendra "2.90"
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

# --- Application Streamlit ---
st.title("Taux Moyen Immobilier Meilleurtaux")

st.write("Ceci est une application Streamlit qui récupère le taux moyen affiché sur la page d'accueil de Meilleurtaux.com.")

if st.button("Actualiser le taux"):
    with st.spinner("Récupération du taux en cours..."):
        taux = get_meilleurtaux_rate()
        if taux:
            st.success(f"Le taux moyen immobilier sur 15 ans est : **{taux} %**")
        else:
            st.warning("Le taux n'a pas pu être récupéré. Veuillez réessayer plus tard ou vérifier la structure du site.")

st.markdown("---")
st.markdown("Note : Le scraping web peut être affecté par les changements de structure du site web cible. Si le taux ne s'affiche plus, le code de scraping pourrait nécessiter une mise à jour :)")
