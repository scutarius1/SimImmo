# tracking/session_tracker.py

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import time
import uuid
import pandas as pd
import os
import json

def track_user(log_file="connections_log.csv"):
    # Génère un ID unique pour la session
    session_id = str(uuid.uuid4())
    start_time = datetime.now()
    start_timestamp = time.time()

    # JS pour récupérer l'IP et renvoyer vers Streamlit
    ip_json = components.html(f"""
    <script>
        const sessionId = "{session_id}";
        const startTime = Date.now();

        fetch("https://api.ipify.org?format=json")
        .then(response => response.json())
        .then(data => {{
            const ip = data.ip;
            const event = new CustomEvent("streamlit:ip_event", {{
                detail: JSON.stringify({{ ip: ip, sessionId: sessionId }})
            }});
            document.dispatchEvent(event);
        }});

        window.addEventListener("beforeunload", function () {{
            const endTime = Date.now();
            const duration = Math.round((endTime - startTime) / 1000);
            navigator.sendBeacon("https://example.com/close?session_id=" + sessionId + "&duration=" + duration);
        }});
    </script>
    """, height=0)

    # Zone d'attente interactive : récupération de l’IP via JS (hack temporaire via événement)
    ip = st.experimental_get_query_params().get("ip", [None])[0]

    # Ou écoute de l’event injecté ci-dessus (pas encore traité par Streamlit directement sans composant React custom)
    # Donc on passe par st.experimental_get_query_params ou simulateur via reload
    # Pour l'instant, demande l’IP manuellement si non transmise
    if not ip:
        st.warning("Impossible d'identifier votre IP automatiquement. Entrez-la manuellement si vous le souhaitez.")
        ip = st.text_input("Adresse IP :", placeholder="123.45.67.89")

    # Affichage et enregistrement
    if ip:
        st.success(f"IP détectée : {ip}")
        # Écriture dans un fichier CSV
        entry = {
            "session_id": session_id,
            "ip": ip,
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if os.path.exists(log_file):
            df = pd.read_csv(log_file)
            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
        else:
            df = pd.DataFrame([entry])

        df.to_csv(log_file, index=False)

    # Retourne le timestamp de début pour calcul de la durée
    return start_timestamp
