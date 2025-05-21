#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para los componentes de la interfaz de usuario
"""

import unittest
import sys
import pandas as pd
import polars as pl
import streamlit as st
from pathlib import Path
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.components.kpi_card import kpi_card, kpi_row, kpi_section
from ui.components.data_table import data_table, editable_data_table, filterable_data_table
from ui.components.chart import chart, time_series_chart
from ui.components.date_selector import date_selector
from ui.components.file_uploader import file_uploader
from ui.utils.formatting import format_currency, format_percentage, format_number, format_status

class TestKpiCard(unittest.TestCase):
    """
    Pruebas unitarias para el componente KPI Card
    """
    
    @patch('streamlit.container')
    @patch('streamlit.metric')
    def test_kpi_card(self, mock_metric, mock_container):
        """
        Prueba el componente KPI Card
        """
        # Configurar los mocks
        mock_container.return_value.__enter__.return_value = MagicMock()
        
        # Llamar a la función
        kpi_card(
            title="Ocupación",
            value=75.5,
            delta=5.2,
            delta_description="vs. año anterior",
            formatter=format_percentage,
            color="blue"
        )
        
        # Verificar que se llamó a st.metric con los parámetros correctos
        mock_metric.assert_called_once()
        args, kwargs = mock_metric.call_args
        
        self.assertEqual(kwargs['label'], "Ocupación")
        self.assertEqual(kwargs['value'], "75.5%")
        self.assertEqual(kwargs['delta'], "5.2%")
        self.assertEqual(kwargs['delta_color'], "normal")
    
    @patch('streamlit.columns')
    def test_kpi_row(self, mock_columns):
        """
        Prueba el componente KPI Row
        """
        # Configurar los mocks
        mock_col = MagicMock()
        mock_columns.return_value = [mock_col, mock_col, mock_col]
        
        # Crear datos de KPIs
        kpis = [
            {"title": "Ocupación", "value": 75.5, "delta": 5.2, "formatter": format_percentage},
            {"title": "ADR", "value": 120000, "delta": -2.5, "formatter": format_currency},
            {"title": "RevPAR", "value": 90600, "delta": 3.1, "formatter": format_currency}
        ]
        
        # Llamar a la función
        kpi_row(kpis)
        
        # Verificar que se llamó a st.columns con el número correcto de columnas
        mock_columns.assert_called_once_with(len(kpis))
    
    @patch('streamlit.container')
    @patch('streamlit.subheader')
    def test_kpi_section(self, mock_subheader, mock_container):
        """
        Prueba el componente KPI Section
        """
        # Configurar los mocks
        mock_container.return_value.__enter__.return_value = MagicMock()
        
        # Crear datos de KPIs
        kpis = [
            {"title": "Ocupación", "value": 75.5, "delta": 5.2, "formatter": format_percentage},
            {"title": "ADR", "value": 120000, "delta": -2.5, "formatter": format_currency},
            {"title": "RevPAR", "value": 90600, "delta": 3.1, "formatter": format_currency}
        ]
        
        # Llamar a la función
        kpi_section("KPIs Principales", kpis)
        
        # Verificar que se llamó a st.subheader con el título correcto
        mock_subheader.assert_called_once_with("KPIs Principales")


class TestDataTable(unittest.TestCase):
    """
    Pruebas unitarias para el componente Data Table
    """
    
    @patch('streamlit.dataframe')
    def test_data_table(self, mock_dataframe):
        """
        Prueba el componente Data Table
        """
        # Crear un DataFrame de prueba
        test_df = pd.DataFrame({
            'fecha': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'habitacion': ['101', '102', '103'],
            'tarifa': [100000, 150000, 200000],
            'ocupacion': [1, 1, 0]
        })
        
        # Llamar a la función
        data_table(test_df, height=400)
        
        # Verificar que se llamó a st.dataframe con los parámetros correctos
        mock_dataframe.assert_called_once()
        args, kwargs = mock_dataframe.call_args
        
        self.assertEqual(args[0].equals(test_df), True)
        self.assertEqual(kwargs['height'], 400)
    
    @patch('streamlit.data_editor')
    def test_editable_data_table(self, mock_data_editor):
        """
        Prueba el componente Editable Data Table
        """
        # Crear un DataFrame de prueba
        test_df = pd.DataFrame({
            'fecha': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'habitacion': ['101', '102', '103'],
            'tarifa': [100000, 150000, 200000],
            'ocupacion': [1, 1, 0]
        })
        
        # Configurar el mock
        mock_data_editor.return_value = test_df.copy()
        
        # Llamar a la función
        editable_df = editable_data_table(
            test_df,
            editable_columns=['tarifa', 'ocupacion'],
            height=400
        )
        
        # Verificar que se llamó a st.data_editor con los parámetros correctos
        mock_data_editor.assert_called_once()
        args, kwargs = mock_data_editor.call_args
        
        self.assertEqual(args[0].equals(test_df), True)
        self.assertEqual(kwargs['height'], 400)
        self.assertEqual(set(kwargs['column_config'].keys()), {'tarifa', 'ocupacion'})
        
        # Verificar que la función devuelve el DataFrame editado
        self.assertEqual(editable_df.equals(test_df), True)
    
    @patch('streamlit.container')
    @patch('streamlit.dataframe')
    @patch('streamlit.multiselect')
    def test_filterable_data_table(self, mock_multiselect, mock_dataframe, mock_container):
        """
        Prueba el componente Filterable Data Table
        """
        # Configurar los mocks
        mock_container.return_value.__enter__.return_value = MagicMock()
        mock_multiselect.return_value = ['101', '102']  # Valores seleccionados para el filtro
        
        # Crear un DataFrame de prueba
        test_df = pd.DataFrame({
            'fecha': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'habitacion': ['101', '102', '103'],
            'tarifa': [100000, 150000, 200000],
            'ocupacion': [1, 1, 0]
        })
        
        # Llamar a la función
        filterable_data_table(
            test_df,
            filters=['habitacion'],
            height=400
        )
        
        # Verificar que se llamó a st.multiselect para cada filtro
        mock_multiselect.assert_called_once()
        args, kwargs = mock_multiselect.call_args
        
        self.assertEqual(args[0], "Filtrar por habitacion")
        self.assertEqual(set(args[1]), {'101', '102', '103'})
        
        # Verificar que se llamó a st.dataframe con el DataFrame filtrado
        mock_dataframe.assert_called_once()


class TestChart(unittest.TestCase):
    """
    Pruebas unitarias para el componente Chart
    """
    
    @patch('streamlit.plotly_chart')
    def test_chart(self, mock_plotly_chart):
        """
        Prueba el componente Chart
        """
        # Crear un DataFrame de prueba
        test_df = pd.DataFrame({
            'fecha': pd.date_range(start='2025-01-01', periods=10),
            'ocupacion': [70, 75, 80, 85, 90, 85, 80, 75, 70, 75],
            'adr': [100000, 105000, 110000, 115000, 120000, 125000, 120000, 115000, 110000, 105000]
        })
        
        # Llamar a la función
        chart(
            data=test_df,
            chart_type='line',
            x='fecha',
            y=['ocupacion', 'adr'],
            title='Ocupación y ADR',
            labels={'fecha': 'Fecha', 'ocupacion': 'Ocupación (%)', 'adr': 'ADR (COP)'}
        )
        
        # Verificar que se llamó a st.plotly_chart
        mock_plotly_chart.assert_called_once()
    
    @patch('streamlit.plotly_chart')
    def test_time_series_chart(self, mock_plotly_chart):
        """
        Prueba el componente Time Series Chart
        """
        # Crear un DataFrame de prueba
        test_df = pd.DataFrame({
            'fecha': pd.date_range(start='2025-01-01', periods=10),
            'ocupacion': [70, 75, 80, 85, 90, 85, 80, 75, 70, 75],
            'adr': [100000, 105000, 110000, 115000, 120000, 125000, 120000, 115000, 110000, 105000]
        })
        
        # Llamar a la función
        time_series_chart(
            data=test_df,
            date_column='fecha',
            value_columns=['ocupacion', 'adr'],
            title='Ocupación y ADR',
            labels={'ocupacion': 'Ocupación (%)', 'adr': 'ADR (COP)'}
        )
        
        # Verificar que se llamó a st.plotly_chart
        mock_plotly_chart.assert_called_once()


class TestDateSelector(unittest.TestCase):
    """
    Pruebas unitarias para el componente Date Selector
    """
    
    @patch('streamlit.columns')
    @patch('streamlit.date_input')
    def test_date_selector(self, mock_date_input, mock_columns):
        """
        Prueba el componente Date Selector
        """
        # Configurar los mocks
        mock_col = MagicMock()
        mock_columns.return_value = [mock_col, mock_col]
        
        from datetime import datetime, timedelta
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=30)
        
        mock_date_input.side_effect = [start_date, end_date]
        
        # Llamar a la función
        result_start, result_end = date_selector(key="test", default_days=30)
        
        # Verificar que se llamó a st.columns
        mock_columns.assert_called_once_with(2)
        
        # Verificar que se llamó a st.date_input dos veces
        self.assertEqual(mock_date_input.call_count, 2)
        
        # Verificar que la función devuelve las fechas correctas
        self.assertEqual(result_start, start_date)
        self.assertEqual(result_end, end_date)


class TestFileUploader(unittest.TestCase):
    """
    Pruebas unitarias para el componente File Uploader
    """
    
    @patch('streamlit.file_uploader')
    def test_file_uploader(self, mock_file_uploader):
        """
        Prueba el componente File Uploader
        """
        # Configurar el mock
        mock_file = MagicMock()
        mock_file_uploader.return_value = mock_file
        
        # Llamar a la función
        uploaded_file = file_uploader(
            label="Subir archivo Excel",
            type=["xlsx", "xls"],
            key="test_uploader"
        )
        
        # Verificar que se llamó a st.file_uploader con los parámetros correctos
        mock_file_uploader.assert_called_once()
        args, kwargs = mock_file_uploader.call_args
        
        self.assertEqual(args[0], "Subir archivo Excel")
        self.assertEqual(kwargs['type'], ["xlsx", "xls"])
        self.assertEqual(kwargs['key'], "test_uploader")
        
        # Verificar que la función devuelve el archivo subido
        self.assertEqual(uploaded_file, mock_file)


class TestFormatting(unittest.TestCase):
    """
    Pruebas unitarias para las funciones de formato
    """
    
    def test_format_currency(self):
        """
        Prueba la función format_currency
        """
        # Probar con diferentes valores
        self.assertEqual(format_currency(1000), "$1,000")
        self.assertEqual(format_currency(1000000), "$1,000,000")
        self.assertEqual(format_currency(1234.56), "$1,235")  # Redondeo
        self.assertEqual(format_currency(None), "N/A")
    
    def test_format_percentage(self):
        """
        Prueba la función format_percentage
        """
        # Probar con diferentes valores
        self.assertEqual(format_percentage(75), "75.0%")
        self.assertEqual(format_percentage(75.5), "75.5%")
        self.assertEqual(format_percentage(0), "0.0%")
        self.assertEqual(format_percentage(100), "100.0%")
        self.assertEqual(format_percentage(None), "N/A")
    
    def test_format_number(self):
        """
        Prueba la función format_number
        """
        # Probar con diferentes valores
        self.assertEqual(format_number(1000), "1,000")
        self.assertEqual(format_number(1000000), "1,000,000")
        self.assertEqual(format_number(1234.56), "1,235")  # Redondeo
        self.assertEqual(format_number(None), "N/A")
    
    def test_format_status(self):
        """
        Prueba la función format_status
        """
        # Probar con diferentes estados
        self.assertEqual(format_status("Pendiente"), "🟡 Pendiente")
        self.assertEqual(format_status("Aprobado"), "🟢 Aprobado")
        self.assertEqual(format_status("Rechazado"), "🔴 Rechazado")
        self.assertEqual(format_status("En Revisión"), "🔵 En Revisión")
        self.assertEqual(format_status("Exportado"), "✅ Exportado")
        self.assertEqual(format_status("Otro Estado"), "❓ Otro Estado")

if __name__ == "__main__":
    unittest.main()