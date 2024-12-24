# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from datetime import datetime
import threading
import time

# Clase que ejecuta órdenes de Futuros
class IB_Futuros_Ordenes(EClient, EWrapper):
    
    """
    Clase que se conecta a IB y ejecuta órdenes de Futuros
    """
    
    def __init__(self):
        
        """
        Constructor de la clase
        """
        
        EClient.__init__(self, self)
        self.evento = threading.Event()
        self.order_id = None
        self.precio_promedio = None
        
        
    def nextValidId(self, orderId):
        
        """
        Se llama cuando se obtiene el Id válido para una orden
        """
        
        print("ID:", orderId)
        self.order_id = orderId
        self.evento.set()
        
        
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, 
                    clientId, whyHeld, mktCapPrice):
        
        """
        Se llama para actualizar el estado de una orden
        """
        
        print(f"Estado de la Orden. ID: {orderId}, Estado: {status}, Llenado: {filled}, Restante: {remaining}, Precio Promedio: {avgFillPrice}")
        # Almacenar Precio Promedio
        self.precio_promedio = avgFillPrice
        
    
# Generar Conexión
IB_ordenes = IB_Futuros_Ordenes()
IB_ordenes.connect(host="127.0.0.1", port=7497, clientId=1)
thread_api = threading.Thread(target=IB_ordenes.run)
thread_api.start()
IB_ordenes.evento.wait()
IB_ordenes.evento.clear()
        
# Crear Contrato
contrato = Contract()
contrato.symbol = "GC"
contrato.secType = "FUT"
contrato.exchange = "COMEX" # Commodity Exchange

fecha_actual = datetime.now()
# Determinar el siguiente mes
if fecha_actual.month == 12:
    mes_siguiente = fecha_actual.replace(year=fecha_actual.year + 1, month=1).strftime("%Y%m")       
else:
    mes_siguiente = fecha_actual.replace(month=fecha_actual.month + 1).strftime("%Y%m")
contrato.lastTradeDateOrContractMonth = mes_siguiente

# Crear orden de mercado
orden_market = Order()
orden_market.action = "BUY"
orden_market.orderType = "MKT"
orden_market.totalQuantity = 1
orden_market.eTradeOnly = ""
orden_market.firmQuoteOnly = ""

IB_ordenes.placeOrder(orderId=IB_ordenes.order_id, contract=contrato, order=orden_market)
print("Orden de mercado ha sido enviada")
time.sleep(5)
        
# Crear orden de límite para cerrar la posición
orden_limit = Order()
orden_limit.action = "SELL"
orden_limit.orderType = "LMT"
orden_limit.totalQuantity = 1
orden_limit.lmtPrice = round(IB_ordenes.precio_promedio * 0.997)
orden_limit.eTradeOnly = ""
orden_limit.firmQuoteOnly = ""

IB_ordenes.placeOrder(orderId=IB_ordenes.order_id + 1, contract=contrato, order=orden_limit)
print("Orden de tipo límite ha sido enviada")
time.sleep(5)    
        
# Desconectar
IB_ordenes.disconnect()      

# Recordatorio:
#   - La Ejecución de Órdenes de Futuros nos permite abrir posiciones en función de nuestras expectativas sobre el movimiento de precios
#     de los activos subyacentes. Esto nos brinda la oportunidad de beneficiarnos de los cambios en el mercado, ya sea mediante
#     especulación o cobertura de riesgos.        
