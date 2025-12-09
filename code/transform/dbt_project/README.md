# 🔄 Car Sales dbt Project

Proyecto dbt para transformación de datos de ventas de automóviles en Snowflake con arquitectura medallion.

## 🏗️ Arquitectura

```
RAW (Bronze) → STAGING (Silver) → INTERMEDIATE (Silver) → MARTS (Gold)
```

### Flujo de Datos

```
source: CAR_SALES (RAW)
    ↓
stg_car_sales (STAGING)
    ↓
int_sales_prep (INTERMEDIATE)
    ↓
├── dim_cars (MARTS)
├── dim_salespeople (MARTS)
├── fct_car_sales (MARTS)
└── obt_car_sales (MARTS)
```

## 📁 Estructura

```
models/
├── A_Sources/
│   └── source.yml              # Definición de fuentes
├── B_Staging/
│   ├── stg_car_sales.sql       # Limpieza y tipado
│   └── schema.yml              # Tests y docs
├── C_Intermediate/
│   ├── int_sales_prep.sql      # Generación de claves
│   └── schema.yml
└── D_Marts/
    ├── dim_cars.sql            # Dimensión de autos
    ├── dim_salespeople.sql     # Dimensión de vendedores
    ├── fct_car_sales.sql       # Tabla de hechos (incremental)
    ├── obt_car_sales.sql       # One Big Table
    └── schema.yml
```

## 🎯 Modelos

### B_Staging

**stg_car_sales.sql**
- **Materialización**: View
- **Schema**: STAGING
- **Propósito**: Limpieza y estandarización de datos crudos
- **Transformaciones**: 
  - Parsing de fechas con múltiples formatos
  - Conversión de tipos numéricos
  - Limpieza de espacios en strings
  - Filtrado de registros sin fecha

**Columnas de salida**:
```
sale_date, sales_person, customer_name, car_make, car_model, 
car_year, sale_price, comm_rate, comm_earned, loaded_at, source_file
```

### C_Intermediate

**int_sales_prep.sql**
- **Materialización**: View
- **Schema**: INTERMEDIATE
- **Propósito**: Generación de claves surrogate para dimensiones y hechos
- **Transformaciones**: 
  - `sale_id`: Clave única de venta (hash de fecha, cliente, precio, vendedor)
  - `sales_person_id`: Clave de dimensión de vendedor
  - `car_id`: Clave de dimensión de auto (hash de marca, modelo, año)

### D_Marts

**dim_cars.sql**
- **Materialización**: Table
- **Tipo**: Dimensión SCD Type 1
- **Columnas**: `car_id`, `car_make`, `car_model`, `car_year`
- **Propósito**: Catálogo único de automóviles

**dim_salespeople.sql**
- **Materialización**: Table
- **Tipo**: Dimensión SCD Type 1
- **Columnas**: `sales_person_id`, `sales_person`
- **Propósito**: Catálogo de vendedores

**fct_car_sales.sql**
- **Materialización**: Incremental (unique_key: `sale_id`)
- **Tipo**: Tabla de hechos
- **Columnas**: 
  - Claves: `sale_id`, `sales_person_id`, `car_id`
  - Métricas: `sale_price`, `comm_rate`, `comm_earned`
  - Dimensiones: `sale_date`, `customer_name`, `loaded_at`
- **Estrategia incremental**: Carga solo registros con `loaded_at` mayor al máximo existente

**obt_car_sales.sql**
- **Materialización**: Table
- **Tipo**: One Big Table desnormalizada
- **Columnas**: 
  - De hechos: `sale_id`, `sale_date`, `customer_name`, `sale_price`, `comm_rate`, `comm_earned`
  - De dim_cars: `car_make`, `car_model`, `car_year`
  - De dim_salespeople: `sales_person_name`
- **Propósito**: Tabla optimizada para dashboards y consultas ad-hoc

## 🚀 Comandos

### Recomendación: Power User for dbt

Para una mejor experiencia de desarrollo, se recomienda instalar la extensión [Power User for dbt](https://marketplace.visualstudio.com/items?itemName=innoverio.vscode-dbt-power-user) en VS Code. Proporciona:
- Ejecución de modelos con un click
- Visualización de lineage interactivo
- Autocompletado inteligente
- Preview de resultados
- Navegación entre modelos

### Setup

```bash
# Instalar dependencias
dbt deps

# Verificar conexión
dbt debug --profiles-dir .
```

### Ejecución

```bash
# Ejecutar todo (run + test)
dbt build --profiles-dir .

# Solo ejecutar modelos
dbt run --profiles-dir .

# Solo tests
dbt test --profiles-dir .

# Ejecutar modelo específico
dbt run --select stg_car_sales --profiles-dir .

# Ejecutar una capa completa
dbt run --select B_Staging.* --profiles-dir .

# Modelo y sus dependencias
dbt run --select +fct_car_sales --profiles-dir .

# Full refresh de modelo incremental
dbt run --select fct_car_sales --full-refresh --profiles-dir .
```

### Documentación

```bash
# Generar y servir documentación
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

## ⚙️ Configuración

### Variables de Entorno

```env
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=CAR_SALES_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

### Materializaciones

```yaml
models:
  car_sales_project:
    B_Staging:
      +materialized: view
      +schema: staging
    C_Intermediate:
      +materialized: view
      +schema: intermediate
    D_Marts:
      +schema: marts
```

**Nota**: Los modelos en `D_Marts` tienen materializaciones configuradas individualmente en cada archivo:
- `dim_cars`, `dim_salespeople`, `obt_car_sales`: Table
- `fct_car_sales`: Incremental

## 🧪 Tests de Calidad

Tests configurados en `schema.yml`:

- **unique**: Claves primarias (`sale_id`, `car_id`, `sales_person_id`)
- **not_null**: Columnas críticas
- **accepted_values**: Valores permitidos
- **relationships**: Integridad referencial entre hechos y dimensiones

## 🔍 Troubleshooting

### Error de conexión

```bash
# Verificar variables de entorno
echo $SNOWFLAKE_ACCOUNT

# Probar conexión
dbt debug --profiles-dir .
```

### Modelo falla

```bash
# Ver logs detallados
dbt run --select modelo_con_error --profiles-dir . --log-level debug

# Ver SQL compilado
dbt compile --select modelo_con_error --profiles-dir .
cat target/compiled/car_sales_project/models/.../modelo_con_error.sql
```

### Tests fallan

```bash
# Ejecutar test específico
dbt test --select stg_car_sales --profiles-dir .

# Guardar resultados de tests fallidos
dbt test --store-failures --profiles-dir .
```

### Modelo incremental no carga datos nuevos

```bash
# Hacer full refresh
dbt run --select fct_car_sales --full-refresh --profiles-dir .
```

## 📚 Recursos

- [dbt Documentation](https://docs.getdbt.com/)
