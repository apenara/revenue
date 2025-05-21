#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para la aplicación de reglas de pricing
"""

import polars as pl
from datetime import datetime, timedelta
from utils.logger import setup_logger
from models.rule import Rule
from models.forecast import Forecast
from models.room import Room
from models.recommendation import ApprovedRecommendation
from config import config

# Configurar logger
logger = setup_logger(__name__)

class PricingRuleEngine:
    """
    Clase para la aplicación de reglas de pricing utilizando Polars
    """
    
    def __init__(self):
        """
        Inicializa la instancia de PricingRuleEngine
        """
        self.pricing_config = config.get_pricing_rules()
        self.room_types = {room.id: room for room in Room.get_all()}
        self.channels = config.get_channels()
        self.seasons = config.get_seasons()
        self.rules = self._load_rules()
    
    def _load_rules(self):
        """
        Carga las reglas de pricing desde la base de datos.
        
        Returns:
            list: Lista de reglas activas
        """
        try:
            # Obtener reglas activas
            rules = Rule.get_active_rules()
            
            if not rules:
                logger.warning("No hay reglas de pricing activas")
                
                # Crear reglas por defecto si no hay reglas
                self._create_default_rules()
                rules = Rule.get_active_rules()
            
            return rules
            
        except Exception as e:
            logger.error(f"Error al cargar reglas de pricing: {e}")
            return []
    
    def _create_default_rules(self):
        """
        Crea reglas de pricing por defecto.
        """
        try:
            logger.info("Creando reglas de pricing por defecto")
            
            # Regla de temporada
            season_rule = Rule(
                nombre="Regla de Temporada",
                descripcion="Ajusta tarifas según la temporada",
                parametros={
                    "tipo": "temporada",
                    "factores": {
                        "Baja": 0.9,
                        "Media": 1.0,
                        "Alta": 1.2
                    }
                },
                prioridad=1,
                activa=True
            )
            season_rule.save()
            
            # Regla de ocupación
            occupancy_rule = Rule(
                nombre="Regla de Ocupación",
                descripcion="Ajusta tarifas según la ocupación prevista",
                parametros={
                    "tipo": "ocupacion",
                    "umbrales": {
                        "bajo": self.pricing_config.get("min_occupancy_threshold", 0.4),
                        "alto": self.pricing_config.get("max_occupancy_threshold", 0.8)
                    },
                    "factores": {
                        "bajo": self.pricing_config.get("low_occupancy_factor", 0.9),
                        "medio": 1.0,
                        "alto": self.pricing_config.get("high_occupancy_factor", 1.15)
                    }
                },
                prioridad=2,
                activa=True
            )
            occupancy_rule.save()
            
            # Regla de canal
            channel_rule = Rule(
                nombre="Regla de Canal",
                descripcion="Ajusta tarifas según el canal de distribución",
                parametros={
                    "tipo": "canal",
                    "factores": {factor_dict for factor_dict in [
                        {"canal": channel["name"], "factor": 1 + channel["commission"]}
                        for channel in self.channels
                    ]}
                },
                prioridad=3,
                activa=True
            )
            channel_rule.save()
            
            # Regla de día de la semana
            weekday_rule = Rule(
                nombre="Regla de Día de Semana",
                descripcion="Ajusta tarifas según el día de la semana",
                parametros={
                    "tipo": "dia_semana",
                    "factores": {
                        "0": 0.9,  # Lunes
                        "1": 0.9,  # Martes
                        "2": 0.9,  # Miércoles
                        "3": 0.95, # Jueves
                        "4": 1.1,  # Viernes
                        "5": 1.2,  # Sábado
                        "6": 1.0   # Domingo
                    }
                },
                prioridad=4,
                activa=True
            )
            weekday_rule.save()
            
            logger.info("Reglas de pricing por defecto creadas correctamente")
            
        except Exception as e:
            logger.error(f"Error al crear reglas de pricing por defecto: {e}")
    
    def reload_rules(self):
        """
        Recarga las reglas de pricing desde la base de datos.
        
        Returns:
            bool: True si se recargaron correctamente, False en caso contrario
        """
        try:
            self.rules = self._load_rules()
            return True
        except Exception as e:
            logger.error(f"Error al recargar reglas de pricing: {e}")
            return False
    
    def apply_rules(self, start_date, end_date, room_type_id=None):
        """
        Aplica las reglas de pricing para generar recomendaciones de tarifas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            pl.DataFrame: DataFrame con las recomendaciones de tarifas
        """
        try:
            logger.info(f"Aplicando reglas de pricing para el rango {start_date} - {end_date}")
            
            # Cargar pronósticos
            forecasts = Forecast.get_by_date_range(start_date, end_date, room_type_id)
            
            if not forecasts:
                logger.warning("No hay pronósticos disponibles para aplicar reglas de pricing")
                return pl.DataFrame()
            
            # Convertir a DataFrame de Polars
            forecast_df = pl.DataFrame([forecast.to_dict() for forecast in forecasts])
            
            # Preparar datos para aplicar reglas
            df = self._prepare_data_for_rules(forecast_df)
            
            if df.is_empty():
                return pl.DataFrame()
            
            # Aplicar reglas
            for rule in sorted(self.rules, key=lambda r: r.prioridad):
                df = self._apply_rule(df, rule)
            
            # Calcular tarifas finales
            df = self._calculate_final_rates(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error al aplicar reglas de pricing: {e}")
            return pl.DataFrame()
    
    def _prepare_data_for_rules(self, forecast_df):
        """
        Prepara los datos para aplicar las reglas de pricing.
        
        Args:
            forecast_df (pl.DataFrame): DataFrame con los pronósticos
            
        Returns:
            pl.DataFrame: DataFrame preparado para aplicar reglas
        """
        try:
            if forecast_df.is_empty():
                return pl.DataFrame()
            
            # Convertir fecha a datetime
            df = forecast_df.with_column(pl.col("fecha").str.to_datetime("%Y-%m-%d"))
            
            # Extraer información de la fecha
            df = df.with_columns([
                pl.col("fecha").dt.weekday().alias("dia_semana"),
                pl.col("fecha").dt.month().alias("mes")
            ])
            
            # Asignar temporada
            season_map = {}
            for season in self.seasons:
                for month in season.get("months", []):
                    season_map[month] = season["name"]
            
            df = df.with_column(
                pl.col("mes").map_dict(season_map, default="Media").alias("temporada")
            )
            
            # Crear columnas para cada canal
            channel_dfs = []
            
            for channel in self.channels:
                if not channel.get("active", True):
                    continue
                
                # Clonar DataFrame para este canal
                channel_df = df.clone()
                
                # Agregar información del canal
                channel_df = channel_df.with_columns([
                    pl.lit(channel["name"]).alias("canal"),
                    pl.lit(channel["commission"]).alias("comision"),
                    pl.lit(channel["priority"]).alias("prioridad_canal")
                ])
                
                channel_dfs.append(channel_df)
            
            # Combinar todos los canales
            combined_df = pl.concat(channel_dfs)
            
            # Agregar columnas para factores y tarifas
            combined_df = combined_df.with_columns([
                pl.lit(1.0).alias("factor_temporada"),
                pl.lit(1.0).alias("factor_ocupacion"),
                pl.lit(1.0).alias("factor_canal"),
                pl.lit(1.0).alias("factor_dia_semana"),
                pl.lit(1.0).alias("factor_total"),
                pl.lit(0.0).alias("tarifa_base"),
                pl.lit(0.0).alias("tarifa_recomendada")
            ])
            
            # Calcular tarifa base a partir del ADR previsto
            combined_df = combined_df.with_column(
                pl.col("adr_previsto").alias("tarifa_base")
            )
            
            # Si la tarifa base es 0, usar un valor por defecto basado en el tipo de habitación
            combined_df = combined_df.with_column(
                pl.when(pl.col("tarifa_base") <= 0)
                .then(pl.col("room_type_id").map_dict(
                    {room.id: room.tarifa_base for room in Room.get_all()},
                    default=100.0
                ))
                .otherwise(pl.col("tarifa_base"))
                .alias("tarifa_base")
            )
            
            return combined_df
            
        except Exception as e:
            logger.error(f"Error al preparar datos para reglas de pricing: {e}")
            return pl.DataFrame()
    
    def _apply_rule(self, df, rule):
        """
        Aplica una regla de pricing al DataFrame.
        
        Args:
            df (pl.DataFrame): DataFrame con los datos
            rule (Rule): Regla a aplicar
            
        Returns:
            pl.DataFrame: DataFrame con la regla aplicada
        """
        try:
            if df.is_empty():
                return df
            
            rule_type = rule.parametros.get("tipo")
            
            if rule_type == "temporada":
                return self._apply_season_rule(df, rule)
            elif rule_type == "ocupacion":
                return self._apply_occupancy_rule(df, rule)
            elif rule_type == "canal":
                return self._apply_channel_rule(df, rule)
            elif rule_type == "dia_semana":
                return self._apply_weekday_rule(df, rule)
            else:
                logger.warning(f"Tipo de regla desconocido: {rule_type}")
                return df
                
        except Exception as e:
            logger.error(f"Error al aplicar regla {rule.nombre}: {e}")
            return df
    
    def _apply_season_rule(self, df, rule):
        """
        Aplica la regla de temporada.
        
        Args:
            df (pl.DataFrame): DataFrame con los datos
            rule (Rule): Regla a aplicar
            
        Returns:
            pl.DataFrame: DataFrame con la regla aplicada
        """
        try:
            factors = rule.parametros.get("factores", {})
            
            # Crear expresión para mapear temporadas a factores
            df = df.with_column(
                pl.col("temporada").map_dict(factors, default=1.0).alias("factor_temporada")
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error al aplicar regla de temporada: {e}")
            return df
    
    def _apply_occupancy_rule(self, df, rule):
        """
        Aplica la regla de ocupación.
        
        Args:
            df (pl.DataFrame): DataFrame con los datos
            rule (Rule): Regla a aplicar
            
        Returns:
            pl.DataFrame: DataFrame con la regla aplicada
        """
        try:
            thresholds = rule.parametros.get("umbrales", {})
            factors = rule.parametros.get("factores", {})
            
            low_threshold = thresholds.get("bajo", 0.4) * 100  # Convertir a porcentaje
            high_threshold = thresholds.get("alto", 0.8) * 100  # Convertir a porcentaje
            
            low_factor = factors.get("bajo", 0.9)
            mid_factor = factors.get("medio", 1.0)
            high_factor = factors.get("alto", 1.15)
            
            # Aplicar factores según la ocupación prevista
            df = df.with_column(
                pl.when(pl.col("ocupacion_prevista") < low_threshold)
                .then(pl.lit(low_factor))
                .when(pl.col("ocupacion_prevista") > high_threshold)
                .then(pl.lit(high_factor))
                .otherwise(pl.lit(mid_factor))
                .alias("factor_ocupacion")
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error al aplicar regla de ocupación: {e}")
            return df
    
    def _apply_channel_rule(self, df, rule):
        """
        Aplica la regla de canal.
        
        Args:
            df (pl.DataFrame): DataFrame con los datos
            rule (Rule): Regla a aplicar
            
        Returns:
            pl.DataFrame: DataFrame con la regla aplicada
        """
        try:
            factors_list = rule.parametros.get("factores", [])
            
            # Crear diccionario de factores por canal
            channel_factors = {}
            for factor_dict in factors_list:
                channel_factors[factor_dict.get("canal")] = factor_dict.get("factor", 1.0)
            
            # Aplicar factores según el canal
            df = df.with_column(
                pl.col("canal").map_dict(channel_factors, default=1.0).alias("factor_canal")
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error al aplicar regla de canal: {e}")
            return df
    
    def _apply_weekday_rule(self, df, rule):
        """
        Aplica la regla de día de la semana.
        
        Args:
            df (pl.DataFrame): DataFrame con los datos
            rule (Rule): Regla a aplicar
            
        Returns:
            pl.DataFrame: DataFrame con la regla aplicada
        """
        try:
            factors = rule.parametros.get("factores", {})
            
            # Convertir claves a strings para el mapeo
            weekday_factors = {str(k): v for k, v in factors.items()}
            
            # Aplicar factores según el día de la semana
            df = df.with_column(
                pl.col("dia_semana").cast(pl.Utf8).map_dict(weekday_factors, default=1.0).alias("factor_dia_semana")
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error al aplicar regla de día de la semana: {e}")
            return df
    
    def _calculate_final_rates(self, df):
        """
        Calcula las tarifas finales aplicando todos los factores.
        
        Args:
            df (pl.DataFrame): DataFrame con los factores aplicados
            
        Returns:
            pl.DataFrame: DataFrame con las tarifas finales calculadas
        """
        try:
            if df.is_empty():
                return df
            
            # Calcular factor total multiplicando todos los factores
            df = df.with_column(
                (pl.col("factor_temporada") * pl.col("factor_ocupacion") * 
                 pl.col("factor_canal") * pl.col("factor_dia_semana")).alias("factor_total")
            )
            
            # Calcular tarifa recomendada
            df = df.with_column(
                (pl.col("tarifa_base") * pl.col("factor_total")).round(0).alias("tarifa_recomendada")
            )
            
            # Aplicar límites de factor
            min_factor = self.pricing_config.get("min_price_factor", 0.7)
            max_factor = self.pricing_config.get("max_price_factor", 1.3)
            
            df = df.with_column(
                pl.when(pl.col("factor_total") < min_factor)
                .then(pl.col("tarifa_base") * min_factor)
                .when(pl.col("factor_total") > max_factor)
                .then(pl.col("tarifa_base") * max_factor)
                .otherwise(pl.col("tarifa_recomendada"))
                .round(0)
                .alias("tarifa_recomendada")
            )
            
            # Aplicar descuento para canal directo
            direct_discount = self.pricing_config.get("direct_channel_discount", 0.05)
            
            df = df.with_column(
                pl.when(pl.col("canal") == "Directo")
                .then((pl.col("tarifa_recomendada") * (1 - direct_discount)).round(0))
                .otherwise(pl.col("tarifa_recomendada"))
                .alias("tarifa_recomendada")
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error al calcular tarifas finales: {e}")
            return df
    
    def generate_recommendations(self, start_date, end_date, room_type_id=None):
        """
        Genera recomendaciones de tarifas aplicando las reglas de pricing.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            tuple: (éxito, mensaje, recomendaciones)
        """
        try:
            logger.info(f"Generando recomendaciones para el rango {start_date} - {end_date}")
            
            # Aplicar reglas
            recommendations_df = self.apply_rules(start_date, end_date, room_type_id)
            
            if recommendations_df.is_empty():
                return (False, "No se pudieron generar recomendaciones", None)
            
            # Convertir a formato de salida
            result = {
                "recomendaciones": recommendations_df,
                "periodo": f"{start_date} a {end_date}",
                "generado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return (True, f"Se generaron {len(recommendations_df)} recomendaciones", result)
            
        except Exception as e:
            logger.error(f"Error al generar recomendaciones: {e}")
            return (False, f"Error: {e}", None)
    
    def save_recommendations(self, recommendations_df):
        """
        Guarda las recomendaciones en la base de datos.
        
        Args:
            recommendations_df (pl.DataFrame): DataFrame con las recomendaciones
            
        Returns:
            tuple: (éxito, mensaje, filas_guardadas)
        """
        try:
            if recommendations_df.is_empty():
                return (False, "No hay recomendaciones para guardar", 0)
            
            # Convertir a lista de diccionarios
            recommendations = recommendations_df.to_dicts()
            
            # Guardar en la base de datos
            saved_count = 0
            
            for rec in recommendations:
                # Buscar si ya existe una recomendación para esta fecha, tipo de habitación y canal
                existing_rec = ApprovedRecommendation.get_by_date_room_channel(
                    rec["fecha"], rec["room_type_id"], self._get_channel_id(rec["canal"])
                )
                
                if existing_rec:
                    # Actualizar recomendación existente
                    existing_rec.tarifa_base = rec["tarifa_base"]
                    existing_rec.tarifa_recomendada = rec["tarifa_recomendada"]
                    existing_rec.tarifa_aprobada = rec["tarifa_recomendada"]  # Por defecto, se aprueba la recomendada
                    existing_rec.save()
                    saved_count += 1
                else:
                    # Crear nueva recomendación
                    new_rec = ApprovedRecommendation(
                        fecha=rec["fecha"],
                        room_type_id=rec["room_type_id"],
                        channel_id=self._get_channel_id(rec["canal"]),
                        tarifa_base=rec["tarifa_base"],
                        tarifa_recomendada=rec["tarifa_recomendada"],
                        tarifa_aprobada=rec["tarifa_recomendada"],  # Por defecto, se aprueba la recomendada
                        estado="Pendiente"
                    )
                    new_rec.save()
                    saved_count += 1
            
            return (True, f"Se guardaron {saved_count} recomendaciones", saved_count)
            
        except Exception as e:
            logger.error(f"Error al guardar recomendaciones: {e}")
            return (False, f"Error: {e}", 0)
    
    def _get_channel_id(self, channel_name):
        """
        Obtiene el ID de un canal por su nombre.
        
        Args:
            channel_name (str): Nombre del canal
            
        Returns:
            int: ID del canal o 1 si no se encuentra
        """
        for i, channel in enumerate(self.channels):
            if channel["name"] == channel_name:
                return i + 1  # IDs empiezan en 1
        return 1  # Canal directo por defecto