import threading
from widgets.slider_menu import SliderMenu
from server import run_server
from configurazione import esiste_config, leggi_config, ConfigurazioneIniziale
import customtkinter as ctk
import os

def main():
    if not esiste_config():
        # Se manca config.ini, apri la finestra di configurazione (bloccante)
        config_window = ConfigurazioneIniziale()
        config_window.mainloop()

    is_primary, host, port, password = leggi_config()

    if is_primary:
        # Avvia server solo se questo PC è primario
        threading.Thread(target=run_server, args=(host, port), daemon=True).start()

    # Salva la password in una variabile globale per l'autenticazione
    os.environ['SERVER_PASSWORD'] = password or ""

    # Avvia la GUI principale
    app = SliderMenu()
    app.mainloop()

if __name__ == "__main__":

    ctk.set_appearance_mode("System")  # opzionale, per tema sistema
    ctk.set_default_color_theme("green")
    main()
