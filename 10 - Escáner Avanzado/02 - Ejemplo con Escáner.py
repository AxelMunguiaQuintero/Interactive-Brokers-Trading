# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.scanner import ScannerSubscription
import threading
import pandas as pd

# Clase que realiza escaneos mediante la API de IB
class IB_Scanner(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y realiza una búsqueda de instrumentos financieros mediante el escáner.
    """
    
    def __init__(self):
        
        """
        Constructor de la clase
        """
        
        EClient.__init__(self, self)
        self.evento = threading.Event()
        self.resultados = {}
        
    
    def nextValidId(self, orderId):
        
        """
        Se llama cuando se obtiene un ID válido para realizar órdenes
        """
        
        self.evento.set()
        
        
    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        
        """
        Se llama cada vez que se recibe un resultado del escáner
        """
        
        # Crear un diccionario con los datos recibidos
        datos = {
            
            "Rango": rank + 1,
            "Símbolo": contractDetails.contract.symbol,
            "Tipo": contractDetails.contract.secType,
            "Mercado":  contractDetails.contract.exchange,
            "Distancia": distance,
            "Proyección": projection,
            "legsStr": legsStr            
            
            }
        
        # Almacenar
        if reqId not in self.resultados:
            self.resultados[reqId] = []
            
        self.resultados[reqId].append(datos)
        
        
    def scannerDataEnd(self, reqId):
        
        """
        Se llama cuando el escáner ha terminado de enviar todos los resultados
        """
        
        print(f"Escaneo {reqId} ha sido completado")
        self.evento.set()
        
        
# Conexión
IB_conexion = IB_Scanner()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
thread = threading.Thread(target=IB_conexion.run)
thread.start()
IB_conexion.evento.wait()
IB_conexion.evento.clear()
        
# Configuración del primer escáner
suscripción1 = ScannerSubscription()
suscripción1.instrument = "STK"
suscripción1.locationCode = "STK.NASDAQ"
suscripción1.scanCode = "TOP_PERC_GAIN"
suscripción1.numberOfRows = 10

# Solicitar el primer escaneo
print("Ejecutando el primer escáner: Acciones con mayores ganancias porcentuales en NASDAQ")
IB_conexion.reqScannerSubscription(reqId=1, subscription=suscripción1, scannerSubscriptionOptions=[],
                                   scannerSubscriptionFilterOptions=[])
IB_conexion.evento.wait()      
IB_conexion.evento.clear()
IB_conexion.cancelScannerSubscription(reqId=1)

# Configuración del segundo escáner
suscripción2 = ScannerSubscription()
suscripción2.instrument = "STK"
suscripción2.locationCode = "STK.US"
suscripción2.scanCode = "HOT_BY_VOLUME"
suscripción2.numberOfRows = 20

# Solicitar el segundo escaneo
print("Ejecutando el segundo escáner para acciones listadas en USA")
IB_conexion.reqScannerSubscription(reqId=2, subscription=suscripción2, scannerSubscriptionOptions=[],
                                   scannerSubscriptionFilterOptions=[])
IB_conexion.evento.wait()      
IB_conexion.evento.clear()
IB_conexion.cancelScannerSubscription(reqId=2)
        
# Obtener los resultados y convertir a DataFrame
for req_id, resultados in IB_conexion.resultados.items():
    df_resultados = pd.DataFrame(resultados)      
    print(f"\nResultados del Escáner {req_id}:\n")
    print(df_resultados)
   
# Desconectar
IB_conexion.disconnect()     

# Recordatorio:
#   - La filtración de activos con el escáner de IB se efectúa utilizando códigos de escáner y
#     filtros personalizables, como rendimiento, volumen y tendencias, para seleccionar activos
#     que cumplen criterios específicos y optimizar estrategias de inversión.
