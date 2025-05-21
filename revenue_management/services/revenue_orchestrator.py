#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Servicio orquestador para el Framework de Revenue Management
"""

import polars as pl
from datetime import datetime, timedelta
from utils.logger import setup_logger
from services.analysis.kpi_calculator import KpiCalculator
from services.forecasting.forecast_service import ForecastService
from services.pricing.pricing_rule_engine import PricingRuleEngine
from services.export.tariff_exporter import TariffExporter
from models.room import Room
from config import config

# Configurar logger
logger = setup_logger(__name__)

class RevenueOrchestrator:
    """
    Clase orquestadora que coordina el flujo completo del proceso de Revenue Management
    """
    
    def __init__(self):
        """
        Inicializa la instancia de RevenueOrchestrator
        """
        self.kpi_calculator = KpiCalculator()
        self.forecast_service = ForecastService()
        self.pricing_engine = PricingRuleEngine()
        self.tariff_exporter = TariffExporter()
        self.room_types = {room.id: room for room in Room.get_all()}
    
    def run_full_process(self, start_date=None, end_date=None, forecast_days=None, room_type_id=None, export_results=False):
        """
        Ejecuta el proceso completo de Revenue Management.
        
        Args:
            start_date (str/datetime, optional): Fecha de inicio para datos históricos
            end_date (str/datetime, optional): Fecha de fin para datos históricos
            forecast_days (int, optional): Número de días a pronosticar
            room_type_id (int, optional): ID del tipo de habitación
            export_results (bool, optional): Indica si se deben exportar los resultados
            
        Returns:
            dict: Resultados del proceso
        """
        try:
            logger.info("Iniciando proceso completo de Revenue Management")
            
            # Establecer fechas por defecto si no se proporcionan
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            if forecast_days is None:
                forecast_days = config.get_forecasting_config().get("forecast_days", 90)
            
            results = {}
            
            # Paso 1: Análisis de KPIs
            logger.info("Paso 1: Análisis de KPIs")
            kpi_results = self.analyze_kpis(start_date, end_date, room_type_id)
            results["kpi_analysis"] = kpi_results
            
            # Paso 2: Generación de pronósticos
            logger.info("Paso 2: Generación de pronósticos")
            forecast_results = self.generate_forecasts(start_date, end_date, forecast_days, room_type_id)
            results["forecasts"] = forecast_results
            
            # Paso 3: Aplicación de reglas de pricing
            logger.info("Paso 3: Aplicación de reglas de pricing")
            pricing_results = self.apply_pricing_rules(forecast_days, room_type_id)
            results["pricing"] = pricing_results
            
            # Paso 4: Exportación de resultados (opcional)
            if export_results:
                logger.info("Paso 4: Exportación de resultados")
                export_results = self.export_tariffs()
                results["export"] = export_results
            
            logger.info("Proceso completo de Revenue Management finalizado con éxito")
            
            return {
                "success": True,
                "message": "Proceso completo ejecutado con éxito",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error en el proceso completo de Revenue Management: {e}")
            return {
                "success": False,
                "message": f"Error: {e}",
                "results": {}
            }
    
    def analyze_kpis(self, start_date, end_date, room_type_id=None):
        """
        Ejecuta el análisis de KPIs.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Resultados del análisis de KPIs
        """
        try:
            logger.info(f"Analizando KPIs para el rango {start_date} - {end_date}")
            
            # Calcular KPIs
            kpi_df = self.kpi_calculator.calculate_kpis(start_date, end_date, room_type_id)
            
            if kpi_df.is_empty():
                return {
                    "success": False,
                    "message": "No hay datos suficientes para calcular KPIs",
                    "data": {}
                }
            
            # Calcular KPIs agregados
            agg_kpis = self.kpi_calculator.calculate_aggregated_kpis(start_date, end_date, "room_type_id")
            
            # Analizar patrones de ocupación
            occupancy_patterns = self.kpi_calculator.analyze_occupancy_patterns(start_date, end_date, room_type_id)
            
            # Calcular comparación YoY
            yoy_comparison = self.kpi_calculator.calculate_yoy_comparison(start_date, end_date, room_type_id)
            
            return {
                "success": True,
                "message": "Análisis de KPIs completado con éxito",
                "data": {
                    "kpis": kpi_df,
                    "kpis_agregados": agg_kpis,
                    "patrones_ocupacion": occupancy_patterns,
                    "comparacion_yoy": yoy_comparison
                }
            }
            
        except Exception as e:
            logger.error(f"Error en el análisis de KPIs: {e}")
            return {
                "success": False,
                "message": f"Error: {e}",
                "data": {}
            }
    
    def generate_forecasts(self, start_date, end_date, forecast_days=None, room_type_id=None):
        """
        Genera pronósticos de ocupación.
        
        Args:
            start_date (str/datetime): Fecha de inicio para datos históricos
            end_date (str/datetime): Fecha de fin para datos históricos
            forecast_days (int, optional): Número de días a pronosticar
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Resultados de la generación de pronósticos
        """
        try:
            logger.info(f"Generando pronósticos para el rango {start_date} - {end_date}")
            
            # Generar pronósticos
            forecasts = self.forecast_service.generate_forecast(start_date, end_date, forecast_days, room_type_id)
            
            if not forecasts:
                return {
                    "success": False,
                    "message": "No se pudieron generar pronósticos",
                    "data": {}
                }
            
            # Guardar pronósticos en la base de datos
            success, message, count = self.forecast_service.save_forecast_to_db(forecasts)
            
            if not success:
                return {
                    "success": False,
                    "message": message,
                    "data": {}
                }
            
            # Actualizar KPIs de pronósticos
            forecast_start = datetime.now().strftime("%Y-%m-%d")
            forecast_end = (datetime.now() + timedelta(days=forecast_days)).strftime("%Y-%m-%d")
            
            success, message, count = self.forecast_service.update_forecast_kpis(forecast_start, forecast_end, room_type_id)
            
            # Cargar pronósticos actualizados
            forecast_df = self.forecast_service.load_forecast_from_db(forecast_start, forecast_end, room_type_id)
            
            return {
                "success": True,
                "message": f"Se generaron y guardaron {count} pronósticos",
                "data": {
                    "forecast_df": forecast_df,
                    "periodo": f"{forecast_start} a {forecast_end}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error en la generación de pronósticos: {e}")
            return {
                "success": False,
                "message": f"Error: {e}",
                "data": {}
            }
    
    def apply_pricing_rules(self, forecast_days=90, room_type_id=None):
        """
        Aplica reglas de pricing para generar recomendaciones de tarifas.
        
        Args:
            forecast_days (int, optional): Número de días a considerar
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Resultados de la aplicación de reglas de pricing
        """
        try:
            logger.info(f"Aplicando reglas de pricing para los próximos {forecast_days} días")
            
            # Establecer fechas
            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=forecast_days)).strftime("%Y-%m-%d")
            
            # Generar recomendaciones
            success, message, recommendations = self.pricing_engine.generate_recommendations(start_date, end_date, room_type_id)
            
            if not success:
                return {
                    "success": False,
                    "message": message,
                    "data": {}
                }
            
            # Guardar recomendaciones
            recommendations_df = recommendations["recomendaciones"]
            success, message, count = self.pricing_engine.save_recommendations(recommendations_df)
            
            return {
                "success": success,
                "message": message,
                "data": {
                    "recommendations_df": recommendations_df,
                    "periodo": recommendations["periodo"],
                    "count": count
                }
            }
            
        except Exception as e:
            logger.error(f"Error en la aplicación de reglas de pricing: {e}")
            return {
                "success": False,
                "message": f"Error: {e}",
                "data": {}
            }
    
    def export_tariffs(self, start_date=None, end_date=None, room_type_id=None, channel_id=None):
        """
        Exporta tarifas aprobadas a Excel.
        
        Args:
            start_date (str/datetime, optional): Fecha de inicio
            end_date (str/datetime, optional): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            channel_id (int, optional): ID del canal
            
        Returns:
            dict: Resultados de la exportación de tarifas
        """
        try:
            logger.info("Exportando tarifas aprobadas")
            
            # Exportar a Excel
            success, message, filepath = self.tariff_exporter.export_to_excel(start_date, end_date, room_type_id, channel_id)
            
            return {
                "success": success,
                "message": message,
                "data": {
                    "filepath": filepath
                }
            }
            
        except Exception as e:
            logger.error(f"Error en la exportación de tarifas: {e}")
            return {
                "success": False,
                "message": f"Error: {e}",
                "data": {}
            }
    
    def get_dashboard_data(self):
        """
        Obtiene datos para el dashboard.
        
        Returns:
            dict: Datos para el dashboard
        """
        try:
            logger.info("Obteniendo datos para el dashboard")
            
            # Fechas para datos históricos (último año)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Fechas para pronósticos (próximos 90 días)
            forecast_start = end_date
            forecast_end = end_date + timedelta(days=90)
            
            # Obtener KPIs históricos
            kpi_df = self.kpi_calculator.calculate_kpis(start_date, end_date)
            
            # Obtener KPIs agregados
            agg_kpis = self.kpi_calculator.calculate_aggregated_kpis(start_date, end_date, "both")
            
            # Obtener pronósticos
            forecast_df = self.forecast_service.load_forecast_from_db(forecast_start, forecast_end)
            
            # Obtener recomendaciones pendientes
            pending_df = self.tariff_exporter.get_pending_exports()
            
            return {
                "success": True,
                "message": "Datos para dashboard obtenidos con éxito",
                "data": {
                    "kpi_df": kpi_df,
                    "agg_kpis": agg_kpis,
                    "forecast_df": forecast_df,
                    "pending_df": pending_df,
                    "periodo_historico": f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}",
                    "periodo_pronostico": f"{forecast_start.strftime('%Y-%m-%d')} a {forecast_end.strftime('%Y-%m-%d')}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error al obtener datos para el dashboard: {e}")
            return {
                "success": False,
                "message": f"Error: {e}",
                "data": {}
            }