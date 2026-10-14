import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import os
import subprocess
from modulos import inventario, red, instalador, mantenimiento

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class HerramientaSoporteApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Toolkit Pro de Soporte TI - Enterprise")
        self.geometry("860x610")
        self.resizable(False, False)

        self.tabview = ctk.CTkTabview(self, width=820, height=560)
        self.tabview.pack(padx=20, pady=15)

        self.tab_inventario = self.tabview.add("📊 Inventario")
        self.tab_red = self.tabview.add("🌐 Red")
        self.tab_instalador = self.tabview.add("📦 Instalador")
        self.tab_mantenimiento = self.tabview.add("🧹 Mantenimiento")
        self.tab_seguridad = self.tabview.add("🛡️ Seguridad")
        self.tab_checklist = self.tabview.add("✅ Checklist")
        self.tab_respaldo = self.tabview.add("💾 Respaldo")
        self.tab_historial = self.tabview.add("📂 Historial")

        self.setup_tab_inventario()
        self.setup_tab_red()
        self.setup_tab_instalador()
        self.setup_tab_mantenimiento()
        self.setup_tab_seguridad()
        self.setup_tab_checklist()
        self.setup_tab_respaldo()
        self.setup_tab_historial()

    # ==================== PESTAÑA 1: INVENTARIO ====================
    def setup_tab_inventario(self):
        ctk.CTkLabel(self.tab_inventario, text="Registro de Sucursal y Soporte", font=("Arial", 16, "bold")).pack(pady=5)

        frame_datos = ctk.CTkFrame(self.tab_inventario, fg_color="transparent")
        frame_datos.pack(pady=5)

        ctk.CTkLabel(frame_datos, text="Sucursal:").grid(row=0, column=0, padx=5, sticky="w")
        self.entry_sucursal = ctk.CTkEntry(frame_datos, width=170, placeholder_text="Ej: CDMX Centro")
        self.entry_sucursal.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(frame_datos, text="ID de Soporte:").grid(row=0, column=2, padx=5, sticky="w")
        self.entry_soporte = ctk.CTkEntry(frame_datos, width=140, placeholder_text="Ej: SOP-1024")
        self.entry_soporte.grid(row=0, column=3, padx=5)

        self.textbox_inv = ctk.CTkTextbox(self.tab_inventario, width=760, height=220, font=("Consolas", 11))
        self.textbox_inv.pack(pady=5)

        frame_botones = ctk.CTkFrame(self.tab_inventario, fg_color="transparent")
        frame_botones.pack(pady=8)

        ctk.CTkButton(frame_botones, text="Cargar Información", command=self.cargar_inventario).grid(row=0, column=0, padx=4)
        ctk.CTkButton(frame_botones, text="Excel", fg_color="green", hover_color="darkgreen", width=90, command=self.exportar_reporte_excel).grid(row=0, column=1, padx=4)
        ctk.CTkButton(frame_botones, text="JSON", fg_color="darkblue", hover_color="navy", width=90, command=self.exportar_reporte_json).grid(row=0, column=2, padx=4)
        ctk.CTkButton(frame_botones, text="Reporte HTML", fg_color="purple", hover_color="darkmagenta", width=120, command=self.exportar_reporte_html).grid(row=0, column=3, padx=4)

        self.datos_actuales = {}

    def cargar_inventario(self):
        sucursal = self.entry_sucursal.get().strip()
        id_soporte = self.entry_soporte.get().strip()

        if not sucursal or not id_soporte:
            messagebox.showwarning("Campos Obligatorios", "Debes rellenar 'Sucursal' e 'ID de Soporte'.")
            return

        self.textbox_inv.delete("0.0", "end")
        datos_pc = inventario.obtener_datos_pc()
        
        # Incluir también el estado del checklist si ya fue marcado
        checklist_data = self.obtener_estado_checklist()

        self.datos_actuales = {
            "Nombre de Sucursal": sucursal,
            "ID de Soporte": id_soporte,
            **datos_pc,
            **checklist_data
        }

        texto_formateado = "=== REPORTE DE SOPORTE E INVENTARIO ===\n\n"
        for clave, valor in self.datos_actuales.items():
            texto_formateado += f"• {clave}: {valor}\n"
            
        self.textbox_inv.insert("0.0", texto_formateado)
        self.guardar_historial_automatico()

    def guardar_historial_automatico(self):
        try:
            carpeta_logs = "historial_soporte"
            if not os.path.exists(carpeta_logs):
                os.makedirs(carpeta_logs)
            hostname = self.datos_actuales.get("Hostname", "PC")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = os.path.join(carpeta_logs, f"reporte_{hostname}_{timestamp}.json")
            inventario.exportar_json(self.datos_actuales, nombre_archivo)
            self.actualizar_lista_historial()
        except Exception as e:
            print(f"Error autoguardado: {str(e)}")

    def exportar_reporte_excel(self):
        if not self.datos_actuales:
            messagebox.showwarning("Advertencia", "Primero carga la información.")
            return
        archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if archivo:
            exito, mensaje = inventario.exportar_excel(self.datos_actuales, archivo)
            messagebox.showinfo("Resultado", mensaje)

    def exportar_reporte_json(self):
        if not self.datos_actuales:
            messagebox.showwarning("Advertencia", "Primero carga la información.")
            return
        archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if archivo:
            exito, mensaje = inventario.exportar_json(self.datos_actuales, archivo)
            messagebox.showinfo("Resultado", mensaje)

    def exportar_reporte_html(self):
        if not self.datos_actuales:
            messagebox.showwarning("Advertencia", "Primero carga la información.")
            return
        archivo = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
        if archivo:
            exito, mensaje = inventario.exportar_html(self.datos_actuales, archivo)
            messagebox.showinfo("Resultado", mensaje)

    # ==================== PESTAÑA 2: RED ====================
    def setup_tab_red(self):
        ctk.CTkLabel(self.tab_red, text="Diagnóstico y Escaneo de Red", font=("Arial", 16, "bold")).pack(pady=5)
        self.lbl_ip_local = ctk.CTkLabel(self.tab_red, text=f"IP Local: {red.obtener_ip_local()}", font=("Arial", 12, "italic"))
        self.lbl_ip_local.pack(pady=2)

        frame_pings = ctk.CTkFrame(self.tab_red, fg_color="transparent")
        frame_pings.pack(pady=5)
        ctk.CTkButton(frame_pings, text="Google (8.8.8.8)", width=120, fg_color="gray50", command=lambda: self.ejecutar_ping("8.8.8.8")).pack(side="left", padx=4)
        ctk.CTkButton(frame_pings, text="Cloudflare (1.1.1.1)", width=130, fg_color="gray50", command=lambda: self.ejecutar_ping("1.1.1.1")).pack(side="left", padx=4)
        ctk.CTkButton(frame_pings, text="Gateway Local", width=110, fg_color="gray50", command=self.ping_gateway).pack(side="left", padx=4)

        frame_manual = ctk.CTkFrame(self.tab_red, fg_color="transparent")
        frame_manual.pack(pady=5)
        self.entry_host = ctk.CTkEntry(frame_manual, width=280, placeholder_text="IP o Dominio")
        self.entry_host.pack(side="left", padx=5)
        ctk.CTkButton(frame_manual, text="Probar Ping", width=100, command=lambda: self.ejecutar_ping(self.entry_host.get().strip())).pack(side="left", padx=5)

        self.lbl_res_ping = ctk.CTkLabel(self.tab_red, text="", font=("Arial", 13, "bold"))
        self.lbl_res_ping.pack(pady=5)

        ctk.CTkButton(self.tab_red, text="🔍 Escanear Dispositivos en Red Local (ARP)", fg_color="darkblue", command=self.escanear_arp).pack(pady=5)
        self.textbox_arp = ctk.CTkTextbox(self.tab_red, width=760, height=130, font=("Consolas", 10))
        self.textbox_arp.pack(pady=2)

    def ejecutar_ping(self, host):
        if not host: return
        self.lbl_res_ping.configure(text=f"Haciendo ping a {host}...", text_color="orange")
        self.update()
        if red.ejecutar_ping(host):
            self.lbl_res_ping.configure(text=f"✔ Conexión exitosa con '{host}'", text_color="green")
        else:
            self.lbl_res_ping.configure(text=f"✖ Sin respuesta de '{host}'", text_color="red")

    def ping_gateway(self):
        try:
            cmd = "powershell -Command \"(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Select-Object -ExpandProperty NextHop)\""
            res = subprocess.run(cmd, capture_output=True, text=True, shell=True).stdout.strip()
            if res: self.ejecutar_ping(res)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def escanear_arp(self):
        self.textbox_arp.delete("0.0", "end")
        self.textbox_arp.insert("0.0", "Escaneando red...\n")
        self.update()
        res = red.escanear_red_local()
        self.textbox_arp.delete("0.0", "end")
        self.textbox_arp.insert("0.0", f"=== DISPOSITIVOS EN RED LOCAL ===\n\n{res}")
      
        # ==================== PESTAÑA 3: INSTALADOR ====================
    def setup_tab_instalador(self):
        ctk.CTkLabel(self.tab_instalador, text="Despliegue y Herramientas Locales", font=("Arial", 16, "bold")).pack(pady=10)
        
        urls = {
            "chrome": ("https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise64.msi", "/qn /norestart", "Google Chrome"),
            "7zip": ("https://www.7-zip.org/a/7z2301-x64.exe", "/S", "7-Zip"),
            "rustdesk": ("https://github.com/rustdesk/rustdesk/releases/latest/download/rustdesk-x86_64.exe", "--silent-install", "RustDesk"),
            "anydesk": ("https://download.anydesk.com/AnyDesk.exe", "--install --silent --accept-licenses", "AnyDesk"),
            "teamviewer": ("https://download.teamviewer.com/download/TeamViewer_Setup.exe", '/S /v"/qn /norestart"', "TeamViewer")
        }

        # Fila 1: Descargas de internet
        f1 = ctk.CTkFrame(self.tab_instalador, fg_color="transparent")
        f1.pack(pady=5)
        ctk.CTkButton(f1, text="Google Chrome", width=140, fg_color="darkblue", command=lambda: self.instalar_app(*urls["chrome"])).grid(row=0, column=0, padx=5)
        ctk.CTkButton(f1, text="7-Zip", width=140, fg_color="darkblue", command=lambda: self.instalar_app(*urls["7zip"])).grid(row=0, column=1, padx=5)
        ctk.CTkButton(f1, text="RustDesk", width=140, fg_color="darkblue", command=lambda: self.instalar_app(*urls["rustdesk"])).grid(row=0, column=2, padx=5)

        # Fila 2: Más descargas
        f2 = ctk.CTkFrame(self.tab_instalador, fg_color="transparent")
        f2.pack(pady=5)
        ctk.CTkButton(f2, text="AnyDesk", width=140, fg_color="darkblue", command=lambda: self.instalar_app(*urls["anydesk"])).grid(row=0, column=0, padx=5)
        ctk.CTkButton(f2, text="TeamViewer", width=140, fg_color="darkblue", command=lambda: self.instalar_app(*urls["teamviewer"])).grid(row=0, column=1, padx=5)

        # --- SECCIÓN DE HERRAMIENTA LOCAL (GdeL.exe) ---
        f_local = ctk.CTkFrame(self.tab_instalador, fg_color="transparent")
        f_local.pack(pady=(15, 5))
        
        ctk.CTkLabel(f_local, text="Herramienta Local de la Carpeta:", font=("Arial", 12, "bold")).pack(pady=2)
        
        btn_gdel = ctk.CTkButton(f_local, text="🚀 Ejecutar GdeL", width=200, fg_color="darkgreen", hover_color="green", command=self.ejecutar_gdel)
        btn_gdel.pack(pady=5)

        self.lbl_instala = ctk.CTkLabel(self.tab_instalador, text="", font=("Arial", 13, "bold"))
        self.lbl_instala.pack(pady=10)

    def ejecutar_gdel(self):
        import os
        import subprocess
        
        # Ruta del archivo GdeL.exe dentro de la misma carpeta del proyecto
        ruta_gdel = os.path.join(os.getcwd(), "GdeL.exe")
        
        if not os.path.exists(ruta_gdel):
            messagebox.showerror("Error", f"No se encontró el archivo 'GdeL.exe' en la ruta:\n{ruta_gdel}")
            return
            
        try:
            if messagebox.askyesno("Confirmar", "¿Deseas ejecutar GdeL.exe?"):
                subprocess.Popen(f'"{ruta_gdel}"', shell=True)
                self.lbl_instala.configure(text="✔ GdeL ejecutado correctamente.", text_color="green")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar GdeL: {str(e)}")
    # ==================== PESTAÑA 4: MANTENIMIENTO ====================
    def setup_tab_mantenimiento(self):
        ctk.CTkLabel(self.tab_mantenimiento, text="Limpieza y Mantenimiento", font=("Arial", 16, "bold")).pack(pady=10)
        f = ctk.CTkFrame(self.tab_mantenimiento, fg_color="transparent")
        f.pack(pady=10)
        ctk.CTkButton(f, text="🧹 Limpiar %TEMP%", command=lambda: messagebox.showinfo("Limpieza", mantenimiento.limpiar_archivos_temporales()[1])).grid(row=0, column=0, padx=8)
        ctk.CTkButton(f, text="🖨️ Reparar Spooler", command=lambda: messagebox.showinfo("Spooler", mantenimiento.reiniciar_cola_impresion()[1])).grid(row=0, column=1, padx=8)
        ctk.CTkButton(f, text="💾 Liberador de Disco", command=mantenimiento.abrir_liberador_disco).grid(row=0, column=2, padx=8)

        ctk.CTkLabel(self.tab_mantenimiento, text="Servicios Críticos:", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        self.tb_serv = ctk.CTkTextbox(self.tab_mantenimiento, width=760, height=180, font=("Consolas", 11))
        self.tb_serv.pack(pady=5)
        ctk.CTkButton(self.tab_mantenimiento, text="Consultar Servicios", command=self.cargar_servicios).pack(pady=5)

    def cargar_servicios(self):
        self.tb_serv.delete("0.0", "end")
        estados = mantenimiento.obtener_estado_servicios()
        t = "=== SERVICIOS ===\n\n"
        for s, st in estados.items(): t += f"• {s}: [{st.upper()}]\n"
        self.tb_serv.insert("0.0", t)

    # ==================== PESTAÑA 5: SEGURIDAD ====================
    def setup_tab_seguridad(self):
        ctk.CTkLabel(self.tab_seguridad, text="Seguridad y Herramientas Nativas", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkButton(self.tab_seguridad, text="🛡️ Verificar BitLocker y Firewall", fg_color="darkgreen", command=self.ver_seguridad).pack(pady=5)
        self.tb_sec = ctk.CTkTextbox(self.tab_seguridad, width=760, height=90, font=("Consolas", 11))
        self.tb_sec.pack(pady=5)

        ctk.CTkLabel(self.tab_seguridad, text="Lanzador de Consolas:", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        f1 = ctk.CTkFrame(self.tab_seguridad, fg_color="transparent")
        f1.pack(pady=5)
        ctk.CTkButton(f1, text="Admin. Dispositivos", width=190, command=lambda: mantenimiento.abrir_herramienta_nativa("Administrador de Dispositivos")).grid(row=0, column=0, padx=5)
        ctk.CTkButton(f1, text="Admin. Discos", width=190, command=lambda: mantenimiento.abrir_herramienta_nativa("Administración de Discos")).grid(row=0, column=1, padx=5)
        ctk.CTkButton(f1, text="Visor Eventos", width=190, command=lambda: mantenimiento.abrir_herramienta_nativa("Visor de Eventos")).grid(row=0, column=2, padx=5)

        f2 = ctk.CTkFrame(self.tab_seguridad, fg_color="transparent")
        f2.pack(pady=5)
        ctk.CTkButton(f2, text="Regedit", width=190, command=lambda: mantenimiento.abrir_herramienta_nativa("Editor de Registro")).grid(row=0, column=0, padx=5)
        ctk.CTkButton(f2, text="Conexiones Red", width=190, command=lambda: mantenimiento.abrir_herramienta_nativa("Conexiones de Red")).grid(row=0, column=1, padx=5)

    def ver_seguridad(self):
        self.tb_sec.delete("0.0", "end")
        self.tb_sec.insert("0.0", f"=== SEGURIDAD ===\n\n{mantenimiento.verificar_seguridad_sistema()}")

    # ==================== PESTAÑA 6: CHECKLIST ====================
    def setup_tab_checklist(self):
        ctk.CTkLabel(self.tab_checklist, text="Checklist de Cierre de Servicio", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkLabel(self.tab_checklist, text="Valida las siguientes tareas antes de entregar el equipo al cliente:", font=("Arial", 12, "italic")).pack(pady=5)

        self.chk_vars = {}
        tareas = [
            "Antivirus actualizado y analizado sin amenazas",
            "Sin errores críticos en Administrador de Dispositivos",
            "Pruebas de navegación web y red exitosas",
            "Equipo limpio físicamente y optimizado",
            "Software de soporte remoto instalado (AnyDesk / RustDesk)",
            "Conformidad y entrega aprobada por el usuario"
        ]

        frame_checks = ctk.CTkFrame(self.tab_checklist, fg_color="transparent")
        frame_checks.pack(pady=10)

        for i, tarea in enumerate(tareas):
            var = ctk.BooleanVar(value=False)
            self.chk_vars[tarea] = var
            chk = ctk.CTkCheckBox(frame_checks, text=tarea, variable=var, font=("Arial", 12))
            chk.grid(row=i, column=0, sticky="w", pady=6, padx=20)

    def obtener_estado_checklist(self):
        estado = {}
        for tarea, var in self.chk_vars.items():
            estado[f"Check: {tarea}"] = "Completado [✔]" if var.get() else "Pendiente [ ]"
        return estado

    # ==================== PESTAÑA 7: RESPALDO ====================
    def setup_tab_respaldo(self):
        ctk.CTkLabel(self.tab_respaldo, text="Respaldo Rápido de Perfil de Usuario", font=("Arial", 16, "bold")).pack(pady=15)
        ctk.CTkLabel(self.tab_respaldo, text="Comprime el Escritorio y Documentos del usuario actual en un archivo ZIP de respaldo.", font=("Arial", 12)).pack(pady=5)

        btn_respaldo = ctk.CTkButton(self.tab_respaldo, text="📦 Iniciar Respaldo Rápido (Escritorio + Documentos)", fg_color="darkorange", hover_color="peru", width=320, command=self.ejecutar_respaldo)
        btn_respaldo.pack(pady=20)

        self.textbox_respaldo = ctk.CTkTextbox(self.tab_respaldo, width=760, height=180, font=("Consolas", 11))
        self.textbox_respaldo.pack(pady=5)

    def ejecutar_respaldo(self):
        if not messagebox.askyesno("Confirmar Respaldo", "¿Deseas comprimir el Escritorio y Documentos del usuario en un archivo ZIP?"):
            return
        self.textbox_respaldo.delete("0.0", "end")
        self.textbox_respaldo.insert("0.0", "Generando respaldo de perfil, por favor espera...\n")
        self.update()

        exito, msg = mantenimiento.respaldo_rapido_perfil()
        self.textbox_respaldo.delete("0.0", "end")
        self.textbox_respaldo.insert("0.0", msg)
        if exito:
            messagebox.showinfo("Respaldo Exitoso", "El respaldo se ha completado correctamente.")
        else:
            messagebox.showerror("Error", msg)

    # ==================== PESTAÑA 8: HISTORIAL ====================
    def setup_tab_historial(self):
        ctk.CTkLabel(self.tab_historial, text="Historial de Reportes Generados", font=("Arial", 16, "bold")).pack(pady=10)
        self.textbox_historial = ctk.CTkTextbox(self.tab_historial, width=760, height=270, font=("Consolas", 11))
        self.textbox_historial.pack(pady=5)

        f = ctk.CTkFrame(self.tab_historial, fg_color="transparent")
        f.pack(pady=10)
        ctk.CTkButton(f, text="Refrescar Historial", command=self.actualizar_lista_historial).grid(row=0, column=0, padx=5)
        ctk.CTkButton(f, text="Abrir Carpeta de Registros", command=lambda: os.startfile(os.path.abspath("historial_soporte"))).grid(row=0, column=1, padx=5)

        self.actualizar_lista_historial()

    def actualizar_lista_historial(self):
        self.textbox_historial.delete("0.0", "end")
        path = "historial_soporte"
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith('.json')]
            if files:
                t = f"=== REPORTES ({len(files)}) ===\n\n"
                for fi in reversed(files): t += f"📄 {fi}\n"
                self.textbox_historial.insert("0.0", t)
            else: self.textbox_historial.insert("0.0", "No hay reportes aún.")
        else: self.textbox_historial.insert("0.0", "Carpeta vacía.")

if __name__ == "__main__":
    app = HerramientaSoporteApp()
    app.mainloop()
        # ==================== PESTAÑA 8: HISTORIAL ====================
    def setup_tab_historial(self):
        ctk.CTkLabel(self.tab_historial, text="Historial de Reportes Generados", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.textbox_historial = ctk.CTkTextbox(self.tab_historial, width=760, height=230, font=("Consolas", 11))
        self.textbox_historial.pack(pady=5)

        f = ctk.CTkFrame(self.tab_historial, fg_color="transparent")
        f.pack(pady=10)
        
        ctk.CTkButton(f, text="Refrescar Historial", command=self.actualizar_lista_historial).grid(row=0, column=0, padx=5)
        ctk.CTkButton(f, text="Abrir Archivo Reciente en Excel/JSON", fg_color="green", hover_color="darkgreen", command=self.abrir_reporte_reciente).grid(row=0, column=1, padx=5)
        ctk.CTkButton(f, text="Abrir Carpeta", command=lambda: os.startfile(os.path.abspath("historial_soporte"))).grid(row=0, column=2, padx=5)

        self.actualizar_lista_historial()

    def actualizar_lista_historial(self):
        self.textbox_historial.delete("0.0", "end")
        path = "historial_soporte"
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith(('.json', '.xlsx', '.html'))]
            if files:
                t = f"=== REPORTES GUARDADOS ({len(files)}) ===\n\n"
                for fi in sorted(files, reverse=True): 
                    t += f"📄 {fi}\n"
                self.textbox_historial.insert("0.0", t)
            else: 
                self.textbox_historial.insert("0.0", "No hay reportes autoguardados aún.")
        else: 
            self.textbox_historial.insert("0.0", "Carpeta de historial vacía.")

    def abrir_reporte_reciente(self):
        path = "historial_soporte"
        if not os.path.exists(path):
            messagebox.showwarning("Aviso", "La carpeta de historial aún no existe.")
            return
            
        files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.json', '.xlsx', '.html'))]
        if not files:
            messagebox.showwarning("Aviso", "No hay reportes disponibles para abrir.")
            return
            
        # Obtener el archivo más reciente
        archivo_reciente = max(files, key=os.path.getmtime)
        try:
            os.startfile(archivo_reciente)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")