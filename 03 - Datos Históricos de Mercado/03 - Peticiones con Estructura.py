# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd
import time

# Clase Datos Históricos con Estructura
class IB_Datos_Estucturados(EWrapper, EClient):
    
    """
    Clase que permite descargar datos históricos estructurados.
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.data = []
        
    
    def historicalData(self, reqId, bar):
        
        """
        Este método recibe y almacena los datos históricos enviados por el Servidor
        """
        
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
        
    
    def historicalDataEnd(self, reqId, start, end):
        
        """
        Este método se manda a llamar una vez que se han recibido todos los datos.
        """
        
        print(f"Fin de los datos históricos. Desde {start} hasta {end} de petición: {reqId}")
        # Convertir datos a DataFrame
        self.data = pd.DataFrame(self.data, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        self.data.set_index("Date", inplace=True)
        self.data.index = pd.to_datetime(self.data.index)
        
    
# Conectar
IB_conn = IB_Datos_Estucturados()
IB_conn.connect(host="127.0.0.1", port=7497, clientId=1)
thread = threading.Thread(target=IB_conn.run)
thread.start()

# Esperar Conexión
time.sleep(2)

# Definir Contrato
contrato = Contract()
contrato.symbol = "AMD"
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Solicitar Datos
IB_conn.reqMarketDataType(3)
IB_conn.reqHistoricalData(reqId=1, contract=contrato, endDateTime="", durationStr="5 Y", barSizeSetting="1 day",
                          whatToShow="TRADES", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])

time.sleep(2)
print("Datos:\n", IB_conn.data) 
        
# Recordatorio:
#   - Las peticiones de IB utilizan múltiples métodos que coordinan la transmisión y finalización de la descarga. Un método gestiona
#     la recepción de datos en tiempo real, mientras que otro señala el cierre del proceso de entrega.
