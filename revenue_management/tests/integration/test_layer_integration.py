#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas de integración para verificar la integración entre las diferentes capas del sistema
"""

import unittest
import os
import sys
import tempfile
import pandas as pd
import polars as pl
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.data_ingestion.data_ingestion_service import DataIngestionService
from services.data_ingestion.excel_reader import ExcelReader
from services.analysis.kpi_calculator import KpiCalculator
from services.forecasting.forecast_service import ForecastService
from services.pricing.pricing_rule_engine import PricingRuleEngine
from services.export.tariff_exporter import TariffExporter
from models.daily_occupancy import DailyOccupancy
from models.daily_revenue import DailyRevenue
from models.forecast import Forecast
from models.recommendation import ApprovedRecommendation
from models.room import Room
from models.rule import Rule
from db.database import db
from config import config

class TestDataToAnalysisIntegration(unittest.TestCase):
    """
    Pruebas de integración entre la capa de datos y la capa de análisis
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear un directorio temporal para archivos de prueba
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Crear un archivo Excel temporal para las pruebas
        self.test_file_path = Path(self.temp_dir.name) / "test_data.xlsx"
        
        # Fechas de prueba
        self.start_date = datetime.now() - timedelta(days=30)
        self.end_date = datetime.now()
        
        # Crear datos de prueba
        self.create_test_data()
        
        # Crear instancias de los servicios
        self.ingestion_service = DataIngestionService()
        self.kpi_calculator = KpiCalculator()
    
    def tearDown(self):
        """
        Limpieza después de las pruebas
        """
        # Eliminar el directorio temporal
        self.temp_dir.cleanup()
    
    def create_test_data(self):
        """
        Crea datos de prueba para la ingesta
        """
        # Crear datos de ocupación diaria
        occupancy_data = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Generar datos para dos tipos de habitación
            for room_type_id in [1, 2]:
                # Simular estacionalidad y tendencia
                day_of_week = current_date.weekday()
                month = current_date.month
                
                # Mayor ocupación en fin de semana y temporada alta
                weekend_factor = 1.2 if day_of_week >= 5 else 1.0
                season_factor = 1.2 if month in [1, 7, 8, 12] else 1.0 if month in [2, 3, 9, 10] else 0.8
                
                # Calcular ocupación con algo de ruido
                base_occupancy = 0.7 if room_type_id == 1 else 0.6
                occupancy = min(1.0, base_occupancy * weekend_factor * season_factor + np.random.normal(0, 0.05))
                
                # Habitaciones disponibles según tipo
                available_rooms = 10 if room_type_id == 1 else 15
                occupied_rooms = int(occupancy * available_rooms)
                
                occupancy_data.append({
                    'fecha': current_date.strftime('%Y-%m-%d'),
                    'tipo_habitacion': f'Tipo {room_type_id}',
                    'habitaciones_disponibles': available_rooms,
                    'habitaciones_ocupadas': occupied_rooms,
                    'ocupacion_porcentaje': occupancy * 100
                })
            
            current_date += timedelta(days=1)
        
        # Crear DataFrame y guardar en Excel
        occupancy_df = pd.DataFrame(occupancy_data)
        occupancy_df.to_excel(self.test_file_path, sheet_name='Ocupacion', index=False)
    
    @patch('models.daily_occupancy.DailyOccupancy.save')
    @patch('models.daily_revenue.DailyRevenue.save')
    def test_data_ingestion_to_analysis(self, mock_revenue_save, mock_occupancy_save):
        """
        Prueba la integración entre la ingesta de datos y el análisis
        """
        # Configurar los mocks
        mock_occupancy_save.return_value = 1  # ID de la ocupación guardada
        mock_revenue_save.return_value = 1  # ID del ingreso guardado
        
        # Paso 1: Leer datos de Excel
        excel_reader = ExcelReader()
        df = excel_reader.read_excel_file(self.test_file_path, sheet_name='Ocupacion')
        
        # Verificar que se leyeron correctamente
        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        
        # Paso 2: Convertir a Polars
        pl_df = excel_reader.convert_to_polars(df)
        
        # Verificar que se convirtió correctamente
        self.assertIsNotNone(pl_df)
        self.assertIsInstance(pl_df, pl.DataFrame)
        self.assertEqual(len(pl_df), len(df))
        
        # Paso 3: Procesar y guardar datos
        # Simulamos el procesamiento y guardado de datos
        occupancy_objects = []
        revenue_objects = []
        
        for row in pl_df.to_dicts():
            # Crear objeto de ocupación
            occupancy = DailyOccupancy(
                fecha=row['fecha'],
                room_type_id=1 if row['tipo_habitacion'] == 'Tipo 1' else 2,
                habitaciones_disponibles=row['habitaciones_disponibles'],
                habitaciones_ocupadas=row['habitaciones_ocupadas'],
                ocupacion_porcentaje=row['ocupacion_porcentaje']
            )
            occupancy.id = occupancy.save()  # Guardar en la base de datos
            occupancy_objects.append(occupancy)
            
            # Crear objeto de ingresos
            # Calcular ADR (entre 100,000 y 200,000 COP)
            adr = 100000 + 50000 * (1 if row['tipo_habitacion'] == 'Tipo 1' else 2)
            ingresos = adr * row['habitaciones_ocupadas']
            revpar = ingresos / row['habitaciones_disponibles']
            
            revenue = DailyRevenue(
                fecha=row['fecha'],
                room_type_id=1 if row['tipo_habitacion'] == 'Tipo 1' else 2,
                ingresos=ingresos,
                adr=adr,
                revpar=revpar
            )
            revenue.id = revenue.save()  # Guardar en la base de datos
            revenue_objects.append(revenue)
        
        # Paso 4: Calcular KPIs
        # Configurar mocks para obtener los datos guardados
        with patch('models.daily_occupancy.DailyOccupancy.get_by_date_range', return_value=occupancy_objects):
            with patch('models.daily_revenue.DailyRevenue.get_by_date_range', return_value=revenue_objects):
                # Calcular KPIs
                kpi_df = self.kpi_calculator.calculate_kpis(
                    self.start_date.strftime('%Y-%m-%d'),
                    self.end_date.strftime('%Y-%m-%d')
                )
                
                # Verificar que se calcularon correctamente
                self.assertIsNotNone(kpi_df)
                self.assertIsInstance(kpi_df, pl.DataFrame)
                self.assertGreater(len(kpi_df), 0)
                
                # Verificar que contiene las columnas esperadas
                expected_columns = ['fecha', 'room_type_id', 'habitaciones_disponibles', 
                                   'habitaciones_ocupadas', 'ocupacion_porcentaje', 
                                   'ingresos', 'adr', 'revpar']
                
                for col in expected_columns:
                    self.assertIn(col, kpi_df.columns)


