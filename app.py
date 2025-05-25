import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pages import taux


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

st.sidebar.markdown("---")
st.sidebar.title("Actualité des taux")
st.sidebar.page_link("pages/taux.py", label=" 📈%📉")

st.markdown("---")
st.sidebar.title("Retrouvez les dernières ventes près de chez vous")
st.sidebar.page_link("pages/etalab.py", label=" 🏘️ 📉")