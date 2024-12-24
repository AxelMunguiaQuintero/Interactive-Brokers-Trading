# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

# Clase que Cancela Órdenes Pendientes
class IB_Cancelar_Ordenes(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y ejecuta/cancela órdenes en el mercado
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.order_id = None
        
        
    def nextValidId(self, orderId):
        
        """
        Obtiene el siguiente ID válido de la sesión
        """
        
        # Almacenar
        self.order_id = orderId
        
        
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, 
                    lastFillPrice, clientId, whyHeld, mktCapPrice):
        
        """
        Muestra el estado de una orden
        """
        
        print(f"Orden: {orderId} - Estado: {status}")
        
        
# Generar Conexión
IB_conn = IB_Cancelar_Ordenes()
IB_conn.connect(host="127.0.0.1", port=7497, clientId=1)
threading.Thread(target=IB_conn.run).start()
time.sleep(2)

# Definir contrato para la Orden
contrato = Contract() 
contrato.symbol = "AAPL"
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Crear una orden límite
orden = Order()
orden.orderId = IB_conn.order_id
orden.action = "BUY"
orden.orderType = "LMT" 
orden.totalQuantity = 100
orden.lmtPrice = 234
orden.eTradeOnly = ""
orden.firmQuoteOnly = ""
        
# Enviar Orden
id_orden = IB_conn.order_id
IB_conn.placeOrder(orderId=id_orden, contract=contrato, order=orden)        
print(f"Orden de compra ha sido enviada: ID {id_orden}")

# Cancelar Orden
IB_conn.cancelOrder(orderId=id_orden)        
        
# Desconectar
IB_conn.disconnect()      

# Recordatorio:
#   - Las órdenes solo se pueden cancelar si aún no han sido ejecutadas en el mercado. Si la orden ya ha sido parcialmente completada,
#     entonces solo se podrá cancelar la parte restante.
