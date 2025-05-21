#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilidades para formatear datos para visualización
"""

import locale
import pandas as pd
import numpy as np
from datetime import datetime, date

# Configurar locale para formateo de números
try:
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')

def format_currency(value, currency="$", decimals=2):
    """
    Formatea un valor como moneda.
    
    Args:
        value (float/int): Valor a formatear
        currency (str): Símbolo de moneda
        decimals (int): Número de decimales
        
    Returns:
        str: Valor formateado como moneda
    """
    if pd.isna(value):
        return "-"
    
    try:
        value_float = float(value)
        
        if abs(value_float) >= 1_000_000:
            # Formatear en millones
            return f"{currency} {value_float/1_000_000:.{decimals}f}M"
        elif abs(value_float) >= 1_000:
            # Formatear en miles
            return f"{currency} {value_float/1_000:.{decimals}f}K"
        else:
            # Formatear normal
            return f"{currency} {value_float:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(value)

def format_percentage(value, decimals=2):
    """
    Formatea un valor como porcentaje.
    
    Args:
        value (float): Valor a formatear (0.1 = 10%)
        decimals (int): Número de decimales
        
    Returns:
        str: Valor formateado como porcentaje
    """
    if pd.isna(value):
        return "-"
    
    try:
        value_float = float(value)
        
        # Verificar si el valor ya está en porcentaje (>1)
        if abs(value_float) > 1 and abs(value_float) <= 100:
            return f"{value_float:.{decimals}f}%"
        else:
            return f"{value_float*100:.{decimals}f}%"
    except:
        return str(value)

def format_number(value, decimals=2, thousands_sep=True):
    """
    Formatea un valor numérico.
    
    Args:
        value (float/int): Valor a formatear
        decimals (int): Número de decimales
        thousands_sep (bool): Usar separador de miles
        
    Returns:
        str: Valor formateado
    """
    if pd.isna(value):
        return "-"
    
    try:
        value_float = float(value)
        
        if abs(value_float) >= 1_000_000:
            # Formatear en millones
            return f"{value_float/1_000_000:.{decimals}f}M"
        elif abs(value_float) >= 1_000:
            # Formatear en miles
            return f"{value_float/1_000:.{decimals}f}K"
        else:
            # Formatear normal
            if thousands_sep:
                return f"{value_float:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                return f"{value_float:.{decimals}f}".replace(".", ",")
    except:
        return str(value)

def format_date(value, format="%d/%m/%Y"):
    """
    Formatea un valor como fecha.
    
    Args:
        value (datetime/date/str): Valor a formatear
        format (str): Formato de fecha
        
    Returns:
        str: Valor formateado como fecha
    """
    if pd.isna(value):
        return "-"
    
    try:
        if isinstance(value, (datetime, date)):
            return value.strftime(format)
        else:
            # Intentar convertir a datetime
            dt = pd.to_datetime(value)
            return dt.strftime(format)
    except:
        return str(value)

def format_duration(value, unit="days"):
    """
    Formatea un valor como duración.
    
    Args:
        value (float/int): Valor a formatear
        unit (str): Unidad de tiempo ('days', 'hours', 'minutes', 'seconds')
        
    Returns:
        str: Valor formateado como duración
    """
    if pd.isna(value):
        return "-"
    
    try:
        value_float = float(value)
        
        if unit == "days":
            days = int(value_float)
            hours = int((value_float - days) * 24)
            
            if hours > 0:
                return f"{days}d {hours}h"
            else:
                return f"{days}d"
        
        elif unit == "hours":
            hours = int(value_float)
            minutes = int((value_float - hours) * 60)
            
            if minutes > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{hours}h"
        
        elif unit == "minutes":
            minutes = int(value_float)
            seconds = int((value_float - minutes) * 60)
            
            if seconds > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{minutes}m"
        
        elif unit == "seconds":
            return f"{int(value_float)}s"
        
        else:
            return str(value_float)
    except:
        return str(value)

def format_dataframe(df, formatters=None):
    """
    Formatea un DataFrame completo.
    
    Args:
        df (pd.DataFrame): DataFrame a formatear
        formatters (dict): Diccionario con funciones de formato por columna
        
    Returns:
        pd.DataFrame: DataFrame formateado
    """
    if df is None or df.empty:
        return df
    
    # Crear copia para no modificar el original
    formatted_df = df.copy()
    
    # Formatear columnas según el tipo de datos
    for col in formatted_df.columns:
        # Si hay un formateador específico para la columna
        if formatters and col in formatters:
            formatted_df[col] = formatted_df[col].apply(formatters[col])
        
        # Si no hay formateador, usar uno por defecto según el tipo
        else:
            col_lower = col.lower()
            
            # Columnas de fecha
            if "fecha" in col_lower or "date" in col_lower:
                formatted_df[col] = formatted_df[col].apply(lambda x: format_date(x))
            
            # Columnas de moneda
            elif "precio" in col_lower or "tarifa" in col_lower or "ingreso" in col_lower or "revenue" in col_lower:
                formatted_df[col] = formatted_df[col].apply(lambda x: format_currency(x))
            
            # Columnas de porcentaje
            elif "porcentaje" in col_lower or "ocupacion" in col_lower or "ratio" in col_lower:
                formatted_df[col] = formatted_df[col].apply(lambda x: format_percentage(x))
            
            # Columnas de duración
            elif "duracion" in col_lower or "estancia" in col_lower or "duration" in col_lower:
                formatted_df[col] = formatted_df[col].apply(lambda x: format_duration(x))
    
    return formatted_df

def format_kpi_value(value, kpi_type):
    """
    Formatea un valor de KPI según su tipo.
    
    Args:
        value (float/int): Valor a formatear
        kpi_type (str): Tipo de KPI ('currency', 'percentage', 'number', 'duration')
        
    Returns:
        str: Valor formateado
    """
    if pd.isna(value):
        return "-"
    
    if kpi_type == "currency":
        return format_currency(value)
    elif kpi_type == "percentage":
        return format_percentage(value)
    elif kpi_type == "duration":
        return format_duration(value)
    else:
        return format_number(value)

def format_change(current, previous, format_type="percentage", positive_is_good=True):
    """
    Formatea un cambio entre dos valores.
    
    Args:
        current (float/int): Valor actual
        previous (float/int): Valor anterior
        format_type (str): Tipo de formato ('percentage', 'value')
        positive_is_good (bool): Indica si un cambio positivo es bueno
        
    Returns:
        tuple: (valor formateado, color)
    """
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return "-", "gray"
    
    # Calcular cambio
    change = current - previous
    change_pct = change / abs(previous)
    
    # Determinar color
    if change == 0:
        color = "gray"
    elif (change > 0 and positive_is_good) or (change < 0 and not positive_is_good):
        color = "green"
    else:
        color = "red"
    
    # Formatear valor
    if format_type == "percentage":
        value = format_percentage(change_pct)
    else:
        value = format_number(change)
    
    # Añadir signo
    if change > 0:
        value = "+" + value
    
    return value, color

def format_status(status):
    """
    Formatea un estado con color.
    
    Args:
        status (str): Estado a formatear
        
    Returns:
        tuple: (emoji, color)
    """
    status_lower = status.lower()
    
    if "completado" in status_lower or "aprobado" in status_lower or "activo" in status_lower:
        return "✅", "green"
    elif "pendiente" in status_lower or "en proceso" in status_lower:
        return "⏳", "orange"
    elif "error" in status_lower or "rechazado" in status_lower or "cancelado" in status_lower:
        return "❌", "red"
    elif "advertencia" in status_lower or "alerta" in status_lower:
        return "⚠️", "yellow"
    else:
        return "ℹ️", "blue"