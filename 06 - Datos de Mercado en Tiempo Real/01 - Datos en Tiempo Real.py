# Importar librerías
import threading
import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

# Clase que gestiona la conexión y la solicitud de datos de mercado
class IB_MarketData(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y obtiene datos en tiempo real
    """
    
    def __init__(self):
        
        """
        Constructor de la clase
        """
        
        EClient.__init__(self, self)
        # Atributos
        self.tick_precios = []
        self.tick_volumen = []
        
    
    def tickPrice(self, reqId, tickType, price, attrib):
        
        """
        Método que recibe los precios de mercado
        """
        
        # Almacenar Precios
        self.tick_precios.append((tickType, price))
        print(f"ID de la Solicitud: {reqId}, Tipo de Tick: {tickType}, Precio: {price}")
        
        
    def tickSize(self, reqId, tickType, size):
        
        """
        Método que recibe el tamaño de los ticks del mercado
        """
        
        # Almacenar Volumen
        self.tick_volumen.append((tickType, size))
        print(f"ID de la Solicitud: {reqId}, Tipo de Tick: {tickType}, Tamaño: {size}")
        
        
# Conectarnos a la API
IB_streaming = IB_MarketData()
IB_streaming.connect(host="127.0.0.1", port=7497, clientId=1)
# Gestionar la comunicación
streaming_thread = threading.Thread(target=IB_streaming.run, daemon=True)
streaming_thread.start()
time.sleep(3)
        
# Crear Contrato 
contrato = Contract()
contrato.symbol = "AMZN"
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Recibir Datos en Tiempo Real
IB_streaming.reqMarketDataType(3)
IB_streaming.reqMktData(reqId=0, contract=contrato, genericTickList="", snapshot=False, regulatorySnapshot=False, mktDataOptions=[])

# Esperar un tiempo para recibir datos
time.sleep(10)

# Cancelar Suscripción
IB_streaming.cancelMktData(reqId=0)
        
# Mostrar Datos
print("\nTick Precios:\n")
print(IB_streaming.tick_precios)

print("\nTick Volumen:\n")
print(IB_streaming.tick_volumen)    
        
# Desconectar
IB_streaming.disconnect()

# Recordatorio:
#   - El método reqMktData solicita datos de mercado en tiempo real, proporcionando precios bid, ask, último precio, volumen, etc.
#     Las actualizaciones son agregadas y no tan frecuentes (esto significa que se obtiene un resumen de los datos de mercado
#     de manera más espaciada), siendo útil para monitorear cambios generales sin necesitar cada transacción o detalle granular
#     del mercado.
#   - Los datos recibidos con reqMktData tienen una frecuencia de actualización de alrededor de 250 ms (4 veces por segundo).
