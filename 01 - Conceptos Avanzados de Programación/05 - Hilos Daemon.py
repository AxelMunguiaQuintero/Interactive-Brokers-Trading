# Importar librerías
import threading
import time

# Funcoón que ejecute un Hilo Daemon
def hilo_daemon():
    
    while True:
        print("Hilo Daemon está en ejecución...")
        time.sleep(1)
        
# Crear un Hilo Daemon
daemon = threading.Thread(target=hilo_daemon, daemon=True)

# Inicializar el Hilo
daemon.start()

# Código Principal
time.sleep(10)
print("Programa finalizado")

# Recordatorio:
#   - Los Hilos Daemon se ejecutan en segundo plano y se detienen automáticamente cuando el Hilo del programa principal termina,
#     sin importar si han completado su tarea o no.
#   - Los Hilos Daemon son útiles para tareas no críticas, como monitoreo o registro, ya que no bloquean el cierre del programa
#     y pueden ser interrumpidos sin afectar el flujo principal.
