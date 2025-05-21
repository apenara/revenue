#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para limpiar y normalizar los datos
"""

import polars as pl
from datetime import datetime
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class DataCleaner:
    """
    Clase para limpiar y normalizar los datos
    """
    
    @staticmethod
    def clean_dates(df, date_columns):
        """
        Limpia y normaliza las columnas de fechas.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            date_columns (list): Lista de nombres de columnas de fechas a limpiar
            
        Returns:
            pl.DataFrame: DataFrame con las fechas normalizadas
        """
        try:
            logger.info(f"Limpiando columnas de fechas: {date_columns}")
            
            for col in date_columns:
                if col in df.columns:
                    # Convertir a tipo Date
                    df = df.with_columns([
                        pl.col(col).str.strptime(pl.Date, format=None, strict=False).alias(col)
                    ])
                    
                    logger.info(f"Columna {col} convertida a tipo Date")
                else:
                    logger.warning(f"La columna {col} no existe en el DataFrame")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al limpiar las columnas de fechas: {e}")
            return df
    
    @staticmethod
    def clean_numeric(df, numeric_columns, dtype=pl.Float64):
        """
        Limpia y normaliza las columnas numéricas.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            numeric_columns (list): Lista de nombres de columnas numéricas a limpiar
            dtype (pl.DataType, optional): Tipo de datos a convertir (por defecto pl.Float64)
            
        Returns:
            pl.DataFrame: DataFrame con las columnas numéricas normalizadas
        """
        try:
            logger.info(f"Limpiando columnas numéricas: {numeric_columns}")
            
            for col in numeric_columns:
                if col in df.columns:
                    # Convertir a tipo numérico
                    df = df.with_columns([
                        pl.col(col).cast(dtype).alias(col)
                    ])
                    
                    logger.info(f"Columna {col} convertida a tipo {dtype}")
                else:
                    logger.warning(f"La columna {col} no existe en el DataFrame")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al limpiar las columnas numéricas: {e}")
            return df
    
    @staticmethod
    def clean_text(df, text_columns):
        """
        Limpia y normaliza las columnas de texto.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            text_columns (list): Lista de nombres de columnas de texto a limpiar
            
        Returns:
            pl.DataFrame: DataFrame con las columnas de texto normalizadas
        """
        try:
            logger.info(f"Limpiando columnas de texto: {text_columns}")
            
            for col in text_columns:
                if col in df.columns:
                    # Limpiar texto: eliminar espacios en blanco, convertir a minúsculas
                    df = df.with_columns([
                        pl.col(col).str.strip().str.to_lowercase().alias(col)
                    ])
                    
                    logger.info(f"Columna {col} limpiada")
                else:
                    logger.warning(f"La columna {col} no existe en el DataFrame")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al limpiar las columnas de texto: {e}")
            return df
    
    @staticmethod
    def standardize_categories(df, category_columns, mapping=None):
        """
        Estandariza las categorías en las columnas especificadas.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            category_columns (list): Lista de nombres de columnas de categorías a estandarizar
            mapping (dict, optional): Diccionario con los mapeos de categorías {columna: {valor_original: valor_estandarizado}}
            
        Returns:
            pl.DataFrame: DataFrame con las categorías estandarizadas
        """
        try:
            logger.info(f"Estandarizando categorías en columnas: {category_columns}")
            
            if mapping is None:
                mapping = {}
            
            for col in category_columns:
                if col in df.columns:
                    if col in mapping:
                        # Aplicar mapeo personalizado
                        col_mapping = mapping[col]
                        
                        # Crear una expresión when-then-otherwise para el mapeo
                        when_expr = None
                        for original, standardized in col_mapping.items():
                            if when_expr is None:
                                when_expr = pl.when(pl.col(col) == original).then(pl.lit(standardized))
                            else:
                                when_expr = when_expr.when(pl.col(col) == original).then(pl.lit(standardized))
                        
                        # Aplicar la expresión
                        if when_expr is not None:
                            df = df.with_columns([
                                when_expr.otherwise(pl.col(col)).alias(col)
                            ])
                        
                        logger.info(f"Categorías en columna {col} estandarizadas según mapeo personalizado")
                    else:
                        # Limpiar y estandarizar sin mapeo específico
                        df = df.with_columns([
                            pl.col(col).str.strip().str.to_lowercase().alias(col)
                        ])
                        
                        logger.info(f"Categorías en columna {col} estandarizadas (limpieza básica)")
                else:
                    logger.warning(f"La columna {col} no existe en el DataFrame")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al estandarizar categorías: {e}")
            return df
    
    @staticmethod
    def handle_missing_values(df, strategy="drop", fill_values=None):
        """
        Maneja los valores faltantes en el DataFrame.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            strategy (str, optional): Estrategia para manejar valores faltantes:
                - "drop": Eliminar filas con valores faltantes
                - "fill": Rellenar valores faltantes según fill_values
            fill_values (dict, optional): Diccionario con los valores de relleno {columna: valor}
            
        Returns:
            pl.DataFrame: DataFrame con los valores faltantes manejados
        """
        try:
            logger.info(f"Manejando valores faltantes con estrategia: {strategy}")
            
            if strategy == "drop":
                # Contar filas antes
                rows_before = df.shape[0]
                
                # Eliminar filas con valores faltantes
                df = df.drop_nulls()
                
                # Contar filas después
                rows_after = df.shape[0]
                rows_dropped = rows_before - rows_after
                
                logger.info(f"Se eliminaron {rows_dropped} filas con valores faltantes")
                
            elif strategy == "fill":
                if fill_values is None:
                    fill_values = {}
                
                # Rellenar valores faltantes según fill_values
                for col, value in fill_values.items():
                    if col in df.columns:
                        df = df.with_columns([
                            pl.col(col).fill_null(value).alias(col)
                        ])
                        
                        logger.info(f"Valores faltantes en columna {col} rellenados con {value}")
                    else:
                        logger.warning(f"La columna {col} no existe en el DataFrame")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al manejar valores faltantes: {e}")
            return df
    
    @staticmethod
    def expand_date_range(df, date_from_col, date_to_col, id_cols=None):
        """
        Expande un DataFrame con rangos de fechas a un DataFrame con una fila por cada fecha.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            date_from_col (str): Nombre de la columna con la fecha de inicio
            date_to_col (str): Nombre de la columna con la fecha de fin
            id_cols (list, optional): Lista de columnas de identificación a mantener
            
        Returns:
            pl.DataFrame: DataFrame expandido con una fila por cada fecha
        """
        try:
            logger.info(f"Expandiendo rangos de fechas de {date_from_col} a {date_to_col}")
            
            if id_cols is None:
                id_cols = []
            
            # Convertir a pandas para usar funciones de expansión de fechas
            df_pandas = df.to_pandas()
            
            # Asegurarse de que las columnas de fechas son de tipo datetime
            df_pandas[date_from_col] = pd.to_datetime(df_pandas[date_from_col])
            df_pandas[date_to_col] = pd.to_datetime(df_pandas[date_to_col])
            
            # Crear lista para almacenar filas expandidas
            expanded_rows = []
            
            # Para cada fila en el DataFrame original
            for _, row in df_pandas.iterrows():
                # Obtener rango de fechas
                date_range = pd.date_range(start=row[date_from_col], end=row[date_to_col])
                
                # Para cada fecha en el rango
                for date in date_range:
                    # Crear nueva fila
                    new_row = row.copy()
                    new_row['fecha'] = date.date()  # Agregar columna de fecha
                    
                    # Agregar a la lista de filas expandidas
                    expanded_rows.append(new_row)
            
            # Crear nuevo DataFrame con las filas expandidas
            expanded_df = pd.DataFrame(expanded_rows)
            
            # Convertir de nuevo a Polars
            result_df = pl.from_pandas(expanded_df)
            
            logger.info(f"DataFrame expandido de {df.shape[0]} filas a {result_df.shape[0]} filas")
            return result_df
            
        except Exception as e:
            logger.error(f"Error al expandir rangos de fechas: {e}")
            return df
    
    @staticmethod
    def calculate_nights(df, check_in_col, check_out_col, nights_col="noches"):
        """
        Calcula el número de noches entre dos fechas.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            check_in_col (str): Nombre de la columna con la fecha de check-in
            check_out_col (str): Nombre de la columna con la fecha de check-out
            nights_col (str, optional): Nombre de la columna para almacenar el número de noches
            
        Returns:
            pl.DataFrame: DataFrame con la columna de noches calculada
        """
        try:
            logger.info(f"Calculando noches entre {check_in_col} y {check_out_col}")
            
            # Calcular la diferencia en días entre las fechas
            df = df.with_columns([
                (pl.col(check_out_col) - pl.col(check_in_col)).dt.days().alias(nights_col)
            ])
            
            logger.info(f"Columna {nights_col} calculada")
            return df
            
        except Exception as e:
            logger.error(f"Error al calcular noches: {e}")
            return df
    
    @staticmethod
    def calculate_rate_per_night(df, total_rate_col, nights_col, rate_per_night_col="tarifa_por_noche"):
        """
        Calcula la tarifa por noche dividiendo la tarifa total entre el número de noches.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            total_rate_col (str): Nombre de la columna con la tarifa total
            nights_col (str): Nombre de la columna con el número de noches
            rate_per_night_col (str, optional): Nombre de la columna para almacenar la tarifa por noche
            
        Returns:
            pl.DataFrame: DataFrame con la columna de tarifa por noche calculada
        """
        try:
            logger.info(f"Calculando tarifa por noche: {total_rate_col} / {nights_col}")
            
            # Calcular la tarifa por noche
            df = df.with_columns([
                (pl.col(total_rate_col) / pl.col(nights_col)).alias(rate_per_night_col)
            ])
            
            logger.info(f"Columna {rate_per_night_col} calculada")
            return df
            
        except Exception as e:
            logger.error(f"Error al calcular tarifa por noche: {e}")
            return df
    
    @staticmethod
    def expand_stays(df, check_in_col, check_out_col, id_cols=None, rate_col=None):
        """
        Expande las estancias para generar una fila por cada noche.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            check_in_col (str): Nombre de la columna con la fecha de check-in
            check_out_col (str): Nombre de la columna con la fecha de check-out
            id_cols (list, optional): Lista de columnas de identificación a mantener
            rate_col (str, optional): Nombre de la columna con la tarifa total para distribuir por noche
            
        Returns:
            pl.DataFrame: DataFrame expandido con una fila por cada noche
        """
        try:
            logger.info(f"Expandiendo estancias de {check_in_col} a {check_out_col}")
            
            if id_cols is None:
                id_cols = []
            
            # Calcular noches si no existe la columna
            if 'noches' not in df.columns:
                df = DataCleaner.calculate_nights(df, check_in_col, check_out_col)
            
            # Calcular tarifa por noche si se proporciona la columna de tarifa
            if rate_col is not None and 'tarifa_por_noche' not in df.columns:
                df = DataCleaner.calculate_rate_per_night(df, rate_col, 'noches')
            
            # Expandir por fecha
            expanded_df = DataCleaner.expand_date_range(df, check_in_col, check_out_col, id_cols)
            
            logger.info(f"Estancias expandidas de {df.shape[0]} filas a {expanded_df.shape[0]} filas")
            return expanded_df
            
        except Exception as e:
            logger.error(f"Error al expandir estancias: {e}")
            return df

# Importar pandas para la función expand_date_range
import pandas as pd