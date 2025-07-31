from flask import Flask, jsonify, request
import threading
import json
import os

FILE_DB = os.path.join("dati", "pazienti.json")

app = Flask(__name__)

# Carica dati da file
def carica_pazienti():
    if os.path.exists(FILE_DB):
        with open(FILE_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Salva dati su file
def salva_pazienti(pazienti):
    with open(FILE_DB, "w", encoding="utf-8") as f:
        json.dump(pazienti, f, indent=2, ensure_ascii=False)

pazienti = carica_pazienti()

@app.route("/pazienti", methods=["GET"])
def get_pazienti():
    return jsonify(pazienti)

@app.route("/pazienti", methods=["POST"])
def aggiungi_paziente():
    nuovo_paziente = request.json
    pazienti.append(nuovo_paziente)
    salva_pazienti(pazienti)
    return jsonify({"message": "Paziente aggiunto"}), 201

@app.route("/pazienti/<cf>", methods=["PUT"])
def modifica_paziente(cf):
    dati = request.json
    for i, p in enumerate(pazienti):
        if p["cf"] == cf:
            pazienti[i].update(dati)
            salva_pazienti(pazienti)
            return jsonify({"message": "Paziente aggiornato"})
    return jsonify({"error": "Paziente non trovato"}), 404

@app.route("/pazienti/<cf>", methods=["DELETE"])
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
