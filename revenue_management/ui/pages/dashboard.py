#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Página de dashboard principal
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from ui.components.kpi_card import kpi_row, kpi_section
from ui.components.data_table import data_table
from ui.components.chart import chart, multi_chart, time_series_chart
from ui.components.date_selector import date_filter_sidebar
from ui.utils.formatting import format_currency, format_percentage, format_number

def show(orchestrator):
    """
    Muestra la página de dashboard.
    
    Args:
        orchestrator: Instancia del orquestador de servicios
    """
    st.header("Dashboard de Revenue Management")
    
    # Filtro de fechas en la barra lateral
    start_date, end_date = date_filter_sidebar(key="dashboard_date", default_days=90)
    
    if start_date and end_date:
        # Obtener datos para el dashboard
        dashboard_data = orchestrator.get_dashboard_data()
        
        if not dashboard_data["success"]:
            st.error(f"Error al obtener datos para el dashboard: {dashboard_data['message']}")
            return
        
        # Extraer datos
        kpi_df = dashboard_data["data"]["kpi_df"]
        agg_kpis = dashboard_data["data"]["agg_kpis"]
        forecast_df = dashboard_data["data"]["forecast_df"]
        pending_df = dashboard_data["data"]["pending_df"]
        
        # Filtrar datos por fecha
        if not kpi_df.empty:
            kpi_df = kpi_df[
                (kpi_df["fecha"] >= pd.Timestamp(start_date)) & 
                (kpi_df["fecha"] <= pd.Timestamp(end_date))
            ]
        
        if not forecast_df.empty:
            forecast_df = forecast_df[
                (forecast_df["fecha"] >= pd.Timestamp(start_date)) & 
                (forecast_df["fecha"] <= pd.Timestamp(end_date))
            ]
        
        # Mostrar KPIs principales
        st.subheader("KPIs Principales")
        
        # Crear datos de KPIs
        if not agg_kpis.empty:
            # Obtener valores agregados
            adr = agg_kpis["adr"].iloc[0] if "adr" in agg_kpis.columns else 0
            revpar = agg_kpis["revpar"].iloc[0] if "revpar" in agg_kpis.columns else 0
            ocupacion = agg_kpis["ocupacion"].iloc[0] if "ocupacion" in agg_kpis.columns else 0
            ingresos = agg_kpis["ingresos_totales"].iloc[0] if "ingresos_totales" in agg_kpis.columns else 0
            
            # Obtener valores del año anterior para comparación
            adr_prev = agg_kpis["adr_prev_year"].iloc[0] if "adr_prev_year" in agg_kpis.columns else None
            revpar_prev = agg_kpis["revpar_prev_year"].iloc[0] if "revpar_prev_year" in agg_kpis.columns else None
            ocupacion_prev = agg_kpis["ocupacion_prev_year"].iloc[0] if "ocupacion_prev_year" in agg_kpis.columns else None
            ingresos_prev = agg_kpis["ingresos_totales_prev_year"].iloc[0] if "ingresos_totales_prev_year" in agg_kpis.columns else None
            
            # Crear lista de KPIs
            kpi_data = [
                {
                    "title": "ADR",
                    "value": adr,
                    "previous_value": adr_prev,
                    "format_type": "currency",
                    "delta_color": "normal",
                    "help_text": "Tarifa media diaria",
                    "icon": "💰"
                },
                {
                    "title": "RevPAR",
                    "value": revpar,
                    "previous_value": revpar_prev,
                    "format_type": "currency",
                    "delta_color": "normal",
                    "help_text": "Ingresos por habitación disponible",
                    "icon": "📈"
                },
                {
                    "title": "Ocupación",
                    "value": ocupacion,
                    "previous_value": ocupacion_prev,
                    "format_type": "percentage",
                    "delta_color": "normal",
                    "help_text": "Porcentaje de ocupación",
                    "icon": "🏨"
                },
                {
                    "title": "Ingresos Totales",
                    "value": ingresos,
                    "previous_value": ingresos_prev,
                    "format_type": "currency",
                    "delta_color": "normal",
                    "help_text": "Ingresos totales en el período",
                    "icon": "💵"
                }
            ]
            
            # Mostrar KPIs
            kpi_row(kpi_data, columns=4)
        else:
            st.warning("No hay datos de KPIs disponibles para el período seleccionado.")
        
        # Dividir en columnas
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico de evolución temporal
            st.subheader("Evolución Temporal")
            
            if not kpi_df.empty:
                # Seleccionar métricas a mostrar
                metrics = st.multiselect(
                    "Seleccionar métricas",
                    options=["ocupacion", "adr", "revpar"],
                    default=["ocupacion", "adr"],
                    key="dashboard_metrics"
                )
                
                if metrics:
                    # Crear gráfico de series temporales
                    time_series_chart(
                        data=kpi_df,
                        date_column="fecha",
                        value_columns=metrics,
                        title="Evolución de métricas clave",
                        color_discrete_map={
                            "ocupacion": "#1f77b4",
                            "adr": "#ff7f0e",
                            "revpar": "#2ca02c"
                        }
                    )
                else:
                    st.info("Seleccione al menos una métrica para visualizar.")
            else:
                st.warning("No hay datos disponibles para el período seleccionado.")
            
            # Tabla de datos
            st.subheader("Datos Históricos")
            
            if not kpi_df.empty:
                data_table(
                    kpi_df,
                    height=300,
                    hide_index=True,
                    key="dashboard_table"
                )
            else:
                st.warning("No hay datos disponibles para el período seleccionado.")
        
        with col2:
            # Pronósticos
            st.subheader("Pronósticos")
            
            if not forecast_df.empty:
                # Filtrar próximos 30 días
                next_30_days = datetime.now().date() + timedelta(days=30)
                forecast_30 = forecast_df[forecast_df["fecha"] <= pd.Timestamp(next_30_days)]
                
                if not forecast_30.empty:
                    # Mostrar ocupación promedio pronosticada
                    avg_occupancy = forecast_30["ocupacion_prevista"].mean()
                    
                    st.metric(
                        "Ocupación promedio (próx. 30 días)",
                        f"{avg_occupancy:.1%}",
                        help="Ocupación promedio pronosticada para los próximos 30 días"
                    )
                    
                    # Gráfico de pronóstico de ocupación
                    chart(
                        data=forecast_30,
                        chart_type="line",
                        x="fecha",
                        y="ocupacion_prevista",
                        title="Pronóstico de ocupación",
                        labels={"fecha": "Fecha", "ocupacion_prevista": "Ocupación"}
                    )
                    
                    # Tabla de pronósticos
                    data_table(
                        forecast_30,
                        height=300,
                        hide_index=True,
                        key="forecast_table"
                    )
                else:
                    st.warning("No hay pronósticos disponibles para los próximos 30 días.")
            else:
                st.warning("No hay pronósticos disponibles.")
            
            # Recomendaciones pendientes
            st.subheader("Recomendaciones Pendientes")
            
            if not pending_df.empty:
                # Mostrar número de recomendaciones pendientes
                st.metric(
                    "Recomendaciones pendientes",
                    len(pending_df),
                    help="Número de recomendaciones de tarifas pendientes de aprobación"
                )
                
                # Tabla de recomendaciones pendientes
                data_table(
                    pending_df,
                    height=200,
                    hide_index=True,
                    key="pending_table"
                )
            else:
                st.info("No hay recomendaciones pendientes de aprobación.")
        
        # Sección inferior
        st.subheader("Análisis por Tipo de Habitación")
        
        if not kpi_df.empty and "tipo_habitacion" in kpi_df.columns:
            # Agrupar por tipo de habitación
            room_type_kpis = kpi_df.groupby("tipo_habitacion").agg({
                "ocupacion": "mean",
                "adr": "mean",
                "revpar": "mean",
                "ingresos": "sum"
            }).reset_index()
            
            # Mostrar tabla
            data_table(
                room_type_kpis,
                title="KPIs por Tipo de Habitación",
                hide_index=True,
                key="room_type_table"
            )
            
            # Gráficos comparativos
            charts_config = [
                {
                    "type": "bar",
                    "title": "Ocupación por Tipo",
                    "x": "tipo_habitacion",
                    "y": "ocupacion"
                },
                {
                    "type": "bar",
                    "title": "ADR por Tipo",
                    "x": "tipo_habitacion",
                    "y": "adr"
                },
                {
                    "type": "pie",
                    "title": "Distribución de Ingresos",
                    "x": "tipo_habitacion",
                    "y": "ingresos"
                }
            ]
            
            multi_chart(
                data=room_type_kpis,
                charts_config=charts_config,
                cols=3,
                height=300
            )
        else:
            st.warning("No hay datos disponibles por tipo de habitación.")
    else:
        st.info("Seleccione un rango de fechas para visualizar el dashboard.")