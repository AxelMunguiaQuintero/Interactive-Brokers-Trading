# -*- coding: utf-8 -*-
# Importar librerías
from IB_Trading import IB_Trading, ScannerSubscription
import pandas as pd

# Definir Función del Escáner
def Open_Gap_Assets(trading_app, suscripciones: list = [], menor_spread_porcentaje: bool = False) -> pd.DataFrame:
    
    """
    Función que identifica activos con mayor ganancia o pérdida basándose en un escáner y, opcionalmente, calcula el spread porcentual.

    Parámetros:
    -----------
    trading_app : IB_Trading
        Instancia del objeto `IB_Trading` utilizado para realizar las peticiones al escáner y recuperar datos históricos.
    
    suscripciones : list, opcional
        Lista que contiene dos objetos `ScannerSubscription`. El primero debe corresponder a los activos con mayor ganancia 
        y el segundo a los activos con mayor pérdida. Si no se proporciona, se utilizarán suscripciones predeterminadas.
        Por defecto, es una lista vacía.
    
    menor_spread_porcentaje : bool, opcional
        Si es True, se calculará el spread porcentual para los activos seleccionados y se incluirá en el resultado. 
        Por defecto, es False.

    Salida:
    -------
    return : dict :
        Diccionario que contiene dos DataFrames con los resultados del escáner:
        - "Ganancia": Activos con mayor ganancia, opcionalmente ordenados por spread porcentual.
        - "Perdida": Activos con mayor pérdida, opcionalmente ordenados por spread porcentual.
    """
    
    # Validar que no se han pasado las Suscripciones
    if len(suscripciones) == 0:
        # Generar Suscripción del Escáner (Activos con Mayor Incremento)
        suscripcion_top_gain = ScannerSubscription()
        suscripcion_top_gain.instrument = "STK"
        suscripcion_top_gain.locationCode = "STK.US"
        suscripcion_top_gain.scanCode = "TOP_PERC_GAIN"
        suscripcion_top_gain.marketCapAbove = 500 # Expresado en Millones
        suscripcion_top_gain.abovePrice = 10
        suscripcion_top_gain.numberOfRows = 20
        
        # Generar Suscripción del Escáner (Activos con Mayor Decremento)
        suscripcion_top_lose = ScannerSubscription()
        suscripcion_top_lose.instrument = "STK"
        suscripcion_top_lose.locationCode = "STK.US"
        suscripcion_top_lose.scanCode = "TOP_PERC_LOSE"
        suscripcion_top_lose.marketCapAbove = 500 # Expresado en Millones
        suscripcion_top_lose.abovePrice = 10
        suscripcion_top_lose.numberOfRows = 20
    else:
        # Validar que existen ambas Suscripciones
        if len(suscripciones) != 2:
            raise ValueError("Se deben proporcionar exactamente dos suscripciones: una para las ganancias y otra para las pérdidas.")
        # Extraer si se Indicador
        suscripcion_top_gain = suscripciones[0]
        suscripcion_top_lose = suscripciones[1]
    
    # Obtener Índices Actuales (Para no eliminar información)
    ids_peticiones = sorted(list(trading_app.escaner_resultados.keys()))
    if len(ids_peticiones) == 0:
        id_peticion1 = 0
        id_peticion2 = 1
    else:
        ultimo_id = ids_peticiones[-1]
        id_peticion1 = int(ultimo_id + 1)
        id_peticion2 = int(ultimo_id + 2)
        
    # Realizar Peticiones
    peticion_gain = trading_app.reqScannerSubscription(reqId=id_peticion1, subscription=suscripcion_top_gain, 
                                                       scannerSubscriptionOptions=[], scannerSubscriptionFilterOptions=[])
    peticion_lose = trading_app.reqScannerSubscription(reqId=id_peticion2, subscription=suscripcion_top_lose, 
                                                       scannerSubscriptionOptions=[], scannerSubscriptionFilterOptions=[])
    
    # Ordenar en Base a Spread
    if menor_spread_porcentaje:
        # Iterar en cada activo (Gain)
        spreads_gain = []
        for indice, registro_gain in peticion_gain.iterrows():
            # Extrar Contrato
            contrato = registro_gain["contrato Detalles"].contract
            # Realizar Petición Datos Ask
            precios_ask = trading_app.reqHistoricalData(reqId=0, contract=contrato, durationStr="1 D", barSizeSetting="1 day",
                                                        whatToShow="ASK", keep_stored=False)
            # Obtener Precio de Mercado
            precios_mercado = trading_app.reqHistoricalData(reqId=0, contract=contrato, durationStr="1 D", barSizeSetting="1 day",
                                                          whatToShow="ADJUSTED_LAST", keep_stored=False)
            # Consultar Precios Bid
            precios_bid = trading_app.reqHistoricalData(reqId=0, contract=contrato, durationStr="1 D", barSizeSetting="1 day",
                                                        whatToShow="BID", keep_stored=False)
            # Calcular el Spread en Términos de Porcentaje
            spread_porcentaje_ask = (precios_ask["Close"] - precios_mercado["Close"]) / precios_mercado["Close"]
            spread_porcentaje_bid = (precios_mercado["Close"] - precios_bid["Close"]) / precios_mercado["Close"]
            # Sumar Spreads
            spread = (precios_ask["Close"] - precios_bid["Close"])
            porcentaje_spread = spread / precios_mercado["Close"]
            # Almacenar
            spreads_gain.append([precios_mercado["Close"].iloc[0], precios_ask["Close"].iloc[0], precios_bid["Close"].iloc[0],
                                 spread_porcentaje_ask.iloc[0], spread_porcentaje_bid.iloc[0], porcentaje_spread.iloc[0]])
      
        # Iterar en cada activo (Lose)
        spreads_lose = []
        for indice, registro_lose in peticion_lose.iterrows():
            # Extrar Contrato
            contrato = registro_lose["contrato Detalles"].contract
            # Realizar Petición Datos Bid
            precios_bid = trading_app.reqHistoricalData(reqId=0, contract=contrato, durationStr="1 D", barSizeSetting="1 day",
                                                        whatToShow="BID", keep_stored=False)
            # Obtener Precio de Mercado
            precios_mercado = trading_app.reqHistoricalData(reqId=0, contract=contrato, durationStr="1 D", barSizeSetting="1 day",
                                                          whatToShow="ADJUSTED_LAST", keep_stored=False)
            # Consultar Precios Ask
            precios_ask = trading_app.reqHistoricalData(reqId=0, contract=contrato, durationStr="1 D", barSizeSetting="1 day",
                                                        whatToShow="ASK", keep_stored=False)
            # Calcular el Spread en Términos de Porcentaje
            spread_porcentaje_bid = (precios_mercado["Close"] - precios_bid["Close"]) / precios_mercado["Close"]
            spread_porcentaje_ask = (precios_ask["Close"] - precios_mercado["Close"]) / precios_mercado["Close"]
            # Sumar Spreads
            spread = (precios_ask["Close"] - precios_bid["Close"])
            porcentaje_spread = spread / precios_mercado["Close"]
            # Almancenar
            spreads_lose.append([precios_mercado["Close"].iloc[0], precios_ask["Close"].iloc[0], precios_bid["Close"].iloc[0],
                                 spread_porcentaje_ask.iloc[0], spread_porcentaje_bid.iloc[0], porcentaje_spread.iloc[0]])
            
        # Agregar a DataFrame
        peticion_gain[["Precio Mercado", "Precio Ask", "Precio Bid", "Spread Comprar Porcentaje",
                       "Spread Vender Porcentaje", "Spread Porcentaje"]] = spreads_gain
        peticion_lose[["Precio Mercado", "Precio Ask", "Precio Bid", "Spread Comprar Porcentaje",
                       "Spread Vender Porcentaje", "Spread Porcentaje"]] = spreads_lose
    
    return {"Ganancia": peticion_gain, "Perdida": peticion_lose}
    

