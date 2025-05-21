#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilidades para crear visualizaciones
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

def create_line_chart(data, x, y, color=None, title=None, labels=None, template="plotly_white"):
    """
    Crea un gráfico de líneas con Plotly.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos
        x (str): Columna para el eje X
        y (str/list): Columna(s) para el eje Y
        color (str, optional): Columna para el color
        title (str, optional): Título del gráfico
        labels (dict, optional): Diccionario con etiquetas personalizadas
        template (str): Plantilla de estilo de Plotly
        
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly
    """
    if isinstance(y, list) and len(y) > 1 and not color:
        # Crear gráfico con múltiples líneas
        fig = go.Figure()
        
        for col in y:
            fig.add_trace(
                go.Scatter(
                    x=data[x],
                    y=data[col],
                    mode='lines+markers',
                    name=col
                )
            )
        
        # Configurar layout
        fig.update_layout(
            title=title,
            xaxis_title=labels.get(x, x) if labels else x,
            yaxis_title="Valor",
            template=template,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    else:
        # Crear gráfico con una línea o agrupado por color
        fig = px.line(
            data, x=x, y=y, color=color,
            title=title,
            labels=labels,
            template=template,
            markers=True
        )
        
        # Mejorar layout
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    
    return fig

def create_bar_chart(data, x, y, color=None, title=None, labels=None, template="plotly_white", barmode="group"):
    """
    Crea un gráfico de barras con Plotly.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos
        x (str): Columna para el eje X
        y (str/list): Columna(s) para el eje Y
        color (str, optional): Columna para el color
        title (str, optional): Título del gráfico
        labels (dict, optional): Diccionario con etiquetas personalizadas
        template (str): Plantilla de estilo de Plotly
        barmode (str): Modo de barras ('group', 'stack', 'relative')
        
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly
    """
    fig = px.bar(
        data, x=x, y=y, color=color,
        title=title,
        labels=labels,
        template=template,
        barmode=barmode
    )
    
    # Mejorar layout
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_pie_chart(data, names, values, title=None, labels=None, template="plotly_white", hole=0.4):
    """
    Crea un gráfico circular con Plotly.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos
        names (str): Columna para las etiquetas
        values (str): Columna para los valores
        title (str, optional): Título del gráfico
        labels (dict, optional): Diccionario con etiquetas personalizadas
        template (str): Plantilla de estilo de Plotly
        hole (float): Tamaño del agujero central (0-1)
        
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly
    """
    fig = px.pie(
        data, names=names, values=values,
        title=title,
        labels=labels,
        template=template,
        hole=hole
    )
    
    # Mejorar layout
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    return fig

def create_heatmap(data, x, y, z, title=None, labels=None, template="plotly_white", color_scale="RdBu_r"):
    """
    Crea un mapa de calor con Plotly.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos
        x (str): Columna para el eje X
        y (str): Columna para el eje Y
        z (str): Columna para los valores
        title (str, optional): Título del gráfico
        labels (dict, optional): Diccionario con etiquetas personalizadas
        template (str): Plantilla de estilo de Plotly
        color_scale (str): Escala de colores
        
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly
    """
    # Pivotar datos si es necesario
    if len(data[x].unique()) * len(data[y].unique()) == len(data):
        # Los datos ya están en formato largo, pivotar a formato ancho
        pivot_data = data.pivot(index=y, columns=x, values=z)
        
        # Crear heatmap
        fig = px.imshow(
            pivot_data,
            title=title,
            labels=labels,
            color_continuous_scale=color_scale,
            template=template
        )
    else:
        # Usar los datos tal como están
        fig = px.density_heatmap(
            data, x=x, y=y, z=z,
            title=title,
            labels=labels,
            color_continuous_scale=color_scale,
            template=template
        )
    
    return fig

def create_scatter_plot(data, x, y, color=None, size=None, title=None, labels=None, template="plotly_white"):
    """
    Crea un gráfico de dispersión con Plotly.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos
        x (str): Columna para el eje X
        y (str): Columna para el eje Y
        color (str, optional): Columna para el color
        size (str, optional): Columna para el tamaño
        title (str, optional): Título del gráfico
        labels (dict, optional): Diccionario con etiquetas personalizadas
        template (str): Plantilla de estilo de Plotly
        
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly
    """
    fig = px.scatter(
        data, x=x, y=y, color=color, size=size,
        title=title,
        labels=labels,
        template=template
    )
    
    # Mejorar layout
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_occupancy_calendar(data, date_column, occupancy_column, room_type_column=None, 
                             title=None, template="plotly_white"):
    """
    Crea un calendario de ocupación con Plotly.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos
        date_column (str): Columna con las fechas
        occupancy_column (str): Columna con los valores de ocupación
        room_type_column (str, optional): Columna con los tipos de habitación
        title (str, optional): Título del gráfico
        template (str): Plantilla de estilo de Plotly
        
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly
    """
    # Asegurar que la columna de fecha esté en formato datetime
    if not pd.api.types.is_datetime64_dtype(data[date_column]):
        data = data.copy()
        data[date_column] = pd.to_datetime(data[date_column])
    
    # Extraer año, mes y día
    data['year'] = data[date_column].dt.year
    data['month'] = data[date_column].dt.month
    data['day'] = data[date_column].dt.day
    
    # Crear figura
    if room_type_column and room_type_column in data.columns:
        # Crear un heatmap por tipo de habitación
        room_types = data[room_type_column].unique()
        
        # Crear subplots
        fig = make_subplots(
            rows=len(room_types),
            cols=1,
            subplot_titles=[f"Tipo: {rt}" for rt in room_types],
            vertical_spacing=0.05
        )
        
        # Añadir heatmap para cada tipo de habitación
        for i, rt in enumerate(room_types):
            rt_data = data[data[room_type_column] == rt]
            
            # Pivotar datos
            pivot_data = rt_data.pivot_table(
                index='day',
                columns=['year', 'month'],
                values=occupancy_column,
                aggfunc='mean'
            )
            
            # Crear etiquetas para los meses
            month_labels = [f"{y}-{m:02d}" for y, m in pivot_data.columns.values]
            
            # Añadir heatmap
            fig.add_trace(
                go.Heatmap(
                    z=pivot_data.values,
                    x=month_labels,
                    y=pivot_data.index,
                    colorscale="RdYlGn_r",
                    showscale=True if i == 0 else False,
                    colorbar=dict(title="Ocupación")
                ),
                row=i+1,
                col=1
            )
    else:
        # Crear un solo heatmap
        # Pivotar datos
        pivot_data = data.pivot_table(
            index='day',
            columns=['year', 'month'],
            values=occupancy_column,
            aggfunc='mean'
        )
        
        # Crear etiquetas para los meses
        month_labels = [f"{y}-{m:02d}" for y, m in pivot_data.columns.values]
        
        # Crear figura
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=month_labels,
            y=pivot_data.index,
            colorscale="RdYlGn_r",
            colorbar=dict(title="Ocupación")
        ))
    
    # Configurar layout
    fig.update_layout(
        title=title,
        template=template,
        xaxis=dict(title="Mes"),
        yaxis=dict(title="Día", autorange="reversed")
    )
    
    return fig

