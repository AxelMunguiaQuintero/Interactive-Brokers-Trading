# -*- coding: utf-8 -*-
# Importar librerías
import numpy as np
import pandas as pd

# Definir Función de Cruce de Promedios Móviles
def Cruce_MA(df: pd.DataFrame, tendencia_rápida: int, tendencia_lenta: int, tendencia_continua: bool = True) -> pd.DataFrame:
    
    """
    Función que calcula el cruce de medias móviles en un DataFrame de series temporales.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame que contiene los datos de series temporales. 
        Debe incluir una columna llamada 'Close' que representa los precios de cierre.
    
    tendencia_rápida : int
        Número de periodos para la media móvil rápida.
    
    tendencia_lenta : int
        Número de periodos para la media móvil lenta.
    
    tendencia_continua : bool, opcional
        Si es True, se mostrará la señal de cruce en todas las filas posteriores al cruce inicial.
        Por defecto, es True.

    Salida:
    -------
    return: pd.DataFrame : Cálculos de las medias móviles y los cruces entre ellas.
    """
    
    # Calcular Tendencia de Corto Plazo (Tendencia Rápida)
    tendencia_corto_plazo = df["Close"].rolling(window = tendencia_rápida).mean()
    # Calcular Tendencia de Largo Plazo (Tendencia Lenta)
    tendencia_largo_plazo = df["Close"].rolling(window = tendencia_lenta).mean()
    # Medias Móviles Desplazadas
    tendencia_corto_plazo_desplazada = tendencia_corto_plazo.shift(periods=1)
    tendencia_largo_plazo_desplazada = tendencia_largo_plazo.shift(periods=1)
    # Detectar Cruces
    cruce_tendencia_alcista = (tendencia_corto_plazo > tendencia_largo_plazo) & \
        (tendencia_corto_plazo_desplazada < tendencia_largo_plazo_desplazada)
    cruce_tendencia_bajista = (tendencia_largo_plazo > tendencia_corto_plazo) & \
        (tendencia_largo_plazo_desplazada < tendencia_corto_plazo_desplazada)
    cruces = np.where(cruce_tendencia_alcista, 1,
                      np.where(cruce_tendencia_bajista, -1, np.nan))
    cruces = pd.DataFrame(cruces, index=df.index)
    # Unir todo en DataFrame
    df_final = pd.concat([tendencia_corto_plazo, tendencia_largo_plazo, cruces], axis = 1)
    df_final.columns = ["MA_Rapida", "MA_Lenta", "Cruces"]
    # Agregar Tendencia Continua (Opcional)
    if tendencia_continua:        
            df_final["Tendencia"] = df_final["Cruces"].ffill() 
            
    return df_final
        
# Recordatorio:
if __name__ == "__main__":
    # Import librerías adicionales
    from IB_Trading import IB_Trading, Contract
    import mplfinance as mpf
    import matplotlib.pyplot as plt
    # Generar Instancia y Conectarse
    IB_datos = IB_Trading()
    IB_datos.connect(host="127.0.0.1", port=7497, clientId=1)
    # Crear Contrato
    contrato = Contract()
    contrato.symbol = "AMZN"
    contrato.secType = "STK"
    contrato.exchange = "SMART"
    contrato.currency = "USD"
    # Descargar Datos
    df = IB_datos.reqHistoricalData(reqId=0, contract=contrato, durationStr="2 Y")
    print(df)
    calculo_ma = Cruce_MA(df=df, tendencia_rápida=9, tendencia_lenta=21, tendencia_continua=True)
    # Realizar Plot de Datos
    ma_lines = [
        
        mpf.make_addplot(calculo_ma["MA_Rapida"], label="Media Móvil 9 Días", color="blue", type="line", 
                         alpha=0.75, panel=0),
        mpf.make_addplot(calculo_ma["MA_Lenta"], label="Media Móvil 21 Días", color="orange", type="line", 
                         alpha=0.75, panel=0),
        mpf.make_addplot(calculo_ma["MA_Rapida"].where(calculo_ma["Cruces"] == 1), color="green",
                         type="scatter", marker="x", markersize=150, alpha=1, panel=0),
        mpf.make_addplot(calculo_ma["MA_Lenta"].where(calculo_ma["Cruces"] == -1), color="red",
                         type="scatter", marker="x", markersize=150, alpha=1, panel=0),
        mpf.make_addplot(calculo_ma["Tendencia"], color="black", type="line", marker="o", panel=2,
                         label="Tendencia Continua"),
        mpf.make_addplot(calculo_ma["Tendencia"].where(calculo_ma["Tendencia"] == 1), color="green", type="scatter",
                         marker="o", panel=2, label="Tendencia Alcista"),
        mpf.make_addplot(calculo_ma["Tendencia"].where(calculo_ma["Tendencia"] == -1), color="red", type="scatter",
                         marker="o", panel=2, label="Tendencia Bajista")
        
        ]
    
    # Generar Plot Principal
    fig, axes = mpf.plot(df[["Open", "High", "Low", "Close", "Volume"]], style="yahoo", figsize=(22, 10),
                         title=dict(title="Promedios Móviles", size=20), volume=True, addplot=ma_lines, returnfig=True)
    # Agregar Etiqueta al Panel 2
    ax_panel2 = axes[4]
    ax_panel2.set_ylabel("Tendencia Continua", fontsize=12, labelpad=10, color="black")
    plt.show()
