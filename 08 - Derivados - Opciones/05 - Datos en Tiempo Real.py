# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd
import time
from datetime import datetime, timedelta

# Clase que extrae datos en tiempo real para las Opciones
class IB_TiempoRealOpciones(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y solicita datos en tiempo real para las Opciones
    """
    
    def __init__(self):
        
        """
        Constructor de la clase
        """
        
        EClient.__init__(self, self)
        self.datos_tiempo_real = {}
        self.evento = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Se llama cuando se obtiene un ID válido para una orden
        """
        
        self.evento.set()
        
        
    def tickPrice(self, reqId, tickType, price, attrib):
        
        """
        Se llama cada vez que se recibe un precio de tick
        """
        
        if reqId not in self.datos_tiempo_real:
            self.datos_tiempo_real[reqId] = []
            
        self.datos_tiempo_real[reqId].append({"TickType": tickType, "Price": price})
        print(f"Datos en Tiempo Real. ReqId: {reqId}, TickType: {tickType}, Precio: {price}")
        
    
    def tickSize(self, reqId, tickType, size):
        
        """
        Se llama cada vez que se recibe un tamaño de tick
        """
        
        print(f"Tamaño de Ticks. ReqId: {reqId}, TickType: {tickType}, Tamaño: {size}")
        
        
# Establecer Conexión
IB_conexion = IB_TiempoRealOpciones()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
thread = threading.Thread(target=IB_conexion.run)
thread.start()
IB_conexion.evento.wait()
IB_conexion.evento.clear()
        
# Crear contrato
contrato = Contract()
contrato.symbol = "AAPL"
contrato.secType = "OPT"
contrato.exchange = "SMART"

# Definir una fecha (Viernes siguiente semana)
fecha_hoy = datetime.now()
dias_rest = (4 - fecha_hoy.weekday()) + 7
viernes_siguiente = (fecha_hoy + timedelta(days=dias_rest)).strftime("%Y%m%d")

contrato.lastTradeDateOrContractMonth = viernes_siguiente
contrato.strike = 230
contrato.right = "C"
contrato.multiplier = "100"     
        
# Solicitar Datos en Tiempo Real
IB_conexion.reqMarketDataType(marketDataType=3)
IB_conexion.reqMktData(reqId=1, contract=contrato, genericTickList="", snapshot=False, regulatorySnapshot=False, mktDataOptions=[])
time.sleep(10)
IB_conexion.cancelMktData(reqId=1)
time.sleep(1)        
        
# Convertir a DataFrame
df_tiempo_real = pd.DataFrame(IB_conexion.datos_tiempo_real[1])      
print(df_tiempo_real)        
        
# Desconectar
IB_conexion.disconnect()       

# Recordatorio:
#   - IB cuenta con miles de contratos de opciones para activos muy líquidos y populares, por lo tanto,
#     cuando pidamos datos en tiempo real para un activo, asegúrate de especificar con precisión el contrato
#     que deseas (incluyendo strike price, fecha de expiración, tipo de opción, etc.).
