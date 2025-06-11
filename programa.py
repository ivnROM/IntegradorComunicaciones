import requests
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from widgets import calendarwidget

API_URL = "http://127.0.0.1:8000/dispositivos/"

global rootwin
global dispositivos

class Dispositivo:
    def __init__( self, nombre: str, ip: str, tipo: str, usuario: str, contrasena: str, puerto: int, b_periodo: int | None = None, b_hora: str | None = None, b_dia: str | None = None, b_mes: int | None = None, b_path: str | None = None):
        self.nombre = nombre
        self.ip = ip
        self.tipo = tipo
        self.usuario = usuario
        self.contrasena = contrasena
        self.puerto = puerto
        self.b_periodo = b_periodo
        self.b_hora = b_hora
        self.b_dia = b_dia
        self.b_mes = b_mes
        self.b_path = b_path

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "ip": self.ip,
            "tipo": self.tipo,
            "usuario": self.usuario,
            "contrasena": self.contrasena,
            "puerto": self.puerto,
            "b_periodo": self.b_periodo,
            "b_hora": self.b_hora,
            "b_dia": self.b_dia,
            "b_mes": self.b_mes,
            "b_path": self.b_path,
        }

def asignar_rootwin(w: Tk):
    global rootwin
    rootwin = w


# crud
def c_api(dispositivo_body):
    response = requests.post(url=API_URL, json=dispositivo_body)
    return response

def r_api():
    response = requests.get(url=API_URL)
    if response.status_code == 200:
        return response.json()  # lista de dispositivos
    else:
        return []

def u_api():
    return 

def d_api():
    return 

