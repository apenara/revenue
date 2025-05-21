#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que define el modelo para las recomendaciones aprobadas
"""

from datetime import datetime
from models.base_model import BaseModel
from db.database import db
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class ApprovedRecommendation(BaseModel):
    """
    Modelo para las recomendaciones aprobadas (APPROVED_RECOMMENDATIONS)
    """
    
    def __init__(self, id=None, fecha=None, room_type_id=None, channel_id=None, 
                 tarifa_base=None, tarifa_recomendada=None, tarifa_aprobada=None, 
                 created_at=None, approved_at=None, estado="Aprobada", 
                 exportado=False, exportado_at=None):
        """
        Inicializa una instancia de ApprovedRecommendation.
        
        Args:
            id (int, optional): ID del registro
            fecha (str/datetime): Fecha de la recomendación
            room_type_id (int): ID del tipo de habitación
            channel_id (int): ID del canal de distribución
            tarifa_base (float): Tarifa base
            tarifa_recomendada (float): Tarifa recomendada
            tarifa_aprobada (float): Tarifa aprobada
            created_at (str/datetime, optional): Fecha de creación del registro
            approved_at (str/datetime, optional): Fecha de aprobación
            estado (str, optional): Estado de la recomendación
            exportado (bool, optional): Indica si la recomendación fue exportada
            exportado_at (str/datetime, optional): Fecha de exportación
        """
        self.id = id
        self.fecha = self._parse_date(fecha)
        self.room_type_id = room_type_id
        self.channel_id = channel_id
        self.tarifa_base = tarifa_base
        self.tarifa_recomendada = tarifa_recomendada
        self.tarifa_aprobada = tarifa_aprobada
        self.created_at = self._parse_date(created_at) if created_at else datetime.now()
        self.approved_at = self._parse_date(approved_at) if approved_at else datetime.now()
        self.estado = estado
        self.exportado = exportado
        self.exportado_at = self._parse_date(exportado_at)
    
    def _parse_date(self, date_value):
        """
        Convierte un valor de fecha a objeto datetime.
        
        Args:
            date_value: Valor de fecha (str, datetime, None)
            
        Returns:
            datetime: Objeto datetime o None si el valor es None
        """
        if date_value is None:
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        try:
            # Intentar diferentes formatos de fecha
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'):
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue
            
            # Si no se pudo convertir con ningún formato
            logger.warning(f"No se pudo convertir la fecha: {date_value}")
            return None
        except Exception as e:
            logger.error(f"Error al convertir la fecha: {e}")
            return None
    
    def _format_date(self, date_value):
        """
        Formatea un objeto datetime como string en formato YYYY-MM-DD.
        
        Args:
            date_value (datetime): Objeto datetime
            
        Returns:
            str: Fecha formateada o None si el valor es None
        """
        if date_value is None:
            return None
        
        return date_value.strftime('%Y-%m-%d')
    
    def _format_datetime(self, date_value):
        """
        Formatea un objeto datetime como string en formato YYYY-MM-DD HH:MM:SS.
        
        Args:
            date_value (datetime): Objeto datetime
            
        Returns:
            str: Fecha y hora formateadas o None si el valor es None
        """
        if date_value is None:
            return None
        
        return date_value.strftime('%Y-%m-%d %H:%M:%S')
    
    @classmethod
    def from_row(cls, row):
        """
        Crea una instancia de ApprovedRecommendation a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            ApprovedRecommendation: Instancia de ApprovedRecommendation
        """
        if not row:
            return None
        
        return cls(
            id=row['id'],
            fecha=row['fecha'],
            room_type_id=row['room_type_id'],
            channel_id=row['channel_id'],
            tarifa_base=row['tarifa_base'],
            tarifa_recomendada=row['tarifa_recomendada'],
            tarifa_aprobada=row['tarifa_aprobada'],
            created_at=row['created_at'],
            approved_at=row['approved_at'],
            estado=row['estado'],
            exportado=bool(row['exportado']),
            exportado_at=row['exportado_at']
        )
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de ApprovedRecommendation a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del registro
            
        Returns:
            ApprovedRecommendation: Instancia de ApprovedRecommendation
        """
        return cls(
            id=data.get('id'),
            fecha=data.get('fecha'),
            room_type_id=data.get('room_type_id'),
            channel_id=data.get('channel_id'),
            tarifa_base=data.get('tarifa_base'),
            tarifa_recomendada=data.get('tarifa_recomendada'),
            tarifa_aprobada=data.get('tarifa_aprobada'),
            created_at=data.get('created_at'),
            approved_at=data.get('approved_at'),
            estado=data.get('estado', "Aprobada"),
            exportado=data.get('exportado', False),
            exportado_at=data.get('exportado_at')
        )
    
    def to_dict(self):
        """
        Convierte la instancia de ApprovedRecommendation a un diccionario.
        
        Returns:
            dict: Diccionario con los datos del registro
        """
        return {
            'id': self.id,
            'fecha': self._format_date(self.fecha),
            'room_type_id': self.room_type_id,
            'channel_id': self.channel_id,
            'tarifa_base': self.tarifa_base,
            'tarifa_recomendada': self.tarifa_recomendada,
            'tarifa_aprobada': self.tarifa_aprobada,
            'created_at': self._format_datetime(self.created_at),
            'approved_at': self._format_datetime(self.approved_at),
            'estado': self.estado,
            'exportado': self.exportado,
            'exportado_at': self._format_datetime(self.exportado_at)
        }
    
    def save(self):
        """
        Guarda el registro en la base de datos.
        Si el registro ya existe (tiene id), lo actualiza.
        Si no existe, lo crea.
        
        Returns:
            int: ID del registro guardado
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.id:
                    # Actualizar registro existente
                    cursor.execute('''
                    UPDATE APPROVED_RECOMMENDATIONS
                    SET fecha = ?, room_type_id = ?, channel_id = ?,
                        tarifa_base = ?, tarifa_recomendada = ?, tarifa_aprobada = ?,
                        approved_at = ?, estado = ?, exportado = ?, exportado_at = ?
                    WHERE id = ?
                    ''', (
                        self._format_date(self.fecha), self.room_type_id, self.channel_id,
                        self.tarifa_base, self.tarifa_recomendada, self.tarifa_aprobada,
                        self._format_datetime(self.approved_at), self.estado,
                        int(self.exportado), self._format_datetime(self.exportado_at),
                        self.id
                    ))
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"No se encontró el registro con ID {self.id} para actualizar")
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                    INSERT INTO APPROVED_RECOMMENDATIONS (
                        fecha, room_type_id, channel_id,
                        tarifa_base, tarifa_recomendada, tarifa_aprobada,
                        created_at, approved_at, estado, exportado, exportado_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self._format_date(self.fecha), self.room_type_id, self.channel_id,
                        self.tarifa_base, self.tarifa_recomendada, self.tarifa_aprobada,
                        self._format_datetime(self.created_at), self._format_datetime(self.approved_at),
                        self.estado, int(self.exportado), self._format_datetime(self.exportado_at)
                    ))
                    
                    self.id = cursor.lastrowid
                
                conn.commit()
                logger.info(f"Recomendación aprobada guardada con ID {self.id}")
                return self.id
        except Exception as e:
            logger.error(f"Error al guardar la recomendación aprobada: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene un registro por su ID.
        
        Args:
            id (int): ID del registro a obtener
            
        Returns:
            ApprovedRecommendation: Instancia de ApprovedRecommendation o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM APPROVED_RECOMMENDATIONS WHERE id = ?', (id,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la recomendación aprobada con ID {id}: {e}")
            return None
    
    @classmethod
    def get_by_date_room_channel(cls, fecha, room_type_id, channel_id):
        """
        Obtiene un registro por su fecha, tipo de habitación y canal.
        
        Args:
            fecha (str/datetime): Fecha del registro
            room_type_id (int): ID del tipo de habitación
            channel_id (int): ID del canal de distribución
            
        Returns:
            ApprovedRecommendation: Instancia de ApprovedRecommendation o None si no existe
        """
        try:
            # Convertir fecha a string si es datetime
            if isinstance(fecha, datetime):
                fecha = fecha.strftime('%Y-%m-%d')
                
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM APPROVED_RECOMMENDATIONS 
                WHERE fecha = ? AND room_type_id = ? AND channel_id = ?
                ''', (fecha, room_type_id, channel_id))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la recomendación aprobada: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Obtiene todos los registros.
        
        Returns:
            list: Lista de instancias de ApprovedRecommendation
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM APPROVED_RECOMMENDATIONS ORDER BY fecha DESC, room_type_id, channel_id')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener todas las recomendaciones aprobadas: {e}")
            return []
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date, room_type_id=None, channel_id=None):
        """
        Obtiene los registros en un rango de fechas, opcionalmente filtrados por tipo de habitación y canal.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            channel_id (int, optional): ID del canal de distribución
            
        Returns:
            list: Lista de instancias de ApprovedRecommendation
        """
        try:
            # Convertir fechas a string si son datetime
            if isinstance(start_date, datetime):
                start_date = start_date.strftime('%Y-%m-%d')
            if isinstance(end_date, datetime):
                end_date = end_date.strftime('%Y-%m-%d')
                
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                SELECT * FROM APPROVED_RECOMMENDATIONS 
                WHERE fecha BETWEEN ? AND ?
                '''
                params = [start_date, end_date]
                
                if room_type_id is not None:
                    query += ' AND room_type_id = ?'
                    params.append(room_type_id)
                
                if channel_id is not None:
                    query += ' AND channel_id = ?'
                    params.append(channel_id)
                
                query += ' ORDER BY fecha, room_type_id, channel_id'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener recomendaciones aprobadas por rango de fechas: {e}")
            return []
    
    @classmethod
    def get_pending_export(cls):
        """
        Obtiene las recomendaciones aprobadas pendientes de exportar.
        
        Returns:
            list: Lista de instancias de ApprovedRecommendation
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM APPROVED_RECOMMENDATIONS 
                WHERE exportado = 0
                ORDER BY fecha, room_type_id, channel_id
                ''')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener recomendaciones aprobadas pendientes de exportar: {e}")
            return []
    
    @classmethod
    def delete(cls, id):
        """
        Elimina un registro por su ID.
        
        Args:
            id (int): ID del registro a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM APPROVED_RECOMMENDATIONS WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar la recomendación aprobada con ID {id}: {e}")
            return False
    
    @classmethod
    def bulk_insert(cls, recommendations):
        """
        Inserta múltiples registros en la base de datos.
        
        Args:
            recommendations (list): Lista de instancias de ApprovedRecommendation
            
        Returns:
            int: Número de registros insertados
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                values = []
                for rec in recommendations:
                    values.append((
                        rec._format_date(rec.fecha), rec.room_type_id, rec.channel_id,
                        rec.tarifa_base, rec.tarifa_recomendada, rec.tarifa_aprobada,
                        rec._format_datetime(rec.created_at), rec._format_datetime(rec.approved_at),
                        rec.estado, int(rec.exportado), rec._format_datetime(rec.exportado_at)
                    ))
                
                cursor.executemany('''
                INSERT INTO APPROVED_RECOMMENDATIONS (
                    fecha, room_type_id, channel_id,
                    tarifa_base, tarifa_recomendada, tarifa_aprobada,
                    created_at, approved_at, estado, exportado, exportado_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', values)
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error al insertar múltiples recomendaciones aprobadas: {e}")
            raise
    
    def mark_as_exported(self):
        """
        Marca la recomendación como exportada.
        
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            self.exportado = True
            self.exportado_at = datetime.now()
            self.estado = "Exportada"
            self.save()
            return True
        except Exception as e:
            logger.error(f"Error al marcar la recomendación como exportada: {e}")
            return False