# Importar librerías
import xml.etree.ElementTree as ET
import xml.dom.minidom

####################### Sección 1: Crear un archivo XML #######################

# Definir un nombre para el archivo
archivo_xml = "libros.xml"

# Crear el elemento raíz
raiz = ET.Element("libros")

def mostrar_archivo(elemento):
    
    """
    Muestra la estructura XML de un elemento dado de forma indentada y legible
    """
    
    # Convertir el elemento XML a una cadena de texto sin formato
    xml_str = ET.tostring(elemento, encoding="utf-8").decode("utf-8")
    reparsed = xml.dom.minidom.parseString(xml_str)
    print(reparsed.toprettyxml(indent="  ", newl="\n"))
    
print("Elemento raíz creado:")
mostrar_archivo(raiz)

# Crear un libro
libro1 = ET.SubElement(raiz, "libro")
libro1.set("id", "1")
ET.SubElement(libro1, "titulo").text = "Cien años de soledad"
ET.SubElement(libro1, "autor").text = "Gabriel García Márquez"
ET.SubElement(libro1, "año").text = "1967"

print("Después de agregar el primer libro:")
mostrar_archivo(raiz)

# Agregando otro libro
libro2 = ET.SubElement(raiz, "libro")
libro2.set("id", "2")
ET.SubElement(libro2, "titulo").text = "El túnel"
ET.SubElement(libro2, "autor").text = "Ernesto Sabato"
ET.SubElement(libro2, "año").text = "1948"

print("Después de agregar el segundo libro:")
mostrar_archivo(raiz)

# Crear el árbol y guardar en un archivo
arbol = ET.ElementTree(raiz)

# Iterar en cada elemento del árbol
for elemento in arbol.iter():
    print(elemento)

# Función para guardar 
def guardar_xml_indentando(arbol, archivo):
    
    xml_str = ET.tostring(arbol.getroot(), encoding="utf-8").decode("utf-8")
    reparsed = xml.dom.minidom.parseString(xml_str)
    with open(archivo, "w", encoding="utf-8") as outfile:
        outfile.write(reparsed.toprettyxml(indent="   "))
        
# Guardar el XML
guardar_xml_indentando(arbol=arbol, archivo=archivo_xml)

###############################################################################

########################### Sección 2: Modificar XML ##########################

# Cargar el archivo XML
arbol = ET.parse(archivo_xml)
raiz = arbol.getroot()
mostrar_archivo(raiz)

# Modificar un libro
for libro in raiz.findall("libro"):
    if libro.get("id") == "1":
        # Cambiar el año de publicación
        libro.find("año").text = "1969"
        print("El cambio ha sido realizado con éxito")
        
mostrar_archivo(raiz)

# Agregando otro libro
libro3 = ET.SubElement(raiz, "libro")
libro3.set("id", "3")
ET.SubElement(libro3, "titulo").text = "El nombre del viento"
ET.SubElement(libro3, "autor").text = "Patrick Rothfuss"
ET.SubElement(libro3, "año").text = "2007"

guardar_xml_indentando(arbol=arbol, archivo=archivo_xml)

###############################################################################

########################## Sección 3: Obtener Datos ##########################

# Cargar el archivo XML
arbol = ET.parse(archivo_xml)
raiz = arbol.getroot()
mostrar_archivo(raiz)

# Imprimir los datos de cada libro
for libro in raiz.findall("libro"):
    id_libro = libro.get("id")
    titulo = libro.find("titulo").text
    autor = libro.find("autor").text
    año = libro.find("año").text
    print(f"ID: {id_libro}, Título: {titulo}, Autor: {autor}, Año de Publicación: {año}")

##############################################################################

# Recordatorio:
#   - XML (Extensible Markup Language) es un formato basado en texto que organiza los datos de forma jerárquica
#     mediante etiquetas. Esto facilita tanto la legibilidad para los humanos como el procesamiento para las máquinas.
#   - XML es ampliamente utilizado para intercambiar datos entre diferentes sistemas y plataformas, ya que es
#     independiente del software y del hardware. Permite almacenar información estructurada de manera flexible.
