#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para la exportación de tarifas aprobadas
"""

import os
import polars as pl
import pandas as pd
from datetime import datetime
from utils.logger import setup_logger
from models.recommendation import ApprovedRecommendation
from models.room import Room
from config import config

# Configurar logger
logger = setup_logger(__name__)

class TariffExporter:
    """
    Clase para la exportación de tarifas aprobadas a Excel
    """
    
    def __init__(self):
        """
        Inicializa la instancia de TariffExporter
        """
        self.export_dir = config.get_path("directories.data_exports")
        self.template_path = config.get_path("excel.export_template")
        self.room_types = {room.id: room for room in Room.get_all()}
        self.channels = config.get_channels()
        self.hotel_info = config.get_hotel_info()
    
    def get_pending_exports(self):
        """
        Obtiene las tarifas aprobadas pendientes de exportar.
        
        Returns:
            pl.DataFrame: DataFrame con las tarifas pendientes de exportar
        """
        try:
            logger.info("Obteniendo tarifas pendientes de exportar")
            
            # Obtener recomendaciones aprobadas pendientes de exportar
            recommendations = ApprovedRecommendation.get_pending_export()
            
            if not recommendations:
                logger.info("No hay tarifas pendientes de exportar")
                return pl.DataFrame()
            
            # Convertir a DataFrame de Polars
            df = pl.DataFrame([rec.to_dict() for rec in recommendations])
            
            # Agregar información adicional
            df = self._enrich_tariff_data(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error al obtener tarifas pendientes de exportar: {e}")
            return pl.DataFrame()
    
    def _enrich_tariff_data(self, df):
        """
        Enriquece los datos de tarifas con información adicional.
        
        Args:
            df (pl.DataFrame): DataFrame con las tarifas
            
        Returns:
            pl.DataFrame: DataFrame enriquecido
        """
        try:
            if df.is_empty():
                return df
            
            # Agregar nombre del tipo de habitación
            df = df.with_column(
                pl.col("room_type_id").map_dict(
                    {room_id: room.nombre for room_id, room in self.room_types.items()},
                    default="Desconocido"
                ).alias("tipo_habitacion")
            )
            
            # Agregar código del tipo de habitación
            df = df.with_column(
                pl.col("room_type_id").map_dict(
                    {room_id: room.codigo for room_id, room in self.room_types.items()},
                    default="UNK"
                ).alias("codigo_habitacion")
            )
            
            # Agregar nombre del canal
            df = df.with_column(
                pl.col("channel_id").map_dict(
                    {i+1: channel["name"] for i, channel in enumerate(self.channels)},
                    default="Desconocido"
                ).alias("canal")
            )
            
            # Convertir fecha a datetime
            df = df.with_column(pl.col("fecha").str.to_datetime("%Y-%m-%d"))
            
            # Extraer información de la fecha
            df = df.with_columns([
                pl.col("fecha").dt.weekday().alias("dia_semana"),
                pl.col("fecha").dt.day().alias("dia"),
                pl.col("fecha").dt.month().alias("mes"),
                pl.col("fecha").dt.year().alias("año")
            ])
            
            # Formatear fecha para mostrar
            df = df.with_column(
                pl.col("fecha").dt.strftime("%d/%m/%Y").alias("fecha_formato")
            )
            
            # Nombre del día de la semana
            dias_semana = {
                0: "Lunes",
                1: "Martes",
                2: "Miércoles",
                3: "Jueves",
                4: "Viernes",
                5: "Sábado",
                6: "Domingo"
            }
            
            df = df.with_column(
                pl.col("dia_semana").map_dict(dias_semana, default="").alias("nombre_dia")
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error al enriquecer datos de tarifas: {e}")
            return df
    
    def export_to_excel(self, start_date=None, end_date=None, room_type_id=None, channel_id=None):
        """
        Exporta las tarifas aprobadas a un archivo Excel.
        
        Args:
            start_date (str/datetime, optional): Fecha de inicio
            end_date (str/datetime, optional): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            channel_id (int, optional): ID del canal
            
        Returns:
            tuple: (éxito, mensaje, ruta_archivo)
        """
        try:
            logger.info(f"Exportando tarifas a Excel para el rango {start_date} - {end_date}")
            
            # Obtener recomendaciones aprobadas
            if start_date and end_date:
                recommendations = ApprovedRecommendation.get_by_date_range(start_date, end_date, room_type_id, channel_id)
            else:
                recommendations = ApprovedRecommendation.get_pending_export()
            
            if not recommendations:
                return (False, "No hay tarifas para exportar", None)
            
            # Convertir a DataFrame de Polars
            df = pl.DataFrame([rec.to_dict() for rec in recommendations])
            
            # Enriquecer datos
            df = self._enrich_tariff_data(df)
            
            # Crear archivo Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tarifas_export_{timestamp}.xlsx"
            filepath = os.path.join(self.export_dir, filename)
            
            # Verificar si existe el directorio
            os.makedirs(self.export_dir, exist_ok=True)
            
            # Exportar a Excel
            self._create_excel_file(df, filepath)
            
            # Marcar como exportadas
            self._mark_as_exported(recommendations)
            
            return (True, f"Se exportaron {len(recommendations)} tarifas", filepath)
            
        except Exception as e:
            logger.error(f"Error al exportar tarifas a Excel: {e}")
            return (False, f"Error: {e}", None)
    
    def _create_excel_file(self, df, filepath):
        """
        Crea el archivo Excel con las tarifas.
        
        Args:
            df (pl.DataFrame): DataFrame con las tarifas
            filepath (str): Ruta del archivo a crear
            
        Returns:
            bool: True si se creó correctamente, False en caso contrario
        """
        try:
            # Convertir a pandas para usar ExcelWriter
            pd_df = df.to_pandas()
            
            # Crear Excel con pandas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja de resumen
                self._create_summary_sheet(pd_df, writer)
                
                # Hoja por tipo de habitación
                self._create_room_type_sheets(pd_df, writer)
                
                # Hoja para Zeus PMS
                self._create_zeus_pms_sheet(pd_df, writer)
            
            logger.info(f"Archivo Excel creado correctamente: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error al crear archivo Excel: {e}")
            return False
    
    def _create_summary_sheet(self, df, writer):
        """
        Crea la hoja de resumen en el archivo Excel.
        
        Args:
            df (pd.DataFrame): DataFrame con las tarifas
            writer: ExcelWriter de pandas
        """
        try:
            # Crear hoja de resumen
            summary_df = df[['fecha_formato', 'nombre_dia', 'tipo_habitacion', 'canal', 'tarifa_aprobada']]
            
            # Pivot para mostrar tarifas por tipo de habitación y fecha
            pivot_df = summary_df.pivot_table(
                index=['fecha_formato', 'nombre_dia'],
                columns=['tipo_habitacion', 'canal'],
                values='tarifa_aprobada',
                aggfunc='first'
            )
            
            # Escribir a Excel
            pivot_df.to_excel(writer, sheet_name='Resumen')
            
            # Dar formato a la hoja
            worksheet = writer.sheets['Resumen']
            
            # Título
            worksheet.cell(row=1, column=1, value=f"Tarifas - {self.hotel_info['name']}")
            worksheet.cell(row=2, column=1, value=f"Exportado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
            # Ajustar anchos de columna
            for i, col in enumerate(pivot_df.columns):
                worksheet.column_dimensions[chr(65 + i)].width = 15
            
        except Exception as e:
            logger.error(f"Error al crear hoja de resumen: {e}")
    
    def _create_room_type_sheets(self, df, writer):
        """
        Crea hojas por tipo de habitación en el archivo Excel.
        
        Args:
            df (pd.DataFrame): DataFrame con las tarifas
            writer: ExcelWriter de pandas
        """
        try:
            # Agrupar por tipo de habitación
            for room_id, room in self.room_types.items():
                # Filtrar por tipo de habitación
                room_df = df[df['room_type_id'] == room_id]
                
                if len(room_df) == 0:
                    continue
                
                # Seleccionar columnas relevantes
                room_df = room_df[['fecha_formato', 'nombre_dia', 'canal', 'tarifa_base', 'tarifa_recomendada', 'tarifa_aprobada']]
                
                # Pivot para mostrar tarifas por canal y fecha
                pivot_df = room_df.pivot_table(
                    index=['fecha_formato', 'nombre_dia'],
                    columns=['canal'],
                    values='tarifa_aprobada',
                    aggfunc='first'
                )
                
                # Escribir a Excel
                sheet_name = f"{room.codigo}"
                pivot_df.to_excel(writer, sheet_name=sheet_name)
                
                # Dar formato a la hoja
                worksheet = writer.sheets[sheet_name]
                
                # Título
                worksheet.cell(row=1, column=1, value=f"Tarifas - {room.nombre}")
                
                # Ajustar anchos de columna
                for i, col in enumerate(pivot_df.columns):
                    worksheet.column_dimensions[chr(65 + i)].width = 15
                
        except Exception as e:
            logger.error(f"Error al crear hojas por tipo de habitación: {e}")
    
    def _create_zeus_pms_sheet(self, df, writer):
        """
        Crea la hoja para Zeus PMS en el archivo Excel.
        
        Args:
            df (pd.DataFrame): DataFrame con las tarifas
            writer: ExcelWriter de pandas
        """
        try:
            # Crear formato específico para Zeus PMS
            zeus_data = []
            
            # Agrupar por fecha y tipo de habitación
            for fecha in sorted(df['fecha'].unique()):
                for room_id in sorted(df['room_type_id'].unique()):
                    # Filtrar por fecha y tipo de habitación
                    filtered_df = df[(df['fecha'] == fecha) & (df['room_type_id'] == room_id)]
                    
                    if len(filtered_df) == 0:
                        continue
                    
                    # Obtener datos
                    fecha_str = filtered_df['fecha_formato'].iloc[0]
                    codigo_hab = filtered_df['codigo_habitacion'].iloc[0]
                    
                    # Obtener tarifas por canal
                    tarifas = {}
                    for _, row in filtered_df.iterrows():
                        tarifas[row['canal']] = row['tarifa_aprobada']
                    
                    # Crear fila para Zeus PMS
                    zeus_row = {
                        'Fecha': fecha_str,
                        'Código': codigo_hab
                    }
                    
                    # Agregar tarifas por canal
                    for channel in self.channels:
                        channel_name = channel['name']
                        zeus_row[channel_name] = tarifas.get(channel_name, 0)
                    
                    zeus_data.append(zeus_row)
            
            # Crear DataFrame para Zeus PMS
            zeus_df = pd.DataFrame(zeus_data)
            
            # Escribir a Excel
            zeus_df.to_excel(writer, sheet_name='Zeus_PMS', index=False)
            
            # Dar formato a la hoja
            worksheet = writer.sheets['Zeus_PMS']
            
            # Título
            worksheet.cell(row=1, column=1, value=f"Tarifas para Zeus PMS - {self.hotel_info['name']}")
            
            # Ajustar anchos de columna
            for i, col in enumerate(zeus_df.columns):
                worksheet.column_dimensions[chr(65 + i)].width = 15
            
        except Exception as e:
            logger.error(f"Error al crear hoja para Zeus PMS: {e}")
    
    def _mark_as_exported(self, recommendations):
        """
        Marca las recomendaciones como exportadas.
        
        Args:
            recommendations (list): Lista de recomendaciones
            
        Returns:
            int: Número de recomendaciones marcadas como exportadas
        """
        try:
            count = 0
            for rec in recommendations:
                if not rec.exportado:
                    rec.mark_as_exported()
                    count += 1
            
            logger.info(f"Se marcaron {count} recomendaciones como exportadas")
            return count
            
        except Exception as e:
            logger.error(f"Error al marcar recomendaciones como exportadas: {e}")
            return 0