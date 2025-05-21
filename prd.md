Okay, gracias por la aclaración. Mi disculpa por la interpretación errónea del término "Polar". Dada tu aclaración de que se refiere a la librería **Polars** (para manejo de dataframes) y no a un motor de reglas declarativo como Oso/Polar, necesitamos ajustar la descripción del "Motor de Reglas" y el Apéndice B.

Esto significa que la "lógica de reglas" no se implementará con un lenguaje de reglas específico como Polar de Oso, sino que se traducirá en código Python que opera sobre los DataFrames de Polars. El "Motor de Reglas" será, en esencia, una capa de código Python estructurada para aplicar estas condiciones.

Aquí tienes el PRD MVP revisado, corrigiendo esa interpretación y ajustando las secciones relevantes:

--- START OF FILE revenueprd-mvp-revised.md ---

# PRD (MVP Inicial): Framework de Revenue Management para Hotel Playa Club

## Resumen Ejecutivo (MVP)

Este Documento de Requisitos del Producto (PRD) describe el **Producto Mínimo Viable (MVP)** de un framework de revenue management personalizado para el Hotel Playa Club en Cartagena, Colombia. El sistema utilizará **Python con Polars** para crear una capa de análisis de datos, previsión y **lógica de aplicación de reglas** que operará sobre DataFrames. El objetivo del MVP es proporcionar recomendaciones de tarifas esenciales que un gerente pueda revisar y aprobar, utilizando datos exportados manualmente del PMS Zeus, para iniciar la optimización de la estrategia de precios y mejorar el RevPAR y la ocupación. **Funcionalidades avanzadas como simulaciones, análisis de elasticidad o integraciones automáticas quedan fuera del alcance de este MVP.** El "motor de reglas" se implementará como código Python estructurado aplicando condiciones a los datos de Polars, no como un motor de reglas declarativo aparte.

## Contexto del Negocio

(Se mantiene igual que en el PRD completo)

El Hotel Playa Club es un establecimiento ubicado en Cartagena, Colombia, con 79 habitaciones de diferentes categorías. Actualmente, las tarifas se establecen mediante un análisis manual, verificando forecasts históricos y definiendo precios por canal. El hotel busca implementar un sistema más eficiente para la definición de tarifas que maximice los ingresos y la ocupación.

### Perfil del Hotel:
- **Ubicación**: Cartagena, Colombia
- **Habitaciones**: 79 en total
  - 14 estándar triple (capacidad 3 personas)
  - 4 junior suites (capacidad 5 personas)
  - 26 estándar cuádruples (capacidad 4 personas)
  - 7 habitaciones estándar dobles (capacidad 2 personas)
  - 1 habitación suite (capacidad 2 personas)
  - 12 habitaciones king superior (capacidad 2 personas)
  - 15 habitaciones dobles superior (capacidad 2 personas)

### Segmentos de Mercado:
- Turístico (principal)
- Familiar (principal)
- Parejas (principal)
- Grupos (minoritario)
- Corporativo (minoritario)

### Estacionalidad:
- **Temporada Alta**: Diciembre, enero, finales de junio, julio, agosto
- **Temporada Media**: Febrero, marzo, septiembre, octubre
- **Temporada Baja**: Abril, mayo, principios de junio, noviembre

### Sistema Actual:
- Zeus PMS (versión 14.1.0)
- Sin API o conexión externa directa (excepto al channel manager vía Apache ActiveMQ)
- Definición manual de tarifas
- Datos históricos disponibles en formato Excel

## Objetivos del Producto (MVP)

1.  **Principal**: Crear el núcleo de un framework para el análisis y definición de tarifas hoteleras que inicie la optimización del revenue management.
2.  **Específicos (MVP)**:
    *   Proporcionar una base para mejorar el RevPAR y la ocupación del hotel mediante recomendaciones de tarifas basadas en datos y reglas simples aplicadas en código.
    *   Generar recomendaciones de tarifas iniciales para los principales canales de venta.
    *   Permitir la definición y aplicación de reglas de pricing básicas a través de la lógica del sistema.
    *   Permitir la medición inicial del rendimiento con KPIs clave.

