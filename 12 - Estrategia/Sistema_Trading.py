# -*- coding: utf-8 -*-
# Importar librerías
from IB_Trading import IB_Trading, Contract
from Analisis_Tecnico import Cruce_MA
from Escaner_Financiero import Open_Gap_Assets
from datetime import datetime
import numpy as np
import time

# Desarrollar Sistema de Trading
def Sistema_Trading_IB(): 
    
    """
    Este método implementa un sistema de trading automatizado con Interactive Brokers (IB). Conecta la plataforma, 
    identifica activos con oportunidades mediante un escáner financiero, aplica filtros técnicos basados en cruces 
    de medias móviles, selecciona contratos de opciones del siguiente mes y ejecuta órdenes de compra o venta 
    automáticamente según los resultados del análisis.
    
    Salida:
    -------
    return: IB_Trading : Instancia de la clase IB_Trading que permite continuar con la conexión y operaciones.
    """
    
    # Sección 1: Conectarse al Servidor
    
    # Generar Instancia
    IB_app = IB_Trading(log_file = "ibapi_errors.log", mode = "w", errors_verbose = False)
    IB_app.clear_logs()
    IB_app.connect(host="127.0.0.1", port=7497, clientId=1)
    
     # Sección 2: Escáner Financiero 
    
    # Detectar Activos
    escaner_busqueda = Open_Gap_Assets(trading_app=IB_app, suscripciones=[], menor_spread_porcentaje=True)
    # Ordenar Activos
    ganancia_df = escaner_busqueda["Ganancia"].sort_values(by=["Spread Porcentaje"], ascending=True)
    perdida_df = escaner_busqueda["Perdida"].sort_values(by=["Spread Porcentaje"], ascending=True)
    # Mantener Activos con un Spread < 1.5% (Max 10 Activos)
    ganancia_df = ganancia_df[ganancia_df["Spread Porcentaje"] <= 0.015].iloc[:10]
    perdida_df = perdida_df[perdida_df["Spread Porcentaje"] <= 0.015].iloc[:10]
    
    # Sección 3: Filtrar en Base a los Promedios Móviles
    
    # Filtrar: Validar Cruce de Medias Móviles Calls
    cruces_gain = []
    for indice, instrumento in ganancia_df.iterrows():
        # Obtener Datos
        df = IB_app.reqHistoricalData(reqId=0, contract=instrumento["contrato Detalles"].contract, durationStr="3 W", 
                                      barSizeSetting="30 mins")
        cma = Cruce_MA(df, tendencia_rápida=9, tendencia_lenta=21)
        # Tendencia Alcista
        if cma["Tendencia"].iloc[-1] == 1.0:
            cruces_gain.append(True)
        else:
            cruces_gain.append(False)
    # Filtrar: Validar Cruce de Medias Móviles Puts
    cruces_lose = []
    for indice, instrumento in perdida_df.iterrows():
        # Obtener Datos
        df = IB_app.reqHistoricalData(reqId=0, contract=instrumento["contrato Detalles"].contract, durationStr="3 W", 
                                      barSizeSetting="30 mins")
        cma = Cruce_MA(df, tendencia_rápida=9, tendencia_lenta=21)
        # Tendencia Alcista
        if cma["Tendencia"].iloc[-1] == -1.0:
            cruces_lose.append(True)
        else:
            cruces_lose.append(False)
    # Reasignar
    ganancia_df = ganancia_df.loc[cruces_gain]
    perdida_df = perdida_df.loc[cruces_lose]
            
    # Sección 4: Seleccionar Opciones
    
    # Seleccionar Contrato de Compra del Siguiente Mes (Calls). Seleccionar el 3 por encima del Contrato ATM 
    contratos_seleccionados_gain = []
    for indice, instrumento_gain in ganancia_df.iterrows():
        # Crear Contrato
        contrato = Contract()
        contrato.symbol = instrumento_gain["Instrumento"]
        contrato.secType = "OPT"
        contrato.exchange = instrumento_gain["Exchange"]
        contrato.currency = instrumento_gain["Divisa"]
        contrato.multiplier = "100"
        # Obtener Siguiente Mes
        fecha_hoy = datetime.now()
        if fecha_hoy.month == 12: 
            fecha_vencimiento = fecha_hoy.replace(year=fecha_hoy.year + 1, month=1, day=1).strftime("%Y%m")
        else:
            fecha_vencimiento = fecha_hoy.replace(month=fecha_hoy.month + 1, day=1).strftime("%Y%m")
        contrato.lastTradeDateOrContractMonth = fecha_vencimiento
        contrato.right = "C"
        contratos = IB_app.reqContractDetails(reqId=0, contract=contrato, timeout=5)
        if contratos is not None:
            # Extraer Precios de Ejercicio
            contratos_strikes = sorted([detalles_contrato.contract.strike for detalles_contrato in contratos])
            # Tomar el 3er Contrato OTM más cercano al precio de mercado
            contratos_strikes = np.array(contratos_strikes)
            strike_seleccionado = contratos_strikes[contratos_strikes > instrumento_gain["Precio Mercado"]][:4][0]
            # Especificar Strike
            contrato.strike = strike_seleccionado
        else: 
            contrato = None
        # Guardar
        contratos_seleccionados_gain.append(contrato)
        # Evitar Bloqueos del Servidor
        time.sleep(1)
    # Seleccionar Contrato de Compra del Siguiente Mes (Puts). Seleccionar el 3 por debajo del Contrato ATM 
    contratos_seleccionados_lose = []
    for indice, instrumento_lose in perdida_df.iterrows():
        # Crear Contrato
        contrato = Contract()
        contrato.symbol = instrumento_lose["Instrumento"]
        contrato.secType = "OPT"
        contrato.exchange = instrumento_lose["Exchange"]
        contrato.currency = instrumento_lose["Divisa"]
        contrato.multiplier = "100"
        # Obtener Siguiente Mes
        fecha_hoy = datetime.now()
        if fecha_hoy.month == 12: 
            fecha_vencimiento = fecha_hoy.replace(year=fecha_hoy.year + 1, month=1, day=1).strftime("%Y%m")
        else:
            fecha_vencimiento = fecha_hoy.replace(month=fecha_hoy.month + 1, day=1).strftime("%Y%m")
        contrato.lastTradeDateOrContractMonth = fecha_vencimiento
        contrato.right = "P"
        contratos = IB_app.reqContractDetails(reqId=0, contract=contrato, timeout=5)
        if contratos is not None:
            # Extraer Precios de Ejercicio
            contratos_strikes = sorted([detalles_contrato.contract.strike for detalles_contrato in contratos])
            # Tomar el 3er Contrato OTM más cercano al precio de mercado
            contratos_strikes = np.array(contratos_strikes)
            strike_seleccionado = contratos_strikes[contratos_strikes < instrumento_lose["Precio Mercado"]][-4:][0]
            # Especificar Strike
            contrato.strike = strike_seleccionado
        else: 
            contrato = None
        # Guardar
        contratos_seleccionados_lose.append(contrato)
        # Evitar Bloqueos del Servidor
        time.sleep(1)
    # Agregar a DataFrames
    ganancia_df["Contrato Opt"] = contratos_seleccionados_gain
    perdida_df["Contrato Opt"] = contratos_seleccionados_lose
    # Mantener Activos Válidos
    ganancia_df = ganancia_df[ganancia_df["Contrato Opt"].notnull()]
    perdida_df = perdida_df[perdida_df["Contrato Opt"].notnull()]
    
    # Sección 5: Ejecutar Órdenes
    
    # Abrir Operaciones (Iterar en Gain)
    for indice, posicion_individual in ganancia_df.iterrows():
        # Generar Orden
        orden_mercado = IB_app.market_order(action="BUY", totalQuantity=1)
        # Siguiente Id válido
        next_id = IB_app.reqIds(numIds=-1)
        IB_app.placeOrder(orderId=next_id, contract=posicion_individual["Contrato Opt"], order=orden_mercado)
    
    # Abrir Operaciones (Iterar en Lose)
    for indice, posicion_individual in perdida_df.iterrows():
        # Generar Orden
        orden_mercado = IB_app.market_order(action="SELL", totalQuantity=1)
        # Siguiente Id válido
        next_id = IB_app.reqIds(numIds=-1)
        IB_app.placeOrder(orderId=next_id, contract=posicion_individual["Contrato Opt"], order=orden_mercado)
        
    
    return IB_app


# Recordatorio:
if __name__ == "__main__":
    Sistema_Trading_IB()    
