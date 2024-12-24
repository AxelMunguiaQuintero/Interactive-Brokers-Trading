# Importar librerías
import threading
import time

# Función que simula una tarea
def tarea(nombre, duracion):
    
    print(f"Thread {nombre} comenzando...")
    time.sleep(duracion) # Simula un trabajo que tarda "duracion" segundos
    print(f"Thread {nombre} finalizado después de {duracion} segundos.")
    
# Lista para guardar los threads
threads = []

# Crear e inicializar varios Threads
for i in range(5):
    # Cada thread ejecutará la función de tarea con un nombre y una duración diferente
    thread = threading.Thread(target=tarea, args=(f"Trabajador-{i+1}", i+1))
    threads.append(thread)
    thread.start()
    
# Esperar a que todos los Hilos/Threads terminen
for thread in threads:
    thread.join()
    
print("Todos los Threads han terminado su tarea")

# Recordatorio:
#   - Los Hilos permiten la ejecución concurrente de múltiples tareas dentro de un programa, mejorando la eficiencia
#     al aprovechar recursos del sistema. Esto es especialmente útil en aplicaciones que requieren realizar operaciones
#     de espera, como descargas de archivos o procesamiento de datos.
#   - El método Join se utiliza para sincronizar la ejecución de Hilos, permitiendo que un Hilo espere a que otro complete
#     su tarea. Esto es crucial para asegurar que los resultados se obtengan antes de continuar con el flujo del programa.
