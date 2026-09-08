# 📊 Análisis de Licitaciones Públicas de Chile

![Python](https://img.shields.io/badge/python-3.9-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-2.3-150458?logo=pandas&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Pipeline de datos y análisis exploratorio sobre **órdenes de compra públicas de Chile** (sector Salud, 2025 Sem. 1), con limpieza y homologación de monedas a CLP, EDA en Python y dashboard ejecutivo en Power BI.

## Tabla de contenidos

- [Estructura del proyecto](#estructura-del-proyecto)
- [Fuente de datos](#fuente-de-datos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Resultados](#resultados)
- [Power BI](#power-bi)
- [Licencia](#licencia)

## Estructura del proyecto

```
Licitaciones/
├── notebooks/
│   ├── 001_exploracion_inicial.ipynb      # Exploración y diagnóstico del dataset crudo
│   ├── 002_limpieza_y_procesamiento.ipynb # Limpieza, homologación de monedas e imputación
│   ├── 003_analisis_exploratorio.ipynb    # EDA y generación de gráficos
│   └── process_licitaciones.py            # Script de procesamiento (usado por el notebook 002)
├── sql/
│   └── analytical_queries.sql             # Consultas analíticas de referencia
├── powerbi/
│   └── README.md                          # Guía de modelado y dashboard en Power BI
├── data/
│   ├── raw/                                # Dataset crudo (no versionado, ver Fuente de datos)
│   └── processed/                          # Salidas del pipeline (parquet, gráficos)
└── requirements.txt
```

## Fuente de datos

El dataset crudo (`Licitacion.csv`, ~561 MB, ~471.7k registros) no está incluido en este repositorio por su peso. Es información pública, descargable desde:

- [Descarga directa (Salud, 2025 Sem. 1)](https://chc-lic-files.mercadopublico.cl/sector/2025/Sem1/Salud.7z)
- [Portal de Datos Abiertos de ChileCompra](https://datos-abiertos.chilecompra.cl/descargas)

Colócalo en `data/raw/Licitacion.csv` y corre `notebooks/process_licitaciones.py` para regenerar `data/processed/Licitacion_procesada.parquet`.

## Instalación

```bash
git clone https://github.com/JPOLagos/AnalisisLicitaciones.git
cd AnalisisLicitaciones
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

1. Descarga el dataset crudo (ver [Fuente de datos](#fuente-de-datos)) y colócalo en `data/raw/Licitacion.csv`.
2. Abre JupyterLab:
   ```bash
   jupyter lab
   ```
3. Ejecuta los notebooks en orden:
   - `001_exploracion_inicial.ipynb` — diagnóstico del dataset crudo.
   - `002_limpieza_y_procesamiento.ipynb` — genera `data/processed/Licitacion_procesada.parquet`.
   - `003_analisis_exploratorio.ipynb` — genera los gráficos de `data/processed/`.

## Resultados

El EDA cubre: gasto por región, top proveedores y compradores, distribución por rubro, participación de PYMEs y evolución temporal del gasto. Los gráficos se generan en `data/processed/*.png` al correr el notebook 003.

*(Capturas del dashboard de Power BI — próximamente.)*

## Power BI

La carpeta [`powerbi/`](powerbi/README.md) incluye la arquitectura del modelo de datos (modelo estrella), fórmulas DAX clave y la estructura sugerida del dashboard ejecutivo, construido sobre `Licitacion_procesada.parquet`.

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE) — libre para usar, copiar y modificar.
