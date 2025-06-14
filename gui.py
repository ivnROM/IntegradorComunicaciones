from tkinter import filedialog
from datetime import datetime
from backup import generar_backup_manual
import requests
import customtkinter as ctk
import socket
import threading
import time
import os
import glob

API_URL = "http://127.0.0.1:8000"

# Configuración Inicial
ctk.set_appearance_mode("dark")
root = ctk.CTk()  # reemplaza Tk()
root.geometry("400x550")  # Aumentado para el nuevo frame
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

def obtener_ultimo_backup():
    """
    Obtiene información del último backup realizado buscando en los directorios de backup
    """
    try:
        # Obtener dispositivos para saber sus rutas de backup
        respuesta = requests.get(f"{API_URL}/dispositivos/")
        if respuesta.status_code != 200:
            return None
            
        dispositivos = respuesta.json()
        if not dispositivos:
            return None
        
        ultimo_backup = None
        ultimo_timestamp = 0
        
        for dispositivo in dispositivos:
            backup_path = dispositivo.get('b_path')
            nombre_dispositivo = dispositivo.get('nombre', '')
            
            if backup_path and os.path.exists(backup_path):
                # Buscar archivos que empiecen con el nombre del dispositivo
                patron = os.path.join(backup_path, f"{nombre_dispositivo}_backup_*.rsc")
                archivos = glob.glob(patron)
                
                for archivo in archivos:
                    try:
                        # Obtener timestamp del archivo
                        timestamp_archivo = os.path.getmtime(archivo)
                        
                        if timestamp_archivo > ultimo_timestamp:
                            ultimo_timestamp = timestamp_archivo
                            tamaño = os.path.getsize(archivo)
                            tamaño_formateado = f"{tamaño / 1024:.2f} KB" if tamaño < 1024*1024 else f"{tamaño / (1024*1024):.2f} MB"
                            
                            ultimo_backup = {
                                'dispositivo': nombre_dispositivo,
                                'timestamp': datetime.fromtimestamp(timestamp_archivo).isoformat(),
                                'archivo': os.path.basename(archivo),
                                'ruta_completa': archivo,
                                'tamaño': tamaño_formateado,
                                'estado': 'exitoso' if os.path.exists(archivo) else 'error'
                            }
                    except Exception as e:
                        print(f"Error al procesar archivo {archivo}: {e}")
                        continue
        
        return ultimo_backup
        
    except Exception as e:
        print(f"Error al obtener último backup: {e}")
        return None

