BASIC_ESTIMATION_EXAMPLES = [
    {
        "meeting_summary": "El cliente necesita una plataforma web de gestión de inventario...",
        "estimation": """
        ## Estimación: Plataforma de Gestión de Inventario

        ### Desglose de tareas:
        1. Diseño UI/UX: 40 horas
        2. Backend API (CRUD inventario): 60 horas
        3. Autenticación y roles: 20 horas
        4. Dashboard con métricas: 30 horas
        5. Testing y QA: 25 horas

        **Total estimado: 175 horas**
        **Equipo recomendado: 2 desarrolladores full-stack + 1 diseñador UX (part-time)**
        **Duración estimada: 6-8 semanas**
        """,
    },
    {
        "meeting_summary": "El cliente necesita implementar testing unitario e integración para un proyecto básico de gestión de passwords. El sistema incluye registro de usuarios, autenticación, cambio de contraseña, recuperación y políticas de seguridad (longitud mínima, complejidad, expiración). Se utiliza Python con FastAPI, base de datos PostgreSQL y hashing con bcrypt.",
        "estimation": """
        ## Estimación: Testing Unitario e Integración - Gestión de Passwords

        ### Desglose de tareas:

        #### Testing Unitario
        1. Tests de validación de políticas de password (longitud, complejidad, caracteres especiales): 12 horas
        2. Tests de hashing y verificación de passwords (bcrypt): 8 horas
        3. Tests de generación de tokens de recuperación: 6 horas
        4. Tests de expiración y rotación de passwords: 8 horas
        5. Tests de servicios de usuario (registro, actualización): 10 horas
        6. Tests de casos edge (inputs vacíos, inyección SQL, caracteres Unicode): 8 horas

        #### Testing de Integración
        7. Tests de flujo completo de registro con password: 10 horas
        8. Tests de flujo de autenticación (login/logout): 8 horas
        9. Tests de flujo de cambio de password: 6 horas
        10. Tests de flujo de recuperación de password (token + reset): 10 horas
        11. Tests de integración con base de datos (persistencia, constraints): 8 horas
        12. Tests de endpoints API (validaciones HTTP, códigos de respuesta): 10 horas

        #### Infraestructura y configuración
        13. Configuración de pytest, fixtures y factories: 6 horas
        14. Configuración de base de datos de test (contenedor Docker): 4 horas
        15. Configuración de cobertura de código y reportes: 4 horas

        **Total estimado: 118 horas**
        **Equipo recomendado: 1 QA engineer + 1 desarrollador backend**
        **Duración estimada: 4-5 semanas**
        **Cobertura objetivo: ≥ 85%**
        """,
    },
    {
        "meeting_summary": "El cliente necesita migrar una base de datos básica de SQL Server a MySQL. La base de datos contiene aproximadamente 30 tablas con relaciones, stored procedures, vistas, triggers e índices. El volumen de datos es de unos 5 GB. Se requiere mantener la integridad referencial, minimizar el tiempo de inactividad y validar que los datos migrados sean correctos.",
        "estimation": """
        ## Estimación: Migración de Base de Datos SQL Server a MySQL

        ### Desglose de tareas:

        #### Análisis y planificación
        1. Inventario de objetos de BD (tablas, vistas, stored procedures, triggers, índices): 8 horas
        2. Análisis de incompatibilidades de tipos de datos entre SQL Server y MySQL: 6 horas
        3. Identificación de funciones T-SQL sin equivalente directo en MySQL: 8 horas
        4. Diseño del plan de migración y estrategia de rollback: 6 horas

        #### Migración de esquema
        5. Conversión de DDL (tablas, constraints, claves foráneas): 12 horas
        6. Adaptación de vistas al dialecto MySQL: 8 horas
        7. Reescritura de stored procedures (T-SQL a MySQL): 16 horas
        8. Conversión de triggers: 6 horas
        9. Recreación de índices y optimización: 6 horas

        #### Migración de datos
        10. Configuración de herramienta de migración (MySQL Workbench Migration Wizard): 4 horas
        11. Extracción, transformación y carga de datos (ETL): 12 horas
        12. Tratamiento de colaciones y codificación de caracteres (UTF-8): 4 horas
        13. Migración de datos binarios y campos especiales (XML, JSON): 6 horas

        #### Validación y testing
        14. Validación de integridad referencial post-migración: 8 horas
        15. Comparación de recuentos y checksums entre origen y destino: 6 horas
        16. Tests funcionales de consultas críticas del negocio: 10 horas
        17. Tests de rendimiento comparativo (queries principales): 8 horas

        #### Puesta en producción
        18. Ensayo de migración en entorno de staging: 8 horas
        19. Documentación del proceso y runbook de migración: 6 horas
        20. Ejecución de migración final y verificación en producción: 6 horas

        **Total estimado: 158 horas**
        **Equipo recomendado: 1 DBA senior + 1 desarrollador backend**
        **Duración estimada: 5-7 semanas**
        **Tiempo de inactividad estimado: 2-4 horas (ventana de migración final)**
        """,
    },
]

