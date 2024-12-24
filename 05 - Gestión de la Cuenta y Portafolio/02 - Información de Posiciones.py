# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import pandas as pd
import time

# Clase que muestra las posiciones de nuestro Portafolio
class IB_Posiciones(EWrapper, EClient):
    
    """
    Clase que implementa la interfaz de la API de Interactive Brokers para solicitar y manejar información sobre las posiciones 
    de la cuenta
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.posiciones = []
        self.posiciones_recibidas = threading.Event()
        
        
    def position(self, account, contract, position, avgCost):
        
        """
        Método que recibe la información de cada posición que conforma nuestro portafolio.
        """
        
        self.posiciones.append((account, contract.symbol, contract.secType, position, avgCost))
        
        
    def positionEnd(self):
        
        """
        Método que se llama cuando se han recibido todas las posiciones
        """
        
        # Dar formato
        self.posiciones_df = pd.DataFrame(self.posiciones, columns=["Cuenta", "Instrumento", "Tipo de Activo",
                                                                    "Cantidad", "Costo Promedio"])
        self.posiciones_df.set_index("Cuenta", inplace=True)
        print("Se recibieron todas las posiciones")
        self.posiciones_recibidas.set()
        
        
# Crear una instancia de la clase
IB_con = IB_Posiciones()
IB_con.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_con.run)
api_thread.start()
time.sleep(2)

# Solicitar Posiciones
IB_con.posiciones_recibidas.clear()
IB_con.reqPositions()
IB_con.posiciones_recibidas.wait()

# Mostrar Posiciones
posiciones_df = IB_con.posiciones_df
print(posiciones_df)
        
# Calcular el valor total de cada posición
posiciones_df["Valor Total"] = posiciones_df["Cantidad"] * posiciones_df["Costo Promedio"]   
        
# Calcular el valor total de todas las posiciones
valor_total = posiciones_df["Valor Total"].sum()     

print(f"\nValor total de posiciones: {valor_total:.2f}")        
        
# Desconectar
IB_con.disconnect()

# Recordatorio:
#   - La composición de cada instrumento en nuestro portafolio nos permite evaluar su rendimiento individual, identificar riesgos
#     y ajustar nuestras estrategias de inversión en consecuencia.
