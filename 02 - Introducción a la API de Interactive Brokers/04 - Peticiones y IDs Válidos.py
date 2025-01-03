# -*- coding: utf-8 -*-
# Importar librerías
import threading
import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

# Clase de Control de Peticiones
class IB_Peticiones(EWrapper, EClient):
    
    """
    Clase que se conecta a Interactive Brokers
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.peticiones = {}
        
        
    def nextValidId(self, orderId: int):
        
        """
        Método que solicita a la TWS el siguiente ID válido que se puede utilizar al realizar una orden.
        El ID devuelto es el siguiente ID válido para la sesión actual y para el cliente de la instancia generada.
        """
        
        self.orderId = orderId
        print("Siguiente Id válido:", self.orderId)
        
        
    def symbolSamples(self, reqId: int, contractDescriptions):
        
        """
        Método que se llamaa cuando se localizan diferentes instrumentos de inversión que coinciden
        """
        
        print(f"Símbolos coincidentes para reqId: {reqId}:\n")
        for symbol in contractDescriptions:
            print(symbol.contract)
            
            
# Generar Instancia
IB_Conexion = IB_Peticiones()
IB_Conexion.connect(host="127.0.0.1", port=7497, clientId=1)
hilo_api = threading.Thread(target=IB_Conexion.run)
hilo_api.start()
time.sleep(3)

# Solicitar el Siguiente ID válido
IB_Conexion.reqIds(-1)        

# Solicitar Instrumentos Financieros Similares
IB_Conexion.reqMatchingSymbols(reqId=100, pattern="AMZN")        
        
# Desconectar
IB_Conexion.disconnect()        
 
# Recordatorio:       
#   - A la API de IB se le debe de proporcionar un ID único para cada nueva solicitud o orden, asegurando que no se repitan
#     y que las operaciones se gestionen de manera correcta.
#   - Cada petición a la API requiere un ID único. Este ID permite identificar la solicitud al recibir la respuesta correspondiente
#     sin confusiones entre múltiples peticiones.
