import json
import os

PERCORSO_FILE = os.path.join("dati", "pazienti.json")

def carica_pazienti():
    if os.path.exists(PERCORSO_FILE):
        with open(PERCORSO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salva_pazienti(pazienti):
    with open(PERCORSO_FILE, "w", encoding="utf-8") as f:
        json.dump(pazienti, f, indent=4, ensure_ascii=False)
