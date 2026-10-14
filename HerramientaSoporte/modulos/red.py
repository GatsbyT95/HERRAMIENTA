import subprocess
import platform
import socket

def ejecutar_ping(host):
    try:
        parametro = "-n" if platform.system().lower() == "windows" else "-c"
        comando = ["ping", parametro, "1", host]
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=3)
        return resultado.returncode == 0
    except Exception:
        return False

def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def escanear_red_local():
    try:
        # Ejecuta arp -a para listar dispositivos conectados en la caché ARP local
        cmd = "arp -a"
        resultado = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return resultado.stdout.strip()
    except Exception as e:
        return f"Error al escanear dispositivos: {str(e)}"