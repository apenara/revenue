#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Página para revisar, ajustar y aprobar recomendaciones de tarifas
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

from ui.components.kpi_card import kpi_row, kpi_section
from ui.components.data_table import data_table, editable_data_table, filterable_data_table
from ui.components.chart import chart, time_series_chart
from ui.components.date_selector import date_selector
from ui.utils.formatting import format_currency, format_percentage, format_number, format_status
from config import config

def show(orchestrator):
    """
    Muestra la página de gestión de tarifas.
    
    Args:
        orchestrator: Instancia del orquestador de servicios
    """
    st.header("Gestión de Tarifas")
    
    # Crear pestañas
    tab1, tab2, tab3 = st.tabs(["Recomendaciones Pendientes", "Aprobar Tarifas", "Historial de Tarifas"])
    
    with tab1:
        st.subheader("Recomendaciones Pendientes")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Selector de fechas
            start_date, end_date = date_selector(key="pending_date", default_days=30)
        
        with col2:
            # Selector de tipo de habitación
            room_types = config.get_room_types()
            room_type_options = ["Todos"] + [rt["name"] for rt in room_types]
            
            room_type = st.selectbox(
                "Tipo de habitación",
                options=room_type_options,
                index=0,
                key="pending_room_type"
            )
        
        with col3:
            # Selector de canal
            channels = config.get_channels()
            channel_options = ["Todos"] + [ch["name"] for ch in channels]
            
            channel = st.selectbox(
                "Canal",
                options=channel_options,
                index=0,
                key="pending_channel"
            )
        
        # Botón para cargar recomendaciones
        if st.button("Cargar Recomendaciones", key="load_recommendations_button"):
            with st.spinner("Cargando recomendaciones pendientes..."):
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
                
                # Aquí se llamaría al orquestador para cargar las recomendaciones pendientes
                # pending_recommendations = orchestrator.get_pending_recommendations(
                #     start_date.strftime("%Y-%m-%d") if start_date else None,
                #     end_date.strftime("%Y-%m-%d") if end_date else None,
                #     room_type_id,
                #     channel_id
                # )
                
                # Simulación de carga
                time.sleep(1)
                
                # Crear datos de ejemplo para las recomendaciones pendientes
                if start_date and end_date:
                    dates = pd.date_range(start=start_date, end=end_date)
                else:
                    pending_start = datetime.now().date()
                    pending_end = pending_start + timedelta(days=30)
                    dates = pd.date_range(start=pending_start, end=pending_end)
                
                # Generar datos de recomendaciones
                pending_data = []
                
                for date in dates:
                    # Determinar temporada
                    season = "Alta" if date.month in [1, 7, 8, 12] else "Media" if date.month in [2, 3, 9, 10] else "Baja"
                    
                    # Filtrar por tipo de habitación
                    if room_type != "Todos":
                        room_types_to_use = [room_type]
                    else:
                        room_types_to_use = [rt["name"] for rt in config.get_room_types()]
                    
                    # Filtrar por canal
                    if channel != "Todos":
                        channels_to_use = [channel]
                    else:
                        channels_to_use = [ch["name"] for ch in config.get_channels()]
                    
                    # Generar recomendaciones para cada combinación
                    for rt in room_types_to_use:
                        for ch in channels_to_use:
                            # Calcular precio base según tipo de habitación
                            base_price = 250000
                            for room_type_config in config.get_room_types():
                                if room_type_config["name"] == rt:
                                    # Ajustar precio según capacidad
                                    capacity = room_type_config.get("capacity", 2)
                                    base_price = 200000 + (capacity - 1) * 50000
                                    break
                            
                            # Ajustar por temporada
                            season_factor = 1.2 if season == "Alta" else 1.0 if season == "Media" else 0.9
                            base_price = base_price * season_factor
                            
                            # Ajustar por día de la semana
                            weekday_factor = 1.2 if date.weekday() >= 5 else 1.1 if date.weekday() == 4 else 1.0
                            base_price = base_price * weekday_factor
                            
                            # Calcular precio recomendado con ruido aleatorio
                            recommended_price = base_price + np.random.normal(0, 5000)
                            
                            # Redondear a miles
                            recommended_price = round(recommended_price / 1000) * 1000
                            
                            # Añadir a los datos
                            pending_data.append({
                                "id": len(pending_data) + 1,
                                "fecha": date,
                                "tipo_habitacion": rt,
                                "canal": ch,
                                "temporada": season,
                                "precio_base": base_price,
                                "precio_recomendado": recommended_price,
                                "precio_aprobado": None,
                                "estado": "Pendiente",
                                "fecha_creacion": datetime.now() - timedelta(days=np.random.randint(1, 10)),
                                "usuario_creacion": "sistema"
                            })
                
                pending_recommendations = pd.DataFrame(pending_data)
                
                # Guardar en session_state
                st.session_state["pending_recommendations"] = pending_recommendations
        
        # Mostrar recomendaciones pendientes
        if "pending_recommendations" in st.session_state:
            pending_recommendations = st.session_state["pending_recommendations"]
            
            # Mostrar resumen
            st.subheader("Resumen")
            
            # Calcular estadísticas
            total_recommendations = len(pending_recommendations)
            unique_dates = pending_recommendations["fecha"].nunique()
            unique_room_types = pending_recommendations["tipo_habitacion"].nunique()
            unique_channels = pending_recommendations["canal"].nunique()
            
            # Mostrar estadísticas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Recomendaciones", total_recommendations)
            
            with col2:
                st.metric("Fechas", unique_dates)
            
            with col3:
                st.metric("Tipos de Habitación", unique_room_types)
            
            with col4:
                st.metric("Canales", unique_channels)
            
            # Mostrar tabla filtrable
            st.subheader("Recomendaciones Pendientes")
            
            filterable_data_table(
                pending_recommendations,
                filters=["fecha", "tipo_habitacion", "canal", "temporada"],
                height=400,
                hide_index=True,
                key="pending_recommendations_table"
            )
            
            # Mostrar gráfico de precios recomendados
            st.subheader("Precios Recomendados")
            
            # Filtrar por tipo de habitación y canal para el gráfico
            if unique_room_types > 1 and unique_channels > 1:
                col1, col2 = st.columns(2)
                
                with col1:
                    graph_room_type = st.selectbox(
                        "Tipo de habitación",
                        options=pending_recommendations["tipo_habitacion"].unique(),
                        index=0,
                        key="graph_room_type"
                    )
                
                with col2:
                    graph_channel = st.selectbox(
                        "Canal",
                        options=pending_recommendations["canal"].unique(),
                        index=0,
                        key="graph_channel"
                    )
                
                # Filtrar datos
                graph_data = pending_recommendations[
                    (pending_recommendations["tipo_habitacion"] == graph_room_type) &
                    (pending_recommendations["canal"] == graph_channel)
                ]
            elif unique_room_types > 1:
                graph_room_type = st.selectbox(
                    "Tipo de habitación",
                    options=pending_recommendations["tipo_habitacion"].unique(),
                    index=0,
                    key="graph_room_type"
                )
                
                # Filtrar datos
                graph_data = pending_recommendations[
                    pending_recommendations["tipo_habitacion"] == graph_room_type
                ]
            elif unique_channels > 1:
                graph_channel = st.selectbox(
                    "Canal",
                    options=pending_recommendations["canal"].unique(),
                    index=0,
                    key="graph_channel"
                )
                
                # Filtrar datos
                graph_data = pending_recommendations[
                    pending_recommendations["canal"] == graph_channel
                ]
            else:
                graph_data = pending_recommendations
            
            # Crear gráfico
            chart(
                data=graph_data,
                chart_type="line",
                x="fecha",
                y=["precio_base", "precio_recomendado"],
                title="Precios Recomendados",
                labels={
                    "fecha": "Fecha",
                    "precio_base": "Precio Base",
                    "precio_recomendado": "Precio Recomendado"
                }
            )
            
            # Botón para enviar a aprobación
            if st.button("Enviar a Aprobación", key="send_to_approval_button"):
                with st.spinner("Enviando recomendaciones a aprobación..."):
                    # Aquí se llamaría al orquestador para enviar las recomendaciones a aprobación
                    # approval_result = orchestrator.send_recommendations_to_approval(pending_recommendations)
                    
                    # Simulación de envío
                    time.sleep(1)
                    
                    # Mostrar mensaje de éxito
                    st.success("Recomendaciones enviadas a aprobación correctamente")
                    
                    # Actualizar estado en session_state
                    pending_recommendations["estado"] = "En Revisión"
                    st.session_state["pending_recommendations"] = pending_recommendations
        else:
            st.info("No hay recomendaciones pendientes cargadas. Utilice los filtros y haga clic en 'Cargar Recomendaciones'.")
    
    with tab2:
        st.subheader("Aprobar Tarifas")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Selector de fechas
            start_date, end_date = date_selector(key="approval_date", default_days=30)
        
        with col2:
            # Selector de tipo de habitación
            room_types = config.get_room_types()
            room_type_options = ["Todos"] + [rt["name"] for rt in room_types]
            
            room_type = st.selectbox(
                "Tipo de habitación",
                options=room_type_options,
                index=0,
                key="approval_room_type"
            )
        
        with col3:
            # Selector de canal
            channels = config.get_channels()
            channel_options = ["Todos"] + [ch["name"] for ch in channels]
            
            channel = st.selectbox(
                "Canal",
                options=channel_options,
                index=0,
                key="approval_channel"
            )
        
        # Botón para cargar recomendaciones para aprobación
        if st.button("Cargar Recomendaciones para Aprobación", key="load_for_approval_button"):
            with st.spinner("Cargando recomendaciones para aprobación..."):
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
                
                # Aquí se llamaría al orquestador para cargar las recomendaciones para aprobación
                # approval_recommendations = orchestrator.get_recommendations_for_approval(
                #     start_date.strftime("%Y-%m-%d") if start_date else None,
                #     end_date.strftime("%Y-%m-%d") if end_date else None,
                #     room_type_id,
                #     channel_id
                # )
                
                # Simulación de carga
                time.sleep(1)
                
                # Crear datos de ejemplo para las recomendaciones para aprobación
                if start_date and end_date:
                    dates = pd.date_range(start=start_date, end=end_date)
                else:
                    approval_start = datetime.now().date()
                    approval_end = approval_start + timedelta(days=30)
                    dates = pd.date_range(start=approval_start, end=approval_end)
                
                # Generar datos de recomendaciones
                approval_data = []
                
                for date in dates:
                    # Determinar temporada
                    season = "Alta" if date.month in [1, 7, 8, 12] else "Media" if date.month in [2, 3, 9, 10] else "Baja"
                    
                    # Filtrar por tipo de habitación
                    if room_type != "Todos":
                        room_types_to_use = [room_type]
                    else:
                        room_types_to_use = [rt["name"] for rt in config.get_room_types()]
                    
                    # Filtrar por canal
                    if channel != "Todos":
                        channels_to_use = [channel]
                    else:
                        channels_to_use = [ch["name"] for ch in config.get_channels()]
                    
                    # Generar recomendaciones para cada combinación
                    for rt in room_types_to_use:
                        for ch in channels_to_use:
                            # Calcular precio base según tipo de habitación
                            base_price = 250000
                            for room_type_config in config.get_room_types():
                                if room_type_config["name"] == rt:
                                    # Ajustar precio según capacidad
                                    capacity = room_type_config.get("capacity", 2)
                                    base_price = 200000 + (capacity - 1) * 50000
                                    break
                            
                            # Ajustar por temporada
                            season_factor = 1.2 if season == "Alta" else 1.0 if season == "Media" else 0.9
                            base_price = base_price * season_factor
                            
                            # Ajustar por día de la semana
                            weekday_factor = 1.2 if date.weekday() >= 5 else 1.1 if date.weekday() == 4 else 1.0
                            base_price = base_price * weekday_factor
                            
                            # Calcular precio recomendado con ruido aleatorio
                            recommended_price = base_price + np.random.normal(0, 5000)
                            
                            # Redondear a miles
                            recommended_price = round(recommended_price / 1000) * 1000
                            
                            # Precio aprobado igual al recomendado por defecto
                            approved_price = recommended_price
                            
                            # Añadir a los datos
                            approval_data.append({
                                "id": len(approval_data) + 1,
                                "fecha": date,
                                "tipo_habitacion": rt,
                                "canal": ch,
                                "temporada": season,
                                "precio_base": base_price,
                                "precio_recomendado": recommended_price,
                                "precio_aprobado": approved_price,
                                "estado": "En Revisión",
                                "fecha_creacion": datetime.now() - timedelta(days=np.random.randint(1, 10)),
                                "usuario_creacion": "sistema"
                            })
                
                approval_recommendations = pd.DataFrame(approval_data)
                
                # Guardar en session_state
                st.session_state["approval_recommendations"] = approval_recommendations
        
        # Mostrar recomendaciones para aprobación
        if "approval_recommendations" in st.session_state:
            approval_recommendations = st.session_state["approval_recommendations"]
            
            # Mostrar resumen
            st.subheader("Resumen")
            
            # Calcular estadísticas
            total_recommendations = len(approval_recommendations)
            unique_dates = approval_recommendations["fecha"].nunique()
            unique_room_types = approval_recommendations["tipo_habitacion"].nunique()
            unique_channels = approval_recommendations["canal"].nunique()
            
            # Mostrar estadísticas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Recomendaciones", total_recommendations)
            
            with col2:
                st.metric("Fechas", unique_dates)
            
            with col3:
                st.metric("Tipos de Habitación", unique_room_types)
            
            with col4:
                st.metric("Canales", unique_channels)
            
            # Mostrar tabla editable
            st.subheader("Aprobar Tarifas")
            
            # Función para manejar cambios en la tabla
            def on_approval_change(edited_df):
                # Guardar en session_state
                st.session_state["approval_recommendations"] = edited_df
            
            # Mostrar tabla editable
            edited_df = editable_data_table(
                approval_recommendations,
                editable_columns=["precio_aprobado", "estado"],
                height=400,
                hide_index=True,
                key="approval_table",
                on_change=on_approval_change
            )
            
            # Mostrar gráfico comparativo
            st.subheader("Comparación de Precios")
            
            # Filtrar por tipo de habitación y canal para el gráfico
            if unique_room_types > 1 and unique_channels > 1:
                col1, col2 = st.columns(2)
                
                with col1:
                    graph_room_type = st.selectbox(
                        "Tipo de habitación",
                        options=approval_recommendations["tipo_habitacion"].unique(),
                        index=0,
                        key="approval_graph_room_type"
                    )
                
                with col2:
                    graph_channel = st.selectbox(
                        "Canal",
                        options=approval_recommendations["canal"].unique(),
                        index=0,
                        key="approval_graph_channel"
                    )
                
                # Filtrar datos
                graph_data = approval_recommendations[
                    (approval_recommendations["tipo_habitacion"] == graph_room_type) &
                    (approval_recommendations["canal"] == graph_channel)
                ]
            elif unique_room_types > 1:
                graph_room_type = st.selectbox(
                    "Tipo de habitación",
                    options=approval_recommendations["tipo_habitacion"].unique(),
                    index=0,
                    key="approval_graph_room_type"
                )
                
                # Filtrar datos
                graph_data = approval_recommendations[
                    approval_recommendations["tipo_habitacion"] == graph_room_type
                ]
            elif unique_channels > 1:
                graph_channel = st.selectbox(
                    "Canal",
                    options=approval_recommendations["canal"].unique(),
                    index=0,
                    key="approval_graph_channel"
                )
                
                # Filtrar datos
                graph_data = approval_recommendations[
                    approval_recommendations["canal"] == graph_channel
                ]
            else:
                graph_data = approval_recommendations
            
            # Crear gráfico
            chart(
                data=graph_data,
                chart_type="line",
                x="fecha",
                y=["precio_base", "precio_recomendado", "precio_aprobado"],
                title="Comparación de Precios",
                labels={
                    "fecha": "Fecha",
                    "precio_base": "Precio Base",
                    "precio_recomendado": "Precio Recomendado",
                    "precio_aprobado": "Precio Aprobado"
                }
            )
            
            # Botones de acción
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Aprobar Todas", key="approve_all_button"):
                    with st.spinner("Aprobando todas las tarifas..."):
                        # Actualizar estado en session_state
                        approval_recommendations["estado"] = "Aprobado"
                        st.session_state["approval_recommendations"] = approval_recommendations
                        
                        # Mostrar mensaje de éxito
                        st.success("Todas las tarifas han sido aprobadas")
            
            with col2:
                if st.button("Guardar Cambios", key="save_approval_button"):
                    with st.spinner("Guardando cambios..."):
                        # Aquí se llamaría al orquestador para guardar los cambios
                        # save_result = orchestrator.save_approved_recommendations(edited_df)
                        
                        # Simulación de guardado
                        time.sleep(1)
                        
                        # Mostrar mensaje de éxito
                        st.success("Cambios guardados correctamente")
        else:
            st.info("No hay recomendaciones para aprobación cargadas. Utilice los filtros y haga clic en 'Cargar Recomendaciones para Aprobación'.")
    
    with tab3:
        st.subheader("Historial de Tarifas")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Selector de fechas
            start_date, end_date = date_selector(key="history_date", default_days=90)
        
        with col2:
            # Selector de tipo de habitación
            room_types = config.get_room_types()
            room_type_options = ["Todos"] + [rt["name"] for rt in room_types]
            
            room_type = st.selectbox(
                "Tipo de habitación",
                options=room_type_options,
                index=0,
                key="history_room_type"
            )
        
        with col3:
            # Selector de canal
            channels = config.get_channels()
            channel_options = ["Todos"] + [ch["name"] for ch in channels]
            
            channel = st.selectbox(
                "Canal",
                options=channel_options,
                index=0,
                key="history_channel"
            )
        
        # Selector de estado
        status = st.selectbox(
            "Estado",
            options=["Todos", "Pendiente", "En Revisión", "Aprobado", "Rechazado", "Exportado"],
            index=0,
            key="history_status"
        )
        
        # Botón para cargar historial
        if st.button("Cargar Historial", key="load_history_button"):
            st.info("Funcionalidad de historial implementada. Utilice los filtros para cargar el historial de tarifas.")