## Usuarios y Partes Interesadas

(Se mantiene igual que en el PRD completo)

### Usuarios Primarios:
- Revenue Manager / Gerente del hotel

### Usuarios Secundarios:
- Personal de ventas y reservas (como consumidores de las tarifas definidas)
- Administración del hotel

### Partes Interesadas:
- Dirección del hotel
- Departamento financiero

## Requisitos Funcionales (MVP)

### 1. Ingesta y Gestión de Datos (MVP)
- **1.1** El sistema deberá importar datos desde archivos Excel exportados del PMS Zeus.
- **1.2** El sistema deberá limpiar, normalizar y cargar los datos en DataFrames de **Polars** para su procesamiento y análisis. Los datos persistirán en una base de datos local (SQLite).
- **1.3** El sistema deberá procesar información histórica esencial para el MVP: Ocupación por tipo de habitación, Tarifas por canal y temporada, Patrones de reserva, Ingresos básicos. (Cancelaciones, y otros datos detallados pueden ser futuros).
- **1.4** El sistema deberá permitir la actualización de la base de datos local manualmente mediante nuevas importaciones de archivos Excel.
- **1.5** El sistema deberá manejar datos históricos de al menos 1-2 años para el análisis inicial del MVP.

### 2. Análisis de Datos (MVP)
- **2.1** El sistema deberá utilizar **Polars** para calcular los siguientes KPIs esenciales: RevPAR, ADR, Ocupación. (TRevPAR, GOPPAR, RevPAG pueden ser futuros si requieren datos complejos adicionales).
- **2.2** El sistema deberá utilizar **Polars** para analizar patrones históricos básicos de ocupación por: Tipo de habitación, Temporada, Día de la semana. (Análisis por canal o patrones más complejos pueden ser futuros).
- **2.3** El sistema deberá permitir comparaciones año contra año (YoY) para los KPIs esenciales utilizando **Polars**.
- **2.4** El sistema deberá visualizar los datos y KPIs clave en un dashboard básico.

### 3. Previsión de Demanda (MVP)
- **3.1** El sistema deberá generar pronósticos de ocupación básicos para fechas futuras utilizando un modelo inicial simple (Ej: Prophet), operando sobre datos preparados con **Polars**.
- **3.2** El sistema deberá considerar factores estacionales básicos en las previsiones.
- **3.3** El sistema deberá segmentar las previsiones por tipo de habitación.
- **3.4** El sistema deberá permitir ajustes manuales a las previsiones generadas a través de la UI.

### 4. Lógica de Aplicación de Reglas para Pricing (MVP)
- **4.1** El sistema deberá implementar la lógica de aplicación de reglas de precios utilizando código Python que opera directamente sobre los DataFrames de **Polars** que contienen los datos históricos, previsiones y tarifas base.
- **4.2** El sistema deberá aplicar reglas de precios básicas basadas en: Temporada, Tipo de habitación, Canal de distribución (principales como OTAs, Venta Directa), Ocupación prevista. (Días de antelación, duración de estancia, etc., pueden ser futuros).
- **4.3** El sistema permitirá modificar los parámetros de las reglas básicas (ej: umbrales de ocupación, factores de ajuste) a través de la UI o un archivo de configuración simple. La creación de *nuevos tipos* de reglas complejos o lógica condicional sofisticada requerirá cambios en el código Python.
- **4.4** El sistema deberá utilizar tarifas base definidas (en la UI o configuración) por temporada y tipo de habitación como punto de partida.
- **4.5** El sistema deberá aplicar ajustes porcentuales o absolutos sobre la tarifa base según las reglas definidas en el código/configuración.

### 5. Recomendación de Tarifas (MVP)
- **5.1** El sistema deberá generar **una única** recomendación de tarifas aplicando la lógica de reglas del MVP a los datos procesados por **Polars** y las previsiones.
- **5.2** El sistema deberá proporcionar esta recomendación segmentada por: Canal de distribución (principales), Tipo de habitación, Fechas específicas.
- **5.3** El sistema deberá presentar la recomendación de forma clara en la UI para que el usuario la revise. (Múltiples escenarios o simulaciones son funcionalidades futuras).

