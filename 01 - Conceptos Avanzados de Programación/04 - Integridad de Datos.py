# -*- coding: utf-8 -*-
# Importar librerías
import threading

# Contador Compartido
contador = 0

# Crear un Lock
lock = threading.Lock()

# Función que incrementará el valor del contador
def incrementar(nombre_hilo: str):
    
    """
    Función incrementa el valor del contador
    """
    
    global contador
    for i in range(1, 5_000_001, 1):
        # Adquirir el lock
        lock.acquire()
        contador += 1
        lock.release()
        
    print(f"Hilo {nombre_hilo} ha terminado")
    
    
# Crear 3 Hilos
thread1 = threading.Thread(target=incrementar, args=("Hilo 1", ))
thread2 = threading.Thread(target=incrementar, args=("Hilo 2", ))
thread3 = threading.Thread(target=incrementar, args=("Hilo 3", ))

# Inicializar los Hilos
thread1.start()
thread2.start()
thread3.start()

# Esperar a que todos los Hilos terminen
thread1.join()
thread2.join()
thread3.join()

print(f"Contador Final: {contador}")

print("Comprobar Resultado:", 5_000_000 * 3)

# Recordatorio:
#   - Los locks son mecanismos de sincronización que garantizan la exclusión mutua, permitiendo que solo un Hilo acceda
#     a una sección crítica del código a la vez. Esto asegura la integridad de los datos al modificar variables compartidas,
#     evitando resultados inconsistentes o errores en la ejecución del programa.
