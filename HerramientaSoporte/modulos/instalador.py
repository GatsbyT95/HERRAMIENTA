import subprocess
import os
import requests
import tempfile

def instalar_programa(ruta_instalador, argumentos):
    try:
        # Si es un archivo .msi, asegurarnos de usar msiexec con los parámetros correctos
        if ruta_instalador.lower().endswith('.msi'):
            # Añadir ALLUSERS=1 para evitar errores de permisos de usuario
            if "ALLUSERS" not in argumentos:
                argumentos += " ALLUSERS=1"
            comando = f'msiexec /i "{ruta_instalador}" {argumentos}'
        else:
            comando = f'"{ruta_instalador}" {argumentos}'

        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            return True, "¡Instalación completada con éxito!"
        else:
            return False, f"Error (Código {resultado.returncode}): {resultado.stderr.strip() or 'Revisar argumentos o conflictos con versiones previas.'}"
    except Exception as e:
        return False, f"Excepción crítica: {str(e)}"

def descargar_e_instalar(url, argumentos, nombre_app):
    try:
        temp_dir = tempfile.gettempdir()
        nombre_archivo = url.split("/")[-1].split("?")[0]
        if not nombre_archivo.endswith(('.exe', '.msi')):
            nombre_archivo = "installer.exe"
        
        ruta_destino = os.path.join(temp_dir, nombre_archivo)
        
        print(f"Descargando {nombre_app}...")
        respuesta = requests.get(url, stream=True, timeout=60)
        
        if respuesta.status_code == 200:
            with open(ruta_destino, 'wb') as f:
                for chunk in respuesta.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            return False, f"Error al descargar (HTTP {respuesta.status_code})"
        
        return instalar_programa(ruta_destino, argumentos)
    except Exception as e:
        return False, f"Error en descarga/instalación: {str(e)}"