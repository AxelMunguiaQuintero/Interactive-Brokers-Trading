# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd
import time

# Clase Datos Históricos con un correcto Procesamiento
class IB_Datos_Estructurados(EWrapper, EClient):
    
    """
    Clase que permite descargar Datos Históricos con Eventos.
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.datos = []
        self.historical_data_event = threading.Event()
        self.timestamp_event = threading.Event()
        
        
    def historicalData(self, reqId, bar):
        
        """
        Recibe y almacena los datos históricos
        """
        
        self.datos.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
        
        
    def historicalDataEnd(self, reqId, start, end):
        
        """
        Este método se manda a llamar una vez que se han recibido todos los datos
        """
        
        print("Todos los datos se han recibido. Desde {} hasta {} con el Id de Petición {}".format(start, end, reqId))
        # Convertir los Datos a DataFrame
        datos = pd.DataFrame(self.datos, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        datos["Date"] = pd.to_datetime(datos["Date"])
        datos.set_index("Date", inplace=True)
        self.datos = datos
        # Avisar que todos los datos se han recibido y procesado
        self.historical_data_event.set()
        
        
    def headTimestamp(self, reqId, headTimestamp):
        
        """
        Método que nos permite conocer la fecha más antigua de datos para un instrumento financiero.
        """
        
        print("La fecha más antigua disponible es:", headTimestamp)
        self.headTimestamp_dato = headTimestamp
        self.timestamp_event.set()
        
        
# Conectar
IB_conexion = IB_Datos_Estructurados()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=5)
thread = threading.Thread(target=IB_conexion.run)
thread.start()
time.sleep(2)

# Definir contrato
contrato = Contract()
contrato.symbol = "AAPL"
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Obtener fecha más antigua para un activo
IB_conexion.reqHeadTimeStamp(reqId=1, contract=contrato, whatToShow="ADJUSTED_LAST", useRTH=1, formatDate=1)
IB_conexion.timestamp_event.wait()
IB_conexion.timestamp_event.clear()
       
# Solicitar Datos
IB_conexion.reqMarketDataType(3)
IB_conexion.reqHistoricalData(reqId=1, contract=contrato, endDateTime="", durationStr="10 Y", barSizeSetting="1 day", 
                              whatToShow="ADJUSTED_LAST", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])
IB_conexion.historical_data_event.wait()
IB_conexion.historical_data_event.clear()

print(f"Datos históricos de {contrato.symbol}:\n", IB_conexion.datos)

# Desconectar
print("Thread Activo:", thread.is_alive())
IB_conexion.disconnect()        
print("Thread Activo:", thread.is_alive())
        
# Recordatorio:
#   - IB requiere que el proceso de extracción, procesamiento y almacenamiento de datos se gestione de manera eficiente para garantizar
#     que se obtengan los datos en tiempo real, minimizando la latencia y optimizando el uso de recursos de conexión.
