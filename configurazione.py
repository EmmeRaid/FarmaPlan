import os
import configparser
import customtkinter as ctk
import socket
import pyperclip
import requests
import threading
import time

CONFIG_FILE = "config.ini"  # Percorso del file di configurazione

class ConfigurazioneIniziale(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("350x300")
        self.title("Configurazione iniziale")
        self.password = None
        self.ip_address = ""

        self.label_info = ctk.CTkLabel(self, text="Seleziona il ruolo del PC:", font=("Arial", 16))
        self.label_info.pack(pady=20)

        self.btn_server = ctk.CTkButton(self, text="Server Primario", command=self.scegli_server)
        self.btn_server.pack(pady=10, fill="x", padx=50)

        self.btn_client = ctk.CTkButton(self, text="Client Secondario", command=self.scegli_client)
        self.btn_client.pack(pady=10, fill="x", padx=50)

        # Elementi per la configurazione password (nascosti inizialmente)
        self.label_password = ctk.CTkLabel(self, text="Crea password server:", font=("Arial", 12))
        self.entry_password = ctk.CTkEntry(self, placeholder_text="Password (min 6 caratteri)", show="*")
        self.btn_conferma_password = ctk.CTkButton(self, text="Conferma Password", command=self.conferma_password_server)
        
        # Elementi per IP e copia (nascosti inizialmente)
        self.label_ip = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.btn_copia_ip = ctk.CTkButton(self, text="Copia IP e Avvia", command=self.copia_ip)

        # Elementi per inserimento password client (nascosti inizialmente)
        self.label_password_client = ctk.CTkLabel(self, text="Inserisci password server:", font=("Arial", 12))
        self.entry_password_client = ctk.CTkEntry(self, placeholder_text="Password server", show="*")
        self.btn_verifica_password = ctk.CTkButton(self, text="Verifica e Connetti", command=self.verifica_password_client)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def scegli_server(self):
        hostname = socket.gethostname()
        try:
            self.ip_address = socket.gethostbyname(hostname)
        except Exception:
            self.ip_address = "0.0.0.0"

        # Nascondi i pulsanti iniziali
        self.btn_server.pack_forget()
        self.btn_client.pack_forget()
        
        # Mostra form per password
        self.label_password.pack(pady=5)
        self.entry_password.pack(pady=5, fill="x", padx=50)
        self.btn_conferma_password.pack(pady=10)

    def conferma_password_server(self):
        password = self.entry_password.get()
        if len(password) < 6:
            self.mostra_errore("Password deve essere di almeno 6 caratteri!")
            return
        
        self.password = password
        
        # Salva configurazione e avvia server
        self.salva_config(True, self.ip_address)
        
        # Avvia server in background
        from server import run_server
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Aspetta che il server si avvii
        time.sleep(2)
        
        # Invia la password al server
        try:
            response = requests.post(f"http://{self.ip_address}:5000/auth/setup", 
                                   json={"password": password}, timeout=5)
            if response.status_code == 201:
                # Password configurata con successo
                self.label_password.pack_forget()
                self.entry_password.pack_forget()
                self.btn_conferma_password.pack_forget()
                
                self.label_ip.configure(text=f"IP Server: {self.ip_address}")
                self.label_ip.pack(pady=5)
                self.btn_copia_ip.pack(pady=5)
            else:
                self.mostra_errore("Errore nella configurazione del server!")
        except Exception as e:
            self.mostra_errore(f"Errore di connessione: {e}")

    def copia_ip(self):
        if self.ip_address:
            pyperclip.copy(self.ip_address)
            self.destroy()  # Chiude la finestra e fa partire il resto del programma

    def scegli_client(self):
        ip = ctk.CTkInputDialog(title="IP Server Primario", text="Inserisci IP del server primario:").get_input()
        if not ip:
            return
        
        self.ip_address = ip
        
        # Controlla se il server ha già una password configurata
        try:
            response = requests.get(f"http://{ip}:5000/auth/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("password_configured"):
                    # Server ha password, chiedi la password
                    self.btn_server.pack_forget()
                    self.btn_client.pack_forget()
                    
                    self.label_password_client.pack(pady=5)
                    self.entry_password_client.pack(pady=5, fill="x", padx=50)
                    self.btn_verifica_password.pack(pady=10)
                else:
                    self.mostra_errore("Il server non ha ancora una password configurata!")
            else:
                self.mostra_errore("Impossibile comunicare con il server!")
        except Exception as e:
            self.mostra_errore(f"Errore di connessione al server: {e}")

    def verifica_password_client(self):
        password = self.entry_password_client.get()
        if not password:
            self.mostra_errore("Inserisci la password!")
            return
        
        # Verifica la password con il server
        try:
            response = requests.post(f"http://{self.ip_address}:5000/auth/login", 
                                   json={"password": password}, timeout=5)
            if response.status_code == 200:
                # Password corretta, salva configurazione
                self.password = password
                self.salva_config(False, self.ip_address)
                self.destroy()
            else:
                self.mostra_errore("Password errata!")
        except Exception as e:
            self.mostra_errore(f"Errore di connessione: {e}")

    def mostra_errore(self, messaggio):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Errore")
        error_window.geometry("300x100")
        error_window.grab_set()
        
        label = ctk.CTkLabel(error_window, text=messaggio)
        label.pack(pady=20)
        
        btn_ok = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
        btn_ok.pack(pady=10)

    def salva_config(self, is_primary, host_ip=None):
        config = configparser.ConfigParser()
        host = host_ip if not is_primary else self.ip_address
        config['server'] = {
            'is_primary': str(is_primary),
            'host': host,
            'port': '5000'
        }
        if self.password:
            config['auth'] = {
                'password': self.password
            }
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    def on_close(self):
        self.destroy()
        exit()

def esiste_config():
    return os.path.exists(CONFIG_FILE)

def leggi_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    is_primary = config.getboolean('server', 'is_primary')
    host = config.get('server', 'host')
    port = config.getint('server', 'port')
    password = config.get('auth', 'password', fallback=None)
    return is_primary, host, port, password
