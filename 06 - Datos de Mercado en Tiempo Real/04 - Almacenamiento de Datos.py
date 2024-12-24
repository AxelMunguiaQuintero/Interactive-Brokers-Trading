# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import datetime
import pandas as pd
import os

# Clase que procesa solicitudes de datos tick-by-tick
class IB_TickByTickData(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y obtiene datos Tick-by-Tick en tiempo real
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.tick_data = []
        self.req_id = 0
        
        
    def tickByTickMidPoint(self, reqId, time, midPoint):
        
        """
        Método que recibe el precio medio de los datos en tiempo real
        """
        
        self.tick_data.append((reqId, time, midPoint))
        print(f"ID Solicitud: {reqId}, Tiempo: {time}, Precio Medio: {midPoint}")
        
        
# Función para crear un contrato
def crear_contrato(symbol, secType="CASH", exchange="IDEALPRO", currency="USD", primary_exchange="IDEALPRO"):
    
    """
    Genera un contrato de un activo específico
    """
    
    contrato = Contract()
    contrato.symbol = symbol
    contrato.secType = secType
    contrato.exchange = exchange
    contrato.currency = currency
    contrato.primaryExchange = primary_exchange
    
    return contrato

# Función para guardar datos en un archivo
def guardar_datos(df, filename):
    
    """
    Función para guardar datos en un archivo csv
    """
    
    # Revisar si hay un archivo existente
    if os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        df = pd.concat([existing_df, df]).drop_duplicates().reset_index(drop=True)
    # Guardar
    df.to_csv(filename, index=False)
    
# Lista de activos para solicitar datos
assets = ["EUR", "GBP", "AUD"]

# Conectar a la API
IB_streaming = IB_TickByTickData()
IB_streaming.connect(host="127.0.0.1", port=7497, clientId=1)
streaming_thread = threading.Thread(target=IB_streaming.run, daemon=True)
streaming_thread.start()
time.sleep(3)
    
# Solicitar los datos para cada activo
for asset in assets:
    contrato = crear_contrato(symbol=asset)
    IB_streaming.reqTickByTickData(reqId=IB_streaming.req_id, contract=contrato, tickType="MidPoint", numberOfTicks=0, ignoreSize=True)
    IB_streaming.req_id += 1
    
# Esperar un tiempo para recibir los datos antes de cancelar
time.sleep(15)

# Cancelar las solicitudes de datos
for i in range(IB_streaming.req_id):
    IB_streaming.cancelTickByTickData(reqId=i)
    
# Esperar a que se procesen los últimos datos
time.sleep(0.5)
    
# Mostrar datos
print(IB_streaming.tick_data)  

# Guardar los datos en un archivo
datos_df = pd.DataFrame(IB_streaming.tick_data, columns=["Request ID", "Time", "MidPoint"])    
print(datos_df)    
for indice, activo in enumerate(assets):
    # Extraer datos para cada activo
    sub_datos = datos_df[datos_df["Request ID"] == indice].copy()
    # Convertir Fecha
    sub_datos["Time"] = sub_datos["Time"].apply(lambda x: datetime.datetime.fromtimestamp(x))
    # Guardar
    guardar_datos(df=sub_datos, filename=assets[indice] + "_USD-tickbytick.csv")
    
# Leer Datos y Mostrarlos
for indice in range(len(assets)):
    # Obtener Nombre
    filename = assets[indice] +  "_USD-tickbytick.csv"
    df = pd.read_csv(filename)
    print("Datos:")
    print(df)
    print("\n" + "-" * 20 + "\n")
    
# Desconectar de la API
IB_streaming.disconnect()  

# Recordatorio:
#   - El alto procesamiento de precios requiere una recepción de datos, especialmente en el trading de alta frecuencia
#     donde las decisiones deben tomarse en milisegundos. Este entorno genera un volumen masivo de información que 
#     debe analizarse rápidamente, permitiendo a los traders aprovechar oportunidades antes que el resto del mercado.
