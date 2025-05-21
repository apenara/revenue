#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para leer archivos Excel y convertirlos a DataFrames de Polars
"""

import os
import polars as pl
from pathlib import Path
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class ExcelReader:
    """
    Clase para leer archivos Excel y convertirlos a DataFrames de Polars
    """
    
    @staticmethod
    def read_excel(file_path, sheet_name=None, sheet_index=0, has_header=True):
        """
        Lee un archivo Excel y lo convierte a un DataFrame de Polars.
        
        Args:
            file_path (str): Ruta al archivo Excel
            sheet_name (str, optional): Nombre de la hoja a leer
            sheet_index (int, optional): Índice de la hoja a leer (por defecto 0)
            has_header (bool, optional): Indica si el archivo tiene encabezado (por defecto True)
            
        Returns:
            pl.DataFrame: DataFrame de Polars con los datos del archivo Excel
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"El archivo {file_path} no existe")
                return None
            
            logger.info(f"Leyendo archivo Excel: {file_path}")
            
            # Leer el archivo Excel con pandas y convertirlo a Polars
            # Polars no tiene soporte nativo para Excel, así que usamos pandas como intermediario
            import pandas as pd
            
            if sheet_name:
                df_pandas = pd.read_excel(
                    file_path, 
                    sheet_name=sheet_name, 
                    header=0 if has_header else None
                )
            else:
                df_pandas = pd.read_excel(
                    file_path, 
                    sheet_name=sheet_index, 
                    header=0 if has_header else None
                )
            
            # Convertir a Polars
            df_polars = pl.from_pandas(df_pandas)
            
            logger.info(f"Archivo Excel leído exitosamente: {df_polars.shape[0]} filas, {df_polars.shape[1]} columnas")
            return df_polars
            
        except Exception as e:
            logger.error(f"Error al leer el archivo Excel {file_path}: {e}")
            return None
    
    @staticmethod
    def read_excel_sheets(file_path, sheet_names=None, has_header=True):
        """
        Lee múltiples hojas de un archivo Excel y las convierte a DataFrames de Polars.
        
        Args:
            file_path (str): Ruta al archivo Excel
            sheet_names (list, optional): Lista de nombres de hojas a leer. Si es None, lee todas las hojas.
            has_header (bool, optional): Indica si el archivo tiene encabezado (por defecto True)
            
        Returns:
            dict: Diccionario con los nombres de las hojas como claves y los DataFrames de Polars como valores
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"El archivo {file_path} no existe")
                return {}
            
            logger.info(f"Leyendo hojas de Excel: {file_path}")
            
            # Leer el archivo Excel con pandas y convertirlo a Polars
            import pandas as pd
            
            # Leer todas las hojas
            excel_file = pd.ExcelFile(file_path)
            
            # Si no se especifican hojas, leer todas
            if sheet_names is None:
                sheet_names = excel_file.sheet_names
            
            # Diccionario para almacenar los DataFrames
            dfs = {}
            
            # Leer cada hoja
            for sheet_name in sheet_names:
                if sheet_name in excel_file.sheet_names:
                    df_pandas = pd.read_excel(
                        excel_file, 
                        sheet_name=sheet_name, 
                        header=0 if has_header else None
                    )
                    
                    # Convertir a Polars
                    df_polars = pl.from_pandas(df_pandas)
                    
                    dfs[sheet_name] = df_polars
                    logger.info(f"Hoja '{sheet_name}' leída exitosamente: {df_polars.shape[0]} filas, {df_polars.shape[1]} columnas")
                else:
                    logger.warning(f"La hoja '{sheet_name}' no existe en el archivo {file_path}")
            
            return dfs
            
        except Exception as e:
            logger.error(f"Error al leer las hojas del archivo Excel {file_path}: {e}")
            return {}
    
    @staticmethod
    def get_sheet_names(file_path):
        """
        Obtiene los nombres de las hojas de un archivo Excel.
        
        Args:
            file_path (str): Ruta al archivo Excel
            
        Returns:
            list: Lista con los nombres de las hojas
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"El archivo {file_path} no existe")
                return []
            
            # Obtener los nombres de las hojas con pandas
            import pandas as pd
            
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            logger.info(f"Hojas encontradas en {file_path}: {sheet_names}")
            return sheet_names
            
        except Exception as e:
            logger.error(f"Error al obtener los nombres de las hojas del archivo Excel {file_path}: {e}")
            return []
    
    @staticmethod
    def save_to_excel(df, file_path, sheet_name="Sheet1"):
        """
        Guarda un DataFrame de Polars en un archivo Excel.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars a guardar
            file_path (str): Ruta donde guardar el archivo Excel
            sheet_name (str, optional): Nombre de la hoja (por defecto "Sheet1")
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            file_path = Path(file_path)
            
            # Crear directorio si no existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Guardando DataFrame en Excel: {file_path}")
            
            # Convertir a pandas y guardar
            df_pandas = df.to_pandas()
            
            # Guardar en Excel
            df_pandas.to_excel(file_path, sheet_name=sheet_name, index=False)
            
            logger.info(f"DataFrame guardado exitosamente en {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar el DataFrame en Excel {file_path}: {e}")
            return False
    
    @staticmethod
    def save_multiple_to_excel(dfs, file_path):
        """
        Guarda múltiples DataFrames de Polars en un archivo Excel, cada uno en una hoja diferente.
        
        Args:
            dfs (dict): Diccionario con los nombres de las hojas como claves y los DataFrames de Polars como valores
            file_path (str): Ruta donde guardar el archivo Excel
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            file_path = Path(file_path)
            
            # Crear directorio si no existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Guardando múltiples DataFrames en Excel: {file_path}")
            
            # Crear un ExcelWriter
            import pandas as pd
            
            with pd.ExcelWriter(file_path) as writer:
                for sheet_name, df in dfs.items():
                    # Convertir a pandas y guardar
                    df_pandas = df.to_pandas()
                    df_pandas.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"DataFrames guardados exitosamente en {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar los DataFrames en Excel {file_path}: {e}")
            return False