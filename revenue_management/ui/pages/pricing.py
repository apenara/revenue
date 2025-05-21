#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Página para configurar reglas de pricing y generar recomendaciones
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

from ui.components.kpi_card import kpi_row, kpi_section
from ui.components.data_table import data_table, editable_data_table
from ui.components.chart import chart, time_series_chart
from ui.components.date_selector import date_selector
from ui.utils.formatting import format_currency, format_percentage, format_number
from config import config

def show(orchestrator):
    """
    Muestra la página de pricing.
    
    Args:
        orchestrator: Instancia del orquestador de servicios
    """
    st.header("Pricing")
    
    # Crear pestañas
    tab1, tab2, tab3 = st.tabs(["Reglas de Pricing", "Generar Recomendaciones", "Análisis de Precios"])
    
    with tab1:
        st.subheader("Reglas de Pricing")
        
        # Obtener configuración de pricing
        pricing_config = config.get_pricing_rules()
        
        # Mostrar reglas actuales
        with st.expander("Reglas Actuales", expanded=True):
            # Umbrales de ocupación
            st.subheader("Umbrales de Ocupación")
            
            col1, col2 = st.columns(2)
            
            with col1:
                min_occupancy = st.slider(
                    "Umbral de ocupación baja",
                    min_value=0.0,
                    max_value=1.0,
                    value=pricing_config.get("min_occupancy_threshold", 0.4),
                    step=0.05,
                    format="%.2f",
                    key="min_occupancy"
                )
            
            with col2:
                max_occupancy = st.slider(
                    "Umbral de ocupación alta",
                    min_value=0.0,
                    max_value=1.0,
                    value=pricing_config.get("max_occupancy_threshold", 0.8),
                    step=0.05,
                    format="%.2f",
                    key="max_occupancy"
                )
            
            # Factores de ajuste
            st.subheader("Factores de Ajuste")
            
            col1, col2 = st.columns(2)
            
            with col1:
                low_occupancy_factor = st.slider(
                    "Factor para ocupación baja",
                    min_value=0.5,
                    max_value=1.0,
                    value=pricing_config.get("low_occupancy_factor", 0.9),
                    step=0.05,
                    format="%.2f",
                    key="low_occupancy_factor"
                )
            
            with col2:
                high_occupancy_factor = st.slider(
                    "Factor para ocupación alta",
                    min_value=1.0,
                    max_value=1.5,
                    value=pricing_config.get("high_occupancy_factor", 1.15),
                    step=0.05,
                    format="%.2f",
                    key="high_occupancy_factor"
                )
            
            # Límites de precio
            st.subheader("Límites de Precio")
            
            col1, col2 = st.columns(2)
            
            with col1:
                min_price_factor = st.slider(
                    "Factor mínimo de precio",
                    min_value=0.5,
                    max_value=1.0,
                    value=pricing_config.get("min_price_factor", 0.7),
                    step=0.05,
                    format="%.2f",
                    key="min_price_factor"
                )
            
            with col2:
                max_price_factor = st.slider(
                    "Factor máximo de precio",
                    min_value=1.0,
                    max_value=2.0,
                    value=pricing_config.get("max_price_factor", 1.3),
                    step=0.05,
                    format="%.2f",
                    key="max_price_factor"
                )
            
            # Descuento para canal directo
            st.subheader("Descuento para Canal Directo")
            
            direct_channel_discount = st.slider(
                "Descuento para canal directo",
                min_value=0.0,
                max_value=0.2,
                value=pricing_config.get("direct_channel_discount", 0.05),
                step=0.01,
                format="%.2f",
                key="direct_channel_discount"
            )
            
            # Botón para guardar configuración
            if st.button("Guardar Configuración", key="save_pricing_config"):
                with st.spinner("Guardando configuración..."):
                    # Crear nueva configuración
                    new_config = {
                        "min_occupancy_threshold": min_occupancy,
                        "max_occupancy_threshold": max_occupancy,
                        "low_occupancy_factor": low_occupancy_factor,
                        "high_occupancy_factor": high_occupancy_factor,
                        "min_price_factor": min_price_factor,
                        "max_price_factor": max_price_factor,
                        "direct_channel_discount": direct_channel_discount
                    }
                    
                    # Aquí se llamaría al orquestador para guardar la configuración
                    # save_result = orchestrator.save_pricing_config(new_config)
                    
                    # Simulación de guardado
                    time.sleep(1)
                    
                    # Mostrar mensaje de éxito
                    st.success("Configuración guardada correctamente")
        
        # Reglas por temporada
        with st.expander("Reglas por Temporada", expanded=True):
            st.subheader("Factores por Temporada")
            
            # Obtener temporadas
            seasons = config.get_seasons()
            
            if seasons:
                # Crear DataFrame con temporadas
                seasons_data = []
                for season in seasons:
                    seasons_data.append({
                        "nombre": season.get("name", ""),
                        "meses": ", ".join([str(m) for m in season.get("months", [])]),
                        "factor_precio": season.get("price_factor", 1.0),
                        "color": season.get("color", "#ffffff")
                    })
                
                seasons_df = pd.DataFrame(seasons_data)
                
                # Mostrar tabla editable
                edited_seasons = editable_data_table(
                    seasons_df,
                    editable_columns=["factor_precio"],
                    height=300,
                    hide_index=True,
                    key="seasons_table"
                )
                
                # Botón para guardar cambios
                if st.button("Guardar Factores por Temporada", key="save_seasons"):
                    with st.spinner("Guardando factores por temporada..."):
                        # Aquí se llamaría al orquestador para guardar los factores
                        # save_result = orchestrator.save_season_factors(edited_seasons)
                        
                        # Simulación de guardado
                        time.sleep(1)
                        
                        # Mostrar mensaje de éxito
                        st.success("Factores por temporada guardados correctamente")
            else:
                st.warning("No hay temporadas configuradas")
        
        # Reglas por tipo de habitación
        with st.expander("Reglas por Tipo de Habitación", expanded=True):
            st.subheader("Factores por Tipo de Habitación")
            
            # Obtener tipos de habitación
            room_types = config.get_room_types()
            
            if room_types:
                # Crear DataFrame con tipos de habitación
                room_types_data = []
                for rt in room_types:
                    room_types_data.append({
                        "codigo": rt.get("code", ""),
                        "nombre": rt.get("name", ""),
                        "capacidad": rt.get("capacity", 0),
                        "cantidad": rt.get("count", 0),
                        "factor_precio": 1.0  # Valor por defecto
                    })
                
                room_types_df = pd.DataFrame(room_types_data)
                
                # Mostrar tabla editable
                edited_room_types = editable_data_table(
                    room_types_df,
                    editable_columns=["factor_precio"],
                    height=300,
                    hide_index=True,
                    key="room_types_table"
                )
                
                # Botón para guardar cambios
                if st.button("Guardar Factores por Tipo de Habitación", key="save_room_types"):
                    with st.spinner("Guardando factores por tipo de habitación..."):
                        # Aquí se llamaría al orquestador para guardar los factores
                        # save_result = orchestrator.save_room_type_factors(edited_room_types)
                        
                        # Simulación de guardado
                        time.sleep(1)
                        
                        # Mostrar mensaje de éxito
                        st.success("Factores por tipo de habitación guardados correctamente")
            else:
                st.warning("No hay tipos de habitación configurados")
        
        # Reglas por canal
        with st.expander("Reglas por Canal", expanded=True):
            st.subheader("Factores por Canal")
            
            # Obtener canales
            channels = config.get_channels()
            
            if channels:
                # Crear DataFrame con canales
                channels_data = []
                for channel in channels:
                    channels_data.append({
                        "nombre": channel.get("name", ""),
                        "comision": channel.get("commission", 0.0),
                        "prioridad": channel.get("priority", 0),
                        "activo": channel.get("active", True),
                        "factor_precio": 1.0 + channel.get("commission", 0.0)  # Valor por defecto basado en comisión
                    })
                
                channels_df = pd.DataFrame(channels_data)
                
                # Mostrar tabla editable
                edited_channels = editable_data_table(
                    channels_df,
                    editable_columns=["factor_precio", "activo"],
                    height=300,
                    hide_index=True,
                    key="channels_table"
                )
                
                # Botón para guardar cambios
                if st.button("Guardar Factores por Canal", key="save_channels"):
                    with st.spinner("Guardando factores por canal..."):
                        # Aquí se llamaría al orquestador para guardar los factores
                        # save_result = orchestrator.save_channel_factors(edited_channels)
                        
                        # Simulación de guardado
                        time.sleep(1)
                        
                        # Mostrar mensaje de éxito
                        st.success("Factores por canal guardados correctamente")
            else:
                st.warning("No hay canales configurados")
    
    with tab2:
        st.subheader("Generar Recomendaciones de Precios")
        
        # Formulario para generar recomendaciones
        with st.form("recommendations_form"):
            # Selección de fechas
            st.subheader("Período")
            
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input(
                    "Fecha inicio",
                    value=datetime.now().date(),
                    key="rec_start_date"
                )
            
            with col2:
                end_date = st.date_input(
                    "Fecha fin",
                    value=datetime.now().date() + timedelta(days=90),
                    key="rec_end_date"
                )
            
            # Parámetros
            st.subheader("Parámetros")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Obtener tipos de habitación
                room_types = config.get_room_types()
                room_type_options = ["Todos"] + [rt["name"] for rt in room_types]
                
                room_type = st.selectbox(
                    "Tipo de habitación",
                    options=room_type_options,
                    index=0,
                    key="rec_room_type"
                )
            
            with col2:
                # Obtener canales
                channels = config.get_channels()
                channel_options = ["Todos"] + [ch["name"] for ch in channels]
                
                channel = st.selectbox(
                    "Canal",
                    options=channel_options,
                    index=0,
                    key="rec_channel"
                )
            
            # Opciones avanzadas
            with st.expander("Opciones Avanzadas", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    use_competitors = st.checkbox(
                        "Considerar precios de competidores",
                        value=False,
                        key="use_competitors"
                    )
                    
                    min_price = st.number_input(
                        "Precio mínimo",
                        min_value=0,
                        value=150000,
                        step=10000,
                        key="min_price"
                    )
                
                with col2:
                    use_events = st.checkbox(
                        "Considerar eventos",
                        value=True,
                        key="use_events"
                    )
                    
                    max_price = st.number_input(
                        "Precio máximo",
                        min_value=0,
                        value=500000,
                        step=10000,
                        key="max_price"
                    )
            
            # Botón para generar recomendaciones
            submit_button = st.form_submit_button("Generar Recomendaciones")
        
        # Procesar formulario
        if submit_button:
            with st.spinner("Generando recomendaciones de precios..."):
                # Preparar parámetros
                room_type_id = None
                if room_type != "Todos":
                    # Buscar ID del tipo de habitación
                    for rt in room_types:
                        if rt["name"] == room_type:
                            room_type_id = rt.get("id") or rt.get("code")
                            break
                
                channel_id = None
                if channel != "Todos":
                    # Buscar ID del canal
                    for ch in channels:
                        if ch["name"] == channel:
                            channel_id = ch.get("id") or ch.get("name")
                            break
                
                # Opciones avanzadas
                advanced_options = {
                    "use_competitors": use_competitors,
                    "use_events": use_events,
                    "min_price": min_price,
                    "max_price": max_price
                }
                
                # Llamar al orquestador para generar recomendaciones
                # recommendations_result = orchestrator.apply_pricing_rules(
                #     (end_date - start_date).days,
                #     room_type_id,
                #     channel_id,
                #     advanced_options
                # )
                
                # Simulación de resultado
                time.sleep(2)
                
                # Crear datos de ejemplo para las recomendaciones
                dates = pd.date_range(start=start_date, end=end_date)
                
                # Generar datos de recomendaciones
                recommendations_data = []
                
                for date in dates:
                    # Determinar temporada
                    season = "Alta" if date.month in [1, 7, 8, 12] else "Media" if date.month in [2, 3, 9, 10] else "Baja"
                    season_factor = 1.2 if season == "Alta" else 1.0 if season == "Media" else 0.9
                    
                    # Determinar día de la semana
                    weekday_factor = 1.2 if date.weekday() >= 5 else 1.1 if date.weekday() == 4 else 1.0
                    
                    # Calcular ocupación prevista
                    occupancy = min(max(0.7 * season_factor * weekday_factor + np.random.normal(0, 0.05), 0.3), 0.95)
                    
                    # Calcular precios
                    base_price = 250000 * season_factor * weekday_factor
                    min_price_val = base_price * 0.7
                    max_price_val = base_price * 1.3
                    
                    # Calcular precio recomendado basado en ocupación
                    if occupancy < 0.4:
                        # Ocupación baja
                        recommended_price = base_price * 0.9
                    elif occupancy > 0.8:
                        # Ocupación alta
                        recommended_price = base_price * 1.15
                    else:
                        # Ocupación media
                        factor = 0.9 + (occupancy - 0.4) * (1.15 - 0.9) / (0.8 - 0.4)
                        recommended_price = base_price * factor
                    
                    # Asegurar que el precio esté dentro de los límites
                    recommended_price = min(max(recommended_price, min_price_val), max_price_val)
                    
                    # Añadir ruido aleatorio
                    recommended_price = recommended_price + np.random.normal(0, 5000)
                    
                    # Redondear a miles
                    recommended_price = round(recommended_price / 1000) * 1000
                    
                    # Añadir a los datos
                    recommendations_data.append({
                        "fecha": date,
                        "tipo_habitacion": room_type if room_type != "Todos" else "Estándar Doble",
                        "canal": channel if channel != "Todos" else "Booking.com",
                        "temporada": season,
                        "ocupacion_prevista": occupancy,
                        "precio_base": base_price,
                        "precio_min": min_price_val,
                        "precio_max": max_price_val,
                        "precio_recomendado": recommended_price,
                        "estado": "Pendiente"
                    })
                
                recommendations_df = pd.DataFrame(recommendations_data)
                
                # Crear resultado simulado
                recommendations_result = {
                    "success": True,
                    "message": f"Se generaron {len(recommendations_df)} recomendaciones de precios",
                    "data": {
                        "recommendations_df": recommendations_df,
                        "periodo": f"{start_date} a {end_date}",
                        "count": len(recommendations_df)
                    }
                }
                
                # Guardar resultado en session_state
                st.session_state["recommendations_result"] = recommendations_result
                
                # Mostrar mensaje de éxito
                st.success(recommendations_result["message"])
        
        # Mostrar resultados si existen
        if "recommendations_result" in st.session_state and st.session_state["recommendations_result"]["success"]:
            recommendations_data = st.session_state["recommendations_result"]["data"]
            recommendations_df = recommendations_data["recommendations_df"]
            
            # Mostrar gráfico de precios recomendados
            st.subheader("Precios Recomendados")
            
            # Crear gráfico
            chart(
                data=recommendations_df,
                chart_type="line",
                x="fecha",
                y=["precio_base", "precio_min", "precio_max", "precio_recomendado"],
                title="Precios Recomendados",
                labels={
                    "fecha": "Fecha",
                    "precio_base": "Precio Base",
                    "precio_min": "Precio Mínimo",
                    "precio_max": "Precio Máximo",
                    "precio_recomendado": "Precio Recomendado"
                }
            )
            
            # Mostrar tabla de recomendaciones
            st.subheader("Tabla de Recomendaciones")
            
            data_table(
                recommendations_df,
                height=400,
                hide_index=True,
                key="recommendations_table"
            )
            
            # Botón para guardar recomendaciones
            if st.button("Guardar Recomendaciones", key="save_recommendations_button"):
                with st.spinner("Guardando recomendaciones..."):
                    # Aquí se llamaría al orquestador para guardar las recomendaciones
                    # save_result = orchestrator.save_recommendations(recommendations_df)
                    
                    # Simulación de guardado
                    time.sleep(1)
                    
                    # Mostrar mensaje de éxito
                    st.success("Recomendaciones guardadas correctamente")
    
    with tab3:
        st.subheader("Análisis de Precios")
        
        # Selección de período para análisis
        col1, col2 = st.columns(2)
        
        with col1:
            # Selector de fechas
            start_date, end_date = date_selector(key="analysis_date", default_days=90)
        
        with col2:
            # Selector de tipo de habitación
            room_types = config.get_room_types()
            room_type_options = ["Todos"] + [rt["name"] for rt in room_types]
            
            room_type = st.selectbox(
                "Tipo de habitación",
                options=room_type_options,
                index=0,
                key="analysis_room_type"
            )
        
        # Botón para analizar precios
        if st.button("Analizar Precios", key="analyze_prices_button"):
            with st.spinner("Analizando precios..."):
                # Preparar parámetros
                room_type_id = None
                if room_type != "Todos":
                    # Buscar ID del tipo de habitación
                    for rt in room_types:
                        if rt["name"] == room_type:
                            room_type_id = rt.get("id") or rt.get("code")
                            break
                
                # Aquí se llamaría al orquestador para analizar los precios
                # price_analysis = orchestrator.analyze_prices(
                #     start_date.strftime("%Y-%m-%d") if start_date else None,
                #     end_date.strftime("%Y-%m-%d") if end_date else None,
                #     room_type_id
                # )
                
                # Simulación de análisis
                time.sleep(2)
                
                # Crear datos de ejemplo para el análisis de precios
                if start_date and end_date:
                    dates = pd.date_range(start=start_date, end=end_date)
                else:
                    analysis_start = datetime.now().date() - timedelta(days=90)
                    analysis_end = datetime.now().date()
                    dates = pd.date_range(start=analysis_start, end=analysis_end)
                
                # Generar datos de precios
                price_data = []
                
                # Obtener canales
                channels = config.get_channels()
                channel_names = [ch["name"] for ch in channels]
                
                for date in dates:
                    # Determinar temporada
                    season = "Alta" if date.month in [1, 7, 8, 12] else "Media" if date.month in [2, 3, 9, 10] else "Baja"
                    season_factor = 1.2 if season == "Alta" else 1.0 if season == "Media" else 0.9
                    
                    # Determinar día de la semana
                    weekday_factor = 1.2 if date.weekday() >= 5 else 1.1 if date.weekday() == 4 else 1.0
                    
                    # Calcular ocupación
                    occupancy = min(max(0.7 * season_factor * weekday_factor + np.random.normal(0, 0.05), 0.3), 0.95)
                    
                    # Calcular precio base
                    base_price = 250000 * season_factor * weekday_factor
                    
                    # Añadir precios por canal
                    for channel in channel_names:
                        # Calcular comisión
                        commission = 0.0
                        for ch in channels:
                            if ch["name"] == channel:
                                commission = ch.get("commission", 0.0)
                                break
                        
                        # Calcular precio con comisión
                        channel_price = base_price / (1 - commission) if commission < 1 else base_price
                        
                        # Añadir ruido aleatorio
                        channel_price = channel_price + np.random.normal(0, 5000)
                        
                        # Redondear a miles
                        channel_price = round(channel_price / 1000) * 1000
                        
                        # Añadir a los datos
                        price_data.append({
                            "fecha": date,
                            "tipo_habitacion": room_type if room_type != "Todos" else "Estándar Doble",
                            "canal": channel,
                            "temporada": season,
                            "ocupacion": occupancy,
                            "precio": channel_price
                        })
                
                price_df = pd.DataFrame(price_data)
                
                # Guardar en session_state
                st.session_state["price_analysis_df"] = price_df
        
        # Mostrar resultados de análisis
        if "price_analysis_df" in st.session_state:
            price_df = st.session_state["price_analysis_df"]
            
            # Mostrar gráfico de precios por canal
            st.subheader("Precios por Canal")
            
            # Filtrar por canal
            channels = price_df["canal"].unique()
            selected_channels = st.multiselect(
                "Seleccionar canales",
                options=channels,
                default=channels[:2],
                key="selected_channels"
            )
            
            if selected_channels:
                # Filtrar datos
                filtered_df = price_df[price_df["canal"].isin(selected_channels)]
                
                # Crear gráfico
                chart(
                    data=filtered_df,
                    chart_type="line",
                    x="fecha",
                    y="precio",
                    color="canal",
                    title="Precios por Canal"
                )
            
            # Mostrar gráfico de precios vs ocupación
            st.subheader("Precios vs Ocupación")
            
            # Filtrar por canal
            selected_channel = st.selectbox(
                "Canal",
                options=channels,
                index=0,
                key="selected_channel_scatter"
            )
            
            # Filtrar datos
            channel_df = price_df[price_df["canal"] == selected_channel]
            
            # Crear gráfico
            chart(
                data=channel_df,
                chart_type="scatter",
                x="ocupacion",
                y="precio",
                color="temporada",
                title=f"Precios vs Ocupación - {selected_channel}"
            )
            
            # Mostrar estadísticas de precios
            st.subheader("Estadísticas de Precios")
            
            # Agrupar por canal y temporada
            stats_df = price_df.groupby(["canal", "temporada"]).agg({
                "precio": ["mean", "min", "max", "std"]
            }).reset_index()
            
            # Aplanar columnas multinivel
            stats_df.columns = ["_".join(col).strip("_") for col in stats_df.columns.values]
            
            # Renombrar columnas
            stats_df = stats_df.rename(columns={
                "precio_mean": "precio_promedio",
                "precio_min": "precio_minimo",
                "precio_max": "precio_maximo",
                "precio_std": "precio_desviacion"
            })
            
            # Mostrar tabla
            data_table(
                stats_df,
                height=300,
                hide_index=True,
                key="price_stats_table"
            )
            
            # Mostrar distribución de precios
            st.subheader("Distribución de Precios")
            
            # Crear histograma
            chart(
                data=price_df,
                chart_type="bar",
                x="canal",
                y="precio",
                title="Distribución de Precios por Canal"
            )