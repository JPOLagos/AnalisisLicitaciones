-- ====================================================================
-- PROYECTO LICITACIONES DE CHILE: CONSULTAS ANALÍTICAS (SQL)
-- Dataset: Licitacion_procesada
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. Resumen de Gasto por Rubro Principal (RubroN1)
-- --------------------------------------------------------------------
SELECT 
    RubroN1,
    COUNT(DISTINCT codigoOC) AS Total_OCs,
    COUNT(*) AS Total_Items,
    SUM(TotalItemCLP) AS Monto_Total_CLP,
    ROUND(SUM(TotalItemCLP) / 950.0, 2) AS Monto_Total_USD,
    ROUND(AVG(MontoNetoItemCLP), 0) AS Monto_Promedio_Item_CLP
FROM licitaciones_procesadas
GROUP BY RubroN1
ORDER BY Monto_Total_CLP DESC;

-- --------------------------------------------------------------------
-- 2. Ranking Top 20 Instituciones Compradoras
-- --------------------------------------------------------------------
SELECT 
    UnidadCompraRUT,
    UnidadCompra,
    RegionUnidadCompra,
    COUNT(DISTINCT codigoOC) AS Cantidad_OC,
    SUM(TotalItemCLP) AS Monto_Total_CLP,
    ROUND(SUM(TotalItemCLP) * 100.0 / (SELECT SUM(TotalItemCLP) FROM licitaciones_procesadas), 2) AS Porcentaje_Gasto_Nacional
FROM licitaciones_procesadas
GROUP BY UnidadCompraRUT, UnidadCompra, RegionUnidadCompra
ORDER BY Monto_Total_CLP DESC
LIMIT 20;

-- --------------------------------------------------------------------
-- 3. Concentración de Proveedores y Segmentación por Tamaño (PYMEs)
-- --------------------------------------------------------------------
SELECT 
    TamanoProveedor,
    COUNT(DISTINCT ProveedorRUT) AS Cantidad_Proveedores_Unicos,
    COUNT(DISTINCT codigoOC) AS Cantidad_OC,
    SUM(TotalItemCLP) AS Monto_Total_CLP,
    ROUND(SUM(TotalItemCLP) * 100.0 / (SELECT SUM(TotalItemCLP) FROM licitaciones_procesadas), 2) AS Porcentaje_Participacion
FROM licitaciones_procesadas
GROUP BY TamanoProveedor
ORDER BY Monto_Total_CLP DESC;

-- --------------------------------------------------------------------
-- 4. Matriz de Comercio Interregional (Comprador vs Proveedor)
-- --------------------------------------------------------------------
SELECT 
    RegionUnidadCompra,
    RegionProveedor,
    CASE 
        WHEN RegionUnidadCompra = RegionProveedor THEN 'Local (Misma Región)'
        ELSE 'Interregional'
    END AS Tipo_Flujo_Comercial,
    COUNT(DISTINCT codigoOC) AS Cantidad_OC,
    SUM(TotalItemCLP) AS Monto_Total_CLP
FROM licitaciones_procesadas
GROUP BY RegionUnidadCompra, RegionProveedor, Tipo_Flujo_Comercial
ORDER BY Monto_Total_CLP DESC;

-- --------------------------------------------------------------------
-- 5. Tendencia Temporal Mensual de Compras
-- --------------------------------------------------------------------
SELECT 
    DATE_TRUNC('month', FechaEnvioOC_dt) AS Mes,
    COUNT(DISTINCT codigoOC) AS Cantidad_OC,
    SUM(TotalItemCLP) AS Monto_Total_CLP,
    ROUND(AVG(TotalItemCLP), 0) AS Ticket_Promedio_CLP
FROM licitaciones_procesadas
WHERE FechaEnvioOC_dt IS NOT NULL
GROUP BY 1
ORDER BY 1 ASC;
