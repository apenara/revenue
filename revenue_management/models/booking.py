#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que define el modelo para las reservas brutas
"""

from datetime import datetime
from models.base_model import BaseModel
from db.database import db
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class RawBooking(BaseModel):
    """
    Modelo para las reservas brutas (RAW_BOOKINGS)
    """
    
    def __init__(self, id=None, registro_num=None, fecha_reserva=None, fecha_llegada=None, 
                 fecha_salida=None, noches=None, cod_hab=None, tipo_habitacion=None, 
                 tarifa_neta=None, canal_distribucion=None, nombre_cliente=None, 
                 email_cliente=None, telefono_cliente=None, estado_reserva=None, 
                 observaciones=None, created_at=None):
        """
        Inicializa una instancia de RawBooking.
        
        Args:
            id (int, optional): ID de la reserva
            registro_num (str, optional): Número de registro de la reserva
            fecha_reserva (str/datetime): Fecha de la reserva
            fecha_llegada (str/datetime): Fecha de llegada
            fecha_salida (str/datetime): Fecha de salida
            noches (int): Número de noches
            cod_hab (str): Código de la habitación
            tipo_habitacion (str): Tipo de habitación
            tarifa_neta (float): Tarifa neta
            canal_distribucion (str): Canal de distribución
            nombre_cliente (str, optional): Nombre del cliente
            email_cliente (str, optional): Email del cliente
            telefono_cliente (str, optional): Teléfono del cliente
            estado_reserva (str): Estado de la reserva
            observaciones (str, optional): Observaciones
            created_at (str/datetime, optional): Fecha de creación del registro
        """
        self.id = id
        self.registro_num = registro_num
        self.fecha_reserva = self._parse_date(fecha_reserva)
        self.fecha_llegada = self._parse_date(fecha_llegada)
        self.fecha_salida = self._parse_date(fecha_salida)
        self.noches = noches
        self.cod_hab = cod_hab
        self.tipo_habitacion = tipo_habitacion
        self.tarifa_neta = tarifa_neta
        self.canal_distribucion = canal_distribucion
        self.nombre_cliente = nombre_cliente
        self.email_cliente = email_cliente
        self.telefono_cliente = telefono_cliente
        self.estado_reserva = estado_reserva
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
        Crea una instancia de RawBooking a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            RawBooking: Instancia de RawBooking
        """
        if not row:
            return None
        
        return cls(
            id=row['id'],
            registro_num=row['registro_num'],
            fecha_reserva=row['fecha_reserva'],
            fecha_llegada=row['fecha_llegada'],
            fecha_salida=row['fecha_salida'],
            noches=row['noches'],
            cod_hab=row['cod_hab'],
            tipo_habitacion=row['tipo_habitacion'],
            tarifa_neta=row['tarifa_neta'],
            canal_distribucion=row['canal_distribucion'],
            nombre_cliente=row['nombre_cliente'],
            email_cliente=row['email_cliente'],
            telefono_cliente=row['telefono_cliente'],
            estado_reserva=row['estado_reserva'],
            observaciones=row['observaciones'],
            created_at=row['created_at']
        )
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de RawBooking a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos de la reserva
            
        Returns:
            RawBooking: Instancia de RawBooking
        """
        return cls(
            id=data.get('id'),
            registro_num=data.get('registro_num'),
            fecha_reserva=data.get('fecha_reserva'),
            fecha_llegada=data.get('fecha_llegada'),
            fecha_salida=data.get('fecha_salida'),
            noches=data.get('noches'),
            cod_hab=data.get('cod_hab'),
            tipo_habitacion=data.get('tipo_habitacion'),
            tarifa_neta=data.get('tarifa_neta'),
            canal_distribucion=data.get('canal_distribucion'),
            nombre_cliente=data.get('nombre_cliente'),
            email_cliente=data.get('email_cliente'),
            telefono_cliente=data.get('telefono_cliente'),
            estado_reserva=data.get('estado_reserva'),
            observaciones=data.get('observaciones'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """
        Convierte la instancia de RawBooking a un diccionario.
        
        Returns:
            dict: Diccionario con los datos de la reserva
        """
        return {
            'id': self.id,
            'registro_num': self.registro_num,
            'fecha_reserva': self._format_date(self.fecha_reserva),
            'fecha_llegada': self._format_date(self.fecha_llegada),
            'fecha_salida': self._format_date(self.fecha_salida),
            'noches': self.noches,
            'cod_hab': self.cod_hab,
            'tipo_habitacion': self.tipo_habitacion,
            'tarifa_neta': self.tarifa_neta,
            'canal_distribucion': self.canal_distribucion,
            'nombre_cliente': self.nombre_cliente,
            'email_cliente': self.email_cliente,
            'telefono_cliente': self.telefono_cliente,
            'estado_reserva': self.estado_reserva,
            'observaciones': self.observaciones,
            'created_at': self._format_date(self.created_at)
        }
    
    def save(self):
        """
        Guarda la reserva en la base de datos.
        Si la reserva ya existe (tiene id), la actualiza.
        Si no existe, la crea.
        
        Returns:
            int: ID de la reserva guardada
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.id:
                    # Actualizar reserva existente
                    cursor.execute('''
                    UPDATE RAW_BOOKINGS
                    SET registro_num = ?, fecha_reserva = ?, fecha_llegada = ?, fecha_salida = ?,
                        noches = ?, cod_hab = ?, tipo_habitacion = ?, tarifa_neta = ?,
                        canal_distribucion = ?, nombre_cliente = ?, email_cliente = ?,
                        telefono_cliente = ?, estado_reserva = ?, observaciones = ?
                    WHERE id = ?
                    ''', (
                        self.registro_num, self._format_date(self.fecha_reserva),
                        self._format_date(self.fecha_llegada), self._format_date(self.fecha_salida),
                        self.noches, self.cod_hab, self.tipo_habitacion, self.tarifa_neta,
                        self.canal_distribucion, self.nombre_cliente, self.email_cliente,
                        self.telefono_cliente, self.estado_reserva, self.observaciones,
                        self.id
                    ))
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"No se encontró la reserva con ID {self.id} para actualizar")
                else:
                    # Crear nueva reserva
                    cursor.execute('''
                    INSERT INTO RAW_BOOKINGS (
                        registro_num, fecha_reserva, fecha_llegada, fecha_salida,
                        noches, cod_hab, tipo_habitacion, tarifa_neta,
                        canal_distribucion, nombre_cliente, email_cliente,
                        telefono_cliente, estado_reserva, observaciones
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self.registro_num, self._format_date(self.fecha_reserva),
                        self._format_date(self.fecha_llegada), self._format_date(self.fecha_salida),
                        self.noches, self.cod_hab, self.tipo_habitacion, self.tarifa_neta,
                        self.canal_distribucion, self.nombre_cliente, self.email_cliente,
                        self.telefono_cliente, self.estado_reserva, self.observaciones
                    ))
                    
                    self.id = cursor.lastrowid
                
                conn.commit()
                logger.info(f"Reserva guardada con ID {self.id}")
                return self.id
        except Exception as e:
            logger.error(f"Error al guardar la reserva: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene una reserva por su ID.
        
        Args:
            id (int): ID de la reserva a obtener
            
        Returns:
            RawBooking: Instancia de RawBooking o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RAW_BOOKINGS WHERE id = ?', (id,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la reserva con ID {id}: {e}")
            return None
    
    @classmethod
    def get_by_registro_num(cls, registro_num):
        """
        Obtiene una reserva por su número de registro.
        
        Args:
            registro_num (str): Número de registro de la reserva a obtener
            
        Returns:
            RawBooking: Instancia de RawBooking o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RAW_BOOKINGS WHERE registro_num = ?', (registro_num,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la reserva con número de registro {registro_num}: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Obtiene todas las reservas.
        
        Returns:
            list: Lista de instancias de RawBooking
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RAW_BOOKINGS ORDER BY fecha_llegada DESC')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener todas las reservas: {e}")
            return []
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """
        Obtiene las reservas en un rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            
        Returns:
            list: Lista de instancias de RawBooking
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
                SELECT * FROM RAW_BOOKINGS 
                WHERE (fecha_llegada BETWEEN ? AND ?) OR (fecha_salida BETWEEN ? AND ?)
                ORDER BY fecha_llegada
                ''', (start_date, end_date, start_date, end_date))
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener reservas por rango de fechas: {e}")
            return []
    
    @classmethod
    def delete(cls, id):
        """
        Elimina una reserva por su ID.
        
        Args:
            id (int): ID de la reserva a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM RAW_BOOKINGS WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar la reserva con ID {id}: {e}")
            return False
    
    @classmethod
    def bulk_insert(cls, bookings):
        """
        Inserta múltiples reservas en la base de datos.
        
        Args:
            bookings (list): Lista de instancias de RawBooking
            
        Returns:
            int: Número de reservas insertadas
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                values = []
                for booking in bookings:
                    values.append((
                        booking.registro_num, booking._format_date(booking.fecha_reserva),
                        booking._format_date(booking.fecha_llegada), booking._format_date(booking.fecha_salida),
                        booking.noches, booking.cod_hab, booking.tipo_habitacion, booking.tarifa_neta,
                        booking.canal_distribucion, booking.nombre_cliente, booking.email_cliente,
                        booking.telefono_cliente, booking.estado_reserva, booking.observaciones
                    ))
                
                cursor.executemany('''
                INSERT INTO RAW_BOOKINGS (
                    registro_num, fecha_reserva, fecha_llegada, fecha_salida,
                    noches, cod_hab, tipo_habitacion, tarifa_neta,
                    canal_distribucion, nombre_cliente, email_cliente,
                    telefono_cliente, estado_reserva, observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', values)
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error al insertar múltiples reservas: {e}")
            raise