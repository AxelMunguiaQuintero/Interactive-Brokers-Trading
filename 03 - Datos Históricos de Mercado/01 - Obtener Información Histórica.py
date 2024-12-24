# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading 
import time

# Clase Datos Históricos
class IB_Datos(EClient, EWrapper):
    
    """
    Clase que permite descargar datos históricos.
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.data = []
        
        
    # Método llamado cuando se recibe un dato histórico
    def historicalData(self, reqId, bar):
        
        """
        Este método recibe y almacena los datos históricos.
        """
        
        print(f"Fecha: {bar.date}, Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}, Volume: {bar.volume}")
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
        
    
    # Método llamado cuando se recibe la hora del servidor
    def currentTime(self, time):
        
        """
        Obtiene la hora del servidor
        """
        
        self.server_time = time
        
        
# Función para crear contratos para un activo
def crear_contrato(simbolo, tipo="STK", exchange="SMART", currency="USD"):
    
    """
    Función que genera un contrato
    """
    
    contrato = Contract()
    contrato.symbol = simbolo
    contrato.secType = tipo
    contrato.exchange = exchange
    contrato.currency = currency
    
    return contrato

# Conectar a IB
IB_conn = IB_Datos()
IB_conn.connect(host="127.0.0.1", port=7497, clientId=1)
# Gestionar Conexión
threading.Thread(target=IB_conn.run).start()
# Esperar Conexión
time.sleep(3)
        
# Obtener Contrato
contrato = crear_contrato(simbolo="AAPL")      

# Obtener Hora del Servidor
IB_conn.reqCurrentTime()        
hora_legible = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(IB_conn.server_time))
print(hora_legible)        

# IB_conn.reqMarketDataType(1) # Datos en Tiempo Real
IB_conn.reqMarketDataType(3) # Datos Retrasados (10 a 20 Minutos)        

IB_conn.reqHistoricalData(reqId=0, contract=contrato, endDateTime="", durationStr="5 Y", barSizeSetting="1 day", whatToShow="TRADES", 
                          useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])

time.sleep(3)        
        
# Convertir a DatFrame
df = pd.DataFrame(IB_conn.data, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
df["Date"] = pd.to_datetime(df["Date"])
df = df.set_index("Date")        
print(df)        
        
# Recordatorio:    
#   - Los Datos Históricos no se envían en un solo bloque, sino que llegan de manera incremental, registro por registro,
#     lo que optimiza la transferencia de grandes volúmenes de datos.
