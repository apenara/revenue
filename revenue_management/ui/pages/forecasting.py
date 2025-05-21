#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Página para generar y ajustar previsiones
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

from ui.components.kpi_card import kpi_row, kpi_section
from ui.components.data_table import data_table, editable_data_table
from ui.components.chart import chart, time_series_chart, comparison_chart
from ui.components.date_selector import date_selector
from ui.utils.formatting import format_currency, format_percentage, format_number
from config import config

def show(orchestrator):
    """
    Muestra la página de forecasting.
    
    Args:
        orchestrator: Instancia del orquestador de servicios
    """
    st.header("Forecasting")
    
    # Crear pestañas
    tab1, tab2, tab3 = st.tabs(["Generar Pronósticos", "Ajustar Pronósticos", "Análisis de Precisión"])
    
    with tab1:
        st.subheader("Generar Pronósticos")
        
        # Formulario para generar pronósticos
        with st.form("forecast_form"):
            # Selección de fechas para datos históricos
            st.subheader("Datos Históricos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input(
                    "Fecha inicio",
                    value=datetime.now().date() - timedelta(days=365),
                    key="forecast_start_date"
                )
            
            with col2:
                end_date = st.date_input(
                    "Fecha fin",
                    value=datetime.now().date(),
                    key="forecast_end_date"
                )
            
            # Parámetros de pronóstico
            st.subheader("Parámetros de Pronóstico")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                forecast_days = st.number_input(
                    "Días a pronosticar",
                    min_value=1,
                    max_value=365,
                    value=90,
                    step=1,
                    key="forecast_days"
                )
            
            with col2:
                # Obtener tipos de habitación de la configuración
                room_types = config.get_room_types()
                room_type_options = ["Todos"] + [rt["name"] for rt in room_types]
                
                room_type = st.selectbox(
                    "Tipo de habitación",
                    options=room_type_options,
                    index=0,
                    key="forecast_room_type"
                )
            
            with col3:
                forecast_model = st.selectbox(
                    "Modelo de pronóstico",
                    options=["Prophet", "ARIMA", "Exponential Smoothing", "LSTM"],
                    index=0,
                    key="forecast_model"
                )
            
            # Parámetros avanzados
            with st.expander("Parámetros Avanzados", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    seasonality_mode = st.selectbox(
                        "Modo de estacionalidad",
                        options=["multiplicative", "additive"],
                        index=0,
                        key="seasonality_mode"
                    )
                    
                    weekly_seasonality = st.checkbox(
                        "Estacionalidad semanal",
                        value=True,
                        key="weekly_seasonality"
                    )
                    
                    yearly_seasonality = st.checkbox(
                        "Estacionalidad anual",
                        value=True,
                        key="yearly_seasonality"
                    )
                
                with col2:
                    changepoint_prior_scale = st.slider(
                        "Changepoint Prior Scale",
                        min_value=0.001,
                        max_value=0.5,
                        value=0.05,
                        step=0.001,
                        format="%.3f",
                        key="changepoint_prior_scale"
                    )
                    
                    seasonality_prior_scale = st.slider(
                        "Seasonality Prior Scale",
                        min_value=0.1,
                        max_value=20.0,
                        value=10.0,
                        step=0.1,
                        format="%.1f",
                        key="seasonality_prior_scale"
                    )
                    
                    include_holidays = st.checkbox(
                        "Incluir festivos",
                        value=True,
                        key="include_holidays"
                    )
            
            # Botón para generar pronósticos
            submit_button = st.form_submit_button("Generar Pronósticos")
        
        # Procesar formulario
        if submit_button:
            with st.spinner("Generando pronósticos..."):
                # Preparar parámetros
                room_type_id = None
                if room_type != "Todos":
                    # Buscar ID del tipo de habitación
                    for rt in room_types:
                        if rt["name"] == room_type:
                            room_type_id = rt.get("id") or rt.get("code")
                            break
                
                # Configurar parámetros avanzados
                advanced_params = {
                    "seasonality_mode": seasonality_mode,
                    "weekly_seasonality": weekly_seasonality,
                    "yearly_seasonality": yearly_seasonality,
                    "changepoint_prior_scale": changepoint_prior_scale,
                    "seasonality_prior_scale": seasonality_prior_scale,
                    "include_holidays": include_holidays
                }
                
                # Llamar al orquestador para generar pronósticos
                # forecast_result = orchestrator.generate_forecasts(
                #     start_date.strftime("%Y-%m-%d"),
                #     end_date.strftime("%Y-%m-%d"),
                #     forecast_days,
                #     room_type_id,
                #     forecast_model.lower(),
                #     advanced_params
                # )
                
                # Simulación de resultado
                time.sleep(2)
                
                # Crear datos de ejemplo para el pronóstico
                forecast_start = datetime.now().date()
                forecast_end = forecast_start + timedelta(days=forecast_days)
                dates = pd.date_range(start=forecast_start, end=forecast_end)
                
                # Generar datos de ocupación con estacionalidad
                base_occupancy = 0.7
                occupancy_data = []
                
                for date in dates:
                    # Añadir estacionalidad semanal
                    weekday_factor = 1.0
                    if date.weekday() >= 5:  # Fin de semana
                        weekday_factor = 1.2
                    elif date.weekday() == 4:  # Viernes
                        weekday_factor = 1.1
                    
                    # Añadir estacionalidad mensual
                    month_factor = 1.0
                    if date.month in [1, 7, 8, 12]:  # Temporada alta
                        month_factor = 1.2
                    elif date.month in [4, 5, 6, 11]:  # Temporada baja
                        month_factor = 0.8
                    
                    # Calcular ocupación con ruido aleatorio
                    occupancy = base_occupancy * weekday_factor * month_factor
                    occupancy = min(max(occupancy + np.random.normal(0, 0.05), 0.3), 0.95)
                    
                    # Calcular ADR basado en ocupación
                    adr = 250000 + (occupancy * 100000) + np.random.normal(0, 10000)
                    
                    # Calcular RevPAR
                    revpar = adr * occupancy
                    
                    occupancy_data.append({
                        "fecha": date,
                        "ocupacion_prevista": occupancy,
                        "adr_previsto": adr,
                        "revpar_previsto": revpar,
                        "tipo_habitacion": room_type if room_type != "Todos" else "Promedio",
                        "modelo": forecast_model
                    })
                
                forecast_df = pd.DataFrame(occupancy_data)
                
                # Crear resultado simulado
                forecast_result = {
                    "success": True,
                    "message": f"Se generaron pronósticos para {forecast_days} días",
                    "data": {
                        "forecast_df": forecast_df,
                        "periodo": f"{forecast_start} a {forecast_end}"
                    }
                }
                
                # Guardar resultado en session_state
                st.session_state["forecast_result"] = forecast_result
                
                # Mostrar mensaje de éxito
                st.success(forecast_result["message"])
        
        # Mostrar resultados si existen
        if "forecast_result" in st.session_state and st.session_state["forecast_result"]["success"]:
            forecast_data = st.session_state["forecast_result"]["data"]
            forecast_df = forecast_data["forecast_df"]
            
            # Mostrar KPIs de pronóstico
            st.subheader("Resumen de Pronósticos")
            
            # Calcular KPIs
            avg_occupancy = forecast_df["ocupacion_prevista"].mean()
            avg_adr = forecast_df["adr_previsto"].mean()
            avg_revpar = forecast_df["revpar_previsto"].mean()
            
            # Crear datos de KPIs
            kpi_data = [
                {
                    "title": "Ocupación Media",
                    "value": avg_occupancy,
                    "format_type": "percentage",
                    "help_text": "Ocupación media pronosticada",
                    "icon": "🏨"
                },
                {
                    "title": "ADR Medio",
                    "value": avg_adr,
                    "format_type": "currency",
                    "help_text": "Tarifa media diaria pronosticada",
                    "icon": "💰"
                },
                {
                    "title": "RevPAR Medio",
                    "value": avg_revpar,
                    "format_type": "currency",
                    "help_text": "Ingresos por habitación disponible pronosticados",
                    "icon": "📈"
                }
            ]
            
            # Mostrar KPIs
            kpi_row(kpi_data, columns=3)
            
            # Mostrar gráfico de pronóstico
            st.subheader("Gráfico de Pronóstico")
            
            # Selector de métricas
            metrics = st.multiselect(
                "Seleccionar métricas",
                options=["ocupacion_prevista", "adr_previsto", "revpar_previsto"],
                default=["ocupacion_prevista"],
                key="forecast_metrics"
            )
            
            if metrics:
                # Crear gráfico de series temporales
                time_series_chart(
                    data=forecast_df,
                    date_column="fecha",
                    value_columns=metrics,
                    title="Pronóstico",
                    color_discrete_map={
                        "ocupacion_prevista": "#1f77b4",
                        "adr_previsto": "#ff7f0e",
                        "revpar_previsto": "#2ca02c"
                    }
                )
            
            # Mostrar tabla de pronósticos
            st.subheader("Tabla de Pronósticos")
            
            data_table(
                forecast_df,
                height=400,
                hide_index=True,
                key="forecast_table"
            )
            
            # Botón para guardar pronósticos
            if st.button("Guardar Pronósticos", key="save_forecast_button"):
                with st.spinner("Guardando pronósticos..."):
                    # Aquí se llamaría al orquestador para guardar los pronósticos
                    # save_result = orchestrator.save_forecast_to_db(forecast_df)
                    
                    # Simulación de guardado
                    time.sleep(1)
                    
                    # Mostrar mensaje de éxito
                    st.success("Pronósticos guardados correctamente")
    
    with tab2:
        st.subheader("Ajustar Pronósticos")
        
        # Cargar pronósticos existentes
        col1, col2 = st.columns(2)
        
        with col1:
            # Selector de fechas
            start_date, end_date = date_selector(key="adjust_date", default_days=90)
        
        with col2:
            # Selector de tipo de habitación
            room_types = config.get_room_types()
            room_type_options = ["Todos"] + [rt["name"] for rt in room_types]
            
            room_type = st.selectbox(
                "Tipo de habitación",
                options=room_type_options,
                index=0,
                key="adjust_room_type"
            )
        
        # Botón para cargar pronósticos
        if st.button("Cargar Pronósticos", key="load_forecast_button"):
            with st.spinner("Cargando pronósticos..."):
                # Preparar parámetros
                room_type_id = None
                if room_type != "Todos":
                    # Buscar ID del tipo de habitación
                    for rt in room_types:
                        if rt["name"] == room_type:
                            room_type_id = rt.get("id") or rt.get("code")
                            break
                
                # Llamar al orquestador para cargar pronósticos
                # forecast_df = orchestrator.load_forecast_from_db(
                #     start_date.strftime("%Y-%m-%d") if start_date else None,
                #     end_date.strftime("%Y-%m-%d") if end_date else None,
                #     room_type_id
                # )
                
                # Simulación de carga
                time.sleep(1)
                
                # Crear datos de ejemplo para el pronóstico
                if start_date and end_date:
                    dates = pd.date_range(start=start_date, end=end_date)
                else:
                    forecast_start = datetime.now().date()
                    forecast_end = forecast_start + timedelta(days=90)
                    dates = pd.date_range(start=forecast_start, end=forecast_end)
                
                # Generar datos de ocupación con estacionalidad
                base_occupancy = 0.7
                occupancy_data = []
                
                for date in dates:
                    # Añadir estacionalidad semanal
                    weekday_factor = 1.0
                    if date.weekday() >= 5:  # Fin de semana
                        weekday_factor = 1.2
                    elif date.weekday() == 4:  # Viernes
                        weekday_factor = 1.1
                    
                    # Añadir estacionalidad mensual
                    month_factor = 1.0
                    if date.month in [1, 7, 8, 12]:  # Temporada alta
                        month_factor = 1.2
                    elif date.month in [4, 5, 6, 11]:  # Temporada baja
                        month_factor = 0.8
                    
                    # Calcular ocupación con ruido aleatorio
                    occupancy = base_occupancy * weekday_factor * month_factor
                    occupancy = min(max(occupancy + np.random.normal(0, 0.05), 0.3), 0.95)
                    
                    # Calcular ADR basado en ocupación
                    adr = 250000 + (occupancy * 100000) + np.random.normal(0, 10000)
                    
                    # Calcular RevPAR
                    revpar = adr * occupancy
                    
                    occupancy_data.append({
                        "fecha": date,
                        "ocupacion_prevista": occupancy,
                        "ocupacion_ajustada": occupancy,
                        "adr_previsto": adr,
                        "adr_ajustado": adr,
                        "revpar_previsto": revpar,
                        "revpar_ajustado": revpar,
                        "tipo_habitacion": room_type if room_type != "Todos" else "Promedio",
                        "modelo": "Prophet",
                        "ajustado": False
                    })
                
                forecast_df = pd.DataFrame(occupancy_data)
                
                # Guardar en session_state
                st.session_state["adjust_forecast_df"] = forecast_df
        
        # Mostrar pronósticos para ajustar
        if "adjust_forecast_df" in st.session_state:
            forecast_df = st.session_state["adjust_forecast_df"]
            
            # Mostrar gráfico comparativo
            st.subheader("Comparación de Pronósticos")
            
            # Selector de métrica
            metric = st.selectbox(
                "Métrica",
                options=["ocupacion", "adr", "revpar"],
                index=0,
                key="adjust_metric"
            )
            
            # Mapear métrica seleccionada a columnas
            if metric == "ocupacion":
                y1 = "ocupacion_prevista"
                y2 = "ocupacion_ajustada"
                y1_name = "Ocupación Prevista"
                y2_name = "Ocupación Ajustada"
            elif metric == "adr":
                y1 = "adr_previsto"
                y2 = "adr_ajustado"
                y1_name = "ADR Previsto"
                y2_name = "ADR Ajustado"
            else:
                y1 = "revpar_previsto"
                y2 = "revpar_ajustado"
                y1_name = "RevPAR Previsto"
                y2_name = "RevPAR Ajustado"
            
            # Crear gráfico comparativo
            comparison_chart(
                data=forecast_df,
                x="fecha",
                y1=y1,
                y2=y2,
                title=f"Comparación de {y1_name} y {y2_name}",
                y1_name=y1_name,
                y2_name=y2_name
            )
            
            # Tabla editable para ajustar pronósticos
            st.subheader("Ajustar Pronósticos")
            
            # Función para manejar cambios en la tabla
            def on_forecast_change(edited_df):
                # Actualizar valores ajustados
                edited_df["ajustado"] = True
                
                # Recalcular RevPAR ajustado
                if "ocupacion_ajustada" in edited_df.columns and "adr_ajustado" in edited_df.columns:
                    edited_df["revpar_ajustado"] = edited_df["ocupacion_ajustada"] * edited_df["adr_ajustado"]
                
                # Guardar en session_state
                st.session_state["adjust_forecast_df"] = edited_df
            
            # Columnas editables
            editable_cols = []
            if metric == "ocupacion":
                editable_cols = ["ocupacion_ajustada"]
            elif metric == "adr":
                editable_cols = ["adr_ajustado"]
            else:
                editable_cols = ["ocupacion_ajustada", "adr_ajustado"]
            
            # Mostrar tabla editable
            edited_df = editable_data_table(
                forecast_df,
                editable_columns=editable_cols,
                height=400,
                hide_index=True,
                key="adjust_forecast_table",
                on_change=on_forecast_change
            )
            
            # Botón para guardar ajustes
            if st.button("Guardar Ajustes", key="save_adjustments_button"):
                with st.spinner("Guardando ajustes..."):
                    # Aquí se llamaría al orquestador para guardar los ajustes
                    # save_result = orchestrator.save_forecast_adjustments(edited_df)
                    
                    # Simulación de guardado
                    time.sleep(1)
                    
                    # Mostrar mensaje de éxito
                    st.success("Ajustes guardados correctamente")
    
    with tab3:
        st.subheader("Análisis de Precisión")
        
        # Selección de período para análisis
        col1, col2 = st.columns(2)
        
        with col1:
            # Selector de fechas
            start_date, end_date = date_selector(key="accuracy_date", default_days=90)
        
        with col2:
            # Selector de modelo
            model = st.selectbox(
                "Modelo",
                options=["Todos", "Prophet", "ARIMA", "Exponential Smoothing", "LSTM"],
                index=0,
                key="accuracy_model"
            )
        
        # Botón para analizar precisión
        if st.button("Analizar Precisión", key="analyze_accuracy_button"):
            with st.spinner("Analizando precisión..."):
                # Aquí se llamaría al orquestador para analizar la precisión
                # accuracy_result = orchestrator.analyze_forecast_accuracy(
                #     start_date.strftime("%Y-%m-%d") if start_date else None,
                #     end_date.strftime("%Y-%m-%d") if end_date else None,
                #     model if model != "Todos" else None
                # )
                
                # Simulación de análisis
                time.sleep(2)
                
                # Crear datos de ejemplo para el análisis de precisión
                if start_date and end_date:
                    dates = pd.date_range(start=start_date, end=end_date)
                else:
                    analysis_start = datetime.now().date() - timedelta(days=90)
                    analysis_end = datetime.now().date()
                    dates = pd.date_range(start=analysis_start, end=analysis_end)
                
                # Generar datos de precisión
                accuracy_data = []
                
                models = ["Prophet", "ARIMA", "Exponential Smoothing", "LSTM"] if model == "Todos" else [model]
                metrics = ["ocupacion", "adr", "revpar"]
                
                for date in dates:
                    for m in models:
                        for metric in metrics:
                            # Generar valores reales y pronosticados
                            actual = np.random.uniform(0.5, 0.9) if metric == "ocupacion" else np.random.uniform(200000, 400000)
                            forecast = actual * np.random.uniform(0.8, 1.2)
                            error = (forecast - actual) / actual
                            
                            accuracy_data.append({
                                "fecha": date,
                                "modelo": m,
                                "metrica": metric,
                                "valor_real": actual,
                                "valor_pronosticado": forecast,
                                "error_porcentual": error
                            })
                
                accuracy_df = pd.DataFrame(accuracy_data)
                
                # Calcular métricas de precisión
                accuracy_metrics = []
                
                for m in models:
                    for metric in metrics:
                        # Filtrar datos
                        filtered_df = accuracy_df[(accuracy_df["modelo"] == m) & (accuracy_df["metrica"] == metric)]
                        
                        # Calcular métricas
                        mape = np.abs(filtered_df["error_porcentual"]).mean()
                        rmse = np.sqrt(np.mean(np.square(filtered_df["valor_pronosticado"] - filtered_df["valor_real"])))
                        
                        accuracy_metrics.append({
                            "modelo": m,
                            "metrica": metric,
                            "mape": mape,
                            "rmse": rmse
                        })
                
                accuracy_metrics_df = pd.DataFrame(accuracy_metrics)
                
                # Guardar en session_state
                st.session_state["accuracy_df"] = accuracy_df
                st.session_state["accuracy_metrics_df"] = accuracy_metrics_df
        
        # Mostrar resultados de precisión
        if "accuracy_df" in st.session_state and "accuracy_metrics_df" in st.session_state:
            accuracy_df = st.session_state["accuracy_df"]
            accuracy_metrics_df = st.session_state["accuracy_metrics_df"]
            
            # Mostrar métricas de precisión
            st.subheader("Métricas de Precisión")
            
            data_table(
                accuracy_metrics_df,
                height=300,
                hide_index=True,
                key="accuracy_metrics_table"
            )
            
            # Mostrar gráfico de error porcentual
            st.subheader("Error Porcentual por Modelo y Métrica")
            
            # Filtrar por métrica
            metric = st.selectbox(
                "Métrica",
                options=["ocupacion", "adr", "revpar"],
                index=0,
                key="accuracy_metric_filter"
            )
            
            filtered_df = accuracy_df[accuracy_df["metrica"] == metric]
            
            # Crear gráfico de error porcentual
            chart(
                data=filtered_df,
                chart_type="line",
                x="fecha",
                y="error_porcentual",
                color="modelo",
                title=f"Error Porcentual - {metric}"
            )
            
            # Mostrar gráfico de valores reales vs pronosticados
            st.subheader("Valores Reales vs Pronosticados")
            
            # Filtrar por modelo
            if model == "Todos":
                selected_model = st.selectbox(
                    "Modelo",
                    options=["Prophet", "ARIMA", "Exponential Smoothing", "LSTM"],
                    index=0,
                    key="accuracy_model_filter"
                )
            else:
                selected_model = model
            
            # Filtrar datos
            model_df = filtered_df[filtered_df["modelo"] == selected_model]
            
            # Crear gráfico comparativo
            comparison_chart(
                data=model_df,
                x="fecha",
                y1="valor_real",
                y2="valor_pronosticado",
                title=f"Valores Reales vs Pronosticados - {selected_model} - {metric}",
                y1_name="Valor Real",
                y2_name="Valor Pronosticado"
            )