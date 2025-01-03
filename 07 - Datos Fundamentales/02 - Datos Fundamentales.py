# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import os

# Clase que gestiona la solicitud de datos fundamentales a la API de IB
class IB_fundamentalData(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y obtiene datos fundamentales, almacenando los resultados en archivos locales
    """
    
    def __init__(self):
        
        """
        Constructor de la clase. Inicializa el cliente y la estructura de datos para almacenar la información
        obtenida de los reportes fundamentales.
        """
        
        EClient.__init__(self, self)
        # Diccionario con los tipos de reporte y los archivos donde se almacenará la información
        self.reportes = {
            "ReportSnapshot": "resumen_empresa.xml",
            "ReportsFinSummary": "resumen_financiero.xml",
            "ReportRatios": "ratios_financieros.xml",
            "ReportsFinStatements": "estados_financieros.xml",
            "RESC": "estimaciones_analistas.xml"
            }
        
        
    def fundamentalData(self, reqId, data):
        
        """
        Función callback que procesa los datos fundamentales recibidos de la API de IB.
        
        Parámetros:
            reqId: ID de la solicitud realizada.
            data: Datos fundamentales en formato XML obtenidos
        """
        
        # Determinar el tipo de reporte a partir del reqId
        report_type = list(self.reportes.keys())[reqId]
        print(f"Reporte {report_type} recibido")
        # Almacenar Datos
        self.guardar_datos(report_type, data)
        
        
    def guardar_datos(self, report_type, data):
        
        """
        Guarda los datos recibidos de cada reporte en el archivo correspondiente
        
        Parámetros:
            report_type: Tipo de reporte fundamental recibido.
            data: Datos fundamentales en formato XML obtenidos
        """
        
        # Obtener el nombre del archivo
        filename = self.reportes[report_type]
        filepath = os.path.join(os.getcwd(), filename)
        
        # Abrir el archivo en modo escritura
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(data)
            
        print("Datos del reporte {} han sido guardados en {}".format(report_type, filepath))
        
        
    def solicitar_reportes(self, contract):
        
        """
        Solicita todos los tipos de reportes fundamentales disponibles para un contrato dado.
        
        Parámetros:
            contract: Objeto Contract que contiene la información del activo (por ejemplo, una acción)
        """
        
        # Iterar sobre los tipos de reportes en el diccionario
        for idx, report_type in enumerate(self.reportes.keys()):
            print(f"\nSolicitando el reporte {report_type}...")
            # Solicitar cada reporte con su ID de la Solicitud
            self.reqFundamentalData(reqId=idx, contract=contract, reportType=report_type, fundamentalDataOptions=[])
            time.sleep(5)
            

# Conectar a la API
IB_FD = IB_fundamentalData()
IB_FD.connect(host="127.0.0.1", port=7497, clientId=1)
api_thread = threading.Thread(target=IB_FD.run)
api_thread.start()
time.sleep(3)
        
# Crear contrato para la acción deseada
contrato_activo = Contract()
contrato_activo.symbol = "AMZN"     
contrato_activo.secType = "STK"
contrato_activo.exchange = "SMART"
contrato_activo.currency = "USD"

# Solicitar todos los reportes fundamentales
IB_FD.solicitar_reportes(contract=contrato_activo)        
        
# Desconectarse de la API
IB_FD.disconnect()

# Recordatorio:
#   - ReportSnapshot (resumen de la empresa): Proporciona una visión general de la empresa, su estructura y sus principales actividades
#     comerciales.
#   - ReportsFinSummary (resumen financiero): Resume los ingresos, utilidaades y márgenes clave para evaluar el rendimiento financiero
#     de la empresa.
#   - ReportRatios (ratios financieros): Incluye indicadores financieros como liquidez, deuda-capital y rentabilidad, útiles para
#     comparaciones de rendimiento.
#   - ReportsFinStatements (estados financieros): Presenta el balance general, estado de resultados y flujo de caja detallados.
#   - RESC (estimaciones de analistas): Contiene proyecciones de ingresos, utilidades y crecimiento futuro según analistas financieros.
