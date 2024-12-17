import os
import streamlit as st
import pandas as pd
import json
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

# Funzione principale Streamlit
def main():
    st.title("Benvenuto")
    st.write("Questa è la tua applicazione principale.")
    # Funzionalità di login e tool qui

# Avvio Flask solo se non è in Streamlit Cloud
if __name__ == "__main__":
    if "STREAMLIT_SERVER" not in os.environ:  # Controlla se è locale
        threading.Thread(target=lambda: app.run(port=5000)).start()
    main()
