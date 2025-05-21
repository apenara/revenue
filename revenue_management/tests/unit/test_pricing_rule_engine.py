#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para el motor de reglas de pricing
"""

import unittest
import sys
import polars as pl
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.pricing.pricing_rule_engine import PricingRuleEngine
from models.rule import Rule
from models.forecast import Forecast
from models.recommendation import ApprovedRecommendation
from config import config

class TestPricingRuleEngine(unittest.TestCase):
    """
    Pruebas unitarias para el motor de reglas de pricing
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear una instancia del motor de reglas
        self.pricing_engine = PricingRuleEngine()
        
        # Fechas de prueba
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=7)
        
        # Crear reglas de prueba
        self.test_rules = [
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
            },
            {
                'id': 3,
                'nombre': 'Regla de Canal',
                'descripcion': 'Ajusta tarifas según el canal de distribución',
                'parametros': {
                    'tipo': 'canal',
                    'factores': [
                        {'canal': 'Directo', 'factor': 1.0},
                        {'canal': 'Booking.com', 'factor': 1.15},
                        {'canal': 'Expedia', 'factor': 1.18}
                    ]
                },
                'prioridad': 3,
                'activa': True
            },
            {
                'id': 4,
                'nombre': 'Regla de Día de Semana',
                'descripcion': 'Ajusta tarifas según el día de la semana',
                'parametros': {
                    'tipo': 'dia_semana',
                    'factores': {
                        '0': 0.9,  # Lunes
                        '1': 0.9,  # Martes
                        '2': 0.9,  # Miércoles
                        '3': 0.95, # Jueves
                        '4': 1.1,  # Viernes
                        '5': 1.2,  # Sábado
                        '6': 1.0   # Domingo
                    }
                },
                'prioridad': 4,
                'activa': True
            }
        ]
        
        # Crear pronósticos de prueba
        self.test_forecasts = []
        current_date = self.start_date
        
        for i in range(7):  # Una semana
            # Determinar día de la semana y mes
            day_of_week = current_date.weekday()
            month = current_date.month
            
            # Determinar temporada
            season = "Alta" if month in [1, 7, 8, 12] else "Media" if month in [2, 3, 9, 10] else "Baja"
            
            # Generar datos para dos tipos de habitación
            for room_type_id in [1, 2]:
                # Ocupación más alta en fin de semana
                occupancy = 85.0 if day_of_week >= 5 else 65.0
                
                self.test_forecasts.append({
                    'id': len(self.test_forecasts) + 1,
                    'fecha': current_date.strftime('%Y-%m-%d'),
                    'room_type_id': room_type_id,
                    'ocupacion_prevista': occupancy,
                    'adr_previsto': 100.0 if room_type_id == 1 else 150.0,
                    'revpar_previsto': occupancy * (100.0 if room_type_id == 1 else 150.0) / 100.0,
                    'ajustado_manualmente': False
                })
            
            current_date += timedelta(days=1)
    
    @patch('models.rule.Rule.get_active_rules')
    def test_load_rules(self, mock_rules):
        """
        Prueba la carga de reglas
        """
        # Configurar el mock
        mock_rules.return_value = [Rule(**rule) for rule in self.test_rules]
        
        # Cargar reglas
        rules = self.pricing_engine._load_rules()
        
        # Verificar que se cargaron correctamente
        self.assertIsNotNone(rules)
        self.assertEqual(len(rules), 4)
        
        # Verificar que las reglas están ordenadas por prioridad
        priorities = [rule.prioridad for rule in rules]
        self.assertEqual(priorities, sorted(priorities))
    
    @patch('models.rule.Rule.get_active_rules')
    @patch('models.rule.Rule.save')
    def test_create_default_rules(self, mock_save, mock_rules):
        """
        Prueba la creación de reglas por defecto
        """
        # Configurar el mock para que no haya reglas activas
        mock_rules.return_value = []
        
        # Crear reglas por defecto
        self.pricing_engine._create_default_rules()
        
        # Verificar que se llamó al método save para cada regla
        self.assertEqual(mock_save.call_count, 4)  # 4 reglas por defecto
    
    @patch('models.forecast.Forecast.get_by_date_range')
    def test_apply_rules(self, mock_forecasts):
        """
        Prueba la aplicación de reglas
        """
        # Configurar el mock
        mock_forecasts.return_value = [Forecast(**forecast) for forecast in self.test_forecasts]
        
        # Configurar reglas de prueba
        self.pricing_engine.rules = [Rule(**rule) for rule in self.test_rules]
        
        # Aplicar reglas
        recommendations_df = self.pricing_engine.apply_rules(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d')
        )
        
        # Verificar que se generaron recomendaciones
        self.assertIsNotNone(recommendations_df)
        self.assertIsInstance(recommendations_df, pl.DataFrame)
        
        # Verificar que contiene las columnas esperadas
        expected_columns = ['fecha', 'room_type_id', 'canal', 'temporada', 'dia_semana',
                           'factor_temporada', 'factor_ocupacion', 'factor_canal', 
                           'factor_dia_semana', 'factor_total', 'tarifa_base', 'tarifa_recomendada']
        
        for col in expected_columns:
            self.assertIn(col, recommendations_df.columns)
        
        # Verificar que se generaron recomendaciones para todos los días y tipos de habitación
        self.assertEqual(len(recommendations_df), 7 * 2 * len(self.pricing_engine.channels))  # Días * tipos de habitación * canales
    
    def test_prepare_data_for_rules(self):
        """
        Prueba la preparación de datos para aplicar reglas
        """
        # Crear un DataFrame de pronósticos
        forecast_df = pl.DataFrame([
            {
                'id': 1,
                'fecha': '2025-01-01',
                'room_type_id': 1,
                'ocupacion_prevista': 80.0,
                'adr_previsto': 100.0,
                'revpar_previsto': 80.0
            },
            {
                'id': 2,
                'fecha': '2025-01-01',
                'room_type_id': 2,
                'ocupacion_prevista': 70.0,
                'adr_previsto': 150.0,
                'revpar_previsto': 105.0
            }
        ])
        
        # Preparar datos
        prepared_df = self.pricing_engine._prepare_data_for_rules(forecast_df)
        
        # Verificar que se prepararon correctamente
        self.assertIsNotNone(prepared_df)
        self.assertIsInstance(prepared_df, pl.DataFrame)
        
        # Verificar que contiene las columnas esperadas
        expected_columns = ['fecha', 'room_type_id', 'ocupacion_prevista', 'adr_previsto',
                           'canal', 'comision', 'dia_semana', 'mes', 'temporada',
                           'factor_temporada', 'factor_ocupacion', 'factor_canal', 
                           'factor_dia_semana', 'factor_total', 'tarifa_base', 'tarifa_recomendada']
        
        for col in expected_columns:
            self.assertIn(col, prepared_df.columns)
        
        # Verificar que se generaron filas para cada canal
        self.assertEqual(len(prepared_df), 2 * len(self.pricing_engine.channels))  # Tipos de habitación * canales
    
    def test_apply_season_rule(self):
        """
        Prueba la aplicación de la regla de temporada
        """
        # Crear un DataFrame de prueba
        test_df = pl.DataFrame([
            {'temporada': 'Alta', 'tarifa_base': 100.0, 'factor_temporada': 1.0},
            {'temporada': 'Media', 'tarifa_base': 100.0, 'factor_temporada': 1.0},
            {'temporada': 'Baja', 'tarifa_base': 100.0, 'factor_temporada': 1.0}
        ])
        
        # Crear regla de temporada
        season_rule = Rule(**self.test_rules[0])
        
        # Aplicar regla
        result_df = self.pricing_engine._apply_season_rule(test_df, season_rule)
        
        # Verificar que se aplicó correctamente
        self.assertEqual(result_df[0, 'factor_temporada'], 1.2)  # Alta
        self.assertEqual(result_df[1, 'factor_temporada'], 1.0)  # Media
        self.assertEqual(result_df[2, 'factor_temporada'], 0.9)  # Baja
    
    def test_apply_occupancy_rule(self):
        """
        Prueba la aplicación de la regla de ocupación
        """
        # Crear un DataFrame de prueba
        test_df = pl.DataFrame([
            {'ocupacion_prevista': 30.0, 'factor_ocupacion': 1.0},
            {'ocupacion_prevista': 60.0, 'factor_ocupacion': 1.0},
            {'ocupacion_prevista': 90.0, 'factor_ocupacion': 1.0}
        ])
        
        # Crear regla de ocupación
        occupancy_rule = Rule(**self.test_rules[1])
        
        # Aplicar regla
        result_df = self.pricing_engine._apply_occupancy_rule(test_df, occupancy_rule)
        
        # Verificar que se aplicó correctamente
        self.assertEqual(result_df[0, 'factor_ocupacion'], 0.9)  # Baja ocupación
        self.assertEqual(result_df[1, 'factor_ocupacion'], 1.0)  # Media ocupación
        self.assertEqual(result_df[2, 'factor_ocupacion'], 1.15)  # Alta ocupación
    
    def test_apply_channel_rule(self):
        """
        Prueba la aplicación de la regla de canal
        """
        # Crear un DataFrame de prueba
        test_df = pl.DataFrame([
            {'canal': 'Directo', 'factor_canal': 1.0},
            {'canal': 'Booking.com', 'factor_canal': 1.0},
            {'canal': 'Expedia', 'factor_canal': 1.0}
        ])
        
        # Crear regla de canal
        channel_rule = Rule(**self.test_rules[2])
        
        # Aplicar regla
        result_df = self.pricing_engine._apply_channel_rule(test_df, channel_rule)
        
        # Verificar que se aplicó correctamente
        self.assertEqual(result_df[0, 'factor_canal'], 1.0)  # Directo
        self.assertEqual(result_df[1, 'factor_canal'], 1.15)  # Booking.com
        self.assertEqual(result_df[2, 'factor_canal'], 1.18)  # Expedia
    
    def test_apply_weekday_rule(self):
        """
        Prueba la aplicación de la regla de día de la semana
        """
        # Crear un DataFrame de prueba
        test_df = pl.DataFrame([
            {'dia_semana': 1, 'factor_dia_semana': 1.0},  # Martes
            {'dia_semana': 4, 'factor_dia_semana': 1.0},  # Viernes
            {'dia_semana': 5, 'factor_dia_semana': 1.0}   # Sábado
        ])
        
        # Crear regla de día de la semana
        weekday_rule = Rule(**self.test_rules[3])
        
        # Aplicar regla
        result_df = self.pricing_engine._apply_weekday_rule(test_df, weekday_rule)
        
        # Verificar que se aplicó correctamente
        self.assertEqual(result_df[0, 'factor_dia_semana'], 0.9)  # Martes
        self.assertEqual(result_df[1, 'factor_dia_semana'], 1.1)  # Viernes
        self.assertEqual(result_df[2, 'factor_dia_semana'], 1.2)  # Sábado
    
    def test_calculate_final_rates(self):
        """
        Prueba el cálculo de tarifas finales
        """
        # Crear un DataFrame de prueba
        test_df = pl.DataFrame([
            {
                'tarifa_base': 100.0,
                'factor_temporada': 1.2,
                'factor_ocupacion': 1.15,
                'factor_canal': 1.0,
                'factor_dia_semana': 1.2,
                'factor_total': 0.0,
                'tarifa_recomendada': 0.0,
                'canal': 'Directo'
            },
            {
                'tarifa_base': 100.0,
                'factor_temporada': 0.9,
                'factor_ocupacion': 0.9,
                'factor_canal': 1.15,
                'factor_dia_semana': 0.9,
                'factor_total': 0.0,
                'tarifa_recomendada': 0.0,
                'canal': 'Booking.com'
            }
        ])
        
        # Calcular tarifas finales
        result_df = self.pricing_engine._calculate_final_rates(test_df)
        
        # Verificar que se calcularon correctamente
        # Caso 1: 100 * 1.2 * 1.15 * 1.0 * 1.2 = 165.6
        # Caso 2: 100 * 0.9 * 0.9 * 1.15 * 0.9 = 84.0
        
        self.assertAlmostEqual(result_df[0, 'factor_total'], 1.2 * 1.15 * 1.0 * 1.2)
        self.assertAlmostEqual(result_df[1, 'factor_total'], 0.9 * 0.9 * 1.15 * 0.9)
        
        # Verificar que las tarifas recomendadas se redondearon a enteros
        self.assertTrue(isinstance(result_df[0, 'tarifa_recomendada'], int))
        self.assertTrue(isinstance(result_df[1, 'tarifa_recomendada'], int))
        
        # Verificar que se aplicó el descuento para canal directo
        direct_discount = self.pricing_engine.pricing_config.get("direct_channel_discount", 0.05)
        expected_direct_price = round(test_df[0, 'tarifa_base'] * result_df[0, 'factor_total'] * (1 - direct_discount))
        
        self.assertEqual(result_df[0, 'tarifa_recomendada'], expected_direct_price)
    
    @patch('models.forecast.Forecast.get_by_date_range')
    def test_generate_recommendations(self, mock_forecasts):
        """
        Prueba la generación de recomendaciones
        """
        # Configurar el mock
        mock_forecasts.return_value = [Forecast(**forecast) for forecast in self.test_forecasts]
        
        # Configurar reglas de prueba
        self.pricing_engine.rules = [Rule(**rule) for rule in self.test_rules]
        
        # Generar recomendaciones
        success, message, recommendations = self.pricing_engine.generate_recommendations(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d')
        )
        
        # Verificar que se generaron correctamente
        self.assertTrue(success)
        self.assertIsNotNone(recommendations)
        self.assertIn('recomendaciones', recommendations)
        self.assertIn('periodo', recommendations)
        self.assertIn('generado_en', recommendations)
        
        # Verificar que las recomendaciones son un DataFrame
        recommendations_df = recommendations['recomendaciones']
        self.assertIsInstance(recommendations_df, pl.DataFrame)
        
        # Verificar que contiene las columnas esperadas
        expected_columns = ['fecha', 'room_type_id', 'canal', 'tarifa_base', 'tarifa_recomendada']
        
        for col in expected_columns:
            self.assertIn(col, recommendations_df.columns)
    
    @patch('models.recommendation.ApprovedRecommendation.get_by_date_room_channel')
    @patch('models.recommendation.ApprovedRecommendation.save')
    def test_save_recommendations(self, mock_save, mock_get):
        """
        Prueba el guardado de recomendaciones
        """
        # Configurar el mock para que no existan recomendaciones previas
        mock_get.return_value = None
        mock_save.return_value = 1  # ID de la recomendación guardada
        
        # Crear un DataFrame de recomendaciones
        recommendations_df = pl.DataFrame([
            {
                'fecha': '2025-01-01',
                'room_type_id': 1,
                'canal': 'Directo',
                'tarifa_base': 100.0,
                'tarifa_recomendada': 110.0
            },
            {
                'fecha': '2025-01-01',
                'room_type_id': 1,
                'canal': 'Booking.com',
                'tarifa_base': 100.0,
                'tarifa_recomendada': 120.0
            }
        ])
        
        # Guardar recomendaciones
        success, message, count = self.pricing_engine.save_recommendations(recommendations_df)
        
        # Verificar que se guardaron correctamente
        self.assertTrue(success)
        self.assertEqual(count, 2)
        
        # Verificar que se llamó al método save para cada recomendación
        self.assertEqual(mock_save.call_count, 2)
    
    def test_get_channel_id(self):
        """
        Prueba la obtención del ID de un canal
        """
        # Probar con canales existentes
        self.assertEqual(self.pricing_engine._get_channel_id('Directo'), 1)
        self.assertEqual(self.pricing_engine._get_channel_id('Booking.com'), 2)
        
        # Probar con un canal inexistente
        self.assertEqual(self.pricing_engine._get_channel_id('Canal Inexistente'), 1)  # Debe devolver el canal directo por defecto

if __name__ == "__main__":
    unittest.main()