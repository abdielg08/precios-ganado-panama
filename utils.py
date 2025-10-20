#!/usr/bin/env python3
"""
Utilidades para análisis de datos de precios de ganado
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta


def load_data(source='auto'):
    """
    Carga datos desde CSV o SQLite

    Args:
        source: 'auto', 'csv', 'sqlite', o ruta específica

    Returns:
        DataFrame con los datos
    """
    if source == 'auto':
        db_path = 'data/precios_ganado.db'
        csv_path = 'data/precios_ganado.csv'

        if os.path.exists(db_path):
            source = db_path
        elif os.path.exists(csv_path):
            source = csv_path
        else:
            raise FileNotFoundError("No se encontró archivo de datos")

    if source.endswith('.db') or source.endswith('.sqlite'):
        conn = sqlite3.connect(source)
        df = pd.read_sql_query("SELECT * FROM precios_ganado", conn)
        conn.close()
    else:
        df = pd.read_csv(source)

    # Convertir fechas
    if 'fecha_desde' in df.columns:
        df['fecha_desde'] = pd.to_datetime(df['fecha_desde'])
    if 'fecha_hasta' in df.columns:
        df['fecha_hasta'] = pd.to_datetime(df['fecha_hasta'])

    # Crear fecha promedio
    df['fecha'] = df[['fecha_desde', 'fecha_hasta']].mean(axis=1)

    return df


def filter_by_date(df, start_date=None, end_date=None):
    """Filtra DataFrame por rango de fechas"""
    if start_date:
        df = df[df['fecha'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['fecha'] <= pd.to_datetime(end_date)]
    return df


def filter_by_lugar(df, lugares):
    """Filtra DataFrame por lugares"""
    if not isinstance(lugares, list):
        lugares = [lugares]
    return df[df['lugar'].isin(lugares)]


def filter_by_categoria(df, categorias):
    """Filtra DataFrame por categorías"""
    if not isinstance(categorias, list):
        categorias = [categorias]
    return df[df['categoria'].isin(categorias)]


def get_price_stats(df, group_by=None):
    """
    Obtiene estadísticas de precios

    Args:
        df: DataFrame
        group_by: 'lugar', 'categoria', 'fecha', o None

    Returns:
        DataFrame con estadísticas
    """
    if group_by:
        stats = df.groupby(group_by)['precio'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('min', 'min'),
            ('max', 'max'),
            ('std', 'std')
        ]).round(2)
    else:
        stats = df['precio'].describe()

    return stats


def get_price_trends(df, freq='M'):
    """
    Calcula tendencias de precios

    Args:
        df: DataFrame
        freq: 'D' (diario), 'W' (semanal), 'M' (mensual), 'Y' (anual)

    Returns:
        DataFrame con tendencias
    """
    df_trend = df.copy()
    df_trend = df_trend.set_index('fecha')

    trends = df_trend.groupby(pd.Grouper(freq=freq))['precio'].agg([
        ('count', 'count'),
        ('mean', 'mean'),
        ('min', 'min'),
        ('max', 'max')
    ]).round(2)

    return trends


def compare_places(df, lugares=None, top_n=10):
    """Compara precios entre lugares"""
    if lugares is None:
        # Tomar top N lugares por número de registros
        lugares = df['lugar'].value_counts().head(top_n).index.tolist()

    comparison = df[df['lugar'].isin(lugares)].groupby('lugar')['precio'].agg([
        ('registros', 'count'),
        ('promedio', 'mean'),
        ('minimo', 'min'),
        ('maximo', 'max'),
        ('desv_std', 'std')
    ]).round(2)

    return comparison.sort_values('promedio', ascending=False)


def compare_categories(df, categorias=None, top_n=10):
    """Compara precios entre categorías"""
    if categorias is None:
        # Tomar top N categorías por número de registros
        categorias = df['categoria'].value_counts().head(top_n).index.tolist()

    comparison = df[df['categoria'].isin(categorias)].groupby('categoria')['precio'].agg([
        ('registros', 'count'),
        ('promedio', 'mean'),
        ('minimo', 'min'),
        ('maximo', 'max'),
        ('desv_std', 'std')
    ]).round(2)

    return comparison.sort_values('promedio', ascending=False)


def get_price_changes(df, freq='M'):
    """
    Calcula cambios en precios periodo a periodo

    Args:
        df: DataFrame
        freq: 'D', 'W', 'M', 'Y'

    Returns:
        DataFrame con cambios absolutos y porcentuales
    """
    trends = get_price_trends(df, freq)

    changes = pd.DataFrame({
        'precio_promedio': trends['mean'],
        'cambio_absoluto': trends['mean'].diff(),
        'cambio_porcentual': trends['mean'].pct_change() * 100
    }).round(2)

    return changes


def find_outliers(df, method='iqr', threshold=1.5):
    """
    Encuentra valores atípicos en precios

    Args:
        df: DataFrame
        method: 'iqr' (rango intercuartil) o 'zscore'
        threshold: 1.5 para IQR, 3 para z-score

    Returns:
        DataFrame con outliers
    """
    if method == 'iqr':
        Q1 = df['precio'].quantile(0.25)
        Q3 = df['precio'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = df[(df['precio'] < lower_bound) | (df['precio'] > upper_bound)]

    elif method == 'zscore':
        from scipy import stats
        z_scores = stats.zscore(df['precio'])
        outliers = df[abs(z_scores) > threshold]

    return outliers


def export_summary(df, output_file='summary_report.txt'):
    """Genera y exporta un resumen completo"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("REPORTE DE ANÁLISIS DE PRECIOS DE GANADO\n")
        f.write("="*70 + "\n\n")

        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Información general
        f.write("1. INFORMACIÓN GENERAL\n")
        f.write("-"*70 + "\n")
        f.write(f"Total de registros: {len(df):,}\n")
        f.write(f"Rango de fechas: {df['fecha'].min().date()} a {df['fecha'].max().date()}\n")
        f.write(f"Lugares únicos: {df['lugar'].nunique()}\n")
        f.write(f"Categorías únicas: {df['categoria'].nunique()}\n\n")

        # Estadísticas de precios
        f.write("2. ESTADÍSTICAS DE PRECIOS\n")
        f.write("-"*70 + "\n")
        stats = df['precio'].describe()
        for stat, value in stats.items():
            f.write(f"{stat.capitalize()}: B/. {value:,.2f}\n")
        f.write("\n")

        # Top lugares
        f.write("3. TOP 10 LUGARES POR PRECIO PROMEDIO\n")
        f.write("-"*70 + "\n")
        top_lugares = compare_places(df, top_n=10)
        f.write(top_lugares.to_string())
        f.write("\n\n")

        # Top categorías
        f.write("4. TOP 10 CATEGORÍAS POR PRECIO PROMEDIO\n")
        f.write("-"*70 + "\n")
        top_cats = compare_categories(df, top_n=10)
        f.write(top_cats.to_string())
        f.write("\n\n")

        # Tendencias mensuales
        f.write("5. TENDENCIAS MENSUALES (ÚLTIMOS 12 MESES)\n")
        f.write("-"*70 + "\n")
        trends = get_price_trends(df, freq='M').tail(12)
        f.write(trends.to_string())
        f.write("\n\n")

        # Outliers
        f.write("6. VALORES ATÍPICOS DETECTADOS\n")
        f.write("-"*70 + "\n")
        outliers = find_outliers(df)
        f.write(f"Total de outliers: {len(outliers)}\n")
        if len(outliers) > 0:
            f.write(f"Precio mínimo atípico: B/. {outliers['precio'].min():,.2f}\n")
            f.write(f"Precio máximo atípico: B/. {outliers['precio'].max():,.2f}\n")
        f.write("\n")

        f.write("="*70 + "\n")
        f.write("FIN DEL REPORTE\n")
        f.write("="*70 + "\n")

    print(f"✓ Reporte guardado en: {output_file}")


