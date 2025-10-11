from tkinter import Toplevel, Label, Frame, Entry, Text, Button, filedialog, messagebox
from tkinter import ttk
import datetime
import os
import qrcode
from PIL import Image, ImageTk
import socket
from urllib.parse import quote


# ----------------------------------------------------
# Obtener IP local para generar enlaces accesibles
# ----------------------------------------------------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# ----------------------------------------------------
# Constantes de archivos
# ----------------------------------------------------
ARCHIVO_MULTAS = "multas.txt"
APELACIONES_ARCHIVO = "apelaciones.txt"


# ----------------------------------------------------
# AGREGAR MULTA
# ----------------------------------------------------
def agregar_multa(ventana_padre, usuario_actual):
    multa = Toplevel(ventana_padre)
    multa.title("Agregar Multa")
    multa.geometry("500x450")
    multa.resizable(False, False)
    multa.config(bg="#34599C")

    Label(multa, text="Agregar Multa", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    form_frame = Frame(multa, bg="white")
    form_frame.pack(padx=20, pady=10, fill="x")

    # Campos
    Label(form_frame, text="Patente:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
    entry_patente = Entry(form_frame, width=25)
    entry_patente.grid(row=0, column=1, pady=5)

    Label(form_frame, text="Observación:", bg="white").grid(row=1, column=0, sticky="nw", pady=5)
    txt_obs = Text(form_frame, width=30, height=5)
    txt_obs.grid(row=1, column=1, pady=5)

    Label(form_frame, text="Importe ($):", bg="white").grid(row=2, column=0, sticky="w", pady=5)
    entry_importe = Entry(form_frame, width=25)
    entry_importe.grid(row=2, column=1, pady=5)

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
        patente = entry_patente.get().strip().upper()
        observacion = txt_obs.get("1.0", "end").strip()
        importe = entry_importe.get().strip()
        foto = foto_path["ruta"] or "Sin foto"

        if not (patente and observacion and importe):
            messagebox.showwarning("Error", "Complete todos los campos")
            return

        # Guardar multa
        with open(ARCHIVO_MULTAS, "a", encoding="utf-8") as f:
            f.write(f"{patente}|{observacion}|{importe}|{foto}\n")

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
            f"Foto: {foto}\n"
            "=================================\n"
            "   Sistema de Control Vehicular   \n"
        )

        with open(ticket_nombre, "w", encoding="utf-8") as t:
            t.write(contenido_ticket)

        messagebox.showinfo("Éxito", f"Multa agregada a {patente}\nTicket generado: {ticket_nombre}")
        multa.destroy()

    Button(multa, text="Guardar Multa", bg="#006172", fg="white", command=guardar_multa).pack(pady=15)


# ----------------------------------------------------
# MOSTRAR MULTAS (usuario o inspector)
# ----------------------------------------------------
def mostrar_multas(ventana_padre, patente, modo_usuario=False):
    ventana = Toplevel(ventana_padre)
    ventana.title(f"Multas de {patente}")
    ventana.geometry("650x400")
    ventana.config(bg="#e6f1fd")

    Label(ventana, text=f"Multas registradas de {patente}",
          font=("Arial", 14, "bold"), bg="#e6f1fd").pack(pady=10)

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
                partes = linea.strip().split("|")
                if len(partes) >= 4 and partes[0] == patente:
                    p, obs, imp, foto = partes[:4]
                    multas.append((p, obs, imp, foto))
                    tree.insert("", "end", values=(obs, imp, foto))

    if not multas:
        messagebox.showinfo("Info", f"No se encontraron multas para {patente}")
        return

    # ----------------------------------------------------
    # MODO USUARIO (Pagar y Apelar)
    # ----------------------------------------------------
    if modo_usuario:

        def pagar_multa():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccione una multa para pagar")
                return

            obs, importe, foto = tree.item(seleccion, "values")

            local_ip = get_local_ip()
            url_pago = (
                f"http://{local_ip}:8000/pay?patente={quote(patente)}"
                f"&obs={quote(obs)}&importe={quote(importe)}&foto={quote(foto)}"
            )

            qr = qrcode.QRCode(version=None, box_size=10, border=4)
            qr.add_data(url_pago)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")

            qr_win = Toplevel(ventana)
            qr_win.title("Escanee el QR para pagar la multa")
            qr_win.geometry("500x500")
            qr_win.resizable(False, False)

            img_qr_tk = ImageTk.PhotoImage(img_qr)
            Label(qr_win, image=img_qr_tk).pack(expand=True, fill="both")
            qr_win.image = img_qr_tk

            def al_cerrar_qr():
                messagebox.showinfo("Pago realizado", "La multa fue pagada correctamente.")
                # Eliminar multa del archivo
                nuevas_lineas = []
                with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
                    for linea in f:
                        datos = linea.strip().split("|")
                        if len(datos) < 4:
                            continue
                        p, o, i, fot = datos[:4]
                        # Comparación flexible sin depender de formato exacto
                        if not (p == patente and o == obs and i == importe and fot == foto):
                            nuevas_lineas.append(linea)
                with open(ARCHIVO_MULTAS, "w", encoding="utf-8") as f:
                    f.writelines(nuevas_lineas)

                tree.delete(seleccion)
                qr_win.destroy()
                messagebox.showinfo("Éxito", "La multa fue eliminada del registro.")

            qr_win.protocol("WM_DELETE_WINDOW", al_cerrar_qr)

        def apelar_multa():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccione una multa para apelar.")
                return

            obs, importe, foto = tree.item(seleccion, "values")

            apelacion_win = Toplevel(ventana)
            apelacion_win.title("Apelar Multa")
            apelacion_win.geometry("400x300")
            apelacion_win.resizable(False, False)

            Label(apelacion_win, text="Escriba el motivo de su apelación:", font=("Arial", 12)).pack(pady=10)
            txt_motivo = Text(apelacion_win, width=45, height=10)
            txt_motivo.pack(padx=10, pady=5)

            def guardar_apelacion():
                motivo = txt_motivo.get("1.0", "end").strip()
                if not motivo:
                    messagebox.showwarning("Error", "Debe escribir un motivo para la apelación.")
                    return

                with open(APELACIONES_ARCHIVO, "a", encoding="utf-8") as f:
                    f.write(f"{patente}|{obs}|{importe}|{foto}|{motivo}|PENDIENTE\n")

                messagebox.showinfo("Éxito", "Apelación enviada correctamente.")
                apelacion_win.destroy()

            Button(apelacion_win, text="Enviar Apelación", command=guardar_apelacion).pack(pady=10)

        botonera = Frame(ventana, bg="#e6f1fd")
        botonera.pack(pady=8)

        Button(botonera, text="PAGAR", bg="green", fg="white",
               font=("Calisto MT", 14, "bold"), width=12, command=pagar_multa).pack(side="left", padx=10)
        Button(botonera, text="APELAR", bg="red", fg="white",
               font=("Calisto MT", 14, "bold"), width=12, command=apelar_multa).pack(side="right", padx=10)

    # ----------------------------------------------------
    # MODO INSPECTOR (Eliminar)
    # ----------------------------------------------------
    else:
        def eliminar_multa():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccione una multa para eliminar")
                return

            obs, importe, foto = tree.item(seleccion, "values")
            confirmar = messagebox.askyesno("Confirmar", "¿Eliminar multa seleccionada?")
            if not confirmar:
                return

            nuevas_lineas = []
            with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
                for linea in f:
                    datos = linea.strip().split("|")
                    if len(datos) < 4:
                        continue
                    p, o, i, fot = datos[:4]
                    if not (p == patente and o == obs and i == importe and fot == foto):
                        nuevas_lineas.append(linea)
            with open(ARCHIVO_MULTAS, "w", encoding="utf-8") as f:
                f.writelines(nuevas_lineas)

            tree.delete(seleccion)
            messagebox.showinfo("Éxito", "Multa eliminada correctamente.")

        Button(ventana, text="ELIMINAR", font=("Calisto MT", 14, "bold"),
               bg="red", fg="white", command=eliminar_multa).pack(pady=10)