# ventana que abre la creación de un dispositivo
def nuevo_dispositivo():
    global rootwin
    w = Toplevel(rootwin)
    # Variables
    nombre_var = StringVar()
    ip_var = StringVar()
    tipo_var = StringVar()
    usuario_var = StringVar()
    contrasena_var = StringVar()
    puerto_var = IntVar()
    b_periodo_var = StringVar()
    b_hora_var = StringVar()
    b_dia_var = StringVar()
    b_mes_var = IntVar()
    b_path_var = StringVar()

    main_frame = ttk.LabelFrame(w, text="Lista de dispositivos")
    details_frame = ttk.LabelFrame(w, text="Detalles del dispositivo")
    main_frame.grid()
    details_frame.grid()

    def seleccionar_directorio():
        ruta = filedialog.askdirectory()
        if ruta:
            b_path_var.set(ruta)
            ttk.Entry(details_frame, textvariable=b_path_var, state='readonly', width=50).grid(row=8, column=1)

    # ------- datos principales -------
    ttk.Label(main_frame, text="Nombre").grid(row=0, column=0, padx=5)
    ttk.Entry(main_frame, textvariable=nombre_var).grid(row=0, column=1, padx=5)
    ttk.Label(main_frame, text="IP").grid(row=1, column=0, padx=5)
    ttk.Entry(main_frame, textvariable=ip_var).grid(row=1, column=1, padx=5)
    ttk.Label(main_frame, text="Tipo").grid(row=0, column=2, padx=5)
    ttk.Combobox(main_frame, textvariable=tipo_var, values=["router", "switch", "pc"]).grid(row=0, column=3, padx=5)
    # ------- detalles -------
    ttk.Label(details_frame, text="Usuario").grid(row=0, column=0, pady=5, sticky="w")
    ttk.Entry(details_frame, textvariable=usuario_var).grid(row=0, column=1, pady=5, sticky="ew")
    ttk.Label(details_frame, text="Contraseña").grid(row=1, column=0, pady=5, sticky="w")
    ttk.Entry(details_frame, textvariable=contrasena_var, show="*").grid(row=1, column=1, pady=5, sticky="ew")
    ttk.Label(details_frame, text="Puerto").grid(row=2, column=0, pady=5, sticky="w")
    ttk.Entry(details_frame, textvariable=puerto_var).grid(row=2, column=1, pady=5, sticky="ew")
    ttk.Label(details_frame, text="Configuración de Backup").grid(row=3, column=0, columnspan=2, pady=(10,5), sticky="w")
    ttk.Label(details_frame, text="Periodo").grid(row=4, column=0, pady=2, sticky="w")
    ttk.Combobox(details_frame, textvariable=b_periodo_var, values=["Diario", "Semanal", "Mensual"]).grid(row=4, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Hora").grid(row=5, column=0, pady=2, sticky="w")
    ttk.Entry(details_frame, textvariable=b_hora_var).grid(row=5, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Día").grid(row=6, column=0, pady=2, sticky="w")
    ttk.Spinbox(details_frame, from_=1, to=28, textvariable=b_dia_var).grid(row=6, column=0, pady=2, sticky="w")
    ttk.Combobox(details_frame, textvariable=b_dia_var, values=["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]).grid(row=6, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Mes").grid(row=7, column=0, pady=2, sticky="w")
    ttk.Spinbox(details_frame, from_=1, to=12, textvariable=b_mes_var).grid(row=7, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Ruta Backup").grid(row=8, column=0, pady=2, sticky="w")
    ttk.Button(details_frame, text="Elegir directorio", command=seleccionar_directorio).grid(row=8, column=0)
    ttk.Entry(details_frame, textvariable=b_path_var, state='readonly', width=50).grid(row=8, column=1)
    
    def enviar_y_cerrar():
        print(b_periodo_var.get())
        match (b_periodo_var.get()):
            case "Diario":
                b_periodo_int = 1
            case "Semanal":
                b_periodo_int = 2
            case "Mensual":
                b_periodo_int = 3
            case _:
                exit("No deberia pasar esto nunca")

        dispositivo = Dispositivo(nombre_var.get(), ip_var.get(), tipo_var.get(), usuario_var.get(), contrasena_var.get(), puerto_var.get(), b_periodo_int, b_hora_var.get(), b_dia_var.get(), b_mes_var.get(), b_path_var.get())
        try:
            response = c_api(dispositivo.to_dict())
            if response.status_code == 200 or response.status_code == 201:
                print("Dispositivo agregado")
            else:
                print(f"Error agregando dispositivo: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error de conexión: {e}")

        cargar_dispositivos()
        w.destroy()

    # crear la clase en base a lo ingresado
    ttk.Button(w, text="Agregar", command=enviar_y_cerrar).grid()
    return
    
# ventana que abre la edición del dispositivo actualmente seleccionado
def editar_dispositivo(dispositivo):
    global rootwin
    w = Toplevel(rootwin)
    # Variables
    nombre_var = StringVar()
    ip_var = StringVar()
    tipo_var = StringVar()
    usuario_var = StringVar()
    contrasena_var = StringVar()
    puerto_var = IntVar()
    b_periodo_var = StringVar()
    b_hora_var = StringVar()
    b_dia_var = StringVar()
    b_mes_var = IntVar()
    b_path_var = StringVar()

    main_frame = ttk.LabelFrame(w, text="Lista de dispositivos")
    details_frame = ttk.LabelFrame(w, text="Detalles del dispositivo")
    main_frame.grid()
    details_frame.grid()

    def seleccionar_directorio():
        ruta = filedialog.askdirectory()
        if ruta:
            b_path_var.set(ruta)
            ttk.Entry(details_frame, textvariable=b_path_var, state='readonly', width=50).grid(row=8, column=1)

    # ------- datos principales -------
    ttk.Label(main_frame, text="Nombre").grid(row=0, column=0, padx=5)
    ttk.Entry(main_frame, textvariable=nombre_var).grid(row=0, column=1, padx=5)
    ttk.Label(main_frame, text="IP").grid(row=1, column=0, padx=5)
    ttk.Entry(main_frame, textvariable=ip_var).grid(row=1, column=1, padx=5)
    ttk.Label(main_frame, text="Tipo").grid(row=0, column=2, padx=5)
    ttk.Combobox(main_frame, textvariable=tipo_var, values=["router", "switch", "pc"]).grid(row=0, column=3, padx=5)
    # ------- detalles -------
    ttk.Label(details_frame, text="Usuario").grid(row=0, column=0, pady=5, sticky="w")
    ttk.Entry(details_frame, textvariable=usuario_var).grid(row=0, column=1, pady=5, sticky="ew")
    ttk.Label(details_frame, text="Contraseña").grid(row=1, column=0, pady=5, sticky="w")
    ttk.Entry(details_frame, textvariable=contrasena_var, show="*").grid(row=1, column=1, pady=5, sticky="ew")
    ttk.Label(details_frame, text="Puerto").grid(row=2, column=0, pady=5, sticky="w")
    ttk.Entry(details_frame, textvariable=puerto_var).grid(row=2, column=1, pady=5, sticky="ew")
    ttk.Label(details_frame, text="Configuración de Backup").grid(row=3, column=0, columnspan=2, pady=(10,5), sticky="w")
    ttk.Label(details_frame, text="Periodo").grid(row=4, column=0, pady=2, sticky="w")
    ttk.Combobox(details_frame, textvariable=b_periodo_var, values=["Diario", "Semanal", "Mensual"]).grid(row=4, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Hora").grid(row=5, column=0, pady=2, sticky="w")
    ttk.Entry(details_frame, textvariable=b_hora_var).grid(row=5, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Día").grid(row=6, column=0, pady=2, sticky="w")
    ttk.Spinbox(details_frame, from_=1, to=28, textvariable=b_dia_var).grid(row=6, column=0, pady=2, sticky="w")
    ttk.Combobox(details_frame, textvariable=b_dia_var, values=["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]).grid(row=6, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Mes").grid(row=7, column=0, pady=2, sticky="w")
    ttk.Spinbox(details_frame, from_=1, to=12, textvariable=b_mes_var).grid(row=7, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Ruta Backup").grid(row=8, column=0, pady=2, sticky="w")
    ttk.Button(details_frame, text="Elegir directorio", command=seleccionar_directorio).grid(row=8, column=0)
    ttk.Entry(details_frame, textvariable=b_path_var, state='readonly', width=50).grid(row=8, column=1)
    
    def enviar_y_cerrar():
        print(b_periodo_var.get())
        match (b_periodo_var.get()):
            case "Diario":
                b_periodo_int = 1
            case "Semanal":
                b_periodo_int = 2
            case "Mensual":
                b_periodo_int = 3
            case _:
                exit("No deberia pasar esto nunca")

        dispositivo = Dispositivo(nombre_var.get(), ip_var.get(), tipo_var.get(), usuario_var.get(), contrasena_var.get(), puerto_var.get(), b_periodo_int, b_hora_var.get(), b_dia_var.get(), b_mes_var.get(), b_path_var.get())
        try:
            response = c_api(dispositivo.to_dict())
            if response.status_code == 200 or response.status_code == 201:
                print("Dispositivo agregado")
            else:
                print(f"Error agregando dispositivo: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error de conexión: {e}")

        cargar_dispositivos()
        w.destroy()

    # crear la clase en base a lo ingresado
    ttk.Button(w, text="Agregar", command=enviar_y_cerrar).grid()
    return

def eliminar_dispositivo():
    global rootwin
    w = Toplevel(rootwin)
    return

def realizar_backup():
    global rootwin
    w = Toplevel(rootwin)
    return

root = Tk()
root.title("Software de Backup")
root.geometry("380x500")
asignar_rootwin(root)


# estilos para los widgets
s = ttk.Style()
style = ttk.Style()
# ver colores dsp
style.configure("TFrame")

opciones_frame = ttk.Frame(root)
dispositivos_frame = ttk.LabelFrame(root, text="Lista de dispositivos")
detalles_frame = ttk.LabelFrame(root, text="Detalles del dispositivo")
detalles_frame_info = ttk.Frame(root)

opciones_frame.grid(row=0)
dispositivos_frame.grid(row=1)
detalles_frame.grid(row=2)
detalles_frame_info.grid(row=2, column=1)

# botones
nuevobtn = ttk.Button(opciones_frame, text="Nuevo", command=nuevo_dispositivo)
editarbtn = ttk.Button(opciones_frame, text="Editar", command=editar_dispositivo)
eliminarbtn = ttk.Button(opciones_frame, text="Eliminar", command=eliminar_dispositivo)
backupbtn = ttk.Button(opciones_frame, text="Realizar Backup", command=realizar_backup)

# labels descriptivas
ttk.Label(dispositivos_frame, text="Nombre").grid(row=0, column=0, padx=5)
ttk.Label(dispositivos_frame, text="IP").grid(row=0, column=1, padx=5)
ttk.Label(dispositivos_frame, text="Tipo").grid(row=0, column=2, padx=5)


ttk.Label(detalles_frame, text="Usuario: ").grid(row=0, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Contraseña: ").grid(row=1, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Puerto: ").grid(row=2, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Periodo: ").grid(row=3, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Mes: ").grid(row=4, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Dia: ").grid(row=5, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Ruta: ").grid(row=6, column=0, pady=5, sticky="w")

nuevobtn.grid(column=0, row=0)
editarbtn.grid(column=1, row=0)
eliminarbtn.grid(column=2, row=0)
backupbtn.grid(column=3, row=0)

def seleccionar_dispositivo(i):
    global dispositivos
    dispositivo = dispositivos[i]

    for widget in detalles_frame.winfo_children():
        widget.destroy()

    periodo = ""
    match (dispositivo['b_periodo']):
        case 1:
            periodo = "Diario"
        case 2:
            periodo = "Semanal"
        case 3:
            periodo = "Mensual"
        case _:
            exit("No deberia pasar esto nunca")

    ttk.Label(detalles_frame, text="Usuario: " + dispositivo['usuario']).grid(row=0, column=0, pady=5, sticky="w")
    ttk.Label(detalles_frame, text="Contraseña: " + dispositivo['contrasena']).grid(row=1, column=0, pady=5, sticky="w")
    ttk.Label(detalles_frame, text="Puerto: " + str(dispositivo['puerto'])).grid(row=2, column=0, pady=5, sticky="w")
    ttk.Label(detalles_frame, text="Periodo: " + periodo).grid(row=3, column=0, pady=5, sticky="w")
    ttk.Label(detalles_frame, text="Mes: " + str(dispositivo['b_mes'])).grid(row=4, column=0, pady=5, sticky="w")
    ttk.Label(detalles_frame, text="Dia: " + dispositivo['b_dia']).grid(row=5, column=0, pady=5, sticky="w")
    ttk.Label(detalles_frame, text="Ruta: " + dispositivo['b_path']).grid(row=6, column=0, pady=5, sticky="w")
    return

def cargar_dispositivos():
    global dispositivos

    dispositivos = r_api()

    for i, dispositivo in enumerate(dispositivos):
        i += 1
        ttk.Label(dispositivos_frame, text=dispositivo['nombre']).grid(row=i, column=0)
        ttk.Label(dispositivos_frame, text=dispositivo['ip']).grid(row=i, column=1)
        ttk.Label(dispositivos_frame, text=dispositivo['tipo']).grid(row=i, column=2)
        ttk.Button(dispositivos_frame, text="+", command=lambda idx=i-1: seleccionar_dispositivo(idx - 1)).grid(row=i, column=4)

cargar_dispositivos()

root.mainloop()

# Ejemlpo de post
#disp = Dispositivo("Router1", "192.168.0.1", "router", "admin", "1234", 22)
#response = requests.post("http://127.0.0.1:8000/dispositivos/", json=disp.to_dict())

