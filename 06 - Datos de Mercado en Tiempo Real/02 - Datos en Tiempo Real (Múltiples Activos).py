# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import pandas as pd

# Clase que recibe datos en tiempo real para múltiples activos
class IB_MarketData(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y obtiene datos en tiempo real para varios activos
    """
    
    def __init__(self):
        
        """
        Constructor de la Clase: Inicializa la conexión y las estructuras para almacenar los datos
        """
        
        EClient.__init__(self, self)
        # Almacenar datos por activo y tipo de dato
        self.datos_activos = {}
        
        # Diccionario que describe cada ticktype
        self.TICK_TYPE_DICT = {
            0: "Bid Size",
            1: "Bid Price",
            2: "Ask Price",
            3: "Ask Size",
            4: "Last Price",
            5: "Last Size",
            6: "High",
            7: "Low",
            8: "Volume",
            9: "Close Price",
            14: "Open Tick",
            23: "Option Historical Volatility", # Tick Genérico 104,
            54: "Trade Count", # Tick Genérico 293
            }
    
    def agregar_activo(self, reqId, symbol):
        
        """
        Agrega un nuevo activo a la estructura de almacenamiento
        """
        
        self.datos_activos[reqId] = {"symbol": symbol, "precios": [], "volumen": [], "genericos": []}
        
        
        
    def tickPrice(self, reqId, tickType, price, attrib):
        
        """
        Método que recibe los precios de mercado para los activos
        """
        
        if reqId in self.datos_activos:
            self.datos_activos[reqId]["precios"].append((tickType, price))
            print(f"Activo: {self.datos_activos[reqId]['symbol']}, Tipo de Tick: {self.TICK_TYPE_DICT.get(tickType, 'Desconocido')}, Precio: {price}")
        
    
    def tickSize(self, reqId, tickType, size):
        
        """
        Método que recibe el tamaño de los ticks del mercado por activo
        """
        
        if reqId in self.datos_activos:
            self.datos_activos[reqId]["volumen"].append((tickType, size))
            print(f"Activo: {self.datos_activos[reqId]['symbol']}, Tipo de Tick: {self.TICK_TYPE_DICT.get(tickType, 'Desconocido')}, Volumen: {size}")
            
            
    def tickGeneric(self, reqId, tickType, value):
        
        """
        Método que recibe los ticks genéricos, como los índices o tasas.
        """
        
        if reqId in self.datos_activos:
            self.datos_activos[reqId]["genericos"].append((tickType, value))
            print(f"Activo: {self.datos_activos[reqId]['symbol']}, Tipo de Tick: {self.TICK_TYPE_DICT.get(tickType, 'Desconocido')}, Valor: {value}")
            
            
    def mostrar_datos(self):
        
        """
        Función que organiza y muestra los datos recibidos en DataFrames
        """
        
        # Dar formato a los datos
        output = {}
        for reqId, datos in self.datos_activos.items():
            
            # Obtener Ticker
            symbol = datos["symbol"]
            # Agregar datos
            output[symbol] = []
            
            # Procesar Precios
            if datos["precios"]:
                df_precios = pd.DataFrame(datos["precios"], columns=["Tipo de Tick", "Precio"])
                df_precios["Descripción"] = df_precios["Tipo de Tick"].map(self.TICK_TYPE_DICT)
                print(f"\nPrecios para: {symbol}:")
                print(df_precios)
                
            # Procesar Volumen
            if datos["volumen"]:
                df_volumen = pd.DataFrame(datos["volumen"], columns=["Tipo de Tick", "Volumen"])
                df_volumen["Descripción"] = df_volumen["Tipo de Tick"].map(self.TICK_TYPE_DICT)
                print(f"\nVolumen para: {symbol}:")
                print(df_volumen)
        
            # Procesar Datos Genéricos
            if datos["genericos"]:
                df_genericos = pd.DataFrame(datos["genericos"], columns=["Tipo de Tick", "Valor"])
                df_genericos["Descripción"] = df_genericos["Tipo de Tick"].map(self.TICK_TYPE_DICT)
                print(f"\nDatos Genéricos para: {symbol}:")
                print(df_genericos)
                
                
            output[symbol].append([df_precios, df_volumen, df_genericos])
            
        return output
        
        
# Función para crear un contrato
def crear_contrato(symbol, secType="STK", exchange="SMART", currency="USD"):
    
    """
    Crea un contrato para un activo dado
    """
    
    contrato = Contract()
    contrato.symbol = symbol
    contrato.secType = secType
    contrato.exchange = exchange
    contrato.currency = currency
    
    return contrato

# Conectar a la API
IB_streaming = IB_MarketData()
IB_streaming.connect(host="127.0.0.1", port=7497, clientId=1)
streaming_thread = threading.Thread(target=IB_streaming.run)
streaming_thread.daemon = True
streaming_thread.start()
time.sleep(3)
        
# Lista de activos a suscribir
activos = ["AAPL", "MSFT", "GOOGL", "AMZN"]

# Recibir datos en tiempo real para múltiples activos
IB_streaming.reqMarketDataType(marketDataType=3)

# Iterar sobre la lista de activos para suscribirnos y almacenar los datos
for idx, symbol in enumerate(activos):
    contrato = crear_contrato(symbol)
    IB_streaming.agregar_activo(reqId=idx, symbol=symbol)
    IB_streaming.reqMktData(reqId=idx, contract=contrato, genericTickList="104, 293", snapshot=False, regulatorySnapshot=False, mktDataOptions=[])
    
# Esperar un tiempo para recibir datos
time.sleep(15)

# Cancelar las suscripciones
for idx in range(len(activos)):
    IB_streaming.cancelMktData(reqId=idx)
    
# Dormir 1 segundo
time.sleep(1)
        
# Mostrar los datos recibidos
IB_streaming.mostrar_datos()   
        
# Desconectar API
IB_streaming.disconnect()

# Recordatorio:
#   - IB nos manda diferentes tipos de datos con cada solicitud en tiempo real, y cada tipo de tick corresponde a un 
#     ID específico. Estos IDs representan datos importantes como el precio bid, ask, transacciones ejecutadas, y otros
#     indicadores clave. Cada tick tiene un significado único y proporciona información sobre la actividad del mercado,
#     lo que permite procesar datos financieros en tiempo real para análisis y toma de decisiones informadas.
