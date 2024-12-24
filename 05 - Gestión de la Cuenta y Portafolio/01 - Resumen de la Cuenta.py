# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time

# Clase que obtiene el Resumen de la Cuenta
class IB_CuentaResumen(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y obtiene el resumen general de la cuenta
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        EClient.__init__(self, self)
        self.cuenta_resumen = []
        self.cuenta_evento = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Recibe el próximo ID válido
        """
        
        self.next_order_id = orderId
        
    
    def accountSummary(self, reqId, account, tag, value, currency):
        
        """
        Método que se llama cuando se recibe el resumen de la cuenta
        """
        
        print(f"Cuenta: {account}, Etiqueta: {tag}, Valor: {value}, Moneda: {currency}")
        # Almacenar los datos recibidos
        self.cuenta_resumen.append((account, tag, value, currency))
        
    
    def accountSummaryEnd(self, reqId):
        
        """
        Se llama cuando se recibe el resumen completo de la cuenta
        """
        
        print("Se recibió el resumen completo de la cuenta")
        self.cuenta_evento.set()
        
        
# Conectar al Servidor de la API
IB_conn = IB_CuentaResumen()
IB_conn.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_conn.run)
api_thread.start()

# Esperar
time.sleep(3)
        
# Solicitar resumen de la cuenta de ciertas variables
IB_conn.reqAccountSummary(reqId=1, groupName="All", tags="AccountType,NetLiquidation,TotalCashValue")
IB_conn.cuenta_evento.wait()
# Cancelar Suscripción
IB_conn.cancelAccountSummary(reqId=1)
        
# Nuevo resumen de la cuenta
IB_conn.cuenta_evento.clear()
IB_conn.reqAccountSummary(reqId=1, groupName="All", tags="$LEDGER:USD")
IB_conn.cuenta_evento.wait()
# Cancelar Suscripción
IB_conn.cancelAccountSummary(reqId=1)
        
# Account Summary Tags (Doc Actualizada): https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/#account-summary-tags
# Account Summary Tags (Doc Actualizada): https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a3e0d55d36cd416639b97ee6e47a86fe9

# Desconectar
IB_conn.disconnect()
api_thread.join()

# Recordatorio:
#   - Hay ciertas solicitudes en IB (como reqAccountSummary) que permanecen activas y envían actualizaciones continuas.
#     Es importante cancelar la suscripción cuando ya no se necesiten los datos, para evitar recibir actualizaciones innecesarias
#     y optimizar el uso de recursos.
