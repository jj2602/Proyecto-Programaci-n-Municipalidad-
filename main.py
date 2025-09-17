from tkinter import Tk, Label, Button, Entry, Frame, Canvas, messagebox, Toplevel
from PIL import Image, ImageTk
import os

# Importamos el panel de admin desde otro archivo
from admin_panel import AdminPanel

# --- Clase de Login ---
class Login:
    def __init__(self):
        self.ventana = Tk()
        self.ventana.geometry("1000x600")
        self.ventana.title("Login")
        self.ventana.resizable(False, False)

        # Crear canvas para la forma redondeada
        self.canvas = Canvas(self.ventana, width=1000, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Dibujar fondo dividido
        self.canvas.create_rectangle(0, 0, 500, 600, fill="#0667c5", outline="#0667c5")
        self.canvas.create_rectangle(500, 0, 1000, 600, fill="#e6f1fd", outline="#e6f1fd")

        # Logo en la izquierda
        self.logo_img = Image.open("Muni.png").resize((410, 151))
        self.logo_photo = ImageTk.PhotoImage(self.logo_img)
        self.canvas.create_image(250, 300, image=self.logo_photo)

        # Frame de login derecha
        self.login_frame = Frame(self.canvas, bg="#e6f1fd")
        self.login_frame.place(x=600, y=150)

        # Título
        Label(self.login_frame, text="LOGIN", font=("Calisto MT", 36, "bold"), bg="#e6f1fd").pack(pady=(0, 30))

        # Usuario
        Label(self.login_frame, text="Usuario", font=("Arial", 18), bg="#e6f1fd").pack(anchor="w")
        self.entry_usuario = Entry(self.login_frame, font=("Arial", 18), width=25)
        self.entry_usuario.pack(pady=(0, 20))

        # Contraseña
        Label(self.login_frame, text="Contrasena", font=("Arial", 18), bg="#e6f1fd").pack(anchor="w")
        self.entry_contrasena = Entry(self.login_frame, font=("Arial", 18), width=25, show="*")
        self.entry_contrasena.pack(pady=(0, 30))

        # Botón Entrar
        Button(self.login_frame, text="Entrar", font=("Arial", 18, "bold"),
               bg="White", fg="black", width=20, command=self.login).pack()

        # Botón Registrarse
        Button(self.login_frame, text="Registrarse", font=("Arial", 18, "bold"),
               bg="White", fg="black", width=20, command=self.abrir_registro).pack(pady=(15, 0))

        # Crear archivo si no existe
        self.archivo_usuarios = "usuarios.txt"
        if not os.path.exists(self.archivo_usuarios):
            with open(self.archivo_usuarios, "w") as f:
                f.write("admin:admin\n")  # Usuario por defecto

    def login(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()
        if self.validar_usuario(usuario, contrasena):
            messagebox.showinfo("Login", f"¡Bienvenido {usuario}!")
            self.ventana.destroy()  # Cierra ventana de login
            if usuario == "admin" and contrasena == "admin":
                AdminPanel()  # Abre panel de admin (otro archivo)
        else:
            messagebox.showerror("Login", "Usuario o contrasena incorrectos.")

    def validar_usuario(self, usuario, contrasena):
        with open(self.archivo_usuarios, "r") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                u, c = linea.split(":", 1)
                if u == usuario and c == contrasena:
                    return True
        return False

    # --- Nueva ventana de registro ---
    def abrir_registro(self):
        Registro(self.archivo_usuarios)

    def run(self):
        self.ventana.mainloop()


# --- Clase Registro ---
class Registro:
    def __init__(self, archivo_usuarios):
        self.archivo_usuarios = archivo_usuarios
        self.registro_ventana = Toplevel()
        self.registro_ventana.title("Registro de Usuario")
        self.registro_ventana.geometry("400x300")
        self.registro_ventana.resizable(False, False)

        Label(self.registro_ventana, text="Nuevo Usuario:", font=("Arial", 14)).pack(pady=(20, 5))
        self.entry_nuevo_usuario = Entry(self.registro_ventana, font=("Arial", 14))
        self.entry_nuevo_usuario.pack(pady=(0, 20))

        Label(self.registro_ventana, text="Nueva Contrasena:", font=("Arial", 14)).pack(pady=(0, 5))
        self.entry_nueva_contrasena = Entry(self.registro_ventana, font=("Arial", 14), show="*")
        self.entry_nueva_contrasena.pack(pady=(0, 20))
        
        Label(self.registro_ventana, text="Repetir Contrasena:", font=("Arial", 14)).pack(pady=(0, 5))
        self.entry_repetir_contrasena = Entry(self.registro_ventana, font=("Arial", 14), show="*")
        self.entry_repetir_contrasena.pack(pady=(0, 20))

        Button(self.registro_ventana, text="Registrar", font=("Arial", 14, "bold"),
               bg="White", fg="black", width=15, command=self.registrar_usuario).pack()

    def validar_contrasena(self, nueva_contrasena):
        tiene_mayus = any(c.isupper() for c in nueva_contrasena)
        tiene_minus = any(c.islower() for c in nueva_contrasena)
        tiene_especial = any(not c.isalnum() for c in nueva_contrasena)
        longitud_ok = len(nueva_contrasena) >= 10
        return tiene_mayus and tiene_minus and tiene_especial and longitud_ok

    
    def registrar_usuario(self):
        nuevo_usuario = self.entry_nuevo_usuario.get()
        nueva_contrasena = self.entry_nueva_contrasena.get()
        repetir_contrasena = self.entry_repetir_contrasena.get()
        if not nuevo_usuario or not nueva_contrasena or not repetir_contrasena:
            messagebox.showwarning("Registro", "Debe completar todos los campos.")
            return
        if nueva_contrasena != repetir_contrasena:
            messagebox.showwarning("Registro", "Las contrasenas no coinciden.")
            return
        if not self.validar_contrasena(nueva_contrasena):
            messagebox.showwarning("Registro", "La contrasena no cumple con las características.")
            return

        # Validar si ya existe
        with open(self.archivo_usuarios, "r") as f:
            for linea in f:
                u, _ = linea.strip().split(":", 1)
                if u == nuevo_usuario:
                    messagebox.showerror("Registro", "El usuario ya existe.")
                    return

        # Guardar usuario
        with open(self.archivo_usuarios, "a") as f:
            f.write(f"{nuevo_usuario}:{nueva_contrasena}\n")

        messagebox.showinfo("Registro", "Usuario registrado con éxito.")
        self.registro_ventana.destroy()


# --- Ejecutar la aplicación ---
if __name__ == "__main__":
    app = Login()
    app.run()
