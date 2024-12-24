# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue
import threading
import pandas as pd
import time

# Clase para realizar escaneos avanzados mediante la API de IB
class IB_Scanner_Avanzado(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y realiza una búsqueda avanzada en el escáner.
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.evento = threading.Event()
        self.resultados_escaner = {}
        
        
    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        
        """
        Callback que se llama cada vez que se recibe un resultado del escáner
        """
        
        # Diccionario para los datos recibidos
        datos_escaner = {
            
            "Rango": rank + 1,
            "Símbolo": contractDetails.contract.symbol,
            "Tipo": contractDetails.contract.secType,
            "Mercado": contractDetails.contract.exchange,
            "Distancia": distance,
            "Proyección": projection,
            "Detalles": contractDetails
            
            
            }
        if reqId not in self.resultados_escaner:
            self.resultados_escaner[reqId] = []
        self.resultados_escaner[reqId].append(datos_escaner)
        
        
    def scannerDataEnd(self, reqId):
        
        """
        Callback que se llama cuando el escáner ha terminado de enviar todos los resultados
        """
        
        print("El escaneo ha terminado")
        self.evento.set()
        
        
# Establecer Conexión
IB_ScanAvanzado = IB_Scanner_Avanzado()
IB_ScanAvanzado.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_ScanAvanzado.run)
api_thread.start()
time.sleep(3)
        
# Configuración del primer escáner - Acciones con mayores pérdidas
suscripcion1 = ScannerSubscription()
suscripcion1.instrument = "STK"
suscripcion1.locationCode = "STK.US"
suscripcion1.scanCode = "TOP_PERC_LOSE"
suscripcion1.numberOfRows = 30

# Filtros de precios
suscripcion1.priceAbove = 1
suscripcion1.belowPrice = 2_000

# Filtros de Volumen
suscripcion1.aboveVolume = 10_000

# Filtros de capitalización de mercado
# suscripcion1.marketCapAbove = 10_000_000
# suscripcion1.marketCapBelow = 50_000_000_000
        
# Filtros de calificación
# suscripcion1.moodyRatingAbove = "Baa"
# suscripcion1.moodyRatingBelow = "A"
# suscripcion1.spRatingAbove = "BBB"
# suscripcion1.spRatingBelow = "AAA"        
        
# Filtros de fecha de vencimiento (para bonos, en formato "YYYYMM")
# suscripcion1.maturityDateAbove = "202601"
# suscripcion1.maturityDateBelow = "203012"      
        
# Filtros de Tasa de Cupón (para bonos)
# suscripcion1.couponRateAbove = 2.5
# suscripcion1.couponRateBelow = 5.0      
        
# Otros filtros
# suscripcion1.excludeConvertible = True      

# Configuraciones adicionales
# suscripcion1.scannerSettingPairs = ""
# suscripcion1.stockTypeFilter = "ALL"

# Solicitar el primer Escaneo
print("Ejecutando el primer escáner: Acciones con mayores pérdidas en USA:")
IB_ScanAvanzado.reqScannerSubscription(reqId=1, subscription=suscripcion1, scannerSubscriptionOptions=[],
                                       scannerSubscriptionFilterOptions=[])
IB_ScanAvanzado.evento.wait()
IB_ScanAvanzado.evento.clear()
IB_ScanAvanzado.cancelScannerSubscription(reqId=1)

# Resultados del Escáner 1
df_scanner1 = pd.DataFrame(IB_ScanAvanzado.resultados_escaner[1])
print(df_scanner1)

# Configuración del segundo escáner - Acciones más activas
suscripcion2 = ScannerSubscription()
suscripcion2.instrument = "STK"
suscripcion2.locationCode = "STK.US"
suscripcion2.scanCode = "MOST_ACTIVE"
suscripcion2.numberOfRows = 20

# Agregar filtros adicionales mediante TagValue
filtros = [
    
    TagValue("priceAbove", 0)
    
    ]

# Solicitar el segundo Escaneo
print("Ejecutando el segundo escáner: Acciones más activas durante la sesión")
IB_ScanAvanzado.reqScannerSubscription(reqId=2, subscription=suscripcion2, scannerSubscriptionOptions=[],
                                       scannerSubscriptionFilterOptions=filtros)
IB_ScanAvanzado.evento.wait()
IB_ScanAvanzado.evento.clear()
IB_ScanAvanzado.cancelScannerSubscription(reqId=2)

# Resultados del Escáner 2
df_scanner2 = pd.DataFrame(IB_ScanAvanzado.resultados_escaner[2])
print(df_scanner2)

# Desconectar
IB_ScanAvanzado.disconnect()

# Recordatorio:
#   - Los Escáneres Financieros nos proporcionan datos en tiempo real, lo que nos permite reaccionar rápidamente
#     a movimientos del mercado y ajustar estrategias.
#   - Escáneres como los de IB permiten definir configuraciones de escaneo adaptadas a necesidades de inversión.
