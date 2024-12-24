# -*- coding: utf-8 -*-
# Importar librerías
import xml.etree.ElementTree as ET
import json

# Leer archivos

# Resumen Empresa
resumen_empresa = ET.parse("resumen_empresa.xml", parser=ET.XMLParser(encoding="utf-8"))
resumen_empresa_root = resumen_empresa.getroot()
# Extraer Datos
company_name = resumen_empresa_root.find("CoIDs").find("CoID[@Type='CompanyName']").text
business_summary = resumen_empresa_root.find("TextInfo").find("Text[@Type='Business Summary']").text
print("Nombre de la empresa:", company_name)
print("Resumen del Negocio:", business_summary)

# Resumen Financiero
resumen_financiero = ET.parse("resumen_financiero.xml", parser=ET.XMLParser(encoding="utf-8"))
resumen_financiero_root = resumen_financiero.getroot()
# Extraer Datos
eps_0 = list(resumen_financiero_root.find("EPSs"))[0].text
tr_0 = list(resumen_financiero_root.find("TotalRevenues"))[0].text
print("Earnings Per Share más reciente:", eps_0)
print("Ingresos Totales más recientes:", tr_0)

# Resumen Estimaciones
estimaciones_analistas = ET.parse("estimaciones_analistas.xml", parser=ET.XMLParser(encoding="utf-8"))
estimaciones_analistas_root = estimaciones_analistas.getroot()
# Extraer Datos
estimaciones = estimaciones_analistas_root.find("ConsEstimates").find("NPEstimates").find("NPEstimate")
estimacion_baja = estimaciones.find("ConsEstimate[@type='Low']").find("ConsValue").text
estimacion_alta = estimaciones.find("ConsEstimate[@type='High']").find("ConsValue").text
estimacion_promedio = estimaciones.find("ConsEstimate[@type='Mean']").find("ConsValue").text
estimacion_mediana = estimaciones.find("ConsEstimate[@type='Median']").find("ConsValue").text

print("Se espera que el precio objetivo del activo sea (dentro de un año):")
print("Estimación esperada alta: {} USD".format(estimacion_alta))
print("Estimación esperada baja: {} USD".format(estimacion_baja))
print("Estimación esperada promedio: {} USD".format(estimacion_promedio))
print("Estimación esperada mediana: {} USD".format(estimacion_mediana))

# Convertir XML a Diccionario
def XMLtoDict(elemento) -> dict:
    
    """
    Convierte un elemento XML en un diccionario, manteniendo tanto los atributos como los elementos hijos del XML.

    Parámetros:
    - elemento (xml.etree.ElementTree.Element): Elemento XML que se desea convertir a un diccionario.

    Retorno:
    - dict: Un diccionario que representa la estructura del XML, donde cada nodo se convierte en una clave,
            y sus atributos, hijos o contenido de texto se almacenan en valores correspondientes.
    """
    
    data = {}
    if elemento.attrib:
        data["attributes"] = elemento.attrib
        
    if len(elemento):
        children_data = {}
        for child in elemento:
            child_data = XMLtoDict(child)
            
            if child.tag not in children_data:
                children_data[child.tag] = child_data
            else:
                if isinstance(children_data[child.tag], list):
                    children_data[child.tag].append(child_data)
                else:
                    children_data[child.tag] = [children_data[child.tag], child_data]
                    
        data["children"] = children_data
    else:
        data = elemento.text or ""
        
        
    return {elemento.tag: data}


# Ejemplo: Libro
libros_xml = ET.parse("libros.xml", parser=ET.XMLParser(encoding="utf-8"))
libros_xml_root = libros_xml.getroot()
libros_dict = XMLtoDict(libros_xml_root)
print(json.dumps(libros_dict, indent=1, ensure_ascii=False))

# Ejemplo: Resumen Empresa
resumen_empresa_dict = XMLtoDict(resumen_empresa_root)
print(json.dumps(resumen_empresa_dict, indent=1, ensure_ascii=False))

# Ejemplo: Resumen Financiero
resumen_financiero_dict = XMLtoDict(resumen_financiero_root)
print(json.dumps(resumen_financiero_dict, indent=1, ensure_ascii=False))

# Ejemplo: Estimaciones Analistas
estimaciones_analistas_dict = XMLtoDict(estimaciones_analistas_root)
print(json.dumps(estimaciones_analistas_dict, indent=1, ensure_ascii=False))

# Recordatorio:
#   - Convertir archivos XML a diccionarios facilita el acceso y manipulación de datos en Python, permitiéndonos integrar estos ficheros
#     en flujos de datos estructurados de forma rápida y eficiente, sin la complejidad del manejo de árboles XML.
