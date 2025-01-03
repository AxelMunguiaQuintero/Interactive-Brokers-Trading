# -*- coding: utf-8 -*-
# Clase Libro
class Libro:
    
    """
    Clase que representa un libro de forma genérica
    """
    
    def __init__(self, titulo, autor):
        
        """
        Constructor
        """
        
        # Atributos
        self.titulo = titulo
        self.autor = autor
        self.disponible = True
        
        
    def prestar(self):
        
        """
        Marca el libro como prestado si está disponible.
        """
        
        if self.disponible:
            self.disponible = False
            print(f"{self.titulo} ha sido prestado")
        else:
            print(f"{self.titulo} no está disponible para préstamo")
            
            
    def devolver(self):
        
        """
        Marca el libro como disponible para préstamo.
        """
        
        self.disponible = True
        print(f"{self.titulo} ha sido devuelto")
        
    
# Clase que representa un usuario
class Usuario:
    
    """
    Representa un individuo que puede solicitar o devolver libros.
    """
    
    def __init__(self, nombre):
        
        """
        Constructor
        """
        
        # Atributos
        self.nombre = nombre
        
        
    def solicitar_prestamo(self, libro):
        
        """
        Método que solicita un libro del sistema
        """
        
        print(f"{self.nombre} solicita prestar el libro: {libro.titulo}")
        libro.prestar()
        
        
    def devolver_libro(self, libro):
        
        """
        Devuelve un libro anteriormente solicitado
        """
        
        print(f"{self.nombre} devuelve el libro: {libro.titulo}")
        libro.devolver()
        

# Clase que combina las funcionalidades de Libro y Usuario
class SistemaDeBiblioteca(Libro, Usuario):
    
    """
    Clase que representa el Sistema de una Biblioteca.
    """
    
    def __init__(self, titulo, autor, nombre_usuario):
        
        """
        Inicializa las clases heredadas
        """
        
        # Inicializar cada clase
        Libro.__init__(self, titulo=titulo, autor=autor)
        Usuario.__init__(self, nombre=nombre_usuario)
        
        
    def gestionar_prestamo(self):
        
        """
        Solicita el préstamo de un libro
        """
        
        self.solicitar_prestamo(self)
        
    
    def gestionar_devolucion(self):
        
        """
        Devuelve un libro previamente prestado
        """
        
        self.devolver_libro(self)
        
        
# Generar una Instancia del Sistema
sistema = SistemaDeBiblioteca(titulo="Cien años de soledad", autor="Gabriel García Márquez", nombre_usuario="Axel Munguía")

# Gestionar un préstamo
sistema.gestionar_prestamo()
# Imprimir atributos
print("Autor:", sistema.autor)
print("Título:", sistema.titulo)
print("Nombre:", sistema.nombre)
print("Disponibilidad:", sistema.disponible)
# Gestionar una devolución
sistema.gestionar_devolucion()
print("Disponibilidad:", sistema.disponible)

# Recordatorio:
#   - La Herencia permite a las clases Hijas heredar atributos y métodos de las clases padres, facilitando la reutilización de código
#     y evitando la duplicación, lo que mejora la eficiencia y el mantenimiento de software.
