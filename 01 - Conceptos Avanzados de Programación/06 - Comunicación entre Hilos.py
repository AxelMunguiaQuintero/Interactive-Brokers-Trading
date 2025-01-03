# -*- coding: utf-8 -*-
# Importar librerías
import threading
import time

# Crear un Evento que simula el Semáforo
evento = threading.Event()
print("Estado Actual del Evento:", evento.is_set())

# Función Coche
def coche(nombre: str):
    
    """
    Simula el comportamiento de un coche que espera a que el semáaforo cambie a verde para avanzar
    """
    
    print(f"{nombre} está esperando en el semáforo...")
    evento.wait()
    print(f"{nombre} ha cruzadao el semáforo.")
    
    
# Función Semáforo
def control_semaforo():
    
    """
    Controla el semáforo, cambiando su estado entre rojo y verde
    """
    
    print("El semáforo está en rojo...")
    time.sleep(5)
    evento.set()
    
    print("El semáforo está en verde. ¡Los autos pueden avanzar!")
    print("Estado actual del Evento:", evento.is_set())
    
    time.sleep(5)
    evento.clear()
    
    print("Estado actual del Evento:", evento.is_set())
    print("El semáforo está en rojo...")
    
    
# Crear Hilos para simular autos
autos = ["Coche 1", "Coche 2", "Coche 3"]  
hilos = []

for auto in autos:
    hilo = threading.Thread(target=coche, args=(auto, ))
    hilos.append(hilo)
    hilo.start()
    
# Controlar el Semáforo
control_hilo = threading.Thread(target=control_semaforo)
control_hilo.start()

# Esperaar a que los autos terminen de cruzar
for hilo in hilos:
    hilo.join()
    
control_hilo.join()
    
# Recordatorio:
#   - Los Eventos permiten coordinar varios Hilos, bloqueando su ejecución hasta que se active el evento, asegurando que no
#     continuén hasta que ocurra una condición específica.
#   - Con métodos como set() y clear(), puedes activar o desactivar eventos facilmente, proporcionando un mecanismo flexible para
#     gestionar flujos de trabajo concurrentes.
