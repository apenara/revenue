#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Página para subir y procesar archivos Excel
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os

from ui.components.file_uploader import file_uploader_with_preview, excel_uploader
from ui.components.data_table import data_table, filterable_data_table
from ui.components.chart import chart
from config import config

def show(orchestrator):
    """
    Muestra la página de ingesta de datos.
    
    Args:
        orchestrator: Instancia del orquestador de servicios
    """
    st.header("Ingesta de Datos")
    
    # Obtener configuración de Excel
    excel_config = config.get_excel_config()
    
    # Crear pestañas para diferentes tipos de ingesta
    tab1, tab2, tab3 = st.tabs(["Carga de Archivos", "Datos Procesados", "Historial de Cargas"])
    
    with tab1:
        st.subheader("Carga de Archivos Excel")
        
        # Información sobre formatos aceptados
        with st.expander("Información sobre formatos aceptados", expanded=False):
            st.markdown("""
            ### Formatos Aceptados
            
            Los archivos Excel deben contener alguna de las siguientes hojas:
            
            1. **Reservas/Bookings**: Datos de reservas con las columnas:
               - ID Reserva
               - Fecha Reserva
               - Fecha Check-in
               - Fecha Check-out
               - Tipo Habitación
               - Tarifa
               - Canal
               - Estado
            
            2. **Estancias/Stays**: Datos de estancias con las columnas:
               - ID Estancia
               - Fecha Check-in
               - Fecha Check-out
               - Tipo Habitación
               - Tarifa
               - Ingresos
               - Noches
            
            3. **Resumen/Summary**: Datos resumidos con las columnas:
               - Fecha
               - Ocupación
               - ADR
               - RevPAR
               - Ingresos
            """)
        
        # Uploader de archivos
        st.subheader("Subir Archivo Excel")
        
        # Definir función de callback para procesar el archivo
        def process_excel_file(result):
            if result and result["data"] is not None:
                st.session_state["uploaded_file"] = result
                st.session_state["processing_status"] = "pending"
        
        # Subir archivo Excel
        uploaded_file = excel_uploader(
            label="Seleccione un archivo Excel con datos de reservas, estancias o resumen",
            help="Formatos aceptados: .xlsx, .xls",
            on_upload=process_excel_file,
            save_path=config.get("directories.data_raw"),
            key="data_ingestion_uploader"
        )
        
        # Inicializar variables de estado si no existen
        if "uploaded_file" not in st.session_state:
            st.session_state["uploaded_file"] = None
        
        if "processing_status" not in st.session_state:
            st.session_state["processing_status"] = None
        
        if "processing_result" not in st.session_state:
            st.session_state["processing_result"] = None
        
        # Mostrar vista previa y opciones de procesamiento
        if st.session_state["uploaded_file"]:
            st.subheader("Opciones de Procesamiento")
            
            # Detectar hojas disponibles
            data = st.session_state["uploaded_file"]["data"]
            
            if isinstance(data, dict):
                # Múltiples hojas
                sheets = list(data.keys())
                
                # Identificar tipo de hoja
                sheet_types = {}
                
                for sheet in sheets:
                    sheet_lower = sheet.lower()
                    
                    if any(name.lower() in sheet_lower for name in excel_config.get("bookings_sheet_names", [])):
                        sheet_types[sheet] = "reservas"
                    elif any(name.lower() in sheet_lower for name in excel_config.get("stays_sheet_names", [])):
                        sheet_types[sheet] = "estancias"
                    elif any(name.lower() in sheet_lower for name in excel_config.get("summary_sheet_names", [])):
                        sheet_types[sheet] = "resumen"
                    else:
                        sheet_types[sheet] = "desconocido"
                
                # Mostrar selector de hoja
                selected_sheet = st.selectbox(
                    "Seleccione la hoja a procesar",
                    options=sheets,
                    format_func=lambda x: f"{x} ({sheet_types[x]})",
                    key="selected_sheet"
                )
                
                # Mostrar vista previa de la hoja seleccionada
                st.subheader(f"Vista previa: {selected_sheet}")
                st.dataframe(data[selected_sheet].head(10))
                
                # Guardar tipo de datos
                data_type = sheet_types[selected_sheet]
            else:
                # Una sola hoja
                st.subheader("Vista previa")
                st.dataframe(data.head(10))
                
                # Determinar tipo de datos
                data_type = st.radio(
                    "Tipo de datos",
                    options=["reservas", "estancias", "resumen"],
                    horizontal=True,
                    key="data_type"
                )
            
            # Opciones adicionales según el tipo de datos
            if data_type == "reservas":
                st.subheader("Opciones para datos de reservas")
                
                # Mapeo de columnas
                with st.expander("Mapeo de columnas", expanded=True):
                    # Obtener columnas del DataFrame
                    if isinstance(data, dict):
                        df_columns = data[selected_sheet].columns.tolist()
                    else:
                        df_columns = data.columns.tolist()
                    
                    # Crear mapeo de columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        id_reserva_col = st.selectbox(
                            "ID Reserva",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "id" in c.lower() or "reserva" in c.lower()), 0),
                            key="id_reserva_col"
                        )
                        
                        fecha_reserva_col = st.selectbox(
                            "Fecha Reserva",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "fecha" in c.lower() and "reserva" in c.lower()), 0),
                            key="fecha_reserva_col"
                        )
                        
                        checkin_col = st.selectbox(
                            "Fecha Check-in",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "checkin" in c.lower() or "check-in" in c.lower() or "llegada" in c.lower()), 0),
                            key="checkin_col"
                        )
                        
                        checkout_col = st.selectbox(
                            "Fecha Check-out",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "checkout" in c.lower() or "check-out" in c.lower() or "salida" in c.lower()), 0),
                            key="checkout_col"
                        )
                    
                    with col2:
                        tipo_hab_col = st.selectbox(
                            "Tipo Habitación",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "tipo" in c.lower() or "habitacion" in c.lower() or "room" in c.lower()), 0),
                            key="tipo_hab_col"
                        )
                        
                        tarifa_col = st.selectbox(
                            "Tarifa",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "tarifa" in c.lower() or "precio" in c.lower() or "rate" in c.lower()), 0),
                            key="tarifa_col"
                        )
                        
                        canal_col = st.selectbox(
                            "Canal",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "canal" in c.lower() or "channel" in c.lower()), 0),
                            key="canal_col"
                        )
                        
                        estado_col = st.selectbox(
                            "Estado",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "estado" in c.lower() or "status" in c.lower()), 0),
                            key="estado_col"
                        )
            
            elif data_type == "estancias":
                st.subheader("Opciones para datos de estancias")
                
                # Mapeo de columnas
                with st.expander("Mapeo de columnas", expanded=True):
                    # Obtener columnas del DataFrame
                    if isinstance(data, dict):
                        df_columns = data[selected_sheet].columns.tolist()
                    else:
                        df_columns = data.columns.tolist()
                    
                    # Crear mapeo de columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        id_estancia_col = st.selectbox(
                            "ID Estancia",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "id" in c.lower() or "estancia" in c.lower() or "stay" in c.lower()), 0),
                            key="id_estancia_col"
                        )
                        
                        checkin_col = st.selectbox(
                            "Fecha Check-in",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "checkin" in c.lower() or "check-in" in c.lower() or "llegada" in c.lower()), 0),
                            key="checkin_col_estancia"
                        )
                        
                        checkout_col = st.selectbox(
                            "Fecha Check-out",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "checkout" in c.lower() or "check-out" in c.lower() or "salida" in c.lower()), 0),
                            key="checkout_col_estancia"
                        )
                    
                    with col2:
                        tipo_hab_col = st.selectbox(
                            "Tipo Habitación",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "tipo" in c.lower() or "habitacion" in c.lower() or "room" in c.lower()), 0),
                            key="tipo_hab_col_estancia"
                        )
                        
                        tarifa_col = st.selectbox(
                            "Tarifa",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "tarifa" in c.lower() or "precio" in c.lower() or "rate" in c.lower()), 0),
                            key="tarifa_col_estancia"
                        )
                        
                        ingresos_col = st.selectbox(
                            "Ingresos",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "ingreso" in c.lower() or "revenue" in c.lower()), 0),
                            key="ingresos_col"
                        )
                        
                        noches_col = st.selectbox(
                            "Noches",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "noche" in c.lower() or "night" in c.lower() or "estancia" in c.lower()), 0),
                            key="noches_col"
                        )
            
            elif data_type == "resumen":
                st.subheader("Opciones para datos de resumen")
                
                # Mapeo de columnas
                with st.expander("Mapeo de columnas", expanded=True):
                    # Obtener columnas del DataFrame
                    if isinstance(data, dict):
                        df_columns = data[selected_sheet].columns.tolist()
                    else:
                        df_columns = data.columns.tolist()
                    
                    # Crear mapeo de columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fecha_col = st.selectbox(
                            "Fecha",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "fecha" in c.lower() or "date" in c.lower()), 0),
                            key="fecha_col"
                        )
                        
                        ocupacion_col = st.selectbox(
                            "Ocupación",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "ocupacion" in c.lower() or "occupancy" in c.lower()), 0),
                            key="ocupacion_col"
                        )
                    
                    with col2:
                        adr_col = st.selectbox(
                            "ADR",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "adr" in c.lower() or "tarifa" in c.lower()), 0),
                            key="adr_col"
                        )
                        
                        revpar_col = st.selectbox(
                            "RevPAR",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "revpar" in c.lower()), 0),
                            key="revpar_col"
                        )
                        
                        ingresos_col = st.selectbox(
                            "Ingresos",
                            options=[""] + df_columns,
                            index=next((i+1 for i, c in enumerate(df_columns) if "ingreso" in c.lower() or "revenue" in c.lower()), 0),
                            key="ingresos_col_resumen"
                        )
            
            # Botón para procesar datos
            if st.button("Procesar Datos", key="process_data_button"):
                # Mostrar spinner mientras se procesan los datos
                with st.spinner("Procesando datos..."):
                    # Preparar datos para el procesamiento
                    file_path = st.session_state["uploaded_file"]["path"]
                    
                    # Crear diccionario con mapeo de columnas
                    column_mapping = {}
                    
                    if data_type == "reservas":
                        column_mapping = {
                            "id_reserva": id_reserva_col,
                            "fecha_reserva": fecha_reserva_col,
                            "fecha_checkin": checkin_col,
                            "fecha_checkout": checkout_col,
                            "tipo_habitacion": tipo_hab_col,
                            "tarifa": tarifa_col,
                            "canal": canal_col,
                            "estado": estado_col
                        }
                    elif data_type == "estancias":
                        column_mapping = {
                            "id_estancia": id_estancia_col,
                            "fecha_checkin": checkin_col,
                            "fecha_checkout": checkout_col,
                            "tipo_habitacion": tipo_hab_col,
                            "tarifa": tarifa_col,
                            "ingresos": ingresos_col,
                            "noches": noches_col
                        }
                    elif data_type == "resumen":
                        column_mapping = {
                            "fecha": fecha_col,
                            "ocupacion": ocupacion_col,
                            "adr": adr_col,
                            "revpar": revpar_col,
                            "ingresos": ingresos_col
                        }
                    
                    # Filtrar columnas vacías
                    column_mapping = {k: v for k, v in column_mapping.items() if v}
                    
                    # Verificar que se hayan mapeado las columnas requeridas
                    if not column_mapping:
                        st.error("Debe mapear al menos una columna para procesar los datos.")
                        return
                    
                    # Procesar datos según el tipo
                    try:
                        # Simular procesamiento (reemplazar con llamada real al orquestador)
                        time.sleep(2)  # Simular tiempo de procesamiento
                        
                        # Llamar al servicio de ingesta de datos
                        if isinstance(data, dict):
                            df_to_process = data[selected_sheet]
                        else:
                            df_to_process = data
                        
                        # Aquí se llamaría al orquestador para procesar los datos
                        # result = orchestrator.process_data(file_path, data_type, column_mapping, sheet_name=selected_sheet if isinstance(data, dict) else None)
                        
                        # Simulación de resultado exitoso
                        result = {
                            "success": True,
                            "message": f"Se procesaron correctamente los datos de {data_type}.",
                            "data": {
                                "rows_processed": len(df_to_process),
                                "rows_inserted": len(df_to_process),
                                "file_path": file_path,
                                "data_type": data_type,
                                "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        }
                        
                        # Guardar resultado
                        st.session_state["processing_result"] = result
                        st.session_state["processing_status"] = "success"
                        
                        # Mostrar mensaje de éxito
                        st.success(result["message"])
                        
                        # Mostrar detalles del procesamiento
                        st.json(result["data"])
                        
                    except Exception as e:
                        # Guardar error
                        st.session_state["processing_result"] = {
                            "success": False,
                            "message": f"Error al procesar los datos: {str(e)}",
                            "data": {}
                        }
                        st.session_state["processing_status"] = "error"
                        
                        # Mostrar mensaje de error
                        st.error(f"Error al procesar los datos: {str(e)}")
        else:
            st.info("Suba un archivo Excel para comenzar.")
    
    with tab2:
        st.subheader("Datos Procesados")
        
        # Selector de tipo de datos
        data_type = st.radio(
            "Tipo de datos",
            options=["Reservas", "Estancias", "Resumen"],
            horizontal=True,
            key="processed_data_type"
        )
        
        # Filtro de fechas
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Fecha inicio",
                value=datetime.now().date() - timedelta(days=30),
                key="processed_start_date"
            )
        
        with col2:
            end_date = st.date_input(
                "Fecha fin",
                value=datetime.now().date(),
                key="processed_end_date"
            )
        
        # Botón para cargar datos
        if st.button("Cargar Datos", key="load_processed_data"):
            with st.spinner("Cargando datos procesados..."):
                # Aquí se llamaría al orquestador para cargar los datos procesados
                # processed_data = orchestrator.load_processed_data(data_type.lower(), start_date, end_date)
                
                # Simulación de datos procesados
                time.sleep(1)
                
                # Crear datos de ejemplo según el tipo
                if data_type == "Reservas":
                    # Datos de ejemplo para reservas
                    dates = pd.date_range(start=start_date, end=end_date)
                    room_types = ["Estándar Triple", "Junior Suite", "Estándar Cuádruple", "Estándar Doble"]
                    channels = ["Directo", "Booking.com", "Expedia", "Hotelbeds"]
                    
                    data = []
                    for i in range(50):
                        checkin = np.random.choice(dates)
                        checkout = checkin + timedelta(days=np.random.randint(1, 7))
                        room_type = np.random.choice(room_types)
                        channel = np.random.choice(channels)
                        rate = np.random.randint(150, 500) * 1000
                        
                        data.append({
                            "id_reserva": f"RES-{i+1000}",
                            "fecha_reserva": checkin - timedelta(days=np.random.randint(1, 30)),
                            "fecha_checkin": checkin,
                            "fecha_checkout": checkout,
                            "tipo_habitacion": room_type,
                            "tarifa": rate,
                            "canal": channel,
                            "estado": np.random.choice(["Confirmada", "Cancelada"], p=[0.9, 0.1])
                        })
                    
                    processed_data = pd.DataFrame(data)
                
                elif data_type == "Estancias":
                    # Datos de ejemplo para estancias
                    dates = pd.date_range(start=start_date, end=end_date)
                    room_types = ["Estándar Triple", "Junior Suite", "Estándar Cuádruple", "Estándar Doble"]
                    
                    data = []
                    for i in range(40):
                        checkin = np.random.choice(dates)
                        nights = np.random.randint(1, 7)
                        checkout = checkin + timedelta(days=nights)
                        room_type = np.random.choice(room_types)
                        rate = np.random.randint(150, 500) * 1000
                        
                        data.append({
                            "id_estancia": f"STAY-{i+1000}",
                            "fecha_checkin": checkin,
                            "fecha_checkout": checkout,
                            "tipo_habitacion": room_type,
                            "tarifa": rate,
                            "ingresos": rate * nights,
                            "noches": nights
                        })
                    
                    processed_data = pd.DataFrame(data)
                
                else:  # Resumen
                    # Datos de ejemplo para resumen
                    dates = pd.date_range(start=start_date, end=end_date)
                    
                    data = []
                    for date in dates:
                        ocupacion = np.random.uniform(0.4, 0.9)
                        adr = np.random.randint(200, 400) * 1000
                        revpar = adr * ocupacion
                        ingresos = revpar * 79  # Total de habitaciones
                        
                        data.append({
                            "fecha": date,
                            "ocupacion": ocupacion,
                            "adr": adr,
                            "revpar": revpar,
                            "ingresos": ingresos
                        })
                    
                    processed_data = pd.DataFrame(data)
                
                # Mostrar datos procesados
                if not processed_data.empty:
                    # Mostrar tabla filtrable
                    filterable_data_table(
                        processed_data,
                        title=f"Datos de {data_type}",
                        filters=processed_data.columns[:3].tolist(),
                        height=400,
                        hide_index=True,
                        key=f"processed_{data_type.lower()}_table"
                    )
                    
                    # Mostrar gráfico según el tipo de datos
                    if data_type == "Reservas":
                        # Gráfico de reservas por canal
                        chart(
                            data=processed_data.groupby("canal").size().reset_index(name="count"),
                            chart_type="pie",
                            x="canal",
                            y="count",
                            title="Reservas por Canal"
                        )
                    
                    elif data_type == "Estancias":
                        # Gráfico de ingresos por tipo de habitación
                        chart(
                            data=processed_data.groupby("tipo_habitacion").agg({"ingresos": "sum"}).reset_index(),
                            chart_type="bar",
                            x="tipo_habitacion",
                            y="ingresos",
                            title="Ingresos por Tipo de Habitación"
                        )
                    
                    else:  # Resumen
                        # Gráfico de ocupación y ADR
                        chart(
                            data=processed_data,
                            chart_type="line",
                            x="fecha",
                            y=["ocupacion", "adr"],
                            title="Ocupación y ADR"
                        )
                else:
                    st.warning("No hay datos procesados para el período seleccionado.")
    
    with tab3:
        st.subheader("Historial de Cargas")
        
        # Botón para cargar historial
        if st.button("Cargar Historial", key="load_history"):
            with st.spinner("Cargando historial de cargas..."):
                # Aquí se llamaría al orquestador para cargar el historial
                # history = orchestrator.get_data_ingestion_history()
                
                # Simulación de historial
                time.sleep(1)
                
                # Crear datos de ejemplo para el historial
                history_data = []
                for i in range(10):
                    date = datetime.now() - timedelta(days=i*3)
                    data_type = np.random.choice(["reservas", "estancias", "resumen"])
                    rows = np.random.randint(50, 500)
                    
                    history_data.append({
                        "id": i+1,
                        "fecha_carga": date,
                        "archivo": f"data_{data_type}_{date.strftime('%Y%m%d')}.xlsx",
                        "tipo_datos": data_type,
                        "filas_procesadas": rows,
                        "filas_insertadas": int(rows * np.random.uniform(0.9, 1.0)),
                        "estado": np.random.choice(["Completado", "Error"], p=[0.9, 0.1]),
                        "usuario": "admin"
                    })
                
                history = pd.DataFrame(history_data)
                
                # Mostrar historial
                if not history.empty:
                    data_table(
                        history,
                        title="Historial de Cargas",
                        height=400,
                        hide_index=True,
                        key="history_table"
                    )
                    
                    # Gráfico de cargas por tipo de datos
                    chart(
                        data=history.groupby("tipo_datos").size().reset_index(name="count"),
                        chart_type="pie",
                        x="tipo_datos",
                        y="count",
                        title="Cargas por Tipo de Datos"
                    )
                else:
                    st.warning("No hay historial de cargas disponible.")