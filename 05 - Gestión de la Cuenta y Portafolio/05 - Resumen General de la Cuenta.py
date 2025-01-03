# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import pandas as pd

# Clase que genera un reporte de la cuenta
class IB_ReporteGeneral(EClient, EWrapper):
    
    """
    Clase que permite interactuar con la API de IB.
    Recopila datos de la cuenta, posiciones abiertas y otros datos relevantes
    """
    
    def __init__(self, account: str):
        
        """
        Constructor que inicializa la clase y crea contenedores para los datos de la cuenta, las posiciones
        y el resumen de la cuenta
        """
        
        # Inicializar
        EClient.__init__(self, self)
        # Atributos
        self.account = account
        self.pnl_list = []
        self.posiciones = []
        self.resumen_cuenta = {}
        self.datos_informe = {}
        self.evento = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Método que recibe el siguiente ID Válido
        """
        
        self.orderId = orderId
        self.evento.set()
        
        
    def accountSummary(self, reqId, account, tag, value, currency):
        
        """
        Método que recibe el resumen de la cuenta
        """
        
        self.resumen_cuenta[tag] = (value, currency)
        
        
    def accountSummaryEnd(self, reqId):
        
        """
        Método llamado al finalizar la obtención del resumen de la cuenta
        """
        
        self.datos_informe["Resumen de la Cuenta"] = {etiqueta: f"{valor} {moneda}"
                                                      for etiqueta, (valor, moneda) in self.resumen_cuenta.items()}
        self.evento.set()
        
        
    def position(self, account, contract, position, avgCost):
        
        """
        Método que recibe información sobre las posiciones abiertas
        """
        
        # Almacenar Posiciones
        self.posiciones.append({
            
            "Simbolo": contract.symbol,
            "Posicion": position,
            "Costo Promedio": avgCost
            
            })
        
        
    def positionEnd(self):
        
        """
        Método llamado al finalizar la obtención de posiciones abiertas
        """
        
        self.datos_informe["Posiciones Abiertas"] = self.posiciones
        # Cancelar Suscripción
        self.cancelPositions()
        self.evento.set()
        
        
    def pnl(self, reqId, dailyPnL, unrealizedPnL, realizedPnL):
        
        """
        Método que recibe la ganancia y pérdida de la cuenta
        """
        
        # Almacenar en lista
        self.pnl_list.append({
            
            "Gan/Per Diaria": dailyPnL,
            "Gan/Per No Realizada": unrealizedPnL,
            "Gan/Per Realizada": realizedPnL
            
            })
        # Detener Suscripción
        self.cancelPnL(reqId=reqId)
        self.evento.set()
        
        
    def generar_informe(self):
        
        """
        Método que genera un informe consolidado que incluye el resumen de la cuenta, las posiciones abiertas y otros
        datos de la cuenta. Muestra el informe en la consola y exporta los datos en archivos CSV.
        """
        
        # Generar Solicitudes
        self.evento.clear()
        self.reqAccountSummary(reqId=0, groupName="All", tags="AccountType,NetLiquidation,TotalCashValue")
        self.evento.wait()
        self.evento.clear()
        self.reqPositions()
        self.evento.wait()
        self.evento.clear()
        self.reqPnL(reqId=0, account=self.account, modelCode="")
        self.evento.wait()
        self.evento.clear()
        
        # Crear DataFrames para cada sección del informe
        resumen_cuenta_df = pd.DataFrame(self.datos_informe["Resumen de la Cuenta"].items(), columns=["Etiqueta", "Valor y Moneda"])
        posiciones_df = pd.DataFrame(self.datos_informe["Posiciones Abiertas"])
        pnl_df = pd.DataFrame(self.pnl_list)
        
        # Mostrar resultados en un solo lugar
        print("\n========= Informe de la Cuenta =========")
        print("\nResumen de la Cuenta:")
        print(resumen_cuenta_df)
        
        print("\nPosiciones Abiertas:")
        print(posiciones_df)
        
        print("\nPnL Cuenta:")
        print(pnl_df)
        
        # Exportar a CSV
        resumen_cuenta_df.to_csv("resumen_cuenta.csv", index=False)
        posiciones_df.to_csv("posiciones_abiertas.csv", index=False)
        pnl_df.to_csv("pnl.csv", index=False)
        
        print("\nLos datos han sido exportados a archivos CSV.")
        
        
# Conexión
IB_app = IB_ReporteGeneral(account="DUE273425")
IB_app.connect(host="127.0.0.1", port=7497, clientId=1)
threading.Thread(target=IB_app.run).start()
IB_app.evento.wait()

# Generar Informe
IB_app.generar_informe()

# Desconectar
IB_app.disconnect()
        
# Recordatorio:
#   - Al ejecutar múltiples peticiones aa la API de IB, asegúrate de que cada proceso se complete adecuadamente
#     antes de proceder al siguiente. Utiliza mecanismos de sincronización, como eventos de threading, para gestionar
#     las solicitudes y garantizar la correcta recopilación de datos.
