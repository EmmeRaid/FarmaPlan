import customtkinter as ctk
from tkinter import StringVar, ttk
from tkcalendar import DateEntry
from datetime import date, timedelta, datetime
from forms.form_aggiungi_paziente import FormAggiungiPaziente
from forms.form_aggiungi_piano import FormAggiungiPiano



class AggiungiFormSwitcher(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.switch_var = ctk.StringVar(value="paziente")
        self.switch = ctk.CTkSegmentedButton(self, values=["paziente", "piano"], command=self.cambia_form)
        self.switch.grid(row=0, column=0, pady=10)

        self.form_container = ctk.CTkFrame(self)
        self.form_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        self.form_paziente = FormAggiungiPaziente(self.form_container, self.switch_to_piano)
        self.form_paziente.pack(fill="both", expand=True)

        self.form_piano = FormAggiungiPiano(self.form_container)

    def cambia_form(self, scelta):
        if scelta == "paziente":
            self.form_piano.pack_forget()
            self.form_paziente.pack(fill="both", expand=True)
        else:
            self.form_paziente.pack_forget()
            self.form_piano.pack(fill="both", expand=True)

    def switch_to_piano(self, codice_fiscale):
        # Passa al form aggiungi piano e inserisce il codice fiscale
        self.switch_var.set("piano")
        self.cambia_form("piano")
        self.form_piano.entry_cf_paziente.delete(0, "end")
        self.form_piano.entry_cf_paziente.insert(0, codice_fiscale)
   