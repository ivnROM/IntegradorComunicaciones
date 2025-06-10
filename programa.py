import requests
from tkinter import *
from tkinter import ttk
API_URL = "http://127.0.0.1:8000/dispositivos/"

global rootwin

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
def c_api():
    requests.post(url=API_URL, json=)
    return 

def r_api():
    return 

def u_api():
    return 

def d_api():
    return 

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
    b_periodo_var = IntVar() # 1->(Diario) 2->(Semanal) 3->(Mensual)
    b_hora_var = StringVar()
    b_dia_var = StringVar()
    b_mes_var = IntVar()
    b_path_var = StringVar()

    main_frame = ttk.LabelFrame(w, text="Lista de dispositivos")
    details_frame = ttk.LabelFrame(w, text="Detalles del dispositivo")
    main_frame.pack()
    details_frame.pack()
    
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
    ttk.Combobox(details_frame, textvariable=b_dia_var, values=["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]).grid(row=6, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Mes").grid(row=7, column=0, pady=2, sticky="w")
    ttk.Spinbox(details_frame, from_=1, to=12, textvariable=b_mes_var).grid(row=7, column=1, pady=2, sticky="ew")
    ttk.Label(details_frame, text="Ruta Backup").grid(row=8, column=0, pady=2, sticky="w")
    ttk.Entry(details_frame, textvariable=b_path_var).grid(row=8, column=1, pady=2, sticky="ew")

    # crear la clase en base a lo ingresado
    nuevobtn = ttk.Button(w, text="Agregar", command=c_api)
    return
    
def editar_dispositivo():
    global rootwin
    w = Toplevel(rootwin)
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

opciones_frame.pack()
dispositivos_frame.pack()
detalles_frame.pack()

# botones
nuevobtn = ttk.Button(opciones_frame, text="Nuevo", command=nuevo_dispositivo)
editarbtn = ttk.Button(opciones_frame, text="Editar", command=editar_dispositivo)
eliminarbtn = ttk.Button(opciones_frame, text="Eliminar", command=eliminar_dispositivo)
backupbtn = ttk.Button(opciones_frame, text="Realizar Backup", command=realizar_backup)

# labels descriptivas
ttk.Label(dispositivos_frame, text="Nombre").grid(row=0, column=0, padx=5)
ttk.Label(dispositivos_frame, text="IP").grid(row=0, column=1, padx=5)
ttk.Label(dispositivos_frame, text="Tipo").grid(row=0, column=2, padx=5)


ttk.Label(detalles_frame, text="Nombre").grid(row=0, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="IP").grid(row=1, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Tipo").grid(row=2, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Contraseña").grid(row=3, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Contraseña").grid(row=4, column=0, pady=5, sticky="w")
ttk.Label(detalles_frame, text="Configuración de Backup").grid(row=5, column=0, pady=5, sticky="w")

nuevobtn.pack(side='left')
editarbtn.pack(side='left')
eliminarbtn.pack(side='left')
backupbtn.pack(side='left')

root.mainloop()


# Ejemlpo de post
#disp = Dispositivo("Router1", "192.168.0.1", "router", "admin", "1234", 22)
#response = requests.post("http://127.0.0.1:8000/dispositivos/", json=disp.to_dict())

