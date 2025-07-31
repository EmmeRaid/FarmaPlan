import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date, timedelta
import requests
import configparser
import logging
import os
from tkinter import messagebox
from widgets.popup_alert import popup_dark
from dati.gestore_dati import get_auth_headers, get_server_config

# Logger per il form aggiungi piano
logger = logging.getLogger('FarmaPlan.FormAggiungiPiano')


class FormAggiungiPiano(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("Inizializzazione FormAggiungiPiano")

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
                                            mindate=oggi - timedelta(days=365 * 10),
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
        """Configura la connessione al server"""
        self.base_url = get_server_config()
        logger.info(f"Configurazione server: {self.base_url}")

    def get_auth_headers(self):
        """Restituisce gli header di autenticazione per le richieste al server"""
        return get_auth_headers()

    def carica_pazienti(self):
        """Carica i pazienti dal server con autenticazione"""
        logger.info("Caricamento pazienti dal server")
        try:
            url = f"{self.base_url}/pazienti"
            headers = self.get_auth_headers()
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Caricati {len(data)} pazienti dal server")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore richiesta server: {e}")
            popup_dark("Errore", f"Errore di connessione al server: {e}")
            return []
        except Exception as e:
            logger.error(f"Errore caricamento pazienti dal server: {e}")
            popup_dark("Errore", f"Errore nel caricamento dati: {e}")
            return []

    def salva_piano(self):
        """Salva il nuovo piano terapeutico"""
        logger.info("Inizio processo salvataggio piano terapeutico")
        
        pazienti = self.carica_pazienti()  # Dati freschi dal server
        if not pazienti:
            logger.warning("Impossibile procedere - lista pazienti vuota")
            return

        cf_paziente = self.entry_cf_paziente.get().strip().upper()
        farmaco = self.entry_nome_farmaco.get().strip()
        dosaggio = self.entry_dosaggio.get().strip()
        data_inizio = self.data_inizio_picker.get_date()
        data_fine = self.data_fine_picker.get_date()

        logger.info(f"Dati piano - CF: {cf_paziente}, Farmaco: {farmaco}, Dosaggio: {dosaggio}")

        # Validazione campi
        if not cf_paziente or not farmaco or not dosaggio or not data_inizio or not data_fine:
            logger.warning("Tentativo salvataggio piano con campi vuoti")
            popup_dark("Errore", "Compila tutti i campi!")
            return

        if data_fine < data_inizio:
            logger.warning(f"Date non valide - Inizio: {data_inizio}, Fine: {data_fine}")
            popup_dark("Errore", "La data di fine non può essere precedente alla data di inizio!")
            return

        # Trova paziente
        paziente = None
        for p in pazienti:
            if p["cf"].upper() == cf_paziente:
                paziente = p
                logger.info(f"Paziente trovato: {p['nome']} {p['cognome']}")
                break

        if not paziente:
            logger.warning(f"Paziente con CF {cf_paziente} non trovato")
            popup_dark("Errore", "Codice Fiscale paziente non trovato!")
            return

        # Crea nuovo piano
        nuovo_piano = {
            "nome_farmaco": farmaco,
            "dosaggio": dosaggio,
            "data_inizio": data_inizio.strftime("%Y-%m-%d"),
            "data_fine": data_fine.strftime("%Y-%m-%d"),
            "motivazione_interruzione": ""
        }

        logger.info(f"Nuovo piano creato: {nuovo_piano}")

        # Aggiungi piano al paziente
        paziente.setdefault("piani", []).append(nuovo_piano)
        logger.info(f"Piano aggiunto al paziente. Totale piani: {len(paziente['piani'])}")

        # Invio aggiornamento al server con PUT sul paziente
        try:
            url = f"{self.base_url}/pazienti/{paziente['cf']}"
            headers = self.get_auth_headers()
            logger.info(f"Invio aggiornamento al server: {url}")
            response = requests.put(url, json=paziente, headers=headers, timeout=5)
            response.raise_for_status()
            logger.info("Piano salvato con successo sul server")
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore richiesta server durante aggiornamento: {e}")
            popup_dark("Errore", f"Errore di connessione al server: {e}")
            return
        except Exception as e:
            logger.error(f"Errore durante aggiornamento server: {e}")
            popup_dark("Errore", f"Errore durante aggiornamento server: {e}")
            return

        popup_dark("Successo", "Piano aggiunto!")
        logger.info("Piano terapeutico aggiunto con successo")

        # Pulizia form
        self.entry_cf_paziente.delete(0, "end")
        self.entry_nome_farmaco.delete(0, "end")
        self.entry_dosaggio.delete(0, "end")
        logger.debug("Form pulito dopo salvataggio")

    def set_cf_paziente(self, cf):
        """Imposta il codice fiscale del paziente nel form"""
        logger.info(f"Impostazione CF paziente: {cf}")
        self.entry_cf_paziente.delete(0, "end")
        self.entry_cf_paziente.insert(0, cf)

    def clear_form(self):
        """Pulisce tutti i campi del form"""
        logger.info("Pulizia completa del form")
        self.entry_cf_paziente.delete(0, "end")
        self.entry_nome_farmaco.delete(0, "end")
        self.entry_dosaggio.delete(0, "end")
        oggi = date.today()
        self.data_inizio_picker.set_date(oggi)
        self.data_fine_picker.set_date(oggi)
