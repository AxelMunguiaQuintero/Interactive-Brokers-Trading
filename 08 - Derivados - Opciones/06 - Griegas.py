# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd
from datetime import datetime, timedelta
import time

# Clase que extrae el cálculo de las griegas para una opción
class IB_Greeks(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y solicita las griegas para un activo.
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.griegas = {}
        self.evento = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Se llama cuando se obtiene el siguiente ID válido
        """
        
        self.evento.set()
        
        
    def tickOptionComputation(self, reqId, tickType, tickAttrib, impliedVol, delta, optPrice, 
                              pvDividend, gamma, vega, theta, undPrice):
        
        """
        Se llama cuando se reciben las griegas para una opción.
        """
        
        if reqId not in self.griegas:
            self.griegas[reqId] = []
            
        self.griegas[reqId].append({
            
            "tickType": tickType, # Tipo de tick recibido (por ejemplo, precio o tamaño)
            "Implied Volatility": impliedVol, # Volatilidad Implícita de la Opción,
            "Delta": delta, # Sensibilidad del precio de la opción a cambios en el precio del activo subyacente
            "Option Price": optPrice, # Precio actual de la opción en el mercado,
            "PV Dividend": pvDividend, # Valor Presente de los dividendos esperados durante la vida de la opción
            "Gamma": gamma, # Sensibilidad del delta de la opción a cambios en el precio del activo subyacente
            "Vega": vega, # Sensibilidad del precio de la opción a cambios en la volatilidad del activo subyacente,
            "Theta": theta, # Tasa de disminución del valor temporal de la opción,
            "Underlying Price": undPrice, # Precio del activo subyacente, que es el activo sobre el que se basa la opción
            
            })
        
        print(f"Griegas recibidas. ReqId: {reqId}, Griegas: {self.griegas[reqId][-1]}")
        
    
# Establecer Conexión
IB_conexion = IB_Greeks()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
hilo = threading.Thread(target=IB_conexion.run)
hilo.start()
IB_conexion.evento.wait()
IB_conexion.evento.clear()

# Crear contrato
contrato = Contract()
contrato.symbol = "AAPL"
contrato.secType = "OPT"
contrato.exchange = "SMART"

# Definir fecha (viernes próximo)
hoy = datetime.now()
dias_faltantes = (4 - hoy.weekday()) + 7
viernes_prox = (hoy + timedelta(days=dias_faltantes)).strftime("%Y%m%d")

contrato.lastTradeDateOrContractMonth = viernes_prox
contrato.strike = 230
contrato.right = "C" 
contrato.multiplier = "100"

# Solicitar Griegas
IB_conexion.reqMarketDataType(marketDataType=3)
IB_conexion.reqMktData(reqId=1, contract=contrato, genericTickList="100", snapshot=False, regulatorySnapshot=False, mktDataOptions=[])
time.sleep(10)
IB_conexion.cancelMktData(reqId=1)    
        
# Convertir a DataFrame
df_griegas = pd.DataFrame(IB_conexion.griegas[1])      
print(df_griegas)        
        
# Desconectar
IB_conexion.disconnect()

# Recordatorio:
#   - La Volatilidad Implícita refleja las expectativas sobre la volatiliad futura del activo subyacente,
#     afectando directamente el precio de la opción.
#   - La Griega Delta mide la sensibilidad del precio de la opción a cambios en el precio del activo subyacente.
#   - La Griega Gamma mide la tasa de cambio del delta, informando sobre la convexidad de la relación entre el precio
#     del activo y la opción.
#   - La Griega Vega evalúa la sensibilidad del precio de la opción a cambios en la volatilidad del activo subyacente.
#   - La Griega Theta representa la disminución del valor temporal de la opción, indicando cómo el tiempo afecta su precio
#     a medidaa que se acerca la expiración.
