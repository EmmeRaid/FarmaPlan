import customtkinter as ctk
import os

def popup_dark(titolo, messaggio):
    popup = ctk.CTkToplevel()
    popup.title(titolo)
    popup.geometry("300x150")
    popup.grab_set()  # modal

    # Percorso alla cartella superiore (es. ../Logo.ico)
    icon_path = os.path.join(os.path.dirname(__file__), "..", "Logo.ico")
    if os.path.exists(icon_path):
        popup.iconbitmap(icon_path)

    label = ctk.CTkLabel(popup, text=messaggio, wraplength=280)
    label.pack(pady=20, padx=20)

    btn_ok = ctk.CTkButton(popup, text="OK", command=popup.destroy)
    btn_ok.pack(pady=10)
