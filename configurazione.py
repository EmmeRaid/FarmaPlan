import os
import configparser
import customtkinter as ctk
import socket
import pyperclip

CONFIG_FILE = "config.ini"  # Percorso del file di configurazione

class ConfigurazioneIniziale(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("350x250")
        self.title("Configurazione iniziale")

        self.label_info = ctk.CTkLabel(self, text="Seleziona il ruolo del PC:", font=("Arial", 16))
        self.label_info.pack(pady=20)

        self.btn_server = ctk.CTkButton(self, text="Server Primario", command=self.scegli_server)
        self.btn_server.pack(pady=10, fill="x", padx=50)

        self.btn_client = ctk.CTkButton(self, text="Client Secondario", command=self.scegli_client)
        self.btn_client.pack(pady=10, fill="x", padx=50)

        self.label_ip = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.btn_copia_ip = ctk.CTkButton(self, text="Copia IP e Avvia", command=self.copia_ip)

        self.label_ip.pack_forget()
        self.btn_copia_ip.pack_forget()

        self.ip_address = ""
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def scegli_server(self):
        hostname = socket.gethostname()
        try:
            self.ip_address = socket.gethostbyname(hostname)
        except Exception:
            self.ip_address = "0.0.0.0"

        self.label_ip.configure(text=f"IP Server: {self.ip_address}")
        self.label_ip.pack(pady=5)
        self.btn_copia_ip.pack(pady=5)

        self.salva_config(True, self.ip_address)

    def copia_ip(self):
        if self.ip_address:
            pyperclip.copy(self.ip_address)
            self.destroy()  # Chiude la finestra e fa partire il resto del programma

    def scegli_client(self):
        ip = ctk.CTkInputDialog(title="IP Server Primario", text="Inserisci IP del server primario:").get_input()
        if not ip:
            return
        self.salva_config(False, ip)
        self.destroy()

    def salva_config(self, is_primary, host_ip=None):
        config = configparser.ConfigParser()
        host = host_ip if not is_primary else self.ip_address
        config['server'] = {
            'is_primary': str(is_primary),
            'host': host,
            'port': '5000'
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
    return is_primary, host, port
