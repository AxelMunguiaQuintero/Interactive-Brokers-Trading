# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd
from datetime import datetime

# Clase que realiza peticiones sobre datos históricos de contratos de Futuros
class IB_DatosHistoricos_Futuros(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y solicita datos históricos de un Futuro
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.datos_historicos = {}
        self.objetos_datos = {}
        self.evento = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Se llama cuando se obtiene el siguiente ID válido
        """
        
        self.evento.set()
        
        
    def historicalData(self, reqId, bar):
        
        """
        Se llama cuando se están procesando los registros de los datos históricos
        """
        
        # Agregar al diccionario el Id de la petición
        if reqId not in self.datos_historicos:
            self.datos_historicos[reqId] = []
            self.objetos_datos[reqId] = []
            
        # Almacenar los datos y objeto
        self.datos_historicos[reqId].append({
            "Date": bar.date,
            "Open": bar.open,
            "High": bar.high,
            "Low": bar.low,
            "Close": bar.close,
            "Volume": bar.volume
            })
        self.objetos_datos[reqId].append(bar)
        
        
    def historicalDataEnd(self, reqId, start, end):
        
        """
        Se llama al final de la recepción de datos históricos
        """
        
        print("Fin de datos históricos para Id: {}".format(reqId))
        self.evento.set()
        
        
# Crear Instancia de la Clase
IB_conexion = IB_DatosHistoricos_Futuros()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_conexion.run)
api_thread.start()
IB_conexion.evento.wait()
IB_conexion.evento.clear()
        
# Crear contrato del Futuro
contrato = Contract()
contrato.symbol = "CL"
contrato.secType = "FUT"
contrato.exchange = "NYMEX"

# Obtener el mes siguiente para el contrato
fecha_hoy = datetime.now()
mes_siguiente = fecha_hoy.replace(year=fecha_hoy.year + 1, month=1) if fecha_hoy.month == 12 else \
    fecha_hoy.replace(month=fecha_hoy.month + 1)
contrato.lastTradeDateOrContractMonth = mes_siguiente.strftime("%Y%m")

# Obtener la fecha y hora en la zona horaria de Nueva York
end_date_time = datetime.now().strftime("%Y%m%d %H:%M:%S")        
end_date_time = end_date_time + " US/Eastern"        
        
# Solicitar datos históricos
IB_conexion.reqHistoricalData(reqId=1, contract=contrato, endDateTime=end_date_time, durationStr="1 M", 
                              barSizeSetting="15 mins", whatToShow="TRADES", useRTH=1, formatDate=1,
                              keepUpToDate=False, chartOptions=[])
IB_conexion.evento.wait()      
        
# Convertir en DataFrame
df_historicos = pd.DataFrame.from_dict(IB_conexion.datos_historicos[1])  
df_historicos["Date"] = pd.to_datetime(df_historicos["Date"])
df_historicos.set_index("Date", inplace=True)        
print(df_historicos)        
        
# Desconectar
IB_conexion.disconnect()      

# Recordatorio:
#   - Los datos históricos de los contratos de futuros son limitados debido a su naturaleza y las fechas de
#     vencimiento deben de ser específicas. Al expirar, la actividad de negociación disminuye y se reemplazan por
#     nuevos contratos, lo que interrumpe la continuidad de la información.
