import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date, timedelta
import requests
import configparser
from tkinter import messagebox
from widgets.popup_alert import popup_dark


class FormAggiungiPiano(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.config_server()

        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Aggiungi Piano", font=("Arial", 18)).grid(row=0, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(self, text="Codice Fiscale Paziente:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_cf_paziente = ctk.CTkEntry(self, placeholder_text="Codice Fiscale")
        self.entry_cf_paziente.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(self, text="Nome Farmaco:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_nome_farmaco = ctk.CTkEntry(self, placeholder_text="Nome farmaco")
        self.entry_nome_farmaco.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(self, text="Dosaggio (mg):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_dosaggio = ctk.CTkEntry(self, placeholder_text="Dosaggio numerico")
        self.entry_dosaggio.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(self, text="Data Inizio:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        oggi = date.today()
        Max_date = oggi.replace(year=oggi.year + 10)
        self.data_inizio_picker = DateEntry(self, date_pattern="yyyy-MM-dd", state="readonly",
                                            mindate=oggi - timedelta(days=365*10),
                                            maxdate=Max_date)
        self.data_inizio_picker.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(self, text="Data Fine:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.data_fine_picker = DateEntry(self, date_pattern="yyyy-MM-dd", state="readonly",
                                          mindate=oggi,
                                          maxdate=Max_date)
        self.data_fine_picker.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        self.btn_salva = ctk.CTkButton(self, text="Salva Piano", command=self.salva_piano)
        self.btn_salva.grid(row=6, column=0, columnspan=2, pady=15)

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

    def salva_piano(self):
        pazienti = self.carica_pazienti()  # Dati freschi dal server

        cf_paziente = self.entry_cf_paziente.get().strip().upper()
        farmaco = self.entry_nome_farmaco.get().strip()
        dosaggio = self.entry_dosaggio.get().strip()
        data_inizio = self.data_inizio_picker.get_date()
        data_fine = self.data_fine_picker.get_date()

        if not cf_paziente or not farmaco or not dosaggio or not data_inizio or not data_fine:
            popup_dark("Errore", "Compila tutti i campi!")
            return

        if data_fine < data_inizio:
            popup_dark("Errore", "La data di fine non può essere precedente alla data di inizio!")
            return

        paziente = None
        for p in pazienti:
            if p["cf"].upper() == cf_paziente:
                paziente = p
                break

        if not paziente:
            popup_dark("Errore", "Codice Fiscale paziente non trovato!")
            return

        nuovo_piano = {
            "nome_farmaco": farmaco,
            "dosaggio": dosaggio,
            "data_inizio": data_inizio.strftime("%Y-%m-%d"),
            "data_fine": data_fine.strftime("%Y-%m-%d"),
            "motivazione_interruzione": ""
        }

        paziente.setdefault("piani", []).append(nuovo_piano)

        # Invio aggiornamento al server con PUT sul paziente
        try:
            url = f"{self.base_url}/pazienti/{paziente['cf']}"
            response = requests.put(url, json=paziente, timeout=5)
            response.raise_for_status()
        except Exception as e:
            popup_dark("Errore", message=f"Errore durante aggiornamento server: {e}")
            return

        popup_dark("Successo", "Piano aggiunto!")

        # Pulizia form
        self.entry_cf_paziente.delete(0, "end")
        self.entry_nome_farmaco.delete(0, "end")
        self.entry_dosaggio.delete(0, "end")
