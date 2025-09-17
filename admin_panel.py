from tkinter import Tk, Label, Button, Frame, messagebox
from tkinter import ttk

class AdminPanel:
    def __init__(self):
        self.ventana = Tk()
        self.ventana.title("Panel de Administración")
        self.ventana.geometry("900x600")
        self.ventana.resizable(False, False)
        self.ventana.config(bg="#006172")

        # --- Layout con 2 frames: izquierda (botones) y derecha (tabla) ---
        self.frame_izquierda = Frame(self.ventana, bg="#004d57", width=250)
        self.frame_izquierda.pack(side="left", fill="y")

        self.frame_derecha = Frame(self.ventana, bg="white")
        self.frame_derecha.pack(side="right", fill="both", expand=True)

        # --- Panel izquierdo con botones ---
        Label(self.frame_izquierda, text="Panel de Administración", font=("Arial", 18, "bold"),
              bg="#004d57", fg="white").pack(pady=20)

        Button(self.frame_izquierda, text="Agregar Inspector", font=("Arial", 14), width=20,
               command=self.agregar_inspector).pack(pady=5)

        Button(self.frame_izquierda, text="Agregar Usuario", font=("Arial", 14), width=20,
               command=self.agregar_usuario).pack(pady=5)

        Button(self.frame_izquierda, text="Agregar Multa", font=("Arial", 14), width=20,
               command=self.agregar_multa).pack(pady=5)

        Button(self.frame_izquierda, text="Quitar Multa", font=("Arial", 14), width=20,
               command=self.quitar_multa).pack(pady=5)

        Button(self.frame_izquierda, text="Eliminar ", font=("Arial", 14), width=20,
               command=self.eliminar_inspector).pack(pady=5)
        
        # --- Panel derecho con Treeview (usuarios) ---
        Label(self.frame_derecha, text="Usuarios del Sistema", font=("Arial", 18, "bold"),
              bg="white", fg="black").pack(pady=10)

        self.tree = ttk.Treeview(self.frame_derecha, columns=("Usuario", "Contraseña","Tipo"), show="headings", height=20)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Definir encabezados
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Contraseña", text="Contraseña")
        self.tree.heading("Tipo", text="Tipo")

        # Definir ancho de columnas
        self.tree.column("Usuario", width=200, anchor="center")
        self.tree.column("Contraseña", width=200, anchor="center")
        self.tree.column("Tipo", width=200, anchor="center")

        # Cargar usuarios desde archivo
        self.cargar_usuarios()

        self.ventana.mainloop()

    # --- Métodos de ejemplo ---
    def agregar_inspector(self):
        messagebox.showinfo("Agregar Inspector", "Función para agregar inspector")

    def agregar_usuario(self):
        messagebox.showinfo("Agregar Usuario", "Función para agregar usuario")

    def agregar_multa(self):
        messagebox.showinfo("Agregar Multa", "Función para agregar multa")

    def quitar_multa(self):
        messagebox.showinfo("Quitar Multa", "Función para quitar multa")

    def eliminar_inspector(self):
        messagebox.showinfo("Eliminar Inspector", "Función para eliminar inspector")

    def eliminar_usuario(self):
        messagebox.showinfo("Eliminar Usuario", "Función para eliminar usuario")

    # --- Mostrar usuarios desde el archivo ---
    def cargar_usuarios(self):
        try:
            with open("usuarios.txt", "r") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    usuario, contrasena = linea.split(":", 1)
                    self.tree.insert("", "end", values=(usuario, contrasena))
        except FileNotFoundError:
            messagebox.showwarning("Archivo no encontrado", "No existe usuarios.txt")
