# Guía de Solución de Problemas

## Introducción

Esta guía proporciona soluciones a problemas comunes que pueden surgir durante el uso del Framework de Revenue Management. Si encuentra un problema que no está cubierto en esta guía, contacte al equipo de soporte.

## Índice

1. [Problemas de Instalación](#1-problemas-de-instalación)
2. [Problemas de Inicio de Sesión](#2-problemas-de-inicio-de-sesión)
3. [Problemas de Ingesta de Datos](#3-problemas-de-ingesta-de-datos)
4. [Problemas de Análisis](#4-problemas-de-análisis)
5. [Problemas de Previsión](#5-problemas-de-previsión)
6. [Problemas de Gestión de Tarifas](#6-problemas-de-gestión-de-tarifas)
7. [Problemas de Exportación](#7-problemas-de-exportación)
8. [Problemas de Base de Datos](#8-problemas-de-base-de-datos)
9. [Problemas de Rendimiento](#9-problemas-de-rendimiento)
10. [Errores Comunes](#10-errores-comunes)

## 1. Problemas de Instalación

### 1.1 Error al instalar dependencias

**Problema**: Al ejecutar `pip install -r requirements.txt`, se producen errores.

**Soluciones**:
1. Asegúrese de tener instalada la versión correcta de Python (3.9 o superior).
2. Actualice pip a la última versión:
   ```bash
   python -m pip install --upgrade pip
   ```
3. Instale las dependencias una por una para identificar cuál está causando el problema:
   ```bash
   pip install pandas
   pip install polars
   pip install streamlit
   # etc.
   ```
4. Si hay problemas con paquetes que requieren compilación (como numpy), instale las herramientas de desarrollo de Python:
   - En Windows: Instale Visual C++ Build Tools
   - En Linux: `sudo apt-get install python3-dev`
   - En macOS: `xcode-select --install`

### 1.2 Error al inicializar la base de datos

**Problema**: Al ejecutar `python initialize_db.py`, se produce un error.

**Soluciones**:
1. Asegúrese de que tiene permisos de escritura en el directorio donde se creará la base de datos.
2. Verifique que el archivo `config.yaml` existe y tiene el formato correcto.
3. Si la base de datos ya existe, elimínela y vuelva a ejecutar el script:
   ```bash
   rm db/revenue_management.db
   python initialize_db.py
   ```
4. Revise los logs para obtener más información sobre el error.

### 1.3 Error al iniciar la aplicación

**Problema**: Al ejecutar `streamlit run app.py`, se produce un error.

**Soluciones**:
1. Asegúrese de que todas las dependencias están instaladas correctamente.
2. Verifique que el archivo `config.yaml` existe y tiene el formato correcto.
3. Compruebe que la base de datos está inicializada correctamente.
4. Revise los logs para obtener más información sobre el error.
5. Intente ejecutar la aplicación en modo debug:
   ```bash
   streamlit run app.py --logger.level=debug
   ```

## 2. Problemas de Inicio de Sesión

### 2.1 No puedo iniciar sesión

**Problema**: Al intentar iniciar sesión, se muestra un mensaje de error.

**Soluciones**:
1. Verifique que está introduciendo las credenciales correctas.
2. Si ha olvidado la contraseña, puede restablecerla utilizando el script `reset_password.py`:
   ```bash
   python reset_password.py --username admin --password nueva_contraseña
   ```
3. Si el problema persiste, puede haber un problema con la base de datos. Intente restaurar una copia de seguridad o reinicializar la base de datos.

### 2.2 La sesión expira rápidamente

**Problema**: La sesión expira demasiado rápido y tengo que iniciar sesión con frecuencia.

**Soluciones**:
1. Aumente el tiempo de expiración de la sesión en el archivo `config.yaml`:
   ```yaml
   app:
     session_expiry_seconds: 3600  # 1 hora
   ```
2. Asegúrese de que su navegador acepta cookies.
3. Si está utilizando un proxy o VPN, puede haber problemas con la gestión de sesiones. Intente desactivarlos.

## 3. Problemas de Ingesta de Datos

### 3.1 Error al importar archivo Excel

**Problema**: Al intentar importar un archivo Excel, se produce un error.

**Soluciones**:
1. Asegúrese de que el archivo Excel tiene el formato correcto.
2. Verifique que el archivo no está dañado abriéndolo con Excel.
3. Compruebe que el archivo no está siendo utilizado por otra aplicación.
4. Verifique que los nombres de las hojas coinciden con los configurados en `config.yaml`.
5. Si el archivo es muy grande, intente dividirlo en archivos más pequeños.
6. Revise los logs para obtener más información sobre el error.

### 3.2 Datos incorrectos después de la importación

**Problema**: Los datos importados no son correctos o están incompletos.

**Soluciones**:
1. Verifique que el archivo Excel tiene el formato correcto.
2. Compruebe que los nombres de las columnas coinciden con los esperados por el sistema.
3. Asegúrese de que los tipos de datos son correctos (fechas, números, etc.).
4. Verifique que no hay filas vacías o con datos incompletos.
5. Compruebe que los códigos de habitación coinciden con los configurados en el sistema.
6. Revise los logs para obtener más información sobre el error.

### 3.3 Duplicación de datos

**Problema**: Al importar datos, se duplican registros existentes.

**Soluciones**:
1. Utilice la opción "Sobrescribir datos existentes" al importar.
2. Antes de importar, elimine los datos existentes para el mismo período:
   ```sql
   DELETE FROM RAW_BOOKINGS WHERE fecha_reserva BETWEEN '2025-01-01' AND '2025-01-31';
   ```
3. Verifique que no hay duplicados en el archivo Excel antes de importarlo.
4. Utilice la herramienta de limpieza de datos para eliminar duplicados después de la importación.

## 4. Problemas de Análisis

### 4.1 KPIs incorrectos

**Problema**: Los KPIs calculados no son correctos o no coinciden con otros informes.

**Soluciones**:
1. Verifique que los datos importados son correctos y completos.
2. Compruebe que está utilizando el mismo rango de fechas y filtros que en otros informes.
3. Revise la metodología de cálculo de KPIs en la documentación.
4. Utilice la herramienta de depuración para ver los cálculos intermedios:
   ```python
   from services.analysis.kpi_calculator import KpiCalculator
   
   calculator = KpiCalculator()
   kpi_df = calculator.calculate_kpis('2025-01-01', '2025-01-31', debug=True)
   print(kpi_df)
   ```
5. Si el problema persiste, puede haber un error en los algoritmos de cálculo. Contacte al equipo de soporte.

### 4.2 Gráficos no se muestran correctamente

**Problema**: Los gráficos no se muestran correctamente o están vacíos.

**Soluciones**:
1. Asegúrese de que hay datos disponibles para el rango de fechas seleccionado.
2. Verifique que está utilizando un navegador compatible (Chrome, Firefox, Edge).
3. Compruebe que JavaScript está habilitado en su navegador.
4. Limpie la caché del navegador y vuelva a cargar la página.
5. Si utiliza un bloqueador de anuncios, desactívelo para este sitio.
6. Revise los logs para obtener más información sobre el error.

### 4.3 Análisis lento

**Problema**: El análisis de KPIs es muy lento.

**Soluciones**:
1. Reduzca el rango de fechas para el análisis.
2. Utilice filtros para reducir la cantidad de datos a procesar.
3. Cierre otras aplicaciones para liberar memoria.
4. Verifique que la base de datos no es demasiado grande. Si es necesario, archive datos antiguos.
5. Optimice la base de datos ejecutando el comando `VACUUM`:
   ```python
   from db.database import db
   
   db.execute_query("VACUUM")
   ```
6. Considere actualizar el hardware del servidor si el problema persiste.

## 5. Problemas de Previsión

### 5.1 Error al generar pronósticos

**Problema**: Al intentar generar pronósticos, se produce un error.

**Soluciones**:
1. Asegúrese de que hay suficientes datos históricos para entrenar el modelo (al menos 30 días).
2. Verifique que los datos históricos no tienen huecos o inconsistencias.
3. Compruebe que los parámetros de forecasting en `config.yaml` son adecuados.
4. Si utiliza Prophet, asegúrese de que está instalado correctamente:
   ```bash
   pip uninstall prophet
   pip install prophet
   ```
5. Revise los logs para obtener más información sobre el error.

### 5.2 Pronósticos poco precisos

**Problema**: Los pronósticos generados no son precisos o tienen valores extremos.

**Soluciones**:
1. Asegúrese de que hay suficientes datos históricos para entrenar el modelo.
2. Verifique que los datos históricos son representativos y no contienen anomalías.
3. Ajuste los parámetros del modelo en `config.yaml`:
   ```yaml
   forecasting:
     changepoint_prior_scale: 0.05  # Reducir para pronósticos más suaves
     seasonality_prior_scale: 10.0  # Ajustar según la estacionalidad de los datos
   ```
4. Considere utilizar un modelo diferente o combinar varios modelos.
5. Utilice la herramienta de ajuste manual para corregir pronósticos extremos.

### 5.3 No se pueden ajustar pronósticos

**Problema**: Al intentar ajustar manualmente los pronósticos, los cambios no se guardan.

**Soluciones**:
1. Asegúrese de que tiene permisos para editar pronósticos.
2. Verifique que está haciendo clic en "Guardar Ajustes" después de realizar los cambios.
3. Compruebe que los valores introducidos son válidos (entre 0 y 100 para ocupación).
4. Revise los logs para obtener más información sobre el error.
5. Si el problema persiste, puede editar directamente la base de datos:
   ```sql
   UPDATE FORECASTS SET ocupacion_prevista = 75.0, ajustado_manualmente = 1 WHERE fecha = '2025-02-01' AND room_type_id = 1;
   ```

## 6. Problemas de Gestión de Tarifas

### 6.1 Error al configurar reglas

**Problema**: Al intentar crear o editar reglas de pricing, se produce un error.

**Soluciones**:
1. Asegúrese de que los parámetros de la regla son válidos.
2. Verifique que el formato JSON de los parámetros es correcto.
3. Compruebe que no hay conflictos con otras reglas (misma prioridad).
4. Revise los logs para obtener más información sobre el error.
5. Si el problema persiste, puede editar directamente la base de datos:
   ```sql
   INSERT INTO RULE_CONFIGS (nombre, descripcion, parametros, prioridad, activa) VALUES ('Regla de Temporada', 'Ajusta tarifas según la temporada', '{"tipo":"temporada","factores":{"Baja":0.9,"Media":1.0,"Alta":1.2}}', 1, 1);
   ```

### 6.2 Recomendaciones de tarifas incorrectas

**Problema**: Las recomendaciones de tarifas generadas no son correctas o tienen valores extremos.

**Soluciones**:
1. Verifique que los pronósticos son precisos.
2. Compruebe que las reglas de pricing están configuradas correctamente.
3. Asegúrese de que las tarifas base son adecuadas.
4. Ajuste los factores de las reglas para evitar valores extremos:
   ```yaml
   pricing:
     min_price_factor: 0.7  # Límite inferior para factores de precio
     max_price_factor: 1.3  # Límite superior para factores de precio
   ```
5. Utilice la herramienta de ajuste manual para corregir recomendaciones extremas.

### 6.3 No se pueden aprobar recomendaciones

**Problema**: Al intentar aprobar recomendaciones de tarifas, se produce un error.

**Soluciones**:
1. Asegúrese de que tiene permisos para aprobar recomendaciones.
2. Verifique que está haciendo clic en "Guardar Aprobaciones" después de seleccionar las recomendaciones.
3. Compruebe que los valores de las tarifas aprobadas son válidos.
4. Revise los logs para obtener más información sobre el error.
5. Si el problema persiste, puede editar directamente la base de datos:
   ```sql
   UPDATE APPROVED_RECOMMENDATIONS SET estado = 'Aprobada', approved_at = CURRENT_TIMESTAMP WHERE fecha = '2025-02-01' AND room_type_id = 1 AND channel_id = 1;
   ```

## 7. Problemas de Exportación

### 7.1 Error al exportar tarifas

**Problema**: Al intentar exportar tarifas, se produce un error.

**Soluciones**:
1. Asegúrese de que hay tarifas aprobadas para exportar.
2. Verifique que el directorio `data_exports` existe y tiene permisos de escritura.
3. Compruebe que la plantilla de exportación existe en el directorio `templates`.
4. Si el problema es con la plantilla, restaure la plantilla por defecto:
   ```bash
   cp templates/export_template_backup.xlsx templates/export_template.xlsx
   ```
5. Revise los logs para obtener más información sobre el error.

### 7.2 Formato de exportación incorrecto

**Problema**: El archivo Excel exportado no tiene el formato correcto para el PMS Zeus.

**Soluciones**:
1. Verifique que está utilizando la plantilla de exportación correcta.
2. Compruebe que la configuración de exportación en `config.yaml` es correcta.
3. Si es necesario, modifique la plantilla de exportación para que coincida con el formato requerido por el PMS Zeus.
4. Contacte al equipo de soporte del PMS Zeus para obtener la plantilla correcta.

### 7.3 No se pueden descargar archivos exportados

**Problema**: Al intentar descargar un archivo exportado, se produce un error.

**Soluciones**:
1. Asegúrese de que el archivo existe en el directorio `data_exports`.
2. Verifique que tiene permisos para acceder al archivo.
3. Compruebe que el navegador permite descargas desde el sitio.
4. Intente acceder directamente al archivo a través de la URL.
5. Si el problema persiste, copie el archivo a una ubicación accesible:
   ```bash
   cp data/exports/tarifas_2025-02-01_2025-02-28.xlsx /tmp/
   ```

## 8. Problemas de Base de Datos

### 8.1 Error de conexión a la base de datos

**Problema**: Se produce un error de conexión a la base de datos.

**Soluciones**:
1. Asegúrese de que el archivo de la base de datos existe y no está dañado.
2. Verifique que tiene permisos para acceder al archivo.
3. Compruebe que la ruta a la base de datos en `config.yaml` es correcta.
4. Si la base de datos está dañada, restaure una copia de seguridad:
   ```python
   from db.database import db
   
   backups = db.list_backups()
   if backups:
       db.restore_backup(backups[-1])  # Restaurar la última copia de seguridad
   ```
5. Si no hay copias de seguridad disponibles, cree una nueva base de datos:
   ```bash
   python initialize_db.py
   ```

### 8.2 Base de datos bloqueada

**Problema**: La base de datos está bloqueada y no se pueden realizar operaciones.

**Soluciones**:
1. Asegúrese de que no hay otras instancias de la aplicación en ejecución.
2. Verifique que no hay otras aplicaciones accediendo a la base de datos.
3. Reinicie la aplicación.
4. Si el problema persiste, puede ser necesario forzar el desbloqueo:
   ```bash
   # En Linux/macOS
   fuser -k db/revenue_management.db
   
   # En Windows
   taskkill /F /IM python.exe
   ```
5. Si el archivo de la base de datos está dañado, restaure una copia de seguridad.

### 8.3 Base de datos demasiado grande

**Problema**: El archivo de la base de datos es demasiado grande y afecta al rendimiento.

**Soluciones**:
1. Archive datos antiguos:
   ```sql
   -- Crear una tabla de archivo
   CREATE TABLE ARCHIVED_BOOKINGS AS SELECT * FROM RAW_BOOKINGS WHERE fecha_reserva < date('now', '-1 year');
   -- Eliminar datos archivados de la tabla principal
   DELETE FROM RAW_BOOKINGS WHERE fecha_reserva < date('now', '-1 year');
   ```
2. Optimice la base de datos:
   ```python
   from db.database import db
   
   db.execute_query("VACUUM")
   ```
3. Considere dividir la base de datos en varias bases de datos (una para datos históricos y otra para datos actuales).
4. Aumente la frecuencia de las copias de seguridad y limpiezas.

## 9. Problemas de Rendimiento

### 9.1 Aplicación lenta

**Problema**: La aplicación es lenta en general.

**Soluciones**:
1. Cierre otras aplicaciones para liberar memoria.
2. Verifique que la base de datos no es demasiado grande. Si es necesario, archive datos antiguos.
3. Optimice la base de datos ejecutando el comando `VACUUM`.
4. Reduzca la cantidad de datos que se cargan a la vez (use filtros y paginación).
5. Considere actualizar el hardware del servidor.
6. Verifique que no hay procesos en segundo plano que consuman recursos.

### 9.2 Carga de página lenta

**Problema**: Las páginas tardan mucho en cargarse.

**Soluciones**:
1. Reduzca la cantidad de datos que se muestran en la página.
2. Utilice paginación para mostrar los datos en bloques más pequeños.
3. Optimice las consultas a la base de datos.
4. Utilice caché para datos que no cambian con frecuencia.
5. Verifique que las imágenes y otros recursos están optimizados.
6. Considere utilizar un navegador más rápido.

### 9.3 Generación de informes lenta

**Problema**: La generación de informes es muy lenta.

**Soluciones**:
1. Reduzca el rango de fechas para el informe.
2. Utilice filtros para reducir la cantidad de datos a procesar.
3. Genere informes en segundo plano y notifique cuando estén listos.
4. Optimice las consultas a la base de datos.
5. Considere utilizar un formato de informe más ligero (CSV en lugar de Excel).
6. Utilice caché para informes que se generan con frecuencia.

## 10. Errores Comunes

### 10.1 "No se puede encontrar el módulo"

**Problema**: Se muestra un error "No se puede encontrar el módulo X".

**Soluciones**:
1. Asegúrese de que el módulo está instalado:
   ```bash
   pip install X
   ```
2. Verifique que está utilizando el entorno virtual correcto.
3. Compruebe que la estructura de directorios es correcta.
4. Si el módulo es parte del proyecto, asegúrese de que está en el PYTHONPATH:
   ```python
   import sys
   from pathlib import Path
   
   sys.path.insert(0, str(Path(__file__).parent))
   ```

### 10.2 "Error de sintaxis"

**Problema**: Se muestra un error de sintaxis en un archivo Python.

**Soluciones**:
1. Verifique que el código tiene la sintaxis correcta.
2. Compruebe que está utilizando la versión correcta de Python.
3. Asegúrese de que no hay caracteres especiales o invisibles en el código.
4. Utilice un editor con resaltado de sintaxis para identificar el error.
5. Si el error está en un archivo de configuración JSON o YAML, verifique que tiene el formato correcto.

### 10.3 "Error de permisos"

**Problema**: Se muestra un error de permisos al acceder a un archivo o directorio.

**Soluciones**:
1. Asegúrese de que tiene permisos para acceder al archivo o directorio.
2. Verifique que el archivo o directorio existe.
3. Compruebe que el archivo no está siendo utilizado por otra aplicación.
4. Cambie los permisos del archivo o directorio:
   ```bash
   # En Linux/macOS
   chmod 644 archivo.txt
   chmod 755 directorio
   
   # En Windows
   icacls archivo.txt /grant Usuario:F
   icacls directorio /grant Usuario:F
   ```

### 10.4 "Error de memoria"

**Problema**: Se muestra un error de memoria al procesar grandes cantidades de datos.

**Soluciones**:
1. Reduzca la cantidad de datos que se procesan a la vez.
2. Utilice procesamiento por lotes para grandes conjuntos de datos.
3. Cierre otras aplicaciones para liberar memoria.
4. Optimice el código para reducir el uso de memoria.
5. Considere actualizar la memoria RAM del servidor.
6. Utilice un enfoque de procesamiento en streaming para datos grandes.

### 10.5 "Error de timeout"

**Problema**: Se muestra un error de timeout al realizar una operación.

**Soluciones**:
1. Aumente el tiempo de timeout en la configuración:
   ```yaml
   app:
     timeout_seconds: 300  # 5 minutos
   ```
2. Divida la operación en partes más pequeñas.
3. Optimice la operación para que sea más rápida.
4. Ejecute la operación en segundo plano y notifique cuando esté lista.
5. Verifique que no hay problemas de red o de servidor que puedan causar retrasos.

## Contacto y Soporte

Si ha intentado las soluciones anteriores y el problema persiste, contacte al equipo de soporte:

- **Email**: soporte@hotelplayaclub.com
- **Teléfono**: +57 123 456 7890
- **Horario de atención**: Lunes a Viernes, 9:00 AM - 6:00 PM (GMT-5)

Al contactar al soporte, proporcione la siguiente información:
1. Descripción detallada del problema
2. Pasos para reproducir el problema
3. Capturas de pantalla o videos que muestren el problema
4. Logs relevantes (ubicados en el directorio `logs`)
5. Versión del sistema y del navegador
6. Cualquier otra información que pueda ser útil para diagnosticar el problema