# inspector_panel.py
from tkinter import Tk, Frame, Label, Button, messagebox, Toplevel, OptionMenu, StringVar, Entry
from PIL import Image, ImageTk
from tkinter import ttk
import os
from decimal import Decimal, InvalidOperation
import json
import datetime
from ticket import agregar_multa, ARCHIVO_MULTAS
APELACIONES_ARCHIVO = "apelaciones.txt"


class InspectorPanel:
    def __init__(self, usuario_actual: str):
        self.usuario_actual = usuario_actual

        # Ventana
        self.ventana = Tk()
        self.ventana.title(f"Panel de Inspector - {usuario_actual}")
        self.ventana.geometry("1200x600")
        self.ventana.resizable(False, False)
        self.ventana.config(bg="#0a4077")

        # Layout principal
        self.frame_izquierda = Frame(self.ventana, bg="#0a4077", width=250)
        self.frame_izquierda.pack(side="left", fill="y")

        self.frame_derecha = Frame(self.ventana, bg="white")
        self.frame_derecha.pack(side="right", fill="both", expand=True)

        # Lado izquierdo (acciones)
        Label(self.frame_izquierda, text="Panel de Inspector", font=("Arial", 18, "bold"),
              bg="#0a4077", fg="white").pack(pady=20)

        self.crear_menu_dinamico()

        # --- Logo en la parte inferior izquierda ---
        try:
            self.logo_img = Image.open("muni.png").resize((180, 63)) # Redimensionamos para que quepa
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            logo_label = Label(self.frame_izquierda, image=self.logo_photo, bg="#0a4077")
            # Usamos side="bottom" para anclarlo abajo
            logo_label.pack(side="bottom", pady=20)
        except FileNotFoundError:
            print("Advertencia: No se encontró la imagen 'muni.png'.")

        # Lado derecho (tabla / contenido)
        Label(self.frame_derecha, text="Apelaciones", font=("Arial", 18, "bold"),
              bg="white", fg="black").pack(pady=10)

        cont_tabla = Frame(self.frame_derecha, bg="white")
        cont_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(
            cont_tabla,
            columns=("patente", "obs", "motivo", "importe", "estado"),
            show="headings",
            height=22,
            displaycolumns=("patente", "obs", "motivo", "importe", "estado")
        )
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(cont_tabla, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # Encabezados
        self.tree.heading("patente", text="Patente")
        self.tree.heading("obs", text="Observación")
        self.tree.heading("motivo", text="Motivo Apelación")
        self.tree.heading("importe", text="Importe ($)")
        self.tree.heading("estado", text="Estado")

        # Columnas
        self.tree.column("patente", width=80, anchor="center")
        self.tree.column("obs", width=200, anchor="w")
        self.tree.column("motivo", width=250, anchor="w")
        self.tree.column("importe", width=80, anchor="center")
        self.tree.column("estado", width=100, anchor="center")

        # Botonera inferior (Aceptar / Rechazar)
        self.botonera = Frame(self.frame_derecha, bg="white")
        self.botonera.pack(fill="x", padx=20, pady=(0, 12))

        Button(self.botonera, text="ACEPTAR", font=("Arial", 13, "bold"),
               bg="#2e7d32", fg="white", width=12,
               command=self.aceptar_apelacion).pack(side="left", padx=(0, 8), pady=2)

        Button(self.botonera, text="RECHAZAR", font=("Arial", 13, "bold"),
               bg="#c62828", fg="white", width=12,
               command=self.rechazar_apelacion).pack(side="left", padx=8, pady=2)
        
        Button(self.botonera, text="PAGO VOLUNTARIO", font=("Arial", 13, "bold"),
               bg="#ff8f00", fg="white", width=18,
               command=self.ofrecer_pago_voluntario).pack(side="left", padx=8, pady=2)

        self.mostrar_apelaciones()
        self.auto_recargar()
        self.ventana.mainloop()

    def crear_menu_dinamico(self):
        """Lee el archivo menu_inspector.json y crea los botones usando IDs."""

        # 1. Mapeo de ID -> función
        comandos = {
            "1": self.btn_agregar_multa,
            "2": self.mostrar_apelaciones,
        }

        # 2. Leer archivo JSON
        try:
            with open("menu_inspector.json", "r", encoding="utf-8") as f:
                opciones_menu = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error de Configuración", "No se encontró el archivo 'menu_inspector.json'.")
            return
        except json.JSONDecodeError:
            messagebox.showerror("Error de Configuración", "El archivo 'menu_inspector.json' tiene un formato inválido.")
            return

        # 3. Crear los botones dinámicamente
        for opcion in opciones_menu:
            id_boton = str(opcion.get("id", ""))
            texto_boton = opcion.get("texto", "Sin nombre")

            if not id_boton:
                continue  # Ignorar si no hay ID

            comando = comandos.get(id_boton, self.funcion_placeholder)

            Button(
                self.frame_izquierda,
                text=texto_boton,
                font=("Arial", 14),
                width=20,
                command=comando
            ).pack(pady=6)

    # ---------- Acciones ----------
    def btn_agregar_multa(self):
        # Usa exactamente el flujo de ticket.py
        agregar_multa(self.ventana, self.usuario_actual)

    def auto_recargar(self):
        """Recarga automáticamente el Treeview cada 3 segundos"""
        self.mostrar_apelaciones()
        self.ventana.after(5000, self.auto_recargar)

    def funcion_placeholder(self):
        """Función para los botones nuevos que no tienen una acción asignada."""
        messagebox.showinfo("Función no implementada", "Este botón no tiene una acción asignada aún.")

    def mostrar_apelaciones(self):
        """
        Carga apelaciones desde apelaciones.txt con formato:
        patente|observacion|importe|foto|motivo|estado
        """
        self.tree.delete(*self.tree.get_children())

        if not os.path.exists(APELACIONES_ARCHIVO):
            return

        with open(APELACIONES_ARCHIVO, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                partes = linea.split("|")
                if len(partes) != 6:
                    continue
                patente, obs, importe, foto, motivo, estado = partes
                self.tree.insert("", "end", values=(patente, obs, motivo, importe, estado), iid=linea)

    def aceptar_apelacion(self):
        """
        Marca la apelación como ACEPTADA y elimina la multa correspondiente
        de multas.txt (si existe un match exacto).
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una apelación.")
            return

        linea_original = sel[0]
        patente, obs, importe_str, foto, motivo, estado = linea_original.split("|")

        # --- VALIDACIÓN: No cambiar una decisión ya tomada ---
        if estado != "PENDIENTE":
            messagebox.showwarning("Acción no permitida", f"Esta apelación ya fue procesada (Estado: {estado}). No se puede cambiar la decisión.")
            return

        # 1. Actualizar estado en apelaciones.txt
        self._actualizar_estado_apelacion(linea_original, "ACEPTADA")

        # 2. Eliminar multa de multas.txt
        nuevas_multas = []
        multa_eliminada = False
        if os.path.exists(ARCHIVO_MULTAS):
            with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
                for linea_multa in f:
                    # Comparación exacta para no borrar la multa equivocada
                    if linea_multa.strip() != f"{patente}|{obs}|{importe_str}|{foto}":
                        nuevas_multas.append(linea_multa)
                    else:
                        multa_eliminada = True
            
            if multa_eliminada:
                with open(ARCHIVO_MULTAS, "w", encoding="utf-8") as f:
                    f.writelines(nuevas_multas)
                messagebox.showinfo("Éxito", "Apelación ACEPTADA. La multa ha sido eliminada.")
            else:
                messagebox.showwarning("Atención", "La apelación fue aceptada, pero no se encontró la multa original para eliminar (posiblemente ya fue pagada o modificada).")
        
        self.mostrar_apelaciones()

    def rechazar_apelacion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una apelación.")
            return
        
        linea_original = sel[0]
        patente, obs, importe_str, foto, motivo, estado = linea_original.split("|")

        # --- VALIDACIÓN: No cambiar una decisión ya tomada ---
        if estado != "PENDIENTE":
            messagebox.showwarning("Acción no permitida", f"Esta apelación ya fue procesada (Estado: {estado}). No se puede cambiar la decisión.")
            return

        self._actualizar_estado_apelacion(linea_original, "RECHAZADA")
        messagebox.showinfo("Éxito", "La apelación ha sido RECHAZADA.")
        self.mostrar_apelaciones()

    def ofrecer_pago_voluntario(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una apelación para ofrecer un descuento.")
            return

        linea_original_apelacion = sel[0]
        patente, obs, importe_str, foto, motivo, estado = linea_original_apelacion.split("|")

        # --- VALIDACIÓN: No cambiar una decisión ya tomada ---
        if estado != "PENDIENTE":
            messagebox.showwarning("Acción no permitida", f"Esta apelación ya fue procesada (Estado: {estado}). No se puede cambiar la decisión.")
            return

        # Ventana para seleccionar descuento
        desc_win = Toplevel(self.ventana)
        desc_win.title("Ofrecer Pago Voluntario")
        desc_win.geometry("400x280")

        Label(desc_win, text=f"Importe actual: ${importe_str}", font=("Arial", 12)).pack(pady=10)
        Label(desc_win, text="Seleccione un descuento:", font=("Arial", 12)).pack(pady=5)

        Label(desc_win, text="Fecha Límite (DD/MM/AAAA):", font=("Arial", 12)).pack(pady=(10, 0))
        entry_fecha = Entry(desc_win, font=("Arial", 12), width=15)
        entry_fecha.pack(pady=5)

        descuento_var = StringVar(desc_win)
        descuento_var.set("10") # Valor por defecto
        opciones = ["10", "20", "30", "40"]
        OptionMenu(desc_win, descuento_var, *opciones).pack(pady=5)

        def aplicar_descuento():
            try:
                fecha_limite_str = entry_fecha.get()
                try:
                    # Validar formato de fecha
                    datetime.datetime.strptime(fecha_limite_str, "%d/%m/%Y")
                except ValueError:
                    messagebox.showerror("Error de Formato", "La fecha límite debe estar en formato DD/MM/AAAA.")
                    return


                importe_original = Decimal(importe_str)
                porcentaje_desc = Decimal(descuento_var.get())
                descuento = importe_original * (porcentaje_desc / 100)
                nuevo_importe = importe_original - descuento

                # 1. Actualizar multas.txt con el nuevo importe
                nuevas_multas = []
                multa_actualizada = False
                with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
                    for linea in f:
                        if linea.strip() == f"{patente}|{obs}|{importe_str}|{foto}":
                            # Nuevo formato: patente|obs|importe_desc|foto|fecha_limite|importe_orig
                            linea_descuento = f"{patente}|{obs}|{nuevo_importe:.2f}|{foto}|{fecha_limite_str}|{importe_original:.2f}\n"
                            nuevas_multas.append(linea_descuento)
                            multa_actualizada = True
                        else:
                            nuevas_multas.append(linea)
                
                if multa_actualizada:
                    with open(ARCHIVO_MULTAS, "w", encoding="utf-8") as f:
                        f.writelines(nuevas_multas)
                    
                    # 2. Actualizar estado en apelaciones.txt
                    self._actualizar_estado_apelacion(linea_original_apelacion, f"PAGO VOLUNTARIO ({porcentaje_desc}% hasta {fecha_limite_str})")
                    messagebox.showinfo("Éxito", f"Se aplicó un descuento del {porcentaje_desc}%. Nuevo importe: ${nuevo_importe:.2f}")
                    self.mostrar_apelaciones()
                    desc_win.destroy()
                else:
                    messagebox.showerror("Error", "No se encontró la multa original para aplicar el descuento.")

            except InvalidOperation:
                messagebox.showerror("Error", "El importe original de la multa no es válido.")

        Button(desc_win, text="Aplicar Descuento", command=aplicar_descuento).pack(pady=15)

    def _actualizar_estado_apelacion(self, linea_a_cambiar: str, nuevo_estado: str):
        lineas_actualizadas = []
        with open(APELACIONES_ARCHIVO, "r", encoding="utf-8") as f:
            for linea in f:
                if linea.strip() == linea_a_cambiar:
                    partes = linea.strip().split("|")
                    partes[-1] = nuevo_estado # El último elemento es el estado
                    lineas_actualizadas.append("|".join(partes) + "\n")
                else:
                    lineas_actualizadas.append(linea)
        
        with open(APELACIONES_ARCHIVO, "w", encoding="utf-8") as f:
            f.writelines(lineas_actualizadas)
