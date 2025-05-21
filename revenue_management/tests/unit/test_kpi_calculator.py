#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para el calculador de KPIs
"""

import unittest
import sys
import polars as pl
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.analysis.kpi_calculator import KpiCalculator
from models.daily_occupancy import DailyOccupancy
from models.daily_revenue import DailyRevenue

class TestKpiCalculator(unittest.TestCase):
    """
    Pruebas unitarias para el calculador de KPIs
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear una instancia del calculador de KPIs
        self.kpi_calculator = KpiCalculator()
        
        # Fechas de prueba
        self.start_date = datetime.now() - timedelta(days=30)
        self.end_date = datetime.now()
        
        # Crear datos de prueba para ocupación diaria
        self.occupancy_data = [
            {
                'id': 1,
                'fecha': (self.start_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'room_type_id': 1,
                'habitaciones_disponibles': 10,
                'habitaciones_ocupadas': 8 if i % 2 == 0 else 6,
                'ocupacion_porcentaje': 80.0 if i % 2 == 0 else 60.0
            }
            for i in range(30)
        ]
        
        # Crear datos de prueba para ingresos diarios
        self.revenue_data = [
            {
                'id': 1,
                'fecha': (self.start_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'room_type_id': 1,
                'ingresos': 800.0 if i % 2 == 0 else 600.0,
                'adr': 100.0,
                'revpar': 80.0 if i % 2 == 0 else 60.0
            }
            for i in range(30)
        ]
    
    @patch('models.daily_occupancy.DailyOccupancy.get_by_date_range')
    @patch('models.daily_revenue.DailyRevenue.get_by_date_range')
    def test_calculate_kpis(self, mock_revenue, mock_occupancy):
        """
        Prueba el cálculo de KPIs
        """
        # Configurar los mocks
        mock_occupancy.return_value = [DailyOccupancy(**data) for data in self.occupancy_data]
        mock_revenue.return_value = [DailyRevenue(**data) for data in self.revenue_data]
        
        # Calcular KPIs
        kpi_df = self.kpi_calculator.calculate_kpis(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            room_type_id=1
        )
        
        # Verificar que se calcularon correctamente
        self.assertIsNotNone(kpi_df)
        self.assertIsInstance(kpi_df, pl.DataFrame)
        self.assertEqual(len(kpi_df), 30)
        
        # Verificar que contiene las columnas esperadas
        expected_columns = ['fecha', 'room_type_id', 'habitaciones_disponibles', 
                           'habitaciones_ocupadas', 'ocupacion_porcentaje', 
                           'ingresos', 'adr', 'revpar']
        
        for col in expected_columns:
            self.assertIn(col, kpi_df.columns)
    
    @patch('models.daily_occupancy.DailyOccupancy.get_by_date_range')
    @patch('models.daily_revenue.DailyRevenue.get_by_date_range')
    def test_calculate_aggregated_kpis(self, mock_revenue, mock_occupancy):
        """
        Prueba el cálculo de KPIs agregados
        """
        # Configurar los mocks
        mock_occupancy.return_value = [DailyOccupancy(**data) for data in self.occupancy_data]
        mock_revenue.return_value = [DailyRevenue(**data) for data in self.revenue_data]
        
        # Calcular KPIs agregados por tipo de habitación
        agg_kpis = self.kpi_calculator.calculate_aggregated_kpis(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            group_by='room_type_id'
        )
        
        # Verificar que se calcularon correctamente
        self.assertIsNotNone(agg_kpis)
        self.assertIsInstance(agg_kpis, pl.DataFrame)
        
        # Verificar que contiene las columnas esperadas
        expected_columns = ['room_type_id', 'ocupacion_promedio', 'adr_promedio', 
                           'revpar_promedio', 'ingresos_totales']
        
        for col in expected_columns:
            self.assertIn(col, agg_kpis.columns)
        
        # Verificar que los valores agregados son correctos
        self.assertAlmostEqual(agg_kpis[0, 'ocupacion_promedio'], 70.0)  # Promedio de 80% y 60%
        self.assertAlmostEqual(agg_kpis[0, 'adr_promedio'], 100.0)
        self.assertAlmostEqual(agg_kpis[0, 'revpar_promedio'], 70.0)  # Promedio de 80 y 60
    
    @patch('models.daily_occupancy.DailyOccupancy.get_by_date_range')
    def test_analyze_occupancy_patterns(self, mock_occupancy):
        """
        Prueba el análisis de patrones de ocupación
        """
        # Configurar el mock
        mock_occupancy.return_value = [DailyOccupancy(**data) for data in self.occupancy_data]
        
        # Analizar patrones de ocupación
        patterns = self.kpi_calculator.analyze_occupancy_patterns(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            room_type_id=1
        )
        
        # Verificar que se analizaron correctamente
        self.assertIsNotNone(patterns)
        self.assertIsInstance(patterns, dict)
        
        # Verificar que contiene los patrones esperados
        expected_patterns = ['ocupacion_por_dia_semana', 'ocupacion_por_mes', 'tendencia_ocupacion']
        
        for pattern in expected_patterns:
            self.assertIn(pattern, patterns)
            self.assertIsInstance(patterns[pattern], pl.DataFrame)
    
    @patch('models.daily_occupancy.DailyOccupancy.get_by_date_range')
    @patch('models.daily_revenue.DailyRevenue.get_by_date_range')
    def test_calculate_yoy_comparison(self, mock_revenue, mock_occupancy):
        """
        Prueba la comparación año contra año
        """
        # Crear datos para el año actual
        current_year_data = self.occupancy_data.copy()
        
        # Crear datos para el año anterior (mismas fechas, año anterior)
        previous_year_data = [
            {
                'id': i + 100,
                'fecha': (datetime.strptime(data['fecha'], '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d'),
                'room_type_id': data['room_type_id'],
                'habitaciones_disponibles': data['habitaciones_disponibles'],
                'habitaciones_ocupadas': data['habitaciones_ocupadas'] - 1,  # Menos ocupación el año anterior
                'ocupacion_porcentaje': data['ocupacion_porcentaje'] - 10.0  # Menos ocupación el año anterior
            }
            for i, data in enumerate(current_year_data)
        ]
        
        # Configurar los mocks para devolver ambos conjuntos de datos
        mock_occupancy.side_effect = [
            [DailyOccupancy(**data) for data in current_year_data],  # Datos actuales
            [DailyOccupancy(**data) for data in previous_year_data]  # Datos del año anterior
        ]
        
        # Crear datos de ingresos para el año actual
        current_year_revenue = self.revenue_data.copy()
        
        # Crear datos de ingresos para el año anterior
        previous_year_revenue = [
            {
                'id': i + 100,
                'fecha': (datetime.strptime(data['fecha'], '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d'),
                'room_type_id': data['room_type_id'],
                'ingresos': data['ingresos'] - 100.0,  # Menos ingresos el año anterior
                'adr': data['adr'] - 10.0,  # Menor ADR el año anterior
                'revpar': data['revpar'] - 15.0  # Menor RevPAR el año anterior
            }
            for i, data in enumerate(current_year_revenue)
        ]
        
        # Configurar los mocks para devolver ambos conjuntos de datos
        mock_revenue.side_effect = [
            [DailyRevenue(**data) for data in current_year_revenue],  # Datos actuales
            [DailyRevenue(**data) for data in previous_year_revenue]  # Datos del año anterior
        ]
        
        # Calcular comparación YoY
        yoy_comparison = self.kpi_calculator.calculate_yoy_comparison(
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            room_type_id=1
        )
        
        # Verificar que se calculó correctamente
        self.assertIsNotNone(yoy_comparison)
        self.assertIsInstance(yoy_comparison, dict)
        
        # Verificar que contiene las comparaciones esperadas
        expected_comparisons = ['ocupacion', 'adr', 'revpar', 'ingresos']
        
        for comp in expected_comparisons:
            self.assertIn(comp, yoy_comparison)
            
            # Verificar que cada comparación tiene los valores actuales, anteriores y variación
            self.assertIn('actual', yoy_comparison[comp])
            self.assertIn('anterior', yoy_comparison[comp])
            self.assertIn('variacion', yoy_comparison[comp])
            self.assertIn('variacion_porcentaje', yoy_comparison[comp])
            
            # Verificar que la variación es positiva (actual > anterior)
            self.assertGreater(yoy_comparison[comp]['variacion'], 0)
            self.assertGreater(yoy_comparison[comp]['variacion_porcentaje'], 0)

if __name__ == "__main__":
    unittest.main()