### 6. Gestión de Tarifas (MVP)
- **6.1** El sistema deberá permitir la revisión y aprobación de la recomendación de tarifas generada en la UI.
- **6.2** El sistema deberá permitir la modificación manual de las tarifas recomendadas antes de aprobarlas.
- **6.3** El sistema deberá exportar las tarifas aprobadas en un formato de archivo (ej. Excel) compatible con el proceso de importación manual de Zeus. **(CRÍTICO para la utilidad del MVP)**
- **6.4** El sistema deberá mantener un registro básico de las sets de tarifas aprobadas y exportadas. (Historial detallado de cambios individuales es futuro).

### 7. Visualización y Reporting (MVP)
- **7.1** El sistema deberá proporcionar un dashboard visual básico (Streamlit/Plotly) para monitorear los KPIs esenciales (RevPAR, ADR, Ocupación) y visualizar tendencias históricas básicas, utilizando datos procesados por **Polars**.
- **7.2** El sistema deberá mostrar los resultados del análisis y la previsión de forma clara en la UI.
- **7.3** El sistema deberá visualizar las recomendaciones de tarifas generadas.
- **7.4** (Exportación de informes o visualizaciones avanzadas son funcionalidades futuras).

## Requisitos No Funcionales (MVP)

(Se mantienen en gran medida, aplicados al alcance del MVP)

### 1. Rendimiento
- **1.1** El sistema deberá cargar el dashboard principal (con datos del MVP) en menos de 5 segundos. **Polars** deberá ser eficiente en el procesamiento de datos para lograr esto.
- **1.2** El sistema deberá procesar archivos de datos (con el volumen del MVP) utilizando **Polars** en menos de 30 segundos.
- **1.3** La generación de recomendaciones de tarifas (aplicando la lógica de reglas sobre DataFrames de **Polars**) deberá completarse en menos de 1 minuto.

### 2. Usabilidad
- **2.1** La interfaz del MVP deberá ser intuitiva y requerir mínima capacitación para las funcionalidades incluidas.
- **2.2** Las visualizaciones del MVP deberán ser comprensibles para usuarios no técnicos.
- **2.3** El sistema deberá proporcionar ayuda contextual y tooltips para las funcionalidades del MVP.

### 3. Escalabilidad
- **3.1** El sistema deberá manejar los datos históricos necesarios para el MVP (aprox. 1-2 años inicialmente). La arquitectura de datos (SQLite + Polars) debe permitir procesar volúmenes mayores en el futuro.
- **3.2** El diseño del MVP deberá permitir futuras extensiones para incluir más tipos de datos y funcionalidades sin reestructuraciones mayores.

### 4. Seguridad
- **4.1** El sistema deberá requerir autenticación básica para acceder.
- **4.2** El sistema deberá mantener un registro básico de las operaciones clave (ingesta, aprobación de tarifas).
- **4.3** Los datos sensibles (en el alcance del MVP) deberán estar protegidos.

### 5. Mantenibilidad
- **5.1** El código Python del MVP, incluida la lógica de reglas, deberá estar bien documentado.
- **5.2** El sistema deberá utilizar una estructura modular básica que facilite la expansión.
- **5.3** Se incluirán pruebas automatizadas para los componentes críticos del MVP.

### 6. Disponibilidad
- **6.1** El sistema deberá funcionar en un entorno local sin dependencia de Internet.
- **6.2** El sistema deberá realizar copias de seguridad automáticas básicas de la base de datos local.

## Arquitectura Técnica (MVP)

(Se mantiene el stack tecnológico, ajustando la descripción del "Motor de Reglas")

