# -*- coding: utf-8 -*-
# Importar librerías
from IB_Trading import IB_Trading, Contract
from Analisis_Tecnico import Cruce_MA
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

# Seleccionar Activos a Analizar
tickers = ["AMZN", "AAPL", "TSLA", "MSFT", "GOOG", "META", "NVDA"]
marco_tiempo = "1 hour"
tiempo_descargado = "15 D"

# Generar Instancia
IB_app = IB_Trading(log_file="alternative_errors.txt", errors_verbose = True)
IB_app.connect(host="127.0.0.1", port=7497, clientId=1)

# Definir Función para ejecutar órdenes
def ejecutar_orden(IB_app: IB_Trading, ticker: str, contrato: Contract, direccion: str, cantidad: int = 10) -> None:
    
    """
    Ejecuta una orden de mercado para un activo específico.
    """
    
    # Ejecutar Orden
    orden_mercado = IB_app.market_order(action=direccion, totalQuantity=cantidad)
    next_id = IB_app.reqIds(numIds=-1)
    IB_app.placeOrder(orderId=next_id, contract=contrato, order=orden_mercado)
    

# Definir Función para Procesar las Posiciones
def procesar_posiciones(IB_app: IB_Trading, ticker: str, direccion: str, contrato: Contract) -> None:
    
    """
    Gestiona las posiciones existentes y decide si se deben ejecutar nuevas órdenes.

    La función verifica las posiciones actuales para el activo especificado. Si existen posiciones y su dirección
    es opuesta a la orden solicitada, se ejecuta una nueva orden en la dirección especificada para cerrar la 
    posición actual.
    """
    
    posiciones = IB_app.reqPositions()
    if isinstance(posiciones, pd.DataFrame):
        posiciones = posiciones[(posiciones["Cantidad"] != 0) & (posiciones["Símbolo"] == ticker)]
        if len(posiciones) > 0:
            cantidad = posiciones["Cantidad"].iloc[0]
            if (direccion == "BUY" and cantidad < 0) or (direccion == "SELL" and cantidad > 0):
                ejecutar_orden(IB_app, ticker, contrato, direccion)
                
    
# Definir Función para Procesar las Órdenes
def procesar_ordenes(IB_app: IB_Trading, ticker: str, direccion: str, contrato: Contract) -> None:
    
    """
    Revisa y gestiona las órdenes abiertas para un activo específico.

    La función primero revisa si hay órdenes abiertas para el activo especificado. Si no hay órdenes abiertas,
    genera una nueva orden de mercado en la dirección especificada. Si ya existen órdenes abiertas y la dirección
    actual es opuesta a la dirección de las órdenes abiertas, cancela las órdenes existentes y coloca una nueva
    orden en la dirección especificada.
    """
    
    ordenes = IB_app.reqAllOpenOrders()
    if isinstance(ordenes, pd.DataFrame):
        ordenes = ordenes[ordenes["activo"] == ticker]
        if len(ordenes) == 0:
            ejecutar_orden(IB_app=IB_app, ticker=ticker, contrato=contrato, direccion=direccion)
        else:
            posicion_actual = ordenes["posicion"].iloc[0]
            if (direccion == "BUY" and posicion_actual == "SELL") or (direccion == "SELL" and posicion_actual == "BUY"):
                IB_app.cancelOrder(orderId=ordenes["orderId"].iloc[0])
                ejecutar_orden(IB_app, ticker, contrato, direccion)

# Ejecutar Sistema
datos = {}
# Crear Contrato
contrato = Contract()
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

while True:
    # Revisar si se han generado señales para cada ticker
    for ticker in tickers:
        contrato.symbol = ticker
        df = IB_app.reqHistoricalData(reqId=0, contract=contrato, durationStr=tiempo_descargado, barSizeSetting=marco_tiempo)
        # Detectar Cruces
        cma = Cruce_MA(df=df, tendencia_rápida=9, tendencia_lenta=21)
        # Revisar si se generó una señal
        if pd.notna(cma["Cruces"].iloc[-1]):
            # Obtener Dirección de la Señal Generada
            direccion = "BUY" if cma["Cruces"].iloc[-1] == 1 else "SELL"
            # Revisar si no hay posiciones u órdenes actuales
            existente = IB_app.existing_order_position(ticker=ticker)
            if not existente:
                # Generar Orden
                ejecutar_orden(IB_app=IB_app, ticker=ticker, contrato=contrato, direccion=direccion)
            else:
                # Procesar Primero las Posiciones
                procesar_posiciones(IB_app=IB_app, ticker=ticker, direccion=direccion, contrato=contrato)
                # Procesar Órdenes Activas
                procesar_ordenes(IB_app=IB_app, ticker=ticker, direccion=direccion, contrato=contrato)

    # Definir Horario de Nueva York (Para Cesar Ejecución)
    ny = pytz.timezone("America/New_York")
    hora_ny = datetime.now(ny)
    horario_cierre = hora_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    # Cerrar Posiciones si ya no se puede realizar otra iteracón: Las posiciones se cerrarán 1 minuto antes de que el mercado cierre
    if (hora_ny + timedelta(hours=1)) > horario_cierre:
        # Pausar la ejecución del código hasta un minuto antes del cierre del mercado
        hora_cierre_menos_un_minuto = horario_cierre - timedelta(minutes=1)
        tiempo_dormir = (hora_cierre_menos_un_minuto - hora_ny).total_seconds()
        time.sleep(tiempo_dormir)
        # Cerrar Todo
        IB_app.end_session(account = "DUE273425", close_orders = True, close_positions = True)
        # Terminar Bucle
        break
    else:
        # Mostrar en Consola
        print("Código dormirá por 1 hora...")
        # Dormir en cada Iteración (1 Hora)
        time.sleep(60 * 60)

# Esperar 1 minuto y desconectarse del Servidor
time.sleep(60)
IB_app.disconnect()