def actualizar_info_ultimo_backup(frame_ultimo_backup):
    """
    Actualiza la información del último backup en el frame
    """
    # Limpiar frame anterior
    for widget in frame_ultimo_backup.winfo_children():
        widget.destroy()
    
    # Título del frame
    titulo_label = ctk.CTkLabel(frame_ultimo_backup, 
                               text="📋 Último Backup Realizado", 
                               font=ctk.CTkFont(size=14, weight="bold"))
    titulo_label.pack(pady=(10, 5))
    
    # Obtener datos del último backup
    ultimo_backup = obtener_ultimo_backup()
    
    if ultimo_backup:
        # Frame contenedor para la info
        info_frame = ctk.CTkFrame(frame_ultimo_backup, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Dispositivo
        dispositivo_label = ctk.CTkLabel(info_frame, 
                                       text=f"🖥️ Dispositivo: {ultimo_backup.get('dispositivo', 'N/A')}")
        dispositivo_label.pack(anchor="w", padx=5, pady=2)
        
        # Fecha y hora
        timestamp = ultimo_backup.get('timestamp', 'N/A')
        if timestamp != 'N/A':
            try:
                # Convertir timestamp a formato legible
                dt = datetime.fromisoformat(timestamp)
                fecha_formateada = dt.strftime("%d/%m/%Y - %H:%M:%S")
            except:
                fecha_formateada = timestamp
        else:
            fecha_formateada = 'N/A'
            
        fecha_label = ctk.CTkLabel(info_frame, 
                                 text=f"🕐 Fecha/Hora: {fecha_formateada}")
        fecha_label.pack(anchor="w", padx=5, pady=2)
        
        # Estado del backup
        estado = ultimo_backup.get('estado', 'N/A')
        estado_color = "#22c55e" if estado == "exitoso" else "#ef4444" if estado == "error" else "#f59e0b"
        estado_icon = "✅" if estado == "exitoso" else "❌" if estado == "error" else "⚠️"
        
        estado_label = ctk.CTkLabel(info_frame, 
                                  text=f"{estado_icon} Estado: {estado.title()}", 
                                  text_color=estado_color)
        estado_label.pack(anchor="w", padx=5, pady=2)
        
        # Archivo de backup
        archivo = ultimo_backup.get('archivo', 'N/A')
        archivo_label = ctk.CTkLabel(info_frame, 
                                   text=f"📁 Archivo: {archivo}")
        archivo_label.pack(anchor="w", padx=5, pady=2)
        
        # Tamaño del archivo
        tamaño = ultimo_backup.get('tamaño', 'N/A')
        tamaño_label = ctk.CTkLabel(info_frame, 
                                  text=f"📏 Tamaño: {tamaño}")
        tamaño_label.pack(anchor="w", padx=5, pady=2)
            
    else:
        # No hay información de backup
        no_backup_label = ctk.CTkLabel(frame_ultimo_backup, 
                                     text="❌ No hay backups disponibles",
                                     text_color="#ef4444")
        no_backup_label.pack(pady=10)
    
    # Timestamp de actualización
    ahora = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    actualizado_label = ctk.CTkLabel(frame_ultimo_backup, 
                                   text=f"🔄 Actualizado: {ahora}",
                                   font=ctk.CTkFont(size=10),
                                   text_color="#6b7280")
    actualizado_label.pack(pady=(5, 10))

def test_conectividad(ip, puerto, timeout=3):
    """
    Testa la conectividad a un dispositivo con un socket
    Devuelve True si está conectado, False si no
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        resultado = sock.connect_ex((ip, int(puerto)))
        sock.close()
        return resultado == 0
    except Exception as e:
        print(f"Error al testear conectividad a {ip}:{puerto} - {e}")
        return False

def actualizar_estado_dispositivo(frame, dispositivo, label_estado):
    """
    Actualiza el estado de un dispositivo en un hilo separado
    """
    def _actualizar():
        try:
            # Test de conectividad
            conectado = test_conectividad(dispositivo['ip'], dispositivo['puerto'])
            
            # Actualizar UI en el hilo principal
            def actualizar_ui():
                if conectado:
                    label_estado.configure(text="🟢", text_color="#22c55e")  # Verde
                    # Tooltip con estado
                    label_estado._text = f"🟢 ONLINE"
                else:
                    label_estado.configure(text="🔴", text_color="#ef4444")  # Rojo
                    label_estado._text = f"🔴 OFFLINE"
            
            # Ejecutar actualización en el hilo principal
            root.after(0, actualizar_ui)
            
        except Exception as e:
            print(f"Error al actualizar estado de {dispositivo['nombre']}: {e}")
            root.after(0, lambda: label_estado.configure(text="⚠️", text_color="#f59e0b"))
    
    # Ejecutar en hilo separado para no bloquear la UI
    threading.Thread(target=_actualizar, daemon=True).start()

def generar_backup_manual_wrapper(dispositivo, frame_ultimo_backup):
    """
    Wrapper para generar backup manual y actualizar la info del último backup
    """
    def _generar():
        generar_backup_manual(dispositivo)
        # Actualizar info del último backup después del backup
        time.sleep(2)  # Esperar un poco para que se procese el backup
        root.after(0, lambda: actualizar_info_ultimo_backup(frame_ultimo_backup))
    
    threading.Thread(target=_generar, daemon=True).start()

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
            # Validar campos obligatorios
            campos_obligatorios = {
                "nombre": inputs["nombre"].get().strip(),
                "ip": inputs["ip"].get().strip(),
                "usuario": inputs["usuario"].get().strip(),
                "contrasena": inputs["contrasena"].get().strip(),
                "puerto": inputs["puerto"].get().strip()
            }
            
            # Verificar si algún campo está vacío
            campos_vacios = []
            for campo, valor in campos_obligatorios.items():
                if not valor:
                    campos_vacios.append(campo.replace("_", " ").title())
            
            # Si hay campos vacíos, mostrar mensaje de error
            if campos_vacios:
                import tkinter.messagebox as msgbox
                campos_faltantes = ", ".join(campos_vacios)
                msgbox.showerror(
                    "Campos obligatorios", 
                    f"Los siguientes campos son obligatorios y no pueden estar vacíos:\n\n{campos_faltantes}\n\nPor favor, completá todos los campos antes de continuar."
                )
                return
            
            # Validar que el puerto sea un número válido
            try:
                puerto_num = int(campos_obligatorios["puerto"])
                if puerto_num <= 0 or puerto_num > 65535:
                    raise ValueError("Puerto fuera de rango")
            except ValueError:
                import tkinter.messagebox as msgbox
                msgbox.showerror(
                    "Puerto inválido", 
                    "El puerto debe ser un número válido entre 1 y 65535."
                )
                return
            
            # Validar formato de IP básico (opcional, pero recomendado)
            ip_parts = campos_obligatorios["ip"].split(".")
            if len(ip_parts) != 4:
                import tkinter.messagebox as msgbox
                msgbox.showerror(
                    "IP inválida", 
                    "La dirección IP debe tener el formato xxx.xxx.xxx.xxx"
                )
                return
            
            try:
                for part in ip_parts:
                    num = int(part)
                    if num < 0 or num > 255:
                        raise ValueError("Parte de IP fuera de rango")
            except ValueError:
                import tkinter.messagebox as msgbox
                msgbox.showerror(
                    "IP inválida", 
                    "La dirección IP contiene valores inválidos. Cada parte debe ser un número entre 0 y 255."
                )
                return
            
            # Validar hora si se ingresó
            hora_valor = hora_entry.get().strip()
            if hora_valor:
                try:
                    # Verificar formato HH:MM
                    hora_parts = hora_valor.split(":")
                    if len(hora_parts) != 2:
                        raise ValueError("Formato incorrecto")
                    
                    hora = int(hora_parts[0])
                    minuto = int(hora_parts[1])
                    
                    if hora < 0 or hora > 23 or minuto < 0 or minuto > 59:
                        raise ValueError("Valores fuera de rango")
                        
                except ValueError:
                    import tkinter.messagebox as msgbox
                    msgbox.showerror(
                        "Hora inválida", 
                        "La hora debe tener el formato HH:MM (por ejemplo: 14:30)\nHora: 00-23, Minutos: 00-59"
                    )
                    return
            
            # Validar día según el período
            periodo = b_periodo_var.get()
            b_dia_val = dia_var.get()
            
            if periodo == "semanal" and b_dia_val:
                if b_dia_val not in DIAS_SEMANA:
                    import tkinter.messagebox as msgbox
                    msgbox.showerror(
                        "Día inválido", 
                        "Seleccioná un día válido de la semana."
                    )
                    return
                b_dia_val = int(DIAS_SEMANA.get(b_dia_val, 0))
            elif periodo == "mensual" and b_dia_val:
                try:
                    b_dia_val = int(b_dia_val)
                    if b_dia_val < 1 or b_dia_val > 28:
                        raise ValueError("Día fuera de rango")
                except ValueError:
                    import tkinter.messagebox as msgbox
                    msgbox.showerror(
                        "Día inválido", 
                        "Para período mensual, el día debe ser un número entre 1 y 28."
                    )
                    return
            else:
                b_dia_val = None
            
            # Si todas las validaciones pasaron, crear el payload
            payload = {
                "nombre": campos_obligatorios["nombre"],
                "ip": campos_obligatorios["ip"],
                "tipo": tipo_var.get(),
                "usuario": campos_obligatorios["usuario"],
                "contrasena": campos_obligatorios["contrasena"],
                "puerto": int(campos_obligatorios["puerto"]),
                "b_periodo": periodo,
                "b_hora": hora_valor or None,
                "b_dia": b_dia_val,
                "b_path": path_entry.get().strip() or None
            }
            
            # Enviar request
            if es_edicion:
                response = requests.put(f"{API_URL}/dispositivos/{dispositivo['id']}", json=payload)
            else:
                response = requests.post(f"{API_URL}/dispositivos/", json=payload)
            
            if response.status_code in [200, 201]:
                print(f"Dispositivo {'actualizado' if es_edicion else 'creado'} exitosamente: ", response.json())
                import tkinter.messagebox as msgbox
                msgbox.showinfo(
                    "Éxito", 
                    f"Dispositivo {'actualizado' if es_edicion else 'creado'} correctamente."
                )
                top.destroy()
                refresh_callback()
            else:
                print(f"Error al {'actualizar' if es_edicion else 'crear'} dispositivo: ", response.status_code, response.text)
                import tkinter.messagebox as msgbox
                msgbox.showerror(
                    "Error del servidor", 
                    f"Error al {'actualizar' if es_edicion else 'crear'} el dispositivo.\nCódigo: {response.status_code}\nVerificá la conexión con el servidor."
                )
                
        except Exception as e:
            print(f"Error al guardar dispositivo: {e}")
            import tkinter.messagebox as msgbox
            msgbox.showerror(
                "Error inesperado", 
                f"Ocurrió un error inesperado:\n{str(e)}\n\nVerificá los datos ingresados y la conexión."
            )

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
button_agregar_dispositivos = ctk.CTkButton(root, text="Agregar dispositivo", 
                                          command=lambda: abrir_modal_dispositivo(root, lambda: cargar_dispositivos(frame_dispositivos)))

# Botón para refrescar estados
button_refresh = ctk.CTkButton(root, text="🔄 Refrescar Estados", 
                              command=lambda: cargar_dispositivos(frame_dispositivos),
                              width=120, height=28)

# Frame de último backup (abajo)
frame_ultimo_backup = ctk.CTkFrame(root, corner_radius=10)

# Botón para actualizar info del último backup
button_refresh_backup = ctk.CTkButton(root, text="🔄 Actualizar Info Backup", 
                                    command=lambda: actualizar_info_ultimo_backup(frame_ultimo_backup),
                                    width=140, height=28)

# Posicionamiento de widgets
label_frame_dispositivos.pack(pady=10)
frame_dispositivos.pack(pady=10)
button_agregar_dispositivos.pack(pady=5)
button_refresh.pack(pady=5)

# Frame y botón de último backup al final
frame_ultimo_backup.pack(pady=10, padx=10, fill="x")
button_refresh_backup.pack(pady=5)

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
    
    for dispositivo in dispositivos:
        frame = ctk.CTkFrame(frame_dispositivos)
        frame.pack(padx=10, pady=5, fill="x")
        
        # Frame para el contenido del dispositivo
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=5, pady=5)
        
        # Icono de estado (inicialmente desconocido)
        estado_label = ctk.CTkLabel(content_frame, text="⏳", font=ctk.CTkFont(size=16))
        estado_label.pack(side="left", padx=(5, 10))
        
        # Info del dispositivo (nombre, IP, tipo)
        texto = f"{dispositivo['nombre']} - {dispositivo['ip']} ({dispositivo['tipo']})"
        info_label = ctk.CTkLabel(content_frame, text=texto)
        info_label.pack(side="left", padx=5)
        
        # Botones en el lado derecho
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(side="right", padx=5)
        
        # Botón de test manual
        test_btn = ctk.CTkButton(
            buttons_frame,
            text="🔍",
            width=30,
            height=30,
            command=lambda d=dispositivo, lbl=estado_label: actualizar_estado_dispositivo(frame, d, lbl)
        )
        test_btn.pack(side="right", padx=2)
        
        # Botón backup manual - modificado para actualizar info del último backup
        backup_btn = ctk.CTkButton(
            buttons_frame,
            text="💾",
            width=30,
            height=30,
            command=lambda d=dispositivo: generar_backup_manual_wrapper(d, frame_ultimo_backup)
        )
        backup_btn.pack(side="right", padx=2)
        
        # Botón de edición
        edit_btn = ctk.CTkButton(
            buttons_frame,
            text="✎",
            width=30,
            height=30,
            command=lambda d=dispositivo: abrir_modal_dispositivo(
                frame_dispositivos.master,
                lambda: cargar_dispositivos(frame_dispositivos),
                dispositivo=d
            )
        )
        edit_btn.pack(side="right", padx=2)
        
        # Iniciar test de conectividad automáticamente
        actualizar_estado_dispositivo(frame, dispositivo, estado_label)

def editar_dispositivo(dispositivo):
    # Acá podrías reusar tu ventana de edición para pasarle los datos
    print(f"Editar: {dispositivo['nombre']} - {dispositivo['ip']}")
    # agregar_dispositivo(modificar=True, datos=dispositivo)

# Función para refrescar estados automáticamente cada 30 segundos
def auto_refresh():
    """Refresca automáticamente los estados cada 30 segundos"""
    def _refresh():
        while True:
            time.sleep(30)  # Esperar 30 segundos
            try:
                # Ejecutar en el hilo principal
                root.after(0, lambda: cargar_dispositivos(frame_dispositivos))
                # También actualizar info del último backup
                root.after(0, lambda: actualizar_info_ultimo_backup(frame_ultimo_backup))
            except:
                break  # Si la ventana se cerró, salir del loop
    
    # Ejecutar en hilo separado
    threading.Thread(target=_refresh, daemon=True).start()

# Cargar datos iniciales
cargar_dispositivos(frame_dispositivos)
actualizar_info_ultimo_backup(frame_ultimo_backup)

# auto_refresh()  # Descomentar para que refresque automaticamente

root.mainloop()