class TestAnalysisToForecastingIntegration(unittest.TestCase):
    """
    Pruebas de integración entre la capa de análisis y la capa de previsión
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Fechas de prueba
        self.start_date = datetime.now() - timedelta(days=365)
        self.end_date = datetime.now()
        self.forecast_days = 30
        
        # Crear instancias de los servicios
        self.kpi_calculator = KpiCalculator()
        self.forecast_service = ForecastService()
    
    @patch('models.daily_occupancy.DailyOccupancy.get_by_date_range')
    @patch('models.daily_revenue.DailyRevenue.get_by_date_range')
    @patch('models.room.Room.get_all')
    @patch('prophet.Prophet')
    @patch('models.forecast.Forecast.save')
    def test_analysis_to_forecasting(self, mock_forecast_save, mock_prophet, mock_rooms, mock_revenue, mock_occupancy):
        """
        Prueba la integración entre el análisis y la previsión
        """
        # Crear datos de ocupación diaria
        occupancy_data = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Generar datos para dos tipos de habitación
            for room_type_id in [1, 2]:
                # Simular estacionalidad y tendencia
                day_of_week = current_date.weekday()
                month = current_date.month
                
                # Mayor ocupación en fin de semana y temporada alta
                weekend_factor = 1.2 if day_of_week >= 5 else 1.0
                season_factor = 1.2 if month in [1, 7, 8, 12] else 1.0 if month in [2, 3, 9, 10] else 0.8
                
                # Calcular ocupación con algo de ruido
                base_occupancy = 0.7 if room_type_id == 1 else 0.6
                occupancy = min(1.0, base_occupancy * weekend_factor * season_factor + np.random.normal(0, 0.05))
                
                # Habitaciones disponibles según tipo
                available_rooms = 10 if room_type_id == 1 else 15
                occupied_rooms = int(occupancy * available_rooms)
                
                occupancy_data.append({
                    'id': len(occupancy_data) + 1,
                    'fecha': current_date.strftime('%Y-%m-%d'),
                    'room_type_id': room_type_id,
                    'habitaciones_disponibles': available_rooms,
                    'habitaciones_ocupadas': occupied_rooms,
                    'ocupacion_porcentaje': occupancy * 100
                })
            
            current_date += timedelta(days=1)
        
        # Crear datos de ingresos diarios
        revenue_data = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Generar datos para dos tipos de habitación
            for room_type_id in [1, 2]:
                # Buscar la ocupación correspondiente
                occupancy_entry = next(
                    (o for o in occupancy_data if o['fecha'] == current_date.strftime('%Y-%m-%d') and o['room_type_id'] == room_type_id),
                    None
                )
                
                if occupancy_entry:
                    # Calcular ADR (entre 100,000 y 200,000 COP)
                    adr = 100000 + 50000 * room_type_id
                    ingresos = adr * occupancy_entry['habitaciones_ocupadas']
                    revpar = ingresos / occupancy_entry['habitaciones_disponibles']
                    
                    revenue_data.append({
                        'id': len(revenue_data) + 1,
                        'fecha': current_date.strftime('%Y-%m-%d'),
                        'room_type_id': room_type_id,
                        'ingresos': ingresos,
                        'adr': adr,
                        'revpar': revpar
                    })
            
            current_date += timedelta(days=1)
        
        # Configurar los mocks
        mock_occupancy.return_value = [DailyOccupancy(**data) for data in occupancy_data]
        mock_revenue.return_value = [DailyRevenue(**data) for data in revenue_data]
        mock_rooms.return_value = [
            Room(id=1, cod_hab='EST', name='Estándar Triple', capacity=3, num_config=10),
            Room(id=2, cod_hab='JRS', name='Junior Suite', capacity=5, num_config=15)
        ]
        
        # Configurar el mock de Prophet
        prophet_instance = MagicMock()
        prophet_instance.fit.return_value = None
        
        # Crear un DataFrame de pronóstico simulado
        future_dates = pd.date_range(start=self.end_date, periods=self.forecast_days)
        forecast_df = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.random.uniform(0.6, 0.8, size=len(future_dates)),
            'yhat_lower': np.random.uniform(0.5, 0.6, size=len(future_dates)),
            'yhat_upper': np.random.uniform(0.8, 0.9, size=len(future_dates))
        })
        
        prophet_instance.predict.return_value = forecast_df
        mock_prophet.return_value = prophet_instance
        
        # Configurar el mock de save
        mock_forecast_save.return_value = 1  # ID del pronóstico guardado
        
        # Paso 1: Calcular KPIs
        kpi_df = self.kpi_calculator.calculate_kpis(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d')
        )
        
        # Verificar que se calcularon correctamente
        self.assertIsNotNone(kpi_df)
        self.assertIsInstance(kpi_df, pl.DataFrame)
        self.assertGreater(len(kpi_df), 0)
        
        # Paso 2: Preparar datos para el modelo de previsión
        prepared_data = self.forecast_service.prepare_data(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d')
        )
        
        # Verificar que se prepararon correctamente
        self.assertIsNotNone(prepared_data)
        self.assertIsInstance(prepared_data, dict)
        self.assertEqual(len(prepared_data), 2)  # Dos tipos de habitación
        
        # Paso 3: Generar pronósticos
        forecasts = self.forecast_service.generate_forecast(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            self.forecast_days
        )
        
        # Verificar que se generaron correctamente
        self.assertIsNotNone(forecasts)
        self.assertIsInstance(forecasts, dict)
        self.assertEqual(len(forecasts), 2)  # Dos tipos de habitación
        
        # Paso 4: Guardar pronósticos
        success, message, count = self.forecast_service.save_forecast_to_db(forecasts)
        
        # Verificar que se guardaron correctamente
        self.assertTrue(success)
        self.assertEqual(count, self.forecast_days * 2)  # Días * tipos de habitación


class TestForecastingToPricingIntegration(unittest.TestCase):
    """
    Pruebas de integración entre la capa de previsión y la capa de pricing
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Fechas de prueba
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=30)
        
        # Crear instancias de los servicios
        self.forecast_service = ForecastService()
        self.pricing_engine = PricingRuleEngine()
    
    @patch('models.forecast.Forecast.get_by_date_range')
    @patch('models.rule.Rule.get_active_rules')
    @patch('models.recommendation.ApprovedRecommendation.save')
    def test_forecasting_to_pricing(self, mock_recommendation_save, mock_rules, mock_forecasts):
        """
        Prueba la integración entre la previsión y el pricing
        """
        # Crear pronósticos de prueba
        forecast_data = []
        current_date = self.start_date
        
        for i in range(30):  # 30 días
            # Generar datos para dos tipos de habitación
            for room_type_id in [1, 2]:
                # Simular estacionalidad y tendencia
                day_of_week = current_date.weekday()
                month = current_date.month
                
                # Mayor ocupación en fin de semana y temporada alta
                weekend_factor = 1.2 if day_of_week >= 5 else 1.0
                season_factor = 1.2 if month in [1, 7, 8, 12] else 1.0 if month in [2, 3, 9, 10] else 0.8
                
                # Calcular ocupación con algo de ruido
                base_occupancy = 0.7 if room_type_id == 1 else 0.6
                occupancy = min(1.0, base_occupancy * weekend_factor * season_factor + np.random.normal(0, 0.05))
                
                # Calcular ADR y RevPAR
                base_adr = 100000 + 50000 * room_type_id
                adr = base_adr + np.random.normal(0, 5000)
                revpar = adr * occupancy
                
                forecast_data.append({
                    'id': len(forecast_data) + 1,
                    'fecha': current_date.strftime('%Y-%m-%d'),
                    'room_type_id': room_type_id,
                    'ocupacion_prevista': occupancy * 100,
                    'adr_previsto': adr,
                    'revpar_previsto': revpar,
                    'ajustado_manualmente': False
                })
            
            current_date += timedelta(days=1)
        
        # Crear reglas de prueba
        rules_data = [
            {
                'id': 1,
                'nombre': 'Regla de Temporada',
                'descripcion': 'Ajusta tarifas según la temporada',
                'parametros': {
                    'tipo': 'temporada',
                    'factores': {
                        'Baja': 0.9,
                        'Media': 1.0,
                        'Alta': 1.2
                    }
                },
                'prioridad': 1,
                'activa': True
            },
            {
                'id': 2,
                'nombre': 'Regla de Ocupación',
                'descripcion': 'Ajusta tarifas según la ocupación prevista',
                'parametros': {
                    'tipo': 'ocupacion',
                    'umbrales': {
                        'bajo': 0.4,
                        'alto': 0.8
                    },
                    'factores': {
                        'bajo': 0.9,
                        'medio': 1.0,
                        'alto': 1.15
                    }
                },
                'prioridad': 2,
                'activa': True
            }
        ]
        
        # Configurar los mocks
        mock_forecasts.return_value = [Forecast(**data) for data in forecast_data]
        mock_rules.return_value = [Rule(**data) for data in rules_data]
        mock_recommendation_save.return_value = 1  # ID de la recomendación guardada
        
        # Paso 1: Cargar pronósticos
        with patch('models.forecast.Forecast.get_by_date_range', return_value=[Forecast(**data) for data in forecast_data]):
            forecast_df = self.forecast_service.load_forecast_from_db(
                self.start_date.strftime('%Y-%m-%d'),
                self.end_date.strftime('%Y-%m-%d')
            )
            
            # Verificar que se cargaron correctamente
            self.assertIsNotNone(forecast_df)
            self.assertIsInstance(forecast_df, pl.DataFrame)
            self.assertEqual(len(forecast_df), len(forecast_data))
        
        # Paso 2: Aplicar reglas de pricing
        recommendations_df = self.pricing_engine.apply_rules(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d')
        )
        
        # Verificar que se aplicaron correctamente
        self.assertIsNotNone(recommendations_df)
        self.assertIsInstance(recommendations_df, pl.DataFrame)
        self.assertGreater(len(recommendations_df), 0)
        
        # Paso 3: Generar recomendaciones
        success, message, recommendations = self.pricing_engine.generate_recommendations(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d')
        )
        
        # Verificar que se generaron correctamente
        self.assertTrue(success)
        self.assertIsNotNone(recommendations)
        self.assertIn('recomendaciones', recommendations)
        
        # Paso 4: Guardar recomendaciones
        recommendations_df = recommendations['recomendaciones']
        success, message, count = self.pricing_engine.save_recommendations(recommendations_df)
        
        # Verificar que se guardaron correctamente
        self.assertTrue(success)
        self.assertGreater(count, 0)


