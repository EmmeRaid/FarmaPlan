import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date, timedelta
import requests
import configparser
from widgets.popup_alert import popup_dark


class FormAggiungiPaziente(ctk.CTkFrame):
    def __init__(self, master, callback_codice_fiscale_esistente):
        super().__init__(master)
        self.callback_codice_fiscale_esistente = callback_codice_fiscale_esistente

        self.config_server()
        self.grid_columnconfigure(1, weight=1)
        

        

        ctk.CTkLabel(self, text="Aggiungi Paziente", font=("Arial", 18)).grid(row=0, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(self, text="Codice Fiscale:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_cf = ctk.CTkEntry(self, placeholder_text="Codice Fiscale")
        self.entry_cf.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.entry_cf.bind("<FocusOut>", self.controlla_codice_fiscale)

        ctk.CTkLabel(self, text="Nome:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_nome = ctk.CTkEntry(self, placeholder_text="Nome")
        self.entry_nome.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(self, text="Cognome:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_cognome = ctk.CTkEntry(self, placeholder_text="Cognome")
        self.entry_cognome.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        oggi = date.today()
        self.data_nascita_picker = DateEntry(self, date_pattern="yyyy-MM-dd", state="readonly",
                                             mindate=oggi - timedelta(days=365*120),
                                             maxdate=oggi)
        self.data_nascita_picker.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        self.btn_salva = ctk.CTkButton(self, text="Salva Paziente", command=self.salva_paziente)
        self.btn_salva.grid(row=5, column=0, columnspan=2, pady=15)

    def config_server(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.host = config.get("server", "host", fallback="localhost")
        self.port = config.get("server", "port", fallback="5000")
        self.base_url = f"http://{self.host}:{self.port}"

    def carica_pazienti(self):
        try:
            url = f"{self.base_url}/pazienti"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Errore caricamento pazienti dal server: {e}")
            return []

    def controlla_codice_fiscale(self, event=None):
        cf = self.entry_cf.get().strip().upper()
        if not cf:
            return
        pazienti = self.carica_pazienti()
        for paz in pazienti:
            if paz["cf"].upper() == cf:
                self.callback_codice_fiscale_esistente(cf)
                break

    def salva_paziente(self, event = None):
        pazienti = self.carica_pazienti()  # Dati freschi dal server

        nome = self.entry_nome.get().strip()
        cognome = self.entry_cognome.get().strip()
        cf = self.entry_cf.get().strip().upper()
        data_nascita = self.data_nascita_picker.get_date().strftime("%Y-%m-%d")

        if not nome or not cognome or not cf or not data_nascita:
            popup_dark("Errore", "Compila tutti i campi!")
            return

        for paz in pazienti:
            if paz["cf"].upper() == cf:
                self.callback_codice_fiscale_esistente(cf)
                return

        nuovo_paziente = {
            "nome": nome,
            "cognome": cognome,
            "cf": cf,
            "data_nascita": data_nascita,
            "piani": [],
            "deceduto": False
        }

        try:
            url = f"{self.base_url}/pazienti"
            response = requests.post(url, json=nuovo_paziente, timeout=5)
            response.raise_for_status()
        except Exception as e:
            popup_dark("Errore", message=f"Errore durante salvataggio paziente: {e}")
            return

        popup_dark("Successo", "Paziente aggiunto!")

        self.entry_nome.delete(0, "end")
        self.entry_cognome.delete(0, "end")
        self.entry_cf.delete(0, "end")
