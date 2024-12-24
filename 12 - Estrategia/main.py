# -*- coding: utf-8 -*-
# Importar librerías
from Sistema_Trading import Sistema_Trading_IB
from datetime import datetime
import pytz
import time

if __name__ == "__main__":
    # Revisar que se ejecutará en el horario correcto:
        
    # Zona horaria de Nueva York
    zona_horaria_ny = pytz.timezone('America/New_York')
    
    # Hora actual en Nueva York
    hora_actual_ny = datetime.now(zona_horaria_ny)
    
    # Establecer horario mínimo
    horario_minimo = hora_actual_ny.replace(hour=9, minute=28, second=0, microsecond=0)
    
    # Establecer horario máximo
    horario_maximo = hora_actual_ny.replace(hour=9, minute=40, second=0, microsecond=0)
    
    # Revisar Horario
    ejecutado = False
    if (hora_actual_ny >= horario_minimo) and (hora_actual_ny <= horario_maximo):
        IB_app = Sistema_Trading_IB()
        ejecutado = True
    elif (hora_actual_ny < horario_minimo):
        diferencia = horario_minimo - hora_actual_ny
        time.sleep(diferencia.seconds + 1)
        IB_app = Sistema_Trading_IB()
        ejecutado = True
    elif (hora_actual_ny > horario_maximo):
        raise RuntimeError(f"La ejecución está fuera del horario permitido."
                           f" Hora actual: {hora_actual_ny.strftime('%H:%M:%S')}."
                           f" El sistema debe ejecutarse entre {horario_minimo.strftime('%H:%M:%S')}"
                           f" y {horario_maximo.strftime('%H:%M:%S')}.")
    
    # Esperar a cerrar posiciones
    if ejecutado:
        hora_final = hora_actual_ny.replace(hour=10, minute=0, microsecond=0)
        diferencia = hora_final - datetime.now(zona_horaria_ny)
        time.sleep(diferencia.seconds + 1)
        # Cerrar todo cuando despierte
        IB_app.end_session(account = "DUE273425", close_orders = True, close_positions = True)
