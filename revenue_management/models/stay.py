#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que define el modelo para las estancias brutas
"""

from datetime import datetime
from models.base_model import BaseModel
from db.database import db
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class RawStay(BaseModel):
    """
    Modelo para las estancias brutas (RAW_STAYS)
    """
    
    def __init__(self, id=None, registro_num=None, fecha_checkin=None, fecha_checkout=None, 
                 noches=None, cod_hab=None, tipo_habitacion=None, valor_venta=None, 
                 canal_distribucion=None, nombre_cliente=None, email_cliente=None, 
                 telefono_cliente=None, estado_estancia=None, observaciones=None, created_at=None):
        """
        Inicializa una instancia de RawStay.
        
        Args:
            id (int, optional): ID de la estancia
            registro_num (str): Número de registro de la estancia
            fecha_checkin (str/datetime): Fecha de check-in
            fecha_checkout (str/datetime): Fecha de check-out
            noches (int): Número de noches
            cod_hab (str): Código de la habitación
            tipo_habitacion (str): Tipo de habitación
            valor_venta (float): Valor de venta
            canal_distribucion (str): Canal de distribución
            nombre_cliente (str): Nombre del cliente
            email_cliente (str, optional): Email del cliente
            telefono_cliente (str, optional): Teléfono del cliente
            estado_estancia (str): Estado de la estancia
            observaciones (str, optional): Observaciones
            created_at (str/datetime, optional): Fecha de creación del registro
        """
        self.id = id
        self.registro_num = registro_num
        self.fecha_checkin = self._parse_date(fecha_checkin)
        self.fecha_checkout = self._parse_date(fecha_checkout)
        self.noches = noches
        self.cod_hab = cod_hab
        self.tipo_habitacion = tipo_habitacion
        self.valor_venta = valor_venta
        self.canal_distribucion = canal_distribucion
        self.nombre_cliente = nombre_cliente
        self.email_cliente = email_cliente
        self.telefono_cliente = telefono_cliente
        self.estado_estancia = estado_estancia
        self.observaciones = observaciones
        self.created_at = self._parse_date(created_at) if created_at else datetime.now()
    
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
    
    @classmethod
    def from_row(cls, row):
        """
        Crea una instancia de RawStay a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            RawStay: Instancia de RawStay
        """
        if not row:
            return None
        
        return cls(
            id=row['id'],
            registro_num=row['registro_num'],
            fecha_checkin=row['fecha_checkin'],
            fecha_checkout=row['fecha_checkout'],
            noches=row['noches'],
            cod_hab=row['cod_hab'],
            tipo_habitacion=row['tipo_habitacion'],
            valor_venta=row['valor_venta'],
            canal_distribucion=row['canal_distribucion'],
            nombre_cliente=row['nombre_cliente'],
            email_cliente=row['email_cliente'],
            telefono_cliente=row['telefono_cliente'],
            estado_estancia=row['estado_estancia'],
            observaciones=row['observaciones'],
            created_at=row['created_at']
        )
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de RawStay a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos de la estancia
            
        Returns:
            RawStay: Instancia de RawStay
        """
        return cls(
            id=data.get('id'),
            registro_num=data.get('registro_num'),
            fecha_checkin=data.get('fecha_checkin'),
            fecha_checkout=data.get('fecha_checkout'),
            noches=data.get('noches'),
            cod_hab=data.get('cod_hab'),
            tipo_habitacion=data.get('tipo_habitacion'),
            valor_venta=data.get('valor_venta'),
            canal_distribucion=data.get('canal_distribucion'),
            nombre_cliente=data.get('nombre_cliente'),
            email_cliente=data.get('email_cliente'),
            telefono_cliente=data.get('telefono_cliente'),
            estado_estancia=data.get('estado_estancia'),
            observaciones=data.get('observaciones'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """
        Convierte la instancia de RawStay a un diccionario.
        
        Returns:
            dict: Diccionario con los datos de la estancia
        """
        return {
            'id': self.id,
            'registro_num': self.registro_num,
            'fecha_checkin': self._format_date(self.fecha_checkin),
            'fecha_checkout': self._format_date(self.fecha_checkout),
            'noches': self.noches,
            'cod_hab': self.cod_hab,
            'tipo_habitacion': self.tipo_habitacion,
            'valor_venta': self.valor_venta,
            'canal_distribucion': self.canal_distribucion,
            'nombre_cliente': self.nombre_cliente,
            'email_cliente': self.email_cliente,
            'telefono_cliente': self.telefono_cliente,
            'estado_estancia': self.estado_estancia,
            'observaciones': self.observaciones,
            'created_at': self._format_date(self.created_at)
        }
    
    def save(self):
        """
        Guarda la estancia en la base de datos.
        Si la estancia ya existe (tiene id), la actualiza.
        Si no existe, la crea.
        
        Returns:
            int: ID de la estancia guardada
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.id:
                    # Actualizar estancia existente
                    cursor.execute('''
                    UPDATE RAW_STAYS
                    SET registro_num = ?, fecha_checkin = ?, fecha_checkout = ?,
                        noches = ?, cod_hab = ?, tipo_habitacion = ?, valor_venta = ?,
                        canal_distribucion = ?, nombre_cliente = ?, email_cliente = ?,
                        telefono_cliente = ?, estado_estancia = ?, observaciones = ?
                    WHERE id = ?
                    ''', (
                        self.registro_num, self._format_date(self.fecha_checkin),
                        self._format_date(self.fecha_checkout), self.noches,
                        self.cod_hab, self.tipo_habitacion, self.valor_venta,
                        self.canal_distribucion, self.nombre_cliente, self.email_cliente,
                        self.telefono_cliente, self.estado_estancia, self.observaciones,
                        self.id
                    ))
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"No se encontró la estancia con ID {self.id} para actualizar")
                else:
                    # Crear nueva estancia
                    cursor.execute('''
                    INSERT INTO RAW_STAYS (
                        registro_num, fecha_checkin, fecha_checkout,
                        noches, cod_hab, tipo_habitacion, valor_venta,
                        canal_distribucion, nombre_cliente, email_cliente,
                        telefono_cliente, estado_estancia, observaciones
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self.registro_num, self._format_date(self.fecha_checkin),
                        self._format_date(self.fecha_checkout), self.noches,
                        self.cod_hab, self.tipo_habitacion, self.valor_venta,
                        self.canal_distribucion, self.nombre_cliente, self.email_cliente,
                        self.telefono_cliente, self.estado_estancia, self.observaciones
                    ))
                    
                    self.id = cursor.lastrowid
                
                conn.commit()
                logger.info(f"Estancia guardada con ID {self.id}")
                return self.id
        except Exception as e:
            logger.error(f"Error al guardar la estancia: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene una estancia por su ID.
        
        Args:
            id (int): ID de la estancia a obtener
            
        Returns:
            RawStay: Instancia de RawStay o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RAW_STAYS WHERE id = ?', (id,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la estancia con ID {id}: {e}")
            return None
    
    @classmethod
    def get_by_registro_num(cls, registro_num):
        """
        Obtiene una estancia por su número de registro.
        
        Args:
            registro_num (str): Número de registro de la estancia a obtener
            
        Returns:
            RawStay: Instancia de RawStay o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RAW_STAYS WHERE registro_num = ?', (registro_num,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la estancia con número de registro {registro_num}: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Obtiene todas las estancias.
        
        Returns:
            list: Lista de instancias de RawStay
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RAW_STAYS ORDER BY fecha_checkin DESC')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener todas las estancias: {e}")
            return []
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """
        Obtiene las estancias en un rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            
        Returns:
            list: Lista de instancias de RawStay
        """
        try:
            # Convertir fechas a string si son datetime
            if isinstance(start_date, datetime):
                start_date = start_date.strftime('%Y-%m-%d')
            if isinstance(end_date, datetime):
                end_date = end_date.strftime('%Y-%m-%d')
                
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM RAW_STAYS 
                WHERE (fecha_checkin BETWEEN ? AND ?) OR (fecha_checkout BETWEEN ? AND ?)
                ORDER BY fecha_checkin
                ''', (start_date, end_date, start_date, end_date))
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener estancias por rango de fechas: {e}")
            return []
    
    @classmethod
    def delete(cls, id):
        """
        Elimina una estancia por su ID.
        
        Args:
            id (int): ID de la estancia a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM RAW_STAYS WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar la estancia con ID {id}: {e}")
            return False
    
    @classmethod
    def bulk_insert(cls, stays):
        """
        Inserta múltiples estancias en la base de datos.
        
        Args:
            stays (list): Lista de instancias de RawStay
            
        Returns:
            int: Número de estancias insertadas
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                values = []
                for stay in stays:
                    values.append((
                        stay.registro_num, stay._format_date(stay.fecha_checkin),
                        stay._format_date(stay.fecha_checkout), stay.noches,
                        stay.cod_hab, stay.tipo_habitacion, stay.valor_venta,
                        stay.canal_distribucion, stay.nombre_cliente, stay.email_cliente,
                        stay.telefono_cliente, stay.estado_estancia, stay.observaciones
                    ))
                
                cursor.executemany('''
                INSERT INTO RAW_STAYS (
                    registro_num, fecha_checkin, fecha_checkout,
                    noches, cod_hab, tipo_habitacion, valor_venta,
                    canal_distribucion, nombre_cliente, email_cliente,
                    telefono_cliente, estado_estancia, observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', values)
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error al insertar múltiples estancias: {e}")
            raise