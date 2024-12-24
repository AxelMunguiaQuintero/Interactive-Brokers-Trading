# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import pandas as pd
import threading
from datetime import datetime, timedelta
import time

# Clase que ejecuta órdenes de Opciones en el mercado
class IB_OrdenesOpciones(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y ejecuta órdenes de Opciones en el mercado
    """
    
    def __init__(self):
        
        """
        Constructor
        """
        
        # Inicializar Clase
        EClient.__init__(self, self)
        self.order_id = None
        self.evento = threading.Event()
        self.contrato = []
        
        
    def nextValidId(self, orderId):
        
        """
        Recibe el siguiente ID válido para una orden
        """
        
        self.order_id = orderId
        self.evento.set()
        
        
    def contractDetails(self, reqId, contractDetails):
        
        """
        Método que almacena la información del Contrato solicitado
        """
        
        self.contrato.append({
            
            "Precio de Ejercicio": contractDetails.contract.strike,
            "Tipo": contractDetails.contract.right,
            "Fecha de Vencimiento": contractDetails.contract.lastTradeDateOrContractMonth,
            "Multiplicador": contractDetails.contract.multiplier,
            "Detalles Contrato": contractDetails
            
            })
        
        
    def contractDetailsEnd(self, reqId):
        
        """
        Método que se manda a llamar cuando la información de todos los contratos ha sido procesada
        """
        
        self.evento.set()
        
        
# Establecer Conexión
IB_opciones = IB_OrdenesOpciones()
IB_opciones.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_opciones.run)
api_thread.start()
IB_opciones.evento.wait()
IB_opciones.evento.clear()

# Crear Contrato
contrato = Contract()
contrato.symbol = "AAPL"
contrato.secType = "OPT"
contrato.exchange = "BOX"
contrato.currency = "USD"
# Definir como fecha el siguiente Viernes
fecha_hoy = datetime.now()
dias_faltantes = (4 - fecha_hoy.weekday()) + 7
fecha_vencimiento = (fecha_hoy + timedelta(days=dias_faltantes)).strftime("%Y%m%d")
contrato.lastTradeDateOrContractMonth = fecha_vencimiento

# Solicitar Contratos de Opciones Vigentes
IB_opciones.reqContractDetails(reqId=0, contract=contrato)
IB_opciones.evento.wait()
IB_opciones.evento.clear()
        
# Convertir a DataFrame
opciones_call_put = pd.DataFrame(IB_opciones.contrato).sort_values(by=["Precio de Ejercicio", "Tipo"]).reset_index(drop=True)       
print(opciones_call_put)        
        
# Seleccionar el Precio de Ejercicio a la mitad de los datos
indice_mitad = opciones_call_put.shape[0] // 2      
# Seleccionar Ambas Opciones (Call y Put)
precio_ejercicio = opciones_call_put.iloc[indice_mitad]["Precio de Ejercicio"]
print("Precio de Ejercicio:", precio_ejercicio)        
call_option = opciones_call_put[(opciones_call_put["Precio de Ejercicio"] == precio_ejercicio) & (opciones_call_put["Tipo"] == "C")]        
print(call_option.T)        
put_option = opciones_call_put[(opciones_call_put["Precio de Ejercicio"] == precio_ejercicio) & (opciones_call_put["Tipo"] == "P")]        
print(put_option.T)        
        
# Función que crea orden
def crear_orden(action: str, lmtPrice: float):

    """
    Función que crea una orden de compra o venta con precio límite
    """        
    
    orden = Order()
    orden.action = action
    orden.orderType = "LMT"
    orden.totalQuantity = 1
    orden.lmtPrice = lmtPrice
    orden.eTradeOnly = ""
    orden.firmQuoteOnly = ""
    
    return orden

# Crear Funciones de Diferentes Contratos para las Órdenes:
    
# Long Call: Un Long Call es una posición compradora en una opción call, otorgando derecho a comprar el activo subyacente
#            a un precio específico antes de la expiración, beneficiándose de alzas en el precio del activo subyacente.
def Long_Call(lmtPrice):
    
    """
    Una función que genera una orden de compra de un Call
    """
        
    # Crear Contrato
    contrato = call_option["Detalles Contrato"].iloc[0].contract
    # Obtener Orden
    orden = crear_orden(action="BUY", lmtPrice=lmtPrice)
    # Obtener siguiente ID válido
    IB_opciones.reqIds(-1)
    IB_opciones.evento.wait()
    IB_opciones.evento.clear()
    # Ejecutar Orden
    IB_opciones.placeOrder(orderId=IB_opciones.order_id, contract=contrato, order=orden)
    
# Short Call: Un Short Call es una posición vendedora en una opción call, que obliga a vender el activo subyacente a un precio
#             específico si el comprador ejerce, beneficiándose cuando el precio cae o permanece bajo.
def Short_Call(lmtPrice):
    
    """
    Una función que genera una orden de venta de un Call
    """
        
    # Crear Contrato
    contrato = call_option["Detalles Contrato"].iloc[0].contract
    # Obtener Orden
    orden = crear_orden(action="SELL", lmtPrice=lmtPrice)
    # Obtener siguiente ID válido
    IB_opciones.reqIds(-1)
    IB_opciones.evento.wait()
    IB_opciones.evento.clear()
    # Ejecutar Orden
    IB_opciones.placeOrder(orderId=IB_opciones.order_id, contract=contrato, order=orden)
    
# Long Put: Un Long Put es una posición compradora en una opción Put, otorgando derecho a vender el activo subyacente a un
#           precio específico antes de la expiración, beneficiándose si el precio baja.
def Long_Put(lmtPrice):
    
    """
    Una función que genera una orden de compra de un Put
    """
        
    # Crear Contrato
    contrato = put_option["Detalles Contrato"].iloc[0].contract
    # Obtener Orden
    orden = crear_orden(action="BUY", lmtPrice=lmtPrice)
    # Obtener siguiente ID válido
    IB_opciones.reqIds(-1)
    IB_opciones.evento.wait()
    IB_opciones.evento.clear()
    # Ejecutar Orden
    IB_opciones.placeOrder(orderId=IB_opciones.order_id, contract=contrato, order=orden)
    
# Short Put: Un Short Put es una posición vendedora en una opción put, obligando a comprar el activo subyacente si el comprador
#            ejerce, beneficiándose si el precio se mantiene estable o sube.
def Short_Put(lmtPrice):
    
    """
    Una función que genera una orden de venta de un Put
    """
        
    # Crear Contrato
    contrato = put_option["Detalles Contrato"].iloc[0].contract
    # Obtener Orden
    orden = crear_orden(action="SELL", lmtPrice=lmtPrice)
    # Obtener siguiente ID válido
    IB_opciones.reqIds(-1)
    IB_opciones.evento.wait()
    IB_opciones.evento.clear()
    # Ejecutar Orden
    IB_opciones.placeOrder(orderId=IB_opciones.order_id, contract=contrato, order=orden)
        
# Ejecutar Órdenes

precio_limite_long_call = 44
Long_Call(lmtPrice=precio_limite_long_call)
time.sleep(5)

precio_limite_short_call = 43
Short_Call(lmtPrice=precio_limite_short_call)
time.sleep(5)

precio_limite_short_put = 0.05
Short_Put(lmtPrice=precio_limite_short_put)
time.sleep(5)

precio_limite_long_put = 0.08
Long_Put(lmtPrice=precio_limite_long_put)
time.sleep(5)
        
# Recordatorio:
#   - Las Cadenas de Opciones son listas completas de todas las opciones disponibles para un activo subyacente específico, que incluye
#     una variedad de precios de ejercicio y fechas de vencimiento. Estas cadenas suelen estar organizadas en dos tipos principales
#     de opciones: calls y puts. Cada combinación de precio de ejercicio y fecha de vencimiento define una opción individual en la cadena.
