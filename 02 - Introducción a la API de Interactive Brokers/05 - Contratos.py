# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading 
import time

# Clase de Contratos
class IB_Contratos(EClient, EWrapper):
    
    """
    Clase que se conecta a IB y solicita datos de contratos
    """
    
    def __init__(self):
        
        """
        Constructor que inicializa la conexión a IB
        """
        
        EClient.__init__(self, self)
        self.contratoDetalles = None
        
        
    def nextValidId(self, orderId):
        
        """
        Método que se llama cuando la API proporciona el siguiente ID de orden válido
        """
        
        # Guardar como atributo
        self.nextOrderId = orderId
        
        
    def contractDetails(self, reqId, contractDetails):
        
        """
        Método que maneja los detalles del contrato devuelto por IB
        """
        
        # Almacenar
        self.contratoDetalles = contractDetails
        # Desplegar en consola
        print(f"Id Solicitado: {reqId} - Contrato: {contractDetails}")
        
        
# Gestionar Conexión
def gestionar_conexion():
    
    """
    Gestiona la conexión con IB para recibir y procesar datos y peticiones
    """
    
    IB_conn.run()
        
# Crear una instancia de la clase
IB_conn = IB_Contratos()
IB_conn.connect(host="127.0.0.1", port=7497, clientId=0)

# Inicializar el Hilo para ejecutar la API
hilo_api = threading.Thread(target=gestionar_conexion)
hilo_api.start()

# Esperar un tiempo para que la conexión se establezca
time.sleep(3)
        
# Definir un contrato
contrato = Contract()
contrato.symbol = "AMZN"      # Símbolo del Activo
contrato.secType = "STK"      # Tipo de Activo: Acciones (STK)
contrato.exchange = "SMART"   # Mercado: NASDAQ o ISLAND
contrato.currency = "USD"     # Divisa: Dólares Estadounidenses

print("Contrato:", contrato)        
print("Campos que se pueden pasar:\n\n", [i for i in dir(contrato) if not i.startswith("_")])
        
# Solicitar los detalles del contrato
IB_conn.reqContractDetails(reqId=0, contract=contrato)
        
# Detalles de contratos diferentes
contrato.symbol = "AAPL"
IB_conn.reqContractDetails(reqId=1, contract=contrato)
contrato.symbol = "TSLA"
IB_conn.reqContractDetails(reqId=2, contract=contrato)

# Acceder a Atributos
print("Contrato:", IB_conn.contratoDetalles)
print("Campos Disponibles:", [i for i in dir(IB_conn.contratoDetalles) if not i.startswith("_")])        
print("Nombre:", IB_conn.contratoDetalles.longName)        
print("Industria:", IB_conn.contratoDetalles.industry)        
print("Categoría:", IB_conn.contratoDetalles.category)        
        
# Desconectar
IB_conn.disconnect()     

# Recordatorio:
#   - Los Contratos en la API de IB representan instrumentos financieros como acciones, futuros o divisas. Especificar correctamente
#     el contrato asegura que las peticiones obtengaan los datos del activo deseado.
