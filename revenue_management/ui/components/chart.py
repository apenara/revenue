#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Componente para mostrar gráficos
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from ui.utils.visualization import create_line_chart, create_bar_chart, create_pie_chart, create_heatmap

def chart(data, chart_type, title=None, x=None, y=None, color=None, size=None, hover_name=None, 
          labels=None, height=None, width=None, template="plotly_white", use_container_width=True):
    """
    Muestra un gráfico con los datos proporcionados.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos a mostrar
        chart_type (str): Tipo de gráfico ('line', 'bar', 'pie', 'scatter', 'heatmap')
        title (str, optional): Título del gráfico
        x (str): Columna para el eje X
        y (str/list): Columna(s) para el eje Y
        color (str, optional): Columna para el color
        size (str, optional): Columna para el tamaño (scatter)
        hover_name (str, optional): Columna para el nombre al hacer hover
        labels (dict, optional): Diccionario con etiquetas personalizadas
        height (int, optional): Altura del gráfico
        width (int, optional): Ancho del gráfico
        template (str): Plantilla de estilo de Plotly
        use_container_width (bool): Usar ancho completo del contenedor
    """
    if data is None or data.empty:
        st.warning("No hay datos disponibles para mostrar el gráfico.")
        return
    
    if title:
        st.subheader(title)
    
    # Crear gráfico según el tipo
    if chart_type == "line":
        fig = create_line_chart(data, x=x, y=y, color=color, title=title, labels=labels, template=template)
    elif chart_type == "bar":
        fig = create_bar_chart(data, x=x, y=y, color=color, title=title, labels=labels, template=template)
    elif chart_type == "pie":
        fig = create_pie_chart(data, names=x, values=y, title=title, labels=labels, template=template)
    elif chart_type == "scatter":
        fig = px.scatter(
            data, x=x, y=y, color=color, size=size, hover_name=hover_name,
            title=title, labels=labels, template=template
        )
    elif chart_type == "heatmap":
        fig = create_heatmap(data, x=x, y=y, z=color, title=title, labels=labels, template=template)
    else:
        st.error(f"Tipo de gráfico no soportado: {chart_type}")
        return
    
    # Configurar tamaño
    if height or width:
        fig.update_layout(
            height=height,
            width=width
        )
    
    # Mostrar gráfico
    st.plotly_chart(fig, use_container_width=use_container_width)

def multi_chart(data, charts_config, title=None, cols=2, height=None):
    """
    Muestra múltiples gráficos en una cuadrícula.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos a mostrar
        charts_config (list): Lista de diccionarios con configuración de gráficos
        title (str, optional): Título de la sección
        cols (int): Número de columnas en la cuadrícula
        height (int, optional): Altura de cada gráfico
    """
    if data is None or data.empty:
        st.warning("No hay datos disponibles para mostrar los gráficos.")
        return
    
    if title:
        st.subheader(title)
    
    # Crear cuadrícula
    chart_cols = st.columns(cols)
    
    # Mostrar gráficos
    for i, config in enumerate(charts_config):
        with chart_cols[i % cols]:
            chart_type = config.get("type", "line")
            chart_title = config.get("title")
            x = config.get("x")
            y = config.get("y")
            color = config.get("color")
            size = config.get("size")
            hover_name = config.get("hover_name")
            labels = config.get("labels")
            template = config.get("template", "plotly_white")
            
            chart(
                data=data,
                chart_type=chart_type,
                title=chart_title,
                x=x,
                y=y,
                color=color,
                size=size,
                hover_name=hover_name,
                labels=labels,
                height=height,
                template=template,
                use_container_width=True
            )

def time_series_chart(data, date_column, value_columns, title=None, color_discrete_map=None, 
                      height=None, template="plotly_white", use_container_width=True):
    """
    Muestra un gráfico de series temporales.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos a mostrar
        date_column (str): Columna con las fechas
        value_columns (list): Lista de columnas con valores a mostrar
        title (str, optional): Título del gráfico
        color_discrete_map (dict, optional): Mapa de colores para las series
        height (int, optional): Altura del gráfico
        template (str): Plantilla de estilo de Plotly
        use_container_width (bool): Usar ancho completo del contenedor
    """
    if data is None or data.empty:
        st.warning("No hay datos disponibles para mostrar el gráfico.")
        return
    
    if title:
        st.subheader(title)
    
    # Asegurar que la columna de fecha esté en formato datetime
    if not pd.api.types.is_datetime64_dtype(data[date_column]):
        data = data.copy()
        data[date_column] = pd.to_datetime(data[date_column])
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir cada serie
    for column in value_columns:
        color = color_discrete_map.get(column) if color_discrete_map else None
        
        fig.add_trace(
            go.Scatter(
                x=data[date_column],
                y=data[column],
                mode='lines+markers',
                name=column,
                line=dict(color=color) if color else None
            )
        )
    
    # Configurar layout
    fig.update_layout(
        title=title,
        xaxis_title=date_column,
        template=template,
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Mostrar gráfico
    st.plotly_chart(fig, use_container_width=use_container_width)

def comparison_chart(data, x, y1, y2, title=None, y1_name=None, y2_name=None, y1_color="#1f77b4", 
                     y2_color="#ff7f0e", height=None, template="plotly_white", use_container_width=True):
    """
    Muestra un gráfico de comparación con dos ejes Y.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos a mostrar
        x (str): Columna para el eje X
        y1 (str): Columna para el primer eje Y
        y2 (str): Columna para el segundo eje Y
        title (str, optional): Título del gráfico
        y1_name (str, optional): Nombre para la primera serie
        y2_name (str, optional): Nombre para la segunda serie
        y1_color (str): Color para la primera serie
        y2_color (str): Color para la segunda serie
        height (int, optional): Altura del gráfico
        template (str): Plantilla de estilo de Plotly
        use_container_width (bool): Usar ancho completo del contenedor
    """
    if data is None or data.empty:
        st.warning("No hay datos disponibles para mostrar el gráfico.")
        return
    
    if title:
        st.subheader(title)
    
    # Nombres por defecto
    y1_name = y1_name or y1
    y2_name = y2_name or y2
    
    # Crear figura con dos ejes Y
    fig = go.Figure()
    
    # Añadir primera serie
    fig.add_trace(
        go.Scatter(
            x=data[x],
            y=data[y1],
            name=y1_name,
            line=dict(color=y1_color)
        )
    )
    
    # Añadir segunda serie
    fig.add_trace(
        go.Scatter(
            x=data[x],
            y=data[y2],
            name=y2_name,
            line=dict(color=y2_color),
            yaxis="y2"
        )
    )
    
    # Configurar layout
    fig.update_layout(
        title=title,
        xaxis=dict(title=x),
        yaxis=dict(
            title=y1_name,
            titlefont=dict(color=y1_color),
            tickfont=dict(color=y1_color)
        ),
        yaxis2=dict(
            title=y2_name,
            titlefont=dict(color=y2_color),
            tickfont=dict(color=y2_color),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        template=template,
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Mostrar gráfico
    st.plotly_chart(fig, use_container_width=use_container_width)