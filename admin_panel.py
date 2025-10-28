import json
from tkinter import Tk, Label, Button, Frame, Entry, messagebox, Toplevel, StringVar, OptionMenu
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

        # --- Panel izquierdo con botones dinámicos ---
        Label(self.frame_izquierda, text="Panel de Administración", font=("Arial", 18, "bold"),
              bg="#0a4077", fg="white").pack(pady=20)

        self.crear_menu_dinamico()

        # --- Panel derecho con tabla de usuarios ---
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

        vsb = ttk.Scrollbar(cont_tabla, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Contraseña", text="Contraseña")
        self.tree.heading("Documento", text="Documento")
        self.tree.heading("Tipo", text="Tipo")

        self.tree.column("Usuario", width=150, anchor="center")
        self.tree.column("Contraseña", width=150, anchor="center")
        self.tree.column("Documento", width=150, anchor="center")
        self.tree.column("Tipo", width=120, anchor="center")

        self.cargar_usuarios()
        self.auto_recargar()
        self.ventana.mainloop()

    # ---------------- MÉTODO NUEVO: Crear menú dinámico usando IDs ----------------
    def crear_menu_dinamico(self):
        """Lee el archivo menu.json y crea los botones usando IDs."""

        # 🔹 1. Mapeo de ID -> función
        comandos = {
            "1": self.agregar_inspector,
            "2": self.agregar_multa,
            "3": self.quitar_multa,
            "4": self.eliminar_usuario,
            "5": self.editar_usuario
        }

        # 🔹 2. Leer archivo JSON
        try:
            with open("menu.json", "r", encoding="utf-8") as f:
                opciones_menu = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error de Configuración", "No se encontró el archivo 'menu.json'.")
            return
        except json.JSONDecodeError:
            messagebox.showerror("Error de Configuración", "El archivo 'menu.json' tiene un formato inválido.")
            return

        # 🔹 3. Crear los botones dinámicamente
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
            ).pack(pady=5)

    def funcion_placeholder(self):
        """Función para los botones nuevos que no tienen una acción asignada."""
        messagebox.showinfo("Función no implementada", "Este botón no tiene una acción asignada aún.")

    # ---------------- MÉTODOS EXISTENTES ----------------
    def auto_recargar(self):
        self.recargar()
        self.ventana.after(5000, self.auto_recargar)

    def recargar(self):
        self.tree.delete(*self.tree.get_children())
        self.cargar_usuarios()

    def agregar_inspector(self):
        Registro(self.archivo_usuarios, solo_usuario_comun=False)

    def agregar_multa(self):
        agregar_multa(self.ventana, self.usuario_actual)

    def quitar_multa(self):
        top = Toplevel(self.ventana)
        top.title("Buscar Multas")
        top.geometry("300x150")
        top.resizable(False, False)
        top.config(bg="#001947")

        Label(top, text="Ingrese Patente:", bg="#e6f1fd").pack(pady=10)
        entry_patente = Entry(top, width=20)
        entry_patente.pack(pady=5)

        def abrir_multas():
            patente = entry_patente.get().strip().upper()
            if not patente:
                messagebox.showwarning("Error", "Debe ingresar una patente")
                return
            mostrar_multas(self.ventana, patente, modo_usuario=False)
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

    def editar_usuario(self):
        if hasattr(self, "editar_ventana") and self.editar_ventana.winfo_exists():
            messagebox.showwarning("Editar Usuario", "Ya hay una ventana de edición abierta.")
            return

        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Editar Usuario", "Debe seleccionar un usuario.")
            return

        usuario, contrasena, documento, tipo = self.tree.item(seleccionado[0], "values")

        self.editar_ventana = Toplevel(self.ventana)
        self.editar_ventana.title("Editar Usuario")
        self.editar_ventana.geometry("400x520")
        self.editar_ventana.resizable(False, False)
        self.editar_ventana.configure(bg="#e6f1fd")

        Label(self.editar_ventana, text="Usuario:", font=("Arial", 14), bg="#e6f1fd").pack(pady=(20, 5))
        entry_usuario = Entry(self.editar_ventana, font=("Arial", 14))
        entry_usuario.pack(pady=(0, 20))
        entry_usuario.insert(0, usuario)
        entry_usuario.config(state="disabled")

        Label(self.editar_ventana, text="Documento (DNI):", font=("Arial", 14), bg="#e6f1fd").pack(pady=(0, 5))
        entry_documento = Entry(self.editar_ventana, font=("Arial", 14))
        entry_documento.pack(pady=(0, 20))
        entry_documento.insert(0, documento)

        Label(self.editar_ventana, text="Contraseña:", font=("Arial", 14), bg="#e6f1fd").pack(pady=(0, 5))
        entry_contrasena = Entry(self.editar_ventana, font=("Arial", 14))
        entry_contrasena.pack(pady=(0, 20))
        entry_contrasena.insert(0, contrasena)

        Label(self.editar_ventana, text="Tipo de Usuario:", font=("Arial", 14), bg="#e6f1fd").pack(pady=(0, 5))
        tipo_var = StringVar(self.editar_ventana)
        tipo_var.set(tipo)
        opciones = {"1": "Administrador", "2": "Inspector", "3": "Usuario"}
        OptionMenu(self.editar_ventana, tipo_var, *opciones.keys()).pack(pady=(0, 20))

        def guardar_cambios():
            nuevo_documento = entry_documento.get()
            nueva_contrasena = entry_contrasena.get()
            nuevo_tipo = tipo_var.get()

            if not nuevo_documento or not nueva_contrasena:
                messagebox.showwarning("Editar Usuario", "Debe completar todos los campos.")
                return

            if len(nuevo_documento) != 8 or not nuevo_documento.isdigit():
                messagebox.showwarning("Editar Usuario", "Documento inválido.")
                return

            try:
                with open(self.archivo_usuarios, "r") as f:
                    lineas = f.readlines()
                with open(self.archivo_usuarios, "w") as f:
                    for linea in lineas:
                        if linea.startswith(usuario + ":"):
                            f.write(f"{usuario}:{nueva_contrasena}:{nuevo_documento}:{nuevo_tipo}\n")
                        else:
                            f.write(linea)
            except FileNotFoundError:
                messagebox.showwarning("Archivo no encontrado", "No existe usuarios.txt")
                return

            self.recargar()
            messagebox.showinfo("Editar Usuario", "Usuario actualizado correctamente.")
            self.editar_ventana.destroy()

        Button(self.editar_ventana, text="Guardar Cambios", font=("Arial", 14, "bold"),
               bg="#ffffff", fg="black", width=15, command=guardar_cambios).pack(pady=10)

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
