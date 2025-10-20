#!/usr/bin/env python3
"""
Análisis Estacional de Precios de Ganado en Panamá
Identifica los mejores meses para comprar (precios bajos) y vender (precios altos)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar estilo de gráficos
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def cargar_datos():
    """Carga los datos de precios de ganado"""
    print("📊 Cargando datos de precios de ganado...")
    df = pd.read_csv('data/precios_ganado_sin_outliers.csv')

    # Convertir fechas
    df['fecha_desde'] = pd.to_datetime(df['fecha_desde'], format='%d/%m/%Y')
    df['fecha_hasta'] = pd.to_datetime(df['fecha_hasta'], format='%d/%m/%Y')

    # Extraer mes y año
    df['mes'] = df['fecha_desde'].dt.month
    df['año'] = df['fecha_desde'].dt.year
    df['mes_nombre'] = df['fecha_desde'].dt.month_name()

    print(f"✓ Datos cargados: {len(df):,} registros")
    print(f"✓ Período: {df['fecha_desde'].min().strftime('%Y-%m-%d')} a {df['fecha_hasta'].max().strftime('%Y-%m-%d')}")
    print(f"✓ Lugares únicos: {df['lugar'].nunique()}")
    print(f"✓ Categorías únicas: {df['categoria'].nunique()}")

    return df

def analizar_por_mes(df):
    """Analiza precios promedio por mes del año"""
    print("\n📈 Analizando precios por mes del año...")

    # Agrupar por mes
    precios_por_mes = df.groupby('mes').agg({
        'precio': ['mean', 'median', 'std', 'min', 'max', 'count']
    }).round(2)

    precios_por_mes.columns = ['Promedio', 'Mediana', 'Desv.Est', 'Mínimo', 'Máximo', 'Registros']

    # Agregar nombres de meses
    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    precios_por_mes['Mes'] = precios_por_mes.index.map(meses_nombres)
    precios_por_mes = precios_por_mes[['Mes', 'Promedio', 'Mediana', 'Desv.Est', 'Mínimo', 'Máximo', 'Registros']]

    return precios_por_mes

def identificar_mejores_meses(precios_por_mes):
    """Identifica los mejores meses para comprar y vender"""
    print("\n💰 Identificando mejores oportunidades...")

    # Ordenar por precio promedio
    mejores_compra = precios_por_mes.nsmallest(3, 'Promedio')
    mejores_venta = precios_por_mes.nlargest(3, 'Promedio')

    return mejores_compra, mejores_venta

def analizar_por_categoria(df):
    """Analiza precios por categoría de ganado y mes"""
    print("\n🐄 Analizando por categoría de ganado...")

    # Top categorías más comunes
    top_categorias = df['categoria'].value_counts().head(10).index.tolist()

    # Filtrar solo top categorías
    df_top = df[df['categoria'].isin(top_categorias)]

    # Agrupar por mes y categoría
    categoria_mes = df_top.groupby(['mes', 'categoria'])['precio'].mean().reset_index()
    categoria_mes_pivot = categoria_mes.pivot(index='mes', columns='categoria', values='precio')

    return categoria_mes_pivot, top_categorias

def analizar_por_lugar(df):
    """Analiza precios por ubicación geográfica"""
    print("\n📍 Analizando por ubicación geográfica...")

    # Promedio por lugar
    precios_por_lugar = df.groupby('lugar')['precio'].agg(['mean', 'count']).round(2)
    precios_por_lugar.columns = ['Precio_Promedio', 'Num_Registros']
    precios_por_lugar = precios_por_lugar.sort_values('Precio_Promedio')

    # Top 5 más baratos y más caros
    lugares_baratos = precios_por_lugar.head(5)
    lugares_caros = precios_por_lugar.tail(5)

    return precios_por_lugar, lugares_baratos, lugares_caros

def crear_visualizaciones(df, precios_por_mes, categoria_mes_pivot):
    """Crea visualizaciones de tendencias"""
    print("\n📊 Creando visualizaciones...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Análisis Estacional de Precios de Ganado en Panamá', fontsize=16, fontweight='bold')

    # 1. Línea de precios promedio por mes
    ax1 = axes[0, 0]
    meses = precios_por_mes.index
    precios = precios_por_mes['Promedio']
    ax1.plot(meses, precios, marker='o', linewidth=2, markersize=8, color='#2E86AB')
    ax1.fill_between(meses, precios, alpha=0.3, color='#2E86AB')
    ax1.set_xlabel('Mes', fontsize=12)
    ax1.set_ylabel('Precio Promedio (B/.)', fontsize=12)
    ax1.set_title('Precio Promedio por Mes del Año', fontsize=13, fontweight='bold')
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(['E', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
    ax1.grid(True, alpha=0.3)

    # Marcar máximos y mínimos
    max_mes = precios.idxmax()
    min_mes = precios.idxmin()
    ax1.scatter([max_mes], [precios[max_mes]], color='red', s=150, zorder=5, label='Precio más alto')
    ax1.scatter([min_mes], [precios[min_mes]], color='green', s=150, zorder=5, label='Precio más bajo')
    ax1.legend()

    # 2. Box plot de distribución por mes
    ax2 = axes[0, 1]
    df_plot = df[['mes', 'precio']].copy()
    df_plot.boxplot(column='precio', by='mes', ax=ax2)
    ax2.set_xlabel('Mes', fontsize=12)
    ax2.set_ylabel('Precio (B/.)', fontsize=12)
    ax2.set_title('Distribución de Precios por Mes', fontsize=13, fontweight='bold')
    plt.sca(ax2)
    plt.xticks(range(1, 13), ['E', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])

    # 3. Heatmap de categorías por mes
    ax3 = axes[1, 0]
    sns.heatmap(categoria_mes_pivot.T, annot=False, cmap='YlOrRd', ax=ax3, cbar_kws={'label': 'Precio (B/.)'})
    ax3.set_xlabel('Mes', fontsize=12)
    ax3.set_ylabel('Categoría', fontsize=12)
    ax3.set_title('Precio por Categoría y Mes', fontsize=13, fontweight='bold')
    ax3.set_xticklabels(['E', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])

    # 4. Precios por lugar (top 10)
    ax4 = axes[1, 1]
    lugar_promedio = df.groupby('lugar')['precio'].mean().sort_values(ascending=False).head(10)
    lugar_promedio.plot(kind='barh', ax=ax4, color='#A23B72')
    ax4.set_xlabel('Precio Promedio (B/.)', fontsize=12)
    ax4.set_ylabel('Lugar', fontsize=12)
    ax4.set_title('Top 10 Lugares con Precios Más Altos', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig('analisis_estacional_ganado.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: analisis_estacional_ganado.png")

    return fig

def generar_reporte(precios_por_mes, mejores_compra, mejores_venta, lugares_baratos, lugares_caros, top_categorias):
    """Genera reporte con recomendaciones"""
    print("\n📝 Generando reporte de recomendaciones...")

    reporte = []
    reporte.append("="*80)
    reporte.append("ANÁLISIS ESTACIONAL DE PRECIOS DE GANADO EN PANAMÁ")
    reporte.append("Sistema de Recomendaciones para Compra y Venta")
    reporte.append("="*80)
    reporte.append("")

    # Resumen ejecutivo
    reporte.append("📊 RESUMEN EJECUTIVO")
    reporte.append("-"*80)
    precio_min_global = precios_por_mes['Promedio'].min()
    precio_max_global = precios_por_mes['Promedio'].max()
    diferencia = precio_max_global - precio_min_global
    porcentaje_ganancia = (diferencia / precio_min_global) * 100

    reporte.append(f"Precio promedio más bajo del año: B/. {precio_min_global:.2f}")
    reporte.append(f"Precio promedio más alto del año: B/. {precio_max_global:.2f}")
    reporte.append(f"Diferencia: B/. {diferencia:.2f} ({porcentaje_ganancia:.1f}% de margen potencial)")
    reporte.append("")

    # Mejores meses para COMPRAR
    reporte.append("🟢 MEJORES MESES PARA COMPRAR (Precios más bajos)")
    reporte.append("-"*80)
    for idx, (mes_num, row) in enumerate(mejores_compra.iterrows(), 1):
        reporte.append(f"{idx}. {row['Mes']}")
        reporte.append(f"   Precio promedio: B/. {row['Promedio']:.2f}")
        reporte.append(f"   Rango: B/. {row['Mínimo']:.2f} - B/. {row['Máximo']:.2f}")
        reporte.append(f"   Registros analizados: {int(row['Registros']):,}")
        reporte.append("")

    # Mejores meses para VENDER
    reporte.append("🔴 MEJORES MESES PARA VENDER (Precios más altos)")
    reporte.append("-"*80)
    for idx, (mes_num, row) in enumerate(mejores_venta.iterrows(), 1):
        reporte.append(f"{idx}. {row['Mes']}")
        reporte.append(f"   Precio promedio: B/. {row['Promedio']:.2f}")
        reporte.append(f"   Rango: B/. {row['Mínimo']:.2f} - B/. {row['Máximo']:.2f}")
        reporte.append(f"   Registros analizados: {int(row['Registros']):,}")
        reporte.append("")

    # Estrategia recomendada
    reporte.append("💡 ESTRATEGIA RECOMENDADA")
    reporte.append("-"*80)
    mes_compra = mejores_compra.iloc[0]['Mes']
    mes_venta = mejores_venta.iloc[0]['Mes']
    precio_compra = mejores_compra.iloc[0]['Promedio']
    precio_venta = mejores_venta.iloc[0]['Promedio']
    ganancia = precio_venta - precio_compra
    roi = (ganancia / precio_compra) * 100

    reporte.append(f"✓ COMPRAR en: {mes_compra} (precio promedio: B/. {precio_compra:.2f})")
    reporte.append(f"✓ VENDER en: {mes_venta} (precio promedio: B/. {precio_venta:.2f})")
    reporte.append(f"✓ Ganancia potencial: B/. {ganancia:.2f} por unidad ({roi:.1f}% ROI)")
    reporte.append("")

    # Mejores lugares para comprar
    reporte.append("📍 MEJORES LUGARES PARA COMPRAR (Precios más bajos)")
    reporte.append("-"*80)
    for idx, (lugar, row) in enumerate(lugares_baratos.iterrows(), 1):
        reporte.append(f"{idx}. {lugar}: B/. {row['Precio_Promedio']:.2f} ({int(row['Num_Registros']):,} registros)")
    reporte.append("")

    # Lugares con precios más altos (evitar para compra)
    reporte.append("📍 LUGARES CON PRECIOS MÁS ALTOS (Para venta)")
    reporte.append("-"*80)
    for idx, (lugar, row) in enumerate(lugares_caros.iterrows(), 1):
        reporte.append(f"{idx}. {lugar}: B/. {row['Precio_Promedio']:.2f} ({int(row['Num_Registros']):,} registros)")
    reporte.append("")

    # Categorías más transadas
    reporte.append("🐄 CATEGORÍAS MÁS TRANSADAS")
    reporte.append("-"*80)
    for idx, cat in enumerate(top_categorias[:5], 1):
        reporte.append(f"{idx}. {cat}")
    reporte.append("")

    # Notas importantes
    reporte.append("⚠️  NOTAS IMPORTANTES")
    reporte.append("-"*80)
    reporte.append("• Los precios varían según categoría, raza y región")
    reporte.append("• Los datos históricos no garantizan precios futuros")
    reporte.append("• Considere factores como clima, demanda y costos operacionales")
    reporte.append("• Verifique precios actuales antes de tomar decisiones")
    reporte.append("")
    reporte.append("="*80)
    reporte.append(f"Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    reporte.append("="*80)

    # Guardar reporte
    with open('REPORTE_ANALISIS_ESTACIONAL.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(reporte))

    print("✓ Reporte guardado: REPORTE_ANALISIS_ESTACIONAL.txt")

    return '\n'.join(reporte)

def main():
    print("\n" + "="*80)
    print("ANÁLISIS ESTACIONAL DE PRECIOS DE GANADO EN PANAMÁ")
    print("="*80 + "\n")

    # Cargar datos
    df = cargar_datos()

    # Analizar por mes
    precios_por_mes = analizar_por_mes(df)
    print("\n" + precios_por_mes.to_string())

    # Identificar mejores meses
    mejores_compra, mejores_venta = identificar_mejores_meses(precios_por_mes)

    # Analizar por categoría
    categoria_mes_pivot, top_categorias = analizar_por_categoria(df)

    # Analizar por lugar
    precios_por_lugar, lugares_baratos, lugares_caros = analizar_por_lugar(df)

    # Crear visualizaciones
    crear_visualizaciones(df, precios_por_mes, categoria_mes_pivot)

    # Generar reporte
    reporte = generar_reporte(precios_por_mes, mejores_compra, mejores_venta,
                              lugares_baratos, lugares_caros, top_categorias)

    # Mostrar reporte en pantalla
    print("\n" + reporte)

    print("\n✅ Análisis completado exitosamente!")
    print(f"📁 Archivos generados:")
    print(f"   • REPORTE_ANALISIS_ESTACIONAL.txt")
    print(f"   • analisis_estacional_ganado.png\n")

if __name__ == "__main__":
    main()
