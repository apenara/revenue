#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Componente para subir archivos
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

def file_uploader(label="Subir archivo", types=None, key=None, help=None, on_upload=None, 
                  save_path=None, max_size_mb=200, accept_multiple_files=False):
    """
    Componente para subir archivos con validación y procesamiento.
    
    Args:
        label (str): Etiqueta para el uploader
        types (list): Lista de tipos de archivo permitidos (ej. ['xlsx', 'csv'])
        key (str, optional): Clave única para el componente
        help (str, optional): Texto de ayuda
        on_upload (function, optional): Función a ejecutar cuando se sube un archivo
        save_path (str, optional): Ruta donde guardar el archivo
        max_size_mb (int): Tamaño máximo permitido en MB
        accept_multiple_files (bool): Permitir subir múltiples archivos
        
    Returns:
        dict/list: Información del archivo o lista de archivos subidos
    """
    # Tipos de archivo por defecto
    if types is None:
        types = ["xlsx", "xls", "csv"]
    
    # Convertir tipos a formato para st.file_uploader
    file_types = [f".{t}" for t in types]
    
    # Crear uploader
    uploaded_files = st.file_uploader(
        label,
        type=file_types,
        key=key,
        help=help,
        accept_multiple_files=accept_multiple_files
    )
    
    # Si no hay archivos, retornar None
    if not uploaded_files:
        return None
    
    # Procesar archivos
    if accept_multiple_files:
        results = []
        
        for file in uploaded_files:
            result = _process_uploaded_file(file, save_path, max_size_mb, on_upload)
            if result:
                results.append(result)
        
        return results if results else None
    else:
        return _process_uploaded_file(uploaded_files, save_path, max_size_mb, on_upload)

def _process_uploaded_file(file, save_path, max_size_mb, on_upload):
    """
    Procesa un archivo subido.
    
    Args:
        file: Archivo subido
        save_path (str): Ruta donde guardar el archivo
        max_size_mb (int): Tamaño máximo permitido en MB
        on_upload (function): Función a ejecutar cuando se sube un archivo
        
    Returns:
        dict: Información del archivo procesado
    """
    try:
        # Validar tamaño
        file_size_mb = file.size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            st.error(f"El archivo {file.name} excede el tamaño máximo permitido ({max_size_mb} MB).")
            return None
        
        # Obtener extensión
        file_ext = Path(file.name).suffix.lower()
        
        # Guardar archivo si se especifica ruta
        saved_path = None
        if save_path:
            # Crear directorio si no existe
            save_dir = Path(save_path)
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{Path(file.name).stem}_{timestamp}{file_ext}"
            saved_path = save_dir / filename
            
            # Guardar archivo
            with open(saved_path, "wb") as f:
                f.write(file.getbuffer())
        
        # Leer datos según el tipo de archivo
        data = None
        if file_ext in [".xlsx", ".xls"]:
            data = pd.read_excel(file)
        elif file_ext == ".csv":
            data = pd.read_csv(file)
        
        # Crear resultado
        result = {
            "name": file.name,
            "size": file_size_mb,
            "type": file_ext[1:],  # Sin el punto
            "data": data,
            "path": str(saved_path) if saved_path else None
        }
        
        # Ejecutar callback si existe
        if on_upload:
            on_upload(result)
        
        return result
    
    except Exception as e:
        st.error(f"Error al procesar el archivo {file.name}: {e}")
        return None

def excel_uploader(label="Subir archivo Excel", key=None, help=None, on_upload=None, 
                   save_path=None, max_size_mb=200, sheet_name=None, accept_multiple_files=False):
    """
    Componente especializado para subir archivos Excel.
    
    Args:
        label (str): Etiqueta para el uploader
        key (str, optional): Clave única para el componente
        help (str, optional): Texto de ayuda
        on_upload (function, optional): Función a ejecutar cuando se sube un archivo
        save_path (str, optional): Ruta donde guardar el archivo
        max_size_mb (int): Tamaño máximo permitido en MB
        sheet_name (str/list, optional): Nombre(s) de hoja(s) a leer
        accept_multiple_files (bool): Permitir subir múltiples archivos
        
    Returns:
        dict/list: Información del archivo o lista de archivos subidos
    """
    # Crear wrapper para on_upload que lea la hoja específica
    def excel_processor(result):
        if result and result["data"] is not None and sheet_name is not None:
            # Leer la hoja específica
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                tmp.write(file.getbuffer())
                tmp_path = tmp.name
            
            try:
                # Leer Excel con la hoja específica
                result["data"] = pd.read_excel(tmp_path, sheet_name=sheet_name)
                
                # Si sheet_name es una lista, result["data"] será un dict de DataFrames
                if isinstance(sheet_name, list) and isinstance(result["data"], dict):
                    result["sheets"] = list(result["data"].keys())
                else:
                    result["sheets"] = [sheet_name]
                
                # Ejecutar callback original si existe
                if on_upload:
                    on_upload(result)
            
            finally:
                # Eliminar archivo temporal
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        elif on_upload:
            # Si no se especifica sheet_name, ejecutar callback original
            on_upload(result)
    
    # Usar el uploader genérico con tipos Excel
    return file_uploader(
        label=label,
        types=["xlsx", "xls"],
        key=key,
        help=help,
        on_upload=excel_processor if sheet_name else on_upload,
        save_path=save_path,
        max_size_mb=max_size_mb,
        accept_multiple_files=accept_multiple_files
    )

