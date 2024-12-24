# -*- coding: utf-8 -*-
# Importar librerías
from IB_Trading import IB_Trading, Contract
import threading
import numpy as np
import matplotlib.pyplot as plt

# Clase que extrae las Volatilidades Implícitas
class IV_Options(IB_Trading):
    
    """
    Clase que nos ayuda a obtener las Volatilidades Implícitas para diferentes activos.
    """
    
    def __init__(self, ticker: str, vencimiento: str):
        
        """
        Constructor.
        """
        
        # Inicializar a IB_Trading
        IB_Trading.__init__(self, errors_verbose = False)
        # Definir Atributos
        self.ticker = ticker
        self.vencimiento = vencimiento
        self.volatilidad_implicita = {}
        self.evento = threading.Event()
        
    
    def tickOptionComputation(self, reqId, tickType, tickAttrib, impliedVol, delta, optPrice, pvDividend,
                              gamma, vega, theta, undPrice):
        
        """
        Este método se ejecuta cada vez que se recibe información de una opción específica, incluyendo
        la volatilidad implícita calculada.
        """
    
        # Agregar Petición
        if reqId not in self.volatilidad_implicita:
            self.volatilidad_implicita[reqId] = {"Activo": True, "Valor": ""}
        # Almacenar Información Recibida
        if (tickType == 83) and (self.volatilidad_implicita[reqId]["Activo"]) and (impliedVol is not None):
            print(f"Id de Petición: {reqId}, TickType: {tickType}, Volatilidad Implícita: {impliedVol}")
            self.volatilidad_implicita[reqId]["Valor"] = impliedVol
            self.volatilidad_implicita[reqId]["Activo"] = False
            # Cancelar Suscripción Activa
            self.cancelMktData(reqId=reqId)
            # Establecer Evento
            self.evento.set()
            
        
    def obtener_volatilidades_implicitas(self):
        
        """
        Este método obtiene todos los contratos de opciones disponibles para el activo y vencimiento especificado.
        Realiza peticiones de volatilidades implícitas para las opciones 'Call' y 'Put' en diferentes strikes
        y guarda los resultados en un diccionario para su posterior uso.
        """
    
        # Crear Contrato
        contrato = Contract()
        contrato.symbol = self.ticker
        contrato.secType = "OPT"
        contrato.exchange = "BOX"
        contrato.currency = "USD"
        contrato.multiplier = "100"
        contrato.lastTradeDateOrContractMonth = self.vencimiento
        # Obtener Contratos (Opciones Disponibles)
        contratos_opcion = self.reqContractDetails(reqId=0, contract=contrato)
        # Elegir 6 Contratos Random
        indices = np.arange(len(contratos_opcion))
        indices_random = np.random.choice(indices, size=6, replace=False).tolist()
        indices_random = sorted(indices_random)
        # Obtener Strikes
        contratos_opcion = np.array(contratos_opcion)[indices_random]
        strikes = sorted([contrato_detalles.contract.strike for contrato_detalles in contratos_opcion])
        # Realizar Peticiones de Volatilidades Implícitas (Calls)
        self.reqMarketDataType(marketDataType=3)
        for n, strike in enumerate(strikes):
            # Call
            contrato.right = "C"
            contrato.strike = strikes[n]
            contrato.exchange = "SMART"
            self.reqMktData(reqId=int(2 * n), contract=contrato, genericTickList="", snapshot=False, 
                            regulatorySnapshot=False, mktDataOptions=[])
            self.evento.wait()
            self.evento.clear()
        # Realizar Peticiones de Volatilidades Implícitas (Puts)
        self.reqMarketDataType(marketDataType=3)
        for n, strike in enumerate(strikes):
            # Put
            contrato.right = "P"
            contrato.strike = strikes[n]
            contrato.exchange = "SMART"
            self.reqMktData(reqId=int(2 * n + 1), contract=contrato, genericTickList="106", snapshot=False, 
                            regulatorySnapshot=False, mktDataOptions=[])
            self.evento.wait()
            self.evento.clear()
            
        # Guardar Strikes utilizados
        self.strikes = strikes

        return self.volatilidad_implicita
    
    
# Crear Instancia y Conectarse
IB_vol_impl = IV_Options(ticker="AAPL", vencimiento="20260116")
IB_vol_impl.connect(host="127.0.0.1", port=7497, clientId=1)
# Realizar Petición
volatilidades_implicitas = IB_vol_impl.obtener_volatilidades_implicitas()
calls_iv = [volatilidades_implicitas[0]["Valor"], volatilidades_implicitas[2]["Valor"], volatilidades_implicitas[4]["Valor"], 
            volatilidades_implicitas[6]["Valor"], volatilidades_implicitas[8]["Valor"], volatilidades_implicitas[10]["Valor"]]  
puts_iv = [volatilidades_implicitas[1]["Valor"], volatilidades_implicitas[3]["Valor"], volatilidades_implicitas[5]["Valor"], 
            volatilidades_implicitas[7]["Valor"], volatilidades_implicitas[9]["Valor"], volatilidades_implicitas[11]["Valor"]]  
strikes = IB_vol_impl.strikes
# Graficar
fig, axes = plt.subplots(ncols=2, nrows=1, figsize=(22, 10))

# Graficar Calls
axes[0].plot(strikes, calls_iv, color="dodgerblue", marker="o", markersize=8, linewidth=2, label="Calls IV")
axes[0].set_title("Volatilidad Implícita - Calls", fontsize=18, weight="bold")
axes[0].set_xlabel("Strike", fontsize=14, weight="bold")
axes[0].set_ylabel("Volatilidad Implícita", fontsize=14, weight="bold")
axes[0].grid(True, linestyle="--", alpha=0.7)
axes[0].legend()

# Graficar Puts
axes[1].plot(strikes, puts_iv, color="tomato", marker="s", markersize=8, linewidth=2, label="Puts IV")
axes[1].set_title("Volatilidad Implícita - Puts", fontsize=18, weight="bold")
axes[1].set_xlabel("Strike", fontsize=14, weight="bold")
axes[1].set_ylabel("Volatilidad Implícita", fontsize=14, weight="bold")
axes[1].grid(True, linestyle="--", alpha=0.7)
axes[1].legend()

# Ajustar el espacio entre subgráficos
plt.tight_layout()

# Mostrar el gráfico
plt.show()

# Recordatorio:
#   - El volatility skew es una representación gráfica que muestra cómo varía la volatilidad implícita de las opciones según su
#     precio de ejercicio (strike).
#   - Las opciones cuyo strike está fuera del dinero o en posiciones más alejadas del precio actual del activo subyacente tienden
#     a tener una volatilidad implícita menor. Esto se traduce en un menor costo inicial para el comprador de la opción. Si un
#     trader espera que el precio del activo subyacente se mueva de manera significativa, comprar opciones con menor volatilidad
#     implícita puede ser una estrategia más rentable, ya que estas opciones son más baratas en términos de prima.