def query_data(df, query_dict):
    """
    Consulta datos con múltiples filtros

    Args:
        df: DataFrame
        query_dict: dict con filtros, ej:
            {
                'fecha_inicio': '2024-01-01',
                'fecha_fin': '2024-12-31',
                'lugares': ['Divisa', 'Aguadulce'],
                'categorias': ['Novillo', 'Ternera'],
                'precio_min': 1000,
                'precio_max': 2000
            }

    Returns:
        DataFrame filtrado
    """
    result = df.copy()

    if 'fecha_inicio' in query_dict:
        result = filter_by_date(result, start_date=query_dict['fecha_inicio'])

    if 'fecha_fin' in query_dict:
        result = filter_by_date(result, end_date=query_dict['fecha_fin'])

    if 'lugares' in query_dict:
        result = filter_by_lugar(result, query_dict['lugares'])

    if 'categorias' in query_dict:
        result = filter_by_categoria(result, query_dict['categorias'])

    if 'precio_min' in query_dict:
        result = result[result['precio'] >= query_dict['precio_min']]

    if 'precio_max' in query_dict:
        result = result[result['precio'] <= query_dict['precio_max']]

    return result


# Ejemplo de uso
if __name__ == "__main__":
    print("Utilidades para análisis de precios de ganado")
    print("\nFunciones disponibles:")
    print("  - load_data(): Cargar datos")
    print("  - filter_by_date(): Filtrar por fechas")
    print("  - filter_by_lugar(): Filtrar por lugares")
    print("  - filter_by_categoria(): Filtrar por categorías")
    print("  - get_price_stats(): Estadísticas de precios")
    print("  - get_price_trends(): Tendencias de precios")
    print("  - compare_places(): Comparar lugares")
    print("  - compare_categories(): Comparar categorías")
    print("  - get_price_changes(): Cambios en precios")
    print("  - find_outliers(): Encontrar valores atípicos")
    print("  - export_summary(): Exportar reporte completo")
    print("  - query_data(): Consultar datos con múltiples filtros")

    print("\nEjemplo de uso:")
    print("""
    from utils import load_data, compare_places

    df = load_data()
    comparison = compare_places(df, top_n=5)
    print(comparison)
    """)