def csv_uploader(label="Subir archivo CSV", key=None, help=None, on_upload=None, 
                 save_path=None, max_size_mb=200, delimiter=",", encoding="utf-8", accept_multiple_files=False):
    """
    Componente especializado para subir archivos CSV.
    
    Args:
        label (str): Etiqueta para el uploader
        key (str, optional): Clave única para el componente
        help (str, optional): Texto de ayuda
        on_upload (function, optional): Función a ejecutar cuando se sube un archivo
        save_path (str, optional): Ruta donde guardar el archivo
        max_size_mb (int): Tamaño máximo permitido en MB
        delimiter (str): Delimitador para el CSV
        encoding (str): Codificación del archivo
        accept_multiple_files (bool): Permitir subir múltiples archivos
        
    Returns:
        dict/list: Información del archivo o lista de archivos subidos
    """
    # Crear wrapper para on_upload que use el delimitador y encoding específicos
    def csv_processor(result):
        if result and result["path"]:
            # Leer CSV con parámetros específicos
            result["data"] = pd.read_csv(result["path"], delimiter=delimiter, encoding=encoding)
            
            # Ejecutar callback original si existe
            if on_upload:
                on_upload(result)
    
    # Usar el uploader genérico con tipo CSV
    return file_uploader(
        label=label,
        types=["csv"],
        key=key,
        help=help,
        on_upload=csv_processor if (delimiter != "," or encoding != "utf-8") else on_upload,
        save_path=save_path,
        max_size_mb=max_size_mb,
        accept_multiple_files=accept_multiple_files
    )

def file_uploader_with_preview(label="Subir archivo", types=None, key=None, help=None, 
                              save_path=None, max_size_mb=200, preview_rows=5):
    """
    Componente para subir archivos con vista previa de datos.
    
    Args:
        label (str): Etiqueta para el uploader
        types (list): Lista de tipos de archivo permitidos (ej. ['xlsx', 'csv'])
        key (str, optional): Clave única para el componente
        help (str, optional): Texto de ayuda
        save_path (str, optional): Ruta donde guardar el archivo
        max_size_mb (int): Tamaño máximo permitido en MB
        preview_rows (int): Número de filas a mostrar en la vista previa
        
    Returns:
        dict: Información del archivo subido
    """
    # Usar el uploader genérico
    result = file_uploader(
        label=label,
        types=types,
        key=key,
        help=help,
        save_path=save_path,
        max_size_mb=max_size_mb
    )
    
    # Mostrar vista previa si hay datos
    if result and result["data"] is not None:
        st.subheader(f"Vista previa: {result['name']}")
        
        # Información del archivo
        col1, col2, col3 = st.columns(3)
        col1.metric("Filas", len(result["data"]))
        col2.metric("Columnas", len(result["data"].columns))
        col3.metric("Tamaño", f"{result['size']:.2f} MB")
        
        # Vista previa de datos
        st.dataframe(result["data"].head(preview_rows))
        
        # Información de columnas
        st.subheader("Información de columnas")
        
        # Crear DataFrame con información de columnas
        columns_info = pd.DataFrame({
            "Columna": result["data"].columns,
            "Tipo": result["data"].dtypes.astype(str),
            "No Nulos": result["data"].count().values,
            "% No Nulos": (result["data"].count() / len(result["data"]) * 100).round(2).astype(str) + "%",
            "Valores únicos": [result["data"][col].nunique() for col in result["data"].columns]
        })
        
        st.dataframe(columns_info)
    
    return result