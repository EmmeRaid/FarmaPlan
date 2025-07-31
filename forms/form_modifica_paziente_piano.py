import customtkinter as ctk
from tkinter import StringVar, Menu
from datetime import datetime
import requests
import configparser
from dati.gestore_dati import salva_pazienti
from tkinter import messagebox
from widgets.popup_alert import popup_dark

class FormModificaPazientePiano(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.config_server()
        self.pazienti = self.carica_dati_dal_server()

        self.selected_paziente_index = None
        self.selected_piano_index = None
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Modifica Paziente e Piano", font=("Arial", 18)).grid(row=0, column=0, columnspan=3, pady=10)

        # Seleziona Paziente con CTkComboBox e autocompletamento personalizzato
        ctk.CTkLabel(self, text="Seleziona Paziente:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.combo_pazienti = ctk.CTkComboBox(
            self,
            values=[f"{p['nome']} {p['cognome']}" for p in self.pazienti],
            command=self.carica_paziente
        )
        self.combo_pazienti.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.combo_pazienti._entry.bind("<KeyRelease>", self._combo_autocomplete)
        self.combo_pazienti._entry.bind("<FocusOut>", lambda e: self._close_menu(self.combo_pazienti))

        # Dati anagrafici
        self.entry_nome = self._crea_entry("Nome:", 2)
        self.entry_cognome = self._crea_entry("Cognome:", 3)
        self.entry_cf = self._crea_entry("Codice Fiscale:", 4)
        self.entry_data_nascita = self._crea_entry("Data Nascita (YYYY-MM-DD):", 5)

        # Piano
        ctk.CTkLabel(self, text="Seleziona Piano:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.combo_piani = ctk.CTkComboBox(self, values=[], command=self.carica_piano)
        self.combo_piani.grid(row=6, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        self.entry_nome_farmaco = self._crea_entry("Nome Farmaco:", 7)
        self.entry_dosaggio = self._crea_entry("Dosaggio (mg):", 8)
        self.entry_data_inizio = self._crea_entry("Data Inizio (YYYY-MM-DD):", 9)
        self.entry_data_fine = self._crea_entry("Data Fine (YYYY-MM-DD):", 10)
        self.entry_motivazione = self._crea_entry("Motivazione Interruzione:", 11)

        self.var_deceduto = ctk.BooleanVar(value=False)
        self.checkbox_deceduto = ctk.CTkCheckBox(self, text="Deceduto", variable=self.var_deceduto, command=self.toggle_motivazione_entry)
        self.checkbox_deceduto.grid(row=12, column=1, columnspan=2, pady=5)

        self.btn_salva = ctk.CTkButton(self, text="Salva Modifiche", command=self.salva_modifiche)
        self.btn_salva.grid(row=13, column=0, pady=15, padx=(20, 10), sticky="ew")

        self.btn_clear = ctk.CTkButton(self, text="Clear", fg_color="red", hover_color="#ff4d4d", command=self.clear_all)
        self.btn_clear.grid(row=13, column=1, columnspan=2, pady=15, padx=(10, 20), sticky="ew")

        # Attiva autocompletamento per gli entry
        self._setup_autocompletamento()

    def config_server(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.host = config.get("server", "host", fallback="localhost")
        self.port = config.get("server", "port", fallback="5000")
        self.base_url = f"http://{self.host}:{self.port}"

    def carica_dati_dal_server(self):
        try:
            url = f"{self.base_url}/pazienti"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Errore caricamento pazienti dal server: {e}")
            return []

    def _crea_entry(self, label, row):
        ctk.CTkLabel(self, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=5)
        entry = ctk.CTkEntry(self)
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        return entry

    def toggle_motivazione_entry(self):
        if self.var_deceduto.get():
            self.entry_motivazione.configure(state="normal")
            self.entry_motivazione.delete(0, 'end')
            self.entry_motivazione.insert(0, "Deceduto")
        else:
            self.entry_motivazione.configure(state="normal")
            self.entry_motivazione.delete(0, 'end')

    def carica_paziente(self, valore):
        for idx, paz in enumerate(self.pazienti):
            nome_cogn = f"{paz['nome']} {paz['cognome']}"
            if nome_cogn == valore:
                self.selected_paziente_index = idx
                self._popola_form_paziente(paz)
                self._aggiorna_combo_piani(paz)
                break

    def _popola_form_paziente(self, paziente):
        self.entry_nome.delete(0, 'end')
        self.entry_nome.insert(0, paziente["nome"])
        self.entry_cognome.delete(0, 'end')
        self.entry_cognome.insert(0, paziente["cognome"])
        self.entry_cf.delete(0, 'end')
        self.entry_cf.insert(0, paziente["cf"])
        self.entry_data_nascita.delete(0, 'end')
        self.entry_data_nascita.insert(0, paziente["data_nascita"])

        self.var_deceduto.set(paziente.get("deceduto", False))
        self.toggle_motivazione_entry()

    def _aggiorna_combo_piani(self, paziente):
        piani = paziente.get("piani", [])
        self.combo_piani.configure(values=[p["nome_farmaco"] for p in piani])
        if piani:
            self.combo_piani.set(self.combo_piani.values[0])
            self.carica_piano(self.combo_piani.values[0])
        else:
            self.combo_piani.set("")
            self.pulisci_form_piano()

    def carica_piano(self, valore):
        if self.selected_paziente_index is None:
            return
        paziente = self.pazienti[self.selected_paziente_index]
        piani = paziente.get("piani", [])
        for idx, piano in enumerate(piani):
            if piano["nome_farmaco"] == valore:
                self.selected_piano_index = idx
                self._popola_form_piano(piano)
                break

    def _popola_form_piano(self, piano):
        self.entry_nome_farmaco.delete(0, 'end')
        self.entry_nome_farmaco.insert(0, piano["nome_farmaco"])
        self.entry_dosaggio.delete(0, 'end')
        self.entry_dosaggio.insert(0, piano["dosaggio"])
        self.entry_data_inizio.delete(0, 'end')
        self.entry_data_inizio.insert(0, piano["data_inizio"])
        self.entry_data_fine.delete(0, 'end')
        self.entry_data_fine.insert(0, piano["data_fine"])
        self.entry_motivazione.delete(0, 'end')
        self.entry_motivazione.insert(0, piano.get("motivazione_interruzione", ""))

    def pulisci_form_piano(self):
        for entry in [self.entry_nome_farmaco, self.entry_dosaggio, self.entry_data_inizio, self.entry_data_fine, self.entry_motivazione]:
            entry.delete(0, 'end')

    def clear_all(self):
        self.selected_paziente_index = None
        self.selected_piano_index = None
        self.combo_pazienti.set("")
        self.combo_piani.set("")
        for e in [self.entry_nome, self.entry_cognome, self.entry_cf, self.entry_data_nascita, self.entry_motivazione]:
            e.delete(0, 'end')
        self.pulisci_form_piano()
        self.var_deceduto.set(False)

    def salva_modifiche(self):
        if self.selected_paziente_index is None:
            popup_dark("Errore", "Nessun paziente selezionato!")
            print("Nessun paziente selezionato")
            return

        paziente = self.pazienti[self.selected_paziente_index]
        paziente["nome"] = self.entry_nome.get()
        paziente["cognome"] = self.entry_cognome.get()
        paziente["cf"] = self.entry_cf.get()
        paziente["data_nascita"] = self.entry_data_nascita.get()
        paziente["deceduto"] = self.var_deceduto.get()

        if self.selected_piano_index is not None:
            piano = paziente["piani"][self.selected_piano_index]
            piano["nome_farmaco"] = self.entry_nome_farmaco.get()
            piano["dosaggio"] = self.entry_dosaggio.get()
            piano["data_inizio"] = self.entry_data_inizio.get()
            piano["data_fine"] = self.entry_data_fine.get()
            piano["motivazione_interruzione"] = self.entry_motivazione.get().strip()

        salva_pazienti(self.pazienti)

        try:
            cf = paziente["cf"]
            url = f"{self.base_url}/pazienti/{cf}"
            response = requests.put(url, json=paziente, timeout=5)
            response.raise_for_status()
        except Exception as e:
            print(f"Errore durante aggiornamento server: {e}")

        try:
            self.pazienti = self.carica_dati_dal_server()
            self.combo_pazienti.configure(values=[f"{p['nome']} {p['cognome']}" for p in self.pazienti])
        except Exception as e:
            print(f"Errore nel caricamento dati aggiornati: {e}")

        messagebox.showinfo("Successo", "Paziente Modificato con successo!")
        print("Modifiche salvate e sincronizzate.")

    def _setup_autocompletamento(self):
        # Associa autocompletamento ai singoli entry
        self._associa_autocomplete(self.entry_nome, "nome")
        self._associa_autocomplete(self.entry_cognome, "cognome")
        self._associa_autocomplete(self.entry_cf, "cf")
        # Non attivo autocompletamento su data_nascita e motivazione per evitare problemi
        # Se vuoi attivare, crea logica simile e lista filtrata coerente
        self._associa_autocomplete(self.entry_nome_farmaco, "nome_farmaco")
        self._associa_autocomplete(self.entry_dosaggio, "dosaggio")
        self._associa_autocomplete(self.entry_data_inizio, "data_inizio")
        self._associa_autocomplete(self.entry_data_fine, "data_fine")
        self._associa_autocomplete(self.entry_motivazione, "motivazione_interruzione")

    def _associa_autocomplete(self, entry, campo):
        entry.bind("<KeyRelease>", lambda e: self._mostra_suggerimenti(entry, campo))
        entry.bind("<FocusOut>", lambda e: self._close_menu(entry))

    def _mostra_suggerimenti(self, entry, campo):
        testo = entry.get().lower()
        if not testo:
            self._close_menu(entry)
            return

        suggerimenti = set()

        if campo in ["nome", "cognome", "cf", "data_nascita"]:
            for p in self.pazienti:
                valore = p.get(campo, "")
                if valore.lower().startswith(testo):
                    suggerimenti.add(valore)
        else:
            # campi del piano
            for p in self.pazienti:
                for piano in p.get("piani", []):
                    valore = piano.get(campo, "")
                    if isinstance(valore, str) and valore.lower().startswith(testo):
                        suggerimenti.add(valore)

        if hasattr(entry, "menu") and entry.menu:
            entry.menu.destroy()

        if suggerimenti:
            menu = Menu(self, tearoff=0)
            for val in sorted(suggerimenti):
                menu.add_command(label=val, command=lambda v=val: self._inserisci_valore(entry, v))
            entry.menu = menu
            try:
                x = entry.winfo_rootx()
                y = entry.winfo_rooty() + entry.winfo_height()
                menu.tk_popup(x, y)
            finally:
                menu.grab_release()
        else:
            self._close_menu(entry)

    def _inserisci_valore(self, entry, valore):
        entry.delete(0, "end")
        entry.insert(0, valore)
        if hasattr(entry, "menu") and entry.menu:
            entry.menu.destroy()

    def _close_menu(self, entry_or_combobox):
        # Chiude il menu di autocompletamento
        if hasattr(entry_or_combobox, "menu") and entry_or_combobox.menu:
            entry_or_combobox.menu.destroy()
            entry_or_combobox.menu = None

    def _combo_autocomplete(self, event):
        # Funzione per autocompletare combo_pazienti (CTkComboBox)
        testo = self.combo_pazienti._entry.get().lower()
        if not testo:
            self._close_menu(self.combo_pazienti)
            return
        valori_filtrati = [f"{p['nome']} {p['cognome']}" for p in self.pazienti if f"{p['nome']} {p['cognome']}".lower().startswith(testo)]

        if hasattr(self.combo_pazienti, "menu") and self.combo_pazienti.menu:
            self.combo_pazienti.menu.destroy()

        if valori_filtrati:
            menu = Menu(self, tearoff=0)
            for val in valori_filtrati:
                menu.add_command(label=val, command=lambda v=val: self._seleziona_da_combo(v))
            self.combo_pazienti.menu = menu
            try:
                x = self.combo_pazienti._entry.winfo_rootx()
                y = self.combo_pazienti._entry.winfo_rooty() + self.combo_pazienti._entry.winfo_height()
                menu.tk_popup(x, y)
            finally:
                menu.grab_release()
        else:
            self._close_menu(self.combo_pazienti)

    def _seleziona_da_combo(self, valore):
        self.combo_pazienti.set(valore)
        self.carica_paziente(valore)
        self._close_menu(self.combo_pazienti)
