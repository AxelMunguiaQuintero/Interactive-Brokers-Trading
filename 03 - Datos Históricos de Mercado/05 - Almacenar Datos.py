# Importar librerías
import sqlite3
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import time
import os

# Clase que almacena la información recibida
class IB_Almacenamiento(EClient, EWrapper):
    
    """
    Clase que se conecta a IB y almacena los datos recibidos en Bases de Datos.
    """
    
    def __init__(self):
        
        """
        Inicializa la instancia de la API
        """
        
        EClient.__init__(self, self)
        # Atributos
        self.datos_event = threading.Event()
        self.historical_data = []
        
        
    def historicalData(self, reqId, bar):
        
        """
        Método que se llama cuando se recibe un nuevo dato
        """
        
        # Almacenar
        self.historical_data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
        
        
    def historicalDataEnd(self, reqId, start, end):
        
        """
        Método que se manda a llamar e indica que todos los datos históricos han sido recibidos.
        """
        
        print("¡Datos han sido recibidos!")
        self.historical_data = pd.DataFrame(data=self.historical_data, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        self.datos_event.set()
        

# Crear Carpeta para almacenar información
if not os.path.isdir("../datos"):
    os.mkdir("../datos")
    
# Crear Base de Datos
conn = sqlite3.connect("../datos/historical_data.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS precios (
        date DATETIME PRIMARY KEY,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER
        )
               """)
conn.commit()
        
# Conectar
IB_conn = IB_Almacenamiento()
IB_conn.connect(host="127.0.0.1", port=7497, clientId=1)
threading.Thread(target=IB_conn.run).start()
time.sleep(3)

# Definir contrato
contrato = Contract()
contrato.symbol = "AMZN"
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Obtener Datos
IB_conn.reqMarketDataType(3)
IB_conn.reqHistoricalData(reqId=1, contract=contrato, endDateTime="", durationStr="10 Y", barSizeSetting="1 day", 
                          whatToShow="TRADES", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])
IB_conn.datos_event.wait(timeout=30)
IB_conn.datos_event.clear()

# Función Guardar Datos
def guardar_datos(datos: list):
    
    """
    Guarda cada registro en la base de datos
    """
    
    # Almacenar
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO precios (date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)", datos)
    conn.commit()
    
# Almacenar datos históricos
datos = IB_conn.historical_data
guardar_datos(datos.values.tolist())

# Consultar las tablas que existen en nuestra base de datos
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(table[0])
    
# Leer Datos: Desde la conexión
cursor.execute("SELECT * FROM precios")
resultados = cursor.fetchall()
datos = pd.DataFrame(resultados, columns=["Date", "Open", "High", "Low", "Close", "Volume"]).set_index("Date")
datos.index = pd.to_datetime(datos.index, format="%Y%m%d")
print(datos)

# Leer Datos: Desde Pandas
datos = pd.read_sql(sql="SELECT * FROM precios", con=conn).set_index("date")
datos.index = pd.to_datetime(datos.index, format="%Y%m%d")
print(datos)

# Leer Datos: Desde Pandas (Diferente)
datos = pd.read_sql_query(sql="SELECT * FROM precios", con=conn).set_index("date")
datos.index = pd.to_datetime(datos.index, format="%Y%m%d")
print(datos)

# Documentación de Datos (Reciente): https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#hist-bar-size
# Documentación de Datos (Antigua): https://interactivebrokers.github.io/tws-api/historical_bars.html

# Recordatorio:
#   - SQLite permite crear bases de datos locales ligeras para almacenar información estructurada, ideal para guardar
#     datos históricos de activos financieros sin depender de un servidor centralizado.