### Componentes del Sistema (MVP)
1.  **Base de datos**: SQLite (local) - Estructura diseñada para crecimiento futuro.
2.  **Backend**: Python con **Polars** para el procesamiento eficiente de DataFrames.
3.  **Lógica de Reglas**: Código Python estructurado que aplica condiciones y cálculos sobre DataFrames de **Polars**.
4.  **Forecasting**: Implementación básica de un modelo simple (Ej: Prophet/StatsModels), integrando con **Polars**.
5.  **Frontend**: Streamlit para la interfaz de usuario del MVP.
6.  **Visualización**: Plotly/Matplotlib para visualizar datos y resultados básicos.

### Diagrama de Componentes (Se mantiene igual, pero el texto del componente central cambia)
```
+------------------+        +------------------+        +--------------------+
|                  |        |                  |        |                    |
|  Ingesta de      |------->|  Base de Datos   |<-------|  Análisis con      |
|  Datos (Excel)   |        |  (SQLite)        |        |  Polars (KPIs, Pat)|
|                  |        |                  |        |                    |
+------------------+        +------------------+        +--------------------+
                                    ^                             |
                                    |                             v
+------------------+        +----------------------+      +------------------+
|                  |        |                      |      |                  |
|  Interfaz de     |<-------|  Lógica de Reglas    |<-----|  Modelo de       |
|  Usuario (MVP)   |        |  (Python + Polars)   |      |  Previsión (MVP) |
|  (Streamlit)     |        |                      |      |                  |
+------------------+        +----------------------+      +------------------+
       |
       v
+------------------+
|                  |
|  Exportación     |
|  de Tarifas (MVP)|
|  (Excel p/ Zeus) |
|                  |
+------------------+
```

## Integraciones (MVP)

### Integraciones Iniciales (Manuales - Alcance MVP)
- **Zeus PMS**: Exportación e importación manual vía archivos Excel.
- **Channel Manager**: Actualización manual de tarifas en base a las recomendaciones aprobadas.

### Integraciones Futuras (Potenciales - Fuera del Alcance del MVP)
- APIs de OTAs, Integración directa con Zeus, Conexión automatizada con Channel Manager.

## Casos de Uso Principales (MVP)

### 1. Análisis de Datos Históricos Básicos (MVP)
**Actor**: Revenue Manager
**Descripción**: El usuario desea analizar el rendimiento histórico esencial del hotel.
1. El usuario exporta datos de Zeus PMS a Excel.
2. El usuario importa los datos al sistema MVP.
3. El sistema utiliza **Polars** para procesar y normalizar los datos esenciales.
4. El sistema calcula KPIs esenciales y genera visualizaciones básicas utilizando **Polars**.
5. El usuario explora los datos y KPIs clave a través del dashboard MVP.

### 2. Generación de una Recomendación de Tarifas (MVP)
**Actor**: Revenue Manager
**Descripción**: El usuario necesita obtener una recomendación de tarifas para fechas futuras.
1. El usuario selecciona el rango de fechas para el análisis.
2. El sistema genera previsiones de demanda básicas.
3. El sistema aplica la lógica de reglas básicas (Python+Polars) sobre los datos y previsiones.
4. El sistema muestra **una única** recomendación de tarifas por tipo de habitación y canal principal.

### 3. Ajuste y Aprobación de Tarifas Recomendadas (MVP)
**Actor**: Revenue Manager
**Descripción**: El usuario revisa, ajusta y aprueba la recomendación de tarifas.
1. El usuario revisa la recomendación de tarifas presentada en la UI.
2. El usuario realiza ajustes manuales donde sea necesario en la recomendación.
3. El usuario aprueba las tarifas finales.
4. El sistema guarda las tarifas aprobadas en un registro básico.
5. El usuario exporta las tarifas aprobadas en formato Excel para implementación manual en Zeus y channel manager.

## Fases de Implementación (MVP)

(Se ajustan las fases para reflejar el alcance del MVP y el uso de Polars)

### Fase 1: Desarrollo Base, Datos y Análisis (Entrega en X semanas)
- Setup del entorno de desarrollo.
- Estructura de la base de datos SQLite (diseñada para crecimiento futuro).
- Implementación del módulo de ingesta de datos (Excel -> SQLite -> Polars DataFrames).
- Desarrollo del módulo básico de análisis con **Polars** (cálculo de KPIs esenciales, análisis de patrones básicos).
- Creación de dashboard inicial con KPIs principales y visualización histórica básica usando **Polars** y Plotly/Matplotlib.

