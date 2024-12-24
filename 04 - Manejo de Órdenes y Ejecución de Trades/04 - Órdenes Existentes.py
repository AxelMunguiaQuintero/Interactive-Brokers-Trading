# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

# Clase que Solicita las Órdenes Abiertas
class IB_InformacionOrdenes(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y solicita las órdenes existentes del cliente
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.evento = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Método llamado cuando se recibe el siguiente Id válido para nuestras órdenes
        """
        
        self.next_order_id = orderId
        
        
    def openOrder(self, orderId, contract, order, orderState):
        
        """
        Método llamado cuando se recibe información de una orden abierta
        """
        
        print(f"Orden {orderId}: {order.action} {order.totalQuantity} de {contract.symbol} a {order.lmtPrice if order.orderType == 'LMT' else 'precio de mercado'}")
        print(f"Estado: {orderState.status}")
        
    
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, 
                    clientId, whyHeld, mktCapPrice):
        
        """
        Muestra el estado actual de la orden
        """
        
        print(f"Estado de la Orden {orderId}: {status}, Llenado: {filled}, Restante: {remaining}, Precio Promedio: {avgFillPrice}")
        
    
    def openOrderEnd(self):
        
        """
        Llamado cuando se han recibido todas las órdenes que siguen abiertas
        """
        
        self.evento.set()
        print("Fin de la lista de órdenes abiertas")
        
        
# Conectar
IB_conexion = IB_InformacionOrdenes()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_conexion.run)
api_thread.start()
time.sleep(2)
        
# Definir el contrato para nuestra orden
contrato = Contract()
contrato.symbol = "TSLA"
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Crear una orden de tipo límite
orden = Order()
orden.action = "BUY"
orden.orderType = "LMT"
orden.totalQuantity = 100
orden.lmtPrice = 331
orden.eTradeOnly = ""
orden.firmQuoteOnly = ""
 
# Ejecutar Orden
IB_conexion.placeOrder(orderId=IB_conexion.next_order_id, contract=contrato, order=orden)
        
time.sleep(2)

# Obtener información de nuestras órdenes
print("\n\nInicio de Órdenes Existentes:\n\n")
IB_conexion.reqOpenOrders()
IB_conexion.evento.wait()       
        
# Desconectar
IB_conexion.disconnect()
api_thread.join()

# Recordatorio:
#   - Al consultar las órdenes abiertas, podrás ver tanto el estado actual de las órdenes enviadas como la cantidad de activos comprados
#     o vendidos.
#   - Al enviar una orden límite, asegúrate de que el precio límite no exceda el 3% del valor total del activo; de lo contrario,
#     podrás recibir un error desde el servidor.
