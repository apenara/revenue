#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para el cálculo de KPIs de Revenue Management
"""

import polars as pl
from datetime import datetime, timedelta
from utils.logger import setup_logger
from models.daily_occupancy import DailyOccupancy
from models.daily_revenue import DailyRevenue
from models.room import Room
from config import config

# Configurar logger
logger = setup_logger(__name__)

class KpiCalculator:
    """
    Clase para el cálculo de KPIs de Revenue Management
    """
    
    def __init__(self):
        """
        Inicializa la instancia de KpiCalculator
        """
        self.room_types = {room.id: room for room in Room.get_all()}
    
    def calculate_kpis(self, start_date, end_date, room_type_id=None):
        """
        Calcula los KPIs esenciales (RevPAR, ADR, Ocupación) para un rango de fechas
        y opcionalmente filtrado por tipo de habitación.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            pl.DataFrame: DataFrame con los KPIs calculados
        """
        try:
            logger.info(f"Calculando KPIs para el rango {start_date} - {end_date}")
            
            # Obtener datos de ocupación
            occupancy_data = DailyOccupancy.get_by_date_range(start_date, end_date, room_type_id)
            
            # Obtener datos de ingresos
            revenue_data = DailyRevenue.get_by_date_range(start_date, end_date, room_type_id)
            
            if not occupancy_data or not revenue_data:
                logger.warning("No hay datos suficientes para calcular KPIs")
                return pl.DataFrame()
            
            # Convertir a DataFrames de Polars
            occupancy_df = pl.DataFrame([occ.to_dict() for occ in occupancy_data])
            revenue_df = pl.DataFrame([rev.to_dict() for rev in revenue_data])
            
            # Unir los DataFrames por fecha y tipo de habitación
            df = occupancy_df.join(
                revenue_df,
                on=["fecha", "room_type_id"],
                how="inner"
            )
            
            # Agregar nombre del tipo de habitación
            df = df.with_column(
                pl.col("room_type_id").map_dict(
                    {room_id: room.nombre for room_id, room in self.room_types.items()},
                    default="Desconocido"
                ).alias("tipo_habitacion")
            )
            
            # Seleccionar y renombrar columnas relevantes
            kpi_df = df.select([
                "fecha",
                "room_type_id",
                "tipo_habitacion",
                "habitaciones_disponibles",
                "habitaciones_ocupadas",
                "ocupacion_porcentaje",
                "ingresos",
                "adr",
                "revpar"
            ])
            
            return kpi_df
            
        except Exception as e:
            logger.error(f"Error al calcular KPIs: {e}")
            return pl.DataFrame()
    
    def calculate_aggregated_kpis(self, start_date, end_date, group_by="room_type_id"):
        """
        Calcula KPIs agregados por tipo de habitación, fecha o ambos.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            group_by (str): Campo por el que agrupar ("room_type_id", "fecha", o "both")
            
        Returns:
            pl.DataFrame: DataFrame con los KPIs agregados
        """
        try:
            # Obtener KPIs detallados
            kpi_df = self.calculate_kpis(start_date, end_date)
            
            if kpi_df.is_empty():
                return pl.DataFrame()
            
            # Definir columnas de agrupación
            if group_by == "room_type_id":
                group_cols = ["room_type_id", "tipo_habitacion"]
            elif group_by == "fecha":
                group_cols = ["fecha"]
            elif group_by == "both":
                group_cols = ["fecha", "room_type_id", "tipo_habitacion"]
            else:
                group_cols = ["room_type_id", "tipo_habitacion"]
            
            # Agregar datos
            agg_df = kpi_df.group_by(group_cols).agg([
                pl.sum("habitaciones_disponibles").alias("habitaciones_disponibles"),
                pl.sum("habitaciones_ocupadas").alias("habitaciones_ocupadas"),
                pl.sum("ingresos").alias("ingresos"),
                (pl.sum("habitaciones_ocupadas") / pl.sum("habitaciones_disponibles") * 100).alias("ocupacion_porcentaje"),
                (pl.sum("ingresos") / pl.sum("habitaciones_ocupadas")).alias("adr"),
                (pl.sum("ingresos") / pl.sum("habitaciones_disponibles")).alias("revpar")
            ])
            
            return agg_df
            
        except Exception as e:
            logger.error(f"Error al calcular KPIs agregados: {e}")
            return pl.DataFrame()
    
    def analyze_occupancy_patterns(self, start_date, end_date, room_type_id=None):
        """
        Analiza patrones históricos de ocupación por tipo de habitación, temporada y día de la semana.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Diccionario con los diferentes análisis de patrones
        """
        try:
            logger.info(f"Analizando patrones de ocupación para el rango {start_date} - {end_date}")
            
            # Obtener KPIs detallados
            kpi_df = self.calculate_kpis(start_date, end_date, room_type_id)
            
            if kpi_df.is_empty():
                return {}
            
            # Convertir fecha a datetime y extraer información
            kpi_df = kpi_df.with_column(pl.col("fecha").str.to_datetime("%Y-%m-%d"))
            kpi_df = kpi_df.with_columns([
                pl.col("fecha").dt.weekday().alias("dia_semana"),
                pl.col("fecha").dt.month().alias("mes")
            ])
            
            # Obtener temporadas
            seasons = config.get_seasons()
            season_map = {}
            for season in seasons:
                for month in season.get("months", []):
                    season_map[month] = season["name"]
            
            # Asignar temporada
            kpi_df = kpi_df.with_column(
                pl.col("mes").map_dict(season_map, default="Desconocida").alias("temporada")
            )
            
            # Análisis por tipo de habitación
            room_type_analysis = kpi_df.group_by(["room_type_id", "tipo_habitacion"]).agg([
                pl.mean("ocupacion_porcentaje").alias("ocupacion_promedio"),
                pl.mean("adr").alias("adr_promedio"),
                pl.mean("revpar").alias("revpar_promedio")
            ]).sort("room_type_id")
            
            # Análisis por temporada
            season_analysis = kpi_df.group_by("temporada").agg([
                pl.mean("ocupacion_porcentaje").alias("ocupacion_promedio"),
                pl.mean("adr").alias("adr_promedio"),
                pl.mean("revpar").alias("revpar_promedio")
            ])
            
            # Análisis por día de la semana
            weekday_analysis = kpi_df.group_by("dia_semana").agg([
                pl.mean("ocupacion_porcentaje").alias("ocupacion_promedio"),
                pl.mean("adr").alias("adr_promedio"),
                pl.mean("revpar").alias("revpar_promedio")
            ]).sort("dia_semana")
            
            # Análisis por tipo de habitación y temporada
            room_season_analysis = kpi_df.group_by(["room_type_id", "tipo_habitacion", "temporada"]).agg([
                pl.mean("ocupacion_porcentaje").alias("ocupacion_promedio"),
                pl.mean("adr").alias("adr_promedio"),
                pl.mean("revpar").alias("revpar_promedio")
            ]).sort(["room_type_id", "temporada"])
            
            # Análisis por tipo de habitación y día de la semana
            room_weekday_analysis = kpi_df.group_by(["room_type_id", "tipo_habitacion", "dia_semana"]).agg([
                pl.mean("ocupacion_porcentaje").alias("ocupacion_promedio"),
                pl.mean("adr").alias("adr_promedio"),
                pl.mean("revpar").alias("revpar_promedio")
            ]).sort(["room_type_id", "dia_semana"])
            
            return {
                "por_tipo_habitacion": room_type_analysis,
                "por_temporada": season_analysis,
                "por_dia_semana": weekday_analysis,
                "por_tipo_y_temporada": room_season_analysis,
                "por_tipo_y_dia": room_weekday_analysis
            }
            
        except Exception as e:
            logger.error(f"Error al analizar patrones de ocupación: {e}")
            return {}
    
    def calculate_yoy_comparison(self, current_start_date, current_end_date, room_type_id=None):
        """
        Calcula comparaciones año contra año (YoY) para los KPIs esenciales.
        
        Args:
            current_start_date (str/datetime): Fecha de inicio del período actual
            current_end_date (str/datetime): Fecha de fin del período actual
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Diccionario con las comparaciones YoY
        """
        try:
            logger.info(f"Calculando comparación YoY para el rango {current_start_date} - {current_end_date}")
            
            # Convertir fechas a datetime si son strings
            if isinstance(current_start_date, str):
                current_start_date = datetime.strptime(current_start_date, '%Y-%m-%d')
            if isinstance(current_end_date, str):
                current_end_date = datetime.strptime(current_end_date, '%Y-%m-%d')
            
            # Calcular fechas del año anterior
            previous_start_date = current_start_date - timedelta(days=365)
            previous_end_date = current_end_date - timedelta(days=365)
            
            # Obtener KPIs del período actual
            current_kpis = self.calculate_aggregated_kpis(current_start_date, current_end_date, "room_type_id")
            
            # Obtener KPIs del período anterior
            previous_kpis = self.calculate_aggregated_kpis(previous_start_date, previous_end_date, "room_type_id")
            
            if current_kpis.is_empty() or previous_kpis.is_empty():
                return {}
            
            # Filtrar por tipo de habitación si se especifica
            if room_type_id is not None:
                current_kpis = current_kpis.filter(pl.col("room_type_id") == room_type_id)
                previous_kpis = previous_kpis.filter(pl.col("room_type_id") == room_type_id)
            
            # Renombrar columnas del período anterior
            previous_kpis = previous_kpis.rename({
                "ocupacion_porcentaje": "ocupacion_anterior",
                "adr": "adr_anterior",
                "revpar": "revpar_anterior",
                "ingresos": "ingresos_anterior",
                "habitaciones_ocupadas": "habitaciones_ocupadas_anterior",
                "habitaciones_disponibles": "habitaciones_disponibles_anterior"
            })
            
            # Unir los DataFrames
            yoy_df = current_kpis.join(
                previous_kpis,
                on=["room_type_id", "tipo_habitacion"],
                how="left"
            )
            
            # Calcular variaciones
            yoy_df = yoy_df.with_columns([
                ((pl.col("ocupacion_porcentaje") - pl.col("ocupacion_anterior")) / pl.col("ocupacion_anterior") * 100).alias("var_ocupacion"),
                ((pl.col("adr") - pl.col("adr_anterior")) / pl.col("adr_anterior") * 100).alias("var_adr"),
                ((pl.col("revpar") - pl.col("revpar_anterior")) / pl.col("revpar_anterior") * 100).alias("var_revpar"),
                ((pl.col("ingresos") - pl.col("ingresos_anterior")) / pl.col("ingresos_anterior") * 100).alias("var_ingresos")
            ])
            
            # Seleccionar columnas relevantes
            result_df = yoy_df.select([
                "room_type_id",
                "tipo_habitacion",
                "ocupacion_porcentaje",
                "ocupacion_anterior",
                "var_ocupacion",
                "adr",
                "adr_anterior",
                "var_adr",
                "revpar",
                "revpar_anterior",
                "var_revpar",
                "ingresos",
                "ingresos_anterior",
                "var_ingresos"
            ])
            
            return {
                "comparacion_yoy": result_df,
                "periodo_actual": f"{current_start_date.strftime('%Y-%m-%d')} a {current_end_date.strftime('%Y-%m-%d')}",
                "periodo_anterior": f"{previous_start_date.strftime('%Y-%m-%d')} a {previous_end_date.strftime('%Y-%m-%d')}"
            }
            
        except Exception as e:
            logger.error(f"Error al calcular comparación YoY: {e}")
            return {}