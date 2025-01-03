# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

# Clase para manejar múltiples órdenes de diferentes clientes
class IB_MultiCliente(EWrapper, EClient):
    
    """
    Clase que se conecta a IB.
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.next_order_id = None
        
        
    def nextValidId(self, orderId):
        
        """
        Llamado cuando se recibe el siguiente ID válido para una orden
        """
        
        self.next_order_id = orderId
        print(f"Cliente {self.clientId} - ID de Orden Inicial {orderId}")
        
        
    def crear_orden(self, contrato_argumentos: dict, orden_argumentos: dict):
        
        """
        Crea una orden de mercado para el cliente actual
        """
        
        # Definir el contrato
        contrato = Contract()
        contrato.symbol = contrato_argumentos.get("symbol", "AAPL")
        contrato.secType = contrato_argumentos.get("secType", "STK")
        contrato.currency = contrato_argumentos.get("currency", "USD")
        contrato.exchange = contrato_argumentos.get("exchange", "SMART")
        
        # Crear una orden de mercado
        orden = Order()
        orden.action = orden_argumentos.get("action", "BUY")
        orden.orderType = orden_argumentos.get("orderType", "LMT")
        orden.totalQuantity = orden_argumentos.get("totalQuantity", 100)
        orden.eTradeOnly = ""
        orden.firmQuoteOnly = ""
        if orden_argumentos.get("lmtPrice", False):
            orden.lmtPrice = orden_argumentos.get("lmtPrice")
            
        # Eviar Orden
        print(f"Cliente {self.clientId} - Enviando orden de compra para {contrato.symbol}")
        self.placeOrder(orderId=self.next_order_id, contract=contrato, order=orden)
        
        
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId,
                    lastFillPrice, clientId, whyHeld, mktCapPrice):
        
        """
        Muestra el estado de la orden
        """
        
        print(f"Cliente {self.clientId} - Estado de la Orden {orderId}: {status}, Llenado: {filled}")
        
        
    def openOrder(self, orderId, contract, order, orderState):
        
        """
        Muestra información sobre una orden abierta
        """
        
        print(f"Cliente {self.clientId} - Orden abierta {orderId} para {contract.symbol}. Estado: {orderState.status}")
        
        
    def openOrderEnd(self):
        
        """
        Llamado cuando se completa la solicitud de órdenes abiertas
        """
        
        print(f"Cliente {self.clientId} - Se recibieron todas las órdenes abiertas")
        
    
# Función para generar diferentes Clientes
def Inicializar_Cliente(cliente_id):
    
    """
    Genera diferentes instancias de clientes
    """
    
    IB_cliente = IB_MultiCliente()
    IB_cliente.connect(host="127.0.0.1", port=7497, clientId=cliente_id)
    api_thread = threading.Thread(target=IB_cliente.run)
    api_thread.start()
    
    # Esperar
    time.sleep(2)
    
    return IB_cliente

# Crear Clientes
cliente1 = Inicializar_Cliente(cliente_id=10)
cliente2 = Inicializar_Cliente(cliente_id=20)
        
# Ejecutar Orden Cliente 1
cliente1.crear_orden(contrato_argumentos={"symbol": "AAPL"}, orden_argumentos={"lmtPrice": 234.50})
time.sleep(2)
# Obtener Órdenes Abiertas
print("\n\nÓrdenes en espera:\n\n")
cliente1.reqOpenOrders()      
        
# Ejecutar Orden Cliente 2
cliente2.crear_orden(contrato_argumentos={"symbol": "AMZN"}, orden_argumentos={"lmtPrice": 205.50})
time.sleep(2)
# Obtener Órdenes Abiertas
print("\n\nÓrdenes en espera:\n\n")
cliente2.reqOpenOrders()      
             
# Obtener órdenes abiertas de toda la cuenta
cliente1.reqAllOpenOrders()    
        
# Desconectar 
cliente1.disconnect()        
cliente2.disconnect()        

# Recordatorio:
#   - Las órdenes enviadas con clientes diferentes son gestionadas de forma independiente. Esto nos permite tener un mayor control
#     en nuestro sistema de trading, si generamos diferentes clientes para diferentes propósitos (estrategias, activos, marcos de
#     tiempo, etc.).