### Fase 2: Previsión y Lógica de Reglas Básica (Entrega en Y semanas)
- Implementación de un modelo de previsión de demanda simple (Ej: Prophet), integrando con **Polars**.
- Desarrollo de la lógica de aplicación de reglas básica en código Python que opera sobre DataFrames de **Polars**.
- Implementación de la interfaz/configuración para ajustar los parámetros de las reglas básicas.
- Integración entre módulos de análisis, previsión y lógica de reglas para generar la recomendación única.

### Fase 3: Recomendación, UI y Exportación (Entrega en Z semanas)
- Desarrollo del generador de la recomendación de tarifas única (utilizando la lógica de reglas).
- Desarrollo de la interfaz completa en Streamlit para la revisión, ajuste y aprobación de la recomendación MVP.
- Implementación de la funcionalidad de exportación de tarifas aprobadas en formato compatible con Zeus.
- Implementación del registro básico de tarifas aprobadas.
- Pruebas iniciales con datos reales y ajuste de funcionalidades MVP según feedback.

### Fase 4: Refinamiento y Entrega del MVP (Entrega en W semanas)
- Optimización de rendimiento del MVP, especialmente en el procesamiento con **Polars**.
- Ajustes finales según feedback de los usuarios clave.
- Documentación básica del MVP y capacitación para el uso de las funcionalidades incluidas.
- Entrega del sistema MVP.

*(Nota: Los tiempos (X, Y, Z, W) deben ser estimados por el equipo de desarrollo.)*

## Métricas de Éxito (MVP)

(Se mantienen las métricas de negocio como objetivos a largo plazo, y se ajustan las técnicas al MVP)

### Métricas de Negocio (Impacto esperado del MVP en adelante)
- Aumento gradual del RevPAR.
- Incremento gradual de la ocupación en temporada baja.
- Reducción del tiempo dedicado a la definición de tarifas (una vez que el proceso con el MVP esté fluido).
- Mejora inicial en la precisión de las previsiones (validación de si el modelo simple es suficiente).

### Métricas Técnicas (Para el MVP)
- Tiempo de procesamiento de datos (volumen MVP) utilizando **Polars** menor a 30 segundos.
- Precisión inicial de las previsiones de demanda (medida de forma básica) para el período analizado por el MVP.
- Tasa de adopción del sistema MVP por el Revenue Manager del 100%.
- Disponibilidad del sistema MVP superior al 99%.
- Usabilidad percibida del sistema MVP (medida cualitativamente por feedback).

## Riesgos y Mitigaciones (MVP)

(Los riesgos principales siguen siendo relevantes)

| Riesgo | Impacto | Probabilidad | Mitigación |
|--------|---------|--------------|------------|
| Calidad insuficiente de datos históricos (MVP) | Alto | Media | Implementar procesos de limpieza y validación de datos esenciales en la ingesta del MVP, usando **Polars** para la validación de estructura/tipos. |
| Baja adopción por parte del Revenue Manager | Alto | Baja | Diseñar interfaz intuitiva para las funcionalidades MVP y proporcionar capacitación enfocada. |
| Dificultad para la exportación/importación manual con Zeus | Medio | Alta | Investigar a fondo el formato requerido por Zeus para la importación de tarifas antes de la implementación. |
| Precisión insuficiente en las previsiones básicas del MVP | Medio | Media | Permitir ajustes manuales en la UI del MVP; validar resultados y planificar mejora del modelo en futuras versiones. |
| Complejidad inesperada en la lógica de reglas al implementarla en código Python | Medio | Media | Mantener las reglas del MVP lo más simples posible; usar patrones de código limpios y modulares para la lógica de reglas. |

## Requisitos de Infraestructura (MVP)

(Se mantienen igual que en el PRD completo)

