#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para el servicio de ingesta de datos
"""

import unittest
import os
import sys
import tempfile
import pandas as pd
import polars as pl
from pathlib import Path
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.data_ingestion.excel_reader import ExcelReader
from services.data_ingestion.data_cleaner import DataCleaner
from services.data_ingestion.data_mapper import DataMapper
from services.data_ingestion.data_ingestion_service import DataIngestionService
from config import config

class TestExcelReader(unittest.TestCase):
    """
    Pruebas unitarias para el lector de archivos Excel
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear un archivo Excel temporal para las pruebas
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = Path(self.temp_dir.name) / "test_data.xlsx"
        
        # Crear un DataFrame de prueba
        self.test_data = pd.DataFrame({
            'fecha': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'habitacion': ['101', '102', '103'],
            'tarifa': [100.0, 150.0, 200.0],
            'ocupacion': [1, 1, 0]
        })
        
        # Guardar el DataFrame en un archivo Excel
        self.test_data.to_excel(self.test_file_path, sheet_name='Reservas', index=False)
        
        # Crear una instancia del lector
        self.excel_reader = ExcelReader()
    
    def tearDown(self):
        """
        Limpieza después de las pruebas
        """
        # Eliminar el directorio temporal
        self.temp_dir.cleanup()
    
    def test_read_excel_file(self):
        """
        Prueba la lectura de un archivo Excel
        """
        # Leer el archivo Excel
        df = self.excel_reader.read_excel_file(self.test_file_path, sheet_name='Reservas')
        
        # Verificar que se leyó correctamente
        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertListEqual(list(df.columns), ['fecha', 'habitacion', 'tarifa', 'ocupacion'])
    
    def test_read_excel_file_with_sheet_detection(self):
        """
        Prueba la detección automática de hojas
        """
        # Configurar nombres de hojas para detección
        sheet_names = ['Reservas', 'Bookings', 'Reservations']
        
        # Leer el archivo Excel con detección automática
        df = self.excel_reader.read_excel_file(self.test_file_path, sheet_names=sheet_names)
        
        # Verificar que se leyó correctamente
        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
    
    def test_read_excel_file_invalid_sheet(self):
        """
        Prueba la lectura de un archivo Excel con una hoja inválida
        """
        # Intentar leer una hoja que no existe
        with self.assertRaises(ValueError):
            self.excel_reader.read_excel_file(self.test_file_path, sheet_name='InvalidSheet')
    
    def test_convert_to_polars(self):
        """
        Prueba la conversión de un DataFrame de pandas a polars
        """
        # Leer el archivo Excel
        pandas_df = self.excel_reader.read_excel_file(self.test_file_path, sheet_name='Reservas')
        
        # Convertir a polars
        polars_df = self.excel_reader.convert_to_polars(pandas_df)
        
        # Verificar que se convirtió correctamente
        self.assertIsNotNone(polars_df)
        self.assertIsInstance(polars_df, pl.DataFrame)
        self.assertEqual(len(polars_df), 3)
        self.assertListEqual(polars_df.columns, ['fecha', 'habitacion', 'tarifa', 'ocupacion'])


