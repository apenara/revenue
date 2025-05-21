#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para la conexión a la base de datos
"""

import unittest
import os
import sys
import sqlite3
from pathlib import Path

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db.database import Database, db
from config import config

class TestDatabase(unittest.TestCase):
    """
    Pruebas unitarias para la clase Database
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas
        """
        # Crear una instancia de prueba con una base de datos temporal
        self.test_db_path = Path("test_db.db")
        self.original_db_path = config.get("database.path")
        
        # Modificar temporalmente la configuración
        config.set("database.path", str(self.test_db_path))
        
        # Crear una instancia de prueba
        self.test_db = Database()
    
    def tearDown(self):
        """
        Limpieza después de las pruebas
        """
        # Cerrar la conexión si está abierta
        if self.test_db.connection:
            self.test_db.close()
        
        # Eliminar la base de datos de prueba si existe
        if self.test_db_path.exists():
            os.remove(self.test_db_path)
        
        # Restaurar la configuración original
        config.set("database.path", self.original_db_path)
    
    def test_connection(self):
        """
        Prueba la conexión a la base de datos
        """
        # Verificar que se puede establecer una conexión
        conn = self.test_db.connect()
        self.assertIsNotNone(conn)
        self.assertIsInstance(conn, sqlite3.Connection)
        
        # Verificar que se puede cerrar la conexión
        self.test_db.close()
        self.assertIsNone(self.test_db.connection)
    
    def test_get_connection_context(self):
        """
        Prueba el contexto de conexión
        """
        # Verificar que el contexto funciona correctamente
        with self.test_db.get_connection() as conn:
            self.assertIsNotNone(conn)
            self.assertIsInstance(conn, sqlite3.Connection)
        
        # Verificar que la conexión se cierra al salir del contexto
        self.assertIsNone(self.test_db.connection)
    
    def test_execute_query(self):
        """
        Prueba la ejecución de consultas
        """
        # Crear una tabla de prueba
        self.test_db.execute_query("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        """)
        
        # Insertar datos
        self.test_db.execute_query(
            "INSERT INTO test_table (name) VALUES (?)",
            ("Test Name",)
        )
        
        # Consultar datos
        rows = self.test_db.execute_query("SELECT * FROM test_table")
        
        # Verificar resultados
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Test Name")
    
    def test_execute_many(self):
        """
        Prueba la ejecución de múltiples consultas
        """
        # Crear una tabla de prueba
        self.test_db.execute_query("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        """)
        
        # Insertar múltiples datos
        data = [("Name 1",), ("Name 2",), ("Name 3",)]
        affected_rows = self.test_db.execute_many(
            "INSERT INTO test_table (name) VALUES (?)",
            data
        )
        
        # Verificar que se insertaron todas las filas
        self.assertEqual(affected_rows, 3)
        
        # Consultar datos
        rows = self.test_db.execute_query("SELECT * FROM test_table")
        
        # Verificar resultados
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["name"], "Name 1")
        self.assertEqual(rows[1]["name"], "Name 2")
        self.assertEqual(rows[2]["name"], "Name 3")
    
    def test_backup_restore(self):
        """
        Prueba la creación y restauración de copias de seguridad
        """
        # Crear una tabla de prueba con datos
        self.test_db.execute_query("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        """)
        
        self.test_db.execute_query(
            "INSERT INTO test_table (name) VALUES (?)",
            ("Backup Test",)
        )
        
        # Crear una copia de seguridad
        backup_path = self.test_db.create_backup("test_backup")
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
        
        # Modificar los datos originales
        self.test_db.execute_query(
            "UPDATE test_table SET name = ? WHERE id = 1",
            ("Modified Data",)
        )
        
        # Verificar que los datos se modificaron
        rows = self.test_db.execute_query("SELECT * FROM test_table")
        self.assertEqual(rows[0]["name"], "Modified Data")
        
        # Restaurar la copia de seguridad
        success = self.test_db.restore_backup(backup_path)
        self.assertTrue(success)
        
        # Verificar que los datos se restauraron
        rows = self.test_db.execute_query("SELECT * FROM test_table")
        self.assertEqual(rows[0]["name"], "Backup Test")
        
        # Limpiar
        if backup_path.exists():
            os.remove(backup_path)

if __name__ == "__main__":
    unittest.main()