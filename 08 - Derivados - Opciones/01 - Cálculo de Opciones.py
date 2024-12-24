# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd
import numpy as np
from scipy.stats import norm
import time

# Clase de IB
class IB_ObtenerPrecio(EClient, EWrapper):
    
    """
    Clase que permite descargar Datos históricos de un activo
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.precios = {}
        self.precio_reciente = {}
        self.evento = threading.Event()
        
    
    def historicalData(self, reqId, bar):
        
        """
        Este método recibe y almacena los datos históricos
        """
        
        # Almacenar Datos
        if reqId not in self.precios:
            self.precios[reqId] = []
        self.precios[reqId].append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
        
        
    def historicalDataEnd(self, reqId, start, end):
        
        """
        Este método se llama cuando ya se han recibido y procesado todos los datos
        """
        
        # Notificar y almacenar el precio más reciente
        self.precio_reciente[reqId] = self.precios[reqId][-1][4]
        self.evento.set()
        
        
# Clase de Operaciones para el cálculo de Primas de Opciones
class Operaciones:
    
    """
    Clase para calcular operaciones básicas y necesarias para opciones Call y Put utilizando el modelo de Black-Scholes.
    """
        
    def __init__(self, S_o: float = None, K: float = None, r: float = None, q: float = 0.0, T: float = None, sigma: float = None):
        
        """
        Inicializa la clase de Operaciones con los parámetros proporcionados.
        
        Parámetros:
        -----------
        S_o: float
            Precio inicial del activo subyacente.
            
        K: float
            Precio de ejercicio de la opción
            
        r: float
            Tasa libre de riesgo anual (en forme decial, por ejemplo, 0.05 para 5%).
            
        q: float
            Tasa de descuento anual (en forma decimal). En este ejemplo, se asume que es 0.
            
        T: float
            Tiempo hasta el vencimiento de la opción, expresado en años
            
        sigma: float
            Volatilidad del activo subyacente (en forma decimal, por ejemplo, 0.20 para 20%).
        """
        
        # Parámetros iniciales
        self.S_o = S_o
        self.K = K
        self.r = r
        self.q = q
        self.T = T
        self.sigma = sigma
        
        
    def d1(self):
        
        """
        Calcula d1 para la Opción usando la fórmula BS.
        """
        
        return (np.log(self.S_o / self.K) + (self.r - self.q + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
    
    
    def d2(self):
        
        """
        Calcula d2 para la Opción usando la fórmula BS.
        """
        
        return (np.log(self.S_o / self.K) + (self.r - self.q - 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
    
    
    def N(self, x):
        
        """
        Calcula el área acumulativa bajo la curva normal estándar para un valor de x.
        """
        
        return norm.cdf(x, loc=0, scale=1)
    
    
    def Black_Scholes(self, tipo_opcion: str = "call"):
        
        """
        Calcula el valor de la prima de la opción.
        """
        
        if tipo_opcion.lower() == "call":
            prima_precio = self.S_o * np.exp(-self.q * self.T) * self.N(self.d1()) - \
                self.K * np.exp(-self.r * self.T) * self.N(self.d2())
        elif tipo_opcion.lower() == "put":
            prima_precio = self.K * np.exp(-self.r * self.T) * self.N(-self.d2()) - \
                self.S_o * np.exp(-self.q * self.T) * self.N(-self.d1())
        else:
            raise ValueError("El valor pasado es diferente de 'call' o 'put'")
            
        return prima_precio
    
    
# Conectar a la API
IB_conn = IB_ObtenerPrecio()
IB_conn.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_conn.run)
api_thread.start()
time.sleep(3)

# Definir el instrumento
activo = "AMZN"

# Crear el contrato para obtener datos
contrato = Contract()
contrato.symbol = activo
contrato.secType = "STK"
contrato.exchange = "SMART"
contrato.currency = "USD"

# Obtener Precios
IB_conn.reqHistoricalData(reqId=0, contract=contrato, endDateTime="", durationStr="1 Y", barSizeSetting="1 day", whatToShow="ADJUSTED_LAST",
                          useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[])
IB_conn.evento.wait()
IB_conn.evento.clear()

# Cambiar estructura de los datos
datos = pd.DataFrame(data=IB_conn.precios[0], columns=["Date", "Open", "High", "Low", "Close", "Volume"])
datos["Rendimiento"] = datos["Close"].pct_change()

# Parámetros de la opción
S_0 = IB_conn.precio_reciente[0] # Precio del activo subyacente
K = S_0 * 1.05 # Precio de ejercicio
T = 30 / 365 # Tiempo hasta el vencimiento (días a años) -> 1 mes
r = 0.05 # Tasa de interés libre de riesgo
sigma = datos["Rendimiento"].std() * np.sqrt(252) # Volatilidad del activo subyacente

# Generar Instancia de Operaciones
bs_operaciones = Operaciones(S_o=S_0, K=K, r=r, q=0, T=T, sigma=sigma)

# Calcular Precios
prima_call = bs_operaciones.Black_Scholes(tipo_opcion="call")
prima_put = bs_operaciones.Black_Scholes(tipo_opcion="put")

# Mostrar resultados
print("Precio Actual:", S_0)
print("Precio de Ejercicio:", K)
print(f"Precio de Opción Call: {prima_call:.2f}")
print(f"Precio de Opción Put: {prima_put:.2f}")

# Recordatorio:
#   - Las opciones se dividen en dos tipos principales: Call y Put. Las opciones Call otorgan al comprador el derecho a comprar un activo
#     a un precio específico, mientras que las Put permiten venderlo, ofreciendo flexibilidad en estrategias de inversión.
#   - El modelo de BS es una de las fórmulas más utilizadas para valorar opciones. Este modelo considera factores como el precio del activo
#     subyacente, el precio de ejercicio, la volatilidad y el tiempo hasta el vencimiento para estimar el precio justo.
