# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading
import time

# Clase Múltiples Datos Históricos
class IB_Datos_Instrumentos(EWrapper, EClient):
    
    """
    Clase que permite descargar datos históricos para múltiples tickers.
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.datos = {}
        
        
    def historicalData(self, reqId, bar):
        
        """
        Método recibe y almacena los datos históricos
        """
        
        # Crear llave si no existe
        if reqId not in self.datos:
            self.datos[reqId] = []
        # Almacenar
        self.datos[reqId].append({"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, 
                                   "Close": bar.close, "Volume": bar.volume})
        

# Definir contrato
contrato = Contract()
contrato.symbol = "AAPL"
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Conectar
IB_conexion = IB_Datos_Instrumentos()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
threading.Thread(target=IB_conexion.run).start()

# Esperar Conexión
time.sleep(3)

# Obtener Datos
IB_conexion.reqMarketDataType(3)
IB_conexion.reqHistoricalData(reqId=1, contract=contrato, endDateTime="", durationStr="5 Y", barSizeSetting="1 week", 
                              whatToShow="TRADES", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])
time.sleep(2)
df_apple = pd.DataFrame(IB_conexion.datos[1]).set_index("Date")
print(df_apple)

# Obtener Datos para otro activo con diferente intervalo
contrato.symbol = "AMZN"
IB_conexion.reqHistoricalData(reqId=2, contract=contrato, endDateTime="", durationStr="2000 S", barSizeSetting="1 secs", 
                              whatToShow="TRADES", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])
time.sleep(4)
df_amzn = pd.DataFrame(IB_conexion.datos[2]).set_index("Date")
print(df_amzn)

# Obtener Datos para otro activo en diferentes intervalos y con diferentes precios
contrato.symbol = "TSLA"
IB_conexion.reqHistoricalData(reqId=3, contract=contrato, endDateTime="", durationStr="1 D", barSizeSetting="1 min", 
                              whatToShow="ADJUSTED_LAST", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])
time.sleep(3)
df_tsla = pd.DataFrame(IB_conexion.datos[3]).set_index("Date")
print(df_tsla)

# Intentar Obtener Datos que requieren suscripción
contrato.symbol = "NFLX"
IB_conexion.reqHistoricalData(reqId=4, contract=contrato, endDateTime="", durationStr="2000 S", barSizeSetting="1 secs", 
                              whatToShow="MIDPOINT", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])
time.sleep(2)

try:
    df_nflx = pd.DataFrame(IB_conexion.datos[4]).set_index("Date")
    print(df_nflx)
except:
    print("No hay datos descargados para este ID")

# Recordatorio:
#   - IB permite trabajar con diferentes ventanas de tiempo, desde segundos hasta años, lo que facilita el 
#     análisis de tendencias macroeconómicas y estrategias de trading intradía, adaptando el estudio de datos
#     a distintos horizontes temporales y objetivos financieros.
