# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd
from datetime import datetime, timedelta

# Clase que extrae datos históricos para Opciones
class IB_HistoricosOpciones(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y solicita datos históricos para Opciones.
    """
    
    def __init__(self):
        
        """
        Constructor de la clase
        """
        
        EClient.__init__(self, self)
        self.datos_historicos = {}
        self.evento = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Se llama cuando se obtiene un ID válido para una orden
        """
        
        print("Id de la orden válida:", orderId)
        self.evento.set()
        
        
    def historicalData(self, reqId, bar):
        
        """
        Método que recibe y procesa los datos históricos.
        """
        
        # Agregar Clave
        if reqId not in self.datos_historicos:
            self.datos_historicos[reqId] = []
            
        # Almacenar
        self.datos_historicos[reqId].append({"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low,
                                             "Close": bar.close, "Volume": bar.volume})
        
        
    def historicalDataEnd(self, reqId, start, end):
        
        """
        Se llama al final de la recepción de los datos históricos
        """
        
        print("Datos Históricos se han recibido")
        self.evento.set()
        
        
# Establecer Conexión
IB_conexion = IB_HistoricosOpciones()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
thread = threading.Thread(target=IB_conexion.run)
thread.start()
IB_conexion.evento.wait()
IB_conexion.evento.clear()
        
# Definir una fecha (del viernes de la próxima semana a la que sigue)
fecha_actual = datetime.now()
dias_restantes = (4 - fecha_actual.weekday()) + 7 * 2
viernes_siguiente_siguiente = (fecha_actual + timedelta(days=dias_restantes)).strftime("%Y%m%d")

# Crear Contrato de Opción
contrato = Contract()
contrato.symbol = "AAPL"
contrato.secType = "OPT"
contrato.exchange = "SMART"
contrato.lastTradeDateOrContractMonth = viernes_siguiente_siguiente
contrato.strike = 230
contrato.right = "C"
contrato.multiplier = "100" 

# Solicitar datos históricos
IB_conexion.reqMarketDataType(marketDataType=3)
IB_conexion.reqHistoricalData(reqId=1, contract=contrato, endDateTime="", durationStr="10 D", barSizeSetting="1 min",
                              whatToShow="TRADES", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[]) 
IB_conexion.evento.wait()      
        
# Convertir Datos a DataFrame de Pandas
df_historicos = pd.DataFrame.from_dict(IB_conexion.datos_historicos[1])      
print(df_historicos)        
        
# Desconectar
IB_conexion.disconnect()      

# Recordatorio:
#   - Para acceder a los datos históricos completos y en tiempo real de Opciones en IB, es necesario tener suscripciones
#     activas a datos de mercado específicos de opciones.
