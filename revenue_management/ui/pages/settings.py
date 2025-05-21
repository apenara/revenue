#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Página para configurar parámetros del sistema
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

from ui.components.data_table import data_table, editable_data_table
from config import config

def show(orchestrator):
    """
    Muestra la página de configuración.
    
    Args:
        orchestrator: Instancia del orquestador de servicios
    """
    st.header("Configuración del Sistema")
    
    # Crear pestañas
    tab1, tab2, tab3, tab4 = st.tabs(["General", "Tipos de Habitación", "Canales", "Temporadas"])
    
    with tab1:
        st.subheader("Configuración General")
        
        # Información del hotel
        hotel_info = config.get_hotel_info()
        
        with st.form("hotel_info_form"):
            st.subheader("Información del Hotel")
            
            hotel_name = st.text_input(
                "Nombre del Hotel",
                value=hotel_info.get("name", "Hotel Playa Club")
            )
            
            hotel_location = st.text_input(
                "Ubicación",
                value=hotel_info.get("location", "Cartagena, Colombia")
            )
            
            total_rooms = st.number_input(
                "Total de Habitaciones",
                min_value=1,
                value=hotel_info.get("total_rooms", 79)
            )
            
            # Botón para guardar
            submit_button = st.form_submit_button("Guardar Información del Hotel")
        
        if submit_button:
            with st.spinner("Guardando información del hotel..."):
                # Aquí se llamaría al orquestador para guardar la información
                # save_result = orchestrator.save_hotel_info(hotel_name, hotel_location, total_rooms)
                
                # Simulación de guardado
                time.sleep(1)
                
                # Mostrar mensaje de éxito
                st.success("Información del hotel guardada correctamente")
        
        # Configuración de forecasting
        forecasting_config = config.get_forecasting_config()
        
        with st.form("forecasting_config_form"):
            st.subheader("Configuración de Forecasting")
            
            forecast_days = st.number_input(
                "Días a pronosticar",
                min_value=1,
                max_value=365,
                value=forecasting_config.get("forecast_days", 90)
            )
            
            seasonality_mode = st.selectbox(
                "Modo de estacionalidad",
                options=["multiplicative", "additive"],
                index=0 if forecasting_config.get("seasonality_mode", "multiplicative") == "multiplicative" else 1
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                weekly_seasonality = st.checkbox(
                    "Estacionalidad semanal",
                    value=forecasting_config.get("weekly_seasonality", True)
                )
                
                yearly_seasonality = st.checkbox(
                    "Estacionalidad anual",
                    value=forecasting_config.get("yearly_seasonality", True)
                )
            
            with col2:
                daily_seasonality = st.checkbox(
                    "Estacionalidad diaria",
                    value=forecasting_config.get("daily_seasonality", False)
                )
                
                include_holidays = st.checkbox(
                    "Incluir festivos",
                    value=forecasting_config.get("include_holidays", True)
                )
            
            # Botón para guardar
            submit_button = st.form_submit_button("Guardar Configuración de Forecasting")
        
        if submit_button:
            with st.spinner("Guardando configuración de forecasting..."):
                # Aquí se llamaría al orquestador para guardar la configuración
                # save_result = orchestrator.save_forecasting_config(
                #     forecast_days,
                #     seasonality_mode,
                #     weekly_seasonality,
                #     yearly_seasonality,
                #     daily_seasonality,
                #     include_holidays
                # )
                
                # Simulación de guardado
                time.sleep(1)
                
                # Mostrar mensaje de éxito
                st.success("Configuración de forecasting guardada correctamente")
        
        # Configuración de pricing
        pricing_config = config.get_pricing_rules()
        
        with st.form("pricing_config_form"):
            st.subheader("Configuración de Pricing")
            
            col1, col2 = st.columns(2)
            
            with col1:
                min_occupancy = st.slider(
                    "Umbral de ocupación baja",
                    min_value=0.0,
                    max_value=1.0,
                    value=pricing_config.get("min_occupancy_threshold", 0.4),
                    step=0.05,
                    format="%.2f"
                )
                
                low_occupancy_factor = st.slider(
                    "Factor para ocupación baja",
                    min_value=0.5,
                    max_value=1.0,
                    value=pricing_config.get("low_occupancy_factor", 0.9),
                    step=0.05,
                    format="%.2f"
                )
                
                min_price_factor = st.slider(
                    "Factor mínimo de precio",
                    min_value=0.5,
                    max_value=1.0,
                    value=pricing_config.get("min_price_factor", 0.7),
                    step=0.05,
                    format="%.2f"
                )
            
            with col2:
                max_occupancy = st.slider(
                    "Umbral de ocupación alta",
                    min_value=0.0,
                    max_value=1.0,
                    value=pricing_config.get("max_occupancy_threshold", 0.8),
                    step=0.05,
                    format="%.2f"
                )
                
                high_occupancy_factor = st.slider(
                    "Factor para ocupación alta",
                    min_value=1.0,
                    max_value=1.5,
                    value=pricing_config.get("high_occupancy_factor", 1.15),
                    step=0.05,
                    format="%.2f"
                )
                
                max_price_factor = st.slider(
                    "Factor máximo de precio",
                    min_value=1.0,
                    max_value=2.0,
                    value=pricing_config.get("max_price_factor", 1.3),
                    step=0.05,
                    format="%.2f"
                )
            
            direct_channel_discount = st.slider(
                "Descuento para canal directo",
                min_value=0.0,
                max_value=0.2,
                value=pricing_config.get("direct_channel_discount", 0.05),
                step=0.01,
                format="%.2f"
            )
            
            # Botón para guardar
            submit_button = st.form_submit_button("Guardar Configuración de Pricing")
        
        if submit_button:
            with st.spinner("Guardando configuración de pricing..."):
                # Aquí se llamaría al orquestador para guardar la configuración
                # save_result = orchestrator.save_pricing_config(
                #     min_occupancy,
                #     max_occupancy,
                #     low_occupancy_factor,
                #     high_occupancy_factor,
                #     min_price_factor,
                #     max_price_factor,
                #     direct_channel_discount
                # )
                
                # Simulación de guardado
                time.sleep(1)
                
                # Mostrar mensaje de éxito
                st.success("Configuración de pricing guardada correctamente")
    
    with tab2:
        st.subheader("Tipos de Habitación")
        
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
                    "cantidad": rt.get("count", 0)
                })
            
            room_types_df = pd.DataFrame(room_types_data)
            
            # Mostrar tabla editable
            edited_room_types = editable_data_table(
                room_types_df,
                editable_columns=["codigo", "nombre", "capacidad", "cantidad"],
                height=300,
                hide_index=True,
                key="room_types_table"
            )
            
            # Botón para guardar cambios
            if st.button("Guardar Tipos de Habitación", key="save_room_types"):
                with st.spinner("Guardando tipos de habitación..."):
                    # Aquí se llamaría al orquestador para guardar los tipos de habitación
                    # save_result = orchestrator.save_room_types(edited_room_types)
                    
                    # Simulación de guardado
                    time.sleep(1)
                    
                    # Mostrar mensaje de éxito
                    st.success("Tipos de habitación guardados correctamente")
            
            # Botón para añadir nuevo tipo de habitación
            if st.button("Añadir Tipo de Habitación", key="add_room_type"):
                # Añadir fila vacía al DataFrame
                new_row = pd.DataFrame([{
                    "codigo": "",
                    "nombre": "",
                    "capacidad": 2,
                    "cantidad": 1
                }])
                
                # Concatenar con el DataFrame existente
                edited_room_types = pd.concat([edited_room_types, new_row], ignore_index=True)
                
                # Actualizar tabla
                st.experimental_rerun()
        else:
            st.warning("No hay tipos de habitación configurados")
    
    with tab3:
        st.subheader("Canales de Distribución")
        
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
                    "activo": channel.get("active", True)
                })
            
            channels_df = pd.DataFrame(channels_data)
            
            # Mostrar tabla editable
            edited_channels = editable_data_table(
                channels_df,
                editable_columns=["nombre", "comision", "prioridad", "activo"],
                height=300,
                hide_index=True,
                key="channels_table"
            )
            
            # Botón para guardar cambios
            if st.button("Guardar Canales", key="save_channels"):
                with st.spinner("Guardando canales..."):
                    # Aquí se llamaría al orquestador para guardar los canales
                    # save_result = orchestrator.save_channels(edited_channels)
                    
                    # Simulación de guardado
                    time.sleep(1)
                    
                    # Mostrar mensaje de éxito
                    st.success("Canales guardados correctamente")
            
            # Botón para añadir nuevo canal
            if st.button("Añadir Canal", key="add_channel"):
                # Añadir fila vacía al DataFrame
                new_row = pd.DataFrame([{
                    "nombre": "",
                    "comision": 0.0,
                    "prioridad": len(channels) + 1,
                    "activo": True
                }])
                
                # Concatenar con el DataFrame existente
                edited_channels = pd.concat([edited_channels, new_row], ignore_index=True)
                
                # Actualizar tabla
                st.experimental_rerun()
        else:
            st.warning("No hay canales configurados")
    
    with tab4:
        st.subheader("Temporadas")
        
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
                editable_columns=["nombre", "meses", "factor_precio", "color"],
                height=300,
                hide_index=True,
                key="seasons_table"
            )
            
            # Botón para guardar cambios
            if st.button("Guardar Temporadas", key="save_seasons"):
                with st.spinner("Guardando temporadas..."):
                    # Aquí se llamaría al orquestador para guardar las temporadas
                    # save_result = orchestrator.save_seasons(edited_seasons)
                    
                    # Simulación de guardado
                    time.sleep(1)
                    
                    # Mostrar mensaje de éxito
                    st.success("Temporadas guardadas correctamente")
            
            # Botón para añadir nueva temporada
            if st.button("Añadir Temporada", key="add_season"):
                # Añadir fila vacía al DataFrame
                new_row = pd.DataFrame([{
                    "nombre": "",
                    "meses": "",
                    "factor_precio": 1.0,
                    "color": "#ffffff"
                }])
                
                # Concatenar con el DataFrame existente
                edited_seasons = pd.concat([edited_seasons, new_row], ignore_index=True)
                
                # Actualizar tabla
                st.experimental_rerun()
        else:
            st.warning("No hay temporadas configuradas")