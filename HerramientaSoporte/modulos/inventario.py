import platform
import psutil
import subprocess
import json
import csv
from datetime import datetime

def obtener_datos_pc():
    try:
        memoria = psutil.virtual_memory()
        
        try:
            disco = psutil.disk_usage('C:')
            disco_total = f"{round(disco.total / (1024**3), 2)} GB"
            disco_libre = f"{round(disco.free / (1024**3), 2)} GB"
        except Exception:
            disco_total = "No disponible"
            disco_libre = "No disponible"

        serial_number = "No disponible"
        motherboard_info = "No disponible"
        licencia_estado = "No disponible"

        # COMANDO ÚNICO CONSOLIDADO: Obtiene BIOS, Placa Base, Producto y Licencia de golpe en formato JSON
        try:
            ps_script = """
            $bios = Get-CimInstance Win32_BIOS | Select-Object -ExpandProperty SerialNumber
            $prod = Get-CimInstance Win32_ComputerSystemProduct | Select-Object -ExpandProperty IdentifyingNumber
            $mb = Get-CimInstance Win32_BaseBoard | ForEach-Object {$_.Manufacturer + ' ' + $_.Product}
            $lic = (Get-CimInstance SoftwareLicensingProduct | Where-Object {$_.LicenseStatus -eq 1}).Name
            
            [PSCustomObject]@{
                SerialBios = $bios
                SerialProd = $prod
                Motherboard = $mb
                Licencia = $lic
            } | ConvertTo-Json -Compress
            """
            
            cmd = f'powershell -Command "{ps_script}"'
            resultado = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if resultado.returncode == 0 and resultado.stdout.strip():
                data_ps = json.loads(resultado.stdout.strip())
                
                # Procesar Serial
                serial = data_ps.get("SerialBios")
                if not serial or serial.lower() in ["", "none", "to be filled by o.e.m.", "default string"]:
                    serial = data_ps.get("SerialProd")
                if serial and serial.lower() not in ["", "none", "to be filled by o.e.m.", "default string"]:
                    serial_number = serial.strip()
                
                # Procesar Placa Base
                mb = data_ps.get("Motherboard")
                if mb:
                    motherboard_info = mb.strip()
                
                # Procesar Licencia
                lic = data_ps.get("Licencia")
                if lic:
                    if isinstance(lic, list):
                        lic = lic[0]
                    licencia_estado = f"Activado ({lic.split('Edition')[0].strip() if 'Edition' in lic else 'Windows'})"
                else:
                    licencia_estado = "No activado / Pendiente"
        except Exception:
            pass

        so_nombre = f"{platform.system()} {platform.release()} (Build {platform.version()})"

        info = {
            "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Hostname": platform.node(),
            "Sistema Operativo": so_nombre,
            "Licencia Windows": licencia_estado,
            "Número de Serie": serial_number,
            "Tarjeta Madre": motherboard_info,
            "Procesador": platform.processor(),
            "RAM Total": f"{round(memoria.total / (1024**3), 2)} GB",
            "RAM Disponible": f"{round(memoria.available / (1024**3), 2)} GB",
            "Disco C: Total": disco_total,
            "Disco C: Libre": disco_libre
        }
        return info
    except Exception as e:
        return {"Error": str(e)}

def exportar_excel(datos, ruta_archivo):
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inventario TI"

        ws.append(["Propiedad", "Valor"])
        for clave, valor in datos.items():
            ws.append([clave, valor])

        wb.save(ruta_archivo)
        return True, "Reporte Excel (.xlsx) exportado con éxito."
    except Exception as e:
        return False, f"Error al generar Excel: {str(e)}"

def exportar_json(datos, ruta_archivo):
    try:
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        return True, "Reporte JSON exportado con éxito."
    except Exception as e:
        return False, f"Error al generar JSON: {str(e)}"

def exportar_html(datos, ruta_archivo):
    try:
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte de Soporte - {datos.get('Hostname', 'PC')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f6f9; color: #333; padding: 20px; }}
        .container {{ max-width: 800px; background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin: auto; }}
        h2 {{ color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 10px 12px; border: 1px solid #ddd; text-align: left; }}
        th {{ background-color: #0056b3; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Reporte Técnico de Soporte TI</h2>
        <table>
            <tr><th>Propiedad</th><th>Valor</th></tr>
"""
        for k, v in datos.items():
            html_content += f"            <tr><td><b>{k}</b></td><td>{v}</td></tr>\n"
        
        html_content += """        </table>
    </div>
</body>
</html>"""

        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return True, "Reporte HTML generado con éxito."
    except Exception as e:
        return False, f"Error al generar HTML: {str(e)}"