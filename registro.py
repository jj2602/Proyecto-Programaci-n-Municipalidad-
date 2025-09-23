from tkinter import Toplevel, Label, Entry, Button, StringVar, OptionMenu, messagebox

class Registro:
    def __init__(self, archivo_usuarios, solo_usuario_comun=False):
        self.archivo_usuarios = archivo_usuarios
        self.solo_usuario_comun = solo_usuario_comun
        self.registro_ventana = Toplevel()
        self.registro_ventana.title("Registro de Usuario")
        self.registro_ventana.geometry("400x475")
        self.registro_ventana.resizable(False, False)
        self.registro_ventana.configure(bg="#e6f1fd")

        Label(self.registro_ventana, text="Nuevo Usuario:", font=("Arial", 14), bg="#e6f1fd").pack(pady=(20, 5))
        self.entry_nuevo_usuario = Entry(self.registro_ventana, font=("Arial", 14))
        self.entry_nuevo_usuario.pack(pady=(0, 20))

        Label(self.registro_ventana, text="Documento(DNI):", font=("Arial", 14),bg="#e6f1fd").pack(pady=(0, 5))
        self.entry_documento = Entry(self.registro_ventana, font=("Arial", 14))
        self.entry_documento.pack(pady=(0, 20))

        Label(self.registro_ventana, text="Nueva Contraseña:", font=("Arial", 14),bg="#e6f1fd").pack(pady=(0, 5))
        self.entry_nueva_contrasena = Entry(self.registro_ventana, font=("Arial", 14), show="*")
        self.entry_nueva_contrasena.pack(pady=(0, 20))
        
        Label(self.registro_ventana, text="Repetir Contraseña:", font=("Arial", 14),bg="#e6f1fd").pack(pady=(0, 5))
        self.entry_repetir_contrasena = Entry(self.registro_ventana, font=("Arial", 14), show="*")
        self.entry_repetir_contrasena.pack(pady=(0, 20))
        
        #Falta agregar toda la parte de patentes , datos como dni , etc etc 
        ##
        ##

        # Tipo de usuario
        if not self.solo_usuario_comun:
            Label(self.registro_ventana, text="Tipo de Usuario:", font=("Arial", 14), bg="#e6f1fd").pack(pady=(0, 5))
            self.tipo_usuario = StringVar(self.registro_ventana)
            self.tipo_usuario.set("3")  # Por defecto usuario común
            opciones = {"1": "Administrador", "2": "Inspector", "3": "Usuario"}
            self.dropdown = OptionMenu(self.registro_ventana, self.tipo_usuario, *opciones.keys())
            self.dropdown.pack(pady=(0, 20))
        else:
            # si es registro desde el login, forzamos tipo = 3
            self.tipo_usuario = "3"

        Button(self.registro_ventana, text="Registrar", font=("Arial", 14, "bold"),
               bg="#ffffff", fg="black", width=15, command=self.registrar_usuario).pack()
        
        condiciones_contrasena = ("La contraseña debe tener al menos 5 caracteres, ""incluir una mayúscula, una minúscula y un carácter especial.")
        Label(self.registro_ventana,text=condiciones_contrasena,font=("Arial", 10),bg="#e6f1fd",fg="#971212",wraplength=360,).pack(side="bottom", fill="x", padx=12, pady=10)
 
    def validar_contrasena(self, nueva_contrasena):
        tiene_mayus = any(c.isupper() for c in nueva_contrasena)
        tiene_minus = any(c.islower() for c in nueva_contrasena)
        tiene_especial = any(not c.isalnum() for c in nueva_contrasena)
        longitud_ok = len(nueva_contrasena) >= 5
        return tiene_mayus and tiene_minus and tiene_especial and longitud_ok
    
    def validar_documento(self, nuevo_documento):
        solo_num = nuevo_documento.isdigit()
        longitud_documento = len(nuevo_documento) == 8
        return solo_num and longitud_documento
    
    def registrar_usuario(self):
        nuevo_usuario = self.entry_nuevo_usuario.get()
        nuevo_documento = self.entry_documento.get()
        nueva_contrasena = self.entry_nueva_contrasena.get()
        repetir_contrasena = self.entry_repetir_contrasena.get()
        
        # si no es admin, tipo fijo
        if self.solo_usuario_comun:
            tipo = "3"
        else:
            tipo = self.tipo_usuario.get()

        if not nuevo_usuario or not nueva_contrasena or not repetir_contrasena or not nuevo_documento:
            messagebox.showwarning("Registro", "Debe completar todos los campos.")
            return
        if nueva_contrasena != repetir_contrasena:
            messagebox.showwarning("Registro", "Las contrasenas no coinciden.")
            return
        if not self.validar_contrasena(nueva_contrasena):
            messagebox.showwarning("Registro", "La contrasena no cumple con las condiciones.")
            return
        if not self.validar_documento(nuevo_documento):
            messagebox.showwarning("Registro", "Ingrese un documento válido.")
        # Validar si ya existe
        with open(self.archivo_usuarios, "r") as f:
            for linea in f:
                u, _, _ = linea.strip().split(":", 2)
                if u == nuevo_usuario:
                    messagebox.showerror("Registro", "El usuario ya existe.")
                    return

        # Guardar usuario
        with open(self.archivo_usuarios, "a") as f:
            f.write(f"{nuevo_usuario}:{nueva_contrasena}:{nuevo_documento}:{tipo}\n")

        messagebox.showinfo("Registro", "Usuario registrado con éxito.")
        self.registro_ventana.destroy()
