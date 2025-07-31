from flask import Flask, jsonify, request
import threading
import json
import os
import hashlib
import secrets
from functools import wraps

FILE_DB = os.path.join("dati", "pazienti.json")
AUTH_FILE = os.path.join("dati", "auth.json")

app = Flask(__name__)

# Funzioni per la gestione dell'autenticazione
def hash_password(password):
    """Hash della password con salt"""
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwdhash.hex()

def verify_password(stored_password, provided_password):
    """Verifica la password"""
    salt = stored_password[:32]
    stored_hash = stored_password[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwdhash.hex() == stored_hash

def salva_password(password):
    """Salva la password hashata"""
    os.makedirs("dati", exist_ok=True)
    hashed_pw = hash_password(password)
    auth_data = {"password": hashed_pw}
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(auth_data, f)

def carica_password():
    """Carica la password hashata"""
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            auth_data = json.load(f)
            return auth_data.get("password")
    return None

def password_exists():
    """Controlla se esiste già una password"""
    return os.path.exists(AUTH_FILE)

def require_auth(f):
    """Decoratore per richiedere autenticazione"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token di autenticazione richiesto"}), 401
        
        token = auth_header.split(' ')[1]
        stored_password = carica_password()
        
        if not stored_password or not verify_password(stored_password, token):
            return jsonify({"error": "Autenticazione fallita"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Carica dati da file
def carica_pazienti():
    if os.path.exists(FILE_DB):
        with open(FILE_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Salva dati su file
def salva_pazienti(pazienti):
    os.makedirs("dati", exist_ok=True)
    with open(FILE_DB, "w", encoding="utf-8") as f:
        json.dump(pazienti, f, indent=2, ensure_ascii=False)

pazienti = carica_pazienti()

# Endpoint per l'autenticazione
@app.route("/auth/setup", methods=["POST"])
def setup_password():
    """Imposta la password iniziale (solo se non esiste già)"""
    if password_exists():
        return jsonify({"error": "Password già configurata"}), 400
    
    data = request.json
    password = data.get("password")
    
    if not password or len(password) < 6:
        return jsonify({"error": "Password deve essere di almeno 6 caratteri"}), 400
    
    salva_password(password)
    return jsonify({"message": "Password configurata con successo"}), 201

@app.route("/auth/login", methods=["POST"])
def login():
    """Verifica la password e restituisce un token"""
    data = request.json
    password = data.get("password")
    
    stored_password = carica_password()
    if not stored_password:
        return jsonify({"error": "Password non ancora configurata"}), 400
    
    if verify_password(stored_password, password):
        return jsonify({"message": "Autenticazione riuscita", "token": password}), 200
    else:
        return jsonify({"error": "Password errata"}), 401

@app.route("/auth/status", methods=["GET"])
def auth_status():
    """Controlla se la password è già configurata"""
    return jsonify({"password_configured": password_exists()})

# Endpoints protetti
@app.route("/pazienti", methods=["GET"])
@require_auth
def get_pazienti():
    return jsonify(pazienti)

@app.route("/pazienti", methods=["POST"])
@require_auth
def aggiungi_paziente():
    nuovo_paziente = request.json
    pazienti.append(nuovo_paziente)
    salva_pazienti(pazienti)
    return jsonify({"message": "Paziente aggiunto"}), 201

@app.route("/pazienti/<cf>", methods=["PUT"])
@require_auth
def modifica_paziente(cf):
    dati = request.json
    for i, p in enumerate(pazienti):
        if p["cf"] == cf:
            pazienti[i].update(dati)
            salva_pazienti(pazienti)
            return jsonify({"message": "Paziente aggiornato"})
    return jsonify({"error": "Paziente non trovato"}), 404

@app.route("/pazienti/<cf>", methods=["DELETE"])
@require_auth
def elimina_paziente(cf):
    global pazienti
    pazienti = [p for p in pazienti if p["cf"] != cf]
    salva_pazienti(pazienti)
    return jsonify({"message": "Paziente eliminato"})

def run_server(*args, **kwargs):
    app.run(host="0.0.0.0", port=5000)
    
# Per eseguire solo il server:
if __name__ == "__main__":
    run_server()
