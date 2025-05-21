#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para el servicio de previsión
"""

import unittest
import sys
import polars as pl
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.forecasting.forecast_service import ForecastService
from models.daily_occupancy import DailyOccupancy
from models.forecast import Forecast
from models.room import Room

class TestForecastService(unittest.TestCase):
    """
    Pruebas unitarias para el servicio de previsión
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear una instancia del servicio de previsión
        self.forecast_service = ForecastService()
        
        # Fechas de prueba
        self.start_date = datetime.now() - timedelta(days=365)
        self.end_date = datetime.now()
        self.forecast_days = 30
        
        # Crear datos de prueba para ocupación diaria
        self.occupancy_data = []
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
                
                self.occupancy_data.append({
                    'id': len(self.occupancy_data) + 1,
                    'fecha': current_date.strftime('%Y-%m-%d'),
                    'room_type_id': room_type_id,
                    'habitaciones_disponibles': available_rooms,
                    'habitaciones_ocupadas': occupied_rooms,
                    'ocupacion_porcentaje': occupancy * 100
                })
            
            current_date += timedelta(days=1)
    
    @patch('models.daily_occupancy.DailyOccupancy.get_by_date_range')
    @patch('models.room.Room.get_all')
    def test_prepare_data(self, mock_rooms, mock_occupancy):
        """
        Prueba la preparación de datos para el modelo de previsión
        """
        # Configurar los mocks
        mock_occupancy.return_value = [DailyOccupancy(**data) for data in self.occupancy_data]
        mock_rooms.return_value = [
            Room(id=1, cod_hab='EST', name='Estándar Triple', capacity=3, num_config=10),
            Room(id=2, cod_hab='JRS', name='Junior Suite', capacity=5, num_config=15)
        ]
        
        # Preparar datos
        prepared_data = self.forecast_service.prepare_data(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d')
        )
        
        # Verificar que se prepararon correctamente
        self.assertIsNotNone(prepared_data)
        self.assertIsInstance(prepared_data, dict)
        self.assertEqual(len(prepared_data), 2)  # Dos tipos de habitación
        
        # Verificar que cada tipo de habitación tiene los datos esperados
        for room_type_id in [1, 2]:
            self.assertIn(room_type_id, prepared_data)
            self.assertIn('prophet_df', prepared_data[room_type_id])
            self.assertIn('room_type', prepared_data[room_type_id])
            
            # Verificar el DataFrame de Prophet
            prophet_df = prepared_data[room_type_id]['prophet_df']
            self.assertIsInstance(prophet_df, pd.DataFrame)
            self.assertIn('ds', prophet_df.columns)
            self.assertIn('y', prophet_df.columns)
            
            # Verificar que las fechas están en orden
            self.assertTrue(prophet_df['ds'].is_monotonic_increasing)
    
    @patch('models.daily_occupancy.DailyOccupancy.get_by_date_range')
    @patch('models.room.Room.get_all')
    @patch('prophet.Prophet')
    def test_generate_forecast(self, mock_prophet, mock_rooms, mock_occupancy):
        """
        Prueba la generación de pronósticos
        """
        # Configurar los mocks
        mock_occupancy.return_value = [DailyOccupancy(**data) for data in self.occupancy_data]
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
        
        # Generar pronósticos
        forecasts = self.forecast_service.generate_forecast(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            self.forecast_days
        )
        
        # Verificar que se generaron correctamente
        self.assertIsNotNone(forecasts)
        self.assertIsInstance(forecasts, dict)
        self.assertEqual(len(forecasts), 2)  # Dos tipos de habitación
        
        # Verificar que cada tipo de habitación tiene los pronósticos esperados
        for room_type_id in [1, 2]:
            self.assertIn(room_type_id, forecasts)
            self.assertIn('room_type', forecasts[room_type_id])
            self.assertIn('forecast', forecasts[room_type_id])
            self.assertIn('model', forecasts[room_type_id])
            
            # Verificar el DataFrame de pronóstico
            forecast_df = forecasts[room_type_id]['forecast']
            self.assertIsInstance(forecast_df, pd.DataFrame)
            self.assertIn('ds', forecast_df.columns)
            self.assertIn('yhat', forecast_df.columns)
            self.assertIn('yhat_lower', forecast_df.columns)
            self.assertIn('yhat_upper', forecast_df.columns)
            
            # Verificar que los valores están entre 0 y 1
            self.assertTrue(all(0 <= y <= 1 for y in forecast_df['yhat']))
            self.assertTrue(all(0 <= y <= 1 for y in forecast_df['yhat_lower']))
            self.assertTrue(all(0 <= y <= 1 for y in forecast_df['yhat_upper']))
    
    @patch('models.forecast.Forecast.get_by_date_and_room_type')
    @patch('models.forecast.Forecast.save')
    def test_save_forecast_to_db(self, mock_save, mock_get):
        """
        Prueba el guardado de pronósticos en la base de datos
        """
        # Configurar los mocks
        mock_get.return_value = None  # No existen pronósticos previos
        mock_save.return_value = 1  # ID del pronóstico guardado
        
        # Crear datos de pronóstico simulados
        room_types = {
            1: Room(id=1, cod_hab='EST', name='Estándar Triple', capacity=3, num_config=10),
            2: Room(id=2, cod_hab='JRS', name='Junior Suite', capacity=5, num_config=15)
        }
        
        future_dates = pd.date_range(start=self.end_date, periods=self.forecast_days)
        forecasts = {}
        
        for room_type_id, room in room_types.items():
            forecast_df = pd.DataFrame({
                'ds': future_dates,
                'yhat': np.random.uniform(0.6, 0.8, size=len(future_dates)),
                'yhat_lower': np.random.uniform(0.5, 0.6, size=len(future_dates)),
                'yhat_upper': np.random.uniform(0.8, 0.9, size=len(future_dates))
            })
            
            forecasts[room_type_id] = {
                'room_type': room,
                'forecast': forecast_df,
                'model': MagicMock()
            }
        
        # Guardar pronósticos
        success, message, count = self.forecast_service.save_forecast_to_db(forecasts)
        
        # Verificar que se guardaron correctamente
        self.assertTrue(success)
        self.assertEqual(count, self.forecast_days * len(room_types))  # Días * tipos de habitación
        
        # Verificar que se llamó al método save para cada pronóstico
        self.assertEqual(mock_save.call_count, self.forecast_days * len(room_types))
    
    @patch('models.forecast.Forecast.get_by_date_range')
    def test_load_forecast_from_db(self, mock_get):
        """
        Prueba la carga de pronósticos desde la base de datos
        """
        # Crear datos de pronóstico simulados
        forecast_data = []
        current_date = self.end_date
        
        for i in range(self.forecast_days):
            # Generar datos para dos tipos de habitación
            for room_type_id in [1, 2]:
                forecast_data.append({
                    'id': len(forecast_data) + 1,
                    'fecha': current_date.strftime('%Y-%m-%d'),
                    'room_type_id': room_type_id,
                    'ocupacion_prevista': 70.0 + np.random.normal(0, 5),
                    'adr_previsto': 100.0 + np.random.normal(0, 10),
                    'revpar_previsto': 70.0 + np.random.normal(0, 7),
                    'ajustado_manualmente': False
                })
            
            current_date += timedelta(days=1)
        
        # Configurar el mock
        mock_get.return_value = [Forecast(**data) for data in forecast_data]
        
        # Cargar pronósticos
        forecast_df = self.forecast_service.load_forecast_from_db(
            self.end_date.strftime('%Y-%m-%d'),
            (self.end_date + timedelta(days=self.forecast_days)).strftime('%Y-%m-%d')
        )
        
        # Verificar que se cargaron correctamente
        self.assertIsNotNone(forecast_df)
        self.assertIsInstance(forecast_df, pl.DataFrame)
        self.assertEqual(len(forecast_df), self.forecast_days * 2)  # Días * tipos de habitación
        
        # Verificar que contiene las columnas esperadas
        expected_columns = ['fecha', 'room_type_id', 'ocupacion_prevista', 'adr_previsto', 'revpar_previsto']
        
        for col in expected_columns:
            self.assertIn(col, forecast_df.columns)
    
    @patch('models.forecast.Forecast.get_by_date_range')
    @patch('services.analysis.kpi_calculator.KpiCalculator.calculate_kpis')
    def test_update_forecast_kpis(self, mock_kpis, mock_get_forecast):
        """
        Prueba la actualización de KPIs de pronósticos
        """
        # Crear datos de pronóstico simulados
        forecast_data = []
        current_date = self.end_date
        
        for i in range(self.forecast_days):
            # Generar datos para dos tipos de habitación
            for room_type_id in [1, 2]:
                forecast_data.append({
                    'id': len(forecast_data) + 1,
                    'fecha': current_date.strftime('%Y-%m-%d'),
                    'room_type_id': room_type_id,
                    'ocupacion_prevista': 70.0,
                    'adr_previsto': 0.0,  # Sin ADR inicial
                    'revpar_previsto': 0.0,  # Sin RevPAR inicial
                    'ajustado_manualmente': False
                })
            
            current_date += timedelta(days=1)
        
        # Configurar los mocks
        mock_get_forecast.return_value = [Forecast(**data) for data in forecast_data]
        
        # Crear datos de KPIs históricos simulados
        historical_kpis = pl.DataFrame({
            'fecha': [(self.end_date - timedelta(days=365 + i)).strftime('%Y-%m-%d') for i in range(30)],
            'room_type_id': [1 if i % 2 == 0 else 2 for i in range(30)],
            'adr': [100.0 + np.random.normal(0, 10) for _ in range(30)],
            'revpar': [70.0 + np.random.normal(0, 7) for _ in range(30)]
        })
        
        mock_kpis.return_value = historical_kpis
        
        # Actualizar KPIs de pronósticos
        success, message, count = self.forecast_service.update_forecast_kpis(
            self.end_date.strftime('%Y-%m-%d'),
            (self.end_date + timedelta(days=self.forecast_days)).strftime('%Y-%m-%d')
        )
        
        # Verificar que se actualizaron correctamente
        self.assertTrue(success)
        self.assertEqual(count, len(forecast_data))

if __name__ == "__main__":
    unittest.main()