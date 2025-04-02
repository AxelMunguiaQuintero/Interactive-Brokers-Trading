# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import pandas as pd
import threading
import time

# Clase que obtiene la Ganancia/Pérdida de la Cuenta
class IB_GananciaPerdida(EWrapper, EClient):
    
    """
    Clase que establece una conexión a la API de Interactive Brokers y obtiene las ganancias o pérdidas de la cuenta
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.ganancias_perdidas = []
        
        
    def pnl(self, reqId, dailyPnL, unrealizedPnL, realizedPnL):
        
        """
        Método que recibe el PnL y almacena la información
        """
        
        # Guardar y mostrar en consola
        self.ganancias_perdidas.append(
            {
                "ID": reqId,
                "Gan/Per Diaria": dailyPnL,
                "Gan/Per No Realizada": unrealizedPnL,
                "Gan/Per Realizada": realizedPnL
                
                }
            
            )
        print("Ganancia/Pérdida Diaria:", dailyPnL)
        print("Ganancia/Pérdida No Realizada:", unrealizedPnL)
        print("Ganancia/Pérdida Realizada:", realizedPnL)
        
        
# Generar Conexión
IB_conexion = IB_GananciaPerdida()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_conexion.run)
api_thread.start()
time.sleep(2)
        
# Realizar Petición
IB_conexion.reqPnL(reqId=1, account="No. Cuenta", modelCode="")
time.sleep(3)
# Detener la actualización de la solicitud de las ganancias o pérdidas
IB_conexion.cancelPnL(reqId=1)     
        
# Obtener y mostrar ganancias/pérdidas
df_ganancias_perdidas = pd.DataFrame(IB_conexion.ganancias_perdidas).set_index("ID")
print(df_ganancias_perdidas)        

# Desconectar
IB_conexion.disconnect()
api_thread.join()

# Recordatorio:
#   - El PnL Diario refleja las ganancias o pérdidas generadas durante el día, considerando los cambios de precio de los
#     activos que tienes en tu portafolio. Es útil para monitorear el desempeño diario de tus inversiones.
#   - El PnL No Realizado muestra las ganancias o pérdidas de posiciones abiertas, basadas en el precio actual del mercado,
#     pero que aún no se han concretado porque no se ha cerrado la posición.
#   - El PnL Realizado se refiere a las ganancias o pérdidas que ya han sido concretadas, es decir, cuando una posición
#     ha sido cerrada y el resultado es definitivo.
