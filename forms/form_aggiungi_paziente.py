import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date, timedelta
import requests
import configparser
import logging
import os
from widgets.popup_alert import popup_dark
from dati.gestore_dati import get_auth_headers, get_server_config

# Logger per il form aggiungi paziente
logger = logging.getLogger('FarmaPlan.FormAggiungiPaziente')

class FormAggiungiPaziente(ctk.CTkFrame):
    def __init__(self, master, callback_codice_fiscale_esistente):
        super().__init__(master)
        logger.info("Inizializzazione FormAggiungiPaziente")
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

        ctk.CTkLabel(self, text="Data Nascita:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        oggi = date.today()
        self.data_nascita_picker = DateEntry(self, date_pattern="yyyy-MM-dd", state="readonly",
                                             mindate=oggi - timedelta(days=365*120),
                                             maxdate=oggi)
        self.data_nascita_picker.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        self.btn_salva = ctk.CTkButton(self, text="Salva Paziente", command=self.salva_paziente)
        self.btn_salva.grid(row=5, column=0, columnspan=2, pady=15)

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

    def controlla_codice_fiscale(self, event=None):
        """Controlla se il codice fiscale esiste già"""
        cf = self.entry_cf.get().strip().upper()
        if not cf:
            return
        
        logger.debug(f"Controllo esistenza codice fiscale: {cf}")
        pazienti = self.carica_pazienti()
        
        if not pazienti:
            logger.warning("Impossibile verificare CF - lista pazienti vuota")
            return
            
        for paz in pazienti:
            if paz["cf"].upper() == cf:
                logger.info(f"Codice fiscale {cf} già esistente, switch al form piano")
                self.callback_codice_fiscale_esistente(cf)
                break
        else:
            logger.debug(f"Codice fiscale {cf} non trovato, si può procedere")

    def salva_paziente(self, event=None):
        """Salva il nuovo paziente"""
        logger.info("Inizio processo salvataggio nuovo paziente")
        
        pazienti = self.carica_pazienti()  # Dati freschi dal server

        nome = self.entry_nome.get().strip()
        cognome = self.entry_cognome.get().strip()
        cf = self.entry_cf.get().strip().upper()
        data_nascita = self.data_nascita_picker.get_date().strftime("%Y-%m-%d")

        logger.info(f"Dati paziente - Nome: {nome}, Cognome: {cognome}, CF: {cf}, Data nascita: {data_nascita}")

        # Validazione campi
        if not nome or not cognome or not cf or not data_nascita:
            logger.warning("Tentativo salvataggio paziente con campi vuoti")
            popup_dark("Errore", "Compila tutti i campi!")
            return

        # Controllo duplicato CF
        for paz in pazienti:
            if paz["cf"].upper() == cf:
                logger.warning(f"Tentativo aggiunta paziente con CF duplicato: {cf}")
                self.callback_codice_fiscale_esistente(cf)
                return

        # Crea nuovo paziente
        nuovo_paziente = {
            "nome": nome,
            "cognome": cognome,
            "cf": cf,
            "data_nascita": data_nascita,
            "piani": [],
            "deceduto": False
        }

        logger.info(f"Nuovo paziente creato: {nuovo_paziente}")

        # Salva sul server
        try:
            url = f"{self.base_url}/pazienti"
            headers = self.get_auth_headers()
            logger.info(f"Invio nuovo paziente al server: {url}")
            response = requests.post(url, json=nuovo_paziente, headers=headers, timeout=5)
            response.raise_for_status()
            logger.info("Paziente salvato con successo sul server")
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore richiesta server durante salvataggio: {e}")
            popup_dark("Errore", f"Errore di connessione al server: {e}")
            return
        except Exception as e:
            logger.error(f"Errore durante salvataggio paziente: {e}")
            popup_dark("Errore", f"Errore durante salvataggio paziente: {e}")
            return

        popup_dark("Successo", "Paziente aggiunto!")
        logger.info(f"Paziente {nome} {cognome} aggiunto con successo")

        # Pulizia form
        self.clear_form()
        logger.debug("Form pulito dopo salvataggio")

    def clear_form(self):
        """Pulisce tutti i campi del form"""
        logger.debug("Pulizia form paziente")
        self.entry_nome.delete(0, "end")
        self.entry_cognome.delete(0, "end")
        self.entry_cf.delete(0, "end")
        oggi = date.today()
        self.data_nascita_picker.set_date(oggi)

    def set_focus_cf(self):
        """Imposta il focus sul campo codice fiscale"""
        logger.debug("Focus impostato su campo CF")
        self.entry_cf.focus()

    def get_cf_value(self):
        """Restituisce il valore del codice fiscale"""
        cf = self.entry_cf.get().strip().upper()
        logger.debug(f"Valore CF richiesto: {cf}")
        return cf

    def validate_inputs(self):
        """Valida tutti gli input del form"""
        nome = self.entry_nome.get().strip()
        cognome = self.entry_cognome.get().strip()
        cf = self.entry_cf.get().strip().upper()
        
        errors = []
        
        if not nome:
            errors.append("Nome è obbligatorio")
        if not cognome:
            errors.append("Cognome è obbligatorio")
        if not cf:
            errors.append("Codice Fiscale è obbligatorio")
        elif len(cf) != 16:
            errors.append("Codice Fiscale deve essere di 16 caratteri")
            
        if errors:
            logger.warning(f"Errori di validazione: {', '.join(errors)}")
            popup_dark("Errori di validazione", "\n".join(errors))
            return False
            
        logger.debug("Validazione input completata con successo")
        return True
