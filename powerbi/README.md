# Guía de Modelado y Dashboard en Power BI — Licitaciones de Chile

Esta guía contiene la arquitectura del modelo de datos, relaciones sugeridas, fórmulas DAX fundamentales y la estructura visual recomendada para construir el tablero ejecutivo en Power BI.

---

## 1. Arquitectura del Modelo de Datos (Modelo Estrella)

Para optimizar el rendimiento de Power BI con el archivo `Licitacion_procesada.parquet` (~471k filas), se recomienda un **Modelo en Estrella (Star Schema)**:

### 📊 Tabla de Hechos: `Fact_Licitaciones`
- **Campos de Montos y Transacciones:** `codigoOC`, `CantidadItem`, `MontoNetoItemCLP`, `TotalItemCLP`, `MontoTotalOCCLP`.
- **Claves Foráneas:** `FechaEnvioOC_dt` (KeyFecha), `UnidadCompraRUT` (KeyComprador), `ProveedorRUT` (KeyProveedor), `CodigoProductoONU` (KeyProducto).

### 🏷️ Tablas de Dimensiones Recomendadas:
1. **`Dim_Calendario`**: `Fecha`, `Año`, `Mes`, `NombreMes`, `Trimestre`, `Semana`.
2. **`Dim_Comprador`**: `UnidadCompraRUT`, `UnidadCompra`, `RegionUnidadCompra`.
3. **`Dim_Proveedor`**: `ProveedorRUT`, `Proveedor`, `TamanoProveedor`, `RegionProveedor`.
4. **`Dim_Rubro`**: `CodigoProductoONU`, `ONUProducto`, `RubroN1`, `RubroN2`, `RubroN3`.

---

## 2. Fórmulas DAX Clave

### 💰 Monto Total Transado en CLP
```dax
[Total Gasto CLP] = 
SUM(Fact_Licitaciones[TotalItemCLP])
```

### 💵 Monto Total Transado en USD
```dax
[Total Gasto USD] = 
DIVIDE([Total Gasto CLP], 950, 0)
```

### 📋 Total de Órdenes de Compra
```dax
[Total OCs] = 
DISTINCTCOUNT(Fact_Licitaciones[codigoOC])
```

### 🏢 Participación de PYMEs (%)
```dax
[% Gasto PYME] = 
CALCULATE(
    [Total Gasto CLP],
    Dim_Proveedor[TamanoProveedor] IN {"Micro", "Pequena", "Mediana"}
) / [Total Gasto CLP]
```

### 🎯 Ranking Dinámico de Proveedores
```dax
[Ranking Proveedor] = 
IF(
    ISINSCOPE(Dim_Proveedor[Proveedor]),
    RANKX(
        ALLSELECTED(Dim_Proveedor[Proveedor]),
        [Total Gasto CLP],
        ,
        DESC
    )
)
```

---

## 3. Estructura Sugerida del Dashboard (3 Páginas)

### 📈 Página 1: Resumen Ejecutivo y Métricas Clave
- **Tarjetas KPI:** Gasto Total CLP / USD, Cantidad de OCs, Proveedores Únicos, % Participación PYME.
- **Gráfico de Líneas:** Evolución mensual del gasto público.
- **Gráfico de Barras Horizontal:** Top 10 Rubros con mayor presupuesto asignado.
- **Filtros (Slicers):** Año, Región Compradora, Tamaño de Proveedor.

### 🏢 Página 2: Análisis de Compradores y Proveedores
- **Matriz / Tabla:** Ranking Top 20 Instituciones Compradoras vs Proveedores adjudicados.
- **Gráfico de Torta / Donas:** Distribución del gasto según tamaño del proveedor (Micro, Pequeña, Mediana, Gran Empresa).
- **Gráfico de Treemap:** Distribución de compras por Procedencia de OC (`Licitacion Publica`, `Convenio Marco`, etc.).

### 🗺️ Página 3: Mapa y Flujo Geográfico
- **Mapa de Coropletas / Puntos:** Gasto por `RegionUnidadCompra` vs `RegionProveedor`.
- **Matriz de Comercio Regional:** Porcentaje de compras locales vs origen interregional.
