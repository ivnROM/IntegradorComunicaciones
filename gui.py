import requests
from tkinter import filedialog
from datetime import datetime
import customtkinter as ctk

API_URL = "http://127.0.0.1:8000"
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

def abrir_modal_dispositivo(parent, refresh_callback, dispositivo=None):
    es_edicion = dispositivo is not None
    top = ctk.CTkToplevel(parent)
    top.title("Editar dispositivo" if es_edicion else "Agregar dispositivo")
    top.geometry("760x300")
    
    # Variables para los campos
    inputs = {}
    tipo_var = ctk.StringVar(value=dispositivo.get("tipo", "router") if es_edicion else "router")
    b_periodo_var = ctk.StringVar(value=dispositivo.get("b_periodo", "diario") if es_edicion else "diario")
    dia_var = ctk.StringVar()
    
    # Configurar día inicial si estamos editando
    if es_edicion and dispositivo.get("b_dia") is not None:
        b_dia_val = dispositivo.get("b_dia")
        periodo = dispositivo.get("b_periodo", "diario")
        if periodo == "semanal":
            # Convertir número a nombre del día
            dia_nombre = next((k for k, v in DIAS_SEMANA.items() if v == b_dia_val), "")
            dia_var.set(dia_nombre)
        elif periodo == "mensual":
            dia_var.set(str(b_dia_val))
    
    def toggle_campos(*_):
        periodo = b_periodo_var.get()
        if periodo == "diario":
            dia_menu.configure(state="disabled", fg_color="#1f1f1f")
            dia_var.set("")
        elif periodo == "semanal":
            dia_menu.configure(values=list(DIAS_SEMANA.keys()), state="normal", fg_color="#333333")
        elif periodo == "mensual":
            dia_menu.configure(values=[str(i) for i in range(1, 29)], state="normal", fg_color="#333333")
    
    def seleccionar_directorio():
        path = filedialog.askdirectory()
        if path:
            path_entry.delete(0, ctk.END)
            path_entry.insert(0, path)
    
    def guardar():
        try:
            # Procesar el día según el período
            b_dia_val = dia_var.get()
            if b_periodo_var.get() == "semanal":
                b_dia_val = int(DIAS_SEMANA.get(b_dia_val, 0)) if b_dia_val else None
            elif b_periodo_var.get() == "mensual":
                b_dia_val = int(b_dia_val) if b_dia_val and b_dia_val.isdigit() else None
            else:
                b_dia_val = None
            
            payload = {
                "nombre": inputs["nombre"].get(),
                "ip": inputs["ip"].get(),
                "tipo": tipo_var.get(),
                "usuario": inputs["usuario"].get(),
                "contrasena": inputs["contrasena"].get(),
                "puerto": int(inputs["puerto"].get()) if inputs["puerto"].get() else 0,
                "b_periodo": b_periodo_var.get(),
                "b_hora": hora_entry.get() or None,
                "b_dia": b_dia_val,
                "b_path": path_entry.get() or None
            }
            
            if es_edicion:
                response = requests.put(f"{API_URL}/dispositivos/{dispositivo['id']}", json=payload)
            else:
                response = requests.post(f"{API_URL}/dispositivos/", json=payload)
            
            if response.status_code in [200, 201]:
                print(f"Dispositivo {'actualizado' if es_edicion else 'creado'} exitosamente: ", response.json())
                top.destroy()
                refresh_callback()
            else:
                print(f"Error al {'actualizar' if es_edicion else 'crear'} dispositivo: ", response.status_code, response.text)
                
        except Exception as e:
            print(f"Error al guardar dispositivo: {e}")
    
    def eliminar():
        try:
            # Confirmar eliminación
            import tkinter.messagebox as msgbox
            if msgbox.askyesno("Confirnar eliminación", 
                              f"¿Estás seguro de que querés eliminar el dispositivo '{dispositivo['nombre']}'?\n\nEsta acción no se puede deshacer."):
                response = requests.delete(f"{API_URL}/dispositivos/{dispositivo['id']}")
                
                if response.status_code == 200:
                    print("Dispositivo eliminado exitosamente: ", response.json())
                    top.destroy()
                    refresh_callback()
                else:
                    print("Error al eliminar dispositivo: ", response.status_code, response.text)
                    msgbox.showerror("Error", f"No se pudo eliminar el dispositivo.\nCódigo: {response.status_code}")
                    
        except Exception as e:
            print(f"Error al eliminar dispositivo: {e}")
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", f"Error de conexión: {e}")
    
    # --- Widgets con grid layout ---
    # Campos básicos (columna izquierda)
    campos = [
        ("Nombre", "nombre"),
        ("IP", "ip"),
        ("Usuario", "usuario"),
        ("Contraseña", "contrasena"),
        ("Puerto", "puerto"),
    ]
    
    for i, (label, key) in enumerate(campos):
        ctk.CTkLabel(top, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        entry = ctk.CTkEntry(top)
        # Precargar datos si estamos editando
        if es_edicion and dispositivo.get(key):
            entry.insert(0, str(dispositivo.get(key, "")))
        entry.grid(row=i, column=1, padx=10, pady=5)
        inputs[key] = entry
    
    # Tipo de dispositivo (columna derecha)
    ctk.CTkLabel(top, text="Tipo").grid(row=0, column=2, padx=10, pady=5, sticky="e")
    tipo_menu = ctk.CTkOptionMenu(top, values=["router", "switch"], variable=tipo_var)
    tipo_menu.grid(row=0, column=3, padx=10, pady=5)
    
    # Período de backup
    ctk.CTkLabel(top, text="Periodo").grid(row=1, column=2, padx=10, pady=5, sticky="e")
    b_periodo_menu = ctk.CTkOptionMenu(top, values=["diario", "semanal", "mensual"], 
                                       variable=b_periodo_var, command=toggle_campos)
    b_periodo_menu.grid(row=1, column=3, padx=10, pady=5)
    
    # Hora
    ctk.CTkLabel(top, text="Hora (HH:MM)").grid(row=2, column=2, padx=10, pady=5, sticky="e")
    hora_entry = ctk.CTkEntry(top)
    if es_edicion and dispositivo.get("b_hora"):
        hora_entry.insert(0, dispositivo.get("b_hora"))
    hora_entry.grid(row=2, column=3, padx=10, pady=5)
    
    # Día
    ctk.CTkLabel(top, text="Día").grid(row=3, column=2, padx=10, pady=5, sticky="e")
    dia_menu = ctk.CTkOptionMenu(top, values=[], variable=dia_var, 
                                state="disabled", fg_color="#333333")
    dia_menu.grid(row=3, column=3, padx=10, pady=5)
    
    # Path con selector
    ctk.CTkLabel(top, text="Ruta de backup").grid(row=4, column=2, padx=10, pady=5, sticky="e")
    path_entry = ctk.CTkEntry(top, state="normal", width=200)
    if es_edicion and dispositivo.get("b_path"):
        path_entry.insert(0, dispositivo.get("b_path"))
    path_entry.grid(row=4, column=3, padx=10, pady=5)
    path_btn = ctk.CTkButton(top, text="Seleccionar", command=seleccionar_directorio, width=100)
    path_btn.grid(row=4, column=4, padx=5)
    
    # Botones
    if es_edicion:
        # Frame para los botones cuando es edición
        botones_frame = ctk.CTkFrame(top)
        botones_frame.grid(row=5, column=0, columnspan=5, pady=20)
        
        # Botón actualizar
        actualizar_btn = ctk.CTkButton(botones_frame, text="Actualizar Dispositivo", command=guardar)
        actualizar_btn.pack(side="left", padx=10)
        
        # Botón eliminar
        eliminar_btn = ctk.CTkButton(botones_frame, text="Eliminar Dispositivo", 
                                    command=eliminar, fg_color="#dc2626", hover_color="#991b1b")
        eliminar_btn.pack(side="right", padx=10)
    else:
        # Botón crear cuando es nuevo dispositivo
        texto_boton = "Crear Dispositivo"
        guardar_btn = ctk.CTkButton(top, text=texto_boton, command=guardar)
        guardar_btn.grid(row=5, column=0, columnspan=5, pady=20)
    
    # Configurar campos dinámicos según el período actual
    toggle_campos()
    
    top.grab_set()  # modal

# MainWindow
label_frame_dispositivos = ctk.CTkLabel(root, text="Dispositivos", font=ctk.CTkFont(size=14, weight="bold"))
frame_dispositivos = ctk.CTkFrame(root, width=150, corner_radius=0)
button_agregar_dispositivos = ctk.CTkButton(root, text="Agregar dispositivo", command=lambda: abrir_modal_dispositivo(root, lambda: cargar_dispositivos(frame_dispositivos)))


label_frame_dispositivos.pack(pady=10)
frame_dispositivos.pack(pady=10)
button_agregar_dispositivos.pack(pady=10)


# Ejemlpo de post
#disp = Dispositivo("Router1", "192.168.0.1", "router", "admin", "1234", 22)
#response = requests.post("http://127.0.0.1:8000/dispositivos/", json=disp.to_dict())

def agregar_dispositivo(root):
    top = ctk.CTkToplevel(root)
    top.title("Agregar Dispositivo")
    top.geometry("760x300")

    inputs = {}

    def toggle_campos(*_):
        periodo = b_periodo_var.get()
        if periodo == "diario":
            dia_menu.configure(state="disabled", fg_color="#1f1f1f")
        elif periodo == "semanal":
            dia_menu.configure(values=list(DIAS_SEMANA.keys()), state="normal", fg_color="#333333")
        elif periodo == "mensual":
            dia_menu.configure(values=[str(i) for i in range(1, 29)], state="normal", fg_color="#333333")

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
            "b_hora": hora_entry.get(),
            "b_dia": b_dia_val,
            "b_path": path_entry.get()
        }

        try:
            response = requests.post(API_URL + "/dispositivos", json=datos)
            if response.status_code == 200:
                print("Se cargo el dispositivo exitosamente: ", response.json())
            else:
                print("Error al enviar la solicitud: ", response.status_code, response.text)
        except Exception as e:
            print("Error de conexion: ", e)
        top.destroy()
        cargar_dispositivos(frame_dispositivos)
        

    # --- Widgets ---
    campos = [
        ("Nombre", "nombre"),
        ("IP", "ip"),
        ("Usuario", "usuario"),
        ("Contraseña", "contrasena"),
        ("Puerto", "puerto"),
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

    # Hora
    ctk.CTkLabel(top, text="Hora (HH:MM)").grid(row=2, column=2, padx=10, pady=5, sticky="e")
    hora_entry = ctk.CTkEntry(top)
    hora_entry.grid(row=2, column=3, padx=10, pady=5)

    # Día
    ctk.CTkLabel(top, text="Día").grid(row=3, column=2, padx=10, pady=5, sticky="e")
    dia_var = ctk.StringVar(value="")
    dia_menu = ctk.CTkOptionMenu(top, values=[], variable=dia_var, state="disabled", fg_color="#333333")
    dia_menu.grid(row=3, column=3, padx=10, pady=5)

    # Path con selector
    ctk.CTkLabel(top, text="Ruta de backup").grid(row=5, column=2, padx=10, pady=5, sticky="e")
    path_entry = ctk.CTkEntry(top, state="normal", width=200)
    path_entry.grid(row=5, column=3, padx=10, pady=5)
    path_btn = ctk.CTkButton(top, text="Seleccionar", command=seleccionar_directorio, width=100)
    path_btn.grid(row=5, column=4, padx=5)

    # Botón de enviar
    enviar_btn = ctk.CTkButton(top, text="Crear Dispositivo", command=enviar)
    enviar_btn.grid(row=6, column=0, columnspan=5, pady=20)

    toggle_campos()
    top.grab_set()  # modal

def cargar_dispositivos(frame_dispositivos):
    # Limpiar contenido anterior del frame
    for widget in frame_dispositivos.winfo_children():
        widget.destroy()

    try:
        respuesta = requests.get(f"{API_URL}/dispositivos/")
        respuesta.raise_for_status()
        dispositivos = respuesta.json()
    except Exception as e:
        print(f"Error al obtener dispositivos: {e}")
        ctk.CTkLabel(frame_dispositivos, text="Error al cargar dispositivos").pack(pady=10)
        return

    if not dispositivos:
        ctk.CTkLabel(frame_dispositivos, text="No hay dispositivos registrados").pack(pady=10)
        return

    for dispositivo in dispositivos:  # ← CORREGIDO ACÁ
        frame = ctk.CTkFrame(frame_dispositivos)
        frame.pack(padx=10, pady=5, fill="x")

        # Info del dispositivo (nombre, IP, tipo)
        texto = f"{dispositivo['nombre']} - {dispositivo['ip']} ({dispositivo['tipo']})"
        ctk.CTkLabel(frame, text=texto).pack(side="left", padx=10)

        # Botón de edición
        ctk.CTkButton(
            frame,
            text="✎",
            width=30,
            command=lambda d=dispositivo: abrir_modal_dispositivo(
                frame_dispositivos.master,  # Esto asume que el padre de frame_dispositivos es la ventana root
                lambda: cargar_dispositivos(frame_dispositivos),
                dispositivo=d
            )
        ).pack(side="right", padx=10)

def editar_dispositivo(dispositivo):
    # Acá podrías reusar tu ventana de edición para pasarle los datos
    print(f"Editar: {dispositivo['nombre']} - {dispositivo['ip']}")
    # agregar_dispositivo(modificar=True, datos=dispositivo)


cargar_dispositivos(frame_dispositivos)
root.mainloop()
