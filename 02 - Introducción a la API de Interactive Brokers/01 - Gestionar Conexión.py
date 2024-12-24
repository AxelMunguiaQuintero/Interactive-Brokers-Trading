# Importar librerías
from ibapi.client import EClient # Clase que manejará la conexión a la API de IB (Comunicación con el Servidor)
from ibapi.wrapper import EWrapper # Clase que procesa las respuestas enviadas del servidor
import threading

# Clase IB Conexión
class IB_Conexion(EWrapper, EClient):
    
    """
    Clase que representa la conexión a la API de Interactive Brokers
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        # Inicializar EClient
        EClient.__init__(self, self)
        self.evento_conexion = threading.Event()
        
        
    def nextValidId(self, orderId: int): 
        
        """
        Recibe el siguiente ID válido para ejecutar operaciones
        """
        
        print("Siguiente ID Válido:", orderId)
        self.orderId = orderId
        # Comunicar que la conexión ya está activa
        self.evento_conexion.set()
        print("¡Conexión ha sido establecida!")
        
        
# Gestionar Conexión
def gestionar_conexion():
    
    """
    Gestiona la conexión con el servidor para permitir que nuestra aplicación reciba datos de la API
    """
    
    # Correr
    IB_app.run()
    
    
# Generar Instancia de Nuestra clase
IB_app = IB_Conexion()

# Conectar a TWS o IB Gateway
IB_app.connect(host="127.0.0.1", port=7497, clientId=1)
print("Conexión:", IB_app.isConnected())
    
# Inicializar un Hilo para manejar la conexión
api_thread = threading.Thread(target=gestionar_conexion)
api_thread.start()

# Esperar a que la conexión esté activa
IB_app.evento_conexion.wait()
IB_app.evento_conexion.clear()
print("Estado Actual Evento:", IB_app.evento_conexion.is_set())
    
# Desconectar Cliente
IB_app.disconnect()
print("Conexión:", IB_app.isConnected())
    
# Recordatorio:
#   - Para interactuar con IB, debes conectarte a su sistema. Esto permite acceder a datos de mercado, enviar órdenes
#     y recibir actualizaciones en tiempo real desde su plataforma.
#   - Se debe de tener una correcta estructura para procesar las respuestas que nos manda el Servidor, de otra forma,
#     nuestro programa podría detenerse por un error.
