from tkinter import Toplevel, Label, Frame, Entry, Text, Button, filedialog, messagebox
from tkinter import ttk
import datetime
import os

ARCHIVO_MULTAS = "multas.txt"

def agregar_multa(ventana_padre, usuario_actual):
    # --- Ventana secundaria ---
    multa = Toplevel(ventana_padre)
    multa.title("Agregar Multa")
    multa.geometry("450x350")
    multa.config(bg="white")

    Label(multa, text="Agregar Multa", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    # Frame formulario
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

    Button(form_frame, text="Agregar Foto", command=seleccionar_foto).grid(row=2, column=1, pady=10, sticky="w")

    # Guardar multa
    def guardar_multa():
        patente     = entry_patente.get().strip().upper()
        observacion = txt_obs.get("1.0", "end").strip()
        foto        = foto_path["ruta"]

        if not patente:
            messagebox.showwarning("Error", "Debe ingresar una patente")
            return

        # Guardar en archivo
        with open(ARCHIVO_MULTAS, "a", encoding="utf-8") as f:
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


def mostrar_multas(ventana_padre, patente):
    """Muestra multas de una patente y permite eliminarlas"""
    ventana = Toplevel(ventana_padre)
    ventana.title(f"Multas de {patente}")
    ventana.geometry("600x400")
    ventana.resizable(False,False)
    ventana.config(bg="#e6f1fd")

    Label(ventana, text=f"Multas registradas de {patente}", font=("Arial", 14, "bold"), bg="#e6f1fd").pack(pady=10)

    # Treeview
    tree = ttk.Treeview(ventana, columns=("obs", "foto"), show="headings")
    tree.heading("obs", text="Observación")
    tree.heading("foto", text="Foto")
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    # Cargar multas desde archivo
    multas = []
    if os.path.exists(ARCHIVO_MULTAS):
        with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                p, obs, foto = linea.split("|")
                if p == patente:
                    multas.append((p, obs, foto))
                    tree.insert("", "end", values=(obs, foto))

    if not multas:
        messagebox.showinfo("Info", f"No se encontraron multas para {patente}")

    # Eliminar multa seleccionada
    def eliminar_multa():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una multa para eliminar")
            return

        obs, foto = tree.item(seleccion, "values")
        confirmar = messagebox.askyesno("Confirmar", "¿Eliminar multa seleccionada?")
        if not confirmar:
            return

        # Actualizar archivo
        nuevas_lineas = []
        with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
            for linea in f:
                if f"{patente}|{obs}|{foto}" not in linea.strip():
                    nuevas_lineas.append(linea)

        with open(ARCHIVO_MULTAS, "w", encoding="utf-8") as f:
            f.writelines(nuevas_lineas)

        tree.delete(seleccion)
        messagebox.showinfo("Éxito", "Multa eliminada")

    Button(ventana, text="ELIMINAR", font=("Calisto MT", 14, "bold"),bg="red", fg="white", command=eliminar_multa).pack(pady=5)
