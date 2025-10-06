# inspector_panel.py
from tkinter import Tk, Frame, Label, Button, messagebox
from tkinter import ttk
import os

from ticket import agregar_multa, ARCHIVO_MULTAS  # reutiliza el flujo de multas de ticket.py

APELACIONES_ARCHIVO = "apelaciones.txt"


class InspectorPanel:
    def __init__(self, usuario_actual: str):
        self.usuario_actual = usuario_actual

        # Ventana
        self.ventana = Tk()
        self.ventana.title(f"Panel de Inspector - {usuario_actual}")
        self.ventana.geometry("900x600")
        self.ventana.resizable(False, False)
        self.ventana.config(bg="#006172")

        # Layout principal
        self.frame_izquierda = Frame(self.ventana, bg="#004d57", width=250)
        self.frame_izquierda.pack(side="left", fill="y")

        self.frame_derecha = Frame(self.ventana, bg="white")
        self.frame_derecha.pack(side="right", fill="both", expand=True)

        # Lado izquierdo (acciones)
        Label(self.frame_izquierda, text="Panel de Inspector", font=("Arial", 18, "bold"),
              bg="#004d57", fg="white").pack(pady=20)

        Button(self.frame_izquierda, text="Agregar Multa", font=("Arial", 14), width=20,
               command=self.btn_agregar_multa).pack(pady=6)

        Button(self.frame_izquierda, text="Revisar Apelaciones", font=("Arial", 14), width=20,
               command=self.mostrar_apelaciones).pack(pady=6)

        # Lado derecho (tabla / contenido)
        Label(self.frame_derecha, text="Apelaciones", font=("Arial", 18, "bold"),
              bg="white", fg="black").pack(pady=10)

        cont_tabla = Frame(self.frame_derecha, bg="white")
        cont_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(
            cont_tabla,
            columns=("patente", "obs", "importe", "foto", "estado"),
            show="headings",
            height=22,
            displaycolumns=("patente", "obs", "importe", "foto", "estado")
        )
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(cont_tabla, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # Encabezados
        self.tree.heading("patente", text="Patente")
        self.tree.heading("obs", text="Observación")
        self.tree.heading("importe", text="Importe ($)")
        self.tree.heading("foto", text="Foto")
        self.tree.heading("estado", text="Estado")

        # Columnas
        self.tree.column("patente", width=120, anchor="center", stretch=True)
        self.tree.column("obs", width=340, anchor="w", stretch=True)
        self.tree.column("importe", width=120, anchor="center", stretch=True)
        self.tree.column("foto", width=160, anchor="center", stretch=True)
        self.tree.column("estado", width=100, anchor="center", stretch=True)

        # Botonera inferior (Aceptar / Rechazar)
        self.botonera = Frame(self.frame_derecha, bg="white")
        self.botonera.pack(fill="x", padx=20, pady=(0, 12))

        Button(self.botonera, text="ACEPTAR", font=("Arial", 13, "bold"),
               bg="#2e7d32", fg="white", width=12,
               command=self.aceptar_apelacion).pack(side="left", padx=(0, 8), pady=2)

        Button(self.botonera, text="RECHAZAR", font=("Arial", 13, "bold"),
               bg="#c62828", fg="white", width=12,
               command=self.rechazar_apelacion).pack(side="left", padx=8, pady=2)

        self.mostrar_apelaciones()
        self.ventana.mainloop()

        # Recarga automática cada 5 segundos
        self.auto_recargar()

        self.ventana.mainloop()


    # ---------- Acciones ----------
    def btn_agregar_multa(self):
        # Usa exactamente el flujo de ticket.py
        agregar_multa(self.ventana, self.usuario_actual)

    def auto_recargar(self):
        """Recarga automáticamente el Treeview cada 5 segundos"""
        self.recargar()
        self.ventana.after(1000, self.auto_recargar)  

    def mostrar_apelaciones(self):
        """
        Carga apelaciones desde apelaciones.txt con formato:
        patente|observacion|importe|foto|estado
        """
        self.tree.delete(*self.tree.get_children())

        if not os.path.exists(APELACIONES_ARCHIVO):
            # Si no existe todavía, no es error; simplemente no hay apelaciones
            return

        with open(APELACIONES_ARCHIVO, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                partes = linea.split("|")
                if len(partes) != 5:
                    continue
                patente, obs, importe, foto, estado = partes
                self.tree.insert("", "end", values=(patente, obs, importe, foto, estado))

    def aceptar_apelacion(self):
        """
        Marca la apelación como ACEPTADA y elimina la multa correspondiente
        de multas.txt (si existe un match exacto).
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una apelación.")
            return

        item_id = sel[0]
        patente, obs, importe, foto, estado = self.tree.item(item_id, "values")

        # 1) Actualizar apelaciones.txt -> estado = ACEPTADA
        self._ac_
