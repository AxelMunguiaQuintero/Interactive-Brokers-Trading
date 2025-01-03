# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time

# Clase que maneja los Errores
class IB_Errores(EWrapper, EClient):
    
    """
    Clase que gestiona y procesa los mensajes del servidor
    """
    
    def __init__(self, guardar_errores: bool = False):
        
        """
        Constructor
        """
        
        # Inicializar EClient
        EClient.__init__(self, self)
        self.guardar_errores = guardar_errores
        
    
    def error(self, reqId: int, errorCode: int, errorString: str):
        
        """
        Método que se llama cuando ocurre un error.
        
        Parámetros:
            - reqId (int): ID de la solicitud asociada al error.
            - errorCode (int): Código del error.
            - errorString (str): Describe el error.
        """
        
        # Definir error
        mensaje_error = (f"Cliente: {self.clientId}: Error\n"
                         f"ID de la solicitud: {reqId}\n"
                         f"Código del error: {errorCode}, Mensaje: {errorString}\n\n")
        # Imprimir consola
        print(mensaje_error)
        
        # Guardar en un archivo
        if self.guardar_errores:
            with open("errores_ibapi.txt", "a") as outfile:
                # Escribir en el archivo
                outfile.write(mensaje_error)
                outfile.close()
                

# Ejecutar API
def ejecutar_api():
    
    """
    Gestiona la conexión con el Servidor
    """
    
    IB_conexion.run()
        
# Generar Instancia
IB_conexion = IB_Errores(guardar_errores=True)
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=100)
hilo_api = threading.Thread(target=ejecutar_api)
hilo_api.start()

# Desconectar el Cliente
IB_conexion.disconnect()
        
# Recordatorio:
#   - La API de IB notifica automáticamente cuando ocurre un error, como fallos de conexión o solicitudes incorrectas. Estos errores
#     pueden ser gestionados para registrarlos o tomar acciones correctivas inmediatas en el código.