class TestPricingToExportIntegration(unittest.TestCase):
    """
    Pruebas de integración entre la capa de pricing y la capa de exportación
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Fechas de prueba
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=30)
        
        # Crear instancias de los servicios
        self.pricing_engine = PricingRuleEngine()
        self.tariff_exporter = TariffExporter()
        
        # Crear un directorio temporal para archivos de prueba
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """
        Limpieza después de las pruebas
        """
        # Eliminar el directorio temporal
        self.temp_dir.cleanup()
    
    @patch('models.recommendation.ApprovedRecommendation.get_by_date_range')
    @patch('models.recommendation.ApprovedRecommendation.update_export_status')
    def test_pricing_to_export(self, mock_update_status, mock_recommendations):
        """
        Prueba la integración entre el pricing y la exportación
        """
        # Crear recomendaciones de prueba
        recommendations_data = []
        current_date = self.start_date
        
        for i in range(30):  # 30 días
            # Generar datos para dos tipos de habitación y dos canales
            for room_type_id in [1, 2]:
                for channel_id in [1, 2]:
                    # Calcular tarifas
                    base_rate = 100000 + 50000 * room_type_id
                    recommended_rate = base_rate * (1 + np.random.normal(0, 0.1))
                    approved_rate = recommended_rate  # Igual a la recomendada para simplificar
                    
                    recommendations_data.append({
                        'id': len(recommendations_data) + 1,
                        'fecha': current_date.strftime('%Y-%m-%d'),
                        'room_type_id': room_type_id,
                        'channel_id': channel_id,
                        'tarifa_base': base_rate,
                        'tarifa_recomendada': recommended_rate,
                        'tarifa_aprobada': approved_rate,
                        'created_at': datetime.now(),
                        'approved_at': datetime.now(),
                        'estado': 'Aprobada',
                        'exportado': False,
                        'exportado_at': None
                    })
            
            current_date += timedelta(days=1)
        
        # Configurar los mocks
        mock_recommendations.return_value = [ApprovedRecommendation(**data) for data in recommendations_data]
        mock_update_status.return_value = True
        
        # Configurar la ruta de exportación
        export_path = Path(self.temp_dir.name) / "tarifas_exportadas.xlsx"
        
        # Paso 1: Exportar tarifas
        with patch('services.export.tariff_exporter.TariffExporter._get_export_path', return_value=export_path):
            success, message, filepath = self.tariff_exporter.export_to_excel(
                self.start_date.strftime('%Y-%m-%d'),
                self.end_date.strftime('%Y-%m-%d')
            )
            
            # Verificar que se exportaron correctamente
            self.assertTrue(success)
            self.assertIsNotNone(filepath)
            self.assertEqual(filepath, str(export_path))
            
            # Verificar que se actualizó el estado de exportación
            self.assertTrue(mock_update_status.called)

if __name__ == "__main__":
    unittest.main()