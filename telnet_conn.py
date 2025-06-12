import telnetlib
import socket

def probar_conexion_telnet(host, puerto, timeout=5):
    try:
        with telnetlib.Telnet(host, puerto, timeout) as tn:
            return True
    except (socket.timeout, ConnectionRefusedError, EOFError, OSError):
        return False

