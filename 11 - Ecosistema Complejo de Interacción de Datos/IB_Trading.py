# -*- coding: utf-8 -*-
# Importar librerías de IB
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.scanner import ScannerSubscription
# Importar librerías Ordinarias
import threading
import logging
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import time

# Clase que Obtiene, Procesa y Almacena Datos de Diferentes Peticiones al Servidor
class IB_Trading(EWrapper, EClient):
    
    """
    Clase Avanzada de Interactive Brokers:
        
        Diseñada para manejar eficientemente peticiones a la API de IB. Esta clase permite recibir, procesar y almacenar datos
        en tiempo real. Ofrece funcionalidades avanzadas para interactuar con mercados financieros, gestionar órdenes, obtener
        cotizaciones, analizar datos históricos, y más.
    """
    
    def __init__(self, log_file: str = "ibapi_errors.log", mode: str = "w", **kwargs) -> None:
        
        """
        Constructor de la clase.
        
        Parámetros:
        -----------
        log_file : str, opcional
            Nombre o ruta del archivo de registro. Por defecto, es 'ibapi_errors.log'.
            
        mode : str, opcional
            Modo en que se abrirá el archivo de errores:
                - "w": Sobrescribir el archivo si ya existe (por defecto).
                - "a": Agregar los nuevos errores al archivo existente.
                
        **kwargs : dict, opcional
            Argumentos adicionales para configurar el comportamiento de la clase:
                - errors_verbose (bool): Define si los errores se mostrarán de forma detallada en la consola además de
                                         registrarse en el archivo. Por defecto, es `False`.
                - verbose (bool): Indica si se debe habilitar un nivel más detallado de mensajes en la consola,
                                  no necesariamente relacionado con errores. Por defecto, es `False`.
                                  
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Inicializar Cliente
        EClient.__init__(self, self)
        # Atributos Generales
        self.log_file = log_file
        self.mode = mode
        self.errors_verbose = kwargs.get("errors_verbose", False)
        self.verbose = kwargs.get("verbose", False)
        self.evento_uso_comun = threading.Event()
        # Crear logger
        self.logger = self.create_logger()
        # Atributos para almacenar información de las peticiones
        self.order_id = None
        self.contador_desconexion = 0
        self.contratos = {}
        self.datos_precios = {}
        self.ordenes_abiertas = []
        self.ordenes_completadas = []
        self.account_summary = []
        self.posiciones = []
        self.pnl_account = []
        self.escaner_resultados = {}
        
        
    def create_logger(self) -> logging.Logger:
        
        """
        Método para configurar y crear un logger personalizado.
        
        Este método inicializa un logger con un nivel de registro mí­nimo, define un manejador para escribir los mensajes
        en un archivo, y configura el formato de los mensajes registrados.
        
        Salida:
        -------
        return: logging.Logger : Instancia del logger configurado, lista para registrar eventos.
        """
        
        # Configuración de logging
        ib_logger = logging.getLogger("IB_logger")
        ib_logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.log_file, mode=self.mode)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        ib_logger.addHandler(handler)
        
        return ib_logger
    
    
    def clear_logs(self) -> None:
        
        """
        Método para vaciar el archivo de logs. Eliminará el contenido previo.
        
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Eliminar contenido del archivo log
        open(self.log_file, "w").close()
        
        
    def error(self, reqId: int, errorCode: int, errorString: str) -> None:
        
        """
        Método para gestionar y registrar errores del servidor de IB.
        
        Este método formatea los mensajes de error recibidos, los guarda en un archivo de log y, opcionalmente,
        los muestra en la consola dependiendo de la configuración.
        
        Parámetros:
        -----------
        reqId : int
            Identificador de la solicitud en la que ocurrió el error.
            Esto ayuda a relacionar el error con la operación específica que lo generó.
            
        errorCode : int
            Código numérico del error proporcionado por el servidor de IB.
            Permite identificar la causa del error según la documentación de IB.
            
        errorString : str
            Descripción en texto del error. Brinda más detalles sobre el problema
            
        Salida:
        -------
        return: NoneType : None
        """
        
        # Definir mensaje
        error_mensaje = f"Error en Solicitud: {reqId}, Código: {errorCode} - {errorString}"
        # Almacenar Errores
        self.logger.error(error_mensaje)
        # Mostrar por consola (Opcional)
        if self.errors_verbose:
            print(error_mensaje)
            
            
    def nextValidId(self, orderId: int) -> None:
        
        """
        Este método se utiliza para recibir y almacenar el siguiente identificador válido de órdenes, necesario para 
        enviar solicitudes al servidor de IB. También se utiliza como indicador para gestionar la conexión y sincronización 
        de eventos.
        
        Parámetros:
        -----------
        orderId : int
            El próximo identificador válido proporcionado por IB para ejecutar órdenes
            
        Salida:
        -------
        return: NoneType : None            
        """
        
        # Almacenar
        self.order_id = orderId
        # Imprimir en consola
        if self.verbose:
            print("Siguiente Id válido:", orderId)
        # Establecer Evento
        self.evento_uso_comun.set()
        
        
    def reqIds(self, numIds: int = -1, timeout: float = 3.0) -> int:
        
        """
        Método que envía una solicitud al servidor de IB para obtener un indentificador único de orden, necesario
        para ejecutar órdenes.
        
        Parámetros:
        -----------
        numIds : int, opcional
            Número de identificador de órden solicitados. Por defecto, es -1.
            
        timeout : float, opcional
            Tiempo máximo (en segundos) que el Evento esperará a que se reciba el ID válido antes de continuar.
            El valor predeterminado es de 3.0 segundos.
            
        Salida:
        -------
        return: int : Próximo identificador de orden
        """
        
        # Reiniciar Bandera del Evento
        self.evento_uso_comun.clear()
        # Llamar al método de las Clases Padres
        super().reqIds(numIds=numIds)
        # Esperar a que termine la petición
        self.evento_uso_comun.wait(timeout=timeout)
        self.evento_uso_comun.clear()
        
        return self.order_id
    
    
    def connect(self, host: str = "127.0.0.1", port: int = 7497, clientId: int = 1, timeout: float = 5.0) -> None:
        
        """
        Método para conectarse al servidor de IB y mantener un comunicación activa.
        
        Parámetros:
        -----------
        host : str, opcional
            Dirección IP o nombre del host del servidor de IB. Por defecto, es '127.0.0.1' (localhost).
            
        port : int, opcional
            Puerto para la conexión al servidor. Por defecto, es 7497, utilizado para conexiones de TWS.
            
        clientId : int, opcional
            Identificador único del cliente para evitar conflictos si se ejecutan múltiples instancias. Por defecto, es 1.
            
        timeout : float, opcional
            Tiempo máximo (en segundos) que el Evento esperará a que se reciba la confirmación de la conexión.
            El valor predeterminado es de 5.0 segundos.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Agregar logs
        self.logger.info("-" * 40 + "\n")
        self.logger.info("Estableciendo Conexión")
        # Mandar a llamar el método de las clases Padres
        super().connect(host=host, port=port, clientId=clientId)
        if self.isConnected():
            self.logger.info(f"Conexión establecida en host: {host} - port: {port} con clientId: {clientId}")
        # Gestionar Conexión
        self.api_thread = threading.Thread(target=self.run)
        self.api_thread.start()
        # Esperar conexión
        respuesta_conexion = self.evento_uso_comun.wait(timeout=timeout)
        # Revisar Respuesta
        if not respuesta_conexion:
            self.logger.warning(msg="Error en la Conexión")
        self.evento_uso_comun.clear()
        
        
    def disconnect(self, clear_logger: bool = False) -> None:
        
        """
        Método para desconectarse del servidor.
        
        Este método finaliza la conexión con el servidor y realiza tareas adicionales como registrar la información
        de desconexión y, opcionalmente, limpiar los logs almacenados.
        
        Parámetros:
        -----------
        clear_logger : bool, opcional
            Indica si los logs almacenados deben limpiarse después de la desconexión.
                - `False` (por defecto): No limpia los logs.
                - `True`: Llama al método `clear_logs` para limpiar los registros.
                
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Desconectar
        super().disconnect()
        if self.contador_desconexion == 0: 
            # Agregar Info a logger
            self.logger.info("Desconexión de la API de IB\n")
            self.logger.info("-" * 40 + "\n")
        # Limpiar logger
        if clear_logger:
            self.clear_logs()
        self.contador_desconexion += 1
        
   
    def contractDetails(self, reqId: int, contractDetails) -> None:
        
        """
        Método que recibe y almacena la información detallada de un contrato solicitado al servidor.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud realizada al servidor.
            
        contractDetails : ContractDetails
            Objeto que contiene la información detallada del contrato devuelta por el servidor de IB.
            Inclue atributos como tipo de activo, símbolo, mercado, divisa, entre otros.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Almacenar contratos en base al tipo de activo
        tipo_activo = contractDetails.contract.secType
        if tipo_activo not in self.contratos:
            self.contratos[tipo_activo] = {}
        if reqId not in self.contratos[tipo_activo]:
            self.contratos[tipo_activo][reqId] = []
        # Apendizar
        self.contratos[tipo_activo][reqId].append(contractDetails)
        
        
    def contractDetailsEnd(self, reqId: int) -> None:
    
        """
        Método que se llama una vez que se han recibido todos los detalles de los contratos solicitados.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud realizada al servidor.

        Salida:
        -------
        return: NoneType : None.
        """
        
        # Establecer Bandera
        self.evento_uso_comun.set()
        
        
    def reqContractDetails(self, reqId: int, contract: Contract, keep_stored: bool = False, timeout: float = 10.0) -> list:
        
        """
        Método para obtener los detalles de un contrato o activo solicitado.
        
        Este método envía una solicitud a IB para obtener detalles específicos de un contrato y espera una respuesta con los 
        datos correspondientes.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único para la solicitud de detalles de contrato.
            
        contract : Contract
            Objeto de tipo `Contract` que describe el contrato o activo cuyos detalles se solicitan.
            
        keep_stored : bool, opcional
            Si es `True`, los detalles del contrato permanecerán almacenados en el atributo de  `self.contratos`.
            Si es `False` (por defecto), los detalles se eliman del almacenamiento después de ser retornados.
            
        timeout : float, opcional
            Tiempo en segundos que el método esperará una respuesta antes de continuar. Por defecto, es de 10 segundos.
            
        Salida:
        -------
        return: list : Lista con los detalles de los contratos solicitados.
        """
        
        # Limpiar Evento
        self.evento_uso_comun.clear()
        # Llamar a método de las Clases Padres
        super().reqContractDetails(reqId=reqId, contract=contract)
        # Esperar respuesta
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        # Revisar respuesta
        if respuesta:
            contratos = self.contratos[contract.secType][reqId]
            # Eliminar Datos (Opcional)
            if not keep_stored:
                del self.contratos[contract.secType][reqId]
                if len(self.contratos[contract.secType]) == 0:
                    del self.contratos[contract.secType]
            
            return contratos
        
        
    def historicalData(self, reqId: int, bar) -> None:
        
        """
        Método para recibir y almacenar datos históricos proporcionados por la API de IB. Este método es llamado automáticamente
        como parte del flujo de datos históricos en respuesta a una solicitud previa.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud de datos históricos.
            
        bar : ibapi.common.BarData
            Objeto que representa un intervalo de datos históricos.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Extraer y almacenar los valores
        datos = [bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume]
        if reqId not in self.datos_precios:
            self.datos_precios[reqId] = []
        self.datos_precios[reqId].append(datos)
        
        
    def historicalDataEnd(self, reqId: int, start: str, end: str) -> None:
        
        """
        Método que se ejecuta al finalizar el envío de datos históricos
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud de datos históricos.
            
        start : str
            Marca de tiempo que indica el inicio del rango de datos históricos procesados (formato: 'YYYYMMDD HH:mm:ss').
            
        end : str
            Marca de tiempo que indica el final del rango de datos históricos procesados (formato: 'YYYYMMDD HH:mm:ss').
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Establecer Evento
        self.evento_uso_comun.set()
        
        
    def reqHistoricalData(self, reqId: int, contract: Contract, endDateTime: str = "", durationStr: str = "1 Y",
                          barSizeSetting: str = "1 day", whatToShow: str = "ADJUSTED_LAST", useRTH: int = 1, 
                          formatDate: int = 1, keepUpToDate: bool = False, chartOptions: list = [], keep_stored: bool = False,
                          timeout: float = 10.0, delayed_data: bool = False) -> pd.DataFrame:
        
        """
        Método para solicitar datos históricos de un activo financiero en un intervalo de tiempo especificado.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud.
            
        contract : Contract
            Objeto que define el contrato financiero (activo) del cual se solicitan los datos históricos.
            
        endDateTime : str, opcional
            Fecha y hora del fin del rango de datos solicitados (formato: 'YYYYMMDD HH:mm:ss'). Si se deja vacío,
            se considera el momento actual como el punto final.
            
        durationStr : str, opcional
            Duración del rango de datos solicitados (por ejemplo, "1 Y" para un año, "30 D" para 30 días).
            
        barSizeSetting : str, opcional
            Intervalo de tiempo para cada barra de datos.
            
        whatToShow : str, opcional
            Tipo de datos que se desea recibir (por ejemplo, "ADJUSTED_LAST" para precios ajustados).
            
        useRTH : int, opcional
            Si se establece el valor en 1, solo se incluyen datos del horario regular del mercado (Regular Trading Hours).
            Si se establece el valor en 0, se incluyen datos fuera de horario (Extended Trading Hours).
            
        formatDate : int, opciona
            Define el formato de la fecha: 1 para formato 'YYYYMMDD HH:mm:ss', 2 para timestamp UNIX.
            
        keepUpToDate : bool, opcional
            Si es True, los datos seguirán actualizandose en tiempo real. Por fecto, es False.
            
        chartOptions : list, opcional
            Lista de pares clave-valor para configuraciones adicionales del gráfico. Parámetro de uso interno.
            
        keep_stored : bool, opcional
            Si es `True`, los detalles de los datos permanecerán almacenados en el atributo de  `self.datos_precios`.
            Si es `False` (por defecto), los datos se eliman del almacenamiento después de ser retornados.
            
        timeout : float, opcional
            Tiempo en segundos que el método esperará una respuesta antes de continuar. Por defecto, es de 10 segundos.
            
        delayed_data : bool, opcional
            Si es True, solicita datos retrasados en lugar de datos en tiempo real. Por defecto, es False.
            
        Salida:
        -------
        return: pd.DataFrame : Datos históricos del activo solicitado.
        """
        
        # Limpiar Estado del Evento
        self.evento_uso_comun.clear()
        # Ajustar Data
        if not delayed_data:
            self.reqMarketDataType(marketDataType=1)
        else:
            self.reqMarketDataType(marketDataType=3)
        # Llamar al método de las clases Padres
        super().reqHistoricalData(reqId=reqId, contract=contract, endDateTime=endDateTime, durationStr=durationStr,
                                  barSizeSetting=barSizeSetting, whatToShow=whatToShow, useRTH=useRTH,
                                  formatDate=formatDate, keepUpToDate=keepUpToDate, chartOptions=chartOptions)
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        self.evento_uso_comun.clear()
        if respuesta:
            # Extraer Valores
            datos = pd.DataFrame(self.datos_precios[reqId], columns=["Date", "Open", "High", "Low", "Close", "Volume"])
            datos["Date"] = pd.to_datetime(datos["Date"])
            datos.set_index(["Date"], inplace=True)
            # Revisar si eliminar datos procesados
            if not keep_stored:
                del self.datos_precios[reqId]
                
            return datos
        
    
    def headTimestamp(self, reqId: int, headTimestamp: str) -> None:
        
        """
        Método que procesa y almacena la fecha más antigua disponible para un activo financiero proporcionada por IB.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud.
            
        headTimestamp : str
            Fecha más antigua disponible en formato 'YYYYMMDD HH:mm:ss'. Esta fecha representa el inicio de los datos históricos
            disponibles para el activo solicitado.
        
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Almacenar
        self.headTimestamp_value = headTimestamp
        self.evento_uso_comun.set()
        
        
    def reqHeadTimeStamp(self, reqId: int, contract: Contract, whatToShow: str = "ADJUSTED_LAST", useRTH: int = 1,
                         formatDate: int = 1, timeout: float = 3.0) -> str:
        
        """
        Método que nos permite conocer la fecha más antigua de datos para un instrumento financiero.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud.
            
        contract : Contract
            Objeto que define el contrato financiero (activo).
            
        whatToShow : str, opcional
            Tipo de datos que se desea solicitar (por ejemplo, "ADJUSTED_LAST" para precios ajustados).
            
        useRTH : int, opcional
            Si se establece el valor en 1, solo se incluyen datos del horario regular del mercado (Regular Trading Hours).
            Si se establece el valor en 0, se incluyen datos fuera de horario (Extended Trading Hours).
            
        formatDate : int, opciona
            Define el formato de la fecha: 1 para formato 'YYYYMMDD HH:mm:ss', 2 para timestamp UNIX.

        timeout : float, opcional
            Tiempo en segundos que el método esperará una respuesta antes de continuar. Por defecto, es de 3.0 segundos.
            
        Salida:
        -------
        return: str : Fecha más antigua disponible para el activo solicitado.
        """
        
        # Limpiar Estado Interno del Evento
        self.evento_uso_comun.clear()
        # Llamar al método de la clase de los Padres
        super().reqHeadTimeStamp(reqId=reqId, contract=contract, whatToShow=whatToShow, useRTH=useRTH, formatDate=formatDate)
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        if respuesta:
            fecha_disponibilidad_inicial = self.headTimestamp_value
            del self.headTimestamp_value
            
            return fecha_disponibilidad_inicial
        
        
    def reqMaxData(self, reqId: int, contract: Contract, **kwargs) -> pd.DataFrame:
        
        """
        Método para obtener todos los datos históricos disponibles para un activo financiero.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud.
            
        contract : Contract
            Objeto que define el contrato financiero (activo).
            
        **kwargs : dict
            Los parámetros adicionales que se le pueden pasar son aquellos que recibe el método de "reqHeadTimeStamp".
            
        Salida:
        -------
        return: pd.DataFrame : Registro máximo de datos históricos para el activo solicitado.
        """
            
        # Obtener fecha más antigua de datos
        fecha_mas_antigua = self.reqHeadTimeStamp(reqId=reqId, contract=contract, **kwargs)
        if isinstance(fecha_mas_antigua, str):
            fecha_mas_antigua = datetime.strptime(fecha_mas_antigua, "%Y%m%d %H:%M:%S")
            fecha_hoy = datetime.now()
            diferencia = int(fecha_hoy.year - fecha_mas_antigua.year + 1)
            # Obtener Datos
            df = self.reqHistoricalData(reqId=reqId, contract=contract, durationStr=f"{diferencia} Y", barSizeSetting="1 day",
                                        whatToShow=kwargs.get("whatToShow", "ADJUSTED_LAST"), timeout=None, delayed_data=True)
            
            return df
        
        
    def Save_to_DB(self, df: pd.DataFrame, db_path: str, table_name: str) -> None:
        
        """
        Método para guardar un DataFrame en una base de datos SQLite.
        
        Este método permite almacenar los datos contenidos en un DataFrame en una tabla específica dentro de una base de datos.
        Si la tabla no existe, se crea automáticamente con la estructura predeterminada.
        
        Parámetros:
        -----------
        df : pd.DataFrame
           El DataFrame que contiene los datos a almacenar. Deben incluir las columnas compatibles con la estrucutra de la tabla
           en la base de datos.
           
        db_path : str
            Ruta del archivo de la base de datos SQLite. Si el archivo no existe, se creará automáticamente.
            
        table_name : str
            El nombre de la tabla donde se guardarán los datos
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Conectar a la Base de Datos
        conn = sqlite3.connect(db_path)
        # Generar Cursor
        cursor = conn.cursor()
        # Definir estructura
        sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                date DATETIME PRIMARY KEY,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER
                )
        """
        # Ejecutar comando
        cursor.execute(sql)
        # Almacenar
        data = df.copy()
        data.index = data.index.strftime("%Y-%m-%d %H:%M:%S")
        lista_datos = data.reset_index().values.tolist()
        cursor.executemany(f"INSERT INTO {table_name} (date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)", lista_datos)
        # Confirmar comando
        conn.commit()
    
    
    def orderStatus(self, orderId: int, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int, parentId: int, 
                    lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float) -> None:
        
        """
        Método que muestra el estado de una orden existente con detalles específicos de ejecución y estado actual.
        
        Parámetros:
        -----------
        orderId : int
            El Identificador único de la orden que se está actualizando.
            
        status : str
            El estado actual de la orden. Puede ser 'Filled', 'Pending', etc.
            
        filled : float
            La cantidad de la orden que se ha llenado hasta este momento.
            
        avgFillPrice : float
            El precio promedio al que se ha llenado la orden hasta este momento.
            
        permId : int
            El Identificador único permanente para la orden, asignado por el sistema de ejecución.
            
        parentId : int
            El identificador de la orden principal en caso de que la orden sea una orden hija.
            
        lastFillPrice : float
            El precio al que se ejecutó la última cantidad de la orden.
            
        clientId : int
            El Identificador del cliente que realizó la orden.
            
        whyHeld : str
            Razón por la cual la orden está en espera, si aplica (por ejemplo, 'Margin' si es por margen).
            
        mktCapPrice : float
            Si se ha limitado una orden, indica el precio limitado actual.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Almacenar en archivo logs
        orden_estado_mensaje = (f"Id de la Orden: {orderId} - "
                                f"Estado de la Orden: {status} - "
                                f"Llenado: {filled} - "
                                f"Faltante: {remaining} - "
                                f"Precio Promedio Obtenido: {avgFillPrice} - "
                                f"Identificador Único Permanente para la Orden: {permId} - "
                                f"ID de la Orden Principal: {parentId} - "
                                f"Precio al que se Ejecutó la Última Cantidad de la Orden: {lastFillPrice} - ",
                                f"Id del cliente: {clientId} - "
                                f"Motivo por el cual la Orden está en espera (si aplica): {whyHeld}",
                                f"Precio de mercado de la Orden (Si corresponde): {mktCapPrice}")
        
        self.logger.info(orden_estado_mensaje)
        # Mostrar Consola
        if self.verbose:
            print(orden_estado_mensaje)
            
            
    def placeOrder(self, orderId: int, contract: Contract, order: Order) -> None:
        
        """
        Método que envía una orden de compra o venta para un contrato y una orden específicada.
        
        Parámetros:
        -----------
        orderId: int
            Identificador único de la orden que se desea enviar.
            
        contract : Contract
            Objeto que especifica los detalles del contrato financiero.
            
        order : Order
            Objeto que define los detalles de la orden.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Agregar mensaje de orden
        mensaje = f"Orden para {contract.symbol}. Tipo de Activo: {contract.secType}. Tipo de Orden: {order.orderType}"
        mensaje = mensaje + f" Posición: {order.action}"
        self.logger.info(mensaje)
        # Mandar a llamar al método de las clases Padres
        super().placeOrder(orderId=orderId, contract=contract, order=order)
        
        
    def cancelOrder(self, orderId: int) -> None:
        
        """
        Este método permite cancelar una orden en curso que aún no ha sido totalmente procesada en el mercado. Es útil para
        ajustar estrategias, detener operaciones imprevistas o reaccionar a cambios en las condiciones del mercado.
        
        Parámetros:
        -----------
        orderId: int
            Identificador único de la orden que se desea cancelar.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Agregar mensaje de la cancelación de la orden
        mensaje = f"Orden ha cancelar con el ID: {orderId}"
        self.logger.info(mensaje)
        # Llamar al método de la superclase
        super().cancelOrder(orderId=orderId)
        
        
    def openOrder(self, orderId: int, contract: Contract, order: Order, orderState) -> None:
        
        """
        Este método es invocado automáticamente cuando se recibe información sobre órdenes abiertas en el sistema de trading.
        Permite registrar detalles importantes de cada orden activa, incluyendo el contrato, tipo de orden y su estado actual.
        
        Parámetros:
        -----------
        orderId: int
            Identificador único de la orden.
            
        contract : Contract
            Objeto que especifica los detalles del contrato financiero.
            
        order : Order
            Objeto que define los detalles de la orden.
            
        orderState : OrderState
            Objeto que describe el estado actual de la orden, incluyendo si está pendiente, activa o completada.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Almacenar Órdenes
        self.ordenes_abiertas.append({
            "orderId": orderId,
            "activo": contract.symbol,
            "tipo_activo": contract.secType,
            "posicion": order.action,
            "tipo_orden": order.orderType,
            "estado_orden": orderState.status,
            "contrato": contract,
            "orden": order
            })
        
    
    def openOrderEnd(self) -> None:
        
        """
        Este método es utilizado para indicar que se ha completado la recepción de todas las órdenes abiertas enviadas por el
        servidor.
        
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Establecer bandera interna del Evento
        self.evento_uso_comun.set()
        
        
    def reqOpenOrders(self, keep_stored: bool = False, timeout: float = 3.0) -> pd.DataFrame:
        
        """
        Este método interactúa con la API para obtener una lista de órdenes abiertas asociadas con el cliente de la instancia
        generada.
        
        Parámetros:
        -----------
        keep_stored : bool, opcional
            Indica si se debe mantener almacenada la lista de órdenes abiertas en el atributo interno `self.ordenes_abiertas`.
            Por defecto es `False`.
            
        timeout : float, opcional
            Tiempo máximo (en segundos) para esperar la respuesta del servidor. El valor predeterminado es de 3.0 segundos.
            
        Salida:
        -------
        return: pd.DataFrame : DataFrame con las órdenes abiertas existentes asociadas con el cliente actual.
        """
        
        # Limpiar Estado del Evento
        self.evento_uso_comun.clear()
        # Limpiar lista de órdenes
        self.ordenes_abiertas.clear()
        # Llamar al método de las super clases
        super().reqOpenOrders()
        # Esperar Respuesta
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        self.evento_uso_comun.clear()
        # Estructura Órdenes
        if respuesta:
            # Obtener Órdenes
            ordenes = self.ordenes_abiertas
            # Revisar si hay órdenes
            if len(ordenes) == 0:
                return False
            ordenes = pd.DataFrame(ordenes)
            if not keep_stored:
                self.ordenes_abiertas.clear()
                
            return ordenes
        
        
    def reqAllOpenOrders(self, keep_stored: bool = False, timeout: float = 3.0) -> pd.DataFrame:
        
        """
        Este método solicita todas las órdenes abiertas en la cuenta, independientemente del cliente que las creó
        o si se generaron desde TWS.
        
        Parámetros:
        -----------
        keep_stored : bool, opcional
            Indica si se debe mantener almacenada la lista de órdenes abiertas en el atributo interno `self.ordenes_abiertas`.
            Por defecto es `False`.
            
        timeout : float, opcional
            Tiempo máximo (en segundos) para esperar la respuesta del servidor. El valor predeterminado es de 3.0 segundos.
            
        Salida:
        -------
        return: pd.DataFrame : DataFrame con las órdenes abiertas existentes asociadas con la cuenta.
        """
        
        # Limpiar Estado del Evento
        self.evento_uso_comun.clear()
        # Limpiar lista de órdenes
        self.ordenes_abiertas.clear()
        # Llamar al método de las super clases
        super().reqAllOpenOrders()
        # Esperar Respuesta
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        self.evento_uso_comun.clear()
        # Estructura Órdenes
        if respuesta:
            # Obtener Órdenes
            ordenes = self.ordenes_abiertas
            # Revisar si hay órdenes
            if len(ordenes) == 0:
                return False
            ordenes = pd.DataFrame(ordenes)
            if not keep_stored:
                self.ordenes_abiertas.clear()
                
            return ordenes
        
        
    def completedOrder(self, contract: Contract, order: Order, orderState) -> None:
        
        """
        Este método se invoca cuando se recibe la información de una orden que ya ha sido completamente ejecutada.
        
        Parámetros:
        -----------
        contract : Contract
            Objeto que contiene la información del contrato relacionado con la orden.
            
        order : Orden
            Objeto que detalla la configuración de la orden ejecutada.
            
        orderState : OrderState
            Objeto que proporciona el estado final de la orden, incluyendo datos como el tiempo de ejecución
            y las comisiones.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Almacenar
        info_ordenes = {
            
            "Simbolo": contract.symbol,
            "Tipo Activo": contract.secType,
            "Posición": order.action,
            "Tipo Orden": order.orderType,
            "Tiempo de Ejecución": orderState.completedTime,
            "Comisión": orderState.commission
            
            }
        self.ordenes_completadas.append(info_ordenes)
        # Mostrar Consola
        if self.verbose:
            print(info_ordenes)
            
            
    def completedOrdersEnd(self) -> None:
        
        """
        Método que se llama cuando todas las órdenes completadas se han recibido.
        
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Establecer Evento
        self.evento_uso_comun.set()
        
        
    def reqCompletedOrders(self, apiOnly: bool = False, keep_stored: bool = False, timeout: float = 3.0) -> pd.DataFrame:
        
        """
        Este método se utiliza para obtener detalles sobre las órdenes completadas de la cuenta. Puede filtrar las órdenes
        dependiendo de si fueron enviadas únicamente a través de la API o también desde otras interfaces como TWS.
        
        Parámetros:
        -----------
        apiOnly : bool, opcional
            Si es True, solicita únicamente las órdenes que fueron enviadas a través de la API.
            Por defecto es False, lo que incluye órdenes creadas desde otras interfaces.
            
        keep_stored : bool, opcional
            Indica si se debe mantener almacenada la lista de órdenes completadas en el atributo interno `self.ordenes_completadas`.
            Por defecto es `False`.
            
        timeout : float, opcional
            Tiempo máximo (en segundos) para esperar la respuesta del servidor. El valor predeterminado es de 3.0 segundos.
            
        Salida:
        -------
        return: pd.DataFrame : Órdenes completadas en un formato de DataFrame.
        """
        
        # Limpiar Evento y la lista de Órdenes Completadas
        self.evento_uso_comun.clear()
        self.ordenes_completadas.clear()
        # Llamar al método de la clase Padre
        super().reqCompletedOrders(apiOnly=apiOnly)
        # Esperar respuesta
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        self.evento_uso_comun.clear()
        # Estructura Órdenes Completadas
        if respuesta:
            # Obtener Valores
            ordenes_completadas = self.ordenes_completadas
            if len(ordenes_completadas) == 0:
                return False
            ordenes_completadas = pd.DataFrame(ordenes_completadas)
            if not keep_stored:
                self.ordenes_completadas.clear()
                
            return ordenes_completadas
        
        
    def market_order(self, action: str, totalQuantity: int, orderType: str = "MKT") -> Order:
        
        """
        Método que genera una orden de mercado.
        
        Este método crea y devuelve una instancia de una orden de mercado configurada con los parámetros especificados.
        Las órdenes de mercado se ejecutan al mejor precio disponible en el mercado en el momento de la ejecución.
        
        Parámetros:
        -----------
        action : str
            Define la acción que realizará la orden. Debe de ser "BUY" (comprar) o "SELL" (vender).
            
        totalQuantity :int
            Cantidad total de unidades (acciones, contratos, etc.) que se desean comprar o vender.
            
        orderType : str, opcional
            Tipo de orden. Por defecto es "MKT".
            
        Salida:
        -------
        return: ibapi.order.Order : Instancia de la clase `Order`.
        """
        
        # Generar Instancia
        orden_mercado = Order()
        orden_mercado.action = action
        orden_mercado.totalQuantity = totalQuantity
        orden_mercado.orderType = orderType
        orden_mercado.eTradeOnly = ""
        orden_mercado.firmQuoteOnly = ""
        
        return orden_mercado
        
        
    def limit_order(self, action: str, totalQuantity: int, lmtPrice: float, orderType: str = "LMT") -> Order:
        
        """
        Método que genera una orden de tipo límite.
        
        Este método crea y devuelve una instancia de una orden límite configurada con los parámetros que se han recibido.
        Las órdenes de tiop límite permiten al usuario establecer un precio específico al cual se desea comprar o vender.
        
        Parámetros:
        -----------
        action : str
            Define la acción que realizará la orden. Debe de ser "BUY" (comprar) o "SELL" (vender).
            
        totalQuantity : int
            Cantidad total de unidades (acciones, contratos, etc.) que se desean comprar o vender.
            
        lmtPrice : float
            Precio límite al cual se desea ejecutar la orden. Para órdenes de compra, la ejecución se producirá si el precio
            es igual o inferior al especificado. Para órdenes de venta, se ejecutará si el precio es igual o superior.
            
        orderType : str, opcional
            Tipo de orden. Por defecto es "LMT".
            
        Salida:
        -------
        return: ibapi.order.Order : Instancia de la clase `Order`.
        """
        
        # Generar Instancia
        orden_limite = Order()
        orden_limite.action = action
        orden_limite.totalQuantity = totalQuantity
        orden_limite.orderType = orderType
        orden_limite.lmtPrice = lmtPrice
        orden_limite.eTradeOnly = ""
        orden_limite.firmQuoteOnly = ""
        
        return orden_limite
    
    
    def tk_sl_order(self, orderId: int, orden_inicial_parametros: dict = {}, tp_parametros: dict = {}, sl_parametros: dict = {}) -> list:
        
        """
        Método que crea una orden de mercado inicial junto con órdenes asociadas de Take Profit y Stop Loss.
        
        Este método genera un conjunto de 3 órdenes:
            1. Una orden inicial (de mercado o límite) para ejecutar la operación principal.
            2. Una orden de Stop Loss para limitar pérdidas si el mercado se mueve en contra.
            3. Una orden de Take Profit para cerrar la operación una vez alcanzado el objetivo de ganancia.
            
        Parámetros:
        ----------
        orderId : int
            Identificador único para la orden inicial. Las órdenes asociadas tendrán `orderId` consecutivos.
    
        orden_inicial_parametros : dict, opcional
            Parámetros para configurar la orden inicial. Las claves disponibles son:
                - "action" (str): Acción de la orden, "BUY" o "SELL". Por defecto es "BUY".
                - "orderType" (str): Tipo de orden inicial, por defecto "MKT" (orden de mercado).
                - "lmtPrice" (float): Precio límite (opcional, requerido solo si `orderType` es "LMT").
                - "totalQuantity" (int): Cantidad total de unidades a operar. Por defecto es 1.
        
        tp_parametros : dict, opcional
            Parámetros para configurar la orden de Take Profit. Las claves disponibles son:
                - "action" (str): Acción de la orden, "SELL" o "BUY". Por defecto es "SELL".
                - "orderType" (str): Tipo de orden, por defecto "LMT".
                - "lmtPrice" (float): Precio límite requerido para el Take Profit.
                - "totalQuantity" (int): Cantidad total de unidades a operar. Por defecto es 1.
    
        sl_parametros : dict, opcional
            Parámetros para configurar la orden de Stop Loss. Las claves disponibles son:
                - "action" (str): Acción de la orden, "SELL" o "BUY". Por defecto es "SELL".
                - "orderType" (str): Tipo de orden, por defecto "STP".
                - "auxPrice" (float): Precio auxiliar requerido para el Stop Loss.
                - "totalQuantity" (int): Cantidad total de unidades a operar. Por defecto es 1.
                
        Salida:
        -------
        return: list : Lista que contiene las tres órdenes configuradas en el siguiente orden:
                        [orden_inicial, orden_stop, orden_limite].
        """
        
        # Orden de mercado
        orden_inicial = Order()
        orden_inicial.orderId = orderId
        orden_inicial.action = orden_inicial_parametros.get("action", "BUY")
        orden_inicial.orderType = orden_inicial_parametros.get("orderType", "MKT")
        orden_inicial.lmtPrice = orden_inicial_parametros.get("lmtPrice", orden_inicial.lmtPrice)
        orden_inicial.totalQuantity = orden_inicial_parametros.get("totalQuantity", 1)
        orden_inicial.eTradeOnly = ""
        orden_inicial.firmQuoteOnly = ""
        orden_inicial.transmit = False
        
        # Orden de Stop Loss
        orden_stop = Order()
        orden_stop.parentId = orden_inicial.orderId
        orden_stop.orderId = orden_inicial.orderId + 1
        orden_stop.action = sl_parametros.get("action", "SELL")
        orden_stop.orderType = sl_parametros.get("orderType", "STP")
        orden_stop.totalQuantity = sl_parametros.get("totalQuantity", 1)
        
        if sl_parametros.get("auxPrice", None) is None:
            raise ValueError("El Precio Auxiliar para la orden del Stop Loss debe de ser pasado")
            
        orden_stop.auxPrice = sl_parametros["auxPrice"]
        orden_stop.eTradeOnly = ""
        orden_stop.firmQuoteOnly = ""
        orden_stop.transmit = False
        
        # Orden de Take Profit
        orden_tk = Order()
        orden_tk.parentId = orden_inicial.orderId
        orden_tk.orderId = orden_inicial.orderId + 2
        orden_tk.action = tp_parametros.get("action", "SELL")
        orden_tk.orderType = tp_parametros.get("orderType", "LMT")
        orden_tk.totalQuantity = tp_parametros.get("totalQuantity", 1)
        
        if tp_parametros.get("lmtPrice", None) is None:
            raise ValueError("El Precio Límite para la orden de Tipo Límite debe de ser pasado")

        orden_tk.lmtPrice = tp_parametros["lmtPrice"]
        orden_tk.eTradeOnly = ""
        orden_tk.firmQuoteOnly = ""
        orden_tk.transmit = True
        
        
        return [orden_inicial, orden_stop, orden_tk]
    
    
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str) -> None:
        
        """
        Método que recibe y procesa la información detallada de un resumen de cuenta proporcionado por el sistema.
        
        Este método se utiliza para capturar y almacenar información relevante de un cuenta, como su identificación,
        etiquetas específicas, valores asociados, y la moneda correspondiente.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud asociada al resumen de la cuenta.
            
        account : str
            Identificación de la cuenta para la cual se ha generado el resumen.
            
        tag : str
            Etiqueta o clave que describe el tipo de información reportada (ejemplo: 'NetLiquidation', 'BuyingPower').
            
        value : str
            Valor asociado a la etiqueta especificada (puede ser un número o texto, dependiendo de la etiqueta).
            
        currency : str
            Moneda en la que se expresa el valor (ejemplo: 'USD', 'EUR').
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Almacenar
        self.account_summary.append({
            
            "reqId": reqId,
            "account": account,
            "tag": tag,
            "value": value,
            "currency": currency
            
            })
        # Mostrar Consola
        if self.verbose:
            print(f"Cuenta: {account}, Etiqueta: {tag}, Valor: {value}, Moneda: {currency}")
            
            
    def accountSummaryEnd(self, reqId: int) -> None:
        
        """
        Método que indica la finalización de la transmisión del resumen de la cuenta.
        
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Establecer Evento
        self.evento_uso_comun.set()
        
    
    def reqAccountSummary(self, reqId: int, groupName: str = "All", tags: str = "$LEDGER:USD", keep_stored: bool = False, 
                          timeout: float = 4.0) -> pd.DataFrame:
        
        """
        Método para solicitar el resumen de una cuenta específica.
        
        Este método permite enviar una solicitud al sistema para obtener información resumida de una cuenta,
        como datos financieros, balance, y otros indicadores relevantes.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único para la solicitud del resumen de la cuenta.
            
        groupName : str, opcional
            Nombre del grupo de cuentas que se desean consultar. Por defecto, se consulta 'All' (todas las cuentas disponibles).
            
        tags : str, opcional
            Filtro para especificar que datos se deben incluir en el resumen. Por defecto, se solicita la información
            de los libros contables en USD ('$LEDGER:USD').
            
        keep_stored : bool, opcional
            Indica si se debe mantener almacenado el resumen de la cuenta en el atributo `self.account_summary`.
            Por defecto es `False`.
            
        timeout : float, opcional
            Tiempo máximo (en segundos) para esperar la respuesta del servidor. El valor predeterminado es de 4.0 segundos.
            
        Salida:
        -------
        return: pd.DataFrame : Resumen de la cuenta solicitada.
        """
        
        # Limpiar Evento y lista
        self.evento_uso_comun.clear()
        self.account_summary.clear()
        # Llamar al método de la clase Padre
        super().reqAccountSummary(reqId=reqId, groupName=groupName, tags=tags)
        # Esperar respuesta
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        self.evento_uso_comun.clear()
        # Cancelar Suscripción
        self.cancelAccountSummary(reqId=reqId)
        if respuesta:
            account_summary = pd.DataFrame(self.account_summary)
            if not keep_stored:
                self.account_summary.clear()
                
            return account_summary
        
        
    def position(self, account: str, contract: Contract, position: float, avgCost: float) -> None:
        
        """
        Método para procesar y almacenar información sobre las posiciones actuales en la cuenta.
        
        Parámetros:
        -----------
        account : str
            Identificador de la cuenta donde se mantiene la posición.
            
        contract : Contract
            Objeto que describe el activo asociado con la petición.
            
        position : float
            Cantidad de unidades de la posición. Un valor positivo indica una posición larga, mientras que
            un valor negativo indica una posición corta.
            
        avgCost : float
            Costo promedio por unidada del activo en la posición.
                    
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Almacenar
        diccionario = {"Cuenta": account, "Símbolo": contract.symbol, "Tipo Activo": contract.secType,
                       "exchange": contract.exchange, "Cantidad": position, "Costo Promedio": avgCost,
                       "Valor Total Posición": position * avgCost, "contrato": contract}
        self.posiciones.append(diccionario)
        # Mostrar Consola
        if self.verbose:
            print(diccionario)
        
        
    def positionEnd(self) -> None:
        
        """
        Método que indica la finalización del envío de información sobre las posiciones abiertas.
                
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Establecer Evento
        self.evento_uso_comun.set()
        
        
    def reqPositions(self, keep_stored: bool = False, timeout: float = 5.0) -> pd.DataFrame:
        
        """
        Método que solicita las posiciones abiertas en la cuenta asociada y espera la respuesta.
        
        Parámetros:
        -----------
        keep_stored : bool, opcional
            Indica si se debe mantener almacenado el resumen de las posiciones en el atributo `self.posiciones`.
            Por defecto es `False`.
            
        timeout : float, opcional
            Tiempo máximo (en segundos) para esperar la respuesta del servidor. El valor predeterminado es de 5.0 segundos.
            
        Salida:
        -------
        return: pd.DataFrame : Un DataFrame con las posiciones abiertas en la cuenta.
        """
        
        # Limpiar Evento y lista de posiciones
        self.evento_uso_comun.clear()
        self.posiciones.clear()
        # Llamar al método de SuperClase
        super().reqPositions()
        # Esperar Respuesta
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        self.evento_uso_comun.clear()
        # Cancelar Suscripción a las posiciones
        self.cancelPositions()
        # Comprobar Respuesta
        if respuesta:
            if len(self.posiciones) == 0:
                return False
            posiciones = pd.DataFrame(self.posiciones)
            if not keep_stored:
                self.posiciones.clear()
                
            return posiciones
        
        
    def pnl(self, reqId: int, dailyPnL: float, unrealizedPnL: float, realizedPnL: float) -> None:
        
        """
        Método que recibe y almacena la información del Profit and Loss (PnL) de la cuenta.
        
        Este método es llamado cada vez que se recibe información sobre el estado de las ganancias o pérdidas de la cuenta.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud asociada al cálculo del PnL.
            
        dailyPnL : float
            Ganancia o Pérdida diaria de la cuenta.
            
        unrealizedPnL : float
            Ganancia o Pérdida no realizada, es decir, correspondiente a las posiciones abiertas.
            
        realizedPnL : float
            Ganancia o Pérdida realizada, correspondiente a las posiciones cerradas.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Almacenar Información
        info = {"reqId": reqId, "PnL Diario": dailyPnL, "PnL No Realizado": unrealizedPnL, "PnL Realizado": realizedPnL}
        self.pnl_account.append(info)
        # Desplegar en Consola
        if self.verbose:
            print(info)
        # Establecer Evento
        self.evento_uso_comun.set()
        
        
    def reqPnL(self, reqId: int, account: str, modelCode: str = "", keep_stored: bool = False, timeout: float = 2.0) -> pd.DataFrame:
        
        """
        Método que solicita información sobre las Ganancias y Pérdidas de la cuenta.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud asociada al cálculo del PnL.
            
        account : str
            El Identificador de la cuenta para la cual se desea obtener la información del PnL.
            
        modelCode : str, opcional
            Código del modelo para obtener los PnL asociados a un modelo específico. Si no se proporciona, se utiliza una cade de texto vacía.
            
        keep_stored : bool, opcional
            Indica si se debe mantener almacenado el resumen de las ganancias y pérdidas de la cuenta en  `self.pnl_account`.
            Por defecto es `False`.
            
        timeout : float, opcional
            Tiempo máximo (en segundos) para esperar la respuesta del servidor. El valor predeterminado es de 2.0 segundos.
            
        Salida:
        -------
        return: pd.DataFrame : Un DataFrame con la información de las ganancias y pérdidas de la cuenta.
        """
        
        # Limpiar Evento y lista de PnL
        self.evento_uso_comun.clear()
        self.pnl_account.clear()
        # Llamar al método de SuperClase
        super().reqPnL(reqId=reqId, account=account, modelCode=modelCode)
        # Esperar Respuesta
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        self.evento_uso_comun.clear()
        # Cancelar Suscripción
        self.cancelPnL(reqId=reqId)
        # Comprobar Respuesta
        if respuesta:
            pnl = pd.DataFrame(self.pnl_account)
            if not keep_stored:
                self.pnl_account.clear()
                
            return pnl
        
        
    def existing_order_position(self, ticker: str) -> bool:
        
        """
        Método que revisa si hay una posición existente o una orden abierta para un activo en específico.
        
        Parámetros:
        -----------
        ticker : str
            El Símbolo del activo que se desea verificar.
            
        Salida:
        -------
        return: bool : True si el activo se encuentra en órdenes abiertas o posiciones activas, Falso en caso contrario.
        """
        
        # Obtener Órdenes Abiertas
        ordenes = self.reqAllOpenOrders(keep_stored=False, timeout=3.0)
        # Obtener Posiciones Existentes
        posiciones = self.reqPositions(keep_stored=False, timeout=5.0)
        
        # Revisar
        condicion = False
        if isinstance(ordenes, pd.DataFrame):
            # Verificar si el ticker está presente en las órdenes abiertas
            condicion += (ticker in ordenes["activo"].values)
        # Revisar que no tengamos posiciones activas en el ticker
        if isinstance(posiciones, pd.DataFrame):
            sub_condicion = (ticker in posiciones["Símbolo"].values)
            # Validar que la suma de las posiciones sea diferente de cero
            if sub_condicion:
                sub_posiciones = posiciones[posiciones["Símbolo"] == ticker]
                if sub_posiciones["Cantidad"].sum() != 0:
                    condicion += True
                else:
                    condicion += False
                    
        return True if condicion > 0 else False
        
        
    def end_session_summary(self, account: str) -> dict:
        
        """
        Método que genera un resumen general de la cuenta solicitando diferetntes tipos de información.
        
        Este método recopila datos relevantes sobre la cuenta, incluyendo las posiciones abiertas, el PnL, las órdenes abiertas,
        el resumen de la cuenta, y las órdenes completadas.
        
        Parámetros:
        -----------
        account : str
            Identificador de la cuenta para cual se solicita el resumen.
            
        Salida:
        -------
        return: dict : Diccionario con la información recopilada.
        """
        
        salida = {}
        # Solicitar Posiciones
        posiciones = self.reqPositions(keep_stored=False, timeout=5.0)
        if posiciones is not False:
            salida["posiciones"] = posiciones
        # Solicitar PnL
        pnl = self.reqPnL(reqId=1, account=account)
        salida["pnl"] = pnl
        # Órdenes Abiertas
        ordenes = self.reqAllOpenOrders(keep_stored=False, timeout=3.0)
        if ordenes is not False:
            salida["ordenes"] = ordenes
        # Información de la Cuenta
        etiquetas = "AccountType,NetLiquidation,TotalCashValue,AvailableFunds"
        resumen_cuenta = self.reqAccountSummary(reqId=1, groupName="All", tags=etiquetas)
        salida["resumen_cuenta"] = resumen_cuenta
        # Órdenes Completadas
        ordenes_completadas = self.reqCompletedOrders(apiOnly=False, keep_stored=False, timeout=3.0)
        if ordenes_completadas is not False:
            salida["ordenes_completadas"] = ordenes_completadas
            
        return salida
    
    
    def end_session(self, account: str, close_orders: bool = False, close_positions: bool = False) -> None:
        
        """
        Método encargado de registrar el estado final de la cuenta al finalizar la sesión de trading, con la opción
        de cerrar las órdenes abiertas y las posiciones existentes.
        
        Parámetros:
        -----------
        account : str
            Identificador único de la cuenta para la cual se solicita el resumen final de la sesión.
            
        close_orders : bool, opcional
            Si se establece como True, cancela todas las órdenes abiertas en la cuenta. El valor por defecto es False.
            
        close_positions : bool, opcional
            Si se establece como True, cierra todas las posiciones abiertas en la cuenta. El valor por defecto es False.
            
        Salida:
        -------
        return: NoneType : None.
        """
        
        # Solicitar Resumen Final
        resumen_final = self.end_session_summary(account=account)
        # Guardar Info en Logs
        self.logger.info("Estado Final de la Sesión (antes de realizar modificaciones):")
        
        # Iterar sobre el diccionario (Posiciones, Órdenes, etc)
        for clave in resumen_final:
            for indice, valores in resumen_final[clave].iterrows():
                valores_dict = valores.to_dict()
                estructura_inicial = ": {} - ".join(valores.keys())
                valores_registros = list(valores_dict.values())
                estructura_final = estructura_inicial.format(*valores_registros)
                self.logger.info(f"Clave: {clave} -> {estructura_final}")
                if self.verbose:
                    print(f"{clave}:", estructura_final)
                    
        # Cerrar Órdenes Abiertas
        if close_orders:
            self.reqGlobalCancel()
            
        # Cerrar Posiciones de la Cuenta
        if close_positions:
            if resumen_final.get("posiciones", False) is not False:
                # Filtrar las posiciones que tienen cantidad diferente de cero (es decir, aquellas que estén abiertas)
                posiciones = resumen_final["posiciones"][resumen_final["posiciones"]["Cantidad"] != 0]
                # Iterar sobre cada posición activa para cerrarla
                for indice, posicion_individual in posiciones.iterrows():
                    # Obtener el siguiente Id válido
                    next_id = self.reqIds(numIds=-1)
                    # Cerrar Posiciones
                    if posicion_individual["Tipo Activo"].lower() == "stk":
                        # Crear Contrato
                        contrato_accion = Contract()
                        contrato_accion.symbol = posicion_individual["Símbolo"]
                        contrato_accion.secType = posicion_individual["Tipo Activo"]
                        contrato_accion.currency = "USD"
                        contrato_accion.exchange = "SMART"
                        # Crear Orden
                        direccion = "SELL" if posicion_individual["Cantidad"] > 0 else "BUY"
                        orden_mercado = self.market_order(action=direccion, totalQuantity=abs(posicion_individual["Cantidad"]),
                                                          orderType="MKT")
                        self.placeOrder(orderId=next_id, contract=contrato_accion, order=orden_mercado)
                    elif posicion_individual["Tipo Activo"].lower() == "opt":
                        # Crear Contrato
                        contrato_opcion = Contract()
                        contrato_opcion.symbol = posicion_individual["Símbolo"]
                        contrato_opcion.secType = posicion_individual["Tipo Activo"]
                        contrato_opcion.strike = posicion_individual["contrato"].strike
                        contrato_opcion.currency = "USD"
                        contrato_opcion.exchange = "BOX"
                        vencimiento = posicion_individual["contrato"].lastTradeDateOrContractMonth
                        contrato_opcion.lastTradeDateOrContractMonth = vencimiento
                        contrato_opcion.right = posicion_individual["contrato"].right
                        # Crear Orden
                        direccion = "SELL" if posicion_individual["Cantidad"] > 0 else "BUY"
                        orden_mercado = self.market_order(action=direccion, totalQuantity=abs(posicion_individual["Cantidad"]),
                                                          orderType="MKT")
                        self.placeOrder(orderId=next_id, contract=contrato_opcion, order=orden_mercado)
                    elif posicion_individual["Tipo Activo"].lower() == "fut":
                        # Crear Contrato
                        contrato_futuros = Contract()
                        contrato_futuros.symbol = posicion_individual["Símbolo"]
                        contrato_futuros.secType = posicion_individual["Tipo Activo"]
                        contrato_futuros.currency = "USD"
                        contrato_futuros.exchange = "COMEX"
                        vencimiento = posicion_individual["contrato"].lastTradeDateOrContractMonth
                        contrato_futuros.lastTradeDateOrContractMonth = vencimiento
                        # Crear Orden
                        direccion = "SELL" if posicion_individual["Cantidad"] > 0 else "BUY"
                        orden_mercado = self.market_order(action=direccion, totalQuantity=abs(posicion_individual["Cantidad"]),
                                                          orderType="MKT")
                        self.placeOrder(orderId=next_id, contract=contrato_futuros, order=orden_mercado)
                    else:
                        self.logger.warn("No se ha podido cerrar una posición:")
                        self.logger.info(f"Cuenta: {posicion_individual['Cuenta']} - "
                                         f"Símbolo: {posicion_individual['Símbolo']} - "
                                         f"Tipo Activo: {posicion_individual['Tipo Activo']}"
                                         f"Cantidad: {posicion_individual['Cantidad']}")
            
    
    def scannerData(self, reqId: int, rank: int, contractDetails, distance: str, benchmark: str, projection: str, legsStr: str) -> None:
        
        """
        Método que procesa y almacena los resultados que cumplen con los filtros del escáner.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud del escáner.
            
        rank : int
            Posición del instrumento en el ranking del escáner.
            
        contractDetails : object
            Objeto que contiene los detalles del contrato asociado al instrumento detectado.
            
        distance : str
            Parámetro de uso interno.
            
        benchmark : str
            Parámetro de uso interno.
            
        projection : str
            Parámetro de uso interno.
            
        legsStr : str
            Detalles de las partes del contrato si se trata de un derivado o spread.
            
        Salida:
        -------
        return: NoneType : None.
        """

        # Almacenar registros
        registro = {
            
            "reqId": reqId,
            "rank": rank,
            "Instrumento": contractDetails.contract.symbol,
            "Tipo Activo": contractDetails.contract.secType,
            "Divisa": contractDetails.contract.currency,
            "Exchange": contractDetails.contract.exchange,
            "contrato Detalles": contractDetails
            
            
            }
        
        # Revisar si ya existe el ID
        if reqId not in self.escaner_resultados:
            self.escaner_resultados[reqId] = []
            
        self.escaner_resultados[reqId].append(registro)
        
    
    def scannerDataEnd(self, reqId: int) -> None:
        
        """
        Este método se manda a llamar una vez que se han procesado todos los registros del escáner.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud del escáner.

        Salida:
        -------
        return: NoneType : None.
        """
        
        # Establecer Evento
        self.evento_uso_comun.set()
        
        
    def reqScannerSubscription(self, reqId: int, subscription: ScannerSubscription, scannerSubscriptionOptions: list, 
                               scannerSubscriptionFilterOptions: list, keep_stored: bool = False, timeout: float = 15.0) -> pd.DataFrame:
        
        """
        Método para suscribirse a un escáner de mercado en tiempo real. Este escáner permite recibir información sobre instrumentos
        financieros que cumplen con ciertos criterios de búsqueda definidos en el objeto de la suscripción.
        
        Parámetros:
        -----------
        reqId : int
            Identificador único de la solicitud del escáner.

        subscription : ScannerSubscription
            Objeto que define los criterios de búsqueda del escáner, como tipos de activos, exchanges y filtros.

        scannerSubscriptionOptions : list
            Opciones adicionales para la suscripción al scáner.

        scannerSubscriptionFilterOptions : list
            Opciones específicas para aplicar filtros adicionales en la búsqueda.
            
        keep_stored : bool, opcional
            Indica si se debe mantener almacenado el resultado del escáner en `self.escaner_resultados`.
            Por defecto es `False`.
            
        timeout : float, opcional
            Tiempo máximo (en segundos) para esperar la respuesta del servidor. El valor predeterminado es de 15.0 segundos.

        Salida:
        -------
        return: pd.DataFrame : Un DataFrame con el resultado del Escáner.
        """
        
        # Limpiar Evento
        self.evento_uso_comun.clear()
        # Hacer un reset de la clave si ya existe
        if reqId in self.escaner_resultados:
            self.escaner_resultados[reqId].clear()
        # Mandar a llamar al método de la superclase
        super().reqScannerSubscription(reqId=reqId, subscription=subscription, scannerSubscriptionOptions=scannerSubscriptionOptions, 
                                       scannerSubscriptionFilterOptions=scannerSubscriptionFilterOptions)
        # Esperar respuesta
        respuesta = self.evento_uso_comun.wait(timeout=timeout)
        self.evento_uso_comun.clear()
        # Cancelar Suscripción
        self.cancelScannerSubscription(reqId=reqId)
        # Validar Petición
        if respuesta:
            # Convertir a DataFrame
            escaner_resultados = pd.DataFrame(self.escaner_resultados[reqId])
            if not keep_stored:
                del self.escaner_resultados[reqId]
                
            return escaner_resultados
        

