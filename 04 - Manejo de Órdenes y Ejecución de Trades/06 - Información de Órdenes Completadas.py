# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

# Clase que muestra información sobre las órdenes completadas
class IB_OrdenesCompletadas(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y extrae información de las órdenes completadas
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.ejecucion_evento = threading.Event()
        self.ordenes_completadas = []
        
        
    def nextValidId(self, orderId):
        
        """
        Recibe el próximo ID válido
        """
        
        self.next_order_id = orderId
        
        
    def completedOrder(self, contract, order, orderState):
        
        """
        Recibe detalles de una orden completada
        """
        
        print(f"Orden completada recibida: {contract.symbol}, Tipo: {order.orderType}")
        self.ordenes_completadas.append((contract, order, orderState))
        
        
    def completedOrdersEnd(self):
        
        """
        Se llama cuando todas las órdenes completadas se han recibido
        """
        
        print("Se recibieron todas las órdenes completadas")
        self.ejecucion_evento.set()
        

# Conectar al Servidor de la API
IB_con = IB_OrdenesCompletadas()
IB_con.connect(host="127.0.0.1", port=7497, clientId=12)
api_thread = threading.Thread(target=IB_con.run)
api_thread.start()

time.sleep(2)
        
# Definir el contrato para la orden
contrato = Contract()
contrato.symbol = "PYPL"
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Crear una orden de mercado
orden = Order()
orden.action = "BUY"
orden.orderType = "MKT"
orden.totalQuantity = 10
orden.eTradeOnly = ""
orden.firmQuoteOnly = ""

# Ejecutar Orden
IB_con.placeOrder(orderId=IB_con.next_order_id, contract=contrato, order=orden)
time.sleep(4)    
        
# Solicitar órdenes completadas
IB_con.ejecucion_evento.clear()
IB_con.reqCompletedOrders(apiOnly=True) # apiOnly=False para obtener órdenes completadas manualmente o desde otras plataformas
IB_con.ejecucion_evento.wait()
        
# Mostrar órdenes completadas
for contract, order, orderState in IB_con.ordenes_completadas:
    print(f"Símbolo: {contract.symbol}, Tipo de Orden: {order.orderType}, Acción: {order.action}, Estado: {orderState.status}")
        
# Desconectar
IB_con.disconnect()
api_thread.join()

# Recordatorio:
#   - Las órdenes completadas que se regresan son aquellas que han sido ejecutadas completamente, y pueden incluir tanto órdenes
#     enviadas por la API como manualmente desde otras plataformas si apiOnly=False.
