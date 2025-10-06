# ticket.py
from tkinter import Toplevel, Label, Frame, Entry, Text, Button, filedialog, messagebox
from tkinter import ttk
import datetime
import os
import qrcode
from PIL import Image, ImageTk

ARCHIVO_MULTAS = "multas.txt"

# ------------------ AGREGAR MULTA ------------------
def agregar_multa(ventana_padre, usuario_actual):
    multa = Toplevel(ventana_padre)
    multa.title("Agregar Multa")
    multa.geometry("500x450")
    multa.resizable(False, False)
    multa.config(bg="#34599C")

    Label(multa, text="Agregar Multa", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

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

    # Importe
    Label(form_frame, text="Importe ($):", bg="white", anchor="w").grid(row=2, column=0, sticky="w", pady=5)
    entry_importe = Entry(form_frame, width=25)
    entry_importe.grid(row=2, column=1, pady=5, padx=5, sticky="w")

    # Foto
    foto_path = {"ruta": None}
    def seleccionar_foto():
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=[("Imagenes", "*.png;*.jpg;*.jpeg")]
        )
        if ruta:
            foto_path["ruta"] = ruta

    Button(form_frame, text="Agregar Foto", command=seleccionar_foto).grid(row=3, column=1, pady=10, sticky="w")

    # Guardar multa
    def guardar_multa():
        patente     = entry_patente.get().strip().upper()
        observacion = txt_obs.get("1.0", "end").strip()
        importe     = entry_importe.get().strip()
        foto        = foto_path["ruta"]

        if not (patente and observacion and importe):
            messagebox.showwarning("Error", "Complete todos los campos")
            return

        # Guardar en archivo
        with open(ARCHIVO_MULTAS, "a", encoding="utf-8") as f:
            f.write(f"{patente}|{observacion}|{importe}|{foto if foto else 'Sin foto'}\n")

        # Crear ticket
        fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ticket_nombre = f"ticket_{patente}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        contenido_ticket = (
            "=================================\n"
            "           TICKET DE MULTA       \n"
            "=================================\n"
            f"Patente: {patente}\n"
            f"Inspector: {usuario_actual}\n"
            f"Fecha: {fecha}\n"
            f"Observación:\n{observacion}\n"
            f"Importe: ${importe}\n"
            f"Foto: {foto if foto else 'Sin foto'}\n"
            "=================================\n"
            "   Sistema de Control Vehicular   \n"
        )

        with open(ticket_nombre, "w", encoding="utf-8") as t:
            t.write(contenido_ticket)

        # Vista previa del ticket
        ticket_win = Toplevel(multa)
        ticket_win.title("Ticket generado")
        ticket_win.geometry("400x650")
        ticket_win.resizable(False, False)
        ticket_win.config(bg="#34599C")

        Label(ticket_win, text="Vista previa del Ticket", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        txt_ticket = Text(ticket_win, wrap="word", width=50, height=18, bg="white", fg="black")
        txt_ticket.pack(padx=10, pady=10, expand=True, fill="both")
        txt_ticket.insert("1.0", contenido_ticket)
        txt_ticket.config(state="disabled")  # Solo lectura

        messagebox.showinfo("Éxito", f"Multa agregada a {patente}\nTicket generado: {ticket_nombre}")
        multa.destroy()

    Button(multa, text="Guardar Multa", bg="#006172", fg="white", command=guardar_multa).pack(pady=15)


# ------------------ MOSTRAR MULTAS ------------------
def mostrar_multas(ventana_padre, patente, modo_usuario=False):
    """
    Muestra multas de una patente.
    Si modo_usuario=True, reemplaza el botón 'Eliminar' por 'Pagar'.
    """
    ventana = Toplevel(ventana_padre)
    ventana.title(f"Multas de {patente}")
    ventana.geometry("650x400")
    ventana.resizable(False, False)
    ventana.config(bg="#e6f1fd")

    Label(ventana, text=f"Multas registradas de {patente}", font=("Arial", 14, "bold"), bg="#e6f1fd").pack(pady=10)

    tree = ttk.Treeview(ventana, columns=("obs", "importe", "foto"), show="headings")
    tree.heading("obs", text="Observación")
    tree.heading("importe", text="Importe ($)")
    tree.heading("foto", text="Foto")
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    # Cargar multas
    multas = []
    if os.path.exists(ARCHIVO_MULTAS):
        with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                p, obs, importe, foto = linea.split("|")
                if p == patente:
                    multas.append((p, obs, importe, foto))
                    tree.insert("", "end", values=(obs, importe, foto))

    if not multas:
        messagebox.showinfo("Info", f"No se encontraron multas para {patente}")

    if modo_usuario:
    # ----------------- BOTON PAGAR -----------------
        def pagar_multa():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccione una multa para pagar")
                return

            obs, importe, foto = tree.item(seleccion, "values")

            # URL de pago, incluyendo patente e importe como parámetros
            url_pago = f"https://www.ucel.edu.ar/courses/ingenieria-en-sistemas-de-informacion/?patente={patente}&importe={importe}"

            # Generar QR
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(url_pago)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")

            # Mostrar QR
            qr_win = Toplevel(ventana)
            qr_win.title("Escanee el QR para pagar la multa")
            qr_win.geometry("500x500")
            qr_win.resizable(False, False)

            img_qr_tk = ImageTk.PhotoImage(img_qr)
            lbl_qr = Label(qr_win, image=img_qr_tk)
            lbl_qr.image = img_qr_tk
            lbl_qr.pack(expand=True, fill="both")

            # Al cerrar QR, eliminar la multa
            def cerrar_qr():
                nuevas_lineas = []
                with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
                    for linea in f:
                        if f"{patente}|{obs}|{importe}|{foto}" not in linea.strip():
                            nuevas_lineas.append(linea)

                with open(ARCHIVO_MULTAS, "w", encoding="utf-8") as f:
                    f.writelines(nuevas_lineas)

                tree.delete(seleccion)
                qr_win.destroy()
                messagebox.showinfo("Éxito", "Multa pagada y eliminada")

            qr_win.protocol("WM_DELETE_WINDOW", cerrar_qr)

        # --- Botón APELAR (por ahora usa la misma función que PAGAR) ---
        def apelar_multa():
            messagebox.showinfo("Apelar", "Función para apelar multa (en desarrollo).")

        # --- Contenedor para ambos botones ---
        botonera = Frame(ventana, bg="#e6f1fd")
        botonera.pack(pady=8, fill="x")

        Button(
            botonera, text="PAGAR", font=("Calisto MT", 14, "bold"),
            bg="green", fg="white", width=12, command=pagar_multa
        ).pack(side="left", padx=(10, 5), pady=2)

        Button(
            botonera, text="APELAR", font=("Calisto MT", 14, "bold"),
            bg="red", fg="white", width=12, command=apelar_multa
        ).pack(side="right", padx=(5, 10), pady=2)


    else:
        # ----------------- BOTON ELIMINAR (admin) -----------------
        def eliminar_multa():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccione una multa para eliminar")
                return

            obs, importe, foto = tree.item(seleccion, "values")
            confirmar = messagebox.askyesno("Confirmar", "¿Eliminar multa seleccionada?")
            if not confirmar:
                return

            # Actualizar archivo
            nuevas_lineas = []
            with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
                for linea in f:
                    if f"{patente}|{obs}|{importe}|{foto}" not in linea.strip():
                        nuevas_lineas.append(linea)

            with open(ARCHIVO_MULTAS, "w", encoding="utf-8") as f:
                f.writelines(nuevas_lineas)

            tree.delete(seleccion)
            messagebox.showinfo("Éxito", "Multa eliminada")

        Button(ventana, text="ELIMINAR", font=("Calisto MT", 14, "bold"), bg="red", fg="white",
               command=eliminar_multa).pack(pady=5)
