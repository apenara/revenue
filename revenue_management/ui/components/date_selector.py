#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Componente para seleccionar rangos de fechas
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

def date_selector(key=None, default_days=30, max_days=365, allow_empty=False):
    """
    Componente para seleccionar un rango de fechas.
    
    Args:
        key (str, optional): Clave única para el componente
        default_days (int): Número de días por defecto para el rango
        max_days (int): Número máximo de días permitidos
        allow_empty (bool): Permitir selección vacía
        
    Returns:
        tuple: (fecha_inicio, fecha_fin) o (None, None) si allow_empty=True y no se selecciona
    """
    # Generar clave única si no se proporciona
    if key is None:
        key = f"date_selector_{id(datetime.now())}"
    
    # Fechas por defecto
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=default_days)
    
    # Opciones predefinidas
    date_options = {
        "Últimos 7 días": (end_date - timedelta(days=7), end_date),
        "Últimos 30 días": (end_date - timedelta(days=30), end_date),
        "Últimos 90 días": (end_date - timedelta(days=90), end_date),
        "Este mes": (datetime(end_date.year, end_date.month, 1).date(), end_date),
        "Mes anterior": (
            datetime(end_date.year, end_date.month - 1 if end_date.month > 1 else 12, 1).date(),
            datetime(
                end_date.year, 
                end_date.month - 1 if end_date.month > 1 else 12,
                calendar.monthrange(
                    end_date.year, 
                    end_date.month - 1 if end_date.month > 1 else 12
                )[1]
            ).date()
        ),
        "Este año": (datetime(end_date.year, 1, 1).date(), end_date),
        "Año anterior": (
            datetime(end_date.year - 1, 1, 1).date(),
            datetime(end_date.year - 1, 12, 31).date()
        ),
        "Personalizado": (None, None)
    }
    
    if allow_empty:
        date_options["Sin filtro"] = (None, None)
    
    # Crear contenedor para el selector
    date_container = st.container()
    
    with date_container:
        # Selector de opción
        col1, col2 = st.columns([1, 3])
        
        with col1:
            selected_option = st.selectbox(
                "Período",
                options=list(date_options.keys()),
                index=2,  # Últimos 30 días por defecto
                key=f"{key}_option"
            )
        
        # Obtener fechas según la opción seleccionada
        start_date, end_date = date_options[selected_option]
        
        # Si es personalizado, mostrar selectores de fecha
        if selected_option == "Personalizado":
            with col2:
                cols = st.columns(2)
                
                with cols[0]:
                    start_date = st.date_input(
                        "Fecha inicio",
                        value=datetime.now().date() - timedelta(days=default_days),
                        key=f"{key}_start"
                    )
                
                with cols[1]:
                    end_date = st.date_input(
                        "Fecha fin",
                        value=datetime.now().date(),
                        key=f"{key}_end"
                    )
                
                # Validar rango de fechas
                if start_date and end_date:
                    if start_date > end_date:
                        st.error("La fecha de inicio debe ser anterior a la fecha de fin.")
                        return None, None
                    
                    days_diff = (end_date - start_date).days
                    if days_diff > max_days:
                        st.warning(f"El rango máximo permitido es de {max_days} días. Se ha ajustado automáticamente.")
                        start_date = end_date - timedelta(days=max_days)
        
        # Mostrar rango seleccionado si no es personalizado y no es vacío
        elif selected_option != "Sin filtro":
            with col2:
                st.info(f"Rango seleccionado: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    
    return start_date, end_date

def date_range_selector(label="Rango de fechas", key=None, default_days=30, max_days=365):
    """
    Selector de rango de fechas con etiqueta.
    
    Args:
        label (str): Etiqueta para el selector
        key (str, optional): Clave única para el componente
        default_days (int): Número de días por defecto para el rango
        max_days (int): Número máximo de días permitidos
        
    Returns:
        tuple: (fecha_inicio, fecha_fin)
    """
    st.subheader(label)
    return date_selector(key=key, default_days=default_days, max_days=max_days)

def date_filter_sidebar(key=None, default_days=30, max_days=365, allow_empty=False):
    """
    Selector de rango de fechas para la barra lateral.
    
    Args:
        key (str, optional): Clave única para el componente
        default_days (int): Número de días por defecto para el rango
        max_days (int): Número máximo de días permitidos
        allow_empty (bool): Permitir selección vacía
        
    Returns:
        tuple: (fecha_inicio, fecha_fin) o (None, None) si allow_empty=True y no se selecciona
    """
    st.sidebar.subheader("Filtro de fechas")
    
    # Generar clave única si no se proporciona
    if key is None:
        key = f"date_sidebar_{id(datetime.now())}"
    
    # Fechas por defecto
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=default_days)
    
    # Opciones predefinidas
    date_options = {
        "Últimos 7 días": (end_date - timedelta(days=7), end_date),
        "Últimos 30 días": (end_date - timedelta(days=30), end_date),
        "Últimos 90 días": (end_date - timedelta(days=90), end_date),
        "Este mes": (datetime(end_date.year, end_date.month, 1).date(), end_date),
        "Mes anterior": (
            datetime(end_date.year, end_date.month - 1 if end_date.month > 1 else 12, 1).date(),
            datetime(
                end_date.year, 
                end_date.month - 1 if end_date.month > 1 else 12,
                calendar.monthrange(
                    end_date.year, 
                    end_date.month - 1 if end_date.month > 1 else 12
                )[1]
            ).date()
        ),
        "Este año": (datetime(end_date.year, 1, 1).date(), end_date),
        "Año anterior": (
            datetime(end_date.year - 1, 1, 1).date(),
            datetime(end_date.year - 1, 12, 31).date()
        ),
        "Personalizado": (None, None)
    }
    
    if allow_empty:
        date_options["Sin filtro"] = (None, None)
    
    # Selector de opción
    selected_option = st.sidebar.selectbox(
        "Período",
        options=list(date_options.keys()),
        index=2,  # Últimos 30 días por defecto
        key=f"{key}_option"
    )
    
    # Obtener fechas según la opción seleccionada
    start_date, end_date = date_options[selected_option]
    
    # Si es personalizado, mostrar selectores de fecha
    if selected_option == "Personalizado":
        start_date = st.sidebar.date_input(
            "Fecha inicio",
            value=datetime.now().date() - timedelta(days=default_days),
            key=f"{key}_start"
        )
        
        end_date = st.sidebar.date_input(
            "Fecha fin",
            value=datetime.now().date(),
            key=f"{key}_end"
        )
        
        # Validar rango de fechas
        if start_date and end_date:
            if start_date > end_date:
                st.sidebar.error("La fecha de inicio debe ser anterior a la fecha de fin.")
                return None, None
            
            days_diff = (end_date - start_date).days
            if days_diff > max_days:
                st.sidebar.warning(f"El rango máximo permitido es de {max_days} días. Se ha ajustado automáticamente.")
                start_date = end_date - timedelta(days=max_days)
    
    # Mostrar rango seleccionado si no es personalizado y no es vacío
    elif selected_option != "Sin filtro":
        st.sidebar.info(f"Rango: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    
    return start_date, end_date