# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

# Clase que Modifica Órdenes Activas
class IB_ModificarOrdenes(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y ejecuta/modifica órdenes en el mercado
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.next_id = None
        self.order_filled = False # Para verificar si la orden fue llenada
        
        
    def nextValidId(self, orderId):
        
        """
        Método almacena el siguiente ID Válido
        """
        
        self.next_id = orderId
        
        
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, 
                    lastFillPrice, clientId, whyHeld, mktCapPrice):
        
        """
        Se llama cuando cambia el estado de la orden
        """
        
        # Guardar Estado
        if status == "Filled":
            self.order_filled = True
        print(f"Estado de la Orden {orderId}: {status}")
        
        
    def crear_contrato(self, symbol, secType, exchange, currency):
        
        """
        Crea un contrato básico
        """
        
        contrato = Contract()
        contrato.symbol = symbol
        contrato.secType = secType
        contrato.exchange = exchange
        contrato.currency = currency
        
        return contrato
    
    
    def crear_orden(self, action, orderType, quantity, price=None):
        
        """
        Crea una orden básica
        """
        
        orden = Order()
        orden.action = action
        orden.orderType = orderType
        orden.totalQuantity = quantity
        if price:
            orden.lmtPrice = price
        orden.eTradeOnly = ""
        orden.firmQuoteOnly = ""
        
        return orden
    
    
# Crear Instancia de la API
IB_app = IB_ModificarOrdenes()
IB_app.connect(host="127.0.0.1", port=7497, clientId=1)
threading.Thread(target=IB_app.run).start()
time.sleep(2)
        
# Generar Contrato
contrato = IB_app.crear_contrato(symbol="AMZN", secType="STK", exchange="SMART", currency="USD")    

# Crear una orden límite de compra
orden_compra = IB_app.crear_orden(action="BUY", orderType="LMT", quantity=10, price=205)        

# Enviar la orden inicial
IB_app.placeOrder(orderId=IB_app.next_id, contract=contrato, order=orden_compra)        

# Simular tiempo de espera antes de modificar la orden
time.sleep(5)

# Modificar la orden (Ejemplo: cambiar el precio límite)
if not IB_app.order_filled:        
    nueva_orden = IB_app.crear_orden(action="BUY", orderType="LMT", quantity=10, price=207)
    # Enviar la orden nueva
    IB_app.placeOrder(orderId=IB_app.next_id, contract=contrato, order=nueva_orden)
else:
    print("No se puede modificar la orden, ya fue llenada")

# Desconectar
IB_app.disconnect()    

# Recordatorio:
#   - Solo es posible modificar órdenes que aún no han sido completamente ejecutadas. Si la orden ya ha sido llenada parcialmente
#     o totalmente, no se podrán hacer cambios a la parte ya ejecutada.
