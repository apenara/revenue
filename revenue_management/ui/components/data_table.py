#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Componente para mostrar tablas de datos
"""

import streamlit as st
import pandas as pd
import numpy as np
from ui.utils.formatting import format_currency, format_percentage, format_date, format_number

def data_table(df, title=None, height=None, column_config=None, use_container_width=True, 
               hide_index=False, selection="single", key=None, on_select=None):
    """
    Muestra una tabla de datos con formato.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos a mostrar
        title (str, optional): Título de la tabla
        height (int, optional): Altura de la tabla en píxeles
        column_config (dict, optional): Configuración de columnas
        use_container_width (bool): Usar ancho completo del contenedor
        hide_index (bool): Ocultar índice de la tabla
        selection (str): Tipo de selección ('single', 'multi', None)
        key (str, optional): Clave única para el componente
        on_select (function, optional): Función a ejecutar cuando se selecciona una fila
        
    Returns:
        pd.DataFrame: DataFrame con las filas seleccionadas o None
    """
    if df is None or df.empty:
        st.warning("No hay datos disponibles para mostrar.")
        return None
    
    if title:
        st.subheader(title)
    
    # Configuración por defecto para columnas comunes
    if column_config is None:
        column_config = {}
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Configurar columnas de fechas
            if "fecha" in col_lower or "date" in col_lower:
                column_config[col] = st.column_config.DateColumn(
                    format="DD/MM/YYYY"
                )
            
            # Configurar columnas de moneda
            elif "precio" in col_lower or "tarifa" in col_lower or "ingreso" in col_lower or "revenue" in col_lower:
                column_config[col] = st.column_config.NumberColumn(
                    format="$ %.2f"
                )
            
            # Configurar columnas de porcentaje
            elif "porcentaje" in col_lower or "ocupacion" in col_lower or "ratio" in col_lower:
                column_config[col] = st.column_config.NumberColumn(
                    format="%.2f%%"
                )
    
    # Mostrar tabla con configuración
    selection_data = st.dataframe(
        df,
        column_config=column_config,
        height=height,
        use_container_width=use_container_width,
        hide_index=hide_index,
        selection=selection,
        key=key
    )
    
    # Procesar selección si hay callback
    if selection_data and on_select:
        selected_rows = df.iloc[selection_data]
        if not selected_rows.empty:
            on_select(selected_rows)
        return selected_rows
    
    return None

def filterable_data_table(df, title=None, filters=None, height=None, column_config=None, 
                          use_container_width=True, hide_index=False, selection="single", key=None):
    """
    Muestra una tabla de datos con filtros.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos a mostrar
        title (str, optional): Título de la tabla
        filters (list, optional): Lista de columnas para filtrar
        height (int, optional): Altura de la tabla en píxeles
        column_config (dict, optional): Configuración de columnas
        use_container_width (bool): Usar ancho completo del contenedor
        hide_index (bool): Ocultar índice de la tabla
        selection (str): Tipo de selección ('single', 'multi', None)
        key (str, optional): Clave única para el componente
        
    Returns:
        pd.DataFrame: DataFrame filtrado
    """
    if df is None or df.empty:
        st.warning("No hay datos disponibles para mostrar.")
        return None
    
    if title:
        st.subheader(title)
    
    # Aplicar filtros si se especifican
    filtered_df = df.copy()
    
    if filters:
        with st.expander("Filtros", expanded=False):
            filter_cols = st.columns(len(filters))
            
            for i, col_name in enumerate(filters):
                with filter_cols[i]:
                    if col_name in df.columns:
                        # Determinar tipo de filtro según el tipo de datos
                        if pd.api.types.is_numeric_dtype(df[col_name]):
                            # Filtro numérico (slider)
                            min_val = float(df[col_name].min())
                            max_val = float(df[col_name].max())
                            
                            if min_val != max_val:
                                values = st.slider(
                                    f"Filtrar por {col_name}",
                                    min_val,
                                    max_val,
                                    (min_val, max_val),
                                    key=f"filter_{col_name}_{key}"
                                )
                                filtered_df = filtered_df[
                                    (filtered_df[col_name] >= values[0]) & 
                                    (filtered_df[col_name] <= values[1])
                                ]
                        
                        elif pd.api.types.is_datetime64_dtype(df[col_name]):
                            # Filtro de fecha
                            min_date = df[col_name].min().date()
                            max_date = df[col_name].max().date()
                            
                            if min_date != max_date:
                                start_date = st.date_input(
                                    f"Desde {col_name}",
                                    min_date,
                                    key=f"filter_start_{col_name}_{key}"
                                )
                                end_date = st.date_input(
                                    f"Hasta {col_name}",
                                    max_date,
                                    key=f"filter_end_{col_name}_{key}"
                                )
                                
                                filtered_df = filtered_df[
                                    (filtered_df[col_name].dt.date >= start_date) & 
                                    (filtered_df[col_name].dt.date <= end_date)
                                ]
                        
                        else:
                            # Filtro categórico (multiselect)
                            options = df[col_name].unique().tolist()
                            selected = st.multiselect(
                                f"Filtrar por {col_name}",
                                options,
                                default=options,
                                key=f"filter_multi_{col_name}_{key}"
                            )
                            
                            if selected:
                                filtered_df = filtered_df[filtered_df[col_name].isin(selected)]
    
    # Mostrar tabla filtrada
    return data_table(
        filtered_df,
        title=None,  # Ya mostramos el título arriba
        height=height,
        column_config=column_config,
        use_container_width=use_container_width,
        hide_index=hide_index,
        selection=selection,
        key=f"table_{key}" if key else None
    )

def editable_data_table(df, title=None, editable_columns=None, height=None, column_config=None, 
                        use_container_width=True, hide_index=False, key=None, on_change=None):
    """
    Muestra una tabla de datos editable.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos a mostrar
        title (str, optional): Título de la tabla
        editable_columns (list, optional): Lista de columnas editables
        height (int, optional): Altura de la tabla en píxeles
        column_config (dict, optional): Configuración de columnas
        use_container_width (bool): Usar ancho completo del contenedor
        hide_index (bool): Ocultar índice de la tabla
        key (str, optional): Clave única para el componente
        on_change (function, optional): Función a ejecutar cuando cambian los datos
        
    Returns:
        pd.DataFrame: DataFrame con los datos editados
    """
    if df is None or df.empty:
        st.warning("No hay datos disponibles para mostrar.")
        return None
    
    if title:
        st.subheader(title)
    
    # Configurar columnas editables
    if editable_columns is None:
        editable_columns = df.columns.tolist()
    
    # Crear configuración de columnas si no se proporciona
    if column_config is None:
        column_config = {}
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Columnas editables
            if col in editable_columns:
                # Configurar columnas de fechas
                if "fecha" in col_lower or "date" in col_lower:
                    column_config[col] = st.column_config.DateColumn(
                        format="DD/MM/YYYY",
                        required=True
                    )
                
                # Configurar columnas de moneda
                elif "precio" in col_lower or "tarifa" in col_lower or "ingreso" in col_lower or "revenue" in col_lower:
                    column_config[col] = st.column_config.NumberColumn(
                        format="$ %.2f",
                        min_value=0,
                        required=True
                    )
                
                # Configurar columnas de porcentaje
                elif "porcentaje" in col_lower or "ocupacion" in col_lower or "ratio" in col_lower:
                    column_config[col] = st.column_config.NumberColumn(
                        format="%.2f%%",
                        min_value=0,
                        max_value=100,
                        required=True
                    )
                
                # Otras columnas numéricas
                elif pd.api.types.is_numeric_dtype(df[col]):
                    column_config[col] = st.column_config.NumberColumn(
                        required=True
                    )
                
                # Columnas de texto
                else:
                    column_config[col] = st.column_config.TextColumn(
                        required=True
                    )
            
            # Columnas no editables
            else:
                # Configurar columnas de fechas
                if "fecha" in col_lower or "date" in col_lower:
                    column_config[col] = st.column_config.DateColumn(
                        format="DD/MM/YYYY",
                        disabled=True
                    )
                
                # Configurar columnas de moneda
                elif "precio" in col_lower or "tarifa" in col_lower or "ingreso" in col_lower or "revenue" in col_lower:
                    column_config[col] = st.column_config.NumberColumn(
                        format="$ %.2f",
                        disabled=True
                    )
                
                # Configurar columnas de porcentaje
                elif "porcentaje" in col_lower or "ocupacion" in col_lower or "ratio" in col_lower:
                    column_config[col] = st.column_config.NumberColumn(
                        format="%.2f%%",
                        disabled=True
                    )
    
    # Mostrar tabla editable
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        height=height,
        use_container_width=use_container_width,
        hide_index=hide_index,
        key=key,
        disabled=not bool(editable_columns)
    )
    
    # Ejecutar callback si hay cambios
    if on_change and not edited_df.equals(df):
        on_change(edited_df)
    
    return edited_df