# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd
from datetime import datetime, timedelta
import time

# Clase que Obtiene los Contratos de Opciones para un Activo
class IB_Opciones_Contratos(EWrapper, EClient):
    
    """
    Clase para obtener contratos de opciones disponibles en IB
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        # Atributos
        self.contratos_info = []
        self.contratos_objetos = []
        self.precio_actual = ""
        self.evento = threading.Event()
        
        
    def contractDetails(self, reqId, contractDetails):
        
        """
        Recibe la información del contrato solicitado
        """
        
        # Almacenar
        self.contratos_objetos.append(contractDetails)
        self.contratos_info.append({
            
            "Instrumento": contractDetails.contract.symbol,
            "Precio de Ejercicio": contractDetails.contract.strike,
            "Tipo": contractDetails.contract.right,
            "Fecha de Vencimiento": contractDetails.contract.lastTradeDateOrContractMonth,
            "Multiplicador": contractDetails.contract.multiplier,
            "Exchange": contractDetails.contract.exchange,
            "SecType": contractDetails.contract.secType
            
            })
        
        
    def contractDetailsEnd(self, reqId):
        
        """
        Método que se manda a llamar una vez que han recibido todos los contratos
        """
        
        self.evento.set()
        
        
    def historicalData(self, reqId, bar):
        
        """
        Este método recibe el precio más reciente
        """
        
        # Almacenar el Precio
        self.precio_actual = bar.close
        
    
    def historicalDataEnd(self, reqId, start, end):
        
        """
        Método que se llama cuando todos los precios se han procesado
        """
        
        self.evento.set()
        
        
# Conexión
IB_conexion = IB_Opciones_Contratos()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
thread = threading.Thread(target=IB_conexion.run)
thread.start()
time.sleep(3)
        
# Definir una fecha (El Viernes de la siguiente semana)
fecha_actual = datetime.now()
dias_restantes = (4 - fecha_actual.weekday()) + 7
viernes_siguiente = (fecha_actual + timedelta(days=dias_restantes)).strftime("%Y%m%d")

# Crear Contrato
contrato = Contract()
contrato.symbol = "AMZN"
contrato.secType = "OPT"
contrato.exchange = "BOX" # Boston Options Exchange
contrato.currency = "USD"
contrato.lastTradeDateOrContractMonth = viernes_siguiente

# Realizar Petición
IB_conexion.reqContractDetails(reqId=0, contract=contrato) 
IB_conexion.evento.wait()
IB_conexion.evento.clear()
        
# Opciones Disponibles
pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", None)
opciones_disponibles = pd.DataFrame(IB_conexion.contratos_info).set_index("Instrumento")
print(opciones_disponibles)        

# Nuevo Contrato
contrato = Contract()
contrato.symbol = "AMZN"
contrato.secType = "STK"
contrato.exchange = "SMART" 
contrato.currency = "USD" 
IB_conexion.reqHistoricalData(reqId=0, contract=contrato, endDateTime="", durationStr="1 D", barSizeSetting="1 day", whatToShow="ADJUSTED_LAST", 
                              useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])
IB_conexion.evento.wait()
IB_conexion.evento.clear()
print("Precio Actual:", IB_conexion.precio_actual)
        
# Calls
calls = opciones_disponibles[opciones_disponibles["Tipo"] == "C"].sort_values(by="Precio de Ejercicio")        
print("Strike más bajo Calls:", calls["Precio de Ejercicio"].min())        
print("Strike más alto Calls:", calls["Precio de Ejercicio"].max())        
# Obtener Call ATM
indice_atm_call = (calls["Precio de Ejercicio"] - IB_conexion.precio_actual).abs().argmin()
print("Strike ATM Call:", calls.iloc[indice_atm_call]["Precio de Ejercicio"])
        
# Puts
puts = opciones_disponibles[opciones_disponibles["Tipo"] == "P"].sort_values(by="Precio de Ejercicio")        
print("Strike más bajo Puts:", puts["Precio de Ejercicio"].min())        
print("Strike más alto Puts:", puts["Precio de Ejercicio"].max())        
# Obtener Put ATM
indice_atm_put = (puts["Precio de Ejercicio"] - IB_conexion.precio_actual).abs().argmin()
print("Strike ATM Put:", puts.iloc[indice_atm_put]["Precio de Ejercicio"])

# Recordatorio:
#   - Las Opciones ITM (In the Money) tienen un valor intrínseco positivo. Para una opción de compra, esto significa
#     que el precio del activo subyacente está por encima del precio de ejercicio. Para una opción de venta, está por debajo.
#   - Las Opciones OTM (Out the Money) no tienen valor intrínseco. Para una opción de compra, esto ocurre cuando el precio
#     del activo subyacente está por debajo del precio de ejercicio. Para una opción de venta, está por encima.
#   - Las Opciones ATM (At the Money) se consideran en el punto de equilibrio. Para ambas opciones de compra y venta, 
#     esto sucede cuando el precio del activo subyacente es igual o muy cercano al precio de ejercicio, resultando en un valor
#     intrínseco nulo.
