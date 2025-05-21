#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para la previsión de demanda utilizando Prophet
"""

import polars as pl
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
from utils.logger import setup_logger
from models.forecast import Forecast
from models.daily_occupancy import DailyOccupancy
from models.room import Room
from config import config

# Configurar logger
logger = setup_logger(__name__)

class ForecastService:
    """
    Clase para la generación de pronósticos de ocupación utilizando Prophet
    """
    
    def __init__(self):
        """
        Inicializa la instancia de ForecastService
        """
        self.forecast_config = config.get_forecasting_config()
        self.room_types = {room.id: room for room in Room.get_all()}
    
    def prepare_data(self, start_date, end_date, room_type_id=None):
        """
        Prepara los datos para el modelo de previsión.
        
        Args:
            start_date (str/datetime): Fecha de inicio del histórico
            end_date (str/datetime): Fecha de fin del histórico
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Diccionario con DataFrames preparados por tipo de habitación
        """
        try:
            logger.info(f"Preparando datos para previsión del rango {start_date} - {end_date}")
            
            # Obtener datos de ocupación
            occupancy_data = DailyOccupancy.get_by_date_range(start_date, end_date, room_type_id)
            
            if not occupancy_data:
                logger.warning("No hay datos suficientes para preparar la previsión")
                return {}
            
            # Convertir a DataFrame de Polars
            df = pl.DataFrame([occ.to_dict() for occ in occupancy_data])
            
            # Agrupar por tipo de habitación y fecha
            prepared_data = {}
            
            # Si se especifica un tipo de habitación, filtrar
            if room_type_id is not None:
                room_types_to_process = [room_type_id]
            else:
                room_types_to_process = list(self.room_types.keys())
            
            for rt_id in room_types_to_process:
                # Filtrar por tipo de habitación
                rt_df = df.filter(pl.col("room_type_id") == rt_id)
                
                if rt_df.is_empty():
                    continue
                
                # Calcular tasa de ocupación
                rt_df = rt_df.with_column(
                    (pl.col("habitaciones_ocupadas") / pl.col("habitaciones_disponibles")).alias("ocupacion_ratio")
                )
                
                # Seleccionar columnas necesarias para Prophet
                prophet_df = rt_df.select([
                    pl.col("fecha").alias("ds"),
                    pl.col("ocupacion_ratio").alias("y")
                ])
                
                # Convertir a pandas para Prophet
                prophet_df_pd = prophet_df.to_pandas()
                
                # Asegurar que la fecha esté en formato datetime
                prophet_df_pd["ds"] = pd.to_datetime(prophet_df_pd["ds"])
                
                # Ordenar por fecha
                prophet_df_pd = prophet_df_pd.sort_values("ds")
                
                # Guardar en el diccionario
                prepared_data[rt_id] = {
                    "prophet_df": prophet_df_pd,
                    "room_type": self.room_types[rt_id]
                }
            
            return prepared_data
            
        except Exception as e:
            logger.error(f"Error al preparar datos para previsión: {e}")
            return {}
    
    def generate_forecast(self, start_date, end_date, forecast_days=None, room_type_id=None):
        """
        Genera pronósticos de ocupación utilizando Prophet.
        
        Args:
            start_date (str/datetime): Fecha de inicio del histórico
            end_date (str/datetime): Fecha de fin del histórico
            forecast_days (int, optional): Número de días a pronosticar
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Diccionario con los pronósticos por tipo de habitación
        """
        try:
            logger.info(f"Generando pronóstico para el rango {start_date} - {end_date}")
            
            # Obtener días de pronóstico de la configuración si no se especifica
            if forecast_days is None:
                forecast_days = self.forecast_config.get("forecast_days", 90)
            
            # Preparar datos
            prepared_data = self.prepare_data(start_date, end_date, room_type_id)
            
            if not prepared_data:
                return {}
            
            forecasts = {}
            
            for rt_id, data in prepared_data.items():
                prophet_df = data["prophet_df"]
                room_type = data["room_type"]
                
                logger.info(f"Generando pronóstico para {room_type.nombre} (ID: {rt_id})")
                
                # Crear modelo Prophet con parámetros de configuración
                model = Prophet(
                    seasonality_mode=self.forecast_config.get("seasonality_mode", "multiplicative"),
                    changepoint_prior_scale=self.forecast_config.get("changepoint_prior_scale", 0.05),
                    seasonality_prior_scale=self.forecast_config.get("seasonality_prior_scale", 10.0)
                )
                
                # Configurar estacionalidades
                if self.forecast_config.get("weekly_seasonality", True):
                    model.add_seasonality(name='weekly', period=7, fourier_order=3)
                
                if self.forecast_config.get("yearly_seasonality", True):
                    model.add_seasonality(name='yearly', period=365.25, fourier_order=10)
                
                # Ajustar modelo
                model.fit(prophet_df)
                
                # Crear DataFrame para pronóstico
                future = model.make_future_dataframe(periods=forecast_days)
                
                # Generar pronóstico
                forecast = model.predict(future)
                
                # Seleccionar solo las fechas futuras
                last_date = prophet_df["ds"].max()
                future_forecast = forecast[forecast["ds"] > last_date]
                
                # Limitar valores entre 0 y 1
                future_forecast["yhat"] = future_forecast["yhat"].clip(0, 1)
                future_forecast["yhat_lower"] = future_forecast["yhat_lower"].clip(0, 1)
                future_forecast["yhat_upper"] = future_forecast["yhat_upper"].clip(0, 1)
                
                # Guardar en el diccionario
                forecasts[rt_id] = {
                    "room_type": room_type,
                    "forecast": future_forecast,
                    "model": model
                }
            
            return forecasts
            
        except Exception as e:
            logger.error(f"Error al generar pronóstico: {e}")
            return {}
    
    def save_forecast_to_db(self, forecasts):
        """
        Guarda los pronósticos en la base de datos.
        
        Args:
            forecasts (dict): Diccionario con los pronósticos por tipo de habitación
            
        Returns:
            tuple: (éxito, mensaje, filas_guardadas)
        """
        try:
            if not forecasts:
                return (False, "No hay pronósticos para guardar", 0)
            
            forecast_objects = []
            
            for rt_id, data in forecasts.items():
                room_type = data["room_type"]
                forecast_df = data["forecast"]
                
                # Convertir a lista de objetos Forecast
                for _, row in forecast_df.iterrows():
                    fecha = row["ds"].strftime("%Y-%m-%d")
                    ocupacion_prevista = float(row["yhat"]) * 100  # Convertir a porcentaje
                    
                    # Verificar si ya existe un pronóstico para esta fecha y tipo de habitación
                    existing_forecast = Forecast.get_by_date_and_room_type(fecha, rt_id)
                    
                    if existing_forecast:
                        # Actualizar pronóstico existente
                        existing_forecast.ocupacion_prevista = ocupacion_prevista
                        existing_forecast.save()
                        forecast_objects.append(existing_forecast)
                    else:
                        # Crear nuevo pronóstico
                        forecast = Forecast(
                            fecha=fecha,
                            room_type_id=rt_id,
                            ocupacion_prevista=ocupacion_prevista,
                            adr_previsto=0,  # Se actualizará posteriormente
                            revpar_previsto=0  # Se actualizará posteriormente
                        )
                        forecast.save()
                        forecast_objects.append(forecast)
            
            return (True, f"Se guardaron {len(forecast_objects)} pronósticos", len(forecast_objects))
            
        except Exception as e:
            logger.error(f"Error al guardar pronósticos en la base de datos: {e}")
            return (False, f"Error: {e}", 0)
    
    def load_forecast_from_db(self, start_date, end_date, room_type_id=None):
        """
        Carga pronósticos desde la base de datos.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            pl.DataFrame: DataFrame con los pronósticos cargados
        """
        try:
            logger.info(f"Cargando pronósticos para el rango {start_date} - {end_date}")
            
            # Obtener pronósticos
            forecast_data = Forecast.get_by_date_range(start_date, end_date, room_type_id)
            
            if not forecast_data:
                logger.warning("No hay pronósticos disponibles para el rango especificado")
                return pl.DataFrame()
            
            # Convertir a DataFrame de Polars
            df = pl.DataFrame([forecast.to_dict() for forecast in forecast_data])
            
            # Agregar nombre del tipo de habitación
            df = df.with_column(
                pl.col("room_type_id").map_dict(
                    {room_id: room.nombre for room_id, room in self.room_types.items()},
                    default="Desconocido"
                ).alias("tipo_habitacion")
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error al cargar pronósticos desde la base de datos: {e}")
            return pl.DataFrame()
    
    def update_forecast_kpis(self, start_date, end_date, room_type_id=None):
        """
        Actualiza los KPIs (ADR, RevPAR) de los pronósticos existentes.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            tuple: (éxito, mensaje, filas_actualizadas)
        """
        try:
            logger.info(f"Actualizando KPIs de pronósticos para el rango {start_date} - {end_date}")
            
            # Cargar pronósticos
            forecasts = Forecast.get_by_date_range(start_date, end_date, room_type_id)
            
            if not forecasts:
                return (False, "No hay pronósticos para actualizar", 0)
            
            # Obtener datos históricos de ADR y RevPAR
            from services.analysis.kpi_calculator import KpiCalculator
            kpi_calculator = KpiCalculator()
            
            # Calcular fecha de inicio para datos históricos (1 año antes)
            if isinstance(start_date, str):
                hist_start = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=365)
            else:
                hist_start = start_date - timedelta(days=365)
                
            if isinstance(end_date, str):
                hist_end = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365)
            else:
                hist_end = end_date - timedelta(days=365)
            
            # Obtener KPIs históricos
            historical_kpis = kpi_calculator.calculate_kpis(hist_start, hist_end, room_type_id)
            
            if historical_kpis.is_empty():
                return (False, "No hay datos históricos para calcular KPIs", 0)
            
            # Calcular promedios por tipo de habitación
            avg_kpis = historical_kpis.group_by("room_type_id").agg([
                pl.mean("adr").alias("adr_promedio"),
                pl.mean("revpar").alias("revpar_promedio")
            ])
            
            # Convertir a diccionario para fácil acceso
            avg_kpis_dict = {}
            for row in avg_kpis.to_dicts():
                avg_kpis_dict[row["room_type_id"]] = {
                    "adr_promedio": row["adr_promedio"],
                    "revpar_promedio": row["revpar_promedio"]
                }
            
            # Actualizar pronósticos
            updated_count = 0
            
            for forecast in forecasts:
                rt_id = forecast.room_type_id
                
                if rt_id in avg_kpis_dict:
                    # Obtener valores promedio
                    adr_promedio = avg_kpis_dict[rt_id]["adr_promedio"]
                    revpar_promedio = avg_kpis_dict[rt_id]["revpar_promedio"]
                    
                    # Calcular ADR y RevPAR previstos basados en la ocupación prevista
                    # Asumimos que el ADR se mantiene similar al histórico
                    forecast.adr_previsto = adr_promedio
                    
                    # El RevPAR se ajusta según la ocupación prevista
                    ocupacion_ratio = forecast.ocupacion_prevista / 100
                    forecast.revpar_previsto = adr_promedio * ocupacion_ratio
                    
                    # Guardar cambios
                    forecast.save()
                    updated_count += 1
            
            return (True, f"Se actualizaron KPIs de {updated_count} pronósticos", updated_count)
            
        except Exception as e:
            logger.error(f"Error al actualizar KPIs de pronósticos: {e}")
            return (False, f"Error: {e}", 0)