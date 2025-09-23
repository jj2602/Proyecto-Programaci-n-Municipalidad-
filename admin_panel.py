from tkinter import Tk, Label, Button, Frame, Entry, messagebox, Toplevel
from tkinter import ttk
from registro import Registro
from ticket import agregar_multa, mostrar_multas


class AdminPanel:
    def __init__(self, usuario_actual):
        self.archivo_usuarios = "usuarios.txt"
        self.usuario_actual = usuario_actual

        self.ventana = Tk()
        self.ventana.title("Panel de Administración")
        self.ventana.geometry("900x600")
        self.ventana.resizable(False, False)
        self.ventana.config(bg="#0a4077")

        # --- Layout con 2 frames ---
        self.frame_izquierda = Frame(self.ventana, bg="#0a4077", width=200)
        self.frame_izquierda.pack(side="left", fill="y")

        self.frame_derecha = Frame(self.ventana, bg="white")
        self.frame_derecha.pack(side="right", fill="both", expand=True)

        # --- Panel izquierdo con botones ---
        Label(self.frame_izquierda, text="Panel de Administración", font=("Arial", 18, "bold"),
              bg="#0a4077", fg="white").pack(pady=20)

        Button(self.frame_izquierda, text="Agregar", font=("Arial", 14), width=20,
               command=self.agregar_inspector).pack(pady=5)

        Button(self.frame_izquierda, text="Agregar Multa", font=("Arial", 14), width=20,
               command=self.agregar_multa).pack(pady=5)

        Button(self.frame_izquierda, text="Quitar Multa", font=("Arial", 14), width=20,
               command=self.quitar_multa).pack(pady=5)

        Button(self.frame_izquierda, text="Eliminar", font=("Arial", 14), width=20,
               command=self.eliminar_usuario).pack(pady=5)

        Button(self.frame_izquierda, text="Recargar", font=("Arial", 14), width=20,
               command=self.recargar).pack(pady=20)

        # --- Panel derecho con Treeview ---
        Label(self.frame_derecha, text="Usuarios del Sistema", font=("Arial", 18, "bold"),
              bg="white", fg="black").pack(pady=10)

        cont_tabla = Frame(self.frame_derecha, bg="white")
        cont_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(
            cont_tabla,
            columns=("Usuario", "Contraseña", "Documento", "Tipo"),
            show="headings",
            height=20
        )
        self.tree.pack(side="left", fill="both", expand=True)

        # Scroll vertical
        vsb = ttk.Scrollbar(cont_tabla, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # Encabezados
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Contraseña", text="Contraseña")
        self.tree.heading("Documento", text="Documento")
        self.tree.heading("Tipo", text="Tipo")

        # Columnas
        self.tree.column("Usuario", width=150, anchor="center")
        self.tree.column("Contraseña", width=150, anchor="center")
        self.tree.column("Documento", width=150, anchor="center")
        self.tree.column("Tipo", width=120, anchor="center")

        # Cargar datos
        self.cargar_usuarios()

        self.ventana.mainloop()

    # ---------------- MÉTODOS ----------------
    def recargar(self):
        self.tree.delete(*self.tree.get_children())
        self.cargar_usuarios()

    def agregar_inspector(self):
        Registro(self.archivo_usuarios, solo_usuario_comun=False)

    def agregar_multa(self):
        agregar_multa(self.ventana, self.usuario_actual)

    def quitar_multa(self):
        # Ventana para pedir patente
        top = Toplevel(self.ventana)
        top.title("Buscar Multas")
        top.geometry("300x150")
        top.resizable(False,False)
        top.config(bg="#e6f1fd")

        Label(top, text="Ingrese Patente:", bg="#e6f1fd").pack(pady=10)
        entry_patente = Entry(top, width=20)
        entry_patente.pack(pady=5)

        def abrir_multas():
            patente = entry_patente.get().strip().upper()
            if not patente:
                messagebox.showwarning("Error", "Debe ingresar una patente")
                return
            mostrar_multas(self.ventana, patente)
            top.destroy()

        Button(top, text="Buscar", command=abrir_multas).pack(pady=10)

    def eliminar_usuario(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Eliminar Usuario", "Debe seleccionar un usuario.")
            return

        usuario = self.tree.item(seleccionado[0], "values")[0]

        confirm = messagebox.askyesno("Confirmar", f"¿Seguro que desea eliminar al usuario '{usuario}'?")
        if not confirm:
            return

        try:
            with open(self.archivo_usuarios, "r") as f:
                lineas = f.readlines()
            with open(self.archivo_usuarios, "w") as f:
                for linea in lineas:
                    if not linea.startswith(usuario + ":"):
                        f.write(linea)
        except FileNotFoundError:
            messagebox.showwarning("Archivo no encontrado", "No existe usuarios.txt")
            return

        self.recargar()
        messagebox.showinfo("Éxito", f"Usuario '{usuario}' eliminado correctamente.")

    def cargar_usuarios(self):
        try:
            with open(self.archivo_usuarios, "r") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = linea.split(":", 3)
                    if len(partes) != 4:
                        continue
                    usuario, contrasena, documento, tipo = partes
                    self.tree.insert("", "end", values=(usuario, contrasena, documento, tipo))
        except FileNotFoundError:
            messagebox.showwarning("Archivo no encontrado", "No existe usuarios.txt")
