import os
import time
import requests
import pandas as pd
import numpy as np

def get_exchange_rates(years):
    """Obtiene el historial completo anual de dólar y UF de mindicador.cl para agilizar las consultas."""
    dolar_series = {}
    uf_series = {}
    
    for year in years:
        # Dólar
        try:
            r = requests.get(f"https://mindicador.cl/api/dolar/{year}", timeout=10)
            if r.status_code == 200:
                for item in r.json().get('serie', []):
                    # fecha viene ISO: '2025-06-24T04:00:00.000Z'
                    dt_str = item['fecha'][:10]
                    dolar_series[dt_str] = item['valor']
        except Exception as e:
            print(f"Error cargando dólar {year}: {e}")
            
        # UF
        try:
            r = requests.get(f"https://mindicador.cl/api/uf/{year}", timeout=10)
            if r.status_code == 200:
                for item in r.json().get('serie', []):
                    dt_str = item['fecha'][:10]
                    uf_series[dt_str] = item['valor']
        except Exception as e:
            print(f"Error cargando UF {year}: {e}")
            
    return dolar_series, uf_series

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    raw_path = os.path.join(base_dir, 'data', 'raw', 'Licitacion.csv')
    output_parquet = os.path.join(base_dir, 'data', 'processed', 'Licitacion_procesada.parquet')
    output_csv = os.path.join(base_dir, 'data', 'processed', 'Licitacion_procesada.csv.gz')

    print("1. Cargando dataset crudo...")
    start_time = time.time()
    
    cols = [
        'codigoOC',
        'FechaEnvioOC',
        'EstadoOC',
        'ProcedenciaOC',
        'MontoTotalOC',
        'MonedaOC',
        'UnidadCompra',
        'UnidadCompraRUT',
        'RegionUnidadCompra',
        'Proveedor',
        'ProveedorRUT',
        'TamanoProveedor',
        'RegionProveedor',
        'RubroN1',
        'RubroN2',
        'RubroN3',
        'CodigoProductoONU',
        'ONUProducto',
        'CantidadItem',
        'MontoNetoItem',
        'UnidadMedida',
        'MonedaItem',
    ]

    df = pd.read_csv(
        raw_path,
        sep=';',
        encoding='latin-1',
        usecols=cols,
        low_memory=False
    )
    print(f"Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas en {time.time() - start_time:.2f}s")

    print("2. Estandarizando fechas y numéricos...")
    df['FechaEnvioOC_dt'] = pd.to_datetime(df['FechaEnvioOC'], format='%d-%m-%Y %H:%M:%S', errors='coerce').dt.normalize()

    for col in ['CantidadItem', 'MontoNetoItem', 'MontoTotalOC']:
        df[col] = (
            df[col].astype(str)
            .str.replace(',', '.', regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['TotalItem'] = df['CantidadItem'] * df['MontoNetoItem']

    print("3. Obteniendo indicadores económicos anuales de mindicador.cl...")
    years = df['FechaEnvioOC_dt'].dropna().dt.year.unique()
    years = [int(y) for y in years if not np.isnan(y)]
    print(f"Años presentes en el dataset: {years}")

    dolar_map, uf_map = get_exchange_rates(years)

    # Crear rango continuo de fechas para ffill
    if len(df['FechaEnvioOC_dt'].dropna()) > 0:
        min_date = df['FechaEnvioOC_dt'].min()
        max_date = df['FechaEnvioOC_dt'].max()
        full_idx = pd.date_range(min_date, max_date)
        
        s_dolar = pd.Series(dolar_map)
        s_dolar.index = pd.to_datetime(s_dolar.index)
        s_dolar = s_dolar.reindex(full_idx).ffill().bfill().fillna(950.0)
        
        s_uf = pd.Series(uf_map)
        s_uf.index = pd.to_datetime(s_uf.index)
        s_uf = s_uf.reindex(full_idx).ffill().bfill().fillna(38000.0)
    else:
        s_dolar = pd.Series(950.0, index=[pd.Timestamp('2025-01-01')])
        s_uf = pd.Series(38000.0, index=[pd.Timestamp('2025-01-01')])

    df['valor_dolar'] = df['FechaEnvioOC_dt'].map(s_dolar).fillna(950.0)
    df['valor_uf'] = df['FechaEnvioOC_dt'].map(s_uf).fillna(38000.0)

    print("4. Convirtiendo montos a CLP...")
    is_usd_item = df['MonedaItem'] == 'USD'
    is_uf_item = df['MonedaItem'].isin(['CLF', 'UF'])
    
    df['MontoNetoItemCLP'] = df['MontoNetoItem'].copy()
    df.loc[is_usd_item, 'MontoNetoItemCLP'] = df.loc[is_usd_item, 'MontoNetoItem'] * df.loc[is_usd_item, 'valor_dolar']
    df.loc[is_uf_item, 'MontoNetoItemCLP'] = df.loc[is_uf_item, 'MontoNetoItem'] * df.loc[is_uf_item, 'valor_uf']
    
    df['TotalItemCLP'] = df['CantidadItem'] * df['MontoNetoItemCLP']

    is_usd_oc = df['MonedaOC'] == 'USD'
    is_uf_oc = df['MonedaOC'].isin(['CLF', 'UF'])
    df['MontoTotalOCCLP'] = df['MontoTotalOC'].copy()
    df.loc[is_usd_oc, 'MontoTotalOCCLP'] = df.loc[is_usd_oc, 'MontoTotalOC'] * df.loc[is_usd_oc, 'valor_dolar']
    df.loc[is_uf_oc, 'MontoTotalOCCLP'] = df.loc[is_uf_oc, 'MontoTotalOC'] * df.loc[is_uf_oc, 'valor_uf']

    print("5. Imputando regiones faltantes por RUT...")
    map_reg_uc = (
        df.dropna(subset=['UnidadCompraRUT', 'RegionUnidadCompra'])
        .drop_duplicates(subset=['UnidadCompraRUT'])
        .set_index('UnidadCompraRUT')['RegionUnidadCompra']
        .to_dict()
    )
    df['RegionUnidadCompra'] = df['RegionUnidadCompra'].fillna(df['UnidadCompraRUT'].map(map_reg_uc))
    df['RegionUnidadCompra'] = df['RegionUnidadCompra'].fillna('No Especificada')

    map_reg_prov = (
        df.dropna(subset=['ProveedorRUT', 'RegionProveedor'])
        .drop_duplicates(subset=['ProveedorRUT'])
        .set_index('ProveedorRUT')['RegionProveedor']
        .to_dict()
    )
    df['RegionProveedor'] = df['RegionProveedor'].fillna(df['ProveedorRUT'].map(map_reg_prov))
    df['RegionProveedor'] = df['RegionProveedor'].fillna('No Especificada')

    df_clean = df.drop(columns=['valor_dolar', 'valor_uf'])

    print("6. Exportando dataset procesado...")
    os.makedirs(os.path.join(base_dir, 'data', 'processed'), exist_ok=True)
    
    df_clean.to_parquet(output_parquet, index=False)
    print(f"✅ Guardado exitoso en {output_parquet}")
    
    df_clean.to_csv(output_csv, index=False, compression='gzip')
    print(f"✅ Guardado exitoso en {output_csv}")
    print(f"🎉 Proceso completado en {time.time() - start_time:.2f}s")

if __name__ == '__main__':
    main()
