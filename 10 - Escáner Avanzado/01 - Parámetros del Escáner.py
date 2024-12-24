# -*- coding: utf-8 -*-
# Importar librerías
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import xml.etree.ElementTree as ET

# Clase que solicita los parámetros del Escáner
class IB_ParametrosEscaner(EWrapper, EClient):
    
    """
    Clase que se conecta a IB y solicita los parámetros disponibles para el Escáner
    """
    
    def __init__(self):
        
        """
        Constructor de la clase
        """
        
        EClient.__init__(self, self)
        self.parametros_escaner = None
        self.evento = threading.Event()
        
        
    def nextValidId(self, orderId):
        
        """
        Se llama cuando se obtiene el siguiente ID válido
        """
        
        self.evento.set()
        
    
    def scannerParameters(self, xml):
        
        """
        Recibe los parámetros del escáner en formato XML
        """
        
        # Almacenar
        self.parametros_escaner = xml
        print("Parámetros del escáner han sido recibidos:")
        print(xml)
        self.evento.set()
        
        
# Crear Instancia de la Clase
IB_conexion = IB_ParametrosEscaner()
IB_conexion.connect(host="127.0.0.1", port=7497, clientId=1)
thread = threading.Thread(target=IB_conexion.run)
thread.start()
IB_conexion.evento.wait()
IB_conexion.evento.clear()
        
# Solicitar los parámetros del Escáne
IB_conexion.reqScannerParameters()
IB_conexion.evento.wait()       
        
# Convertir a XML desde una cadena de texto
raiz = ET.fromstringlist(sequence=IB_conexion.parametros_escaner)      

print("Parámetros del Escáner Disponibles:")

print("\nMercados y categorías disponibles para el Escáner:")
for location in raiz.findall(".//Location"):
    ubicacion_nombre = location.find("displayName").text
    print(f" - {ubicacion_nombre}")       
        
# Atributos dentro de cada elemento encontrado
lista_location = list(raiz.findall(".//Location")[0])       
print(lista_location)        
        
print("Nombre:", lista_location[0].text)
print("Código:", lista_location[1].text)      
print("Instrumentos:", lista_location[2].text)
print("Mercado:", lista_location[3].text)
        
# Encontrar la ubicación específica (Ejemplo con "NYSE")
location_nyse = raiz.find(".//Location[displayName='NYSE']")      
print(list(location_nyse))        

# Obtener los diferentes instrumentos disponibles
print("\nInstrumentos disponibles para el Escáner:\n")
for instrumento in raiz.findall(".//Instrument"):
    nombre_instrumento = instrumento.find("name").text
    print(f" - {nombre_instrumento}")
 
# Atributos dentro de cada elemento
lista_instrumentos = list(raiz.findall(".//Instrument")[0])       
print(lista_instrumentos)        
print("Nombre:", lista_instrumentos[0].text)
print("Tipo:", lista_instrumentos[1].text)        
print("Filtros:", lista_instrumentos[2].text)
        
# Tipos de Escáner
print("\nTipos de Escaneo disponibles:")
for scan_type in raiz.findall(".//ScanType"):
    tipo_escaner = scan_type.find("scanCode").text
    print(f" - {tipo_escaner}")       
        
# Atributos dentro de cada elemento encontrado
lista_tipos_escaner = list(raiz.find(".//ScanType[scanCode='TOP_PERC_GAIN']"))     
print(lista_tipos_escaner)        
print("Tipo de Escáner:", lista_tipos_escaner[0].text)
print("Código del Scan:", lista_tipos_escaner[1].text)
print("Instumento:", lista_tipos_escaner[2].text)
print("Gratis con datos retrasados:", lista_tipos_escaner[8].text)
        
# Desconectar
IB_conexion.disconnect()      

# Recordatorio:
#   - El Escáner de IB permite identificar oportunidades de inversión mediante filtros personalizables. Facilita la búsqueda
#     de acciones, futuros y opciones basadas en métricas como el cambio porcentual y volumen, optimizando el análisis
#     en tiempo real.
