# payment_api.py ## GENERA LA PARTE DE LA PAGINA WEB CUANDO ESCANEAS EL QR

import threading
import uvicorn
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
import os
from decimal import Decimal, InvalidOperation
 
# --- SOLUCIÓN: Construir una ruta absoluta al archivo de multas ---
# 1. Obtener la ruta del directorio donde se encuentra este script (payment_api.py)
directorio_actual = os.path.dirname(os.path.abspath(__file__))
# 2. Subir un nivel para llegar a la carpeta 'Proyecto_Programacion'
directorio_proyecto = os.path.dirname(directorio_actual)
# 3. Construir la ruta completa a multas.txt
ARCHIVO_MULTAS = os.path.join(directorio_actual, "multas.txt")
 
# Lock para evitar condiciones de carrera al escribir en el archivo
file_lock = threading.Lock()
 
app = FastAPI()
 
@app.get("/pay", response_class=HTMLResponse)
def process_payment(patente: str, obs: str, importe: str, foto: str):
    """
    Muestra la página de pago para que el usuario elija el monto.
    """
    try:
        importe_decimal = Decimal(importe)
    except InvalidOperation:
        return "<h1>Error: Importe inválido</h1>"
 
    # Devolver una página con un formulario de pago
    return f"""
    <html>
        <head>
            <title>Realizar Pago de Multa</title>
            <style>
                body {{ font-family: sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .container {{ background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 400px; }}
                h1 {{ color: #333; }}
                .detail {{ margin: 10px 0; }}
                .detail strong {{ color: #555; }}
                input[type=number], button {{ width: 100%; padding: 12px; margin-top: 10px; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; font-size: 16px; }}
                button {{ background-color: #28a745; color: white; font-weight: bold; cursor: pointer; border: none; }}
                button:hover {{ background-color: #218838; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Pago de Multa</h1>
                <div class="detail"><strong>Patente:</strong> {patente}</div>
                <div class="detail"><strong>Infracción:</strong> {obs}</div>
                <div class="detail"><strong>Importe Total Adeudado:</strong> ${importe_decimal:.2f}</div>
                <hr>
                <form action="/process-payment" method="post">
                    <input type="hidden" name="patente" value="{patente}">
                    <input type="hidden" name="obs" value="{obs}">
                    <input type="hidden" name="original_importe" value="{importe}">
                    <input type="hidden" name="foto" value="{foto}">
                    
                    <label for="monto_a_pagar"><strong>Monto a Pagar:</strong></label>
                    <input type="number" id="monto_a_pagar" name="monto_a_pagar" value="{importe_decimal:.2f}" step="0.01" min="0.01" max="{importe_decimal:.2f}" required>
                    
                    <button type="submit">Confirmar Pago</button>
                </form>
            </div>
        </body>
    </html>
    """
 
@app.post("/process-payment", response_class=HTMLResponse)
def do_payment(
    patente: str = Form(...),
    obs: str = Form(...),
    original_importe: str = Form(...),
    foto: str = Form(...),
    monto_a_pagar: str = Form(...)
):
    try:
       
        # Eliminar multa del archivo
        nuevas_lineas = []
        with open(ARCHIVO_MULTAS, "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split("|")
                if len(datos) < 4:
                    continue
                p, o, i, fot = datos[:4]
                # Comparación flexible sin depender de formato exacto
                if not (p == patente and o == obs and i == original_importe and fot == foto):
                    nuevas_lineas.append(linea)
        with open(ARCHIVO_MULTAS, "w", encoding="utf-8") as f:
            f.writelines(nuevas_lineas)

    except InvalidOperation:
        return "<h1>Error: Monto inválido.</h1>"
    return """<html>
La multa fue pagada
</html>

"""
"""""
    """
 
def run_api():
    """Función para correr uvicorn en el host y puerto especificados."""
    # Usamos 0.0.0.0 para que sea accesible desde otros dispositivos en la misma red (como tu teléfono)
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
def start_api_in_thread():
    """Inicia el servidor FastAPI en un hilo separado para no bloquear la GUI."""
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print("Servidor de pagos iniciado. Escanee el QR desde su teléfono.")
    print("Asegúrese de que su PC y teléfono estén en la misma red WiFi.")