# Recordatorio:
if __name__ == "__main__":
    
    # Generar Instancia de la Clase
    IB_Instancia = IB_Trading(mode="a", errors_verbose=True, verbose=False)

    # Limpiar Logs (Eliminar Datos Existentes)
    IB_Instancia.clear_logs()      
        
    # Conectar al servidor de IB
    IB_Instancia.connect(host="127.0.0.1", port=7497, clientId=1)
    
    # Realizar Petición del Siguiente Id Válido
    next_order_id = IB_Instancia.reqIds(numIds=-1)
    print("Siguiente ID Válido:", next_order_id)

    # Crear Contrato de Acciones
    contrato_acciones = Contract() 
    contrato_acciones.symbol = "AMZN"
    contrato_acciones.secType = "STK"
    contrato_acciones.exchange = "SMART"
    contrato_acciones.currency = "USD"       
        
    # Solicitar Detalles del Contrato
    reqId = 1
    contratos = IB_Instancia.reqContractDetails(reqId=reqId, contract=contrato_acciones, keep_stored=False, timeout=10.0)
    
    # Mostrar Detalles del Contrato
    print("Detalles del Contrato:\n", contratos[0])
    
    # Crear Contrato de Opciones
    contrato_opciones = Contract()
    contrato_opciones.symbol = "AMZN"
    contrato_opciones.secType = "OPT"
    contrato_opciones.exchange = "BOX"
    contrato_opciones.currency = "USD"
    # Definir el siguiente viernes como vencimiento
    fecha_hoy = datetime.now()
    dias_restantes = (4 - fecha_hoy.weekday()) + 7
    viernes_siguiente = (fecha_hoy + timedelta(days=dias_restantes)).strftime("%Y%m%d")
    contrato_opciones.lastTradeDateOrContractMonth = viernes_siguiente
    contrato_opciones.right = "C"
        
    # Solicitar Datos
    reqId = 1
    contratos_opciones = IB_Instancia.reqContractDetails(reqId=reqId, contract=contrato_opciones, keep_stored=True, timeout=None)
        
    # Mostrar Detalles de los diferentes contratos existentes
    print("Detalles de los Contratos:\n", contratos_opciones)
    print("Claves en el Atributo de Contratos:", IB_Instancia.contratos.keys())  
    print("Hay un total de {} contratos activos".format(len(IB_Instancia.contratos[contrato_opciones.secType][reqId])))    
        
    # Descargar Datos Históricos
    contrato_datos = Contract() 
    contrato_datos.symbol = "TSLA"
    contrato_datos.secType = "STK"
    contrato_datos.exchange = "SMART"
    contrato_datos.currency = "USD" 
    # Datos Diarios
    df1 = IB_Instancia.reqHistoricalData(reqId=1, contract=contrato_datos, delayed_data=True)
    print(df1)
    print(IB_Instancia.datos_precios)
    # Datos Intradía
    df2 = IB_Instancia.reqHistoricalData(reqId=2, contract=contrato_datos, durationStr="1 D", barSizeSetting="5 secs",
                                         keep_stored=True, timeout=None, delayed_data=True)
    print(df2)
    print(IB_Instancia.datos_precios)
    
    # Obtener Fecha más Antigua
    contrato_fecha = Contract()
    contrato_fecha.symbol = "AAPL"
    contrato_fecha.secType = "STK"
    contrato_fecha.exchange = "SMART"
    contrato_fecha.currency = "USD" 
    fecha_mas_antigua = IB_Instancia.reqHeadTimeStamp(reqId=1, contract=contrato_fecha)
    print("Fecha más antigua:", fecha_mas_antigua)
        
    # Extraer Datos Históricos Disponibles
    contrato_max_data = Contract()
    contrato_max_data.symbol = "AAPL"
    contrato_max_data.secType = "STK"
    contrato_max_data.exchange = "SMART"
    contrato_max_data.currency = "USD" 
    df_max = IB_Instancia.reqMaxData(reqId=3, contract=contrato_max_data, whatToShow="ADJUSTED_LAST")
    print(df_max)        
        
    # Almacenar Datos
    df_casi_max = df_max.iloc[:-100]
    print(df_casi_max)        
    df_restantes_max = df_max.iloc[-100:] 
    print(df_restantes_max)

    # Guardar el primer conjunto
    db_path = "AAPL.db"
    table_name = "AAPL_Stock"
    IB_Instancia.Save_to_DB(df=df_casi_max, db_path=db_path, table_name=table_name)        
        
    # Leer Datos Parciales
    conn = sqlite3.connect(db_path)
    datos_db = pd.read_sql(sql=f"SELECT * FROM {table_name}", con=conn)
    print(datos_db)        
    # Agregar Más Datos a Base de Datos Existente
    IB_Instancia.Save_to_DB(df=df_restantes_max, db_path=db_path, table_name=table_name)
    # Leer Datos Completados
    datos_db = pd.read_sql(sql=f"SELECT * FROM {table_name}", con=conn)    
    print(datos_db)            
    if len(datos_db) == len(df_max):
        print("!Datos guardados exitosamente!")
        
    # Crear Contrato Para Orden
    contrato_orden = Contract()
    contrato_orden.symbol = "TSLA"
    contrato_orden.secType = "STK"
    contrato_orden.exchange = "SMART"
    contrato_orden.currency = "USD" 
    # Crear Orden de Mercado
    orden_mercado = IB_Instancia.market_order(action="BUY", totalQuantity=100)
    next_id = IB_Instancia.reqIds(-1)
    IB_Instancia.placeOrder(orderId=next_id, contract=contrato_orden, order=orden_mercado)
        
    # Solicitar Órdenes Completadas
    ordenes_completadas = IB_Instancia.reqCompletedOrders()
    print(ordenes_completadas)        
        
    # Crear Contrato Para Orden (Tipo de Límite)
    contrato_orden_limite = Contract()
    contrato_orden_limite.symbol = "AAPL"
    contrato_orden_limite.secType = "STK"
    contrato_orden_limite.exchange = "SMART"
    contrato_orden_limite.currency = "USD" 
    orden_limite = IB_Instancia.limit_order(action="BUY", totalQuantity=100, lmtPrice=240)
    next_id = IB_Instancia.reqIds(-1)
    IB_Instancia.placeOrder(orderId=next_id, contract=contrato_orden_limite, order=orden_limite)
        
    # Obtener Órdenes Abiertas
    ordenes_abiertas = IB_Instancia.reqOpenOrders(keep_stored=False, timeout=3.0)
    print(ordenes_abiertas)    
    
    ordenes_abiertas_cuentas = IB_Instancia.reqAllOpenOrders(keep_stored=False, timeout=3.0)        
    print(ordenes_abiertas_cuentas)        
    
    # Cancelar Orden
    IB_Instancia.cancelOrder(orderId=next_id)        
        
    # Abrir Orden con TP y SL
    contrato_orden_tk_stl = Contract()
    contrato_orden_tk_stl.symbol = "META"
    contrato_orden_tk_stl.secType = "STK"
    contrato_orden_tk_stl.exchange = "SMART"
    contrato_orden_tk_stl.currency = "USD" 
    next_id = IB_Instancia.reqIds(-1) 
    ordenes = IB_Instancia.tk_sl_order(orderId=next_id, orden_inicial_parametros={"action": "BUY", "orderType": "MKT", "totalQuantity":10},
                                       tp_parametros={"action": "SELL", "orderType": "LMT", "totalQuantity":10, "lmtPrice": 620},
                                       sl_parametros={"action": "SELL", "orderType": "STP", "totalQuantity": 10, "auxPrice": 580})
    # Ejecutar Órdenes
    for orden in ordenes:
        IB_Instancia.placeOrder(orderId=orden.orderId, contract=contrato_orden_tk_stl, order=orden)
   
    
    # Resumen de Cuenta
    resumen_cuenta = IB_Instancia.reqAccountSummary(reqId=1)
    print(resumen_cuenta)
    etiquetas = "AccountType,NetLiquidation,TotalCashValue"    
    resumen_cuenta_especifico = IB_Instancia.reqAccountSummary(reqId=2, groupName="All", tags=etiquetas)
    print(resumen_cuenta_especifico)
    
    # Obtener Posiciones en la Cuenta
    posiciones_cuenta = IB_Instancia.reqPositions(keep_stored=False, timeout=5.0)
    print(posiciones_cuenta)
    
    # Obtener la ganancia/pérdida de la cuenta.
    pnl_cuenta = IB_Instancia.reqPnL(reqId=1, account=resumen_cuenta["account"].iloc[0])
    print(pnl_cuenta)    
    
    # Revisar si hay un activo en nuestra cuenta o en las órdenes
    ticker = "TSLA"
    existing_asset = IB_Instancia.existing_order_position(ticker)
    if existing_asset:
        print("¡Ya hay una posición o una orden existente de ese activo en el portafolio!")
    
    # Obtener Resumen Final
    resumen_final = IB_Instancia.end_session_summary(account=resumen_cuenta["account"].iloc[0])
    print("Posiciones:\n\n", resumen_final["posiciones"])    
    print("PnL:\n\n", resumen_final["pnl"])
    print("Órdenes Activas:\n\n", resumen_final["ordenes"])
    print("Resumen Cuenta:\n\n", resumen_final["resumen_cuenta"])    
    print("Órdenes Completadas:\n\n", resumen_final["ordenes_completadas"])
    
    # Cerrar Sesión
    IB_Instancia.end_session(account=resumen_cuenta["account"].iloc[0], close_orders=True, close_positions=True)

    # Esperar 10
    time.sleep(10)    
        
    # Obtener Nuevamente Posiciones
    posiciones_actualizadas = IB_Instancia.reqPositions()    
    print(posiciones_actualizadas.iloc[:, :-2])        
        
    # Realizar Petición al Escáner
    suscripcion = ScannerSubscription()
    suscripcion.instrument = "STK"
    suscripcion.locationCode = "STK.US"
    suscripcion.scanCode = "TOP_PERC_GAIN"
    suscripcion.numberOfRows = 25
    escaner_resultados = IB_Instancia.reqScannerSubscription(reqId=1, subscription=suscripcion,
                                                             scannerSubscriptionOptions=[], scannerSubscriptionFilterOptions=[])
    print(escaner_resultados.iloc[:, :-1])    
    
    # Desconectarse del Servidor de IB
    IB_Instancia.disconnect(clear_logger=False)        
     