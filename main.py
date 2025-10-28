from tkinter import Tk, Label, Button, Entry, Frame, Canvas, messagebox
from PIL import Image, ImageTk
import os
from inspector_panel import InspectorPanel
from admin_panel import AdminPanel  
from registro import Registro      
from Panel_Usuario import UserPanel
from payment_api import start_api_in_thread 

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
        self.canvas.create_rectangle(0, 0, 500, 600, fill="#0667c5", outline="#34599C")
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
        Label(self.login_frame, text="Contraseña", font=("Arial", 18), bg="#e6f1fd").pack(anchor="w")
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
            with open(self.archivo_usuarios, "w", encoding="utf-8") as f:
                f.write("admin:admin:-:1\n")

        self.ventana.bind("<Return>", lambda event: self.login())
        self.ventana.bind("<KP_Enter>", lambda event: self.login())

    def login(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()
        tipo = self.validar_usuario(usuario, contrasena)

        if tipo:
            messagebox.showinfo("Login", f"¡Bienvenido {usuario}!")
            self.ventana.destroy()  # Cierra ventana de login

            if tipo == "1":  # Admin
                AdminPanel(usuario)
            elif tipo == "2":  # Inspector
                InspectorPanel(usuario)               
            elif tipo == "3": #Usuario  
                UserPanel(usuario)  
        else:
            messagebox.showerror("Login", "Usuario o contraseña incorrectos.")

    def validar_usuario(self, usuario, contrasena):
        with open(self.archivo_usuarios, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                u, c, d, t = linea.split(":", 3)  # 4 campos
                if u == usuario and c == contrasena:
                    return t
        return None

    def abrir_registro(self):
        # Desde el login permitir registrarse como tipo de usuario 3 (Usuario)
        Registro(self.archivo_usuarios, solo_usuario_comun=True)

    def run(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    start_api_in_thread() # <-- 2. Iniciar el servidor API antes de la GUI
    app = Login()
    app.run()