class TestDataCleaner(unittest.TestCase):
    """
    Pruebas unitarias para el limpiador de datos
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear un DataFrame de prueba
        self.test_data = pl.DataFrame({
            'fecha': ['2025-01-01', '2025-01-02', '2025-01-03', None],
            'habitacion': ['101', '102', '103', '104'],
            'tarifa': [100.0, 150.0, 200.0, None],
            'ocupacion': [1, 1, 0, None]
        })
        
        # Crear una instancia del limpiador
        self.data_cleaner = DataCleaner()
    
    def test_clean_dates(self):
        """
        Prueba la limpieza de fechas
        """
        # Limpiar fechas
        cleaned_df = self.data_cleaner.clean_dates(self.test_data, 'fecha')
        
        # Verificar que se limpiaron correctamente
        self.assertEqual(len(cleaned_df), 3)  # Se eliminó la fila con fecha None
        self.assertTrue(all(isinstance(date, pl.Date) for date in cleaned_df['fecha']))
    
    def test_clean_numeric_values(self):
        """
        Prueba la limpieza de valores numéricos
        """
        # Limpiar valores numéricos
        cleaned_df = self.data_cleaner.clean_numeric_values(self.test_data, 'tarifa', 'float')
        
        # Verificar que se limpiaron correctamente
        self.assertEqual(len(cleaned_df), 3)  # Se eliminó la fila con tarifa None
        self.assertTrue(all(isinstance(value, float) for value in cleaned_df['tarifa']))
    
    def test_remove_duplicates(self):
        """
        Prueba la eliminación de duplicados
        """
        # Crear un DataFrame con duplicados
        df_with_duplicates = pl.concat([self.test_data, self.test_data.slice(0, 2)])
        
        # Eliminar duplicados
        cleaned_df = self.data_cleaner.remove_duplicates(df_with_duplicates)
        
        # Verificar que se eliminaron los duplicados
        self.assertEqual(len(cleaned_df), 4)  # 4 filas únicas


class TestDataMapper(unittest.TestCase):
    """
    Pruebas unitarias para el mapeador de datos
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear un DataFrame de prueba
        self.test_data = pl.DataFrame({
            'fecha_reserva': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'codigo_habitacion': ['EST', 'JRS', 'ESC'],
            'tarifa_neta': [100.0, 150.0, 200.0],
            'canal': ['Directo', 'Booking.com', 'Expedia']
        })
        
        # Crear una instancia del mapeador
        self.data_mapper = DataMapper()
    
    def test_map_room_types(self):
        """
        Prueba el mapeo de tipos de habitación
        """
        # Definir mapeo de tipos de habitación
        room_type_mapping = {
            'EST': 'Estándar Triple',
            'JRS': 'Junior Suite',
            'ESC': 'Estándar Cuádruple'
        }
        
        # Mapear tipos de habitación
        mapped_df = self.data_mapper.map_room_types(self.test_data, 'codigo_habitacion', room_type_mapping)
        
        # Verificar que se mapearon correctamente
        self.assertTrue('tipo_habitacion' in mapped_df.columns)
        self.assertEqual(mapped_df['tipo_habitacion'][0], 'Estándar Triple')
        self.assertEqual(mapped_df['tipo_habitacion'][1], 'Junior Suite')
        self.assertEqual(mapped_df['tipo_habitacion'][2], 'Estándar Cuádruple')
    
    def test_map_channels(self):
        """
        Prueba el mapeo de canales
        """
        # Definir mapeo de canales
        channel_mapping = {
            'Directo': 'Directo',
            'Booking.com': 'OTA',
            'Expedia': 'OTA'
        }
        
        # Mapear canales
        mapped_df = self.data_mapper.map_channels(self.test_data, 'canal', channel_mapping)
        
        # Verificar que se mapearon correctamente
        self.assertTrue('tipo_canal' in mapped_df.columns)
        self.assertEqual(mapped_df['tipo_canal'][0], 'Directo')
        self.assertEqual(mapped_df['tipo_canal'][1], 'OTA')
        self.assertEqual(mapped_df['tipo_canal'][2], 'OTA')


