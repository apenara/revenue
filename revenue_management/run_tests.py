#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para ejecutar todas las pruebas del Framework de Revenue Management
"""

import os
import sys
import unittest
import argparse
from pathlib import Path

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent))

def run_tests(test_type=None, verbose=False):
    """
    Ejecuta las pruebas especificadas.
    
    Args:
        test_type (str, optional): Tipo de pruebas a ejecutar ('unit', 'integration', 'all')
        verbose (bool, optional): Si es True, muestra información detallada de las pruebas
    
    Returns:
        bool: True si todas las pruebas pasaron, False en caso contrario
    """
    # Configurar el nivel de verbosidad
    verbosity = 2 if verbose else 1
    
    # Crear el cargador de pruebas
    loader = unittest.TestLoader()
    
    # Crear el ejecutor de pruebas
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    # Determinar qué pruebas ejecutar
    if test_type == 'unit' or test_type is None:
        print("Ejecutando pruebas unitarias...")
        unit_tests = loader.discover('tests/unit', pattern='test_*.py')
        unit_result = runner.run(unit_tests)
        
        if test_type == 'unit':
            return unit_result.wasSuccessful()
    
    if test_type == 'integration' or test_type is None:
        print("\nEjecutando pruebas de integración...")
        integration_tests = loader.discover('tests/integration', pattern='test_*.py')
        integration_result = runner.run(integration_tests)
        
        if test_type == 'integration':
            return integration_result.wasSuccessful()
    
    if test_type == 'all' or test_type is None:
        print("\nEjecutando todas las pruebas...")
        all_tests = loader.discover('tests', pattern='test_*.py')
        all_result = runner.run(all_tests)
        
        if test_type == 'all':
            return all_result.wasSuccessful()
    
    # Si no se especificó un tipo de prueba, devolver True solo si todas las pruebas pasaron
    if test_type is None:
        return unit_result.wasSuccessful() and integration_result.wasSuccessful()
    
    # Si se llegó aquí, es porque se especificó un tipo de prueba inválido
    print(f"Tipo de prueba inválido: {test_type}")
    return False

if __name__ == "__main__":
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Ejecutar pruebas del Framework de Revenue Management')
    parser.add_argument('--type', choices=['unit', 'integration', 'all'], default=None,
                        help='Tipo de pruebas a ejecutar (unit, integration, all)')
    parser.add_argument('--verbose', action='store_true',
                        help='Mostrar información detallada de las pruebas')
    
    # Parsear los argumentos
    args = parser.parse_args()
    
    # Ejecutar las pruebas
    success = run_tests(args.type, args.verbose)
    
    # Salir con el código de estado adecuado
    sys.exit(0 if success else 1)