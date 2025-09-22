from tkinter import Toplevel, Label, Frame, Entry, Text, Button, filedialog, messagebox
import datetime

def agregar_multa(ventana_padre, usuario_actual):
    # --- Ventana secundaria ---
    multa = Toplevel(ventana_padre)
    multa.title("Agregar Multa")
    multa.geometry("450x350")
    multa.config(bg="white")

    Label(multa, text="Agregar Multa", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    # Frame para formulario con grid
    form_frame = Frame(multa, bg="white")
    form_frame.pack(padx=20, pady=10, fill="x")

    # Patente
    Label(form_frame, text="Patente:", bg="white", anchor="w").grid(row=0, column=0, sticky="w", pady=5)
    entry_patente = Entry(form_frame, width=25)
    entry_patente.grid(row=0, column=1, pady=5, padx=5, sticky="w")

    # Observación
    Label(form_frame, text="Observación:", bg="white", anchor="w").grid(row=1, column=0, sticky="nw", pady=5)
    txt_obs = Text(form_frame, width=30, height=5)
    txt_obs.grid(row=1, column=1, pady=5, padx=5, sticky="w")

    # Foto
    foto_path = {"ruta": None}
    def seleccionar_foto():
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=[("Imagenes", "*.png;*.jpg;*.jpeg")]
        )
        if ruta:
            foto_path["ruta"] = ruta
           # messagebox.showinfo("Foto seleccionada", f"Se cargó: {ruta}")

    Button(form_frame, text="Agregar Foto", command=seleccionar_foto).grid(row=2, column=1, pady=10, sticky="w")

    # Botón guardar
    def guardar_multa():
        patente = entry_patente.get().strip()
        observacion = txt_obs.get("1.0", "end").strip()
        foto = foto_path["ruta"]

        if not patente:
            messagebox.showwarning("Error", "Debe ingresar una patente")
            return

        # Guardar en archivo de registro
        with open("multas.txt", "a") as f:
            f.write(f"{patente}|{observacion}|{foto if foto else 'Sin foto'}\n")

        # Crear ticket TXT
        fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ticket_nombre = f"ticket_{patente}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(ticket_nombre, "w", encoding="utf-8") as t:
            t.write("=================================\n")
            t.write("           TICKET DE MULTA       \n")
            t.write("=================================\n")
            t.write(f"Patente: {patente}\n")
            t.write(f"Inspector: {usuario_actual}\n")
            t.write(f"Fecha: {fecha}\n")
            t.write(f"Observación:\n{observacion}\n")
            t.write(f"Foto: {foto if foto else 'Sin foto'}\n")
            t.write("=================================\n")
            t.write("   Sistema de Control Vehicular   \n")

        messagebox.showinfo("Éxito", f"Multa agregada a {patente}\nTicket generado: {ticket_nombre}")
        multa.destroy()

    Button(multa, text="Guardar Multa", bg="#006172", fg="white", command=guardar_multa).pack(pady=15)