class TestDataIngestionService(unittest.TestCase):
    """
    Pruebas unitarias para el servicio de ingesta de datos
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear un archivo Excel temporal para las pruebas
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = Path(self.temp_dir.name) / "test_bookings.xlsx"
        
        # Crear un DataFrame de prueba para reservas
        self.test_bookings = pd.DataFrame({
            'registro_num': ['R001', 'R002', 'R003'],
            'fecha_reserva': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'fecha_llegada': ['2025-02-01', '2025-02-02', '2025-02-03'],
            'fecha_salida': ['2025-02-03', '2025-02-05', '2025-02-06'],
            'noches': [2, 3, 3],
            'cod_hab': ['EST', 'JRS', 'ESC'],
            'tipo_habitacion': ['Estándar Triple', 'Junior Suite', 'Estándar Cuádruple'],
            'tarifa_neta': [200.0, 450.0, 600.0],
            'canal_distribucion': ['Directo', 'Booking.com', 'Expedia'],
            'nombre_cliente': ['Cliente 1', 'Cliente 2', 'Cliente 3'],
            'estado_reserva': ['Confirmada', 'Confirmada', 'Confirmada']
        })
        
        # Guardar el DataFrame en un archivo Excel
        self.test_bookings.to_excel(self.test_file_path, sheet_name='Reservas', index=False)
        
        # Crear una instancia del servicio de ingesta
        self.ingestion_service = DataIngestionService()
    
    def tearDown(self):
        """
        Limpieza después de las pruebas
        """
        # Eliminar el directorio temporal
        self.temp_dir.cleanup()
    
    @patch('services.data_ingestion.data_ingestion_service.DataIngestionService.save_to_database')
    def test_process_bookings(self, mock_save):
        """
        Prueba el procesamiento de reservas
        """
        # Configurar el mock
        mock_save.return_value = (True, 3)
        
        # Procesar reservas
        success, message, count = self.ingestion_service.process_bookings(self.test_file_path)
        
        # Verificar que se procesaron correctamente
        self.assertTrue(success)
        self.assertEqual(count, 3)
        
        # Verificar que se llamó al método save_to_database
        mock_save.assert_called_once()
    
    @patch('services.data_ingestion.excel_reader.ExcelReader.read_excel_file')
    def test_process_bookings_error(self, mock_read):
        """
        Prueba el manejo de errores al procesar reservas
        """
        # Configurar el mock para lanzar una excepción
        mock_read.side_effect = Exception("Error de prueba")
        
        # Procesar reservas
        success, message, count = self.ingestion_service.process_bookings(self.test_file_path)
        
        # Verificar que se manejó el error correctamente
        self.assertFalse(success)
        self.assertIn("Error", message)
        self.assertEqual(count, 0)
    
    @patch('services.data_ingestion.data_ingestion_service.DataIngestionService.expand_booking_to_nights')
    def test_calculate_daily_occupancy(self, mock_expand):
        """
        Prueba el cálculo de ocupación diaria
        """
        # Crear un DataFrame de prueba para noches expandidas
        expanded_df = pl.DataFrame({
            'fecha': ['2025-02-01', '2025-02-02', '2025-02-02', '2025-02-03', '2025-02-03', '2025-02-04', '2025-02-05'],
            'cod_hab': ['EST', 'EST', 'JRS', 'ESC', 'JRS', 'JRS', 'ESC'],
            'tarifa_noche': [100.0, 100.0, 150.0, 200.0, 150.0, 150.0, 200.0]
        })
        
        # Configurar el mock
        mock_expand.return_value = expanded_df
        
        # Configurar capacidades de habitaciones
        room_capacities = {
            'EST': 14,
            'JRS': 4,
            'ESC': 26
        }
        
        # Calcular ocupación diaria
        with patch.object(self.ingestion_service, 'get_room_capacities', return_value=room_capacities):
            occupancy_df = self.ingestion_service.calculate_daily_occupancy(pl.DataFrame())
        
        # Verificar que se calculó correctamente
        self.assertIsNotNone(occupancy_df)
        self.assertIn('fecha', occupancy_df.columns)
        self.assertIn('cod_hab', occupancy_df.columns)
        self.assertIn('habitaciones_disponibles', occupancy_df.columns)
        self.assertIn('habitaciones_ocupadas', occupancy_df.columns)
        self.assertIn('ocupacion_porcentaje', occupancy_df.columns)

if __name__ == "__main__":
    unittest.main()