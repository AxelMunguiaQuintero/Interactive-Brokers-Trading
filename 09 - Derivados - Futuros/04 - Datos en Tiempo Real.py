# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd
from datetime import datetime
import time

# Clase para extraer datos en tiempo real de futuros
class IB_TiempoRealFuturos(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y solicita datos en tiempo real para futuros.
    """
    
    def __init__(self):
        
        """
        Constructor de la clase
        """
        
        EClient.__init__(self, self)
        self.datos_futuros = {}
        self.evento = threading.Event()
        
        
    def tickPrice(self, reqId, tickType, price, attrib):
        
        """
        Se llama cada vez que se recibe un precio de tick
        """
        
        if reqId not in self.datos_futuros:
            self.datos_futuros[reqId] = []
        self.datos_futuros[reqId].append({"TickType": tickType, "Price": price})
        print(f"Datos en tiempo real. ReqId: {reqId}, TickType: {tickType}, Precio: {price}")
        
        
        
    def tickSize(self, reqId, tickType, size):
        
        """
        Se llama cada vez que se recibe un tamaño de tick
        """
        
        print("Tamaño de tick. ReqId: {}, TickType: {}, Tamaño: {}".format(reqId, tickType, size))
        
        
# Establecer Conexión
IB_conexion = IB_TiempoRealFuturos()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
thread = threading.Thread(target=IB_conexion.run)
thread.start()
time.sleep(3)
        
# Crear Contrato del Futuro
contrato = Contract()
contrato.symbol = "ES"
contrato.secType = "FUT"
contrato.exchange = "CME"
contrato.currency = "USD"

# Obtener el siguiente trimestre más cercano
def siguiente_vencimiento():

    """
    Calcula el siguiente vencimiento más cercano de los contratos de futuros trimestrales. 
    """     
    
    # Fecha actual
    fecha_actual = datetime.now()
    
    # Vencimientos trimestrales: marzo, junio, septiembre y diciembre
    vencimientos = [
        
        datetime(fecha_actual.year, 3, 1),
        datetime(fecha_actual.year, 6, 1),
        datetime(fecha_actual.year, 9, 1),
        datetime(fecha_actual.year, 12, 1)
    
        ]
        
    # Filtrar vencimientos que ya han pasado
    vencimientos_futuros = [v for v in vencimientos if v > fecha_actual]
    
    # Si no hay vencimientos en el año actual, agregar el primer vencimiento del próximo año
    if len(vencimientos_futuros) == 0:
        return datetime(fecha_actual.year + 1, 3, 1).strftime("%Y%m")
    
    # Obtener el siguiente vencimiento
    siguiente_vencimiento = min(vencimientos_futuros)
    
    return siguiente_vencimiento.strftime("%Y%m")


contrato.lastTradeDateOrContractMonth = siguiente_vencimiento()
        
# Realizar Petición de Datos en Tiempo Real
IB_conexion.reqMarketDataType(marketDataType=3)
IB_conexion.reqMktData(reqId=1, contract=contrato, genericTickList="", snapshot=False,
                       regulatorySnapshot=False, mktDataOptions=[])
time.sleep(10)
IB_conexion.cancelMktData(reqId=1)

time.sleep(1)
        
# Converti datos a DataFrame
df_futuros = pd.DataFrame(IB_conexion.datos_futuros[1])       
print(df_futuros)        

# Desconectar
IB_conexion.disconnect()        
        
# Recordatorio:
#   - Hay distintos tipos de contratos de futuros con vencimientos mensuales, trimestrales y anuales. Esta variedad
#     nos permite a los traders gestionar riesgos y ajustar posiciones según sus estrategias de inversión, ya sea
#     para cobertura, especulación o planificación a corto y largo plazo.
