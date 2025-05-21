#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de demostración para el Framework de Revenue Management del Hotel Playa Club (MVP).
Este script muestra cómo utilizar las principales funcionalidades del framework.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import streamlit as st

# Asegurar que el directorio raíz del proyecto esté en el path
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

# Importar módulos del framework
from revenue_management.config import config
from revenue_management.db.database import db
from revenue_management.initialize_db import initialize_database
from revenue_management.services.revenue_orchestrator import RevenueOrchestrator
from revenue_management.models.room import Room
from revenue_management.models.rule import Rule
from revenue_management.scripts.load_sample_data import (
    generate_sample_bookings, 
    generate_sample_stays,
    generate_historical_summary,
    generate_daily_occupancy,
    generate_daily_revenue,
    generate_pricing_rules
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("demo")

def setup_database():
    """
    Inicializa la base de datos y carga datos de ejemplo.
    
    Returns:
        bool: True si la inicialización fue exitosa, False en caso contrario.
    """
    logger.info("Inicializando base de datos...")
    
    try:
        # Inicializar base de datos
        success = initialize_database()
        if not success:
            logger.error("Error al inicializar la base de datos")
            return False
        
        logger.info("Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        return False

def load_sample_data():
    """
    Genera y carga datos de ejemplo en la base de datos.
    
    Returns:
        bool: True si la carga fue exitosa, False en caso contrario.
    """
    logger.info("Generando y cargando datos de ejemplo...")
    
    try:
        # Definir período para los datos (último año)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Generar datos de reservas
        bookings_df = generate_sample_bookings(start_date, end_date, num_bookings=2000)
        
        # Generar datos de estancias
        stays_df = generate_sample_stays(bookings_df, end_date)
        
        # Generar datos de resumen diario histórico
        summary_df = generate_historical_summary(start_date, end_date, bookings_df, stays_df)
        
        # Generar datos de ocupación diaria
        occupancy_df = generate_daily_occupancy(start_date, end_date, stays_df)
        
        # Generar datos de ingresos diarios
        revenue_df = generate_daily_revenue(start_date, end_date, stays_df)
        
        # Generar reglas de pricing
        rules = generate_pricing_rules()
        
        # Cargar datos en la base de datos
        from revenue_management.services.data_ingestion.data_ingestion_service import DataIngestionService
        ingestion_service = DataIngestionService()
        
        # Cargar reservas
        if not bookings_df.empty:
            # Guardar DataFrame en un archivo temporal
            temp_bookings_path = Path("temp_bookings.xlsx")
            bookings_df.to_excel(temp_bookings_path, sheet_name='Reservas', index=False)
            
            # Procesar reservas
            success, message, bookings_count = ingestion_service.process_bookings(temp_bookings_path)
            
            # Eliminar archivo temporal
            if temp_bookings_path.exists():
                os.remove(temp_bookings_path)
            
            if success:
                logger.info(f"Cargados {bookings_count} registros de reservas en la base de datos.")
            else:
                logger.error(f"Error al cargar reservas: {message}")
        
        # Cargar estancias
        if not stays_df.empty:
            # Guardar DataFrame en un archivo temporal
            temp_stays_path = Path("temp_stays.xlsx")
            stays_df.to_excel(temp_stays_path, sheet_name='Estancias', index=False)
            
            # Procesar estancias
            success, message, stays_count = ingestion_service.process_stays(temp_stays_path)
            
            # Eliminar archivo temporal
            if temp_stays_path.exists():
                os.remove(temp_stays_path)
            
            if success:
                logger.info(f"Cargados {stays_count} registros de estancias en la base de datos.")
            else:
                logger.error(f"Error al cargar estancias: {message}")
        
        # Cargar resumen diario histórico
        if not summary_df.empty:
            # Insertar directamente en la base de datos
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                for _, row in summary_df.iterrows():
                    cursor.execute('''
                    INSERT INTO HISTORICAL_SUMMARY (
                        fecha, habitaciones_disponibles, habitaciones_ocupadas, 
                        ingresos_totales, adr, revpar, ocupacion_porcentaje
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['fecha'], row['habitaciones_disponibles'], row['habitaciones_ocupadas'],
                        row['ingresos_totales'], row['adr'], row['revpar'], row['ocupacion_porcentaje']
                    ))
                
                conn.commit()
                
                logger.info(f"Cargados {len(summary_df)} registros de resumen diario histórico en la base de datos.")
        
        # Cargar ocupación diaria
        if not occupancy_df.empty:
            # Insertar directamente en la base de datos
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                for _, row in occupancy_df.iterrows():
                    # Obtener ID del tipo de habitación
                    cursor.execute('SELECT id FROM ROOM_TYPES WHERE cod_hab = ?', (row['room_type_id'],))
                    room_type_id = cursor.fetchone()[0]
                    
                    cursor.execute('''
                    INSERT INTO DAILY_OCCUPANCY (
                        fecha, room_type_id, habitaciones_disponibles, 
                        habitaciones_ocupadas, ocupacion_porcentaje
                    ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        row['fecha'], room_type_id, row['habitaciones_disponibles'],
                        row['habitaciones_ocupadas'], row['ocupacion_porcentaje']
                    ))
                
                conn.commit()
                
                logger.info(f"Cargados {len(occupancy_df)} registros de ocupación diaria en la base de datos.")
        
        # Cargar ingresos diarios
        if not revenue_df.empty:
            # Insertar directamente en la base de datos
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                for _, row in revenue_df.iterrows():
                    # Obtener ID del tipo de habitación
                    cursor.execute('SELECT id FROM ROOM_TYPES WHERE cod_hab = ?', (row['room_type_id'],))
                    room_type_id = cursor.fetchone()[0]
                    
                    cursor.execute('''
                    INSERT INTO DAILY_REVENUE (
                        fecha, room_type_id, ingresos, adr, revpar
                    ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        row['fecha'], room_type_id, row['ingresos'], row['adr'], row['revpar']
                    ))
                
                conn.commit()
                
                logger.info(f"Cargados {len(revenue_df)} registros de ingresos diarios en la base de datos.")
        
        # Cargar reglas de pricing
        for rule in rules:
            # Convertir parámetros a JSON
            parametros_json = str(rule['parametros']).replace("'", '"')
            
            # Insertar en la base de datos
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT INTO RULE_CONFIGS (
                    nombre, descripcion, parametros, prioridad, activa
                ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    rule['nombre'], rule['descripcion'], parametros_json,
                    rule['prioridad'], rule['activa']
                ))
                
                conn.commit()
        
        logger.info(f"Cargadas {len(rules)} reglas de pricing en la base de datos.")
        
        logger.info("Datos de ejemplo cargados correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al cargar datos de ejemplo: {e}")
        return False

def demo_analyze_kpis():
    """
    Demuestra el análisis de KPIs.
    
    Returns:
        dict: Resultados del análisis de KPIs.
    """
    logger.info("Demostrando análisis de KPIs...")
    
    try:
        # Crear instancia del orquestador
        orchestrator = RevenueOrchestrator()
        
        # Definir período para el análisis (último año)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        # Analizar KPIs
        kpi_results = orchestrator.analyze_kpis(start_date, end_date)
        
        if kpi_results["success"]:
            logger.info("Análisis de KPIs completado con éxito")
            
            # Mostrar algunos resultados
            kpi_df = kpi_results["data"]["kpis"]
            if not kpi_df.is_empty():
                logger.info(f"KPIs calculados para {kpi_df.height} días")
                
                # Calcular promedios
                avg_occupancy = kpi_df.select(pl.col("ocupacion_porcentaje").mean()).item()
                avg_adr = kpi_df.select(pl.col("adr").mean()).item()
                avg_revpar = kpi_df.select(pl.col("revpar").mean()).item()
                
                logger.info(f"Ocupación promedio: {avg_occupancy:.2f}%")
                logger.info(f"ADR promedio: ${avg_adr:,.0f}")
                logger.info(f"RevPAR promedio: ${avg_revpar:,.0f}")
        else:
            logger.error(f"Error en el análisis de KPIs: {kpi_results['message']}")
        
        return kpi_results
        
    except Exception as e:
        logger.error(f"Error al demostrar análisis de KPIs: {e}")
        return {"success": False, "message": str(e), "data": {}}

def demo_generate_forecasts():
    """
    Demuestra la generación de pronósticos.
    
    Returns:
        dict: Resultados de la generación de pronósticos.
    """
    logger.info("Demostrando generación de pronósticos...")
    
    try:
        # Crear instancia del orquestador
        orchestrator = RevenueOrchestrator()
        
        # Definir período para los datos históricos (último año)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        # Definir número de días a pronosticar
        forecast_days = 90
        
        # Generar pronósticos
        forecast_results = orchestrator.generate_forecasts(start_date, end_date, forecast_days)
        
        if forecast_results["success"]:
            logger.info("Generación de pronósticos completada con éxito")
            
            # Mostrar algunos resultados
            forecast_df = forecast_results["data"]["forecast_df"]
            if not forecast_df.is_empty():
                logger.info(f"Pronósticos generados para {forecast_df.height} días")
                
                # Calcular promedios
                avg_occupancy = forecast_df.select(pl.col("ocupacion_prevista").mean()).item() * 100
                avg_adr = forecast_df.select(pl.col("adr_previsto").mean()).item()
                avg_revpar = forecast_df.select(pl.col("revpar_previsto").mean()).item()
                
                logger.info(f"Ocupación prevista promedio: {avg_occupancy:.2f}%")
                logger.info(f"ADR previsto promedio: ${avg_adr:,.0f}")
                logger.info(f"RevPAR previsto promedio: ${avg_revpar:,.0f}")
        else:
            logger.error(f"Error en la generación de pronósticos: {forecast_results['message']}")
        
        return forecast_results
        
    except Exception as e:
        logger.error(f"Error al demostrar generación de pronósticos: {e}")
        return {"success": False, "message": str(e), "data": {}}

def demo_apply_pricing_rules():
    """
    Demuestra la aplicación de reglas de pricing.
    
    Returns:
        dict: Resultados de la aplicación de reglas de pricing.
    """
    logger.info("Demostrando aplicación de reglas de pricing...")
    
    try:
        # Crear instancia del orquestador
        orchestrator = RevenueOrchestrator()
        
        # Definir número de días a considerar
        forecast_days = 90
        
        # Aplicar reglas de pricing
        pricing_results = orchestrator.apply_pricing_rules(forecast_days)
        
        if pricing_results["success"]:
            logger.info("Aplicación de reglas de pricing completada con éxito")
            
            # Mostrar algunos resultados
            recommendations_df = pricing_results["data"]["recommendations_df"]
            if not recommendations_df.is_empty():
                logger.info(f"Recomendaciones generadas para {recommendations_df.height} combinaciones de fecha/habitación/canal")
                
                # Calcular estadísticas
                avg_base_rate = recommendations_df.select(pl.col("tarifa_base").mean()).item()
                avg_recommended_rate = recommendations_df.select(pl.col("tarifa_recomendada").mean()).item()
                avg_change = ((avg_recommended_rate / avg_base_rate) - 1) * 100
                
                logger.info(f"Tarifa base promedio: ${avg_base_rate:,.0f}")
                logger.info(f"Tarifa recomendada promedio: ${avg_recommended_rate:,.0f}")
                logger.info(f"Cambio promedio: {avg_change:+.2f}%")
        else:
            logger.error(f"Error en la aplicación de reglas de pricing: {pricing_results['message']}")
        
        return pricing_results
        
    except Exception as e:
        logger.error(f"Error al demostrar aplicación de reglas de pricing: {e}")
        return {"success": False, "message": str(e), "data": {}}

def demo_export_tariffs():
    """
    Demuestra la exportación de tarifas.
    
    Returns:
        dict: Resultados de la exportación de tarifas.
    """
    logger.info("Demostrando exportación de tarifas...")
    
    try:
        # Crear instancia del orquestador
        orchestrator = RevenueOrchestrator()
        
        # Definir período para la exportación (próximos 90 días)
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        
        # Exportar tarifas
        export_results = orchestrator.export_tariffs(start_date, end_date)
        
        if export_results["success"]:
            logger.info("Exportación de tarifas completada con éxito")
            
            # Mostrar ruta del archivo exportado
            filepath = export_results["data"]["filepath"]
            logger.info(f"Tarifas exportadas a: {filepath}")
        else:
            logger.error(f"Error en la exportación de tarifas: {export_results['message']}")
        
        return export_results
        
    except Exception as e:
        logger.error(f"Error al demostrar exportación de tarifas: {e}")
        return {"success": False, "message": str(e), "data": {}}

def run_full_demo():
    """
    Ejecuta la demostración completa del framework.
    """
    logger.info("Iniciando demostración completa del Framework de Revenue Management")
    
    # Paso 1: Inicializar base de datos
    logger.info("\n=== PASO 1: INICIALIZACIÓN DE BASE DE DATOS ===")
    if not setup_database():
        logger.error("Error al inicializar la base de datos. Abortando demostración.")
        return
    
    # Paso 2: Cargar datos de ejemplo
    logger.info("\n=== PASO 2: CARGA DE DATOS DE EJEMPLO ===")
    if not load_sample_data():
        logger.error("Error al cargar datos de ejemplo. Abortando demostración.")
        return
    
    # Paso 3: Análisis de KPIs
    logger.info("\n=== PASO 3: ANÁLISIS DE KPIs ===")
    kpi_results = demo_analyze_kpis()
    if not kpi_results["success"]:
        logger.warning("El análisis de KPIs no se completó correctamente. Continuando con la demostración.")
    
    # Paso 4: Generación de pronósticos
    logger.info("\n=== PASO 4: GENERACIÓN DE PRONÓSTICOS ===")
    forecast_results = demo_generate_forecasts()
    if not forecast_results["success"]:
        logger.warning("La generación de pronósticos no se completó correctamente. Continuando con la demostración.")
    
    # Paso 5: Aplicación de reglas de pricing
    logger.info("\n=== PASO 5: APLICACIÓN DE REGLAS DE PRICING ===")
    pricing_results = demo_apply_pricing_rules()
    if not pricing_results["success"]:
        logger.warning("La aplicación de reglas de pricing no se completó correctamente. Continuando con la demostración.")
    
    # Paso 6: Exportación de tarifas
    logger.info("\n=== PASO 6: EXPORTACIÓN DE TARIFAS ===")
    export_results = demo_export_tariffs()
    if not export_results["success"]:
        logger.warning("La exportación de tarifas no se completó correctamente.")
    
    logger.info("\n=== DEMOSTRACIÓN COMPLETADA ===")
    logger.info("El Framework de Revenue Management ha sido probado con éxito.")
    logger.info("Para iniciar la aplicación Streamlit, ejecute: streamlit run revenue_management/app.py")

if __name__ == "__main__":
    run_full_demo()