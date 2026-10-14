import subprocess
import os
import shutil
import zipfile
from datetime import datetime

def limpiar_archivos_temporales():
    archivos_eliminados = 0
    errores = 0
    carpetas = [
        os.environ.get('TEMP'),
        r'C:\Windows\Temp',
        r'C:\Windows\Prefetch'
    ]
    
    for carpeta in carpetas:
        if carpeta and os.path.exists(carpeta):
            for item in os.listdir(carpeta):
                ruta_item = os.path.join(carpeta, item)
                try:
                    if os.path.isfile(ruta_item) or os.path.islink(ruta_item):
                        os.unlink(ruta_item)
                        archivos_eliminados += 1
                    elif os.path.isdir(ruta_item):
                        shutil.rmtree(ruta_item)
                        archivos_eliminados += 1
                except Exception:
                    errores += 1

    return True, f"Limpieza finalizada. Archivos/Carpetas eliminados: {archivos_eliminados} (Omitidos: {errores})"

def reiniciar_cola_impresion():
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin:
            return False, "Acceso denegado: Debes ejecutar la aplicación como Administrador."

        cmd = 'powershell -Command "Stop-Service -Name Spooler -Force; Remove-Item -Path $env:SystemRoot\\System32\\spool\\PRINTERS\\* -Force -Recurse -ErrorAction SilentlyContinue; Start-Service -Name Spooler"'
        resultado = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if resultado.returncode == 0:
            return True, "Cola de impresión limpiada y servicio Spooler reiniciado con éxito."
        else:
            return False, f"Error al reiniciar cola de impresión: {resultado.stderr.strip()}"
    except Exception as e:
        return False, str(e)

def abrir_liberador_disco():
    try:
        subprocess.Popen("cleanmgr.exe", shell=True)
        return True, "Liberador de espacio en disco abierto."
    except Exception as e:
        return False, str(e)

def verificar_seguridad_sistema():
    try:
        # BitLocker C: status
        cmd_bit = 'powershell -Command "(Get-BitLockerVolume -MountPoint C: -ErrorAction SilentlyContinue).ProtectionStatus"'
        res_bit = subprocess.run(cmd_bit, capture_output=True, text=True, shell=True)
        bit_status = res_bit.stdout.strip()
        
        if bit_status == "1":
            bitlock_str = "Activado (Protegido)"
        elif bit_status == "0":
            bitlock_str = "Desactivado (Sin protección)"
        else:
            bitlock_str = "No disponible / No soportado"

        # Firewall status por perfiles
        cmd_fw = 'powershell -Command "(Get-NetFirewallProfile).Enabled"'
        res_fw = subprocess.run(cmd_fw, capture_output=True, text=True, shell=True)
        fw_lines = [l.strip() for l in res_fw.stdout.strip().split('\n') if l.strip()]
        fw_str = " / ".join(fw_lines) if fw_lines else "Desconocido"

        return f"• BitLocker (Unidad C:): {bitlock_str}\n• Firewall de Windows (Dom/Priv/Pub): {fw_str}"
    except Exception as e:
        return f"Error al verificar seguridad: {str(e)}"

def abrir_herramienta_nativa(nombre):
    herramientas = {
        "Administrador de Dispositivos": "devmgmt.msc",
        "Administración de Discos": "diskmgmt.msc",
        "Visor de Eventos": "eventvwr.msc",
        "Editor de Registro": "regedit",
        "Conexiones de Red": "ncpa.cpl"
    }
    cmd = herramientas.get(nombre)
    if cmd:
        try:
            subprocess.Popen(cmd, shell=True)
            return True, f"Abriendo {nombre}..."
        except Exception as e:
            return False, str(e)
    return False, "Herramienta no encontrada."
def respaldo_rapido_perfil(ruta_destino_personalizada=None):
    try:
        user_profile = os.environ.get('USERPROFILE')
        if not user_profile:
            return False, "No se pudo detectar el perfil del usuario."

        escritorio = os.path.join(user_profile, "Desktop")
        documentos = os.path.join(user_profile, "Documents")

        carpeta_respaldos = ruta_destino_personalizada or "respaldos_perfil"
        if not os.path.exists(carpeta_respaldos):
            os.makedirs(carpeta_respaldos)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_zip = os.path.join(carpeta_respaldos, f"Respaldo_Perfil_{timestamp}.zip")

        archivos_agregados = 0
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for carpeta_origen in [escritorio, documentos]:
                if os.path.exists(carpeta_origen):
                    for foldername, subfolders, filenames in os.walk(carpeta_origen):
                        for filename in filenames:
                            ruta_completa = os.path.join(foldername, filename)
                            # Evitar respaldar archivos temporales o muy pesados si es necesario
                            try:
                                relpath = os.path.relpath(ruta_completa, user_profile)
                                zipf.write(ruta_completa, relpath)
                                archivos_agregados += 1
                            except Exception:
                                pass

        return True, f"Respaldo creado con éxito ({archivos_agregados} archivos).\nGuardado en: {nombre_zip}"
    except Exception as e:
        return False, f"Error al generar respaldo: {str(e)}"