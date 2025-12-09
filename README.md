# 🚗 Car Sales Data Pipeline

Pipeline incremental de datos de ventas de automóviles con Airflow, Snowflake, dbt y Streamlit.

## 📋 Descripción

Pipeline end-to-end que extrae datos mensuales de ventas desde CSVs, los carga en Snowflake, los transforma con dbt usando arquitectura medallion, y los visualiza en un dashboard interactivo.

## 🛠️ Stack Tecnológico

- **Orquestación**: Apache Airflow 2.10.3
- **Data Warehouse**: Snowflake
- **Transformación**: dbt 1.10.15
- **Visualización**: Streamlit + Plotly + Polars
- **Containerización**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## 🏗️ Arquitectura

```
data_lake (CSV files)
    ↓
Apache Airflow (Orchestration)
    ↓
Snowflake Data Warehouse
    ├── RAW (Landing Zone)
    ├── STAGING (Cleaned Data)
    ├── INTERMEDIATE (Business Logic)
    └── MARTS (Analytics-Ready)
    ↓
Streamlit Dashboard
```

## 🚀 Quick Start

### Prerrequisitos

- Docker y Docker Compose
- Cuenta de Snowflake con credenciales

### Configuración

1. **Clonar el repositorio**

```bash
git clone https://github.com/NavierCracco/car-sales-data-pipeline.git
cd car-sales-data-pipeline
```

2. **Descargar el dataset**

Descarga los archivos CSV desde [Kaggle](https://www.kaggle.com/datasets/flaviocesarsandoval/car-sales-etl) y colócalos en `data_lake/car_sales_data/`.

3. **Configurar Snowflake**

Ejecuta el siguiente script en un Worksheet de Snowflake para preparar el entorno:

```sql
USE ROLE SYSADMIN;

-- Crear almacén y base de datos
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH WITH WAREHOUSE_SIZE = 'X-SMALL';
CREATE DATABASE IF NOT EXISTS CAR_SALES_DB;

-- Crear el esquema donde aterrizan los datos
CREATE SCHEMA IF NOT EXISTS CAR_SALES_DB.RAW;
```

4. **Configurar variables de entorno**

Crear archivo `.env`:

```env
# Postgres
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# Snowflake
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=CAR_SALES_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

5. **Levantar servicios**

```bash
docker compose build
docker compose up -d
```

6. **Acceder a las interfaces**

- **Airflow**: http://localhost:8080 (admin/admin)
- **Dashboard**: http://localhost:8501

## 📁 Estructura del Proyecto

```
├── code/
│   ├── extract_load/src/
│   │   └── ingest_to_snowflake.py    # Script de ingesta
│   └── transform/dbt_project/         # Modelos dbt
│       └── models/
│           ├── A_Sources/             # Definición de fuentes
│           ├── B_Staging/             # Limpieza y tipado
│           ├── C_Intermediate/        # Lógica de negocio
│           └── D_Marts/               # Tablas analíticas
├── dags/
│   └── car_sales_pipeline.py         # DAG de Airflow
├── dashboard/
│   ├── app.py                         # Aplicación Streamlit
│   ├── data.py                        # Conexión a Snowflake
│   ├── utils.py                       # Funciones auxiliares
│   └── requirements.txt
├── data_lake/car_sales_data/          # Archivos CSV fuente
├── infra/airflow/
│   ├── Dockerfile                     # Imagen custom de Airflow
│   └── requirements.txt
├── tests/
│   ├── unit/                          # Tests unitarios
│   └── integration_test_snowflake.py  # Test de integración
├── docker-compose.yml
└── .env
```

## 📊 Pipeline de Datos

### DAG: `car_sales_data_pipeline`

```
start → ingest_to_snowflake → dbt_build → end
```

**Configuración:**

- **Schedule**: `@monthly` (primer día de cada mes)
- **Start Date**: 2018-03-01
- **Catchup**: `True` (procesa datos históricos)
- **Retries**: 1

### 1. Ingesta (Extract & Load)

Lee archivos CSV mensuales (`car_sales_data_YYYY_M.csv`) y los carga en `CAR_SALES_DB.RAW.CAR_SALES`.

### 2. Transformación (dbt)

**Capas:**

- **Staging**: Limpieza y estandarización (`stg_car_sales`)
- **Intermediate**: Cálculos de negocio (`int_sales_prep`)
- **Marts**: Tablas analíticas
  - `dim_cars`: Dimensión de automóviles
  - `dim_salespeople`: Dimensión de vendedores
  - `fct_car_sales`: Tabla de hechos
  - `obt_car_sales`: One Big Table para dashboards

### 3. Visualización

Dashboard con:

- **KPIs**: Ingresos totales, comisiones pagadas, ticket promedio, unidades vendidas
- **Gráficos**: Tendencia mensual de ventas, ranking de vendedores
- **Filtros**: Por marca y rango de fechas
- **Detalle**: Tabla transaccional completa

## 🧪 Testing & CI/CD

### Tests Locales

```bash
# Tests unitarios
python3 -m unittest discover -s tests/unit

# Test de integración Snowflake
python3 tests/integration_test_snowflake.py
```

### GitHub Actions

El pipeline CI/CD ejecuta automáticamente:

1. Linting con flake8
2. Tests unitarios
3. Test de integración con Snowflake
4. Validación de modelos dbt

## 🔧 Comandos Útiles

```bash
# Ver logs de Airflow
docker compose logs airflow-scheduler --tail=50

# Ejecutar DAG manualmente
docker compose exec airflow-scheduler airflow dags trigger car_sales_data_pipeline

# Ejecutar dbt manualmente
docker compose exec airflow-scheduler bash
cd /opt/airflow/code/transform/dbt_project
/opt/dbt_venv/bin/dbt build --profiles-dir .

# Reiniciar servicios
docker compose restart

# Detener todo
docker compose down
```

## 🛠️ Troubleshooting

### Airflow no detecta el DAG

```bash
docker compose restart airflow-scheduler
```

### Error de conexión a Snowflake

```bash
# Verificar variables de entorno
docker compose exec airflow-webserver env | grep SNOWFLAKE
```

### Dashboard no carga datos

```bash
docker compose logs streamlit-app
```

## 👤 Autor

**Navier Cracco**
