import streamlit as st
import pandas as pd
import json
import os
import io
import bcrypt
import stripe
from flask import Flask, request, jsonify
import threading
import streamlit_authenticator as stauth
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

# Chiave segreta Stripe e Webhook Secret
stripe.api_key = os.getenv("STRIPE_API_KEY")
endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")

# File credenziali
CREDENTIALS_FILE = "user_credentials.json"
PROFILE_DIR = "profiles"
os.makedirs(PROFILE_DIR, exist_ok=True)

# Flask per i Webhooks
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return jsonify(success=False), 400
    except stripe.error.SignatureVerificationError:
        return jsonify(success=False), 400

    # Evento: pagamento completato
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session["customer_details"]["email"]

        # Aggiorna lo stato premium
        with open(CREDENTIALS_FILE, 'r+') as file:
            credentials = json.load(file)
            for username, user_data in credentials["usernames"].items():
                if user_data["email"] == customer_email:
                    user_data["premium"] = True
                    file.seek(0)
                    json.dump(credentials, file, indent=4)
                    print(f"Utente {username} aggiornato a Premium.")
    return jsonify(success=True), 200

# Funzione per registrare un nuovo utente
def register_user():
    st.title("Registrazione Nuovo Utente")
    with st.form("register_form", clear_on_submit=True):
        new_username = st.text_input("Username")
        new_name = st.text_input("Nome Completo")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Conferma Password", type="password")
        submitted = st.form_submit_button("Registrati")

        if submitted:
            if new_password != confirm_password:
                st.error("Le password non coincidono.")
                return
            credentials = load_credentials()
            if new_username in credentials["usernames"]:
                st.error("L'username esiste già.")
            else:
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                credentials["usernames"][new_username] = {
                    "name": new_name,
                    "email": new_email,
                    "password": hashed_password,
                    "premium": False
                }
                save_credentials(credentials)
                st.success("Registrazione completata con successo!")

# Funzionalità principali (solo per utenti Premium)
def main_page():
    st.title("Convertitore Tracciati Record")
    if st.session_state.get("premium"):
        st.success("Sei un utente Premium! Accedi a tutte le funzionalità.")
        st.subheader("Caricamento e Mappatura File")
        input_file = st.file_uploader("Carica il file di input (Excel o CSV):", type=["csv", "xlsx"])
        if input_file:
            input_df = pd.read_csv(input_file) if input_file.name.endswith('.csv') else pd.read_excel(input_file)
            st.write("Anteprima del file di input:")
            st.dataframe(input_df.head())
    else:
        st.warning("Questa funzionalità è riservata agli utenti Premium.")
        st.markdown("[Clicca qui per diventare Premium 🚀](https://buy.stripe.com/4gw9Cwd1I7eeaOs6oo)")

# Carica e salva credenziali
def load_credentials():
    with open(CREDENTIALS_FILE, 'r') as file:
        return json.load(file)

def save_credentials(credentials):
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file, indent=4)

# Main
def main():
    credentials = load_credentials()
    authenticator = stauth.Authenticate(credentials, "cookie_name", "abcdef", cookie_expiry_days=30)

    if st.session_state.get("authentication_status"):
        st.sidebar.title(f"Benvenuto, {st.session_state['name']}")
        username = st.session_state["username"]
        st.session_state["premium"] = credentials["usernames"][username].get("premium", False)
        authenticator.logout("Logout", location="sidebar")
        main_page()
    elif st.session_state.get("authentication_status") is False:
        st.sidebar.error("Username o password errati!")
        authenticator.login(location="sidebar")
    else:
        st.sidebar.title("Menu")
        page = st.sidebar.radio("Seleziona una pagina", ["Login", "Registrazione"])
        if page == "Login":
            authenticator.login(location="sidebar")
        elif page == "Registrazione":
            register_user()

# Avvio del server Flask per i webhook
def start_flask():
    app.run(port=5000)

# Avvio dell'applicazione
if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    main()
