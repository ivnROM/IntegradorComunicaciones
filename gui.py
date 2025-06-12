import requests
from tkinter import filedialog
from datetime import datetime
import customtkinter as ctk

API_URL = "http://127.0.0.1:8000/dispositivos/"
# Configuración Inicial
ctk.set_appearance_mode("dark")
root = ctk.CTk()  # reemplaza Tk()
root.geometry("300x400")
root.title("Gestor de Backups")

# Mapeo de días de la semana
DIAS_SEMANA = {
    "Lunes": "1",
    "Martes": "2",
    "Miércoles": "3",
    "Jueves": "4",
    "Viernes": "5",
    "Sábado": "6",
    "Domingo": "7"
}

def agregar_dispositivo(root):
    top = ctk.CTkToplevel(root)
    top.title("Agregar Dispositivo")
    top.geometry("700x400")

    inputs = {}

    def toggle_campos(*_):
        periodo = b_periodo_var.get()
        if periodo == "diario":
            dia_menu.configure(state="disabled", fg_color="#1f1f1f")
            mes_entry.configure(state="disabled", fg_color="#1f1f1f")
        elif periodo == "semanal":
            dia_menu.configure(values=list(DIAS_SEMANA.keys()), state="normal", fg_color="#333333")
            mes_entry.configure(state="disabled", fg_color="#1f1f1f")
        elif periodo == "mensual":
            dia_menu.configure(values=[str(i) for i in range(1, 29)], state="normal", fg_color="#333333")
            mes_entry.configure(state="normal", fg_color="#333333")

    def seleccionar_directorio():
        path = filedialog.askdirectory()
        if path:
            path_entry.delete(0, ctk.END)
            path_entry.insert(0, path)

    def enviar():
        b_dia_val = dia_var.get()
        if b_periodo_var.get() == "semanal":
            b_dia_val = int(DIAS_SEMANA.get(b_dia_val, 0)) if b_dia_val else None
        elif b_periodo_var.get() == "mensual":
            b_dia_val = int(b_dia_val) if b_dia_val.isdigit() else None
        else:
            b_dia_val = None

        datos = {
            "nombre": inputs["nombre"].get(),
            "ip": inputs["ip"].get(),
            "tipo": tipo_var.get(),
            "usuario": inputs["usuario"].get(),
            "contrasena": inputs["contrasena"].get(),
            "puerto": int(inputs["puerto"].get()),
            "b_periodo": b_periodo_var.get(),
            "b_hora": inputs["b_hora"].get(),
            "b_dia": b_dia_val,
            "b_mes": int(mes_entry.get()) if mes_entry.get().isdigit() else None,
            "b_path": path_entry.get()
        }
        print("Datos listos para crear:", datos)
        top.destroy()

    # --- Widgets ---
    campos = [
        ("Nombre", "nombre"),
        ("IP", "ip"),
        ("Usuario", "usuario"),
        ("Contraseña", "contrasena"),
        ("Puerto", "puerto"),
        ("Hora (HH:MM)", "b_hora")
    ]

    for i, (label, key) in enumerate(campos):
        ctk.CTkLabel(top, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        entry = ctk.CTkEntry(top)
        entry.grid(row=i, column=1, padx=10, pady=5)
        inputs[key] = entry

    # Tipo de dispositivo
    ctk.CTkLabel(top, text="Tipo").grid(row=0, column=2, padx=10, pady=5, sticky="e")
    tipo_var = ctk.StringVar(value="router")
    tipo_menu = ctk.CTkOptionMenu(top, values=["router", "switch"], variable=tipo_var)
    tipo_menu.grid(row=0, column=3, padx=10, pady=5)

    # Período de backup
    ctk.CTkLabel(top, text="Periodo").grid(row=1, column=2, padx=10, pady=5, sticky="e")
    b_periodo_var = ctk.StringVar(value="diario")
    b_periodo_menu = ctk.CTkOptionMenu(top, values=["diario", "semanal", "mensual"], variable=b_periodo_var,
                                       command=toggle_campos)
    b_periodo_menu.grid(row=1, column=3, padx=10, pady=5)

    # Día
    ctk.CTkLabel(top, text="Día").grid(row=2, column=2, padx=10, pady=5, sticky="e")
    dia_var = ctk.StringVar(value="")
    dia_menu = ctk.CTkOptionMenu(top, values=[], variable=dia_var, state="disabled", fg_color="#333333")
    dia_menu.grid(row=2, column=3, padx=10, pady=5)

    # Mes
    ctk.CTkLabel(top, text="Mes").grid(row=3, column=2, padx=10, pady=5, sticky="e")
    mes_entry = ctk.CTkEntry(top, state="disabled", fg_color="#333333")
    mes_entry.grid(row=3, column=3, padx=10, pady=5)

    # Path con selector
    ctk.CTkLabel(top, text="Ruta de backup").grid(row=4, column=2, padx=10, pady=5, sticky="e")
    path_entry = ctk.CTkEntry(top, width=200)
    path_entry.grid(row=4, column=3, padx=10, pady=5)
    path_btn = ctk.CTkButton(top, text="Seleccionar", command=seleccionar_directorio, width=100)
    path_btn.grid(row=4, column=4, padx=5)

    # Botón de enviar
    enviar_btn = ctk.CTkButton(top, text="Crear Dispositivo", command=enviar)
    enviar_btn.grid(row=6, column=0, columnspan=5, pady=20)

    toggle_campos()
    top.grab_set()  # modal


# MainWindow
label_frame_dispositivos = ctk.CTkLabel(root, text="Dispositivos", font=ctk.CTkFont(size=14, weight="bold"))
frame_dispositivos = ctk.CTkFrame(root, width=150, corner_radius=0)
button_agregar_dispositivos = ctk.CTkButton(root, text="Agregar dispositivo", command=lambda: agregar_dispositivo(root))

label_frame_dispositivos.pack(pady=10)
frame_dispositivos.pack(pady=10)
button_agregar_dispositivos.pack(pady=10)

root.mainloop()

# Ejemlpo de post
#disp = Dispositivo("Router1", "192.168.0.1", "router", "admin", "1234", 22)
#response = requests.post("http://127.0.0.1:8000/dispositivos/", json=disp.to_dict())