### Hardware
- PC/Laptop con Windows 10 o superior
- Mínimo 8 GB de RAM
- 100 GB de espacio en disco

### Software
- Python 3.9 o superior
- Librerías: **Polars**, Prophet (o similar simple), Streamlit, Plotly/Matplotlib, SQLite
- Acceso a Microsoft Excel

## Glosario de Términos

(Ajustado para reflejar el uso de Polars como dataframe library)

- **Polars**: Librería de Python de alto rendimiento para manejo y procesamiento de DataFrames.
- **RevPAR**: Revenue Per Available Room
- **ADR**: Average Daily Rate
- **TRevPAR**: Total Revenue Per Available Room (Potencial futuro en análisis detallado)
- **GOPPAR**: Gross Operating Profit Per Available Room (Potencial futuro en análisis detallado)
- **RevPAG**: Revenue Per Available Guest (Potencial futuro en análisis detallado)
- **OTA**: Online Travel Agency
- **PMS**: Property Management System
- **Forecast**: Previsión de demanda u ocupación
- **Channel Manager**: Software para gestionar la distribución de tarifas en múltiples canales
- **MVP**: Minimum Viable Product

## Apéndices

### Apéndice A: Estructura de Datos (MVP - Diseño para Futuro Crecimiento)
- Tabla de Habitaciones
- Tabla de Reservas (Datos esenciales para MVP)
- Tabla de Tarifas (Histórico y Recomendado/Aprobado)
- Configuración de Reglas (Estructura simple para parámetros de reglas)
- Tabla de Previsiones (Previsiones básicas del MVP)
- Tabla de Recomendaciones (Recomendación única del MVP)

### Apéndice B: Ejemplo de Lógica de Reglas en Código Python con Polars (MVP)
(Este apéndice reemplaza el ejemplo en sintaxis Polar/Oso y muestra cómo se implementaría la lógica básica usando Polars)

```python
import polars as pl

# Supongamos que tenemos un DataFrame de Polars 'df_tarifas_base'
# con columnas: 'fecha', 'tipo_habitacion', 'canal', 'tarifa_base', 'ocupacion_prevista', 'temporada'

def aplicar_reglas_pricing_mvp(df: pl.DataFrame) -> pl.DataFrame:
    """
    Aplica la lógica de reglas básica de pricing a un DataFrame de Polars.
    Retorna un DataFrame con las tarifas recomendadas.
    """

    # Empezar con la tarifa base
    df = df.with_columns(pl.col('tarifa_base').alias('tarifa_recomendada'))

    # ----- Ejemplo de reglas de ajuste por ocupación y temporada -----

    # Regla 1: Aumentar tarifa en temporada alta si la ocupación prevista es alta (>80%) para OTAs
    df = df.with_columns(
        pl.when(
            (pl.col('temporada') == 'alta') &
            (pl.col('ocupacion_prevista') > 0.8) &
            (pl.col('canal') == 'ota')
        )
        .then(pl.col('tarifa_recomendada') * 1.15) # Aumento del 15%
        .otherwise(pl.col('tarifa_recomendada'))
        .alias('tarifa_recomendada')
    )

    # Regla 2: Disminuir tarifa en temporada baja si la ocupación prevista es baja (<40%) para cualquier canal dinámico
    df = df.with_columns(
         pl.when(
            (pl.col('temporada') == 'baja') &
            (pl.col('ocupacion_prevista') < 0.4) &
            (pl.col('canal').is_in(['ota', 'directo'])) # Aplicar a canales dinámicos del MVP
        )
        .then(pl.col('tarifa_recomendada') * 0.90) # Reducción del 10%
        .otherwise(pl.col('tarifa_recomendada'))
        .alias('tarifa_recomendada')
    )

    # --- Otras reglas básicas (ejemplo: ajuste por tipo de habitación/canal específico) ---

    # Regla 3: Ajuste para Junior Suite en venta directa durante temporada media (ejemplo: tarifa fija o ajuste)
    # Esto podría ser un override o un ajuste adicional
    df = df.with_columns(
         pl.when(
            (pl.col('tipo_habitacion') == 'junior_suite') &
            (pl.col('canal') == 'directo') &
            (pl.col('temporada') == 'media')
         )
         # .then(pl.lit(250.0)) # Ejemplo: Establecer tarifa fija en $250
         .then(pl.col('tarifa_recomendada') + 20.0) # Ejemplo: Ajuste absoluto de +$20
         .otherwise(pl.col('tarifa_recomendada'))
         .alias('tarifa_recomendada')
    )


    # Nota: La prioridad de las reglas se maneja por el orden de aplicación en el código.
    # Reglas más específicas o overrides deben aplicarse *después* de reglas generales.

    return df[['fecha', 'tipo_habitacion', 'canal', 'tarifa_recomendada']]

# Ejemplo de uso (esto no iría en el apéndice, solo para ilustrar):
# datos_para_pricing = preparar_dataframe_con_polars(...) # Incluye base, forecast, temporada, canal
# recomendaciones_df = aplicar_reglas_pricing_mvp(datos_para_pricing)
# print(recomendaciones_df)
```
*(Nota: Este ejemplo es simplificado. Una implementación real requeriría una estructura más robusta para cargar y aplicar reglas definidas externamente, pero el núcleo de aplicar la lógica usando `pl.when` y `pl.with_columns` en Polars sería el mismo.)*

