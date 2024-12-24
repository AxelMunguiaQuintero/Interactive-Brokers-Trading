# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

# Clase que permite ejecutar diferentes tipos de órdenes
class IB_TiposOrdenes(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y permite ejecutar diferentes tipos de órdenes
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.next_order_id = None
        self.evento_ordenes = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Este método es llamado cuando se recibe el siguiente ID válido de orden disponible
        """
        
        self.next_order_id = orderId
        print("Siguiente ID válido es:", orderId)
        
        
    def crear_contrato(self):
        
        """
        Crea y devuelve un contrato para el símbolo deseado
        """
        
        contrato = Contract()
        contrato.symbol = "AAPL"
        contrato.secType = "STK"
        contrato.exchange = "SMART"
        contrato.currency = "USD"

        return contrato

        
    def ejecutar_orden_mercado(self):

        """
        Envía una orden de mercado para comprar acciones
        """        
        
        contrato = self.crear_contrato()
        orden = Order()
        orden.action = "BUY"
        orden.orderType = "MKT" # Tipo de Orden (Mercado)
        orden.totalQuantity = 10
        orden.eTradeOnly = ""
        orden.firmQuoteOnly = ""
        
        print(f"Cliente {self.clientId} - Enviando orden de mercado para {contrato.symbol}")
        self.placeOrder(orderId=self.next_order_id, contract=contrato, order=orden)
        self.evento_ordenes.set()
        
    
    def ejecutar_orden_limite(self, precio):
        
        """
        Envía una orden limitada para comprar acciones
        """
        
        contrato = self.crear_contrato()
        orden = Order()
        orden.action = "BUY"
        orden.orderType = "LMT" # Tipo de Orden (Límite)
        orden.lmtPrice = precio
        orden.totalQuantity = 10
        orden.eTradeOnly = ""
        orden.firmQuoteOnly = ""
        
        print(f"Cliente {self.clientId} - Enviando orden limitada para {contrato.symbol}")
        self.placeOrder(orderId=self.next_order_id + 1, contract=contrato, order=orden)
        self.evento_ordenes.set()
        
        
    def ejecutar_orden_stop(self, precio_auxiliar):
        
        """
        Envía una orden stop para comprar acciones
        """
        
        contrato = self.crear_contrato()
        orden = Order()
        orden.action = "BUY"
        orden.orderType = "STP" # Tipo de Orden (Stop)
        orden.totalQuantity = 10
        orden.auxPrice = precio_auxiliar
        orden.eTradeOnly = ""
        orden.firmQuoteOnly = ""
        
        print(f"Cliente {self.clientId} - Enviando orden stop para {contrato.symbol} a {orden.auxPrice}")
        self.placeOrder(orderId=self.next_order_id + 2, contract=contrato, order=orden)
        self.evento_ordenes.set()
        
        
    def ejecutar_orden_stop_limit(self, precio, precio_auxiliar):
        
        """
        Envía una orden stop-limit para comprar acciones
        """
        
        contrato = self.crear_contrato()
        orden = Order()
        orden.action = "BUY"
        orden.orderType = "STP LMT" # Tipo de Orden (Stop-Limit)
        orden.totalQuantity = 10
        orden.lmtPrice = precio
        orden.auxPrice = precio_auxiliar
        orden.eTradeOnly = ""
        orden.firmQuoteOnly = ""
        
        print(f"Cliente {self.clientId} - Enviando orden stop-limit para {contrato.symbol} a {orden.lmtPrice} (stop: {orden.auxPrice})")
        self.placeOrder(orderId=self.next_order_id + 3, contract=contrato, order=orden)
        self.evento_ordenes.set()
        
        
    def ejecutar_orden_tk_sl(self, stop_loss_price, take_profit_price):
        
        """
        Envía una orden de mercado para comprar acciones y establece stop loss y take profit
        """
        
        contrato = self.crear_contrato()
        
        # Orden de mercado
        market_order = Order()
        market_order.orderId = self.next_order_id + 4 
        market_order.action = "BUY"
        market_order.orderType = "MKT"
        market_order.totalQuantity = 10
        market_order.eTradeOnly = ""
        market_order.firmQuoteOnly = ""
        market_order.transmit = False
        
        # Orden de Stop Loss
        stop_loss = Order()
        stop_loss.parentId = market_order.orderId
        stop_loss.orderId = market_order.orderId + 1 
        stop_loss.action = "SELL"
        stop_loss.orderType = "STP"
        stop_loss.totalQuantity = 10
        stop_loss.auxPrice = stop_loss_price
        stop_loss.eTradeOnly = ""
        stop_loss.firmQuoteOnly = ""
        stop_loss.transmit = False
        
        # Orden de Take Profit
        limit_order = Order()
        limit_order.parentId = market_order.orderId
        limit_order.orderId = market_order.orderId + 2
        limit_order.action = "SELL"
        limit_order.orderType = "LMT"
        limit_order.totalQuantity = 10
        limit_order.lmtPrice = take_profit_price
        limit_order.eTradeOnly = ""
        limit_order.firmQuoteOnly = ""
        limit_order.transmit = True
        
        self.placeOrder(orderId=market_order.orderId, contract=contrato, order=market_order)
        self.placeOrder(orderId=stop_loss.orderId, contract=contrato, order=stop_loss)
        self.placeOrder(orderId=limit_order.orderId, contract=contrato, order=limit_order)
        self.evento_ordenes.set()
        
        
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, 
                    clientId, whyHeld, mktCapPrice):
        
        """
        Muestra el estado de la orden
        """
        
        print(f"Cliente {self.clientId} - Estado de la Orden {orderId}: {status}, Llenado: {filled}, Restante: {remaining}, Precio Promedio: {avgFillPrice}")
        
        
# Conectar al Servidor de la API
IB_con = IB_TiposOrdenes()
IB_con.connect(host="127.0.0.1", port=7497, clientId=10)
api_thread = threading.Thread(target=IB_con.run)
api_thread.start()
time.sleep(2)
        
# Ejecutar Órdenes

# Tipo: Market
IB_con.evento_ordenes.clear()   
IB_con.ejecutar_orden_mercado()
IB_con.evento_ordenes.wait()
        
# Tipo: Límite
IB_con.evento_ordenes.clear()
IB_con.ejecutar_orden_limite(precio=236.50) # Ajustar precio al del mercado
IB_con.evento_ordenes.wait()       
        
# Tipo: Stop
IB_con.evento_ordenes.clear()
IB_con.ejecutar_orden_stop(precio_auxiliar=240) # Ajustar precio al del mercado
IB_con.evento_ordenes.wait()      
        
# Tipo: Stop Limit
IB_con.evento_ordenes.clear()
IB_con.ejecutar_orden_stop_limit(precio=240.03, precio_auxiliar=240) # Ajustar precio
IB_con.evento_ordenes.wait()    
        
# Tipo: Mercado con Take Profit y Stop-Loss
IB_con.evento_ordenes.clear()
IB_con.ejecutar_orden_tk_sl(stop_loss_price=230, take_profit_price=250) # Ajustar niveles
IB_con.evento_ordenes.wait()     
        
# Desconectar
IB_con.disconnect()
api_thread.join()

# Recordatorio:
#   - Las órdenes que están compuestas por varias órdenes deben indicar un parentId, que establece la relación entre ellas.
#     Este identificador ayuda al sistema a reconocer cual es la orden principal para que gestione correctamente la ejecución
#     de las órdenes secundarias.
