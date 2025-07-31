import json
import os
import configparser

PERCORSO_FILE = os.path.join("dati", "pazienti.json")

def carica_pazienti():
    if os.path.exists(PERCORSO_FILE):
        with open(PERCORSO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salva_pazienti(pazienti):
    os.makedirs("dati", exist_ok=True)
    with open(PERCORSO_FILE, "w", encoding="utf-8") as f:
        json.dump(pazienti, f, indent=4, ensure_ascii=False)

def get_auth_headers():
    """Restituisce gli header di autenticazione per le richieste al server"""
    password = os.environ.get('SERVER_PASSWORD')
    if password:
        return {"Authorization": f"Bearer {password}"}
    return {}

def get_server_config():
    """Legge la configurazione del server dal file config.ini"""
    config = configparser.ConfigParser()
    config.read("config.ini")
    host = config.get("server", "host", fallback="localhost")
    port = config.get("server", "port", fallback="5000")
    return f"http://{host}:{port}"
