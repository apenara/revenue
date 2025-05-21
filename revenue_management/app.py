#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Framework de Revenue Management - Hotel Playa Club (MVP)
Punto de entrada principal de la aplicación
"""

import os
import sys
import streamlit as st
from pathlib import Path
from datetime import datetime
import time
import hashlib

# Asegurar que el directorio raíz del proyecto esté en el path
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

# Importar módulos de la aplicación
from config import config
from db.database import db
from db.schema import schema_manager
from utils.logger import setup_logger
from initialize_db import initialize_database
from services.revenue_orchestrator import RevenueOrchestrator

# Importar páginas de la UI
from ui.pages import dashboard, data_ingestion, forecasting, pricing, tariff_management, settings

# Configurar logger
logger = setup_logger(__name__)

# Inicializar el orquestador de servicios
orchestrator = RevenueOrchestrator()

# Configuración de autenticación (usuarios y contraseñas)
USERS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "manager": hashlib.sha256("manager123".encode()).hexdigest(),
    "user": hashlib.sha256("user123".encode()).hexdigest()
}

# Roles y permisos
ROLES = {
    "admin": ["dashboard", "data_ingestion", "forecasting", "pricing", "tariff_management", "settings"],
    "manager": ["dashboard", "forecasting", "pricing", "tariff_management"],
    "user": ["dashboard", "data_ingestion"]
}

def check_database():
    """
    Verifica si la base de datos existe y está inicializada.
    Si no existe, la inicializa.
    
    Returns:
        bool: True si la base de datos está lista, False en caso contrario
    """
    try:
        db_path = config.get_path("database.path")
        
        if not db_path or not db_path.exists():
            logger.info("Base de datos no encontrada. Inicializando...")
            success = initialize_database()
            
            if not success:
                logger.error("Error al inicializar la base de datos")
                return False
            
            logger.info("Base de datos inicializada correctamente")
        
        # Verificar si se debe hacer backup al iniciar
        if config.get("database.backup_on_startup", False):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"startup_backup_{timestamp}"
            backup_path = db.create_backup(backup_name)
            
            if backup_path:
                logger.info(f"Copia de seguridad creada en: {backup_path}")
            else:
                logger.warning("No se pudo crear la copia de seguridad")
        
        return True
        
    except Exception as e:
        logger.error(f"Error al verificar la base de datos: {e}")
        return False

def check_password():
    """
    Verifica las credenciales del usuario.
    
    Returns:
        bool: True si las credenciales son válidas, False en caso contrario
    """
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = False
    
    if "username" not in st.session_state:
        st.session_state["username"] = ""
    
    if "role" not in st.session_state:
        st.session_state["role"] = ""
    
    if st.session_state["authentication_status"]:
        return True
    
    st.title("Revenue Management - Acceso")
    
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username] == hashlib.sha256(password.encode()).hexdigest():
            st.session_state["authentication_status"] = True
            st.session_state["username"] = username
            st.session_state["role"] = "admin" if username == "admin" else "manager" if username == "manager" else "user"
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    
    return False

def apply_theme():
    """Aplica el tema personalizado a la aplicación"""
    # Definir colores personalizados
    primary_color = "#1E88E5"
    background_color = "#FAFAFA"
    text_color = "#212121"
    secondary_background_color = "#E3F2FD"
    
    # Aplicar tema personalizado
    st.markdown(f"""
    <style>
        .reportview-container .main .block-container{{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        .stApp {{
            background-color: {background_color};
            color: {text_color};
        }}
        .stButton>button {{
            background-color: {primary_color};
            color: white;
        }}
        .stTextInput>div>div>input {{
            border-color: {primary_color};
        }}
        .stSelectbox>div>div>div {{
            border-color: {primary_color};
        }}
        .stDateInput>div>div>input {{
            border-color: {primary_color};
        }}
        .sidebar .sidebar-content {{
            background-color: {secondary_background_color};
        }}
    </style>
    """, unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""
    logger.info("Iniciando aplicación de Revenue Management")
    
    # Verificar base de datos
    if not check_database():
        st.error("Error al inicializar la base de datos. Consulte los logs para más detalles.")
        return
    
    # Aplicar tema personalizado
    apply_theme()
    
    # Verificar autenticación
    if not check_password():
        return
    
    # Obtener información del hotel
    hotel_info = config.get_hotel_info()
    
    # Configurar Streamlit
    st.set_page_config(
        page_title=config.get("app.name", "Revenue Management"),
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Título de la aplicación
    st.title(f"Framework de Revenue Management - {hotel_info['name']}")
    st.caption(f"Ubicación: {hotel_info['location']} | Habitaciones: {hotel_info['total_rooms']}")
    
    # Menú lateral
    st.sidebar.title("Navegación")
    
    # Filtrar páginas según el rol del usuario
    available_pages = ROLES.get(st.session_state["role"], [])
    
    page_options = []
    if "dashboard" in available_pages:
        page_options.append("Dashboard")
    if "data_ingestion" in available_pages:
        page_options.append("Ingesta de Datos")
    if "forecasting" in available_pages:
        page_options.append("Forecasting")
    if "pricing" in available_pages:
        page_options.append("Pricing")
    if "tariff_management" in available_pages:
        page_options.append("Gestión de Tarifas")
    if "settings" in available_pages:
        page_options.append("Configuración")
    
    page = st.sidebar.radio("Seleccione una página:", page_options)
    
    # Mostrar la página seleccionada
    if page == "Dashboard":
        dashboard.show(orchestrator)
    elif page == "Ingesta de Datos":
        data_ingestion.show(orchestrator)
    elif page == "Forecasting":
        forecasting.show(orchestrator)
    elif page == "Pricing":
        pricing.show(orchestrator)
    elif page == "Gestión de Tarifas":
        tariff_management.show(orchestrator)
    elif page == "Configuración":
        settings.show(orchestrator)
    
    # Mostrar información de la base de datos
    st.sidebar.markdown("---")
    st.sidebar.subheader("Información del Sistema")
    
    # Verificar si la base de datos existe
    db_path = config.get_path("database.path")
    if db_path and db_path.exists():
        db_size = db_path.stat().st_size / (1024 * 1024)  # Tamaño en MB
        st.sidebar.text(f"Base de datos: {db_size:.2f} MB")
        
        # Obtener última copia de seguridad
        backups = db.list_backups()
        if backups:
            last_backup = backups[0]
            last_backup_time = datetime.fromtimestamp(last_backup.stat().st_mtime)
            st.sidebar.text(f"Última copia: {last_backup_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Información del usuario
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"Usuario: {st.session_state['username']}")
    st.sidebar.text(f"Rol: {st.session_state['role']}")
    
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["authentication_status"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.experimental_rerun()
    
    # Pie de página
    st.sidebar.markdown("---")
    st.sidebar.info(
        f"Versión: {config.get('app.version', '1.0.0')}"
    )

if __name__ == "__main__":
    main()