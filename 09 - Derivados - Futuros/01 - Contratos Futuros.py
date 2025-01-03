# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from datetime import datetime
import threading

# Clase para extraer información de contratos de Futuros
class IB_InfoContratos(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y solicita información básica de un contrato de futuros
    """
    
    def __init__(self):
        
        """
        Constructor de la clase
        """
        
        EClient.__init__(self, self)
        self.evento = threading.Event()
        self.contrato_detalles = None
        
        
    def nextValidId(self, orderId):
        
        """
        Se llama cuando se obtiene un ID válido para una orden
        """
        
        print("ID de orden válida:", orderId)
        self.evento.set()
        
        
    def contractDetails(self, reqId, contractDetails):
        
        """
        Se llama cuando se reciben los detalles del contrato
        """
        
        # Almacenar
        self.contrato_detalles = contractDetails
        print("Detalles del contrato recibido:")
        print(f" - Símbolo: {contractDetails.contract.symbol}")
        print(f" - Tipo: {contractDetails.contract.secType}")
        print(f" - Mercado: {contractDetails.contract.exchange}")
        print(f" - Moneda: {contractDetails.contract.currency}")
        print(f" - Fecha de Vencimiento: {contractDetails.contract.lastTradeDateOrContractMonth}")

    
    def contractDetailsEnd(self, reqId):
        
        """
        Método que se llama cuando toda la información ha sido procesada
        """
        
        self.evento.set()
        
        
# Establecer Conexión
IB_conexion = IB_InfoContratos()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
thread = threading.Thread(target=IB_conexion.run)
thread.start()
IB_conexion.evento.wait()
IB_conexion.evento.clear()
        
# Crear Contrato del Futuro
contrato = Contract()
contrato.symbol = "CL" # Futuros de Petróleo Crudo
contrato.secType = "FUT"
contrato.exchange = "NYMEX" 
contrato.currency = "USD"

# Obtener el mes siguiente para el contrato
fecha_actual = datetime.now()
# Agregar un mes
if fecha_actual.month == 12: 
    mes_siguiente = fecha_actual.replace(year = fecha_actual.year + 1, month=1).strftime("%Y%m")
else:
    mes_siguiente = fecha_actual.replace(month = fecha_actual.month + 1).strftime("%Y%m")
contrato.lastTradeDateOrContractMonth = mes_siguiente

# Solicitar detalles
IB_conexion.reqContractDetails(reqId=0, contract=contrato)
IB_conexion.evento.wait()

# Detalles del Contrato
print("Contrato:", IB_conexion.contrato_detalles)
        
# Desconectar
IB_conexion.disconnect()       

# Recordatorio:
#   - La fecha de vencimiento de los contratos de futuros puede ser confusa, ya que la negociación activa generalmente
#     cesa en el mes anterior. Esto permite a los inversionistas ajustar sus posiciones y evitar la entrega física del activo
#     subyacente.
