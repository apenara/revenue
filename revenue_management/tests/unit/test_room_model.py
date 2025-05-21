#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para el modelo Room
"""

import unittest
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.room import Room
from db.database import db

class TestRoomModel(unittest.TestCase):
    """
    Pruebas unitarias para el modelo Room
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear una tabla temporal para las pruebas
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ROOM_TYPES_TEST (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cod_hab TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                description TEXT,
                amenities TEXT,
                num_config INTEGER NOT NULL
            )
            """)
            conn.commit()
        
        # Guardar el nombre de la tabla original
        self.original_table = Room._table_name
        
        # Cambiar el nombre de la tabla para las pruebas
        Room._table_name = "ROOM_TYPES_TEST"
        
        # Datos de prueba
        self.test_room_data = {
            'cod_hab': 'TEST',
            'name': 'Test Room',
            'capacity': 2,
            'description': 'Room for testing',
            'amenities': 'WiFi, TV',
            'num_config': 5
        }
    
    def tearDown(self):
        """
        Limpieza después de las pruebas
        """
        # Restaurar el nombre de la tabla original
        Room._table_name = self.original_table
        
        # Eliminar la tabla de prueba
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS ROOM_TYPES_TEST")
            conn.commit()
    
    def test_create_room(self):
        """
        Prueba la creación de una habitación
        """
        # Crear una instancia de Room
        room = Room(**self.test_room_data)
        
        # Guardar en la base de datos
        room_id = room.save()
        
        # Verificar que se asignó un ID
        self.assertIsNotNone(room_id)
        self.assertGreater(room_id, 0)
        
        # Verificar que el ID se asignó a la instancia
        self.assertEqual(room.id, room_id)
    
    def test_get_by_id(self):
        """
        Prueba la obtención de una habitación por ID
        """
        # Crear una habitación
        room = Room(**self.test_room_data)
        room_id = room.save()
        
        # Obtener la habitación por ID
        retrieved_room = Room.get_by_id(room_id)
        
        # Verificar que se obtuvo la habitación correcta
        self.assertIsNotNone(retrieved_room)
        self.assertEqual(retrieved_room.id, room_id)
        self.assertEqual(retrieved_room.cod_hab, self.test_room_data['cod_hab'])
        self.assertEqual(retrieved_room.name, self.test_room_data['name'])
        self.assertEqual(retrieved_room.capacity, self.test_room_data['capacity'])
        self.assertEqual(retrieved_room.description, self.test_room_data['description'])
        self.assertEqual(retrieved_room.amenities, self.test_room_data['amenities'])
        self.assertEqual(retrieved_room.num_config, self.test_room_data['num_config'])
    
    def test_get_by_cod_hab(self):
        """
        Prueba la obtención de una habitación por código
        """
        # Crear una habitación
        room = Room(**self.test_room_data)
        room.save()
        
        # Obtener la habitación por código
        retrieved_room = Room.get_by_cod_hab(self.test_room_data['cod_hab'])
        
        # Verificar que se obtuvo la habitación correcta
        self.assertIsNotNone(retrieved_room)
        self.assertEqual(retrieved_room.cod_hab, self.test_room_data['cod_hab'])
        self.assertEqual(retrieved_room.name, self.test_room_data['name'])
    
    def test_get_all(self):
        """
        Prueba la obtención de todas las habitaciones
        """
        # Crear varias habitaciones
        room1 = Room(cod_hab='TEST1', name='Test Room 1', capacity=2, description='Room 1', amenities='WiFi', num_config=3)
        room2 = Room(cod_hab='TEST2', name='Test Room 2', capacity=3, description='Room 2', amenities='TV', num_config=4)
        room3 = Room(cod_hab='TEST3', name='Test Room 3', capacity=4, description='Room 3', amenities='Minibar', num_config=5)
        
        room1.save()
        room2.save()
        room3.save()
        
        # Obtener todas las habitaciones
        rooms = Room.get_all()
        
        # Verificar que se obtuvieron todas las habitaciones
        self.assertEqual(len(rooms), 3)
        
        # Verificar que los códigos de habitación son correctos
        codes = [room.cod_hab for room in rooms]
        self.assertIn('TEST1', codes)
        self.assertIn('TEST2', codes)
        self.assertIn('TEST3', codes)
    
    def test_update_room(self):
        """
        Prueba la actualización de una habitación
        """
        # Crear una habitación
        room = Room(**self.test_room_data)
        room_id = room.save()
        
        # Modificar la habitación
        room.name = "Updated Room Name"
        room.capacity = 3
        room.save()
        
        # Obtener la habitación actualizada
        updated_room = Room.get_by_id(room_id)
        
        # Verificar que los cambios se guardaron
        self.assertEqual(updated_room.name, "Updated Room Name")
        self.assertEqual(updated_room.capacity, 3)
    
    def test_delete_room(self):
        """
        Prueba la eliminación de una habitación
        """
        # Crear una habitación
        room = Room(**self.test_room_data)
        room_id = room.save()
        
        # Verificar que la habitación existe
        self.assertIsNotNone(Room.get_by_id(room_id))
        
        # Eliminar la habitación
        success = Room.delete(room_id)
        
        # Verificar que la eliminación fue exitosa
        self.assertTrue(success)
        
        # Verificar que la habitación ya no existe
        self.assertIsNone(Room.get_by_id(room_id))
    
    def test_to_dict(self):
        """
        Prueba la conversión de una habitación a diccionario
        """
        # Crear una habitación
        room = Room(**self.test_room_data)
        room_id = room.save()
        
        # Convertir a diccionario
        room_dict = room.to_dict()
        
        # Verificar que el diccionario contiene todos los campos
        self.assertEqual(room_dict['id'], room_id)
        self.assertEqual(room_dict['cod_hab'], self.test_room_data['cod_hab'])
        self.assertEqual(room_dict['name'], self.test_room_data['name'])
        self.assertEqual(room_dict['capacity'], self.test_room_data['capacity'])
        self.assertEqual(room_dict['description'], self.test_room_data['description'])
        self.assertEqual(room_dict['amenities'], self.test_room_data['amenities'])
        self.assertEqual(room_dict['num_config'], self.test_room_data['num_config'])
    
    def test_from_dict(self):
        """
        Prueba la creación de una habitación a partir de un diccionario
        """
        # Crear un diccionario con datos de habitación
        room_dict = {
            'id': None,
            'cod_hab': 'DICT',
            'name': 'Dict Room',
            'capacity': 4,
            'description': 'Room from dict',
            'amenities': 'WiFi, TV, Minibar',
            'num_config': 6
        }
        
        # Crear una habitación a partir del diccionario
        room = Room.from_dict(room_dict)
        
        # Verificar que los datos se asignaron correctamente
        self.assertEqual(room.cod_hab, room_dict['cod_hab'])
        self.assertEqual(room.name, room_dict['name'])
        self.assertEqual(room.capacity, room_dict['capacity'])
        self.assertEqual(room.description, room_dict['description'])
        self.assertEqual(room.amenities, room_dict['amenities'])
        self.assertEqual(room.num_config, room_dict['num_config'])
    
    def test_get_total_rooms(self):
        """
        Prueba la obtención del número total de habitaciones
        """
        # Crear varias habitaciones
        room1 = Room(cod_hab='TOTAL1', name='Total Room 1', capacity=2, description='Room 1', amenities='WiFi', num_config=3)
        room2 = Room(cod_hab='TOTAL2', name='Total Room 2', capacity=3, description='Room 2', amenities='TV', num_config=4)
        room3 = Room(cod_hab='TOTAL3', name='Total Room 3', capacity=4, description='Room 3', amenities='Minibar', num_config=5)
        
        room1.save()
        room2.save()
        room3.save()
        
        # Obtener el número total de habitaciones
        total_rooms = Room.get_total_rooms()
        
        # Verificar que el total es correcto (3 + 4 + 5 = 12)
        self.assertEqual(total_rooms, 12)

if __name__ == "__main__":
    unittest.main()