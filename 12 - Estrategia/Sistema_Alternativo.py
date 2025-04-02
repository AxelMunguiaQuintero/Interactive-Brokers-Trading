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
IB_app = IB_Trading(log_file="alternative_errors.txt", errors_verbose=True)
IB_app.connect(host="127.0.0.1", port=7497, clientId=2)

# Definir Función para ejecutar órdenes
def ejecutar_orden(IB_app: IB_Trading, ticker: str, contrato: Contract, direccion: str, cantidad: int = 10) -> None:
    
    """
    Ejecuta una orden de mercado para un activo específico.
    """
    
    # Ejecutar Orden
    orden_mercado = IB_app.market_order(action=direccion, totalQuantity=cantidad)
    next_id = IB_app.reqIds(numIds=-1)
    IB_app.placeOrder(orderId=next_id, contract=contrato, order=orden_mercado)
    

# Definir Función para procesar las Posiciones
def procesar_posiciones(IB_app: IB_Trading, ticker: str, direccion: str, contrato: Contract) -> None:
    
    """
    Gestiona las posiciones existentes y decide si deben de ejecutar nuevas órdenes.
    
    La función verifica las posiciones actuales para el activo especificado. Si existen posiciones y su dirección
    es opuesta a la orden solicitada, se ejecuta una nueva orden en la dirección especificada para cerrar la posición
    actual.
    
    En cambio, si la señal generada coincide con la dirección de la posición actual, no se abre una nueva posición
    y se mantiene únicamente la existente.
    """
    
    # Obtener Cartera de Inversión
    posiciones = IB_app.reqPositions()
    if isinstance(posiciones, pd.DataFrame):
        # Filtrar posiciones reales
        posiciones = posiciones[(posiciones["Cantidad"] != 0) & (posiciones["Símbolo"] == ticker)]
        if len(posiciones) > 0:
            cantidad = posiciones["Cantidad"].iloc[0]
            # Revisar si se tiene que cerrar (Se generó una señal opuesta)
            if (direccion == "BUY" and cantidad < 0) or (direccion == "SELL" and cantidad > 0):
                ejecutar_orden(IB_app=IB_app, ticker=ticker, contrato=contrato, direccion=direccion)
                
                
# Definir Función para Procesar las órdenes
def procesar_ordenes(IB_app: IB_Trading, ticker: str, direccion: str, contrato: Contract) -> None:
    
    """
    Revisa y gestiona las órdenes abiertas para un activo específico.
    
    La función primero revisa si hay órdenes para el activo especificado. Si no hay órdenes abiertas,
    genera una nueva orden de mercado en la dirección especificada. Si ya existen órdenes abiertas y la dirección
    actual es opuesta a la dirección de las órdenes abiertas, cancela las órdenes existentes y coloca una nueva
    orden en la dirección especificada.
    """
    
    # Obtener Órdenes
    ordenes = IB_app.reqAllOpenOrders()
    if isinstance(ordenes, pd.DataFrame):
        ordenes = ordenes[ordenes["activo"] == ticker]
        # Abrir Posición
        if len(ordenes) == 0:
            ejecutar_orden(IB_app=IB_app, ticker=ticker, contrato=contrato, direccion=direccion)
        else:
            posicion_actual = ordenes["posiscion"].iloc[0]
            if (direccion == "BUY" and posicion_actual == "SELL") or (direccion == "SELL" and posicion_actual == "BUY"):
                IB_app.cancelOrder(orderId=ordenes["orderId"].iloc[0])
                ejecutar_orden(IB_app=IB_app, ticker=ticker, contrato=contrato, direccion=direccion)
                
# Ejecutar Sistema:
    
# Crear Contrato
contrato = Contract()
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Iterar hasta que cierre el mercado
while True:
    # Revisar si se han generado señales para cada ticker
    for ticker in tickers:
        contrato.symbol = ticker
        df = IB_app.reqHistoricalData(reqId=0, contract=contrato, durationStr=tiempo_descargado, barSizeSetting=marco_tiempo)
        # Detectar Cruces
        cma = Cruce_MA(df=df, tendencia_rapida=9, tendencia_lenta=21)
        # Revisar si se generó una señal en la última vela
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
                
    # Definir horario de Nueva York (Para Cesar Ejecución)
    ny = pytz.timezone("America/New_York")
    hora_ny = datetime.now(tz=ny)
    hora_ny = hora_ny.replace(hour=15, minute=58, second=0, microsecond=0)
    horario_cierre = hora_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    
    # Cerrar Posiciones si ya no se puede realizar otra iteración: Las posiciones se cerrarán 1 minuto antes de que el mercado cierre.
    if (hora_ny + timedelta(hours=1)) > horario_cierre:
        # Pausar la ejecución del código hasta un minuto antes del cierre del mercado
        hora_cierre_menos_un_minuto = horario_cierre - timedelta(minutes=1)
        tiempo_dormir = (hora_cierre_menos_un_minuto - hora_ny).total_seconds()
        time.sleep(tiempo_dormir)
        # Cerrar Todo
        IB_app.end_session(account="No. Cuenta", close_orders=True, close_positions=True)
        # Terminar Bucle
        break
    else:
        # Mostrar en consola
        print("Código dormirá por 1 hora...")
        time.sleep(60 * 60)
        
# Esperar 1 minuto y desconectar al Servidor
time.sleep(60)
IB_app.disconnect()
