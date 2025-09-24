from tkinter import Tk, Label, Button, Frame, messagebox, Toplevel, Entry
from tkinter import ttk
import os
from ticket import mostrar_multas  # <-- Importar función de multas

class UserPanel:
    def __init__(self, usuario_actual):
        self.usuario_actual = usuario_actual
        self.archivo_vehiculos = "vehiculos.txt"

        self.ventana = Tk()
        self.ventana.title(f"Panel de Usuario - {usuario_actual}")
        self.ventana.geometry("900x600")
        self.ventana.resizable(False, False)
        self.ventana.config(bg="#0a4077")

        # --- Layout con 2 frames ---
        self.frame_izquierda = Frame(self.ventana, bg="#0a4077", width=200)
        self.frame_izquierda.pack(side="left", fill="y")

        self.frame_derecha = Frame(self.ventana, bg="white")
        self.frame_derecha.pack(side="right", fill="both", expand=True)

        # --- Panel izquierdo con botones ---
        Label(self.frame_izquierda, text="Panel de Usuario", font=("Arial", 18, "bold"),
              bg="#0a4077", fg="white").pack(pady=20)

        Button(self.frame_izquierda, text="Cargar Vehículo", font=("Arial", 14), width=20,
               command=self.cargar_vehiculo).pack(pady=5)

        Button(self.frame_izquierda, text="Consultar Multas", font=("Arial", 14), width=20,
               command=self.consultar_multas).pack(pady=5)

        Button(self.frame_izquierda, text="Pagar Multas", font=("Arial", 14), width=20,
               command=self.pagar_multas).pack(pady=5)

        Button(self.frame_izquierda, text="Hacer Apelación", font=("Arial", 14), width=20,
               command=self.hacer_apelacion).pack(pady=5)

        # --- Panel derecho con Treeview ---
        Label(self.frame_derecha, text="Mis Vehículos", font=("Arial", 18, "bold"),
              bg="white", fg="black").pack(pady=10)

        cont_tabla = Frame(self.frame_derecha, bg="white")
        cont_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(
            cont_tabla,
            columns=("Patente", "Marca", "Modelo", "Año"),
            show="headings",
            height=20
        )
        self.tree.pack(side="left", fill="both", expand=True)

        # Scroll vertical
        vsb = ttk.Scrollbar(cont_tabla, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # Encabezados
        self.tree.heading("Patente", text="Patente")
        self.tree.heading("Marca", text="Marca")
        self.tree.heading("Modelo", text="Modelo")
        self.tree.heading("Año", text="Año")

        # Columnas
        self.tree.column("Patente", width=120, anchor="center")
        self.tree.column("Marca", width=150, anchor="center")
        self.tree.column("Modelo", width=150, anchor="center")
        self.tree.column("Año", width=100, anchor="center")

        # Cargar vehículos del usuario actual
        self.cargar_vehiculos()

        self.ventana.mainloop()

    # ---------------- MÉTODOS ----------------
    def cargar_vehiculo(self):
        """Formulario emergente para agregar un vehículo"""
        top = Toplevel(self.ventana)
        top.title("Cargar Vehículo")
        top.geometry("300x300")
        top.resizable(False, False)

        Label(top, text="Patente:").pack(pady=5)
        entry_patente = Entry(top)
        entry_patente.pack(pady=5)

        Label(top, text="Marca:").pack(pady=5)
        entry_marca = Entry(top)
        entry_marca.pack(pady=5)

        Label(top, text="Modelo:").pack(pady=5)
        entry_modelo = Entry(top)
        entry_modelo.pack(pady=5)

        Label(top, text="Año:").pack(pady=5)
        entry_anio = Entry(top)
        entry_anio.pack(pady=5)

        def guardar():
            patente = entry_patente.get().strip().upper()
            marca = entry_marca.get().strip()
            modelo = entry_modelo.get().strip()
            anio = entry_anio.get().strip()

            if not (patente and marca and modelo and anio):
                messagebox.showwarning("Error", "Complete todos los campos")
                return

            # Guardar en archivo
            with open(self.archivo_vehiculos, "a", encoding="utf-8") as f:
                f.write(f"{self.usuario_actual}:{patente}:{marca}:{modelo}:{anio}\n")

            top.destroy()
            self.recargar()

        Button(top, text="Guardar", command=guardar).pack(pady=10)

    def consultar_multas(self):
        """Abrir ventana de multas de la patente seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un vehículo para consultar sus multas")
            return

        patente = self.tree.item(seleccion, "values")[0]  # Primer valor = patente
        mostrar_multas(self.ventana, patente, modo_usuario=True)


    def pagar_multas(self):
        messagebox.showinfo("Pagar Multas", "Acá va la lógica para pagar multas")

    def hacer_apelacion(self):
        messagebox.showinfo("Hacer Apelación", "Acá va la lógica para hacer una apelación")

    def cargar_vehiculos(self):
        """Carga los vehículos del usuario actual"""
        self.tree.delete(*self.tree.get_children())
        if not os.path.exists(self.archivo_vehiculos):
            return

        with open(self.archivo_vehiculos, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                partes = linea.split(":")
                if len(partes) == 5:
                    usuario, patente, marca, modelo, anio = partes
                    if usuario == self.usuario_actual:  # Filtrar por usuario actual
                        self.tree.insert("", "end", values=(patente, marca, modelo, anio))

    def recargar(self):
        """Recarga los datos de la grilla"""
        self.cargar_vehiculos()
