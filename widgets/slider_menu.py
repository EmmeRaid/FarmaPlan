import customtkinter as ctk
from tkinter import StringVar, ttk
from tkcalendar import DateEntry
from datetime import date, timedelta, datetime
from forms.form_switcherform import AggiungiFormSwitcher
from forms.form_modifica_paziente_piano import FormModificaPazientePiano
from forms.form_stampa_pazienti import PaginaStampaPazienti

class SliderMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PlanLog")
        self.iconbitmap("Logo.ico")  # solo .ico su Windows
        self.geometry("900x600")
        self.resizable(False, False)
        # Key bindings
        self.bind("<F1>", lambda event: self.mostra_aggiungi())
        self.bind("<F2>", lambda event: self.mostra_modifica())
        self.bind("<F3>", lambda event: self.mostra_stampa())
        self.bind("<Escape>", self.conferma_uscita)



        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.menu_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, sticky="nswe")
        self.menu_frame.grid_rowconfigure(0, weight=1)

        self.label_menu = ctk.CTkLabel(self.menu_frame, text="Menu", font=("Arial", 20))
        self.label_menu.pack(pady=20)

        self.btn_aggiungi = ctk.CTkButton(self.menu_frame, text="Aggiungi Paziente", command=self.mostra_aggiungi)
        self.btn_aggiungi.pack(pady=10, padx=20)

        self.btn_modifica = ctk.CTkButton(self.menu_frame, text="Modifica Paziente", command=self.mostra_modifica)
        self.btn_modifica.pack(pady=10, padx=20)

        self.btn_stampa = ctk.CTkButton(self.menu_frame, text="Stampa Pazienti", command=self.mostra_stampa)
        self.btn_stampa.pack(pady=10, padx=20)
        
        self.btn_escape = ctk.CTkButton(self.menu_frame, text="Esci", command=self.conferma_uscita, hover_color="red")
        self.btn_escape.pack(pady=10, padx=20)

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        self.agg_form_switcher = None
        self.form_modifica = None
        self.pagina_stampa = None
        
    def conferma_uscita(self, event = None):
        finestra = ctk.CTkToplevel(self)
        finestra.title("Conferma Uscita")
        finestra.iconbitmap("Logo.ico") 
        finestra.geometry("300x120")
        finestra.grab_set() #Blocca interazione con finestra principale
        
        label = ctk.CTkLabel(finestra, text="Vuoi davvero uscire?")
        label.pack(pady= 15)
        
        pulsanti_frame= ctk.CTkFrame(finestra, fg_color= "transparent")
        pulsanti_frame.pack(pady=15)
        
        btn_si = ctk.CTkButton(pulsanti_frame, text="Sì", width=80, hover_color="red",command=self.destroy)
        btn_si.grid(row=0, column=0, padx=10)

        btn_no = ctk.CTkButton(pulsanti_frame, text="No", width=80, command=finestra.destroy)
        btn_no.grid(row=0, column=1, padx=10)

    def svuota_contenuto(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def mostra_aggiungi(self):
        self.svuota_contenuto()
        self.agg_form_switcher = AggiungiFormSwitcher(self.content_frame)
        self.agg_form_switcher.pack(fill="both", expand=True)

    def mostra_modifica(self):
        self.svuota_contenuto()
        self.form_modifica = FormModificaPazientePiano(self.content_frame)
        self.form_modifica.pack(fill="both", expand=True)

    def mostra_stampa(self):
        self.svuota_contenuto()
        self.pagina_stampa = PaginaStampaPazienti(self.content_frame)
        self.pagina_stampa.pack(fill="both", expand=True)