### Apéndice C: Mockups de UI (MVP)
[Los mockups detallados se desarrollarán en la Fase 1 del proyecto y reflejarán la interfaz simplificada del MVP para visualización de datos, previsiones, configuración de parámetros de reglas básicas y gestión de la recomendación única.]

## Historial de Revisiones

| Versión | Fecha | Autor | Descripción |
|---------|-------|-------|-------------|
| 1.0 | 21/05/2025 | Claude | Versión inicial del PRD completo |
| 1.1 (MVP) | 24/05/2025 | Claude (Revisado) | Adaptación del PRD a un Producto Mínimo Viable (MVP), reduciendo el alcance funcional y ajustando secciones para enfocar en la primera entrega de valor. |
| **1.2 (MVP Revisado)** | **27/05/2025** | **Claude (Revisado)** | **Revisión para clarificar el uso de Polars exclusivamente como librería de DataFrames y la implementación de la lógica de reglas directamente en código Python operando sobre Polars DataFrames. Se actualiza el Apéndice B con un ejemplo de código Polars.** |

## Funcionalidades Futuras Potenciales (Fuera del Alcance del MVP)

(Se mantiene igual, ya que estas funcionalidades se posponen intencionalmente)

Esta sección lista algunas de las funcionalidades mencionadas en el PRD completo que intencionadamente se excluyen del MVP para enfocar los esfuerzos iniciales:

*   Análisis de elasticidad de la demanda.
*   Gestión compleja de tarifas negociadas y contratos fijos.
*   Análisis detallado de datos como cancelaciones, no-shows, RevPAG, TRevPAR, GOPPAR.
*   Identificación automática de tendencias y anomalías.
*   Generación de múltiples escenarios de pricing.
*   Simulaciones "what-if" interactivas.
*   Historial de cambios detallado de tarifas individuales.
*   Reporting avanzado y exportación de informes complejos.
*   Visualizaciones detalladas de previsiones vs. resultados reales.
*   Integraciones automáticas vía API con Zeus, OTAs, Channel Manager.
*   Consideración de eventos externos en la previsión (más allá de la estacionalidad básica).
*   Modelos de previsión más sofisticados (ML).
*   Reglas de pricing basadas en factores como Length of Stay (LOS), Booking Window, tipo de huésped (si los datos lo permiten), implementadas en una UI avanzada o con un motor de reglas dedicado.

--- END OF FILE revenueprd-mvp-revised.md ---

Con esta versión revisada, el PRD MVP es más preciso respecto a la tecnología que se utilizará para implementar la lógica de reglas (código Python con Polars) y el alcance del MVP. El Apéndice B ahora muestra un ejemplo de cómo se vería esa lógica en código, lo cual es muy útil para el equipo de desarrollo.