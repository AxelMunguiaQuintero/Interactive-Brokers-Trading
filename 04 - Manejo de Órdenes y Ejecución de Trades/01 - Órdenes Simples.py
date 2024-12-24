# -*- coding: utf-8 -*-
# Importar librerías
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

# Clase que Ejecuta Órdenes en el Mercado
class IB_Ordenes(EClient, EWrapper):
    
    """
    Clase que se conecta a IB y ejecuta órdenes en el mercado
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.nextid_evento = threading.Event()
        self.next_order_id = None
        
    
    def nextValidId(self, orderId):
        
        """
        Recibe el próximo ID válido para una orden
        """
        
        # Almacenar
        self.next_order_id = orderId
        self.nextid_evento.set()
        
        
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, 
                    clientId, whyHeld, mktCapPrice):
        
        """
        Monitorea el estado de la orden
        """
        
        print(f"Estado de la Orden {orderId}: {status}, Llenado: {filled}, Faltante: {remaining}, Precio Promedio: {avgFillPrice}")
        
        
# Crear Contratos
def crear_contrato(symbol, sec_type="STK", exchange="SMART", currency="USD"):
        
    """
    Crea el contrato del activo a negociar
    """
    
    contrato = Contract()
    contrato.symbol = symbol
    contrato.secType = sec_type
    contrato.exchange = exchange
    contrato.currency = currency
    
    return contrato

# Crear Orden
def crear_orden(action, quantity, order_type="MKT"):

    """
    Crea una orden de compra o venta de mercado
    """        
    
    orden = Order()
    orden.action = action
    orden.totalQuantity = quantity
    orden.orderType = order_type
    orden.eTradeOnly = ""
    orden.firmQuoteOnly = ""
    
    return orden

# Generar Conexión
IB_conexion = IB_Ordenes()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
threading.Thread(target=IB_conexion.run).start()
IB_conexion.nextid_evento.wait()

# Crear contrato
contrato = crear_contrato("AAPL")

# Crear una orden de compra de 10 acciones
orden_compra = crear_orden(action="BUY", quantity=10, order_type="MKT")
print(orden_compra)

# Ejecutar Orden (Compra)
IB_conexion.placeOrder(orderId=IB_conexion.next_order_id, contract=contrato, order=orden_compra)

# Crear una orden de venta de 10 acciones
orden_venta = crear_orden(action="SELL", quantity=10, order_type="MKT")
print(orden_venta)

# Obtener el siguiente ID válido
IB_conexion.nextid_evento.clear()
IB_conexion.reqIds(-1)
IB_conexion.nextid_evento.wait()

# Ejecutar Orden (Venta)
IB_conexion.placeOrder(orderId=IB_conexion.next_order_id, contract=contrato, order=orden_venta)

# Desconectar
IB_conexion.disconnect()

# Recordatorio:
#   - El Objeto de Orden define las instrucciones para ejecutar una transacción, como comprar o vender un activo en el mercado.
#   - Para cerrar una posición, se ejecuta una orden inversa a la original, usando la misma cantidad de acciones.
