# main.py
from dati.gestore_dati import carica_pazienti, salva_pazienti
import app

# Carica all'avvio
pazienti = carica_pazienti()

if __name__ == "__main__":
    app.main()
