import customtkinter as ctk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import requests
import configparser
import os


class PaginaStampaPazienti(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        style = ttk.Style()
        style.theme_use("clam")  # stile base con personalizzazioni supportate

        # Colori personalizzati
        verde_chiaro = "#b5f7c9"   # selezione
        verde_hover = "#84e4a2"    # hover
        bianco = "#ffffff"
        nero = "#000000"
        bordo = "#cccccc"

        # Layout senza bordi esterni
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        # Impostazioni generali tabella
        style.configure("Treeview",
                        background=bianco,
                        foreground=nero,
                        fieldbackground=bianco,
                        rowheight=24,
                        bordercolor=bordo,
                        borderwidth=1,
                        relief="flat")

        # Colore selezione e hover
        style.map("Treeview",
                  background=[
                      ("selected", verde_chiaro),
                      ("active", verde_hover)
                  ],
                  foreground=[
                      ("selected", nero),
                      ("active", nero)
                  ])

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.config_server()
        self.pazienti = self.carica_dati_dal_server()

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        # Tab Pazienti
        self.tabview.add("Pazienti")
        self.tree_pazienti = ttk.Treeview(
            self.tabview.tab("Pazienti"),
            columns=("nome", "cognome", "cf", "num_piani"),
            show="headings"
        )
        self.tree_pazienti.heading("nome", text="Nome")
        self.tree_pazienti.heading("cognome", text="Cognome")
        self.tree_pazienti.heading("cf", text="Codice Fiscale")
        self.tree_pazienti.heading("num_piani", text="Num. Piani")
        self.tree_pazienti.column("nome", width=150)
        self.tree_pazienti.column("cognome", width=150)
        self.tree_pazienti.column("cf", width=150)
        self.tree_pazienti.column("num_piani", width=100)
        self.tree_pazienti.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_pazienti.bind("<<TreeviewSelect>>", self.mostra_piani)

        # Tab Piani Terapeutici
        self.tabview.add("Piani Terapeutici")
        self.tree_piani = ttk.Treeview(
            self.tabview.tab("Piani Terapeutici"),
            columns=("farmaco", "dosaggio", "inizio", "fine", "motivazione"),
            show="headings"
        )
        self.tree_piani.heading("farmaco", text="Nome Farmaco")
        self.tree_piani.heading("dosaggio", text="Dosaggio (mg)")
        self.tree_piani.heading("inizio", text="Data Inizio")
        self.tree_piani.heading("fine", text="Data Fine")
        self.tree_piani.heading("motivazione", text="Motivazione Interruzione")
        self.tree_piani.column("farmaco", width=200)
        self.tree_piani.column("dosaggio", width=100)
        self.tree_piani.column("inizio", width=80)
        self.tree_piani.column("fine", width=80)
        self.tree_piani.column("motivazione", width=250)
        self.tree_piani.pack(fill="both", expand=True, padx=10, pady=10)

        self.popola_tabella_pazienti()

    def config_server(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.host = config.get("server", "host", fallback="localhost")
        self.port = config.get("server", "port", fallback="5000")
        self.base_url = f"http://{self.host}:{self.port}"

    def get_auth_headers(self):
        """Restituisce gli header di autenticazione per le richieste al server"""
        password = os.environ.get('SERVER_PASSWORD')
        if password:
            return {"Authorization": f"Bearer {password}"}
        return {}

    def carica_dati_dal_server(self):
        try:
            url = f"{self.base_url}/pazienti"
            headers = self.get_auth_headers()
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Errore richiesta server: {e}")
            return []
        except Exception as e:
            print(f"Errore connessione server: {e}")
            return []

    def popola_tabella_pazienti(self):
        self.tree_pazienti.delete(*self.tree_pazienti.get_children())
        for idx, paz in enumerate(self.pazienti):
            num_piani = len(paz.get("piani", []))
            tag = "deceduto" if paz.get("deceduto", False) else "normale"
            self.tree_pazienti.insert(
                "", "end", iid=str(idx),
                values=(paz["nome"], paz["cognome"], paz["cf"], num_piani),
                tags=(tag,)
            )
        self.tree_pazienti.tag_configure("deceduto", background="red", foreground="white")

    def mostra_piani(self, event):
        selezione = self.tree_pazienti.selection()
        if not selezione:
            return
        idx = int(selezione[0])

        self.tree_piani.delete(*self.tree_piani.get_children())
        oggi = datetime.today().date()
        piani = self.pazienti[idx].get("piani", [])

        if not piani:
            self.tree_piani.insert("", "end", values=("Nessun piano disponibile", "", "", "", ""))
        else:
            for p in piani:
                data_fine_str = p.get("data_fine", "")
                motivazione = p.get("motivazione_interruzione", "").strip()
                scaduto = False

                try:
                    data_fine = datetime.strptime(data_fine_str, "%Y-%m-%d").date()
                    if data_fine <= oggi:
                        scaduto = True
                        if not motivazione:
                            motivazione = "Piano scaduto"
                except Exception:
                    pass

                tag = "interrotto" if motivazione else "attivo"

                self.tree_piani.insert(
                    "", "end",
                    values=(
                        p.get("nome_farmaco", ""),
                        p.get("dosaggio", ""),
                        p.get("data_inizio", ""),
                        data_fine_str,
                        motivazione
                    ),
                    tags=(tag,)
                )
                
        self.tree_pazienti.tag_configure("deceduto", background="red", foreground="white")
                
        self.tree_piani.tag_configure("interrotto", background="#FF9999")
        self.tree_piani.tag_configure("attivo", background="white")
        self.tabview.set("Piani Terapeutici")