def create_forecast_comparison(historical_data, forecast_data, date_column, value_column, 
                              title=None, template="plotly_white"):
    """
    Crea un gráfico comparativo entre datos históricos y pronósticos.
    
    Args:
        historical_data (pd.DataFrame): DataFrame con datos históricos
        forecast_data (pd.DataFrame): DataFrame con pronósticos
        date_column (str): Columna con las fechas
        value_column (str): Columna con los valores
        title (str, optional): Título del gráfico
        template (str): Plantilla de estilo de Plotly
        
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly
    """
    # Asegurar que las columnas de fecha estén en formato datetime
    historical = historical_data.copy()
    forecast = forecast_data.copy()
    
    if not pd.api.types.is_datetime64_dtype(historical[date_column]):
        historical[date_column] = pd.to_datetime(historical[date_column])
    
    if not pd.api.types.is_datetime64_dtype(forecast[date_column]):
        forecast[date_column] = pd.to_datetime(forecast[date_column])
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir datos históricos
    fig.add_trace(
        go.Scatter(
            x=historical[date_column],
            y=historical[value_column],
            mode='lines+markers',
            name='Histórico',
            line=dict(color='blue')
        )
    )
    
    # Añadir pronósticos
    fig.add_trace(
        go.Scatter(
            x=forecast[date_column],
            y=forecast[value_column],
            mode='lines+markers',
            name='Pronóstico',
            line=dict(color='red', dash='dash')
        )
    )
    
    # Configurar layout
    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title=value_column,
        template=template,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_pricing_recommendation_chart(data, date_column, price_columns, title=None, template="plotly_white"):
    """
    Crea un gráfico de recomendaciones de precios.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos
        date_column (str): Columna con las fechas
        price_columns (dict): Diccionario con columnas de precios y sus etiquetas
        title (str, optional): Título del gráfico
        template (str): Plantilla de estilo de Plotly
        
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly
    """
    # Asegurar que la columna de fecha esté en formato datetime
    if not pd.api.types.is_datetime64_dtype(data[date_column]):
        data = data.copy()
        data[date_column] = pd.to_datetime(data[date_column])
    
    # Crear figura
    fig = go.Figure()
    
    # Colores para cada tipo de precio
    colors = {
        'base': 'blue',
        'min': 'green',
        'max': 'red',
        'recomendado': 'purple',
        'actual': 'orange'
    }
    
    # Añadir cada serie de precios
    for col, label in price_columns.items():
        if col in data.columns:
            color = colors.get(col.lower().split('_')[-1], 'gray')
            
            fig.add_trace(
                go.Scatter(
                    x=data[date_column],
                    y=data[col],
                    mode='lines+markers',
                    name=label,
                    line=dict(color=color)
                )
            )
    
    # Configurar layout
    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title="Precio",
        template=template,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig