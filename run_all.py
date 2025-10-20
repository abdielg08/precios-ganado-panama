#!/usr/bin/env python3
"""
Script principal para ejecutar todo el pipeline de extracción y análisis
"""

import sys
import os
import subprocess

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print_header("VERIFICANDO DEPENDENCIAS")

    required = [
        'requests', 'beautifulsoup4', 'pdfplumber', 'pandas',
        'plotly', 'jupyter', 'openpyxl'
    ]

    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NO INSTALADO")
            missing.append(package)

    if missing:
        print(f"\n⚠ Faltan dependencias. Instalando...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-q'
        ] + missing)
        print("✓ Dependencias instaladas")

    print("\n✓ Todas las dependencias están disponibles")

def run_scraper():
    """Ejecuta el scraper de PDFs"""
    print_header("FASE 1: SCRAPING DE PDFs")

    if os.path.exists('pdfs') and len(os.listdir('pdfs')) > 0:
        response = input(f"\nYa existen {len(os.listdir('pdfs'))} archivos en pdfs/. ¿Desea volver a descargar? (s/n): ")
        if response.lower() != 's':
            print("✓ Omitiendo descarga de PDFs")
            return True

    try:
        from scraper import SubastaGanaderaScraper

        scraper = SubastaGanaderaScraper()
        scraper.crawl_site(max_pages=200)
        scraper.download_all_pdfs()
        scraper.save_metadata()

        print("\n✓ Scraping completado exitosamente")
        return True
    except Exception as e:
        print(f"\n✗ Error en scraping: {e}")
        return False

def run_extractor():
    """Ejecuta el extractor de datos de PDFs"""
    print_header("FASE 2: EXTRACCIÓN DE DATOS DE PDFs")

    if not os.path.exists('pdfs') or len(os.listdir('pdfs')) == 0:
        print("✗ No hay PDFs para procesar. Ejecute primero el scraper.")
        return False

    try:
        from pdf_extractor import PDFDataExtractor

        extractor = PDFDataExtractor()
        tables = extractor.process_all_pdfs()

        if not tables:
            print("✗ No se extrajeron tablas")
            return False

        # Decidir formato según tamaño
        if len(extractor.extracted_data) > 50000:
            print(f"\nDataset grande ({len(extractor.extracted_data)} registros), usando SQLite...")
            extractor.save_to_sqlite()
        else:
            print(f"\nDataset mediano ({len(extractor.extracted_data)} registros), usando CSV...")
            extractor.save_to_csv()

        extractor.generate_summary()

        print("\n✓ Extracción completada exitosamente")
        return True
    except Exception as e:
        print(f"\n✗ Error en extracción: {e}")
        import traceback
        traceback.print_exc()
        return False

def launch_dashboard():
    """Lanza el dashboard de Jupyter"""
    print_header("FASE 3: LANZANDO DASHBOARD")

    if not os.path.exists('data'):
        print("✗ No hay datos procesados. Ejecute primero el extractor.")
        return False

    print("Iniciando Jupyter Notebook...")
    print("\nInstrucciones:")
    print("  1. Se abrirá Jupyter en su navegador")
    print("  2. Abra el archivo 'dashboard.ipynb'")
    print("  3. Ejecute todas las celdas (Cell > Run All)")
    print("\nPresione Ctrl+C en esta terminal para detener Jupyter cuando termine\n")

    try:
        subprocess.run([
            'jupyter', 'notebook', 'dashboard.ipynb'
        ])
    except KeyboardInterrupt:
        print("\n✓ Dashboard cerrado")
    except Exception as e:
        print(f"\n✗ Error al lanzar Jupyter: {e}")
        print("\nIntente ejecutar manualmente:")
        print("  jupyter notebook dashboard.ipynb")
        return False

    return True

def main():
    print("="*70)
    print("  SISTEMA DE ANÁLISIS DE PRECIOS DE GANADO - PANAMÁ")
    print("="*70)
    print("\nEste script ejecutará todo el pipeline:")
    print("  1. Descargar PDFs del sitio web")
    print("  2. Extraer datos de los PDFs")
    print("  3. Crear base de datos estructurada")
    print("  4. Lanzar dashboard interactivo")

    response = input("\n¿Desea continuar? (s/n): ")
    if response.lower() != 's':
        print("Operación cancelada")
        return

    # Verificar dependencias
    check_dependencies()

    # Ejecutar scraper
    if not run_scraper():
        print("\n⚠ Error en scraping. ¿Desea continuar con los PDFs existentes? (s/n): ")
        if input().lower() != 's':
            return

    # Ejecutar extractor
    if not run_extractor():
        print("\n✗ No se pudo completar la extracción de datos")
        return

    # Lanzar dashboard
    print("\n¿Desea lanzar el dashboard ahora? (s/n): ")
    if input().lower() == 's':
        launch_dashboard()
    else:
        print("\nPuede lanzar el dashboard más tarde con:")
        print("  jupyter notebook dashboard.ipynb")

    print_header("PROCESO COMPLETADO")
    print("Archivos generados:")
    print("  - pdfs/           : PDFs descargados")
    print("  - data/           : Datos procesados (CSV o SQLite)")
    print("  - dashboard.ipynb : Dashboard interactivo")
    print("\n✓ Sistema listo para usar")

if __name__ == "__main__":
    main()
