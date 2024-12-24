# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading

# Múltiples Clientes
class IB_Clientes(EWrapper, EClient):
    
    """
    Clase que gestiona la conexión a IB con múltiples clientes
    """
    
    def __init__(self, client_id):
        
        """
        Constructor
        """
        
        # Inicializar EClient
        EClient.__init__(self, self)
        # Atributos
        self.clientId = client_id
        self.evento = threading.Event()
        
        
    def nextValidId(self, orderId: int):
        
        """
        Método que se llama cuando se establece la conexión de la API.
        """
        
        print(f"Cliente {self.clientId} está conectado. Siguiente ID Válido: {orderId}")
        # Cambiar estado interno del Evento
        self.evento.set()
        

# Correr API
def ejecutar_API(app):

    """
    Ejecuta el método de run() de la clase IBAPI
    """    
    
    app.run()
    
# Número de Clientes
NUM_CLIENTES = 3

# Crear y conectar múltiples instancias de Clientes
clientes = []
for i in range(1, NUM_CLIENTES + 1):
    # Crear una Conexión con un ID único
    IB_Conn = IB_Clientes(client_id=i)
    IB_Conn.connect(host="127.0.0.1", port=7497, clientId=i) 
    # Crear Hilo para cada Cliente
    hilo_api = threading.Thread(target=ejecutar_API, args=(IB_Conn, ))
    hilo_api.start()
    clientes.append(IB_Conn)

# Esperar a que todos los clientes se conecten
for cliente in clientes:
    cliente.evento.wait()
print("¡Conexión exitosa!")

# Desconectar todos los clientes
for cliente  in clientes:
    print(f"Cliente {cliente.clientId} está desconectado")
    cliente.disconnect()
    
# Recordatorio:
#   - Puedes conectar varios clientes a la API de IB usando diferentes identificadores. Cada clientes puede enviar solicitudes
#     independientes y recibir datos simultáneamente.
#   - Cada cliente conectado funciona de manera autónoma, permitiendo realizar operaciones separadas, como consultar diferentes mercados
#     o enviar órdenes distintas al mismo tiempo.