# Recordatorio:
if __name__ == "__main__":
    # Crear Instancia
    IB_escaner = IB_Trading(errors_verbose=True)
    # Conectarse
    IB_escaner.connect()
    # Realizar Peticiones (Sin Cálculos Adicionales)
    peticiones_escaner = Open_Gap_Assets(trading_app=IB_escaner, suscripciones=[], 
                                         menor_spread_porcentaje=False)
    # Mostrar Activos con el Mayor Gap (Ganancia)
    print("Activos con Mayor Ganancia:\n\n", peticiones_escaner["Ganancia"].iloc[:, :-1])
    
    # Mostrar Activos con el Mayor Gap (Pérdida)
    print("Activos con Mayor Pérdida:\n\n", peticiones_escaner["Perdida"].iloc[:, :-1])
    # Realizar Peticiones (Con Cálculos Adicionales)
    peticiones_escaner = Open_Gap_Assets(trading_app=IB_escaner, suscripciones=[], 
                                         menor_spread_porcentaje=True)
    # Mostrar Activos con el Mayor Gap (Ganancia)
    gap_gain = peticiones_escaner["Ganancia"][["Instrumento", "Precio Mercado", "Precio Ask", "Precio Bid", "Spread Comprar Porcentaje",
                   "Spread Vender Porcentaje", "Spread Porcentaje"]].sort_values(by=["Spread Porcentaje"], ascending=True)
    print("Activos con Mayor Ganancia:\n\n", gap_gain)
    
    # Mostrar Activos con el Mayor Gap (Pérdida)
    gap_lose = peticiones_escaner["Perdida"][["Instrumento", "Precio Mercado", "Precio Ask", "Precio Bid", "Spread Comprar Porcentaje",
                   "Spread Vender Porcentaje", "Spread Porcentaje"]].sort_values(by=["Spread Porcentaje"], ascending=True)
    print("Activos con Mayor Pérdida:\n\n", gap_lose)
