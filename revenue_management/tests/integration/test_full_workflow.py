#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas de integración para el flujo completo del sistema
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

from services.revenue_orchestrator import RevenueOrchestrator
from services.data_ingestion.data_ingestion_service import DataIngestionService
from services.analysis.kpi_calculator import KpiCalculator
from services.forecasting.forecast_service import ForecastService
from services.pricing.pricing_rule_engine import PricingRuleEngine
from services.export.tariff_exporter import TariffExporter
from models.room import Room
from models.rule import Rule
from config import config

class TestFullWorkflow(unittest.TestCase):
    """
    Pruebas de integración para el flujo completo del sistema
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear un directorio temporal para archivos de prueba
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Crear archivos de prueba
        self.create_test_files()
        
        # Crear una instancia del orquestador
        self.orchestrator = RevenueOrchestrator()
        
        # Fechas de prueba
        self.start_date = datetime.now() - timedelta(days=365)
        self.end_date = datetime.now()
        self.forecast_days = 30
    
    def tearDown(self):
        """
        Limpieza después de las pruebas
        """
        # Eliminar el directorio temporal
        self.temp_dir.cleanup()
    
    def create_test_files(self):
        """
        Crea archivos de prueba para la ingesta de datos
        """
        # Crear un archivo Excel para reservas
        bookings_file = Path(self.temp_dir.name) / "test_bookings.xlsx"
        
        # Crear datos de reservas
        bookings_data = []
        current_date = self.start_date
        
        for i in range(100):  # 100 reservas de prueba
            # Fecha de reserva
            booking_date = current_date + timedelta(days=np.random.randint(1, 30))
            
            # Fecha de llegada (entre 1 y 90 días después de la reserva)
            check_in_date = booking_date + timedelta(days=np.random.randint(1, 90))
            
            # Duración de la estancia (entre 1 y 7 noches)
            nights = np.random.randint(1, 8)
            check_out_date = check_in_date + timedelta(days=nights)
            
            # Tipo de habitación
            room_types = ['EST', 'JRS', 'ESC', 'ESD', 'SUI', 'KSP', 'DSP']
            room_type = np.random.choice(room_types)
            
            # Tarifa (entre 100,000 y 300,000 COP por noche)
            rate_per_night = np.random.randint(100000, 300001)
            total_rate = rate_per_night * nights
            
            # Canal de distribución
            channels = ['Directo', 'Booking.com', 'Expedia', 'Hotelbeds', 'Despegar']
            channel = np.random.choice(channels)
            
            # Añadir a los datos
            bookings_data.append({
                'registro_num': f'R{i+1:03d}',
                'fecha_reserva': booking_date.strftime('%Y-%m-%d'),
                'fecha_llegada': check_in_date.strftime('%Y-%m-%d'),
                'fecha_salida': check_out_date.strftime('%Y-%m-%d'),
                'noches': nights,
                'cod_hab': room_type,
                'tipo_habitacion': self.get_room_type_name(room_type),
                'tarifa_neta': total_rate,
                'canal_distribucion': channel,
                'nombre_cliente': f'Cliente {i+1}',
                'email_cliente': f'cliente{i+1}@example.com',
                'telefono_cliente': f'123456789{i%10}',
                'estado_reserva': 'Confirmada',
                'observaciones': ''
            })
            
            # Avanzar la fecha actual
            current_date += timedelta(days=np.random.randint(1, 5))
        
        # Crear DataFrame y guardar en Excel
        bookings_df = pd.DataFrame(bookings_data)
        bookings_df.to_excel(bookings_file, sheet_name='Reservas', index=False)
        
        # Guardar la ruta del archivo
        self.test_bookings_file = bookings_file
        
        # Crear un archivo Excel para estancias
        stays_file = Path(self.temp_dir.name) / "test_stays.xlsx"
        
        # Crear datos de estancias (basados en las reservas)
        stays_data = []
        
        for i, booking in enumerate(bookings_data):
            # Solo convertir algunas reservas en estancias (las que ya habrían ocurrido)
            if datetime.strptime(booking['fecha_llegada'], '%Y-%m-%d') < datetime.now():
                stays_data.append({
                    'registro_num': booking['registro_num'],
                    'fecha_checkin': booking['fecha_llegada'],
                    'fecha_checkout': booking['fecha_salida'],
                    'noches': booking['noches'],
                    'cod_hab': booking['cod_hab'],
                    'tipo_habitacion': booking['tipo_habitacion'],
                    'valor_venta': booking['tarifa_neta'],
                    'canal_distribucion': booking['canal_distribucion'],
                    'nombre_cliente': booking['nombre_cliente'],
                    'email_cliente': booking['email_cliente'],
                    'telefono_cliente': booking['telefono_cliente'],
                    'estado_estancia': 'Completada',
                    'observaciones': ''
                })
        
        # Crear DataFrame y guardar en Excel
        stays_df = pd.DataFrame(stays_data)
        stays_df.to_excel(stays_file, sheet_name='Estancias', index=False)
        
        # Guardar la ruta del archivo
        self.test_stays_file = stays_file
    
    def get_room_type_name(self, code):
        """
        Obtiene el nombre del tipo de habitación a partir del código
        """
        room_types = {
            'EST': 'Estándar Triple',
            'JRS': 'Junior Suite',
            'ESC': 'Estándar Cuádruple',
            'ESD': 'Estándar Doble',
            'SUI': 'Suite',
            'KSP': 'King Superior',
            'DSP': 'Doble Superior'
        }
        return room_types.get(code, 'Desconocido')
    
    @patch('services.data_ingestion.data_ingestion_service.DataIngestionService.save_to_database')
    def test_data_ingestion(self, mock_save):
        """
        Prueba la ingesta de datos
        """
        # Configurar el mock
        mock_save.return_value = (True, 100)  # 100 registros guardados
        
        # Crear una instancia del servicio de ingesta
        ingestion_service = DataIngestionService()
        
        # Procesar reservas
        success, message, count = ingestion_service.process_bookings(self.test_bookings_file)
        
        # Verificar que se procesaron correctamente
        self.assertTrue(success)
        self.assertEqual(count, 100)
        
        # Procesar estancias
        success, message, count = ingestion_service.process_stays(self.test_stays_file)
        
        # Verificar que se procesaron correctamente
        self.assertTrue(success)
        self.assertGreater(count, 0)
    
    @patch('models.daily_occupancy.DailyOccupancy.get_by_date_range')
    @patch('models.daily_revenue.DailyRevenue.get_by_date_range')
    def test_kpi_analysis(self, mock_revenue, mock_occupancy):
        """
        Prueba el análisis de KPIs
        """
        # Crear datos de ocupación diaria
        occupancy_data = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Generar datos para cada tipo de habitación
            for room_type_id in range(1, 8):  # 7 tipos de habitación
                # Simular estacionalidad y tendencia
                day_of_week = current_date.weekday()
                month = current_date.month
                
                # Mayor ocupación en fin de semana y temporada alta
                weekend_factor = 1.2 if day_of_week >= 5 else 1.0
                season_factor = 1.2 if month in [1, 7, 8, 12] else 1.0 if month in [2, 3, 9, 10] else 0.8
                
                # Calcular ocupación con algo de ruido
                base_occupancy = 0.7
                occupancy = min(1.0, base_occupancy * weekend_factor * season_factor + np.random.normal(0, 0.05))
                
                # Habitaciones disponibles según tipo
                available_rooms = 10 + room_type_id * 2
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
            # Generar datos para cada tipo de habitación
            for room_type_id in range(1, 8):  # 7 tipos de habitación
                # Buscar la ocupación correspondiente
                occupancy_entry = next(
                    (o for o in occupancy_data if o['fecha'] == current_date.strftime('%Y-%m-%d') and o['room_type_id'] == room_type_id),
                    None
                )
                
                if occupancy_entry:
                    # Calcular ADR (entre 100,000 y 300,000 COP)
                    base_adr = 100000 + room_type_id * 20000
                    adr = base_adr + np.random.normal(0, 5000)
                    
                    # Calcular ingresos
                    revenue = adr * occupancy_entry['habitaciones_ocupadas']
                    
                    # Calcular RevPAR
                    revpar = revenue / occupancy_entry['habitaciones_disponibles']
                    
                    revenue_data.append({
                        'id': len(revenue_data) + 1,
                        'fecha': current_date.strftime('%Y-%m-%d'),
                        'room_type_id': room_type_id,
                        'ingresos': revenue,
                        'adr': adr,
                        'revpar': revpar
                    })
            
            current_date += timedelta(days=1)
        
        # Configurar los mocks
        from models.daily_occupancy import DailyOccupancy
        from models.daily_revenue import DailyRevenue
        
        mock_occupancy.return_value = [DailyOccupancy(**data) for data in occupancy_data]
        mock_revenue.return_value = [DailyRevenue(**data) for data in revenue_data]
        
        # Crear una instancia del calculador de KPIs
        kpi_calculator = KpiCalculator()
        
        # Calcular KPIs
        kpi_df = kpi_calculator.calculate_kpis(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d')
        )
        
        # Verificar que se calcularon correctamente
        self.assertIsNotNone(kpi_df)
        self.assertIsInstance(kpi_df, pl.DataFrame)
        self.assertGreater(len(kpi_df), 0)
        
        # Calcular KPIs agregados
        agg_kpis = kpi_calculator.calculate_aggregated_kpis(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            group_by='room_type_id'
        )
        
        # Verificar que se calcularon correctamente
        self.assertIsNotNone(agg_kpis)
        self.assertIsInstance(agg_kpis, pl.DataFrame)
        self.assertGreater(len(agg_kpis), 0)
    
    @patch('models.daily_occupancy.DailyOccupancy.get_by_date_range')
    @patch('models.room.Room.get_all')
    @patch('prophet.Prophet')
    @patch('models.forecast.Forecast.save')
    def test_forecasting(self, mock_save, mock_prophet, mock_rooms, mock_occupancy):
        """
        Prueba la generación de pronósticos
        """
        # Crear datos de ocupación diaria (similar a test_kpi_analysis)
        occupancy_data = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Generar datos para cada tipo de habitación
            for room_type_id in range(1, 8):  # 7 tipos de habitación
                # Simular estacionalidad y tendencia
                day_of_week = current_date.weekday()
                month = current_date.month
                
                # Mayor ocupación en fin de semana y temporada alta
                weekend_factor = 1.2 if day_of_week >= 5 else 1.0
                season_factor = 1.2 if month in [1, 7, 8, 12] else 1.0 if month in [2, 3, 9, 10] else 0.8
                
                # Calcular ocupación con algo de ruido
                base_occupancy = 0.7
                occupancy = min(1.0, base_occupancy * weekend_factor * season_factor + np.random.normal(0, 0.05))
                
                # Habitaciones disponibles según tipo
                available_rooms = 10 + room_type_id * 2
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
        
        # Configurar los mocks
        from models.daily_occupancy import DailyOccupancy
        from models.room import Room
        
        mock_occupancy.return_value = [DailyOccupancy(**data) for data in occupancy_data]
        mock_rooms.return_value = [
            Room(id=i, cod_hab=f'ROOM{i}', name=f'Room Type {i}', capacity=2+i, num_config=10+i*2)
            for i in range(1, 8)
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
        mock_save.return_value = 1  # ID del pronóstico guardado
        
        # Crear una instancia del servicio de previsión
        forecast_service = ForecastService()
        
        # Generar pronósticos
        forecasts = forecast_service.generate_forecast(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            self.forecast_days
        )
        
        # Verificar que se generaron correctamente
        self.assertIsNotNone(forecasts)
        self.assertIsInstance(forecasts, dict)
        self.assertGreater(len(forecasts), 0)
        
        # Guardar pronósticos
        success, message, count = forecast_service.save_forecast_to_db(forecasts)
        
        # Verificar que se guardaron correctamente
        self.assertTrue(success)
        self.assertGreater(count, 0)
    
    @patch('models.forecast.Forecast.get_by_date_range')
    @patch('models.rule.Rule.get_active_rules')
    @patch('models.recommendation.ApprovedRecommendation.save')
    def test_pricing_rules(self, mock_save, mock_rules, mock_forecasts):
        """
        Prueba la aplicación de reglas de pricing
        """
        # Crear pronósticos de prueba
        forecast_data = []
        current_date = self.end_date
        
        for i in range(self.forecast_days):
            # Generar datos para cada tipo de habitación
            for room_type_id in range(1, 8):  # 7 tipos de habitación
                # Simular estacionalidad y tendencia
                day_of_week = current_date.weekday()
                month = current_date.month
                
                # Mayor ocupación en fin de semana y temporada alta
                weekend_factor = 1.2 if day_of_week >= 5 else 1.0
                season_factor = 1.2 if month in [1, 7, 8, 12] else 1.0 if month in [2, 3, 9, 10] else 0.8
                
                # Calcular ocupación con algo de ruido
                base_occupancy = 0.7
                occupancy = min(1.0, base_occupancy * weekend_factor * season_factor + np.random.normal(0, 0.05))
                
                # Calcular ADR y RevPAR
                base_adr = 100000 + room_type_id * 20000
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
        from models.forecast import Forecast
        from models.rule import Rule
        
        mock_forecasts.return_value = [Forecast(**data) for data in forecast_data]
        mock_rules.return_value = [Rule(**data) for data in rules_data]
        
        # Configurar el mock de save
        mock_save.return_value = 1  # ID de la recomendación guardada
        
        # Crear una instancia del motor de reglas
        pricing_engine = PricingRuleEngine()
        
        # Generar recomendaciones
        success, message, recommendations = pricing_engine.generate_recommendations(
            self.end_date.strftime('%Y-%m-%d'),
            (self.end_date + timedelta(days=self.forecast_days)).strftime('%Y-%m-%d')
        )
        
        # Verificar que se generaron correctamente
        self.assertTrue(success)
        self.assertIsNotNone(recommendations)
        self.assertIn('recomendaciones', recommendations)
        
        # Guardar recomendaciones
        recommendations_df = recommendations['recomendaciones']
        success, message, count = pricing_engine.save_recommendations(recommendations_df)
        
        # Verificar que se guardaron correctamente
        self.assertTrue(success)
        self.assertGreater(count, 0)
    
    @patch('models.recommendation.ApprovedRecommendation.get_by_date_range')
    def test_tariff_export(self, mock_recommendations):
        """
        Prueba la exportación de tarifas
        """
        # Crear recomendaciones de prueba
        recommendations_data = []
        current_date = self.end_date
        
        for i in range(self.forecast_days):
            # Generar datos para cada tipo de habitación y canal
            for room_type_id in range(1, 8):  # 7 tipos de habitación
                for channel_id in range(1, 6):  # 5 canales
                    # Calcular tarifas
                    base_rate = 100000 + room_type_id * 20000
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
        
        # Configurar el mock
        from models.recommendation import ApprovedRecommendation
        
        mock_recommendations.return_value = [ApprovedRecommendation(**data) for data in recommendations_data]
        
        # Crear una instancia del exportador de tarifas
        tariff_exporter = TariffExporter()
        
        # Exportar tarifas
        success, message, filepath = tariff_exporter.export_to_excel(
            self.end_date.strftime('%Y-%m-%d'),
            (self.end_date + timedelta(days=self.forecast_days)).strftime('%Y-%m-%d')
        )
        
        # Verificar que se exportaron correctamente
        self.assertTrue(success)
        self.assertIsNotNone(filepath)
    
    @patch('services.revenue_orchestrator.RevenueOrchestrator.analyze_kpis')
    @patch('services.revenue_orchestrator.RevenueOrchestrator.generate_forecasts')
    @patch('services.revenue_orchestrator.RevenueOrchestrator.apply_pricing_rules')
    @patch('services.revenue_orchestrator.RevenueOrchestrator.export_tariffs')
    def test_full_process(self, mock_export, mock_pricing, mock_forecast, mock_kpis):
        """
        Prueba el proceso completo
        """
        # Configurar los mocks
        mock_kpis.return_value = {
            'success': True,
            'message': 'Análisis de KPIs completado con éxito',
            'data': {'kpis': pl.DataFrame()}
        }
        
        mock_forecast.return_value = {
            'success': True,
            'message': 'Se generaron y guardaron pronósticos',
            'data': {'forecast_df': pl.DataFrame()}
        }
        
        mock_pricing.return_value = {
            'success': True,
            'message': 'Se generaron recomendaciones',
            'data': {'recommendations_df': pl.DataFrame()}
        }
        
        mock_export.return_value = {
            'success': True,
            'message': 'Tarifas exportadas correctamente',
            'data': {'filepath': 'ruta/al/archivo.xlsx'}
        }
        
        # Ejecutar el proceso completo
        results = self.orchestrator.run_full_process(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            self.forecast_days,
            export_results=True
        )
        
        # Verificar que se ejecutó correctamente
        self.assertTrue(results['success'])
        self.assertIn('kpi_analysis', results['results'])
        self.assertIn('forecasts', results['results'])
        self.assertIn('pricing', results['results'])
        self.assertIn('export', results['results'])

if __name__ == "__main__":
    unittest.main()