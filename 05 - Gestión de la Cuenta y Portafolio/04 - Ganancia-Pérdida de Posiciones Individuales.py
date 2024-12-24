# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.order import Order
from ibapi.contract import Contract
import threading
import time

# Clase que obtiene la Ganancia/Pérdida de una posición en específico
class IB_GananciaPerdida_Individual(EClient, EWrapper):
    
    """
    Clase que establece una conexión a la API de IB y obtiene las ganancias o pérdidas de posiciones específicas
    """
    
    def __init__(self):
        
        """
        Constructor.
        """
        
        # Inicializar Cliente 
        EClient.__init__(self, self)
        self.pnl_individual = {}
        self.next_order_id = None
        self.evento_conexion = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Método que se llama cuando se recibe el próximo ID válido de la API.
        """
        
        self.next_order_id = orderId
        self.evento_conexion.set()
        
        
    def pnlSingle(self, reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value):
        
        """
        Método que recibe la PnL de un solo instrumento y almacena la información.
        """
        
        # Almacenar datos y mostrarlos por consola
        self.pnl_individual[reqId] = {
            
            "ID de Solicitud": reqId,
            "Ganancia/Pérdida Diaria": dailyPnL,
            "Ganancia/Pérdida No Realizada": unrealizedPnL,
            "Ganancia/Pérdida Realizada": realizedPnL,
            "Valor de Mercado": value
            
        }
        texto = ("ID Solicitud: {} ".format(reqId) + \
                 "Ganancia/Pérdida Diaria: {} ".format(dailyPnL))
        print(texto)
          
    
    def contractDetails(self, reqId, contractDetails):
        
        """
        Método que recibe los detalles del contrato
        """
        
        self.contrato_detalles = contractDetails
        
        
    def ejecutar_operacion(self, instrumento):
       
        """
        Método para abrir una posición en un instrumento.
        """
        
        # Crear contrato
        contrato = Contract()
        contrato.symbol = instrumento
        contrato.secType = "STK"
        contrato.exchange = "SMART"
        contrato.currency = "USD"
        # Crear Orden de Mercado
        orden = Order()
        orden.action = "BUY" 
        orden.orderType = "MKT"
        orden.totalQuantity = 100
        orden.eTradeOnly = ""
        orden.firmQuoteOnly = ""
        # Enviar orden
        self.placeOrder(orderId=self.next_order_id, contract=contrato, order=orden)
        # Almacenar Valores
        self.ordenes = [contrato, orden, self.next_order_id]
        self.reqIds(-1)
        

# Conectarse a la API
IB_conexion = IB_GananciaPerdida_Individual()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_conexion.run)
api_thread.start()       
# Esperar conexión
IB_conexion.evento_conexion.wait()
IB_conexion.evento_conexion.clear()

# Abrir Operación
ticker = "DIS"
IB_conexion.ejecutar_operacion(instrumento=ticker)
time.sleep(3)

# Obtener Ganancia/Pérdida
detalles_contrato = IB_conexion.reqContractDetails(reqId=0, contract=IB_conexion.ordenes[0])
time.sleep(1)
id_contrato = IB_conexion.contrato_detalles.contract.conId
IB_conexion.reqPnLSingle(reqId=1, account="DU5375084", modelCode="", conid=id_contrato)

# Esperar antes de cancelar suscripción
time.sleep(10)

# Cancelar Actualizaciones
IB_conexion.cancelPnLSingle(reqId=1)

# Cancelar Nuevamente
try:
    IB_conexion.cancelPnLSingle(reqId=1)
except Exception as error:
    print(error)

# Mostrar Datos Almacenados
print(IB_conexion.pnl_individual[1])
#- [Comentar]
#- Ya nada más agreguemos el recordatorio...

# Desconectar del Servidor
IB_conexion.disconnect()

# Recordatorio:
#   - El PnL Individual nos permite monitorear las ganancias o pérdidas específicas de una posición abierta en un 
#     instrumento financiero particular.
#   - Este monitoreo puede realizarse en tiempo real, recibiendo actualizaciones continuas mientras la posición está abierta.
#   - Es importante recordar que, si ya tenemos posiciones abiertas en el mismo instrumento, el PnL que recibimos corresponde
#     al conjunto de todas las posiciones abiertas en dicho instrumento, no solo a la nueva operación.
