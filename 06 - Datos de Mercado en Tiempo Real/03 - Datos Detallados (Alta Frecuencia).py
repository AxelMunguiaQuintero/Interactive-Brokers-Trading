# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

# Clase que procesa solicitudes de datos Tick-by-tick
class IB_TickByTickData(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y obtiene datos tick-by-tick en tiempo real
    """
    
    def __init__(self):
        
        """
        Constructor de la clase
        """
        
        EClient.__init__(self, self)
        # Atributos
        self.tick_data_last = []
        self.tick_data_bid_ask = []
        self.tick_data_midpoint = []
        
        
    def tickByTickAllLast(self, reqId, tickType, time, price, size, tickAttribLast, exchange, specialConditions):
        
        """
        Método que recibe los datos Tick-by-Tick.
        
        Este método se utiliza para recibir datos de la última transacción realizada, incluyendo el precio y el tamaño
        de la transacción.
        
        Uso: Es útil para obtener un panorama detallado de las últimas transacciones que han ocurrido en el mercado,
        lo que ayuda a los traders a evaluar la actividad reciente y a tomar decisiones informadas.
        """
        
        self.tick_data_last.append((reqId, time, price, size))
        print(f"ID de solicitud: {reqId}, Tiempo: {time}, Precio: {price}, Tamaño: {size}, Exchange: {exchange}")
        
        
    
    def tickByTickBidAsk(self, reqId, time, bidPrice, askPrice, bidSize, askSize, tickAttribBidAsk):
        
        """
        Método que recibe los precios Bid y Ask en Tick-by-Tick.
        
        Este método proporciona información sobre los precios Bid y Ask en tiempo real, así como sus respectivos tamaños.
        
        Uso: Es fundamental para traders que utilizan estrategias basadas en la diferencia entre el precio Bid y Ask,
        permitiendo evaluar la liquidez y la profundidad del mercado en tiempo real.
        """
        
        self.tick_data_bid_ask.append((reqId, time, bidPrice, askPrice, bidSize, askSize))
        print(f"""ID de Solicitud: {reqId}, Tiempo: {time}, Precio Bid: {bidPrice}, Tamaño Bid: {bidSize},
              Precio Ask: {askPrice}, Tamaño Ask: {askSize}""")
              
              
    def tickByTickMidPoint(self, reqId, time, midPoint):
        
        """
        Método que recibe el precio Medio en Tick-by-Tick
        """
        
        self.tick_data_midpoint.append((reqId, time, midPoint))
        print(f"ID de Solicitud: {reqId}, Tiempo: {time}, Precio Medio: {midPoint}")
        
        
# Conectar a la API
IB_streaming = IB_TickByTickData()
IB_streaming.connect(host="127.0.0.1", port=4001, clientId=1)
streaming_thread = threading.Thread(target=IB_streaming.run)
streaming_thread.start()
time.sleep(3)

# Crear Contrato
contract = Contract()
contract.symbol = "EUR"
contract.secType = "CASH"
contract.exchange = "IDEALPRO"
contract.currency = "USD"
contract.primaryExchange = "IDEALPRO"

# Solicitar datos Tick-by-Tick
IB_streaming.reqTickByTickData(reqId=0, contract=contract, tickType="MidPoint", numberOfTicks=0, ignoreSize=True)

# Tipos de Ticks (tickType):
# AllLast: Última Transacción (Precio y Tamaño) -> tickbyTickAllLast
# BidAsk: Precios Bid y Ask -> tickByTickBidAsk
# MidPoint: Precio medio entre el bid y ask -> tickByTickMidPoint

time.sleep(10)
        
# Cancelar la solicitud de datos   
IB_streaming.cancelTickByTickData(reqId=0)
        
# Desconectar de la API
IB_streaming.disconnect()   

# Recordatorio:
#   - El método reqTickByTickData proporciona datos tick por tick, capturando cada transacción o cambio en el bid/ask.
#     Es altamente granular y detallado, ideal para análisis de alta frecuencia o estrategias algorítmicas que requieren
#     seguimiento preciso de cada evento del mercado en tiempo real.
