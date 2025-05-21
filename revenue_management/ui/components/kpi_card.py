#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Componente para mostrar KPIs en tarjetas
"""

import streamlit as st
import pandas as pd
import numpy as np
from ui.utils.formatting import format_currency, format_percentage, format_number

def kpi_card(title, value, previous_value=None, format_type="number", delta_color="normal", help_text=None, icon=None):
    """
    Muestra un KPI en una tarjeta con formato.
    
    Args:
        title (str): Título del KPI
        value (float/int): Valor actual del KPI
        previous_value (float/int, optional): Valor anterior para comparación
        format_type (str): Tipo de formato ('number', 'currency', 'percentage')
        delta_color (str): Color del delta ('normal', 'inverse')
        help_text (str, optional): Texto de ayuda para mostrar en tooltip
        icon (str, optional): Icono para mostrar junto al título
    """
    # Formatear valor según el tipo
    if format_type == "currency":
        formatted_value = format_currency(value)
    elif format_type == "percentage":
        formatted_value = format_percentage(value)
    else:
        formatted_value = format_number(value)
    
    # Calcular delta si hay valor anterior
    if previous_value is not None and previous_value != 0:
        delta = (value - previous_value) / previous_value
        delta_text = f"{delta:.1%}"
        
        # Determinar si el delta es positivo o negativo según el tipo
        if delta_color == "inverse":
            # Para métricas donde menor es mejor (costos, tiempo, etc.)
            delta_color = "normal" if delta < 0 else "inverse"
        
        # Mostrar métrica con delta
        if icon:
            st.metric(f"{icon} {title}", formatted_value, delta_text, help=help_text, delta_color=delta_color)
        else:
            st.metric(title, formatted_value, delta_text, help=help_text, delta_color=delta_color)
    else:
        # Mostrar métrica sin delta
        if icon:
            st.metric(f"{icon} {title}", formatted_value, help=help_text)
        else:
            st.metric(title, formatted_value, help=help_text)

def kpi_row(kpi_data, columns=3):
    """
    Muestra una fila de KPIs.
    
    Args:
        kpi_data (list): Lista de diccionarios con datos de KPIs
        columns (int): Número de columnas para mostrar
    """
    cols = st.columns(columns)
    
    for i, kpi in enumerate(kpi_data):
        with cols[i % columns]:
            kpi_card(
                title=kpi.get("title", ""),
                value=kpi.get("value", 0),
                previous_value=kpi.get("previous_value"),
                format_type=kpi.get("format_type", "number"),
                delta_color=kpi.get("delta_color", "normal"),
                help_text=kpi.get("help_text"),
                icon=kpi.get("icon")
            )

def kpi_section(title, kpi_data, columns=3):
    """
    Muestra una sección de KPIs con título.
    
    Args:
        title (str): Título de la sección
        kpi_data (list): Lista de diccionarios con datos de KPIs
        columns (int): Número de columnas para mostrar
    """
    st.subheader(title)
    kpi_row(kpi_data, columns)