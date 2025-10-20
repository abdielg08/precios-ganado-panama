#!/usr/bin/env python3
"""
Script para extraer datos de tablas de los PDFs de precios de ganado
"""

import pdfplumber
import pandas as pd
import re
import os
from datetime import datetime
from pathlib import Path
import json
import glob


class PDFDataExtractor:
    def __init__(self, pdf_dir="pdfs", output_dir="data"):
        self.pdf_dir = pdf_dir
        self.output_dir = output_dir
        self.extracted_data = []
        self.errors = []

        os.makedirs(self.output_dir, exist_ok=True)

    def extract_date_from_filename(self, filename):
        """Extrae fechas del nombre del archivo"""
        # Patrón: Del DD-MM-YY al DD-MM-YY
        pattern = r'(?:Del|del)?\s*(\d{1,2})-(\d{1,2})-(\d{2,4})\s*(?:al|a|-)?\s*(\d{1,2})-(\d{1,2})-(\d{2,4})'
        match = re.search(pattern, filename)

        if match:
            day1, month1, year1, day2, month2, year2 = match.groups()

            # Convertir año de 2 dígitos a 4
            if len(year1) == 2:
                year1 = '20' + year1
            if len(year2) == 2:
                year2 = '20' + year2

            try:
                date_from = datetime.strptime(f"{day1}-{month1}-{year1}", "%d-%m-%Y")
                date_to = datetime.strptime(f"{day2}-{month2}-{year2}", "%d-%m-%Y")
                return date_from, date_to
            except:
                pass

        return None, None

    def extract_date_from_text(self, text):
        """Extrae fechas del texto del PDF"""
        patterns = [
            r'(?:Del|del)\s+(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{2,4})\s+(?:al|a)\s+(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{2,4})',
            r'(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{2,4})\s+(?:al|a|-)\s+(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{2,4})',
            r'Semana.*?(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{2,4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 6:
                    day1, month1, year1, day2, month2, year2 = groups[:6]
                elif len(groups) == 3:
                    day1, month1, year1 = groups
                    day2, month2, year2 = day1, month1, year1

                # Convertir año de 2 dígitos a 4
                if len(year1) == 2:
                    year1 = '20' + year1
                if len(year2) == 2:
                    year2 = '20' + year2

                try:
                    date_from = datetime.strptime(f"{day1}-{month1}-{year1}", "%d-%m-%Y")
                    date_to = datetime.strptime(f"{day2}-{month2}-{year2}", "%d-%m-%Y")
                    return date_from, date_to
                except:
                    pass

        return None, None

    def clean_price(self, price_str):
        """Limpia y convierte precio a número"""
        if pd.isna(price_str) or price_str == '':
            return None

        # Convertir a string
        price_str = str(price_str)

        # Eliminar símbolos de moneda, espacios, comas
        price_str = re.sub(r'[B/.\s,]', '', price_str)

        # Extraer números
        match = re.search(r'(\d+(?:\.\d+)?)', price_str)
        if match:
            try:
                return float(match.group(1))
            except:
                return None

        return None

    def identify_table_type(self, df):
        """Identifica el tipo de tabla basándose en sus columnas"""
        if df.empty:
            return "unknown"

        # Convertir nombres de columnas a lowercase para comparación
        cols_lower = [str(col).lower() for col in df.columns]
        first_col = str(df.iloc[0, 0]).lower() if len(df) > 0 else ""

        # Buscar palabras clave
        keywords_lugar = ['lugar', 'feria', 'mercado', 'ubicación', 'sitio']
        keywords_categoria = ['categoría', 'categoria', 'tipo', 'clase']
        keywords_precio = ['precio', 'valor', 'monto', 'b/', '$']

        has_lugar = any(kw in ' '.join(cols_lower + [first_col]) for kw in keywords_lugar)
        has_categoria = any(kw in ' '.join(cols_lower + [first_col]) for kw in keywords_categoria)
        has_precio = any(kw in ' '.join(cols_lower) for kw in keywords_precio)

        if has_lugar and has_precio:
            return "por_lugar"
        elif has_categoria and has_precio:
            return "por_categoria"
        else:
            return "general"

    def extract_tables_from_pdf(self, pdf_path):
        """Extrae todas las tablas de un PDF"""
        tables_data = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extraer texto completo para buscar fechas
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""

                # Intentar extraer fechas del texto
                date_from, date_to = self.extract_date_from_text(full_text)

                # Si no se encontró en el texto, buscar en el nombre del archivo
                if not date_from:
                    filename = os.path.basename(pdf_path)
                    date_from, date_to = self.extract_date_from_filename(filename)

                # Extraer tablas de cada página
                for page_num, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()

                    for table_num, table in enumerate(tables, 1):
                        if not table or len(table) < 2:
                            continue

                        # Convertir a DataFrame
                        df = pd.DataFrame(table[1:], columns=table[0])

                        # Limpiar DataFrame
                        df = df.dropna(how='all').reset_index(drop=True)
                        df.columns = [str(col).strip() if col else f"col_{i}"
                                     for i, col in enumerate(df.columns)]

                        # Identificar tipo de tabla
                        table_type = self.identify_table_type(df)

                        tables_data.append({
                            'pdf_path': pdf_path,
                            'pdf_filename': os.path.basename(pdf_path),
                            'page': page_num,
                            'table_num': table_num,
                            'table_type': table_type,
                            'date_from': date_from,
                            'date_to': date_to,
                            'data': df
                        })

        except Exception as e:
            self.errors.append({
                'pdf_path': pdf_path,
                'error': str(e)
            })
            print(f"  ✗ Error procesando {os.path.basename(pdf_path)}: {e}")

        return tables_data

    def normalize_data(self, tables_data):
        """Normaliza los datos extraídos a un formato estándar"""
        normalized = []

        for item in tables_data:
            df = item['data']
            table_type = item['table_type']

            # Intentar diferentes estrategias según el tipo de tabla
            if table_type == "por_lugar":
                normalized.extend(self._normalize_por_lugar(item, df))
            elif table_type == "por_categoria":
                normalized.extend(self._normalize_por_categoria(item, df))
            else:
                normalized.extend(self._normalize_general(item, df))

        return normalized

    def _normalize_por_lugar(self, item, df):
        """Normaliza tablas organizadas por lugar"""
        records = []

        for idx, row in df.iterrows():
            # Buscar columna de lugar
            lugar = None
            for col in df.columns:
                val = str(row[col])
                if any(kw in str(col).lower() for kw in ['lugar', 'feria', 'mercado']):
                    lugar = val
                    break

            if not lugar:
                lugar = str(row.iloc[0])

            # Buscar columnas de precios
            for col in df.columns:
                if any(kw in str(col).lower() for kw in ['precio', 'valor', 'b/', '$']):
                    precio = self.clean_price(row[col])
                    if precio:
                        records.append({
                            'fecha_desde': item['date_from'],
                            'fecha_hasta': item['date_to'],
                            'lugar': lugar.strip(),
                            'categoria': str(col),
                            'precio': precio,
                            'fuente_pdf': item['pdf_filename'],
                            'tipo_tabla': item['table_type']
                        })

        return records

    def _normalize_por_categoria(self, item, df):
        """Normaliza tablas organizadas por categoría"""
        records = []

        for idx, row in df.iterrows():
            # Buscar columna de categoría
            categoria = None
            for col in df.columns:
                val = str(row[col])
                if any(kw in str(col).lower() for kw in ['categoría', 'categoria', 'tipo']):
                    categoria = val
                    break

            if not categoria:
                categoria = str(row.iloc[0])

            # Buscar columnas de precios o lugares
            for col in df.columns:
                if col != df.columns[0]:  # Saltar primera columna (categoría)
                    precio = self.clean_price(row[col])
                    if precio:
                        records.append({
                            'fecha_desde': item['date_from'],
                            'fecha_hasta': item['date_to'],
                            'lugar': str(col) if 'precio' not in str(col).lower() else 'General',
                            'categoria': categoria.strip(),
                            'precio': precio,
                            'fuente_pdf': item['pdf_filename'],
                            'tipo_tabla': item['table_type']
                        })

        return records

    def _normalize_general(self, item, df):
        """Normaliza tablas de formato general"""
        records = []

        # Estrategia: primera columna = categoría/lugar, otras columnas = precios
        for idx, row in df.iterrows():
            identifier = str(row.iloc[0]).strip()

            for col_idx, col in enumerate(df.columns[1:], 1):
                precio = self.clean_price(row.iloc[col_idx])
                if precio:
                    records.append({
                        'fecha_desde': item['date_from'],
                        'fecha_hasta': item['date_to'],
                        'lugar': identifier if 'lugar' in str(df.columns[0]).lower() else str(col),
                        'categoria': identifier if 'categ' in str(df.columns[0]).lower() else str(col),
                        'precio': precio,
                        'fuente_pdf': item['pdf_filename'],
                        'tipo_tabla': item['table_type']
                    })

        return records

    def process_all_pdfs(self):
        """Procesa todos los PDFs en el directorio"""
        pdf_files = glob.glob(os.path.join(self.pdf_dir, "*.pdf"))

        if not pdf_files:
            print(f"No se encontraron PDFs en {self.pdf_dir}/")
            return

        print(f"Procesando {len(pdf_files)} archivos PDF...\n")

        all_tables = []
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"[{i}/{len(pdf_files)}] {os.path.basename(pdf_path)}")
            tables = self.extract_tables_from_pdf(pdf_path)
            print(f"  ✓ Extraídas {len(tables)} tablas")
            all_tables.extend(tables)

        print(f"\n{'='*60}")
        print(f"Extracción completada:")
        print(f"  - PDFs procesados: {len(pdf_files)}")
        print(f"  - Tablas extraídas: {len(all_tables)}")
        print(f"  - Errores: {len(self.errors)}")
        print(f"{'='*60}\n")

        # Normalizar datos
        print("Normalizando datos...")
        self.extracted_data = self.normalize_data(all_tables)
        print(f"  ✓ {len(self.extracted_data)} registros normalizados\n")

        return all_tables

    def save_to_csv(self, filename="precios_ganado.csv"):
        """Guarda los datos en formato CSV"""
        if not self.extracted_data:
            print("No hay datos para guardar")
            return

        df = pd.DataFrame(self.extracted_data)

        # Ordenar por fecha
        df = df.sort_values('fecha_desde').reset_index(drop=True)

        output_path = os.path.join(self.output_dir, filename)
        df.to_csv(output_path, index=False, encoding='utf-8')

        print(f"Datos guardados en: {output_path}")
        print(f"  - Registros: {len(df)}")
        print(f"  - Columnas: {list(df.columns)}")

        return output_path

    def save_to_sqlite(self, db_name="precios_ganado.db"):
        """Guarda los datos en una base de datos SQLite"""
        import sqlite3

        if not self.extracted_data:
            print("No hay datos para guardar")
            return

        df = pd.DataFrame(self.extracted_data)
        df = df.sort_values('fecha_desde').reset_index(drop=True)

        db_path = os.path.join(self.output_dir, db_name)
        conn = sqlite3.connect(db_path)

        # Guardar en tabla principal
        df.to_sql('precios_ganado', conn, if_exists='replace', index=False)

        # Crear índices para búsquedas eficientes
        cursor = conn.cursor()
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fecha_desde ON precios_ganado(fecha_desde)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fecha_hasta ON precios_ganado(fecha_hasta)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_lugar ON precios_ganado(lugar)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_categoria ON precios_ganado(categoria)
        ''')
        conn.commit()
        conn.close()

        print(f"Datos guardados en SQLite: {db_path}")
        print(f"  - Registros: {len(df)}")
        print(f"  - Tabla: precios_ganado")

        return db_path

    def generate_summary(self):
        """Genera un resumen de los datos extraídos"""
        if not self.extracted_data:
            return {}

        df = pd.DataFrame(self.extracted_data)

        summary = {
            'total_registros': len(df),
            'fecha_minima': df['fecha_desde'].min() if 'fecha_desde' in df.columns else None,
            'fecha_maxima': df['fecha_hasta'].max() if 'fecha_hasta' in df.columns else None,
            'lugares_unicos': df['lugar'].nunique() if 'lugar' in df.columns else 0,
            'categorias_unicas': df['categoria'].nunique() if 'categoria' in df.columns else 0,
            'precio_min': df['precio'].min() if 'precio' in df.columns else None,
            'precio_max': df['precio'].max() if 'precio' in df.columns else None,
            'precio_promedio': df['precio'].mean() if 'precio' in df.columns else None,
            'lugares': sorted(df['lugar'].unique().tolist()) if 'lugar' in df.columns else [],
            'categorias': sorted(df['categoria'].unique().tolist()) if 'categoria' in df.columns else [],
        }

        # Guardar resumen
        summary_path = os.path.join(self.output_dir, 'resumen.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

        print(f"\nResumen de datos:")
        print(f"{'='*60}")
        print(f"  Total de registros: {summary['total_registros']}")
        print(f"  Rango de fechas: {summary['fecha_minima']} a {summary['fecha_maxima']}")
        print(f"  Lugares únicos: {summary['lugares_unicos']}")
        print(f"  Categorías únicas: {summary['categorias_unicas']}")
        print(f"  Rango de precios: {summary['precio_min']:.2f} - {summary['precio_max']:.2f} (Promedio: {summary['precio_promedio']:.2f})")
        print(f"{'='*60}")

        return summary


def main():
    print("="*60)
    print("EXTRACTOR DE DATOS DE PDFs - PRECIOS DE GANADO")
    print("="*60)
    print()

    extractor = PDFDataExtractor()

    # Fase 1: Extraer datos de PDFs
    print("FASE 1: Extracción de tablas de PDFs")
    print("-"*60)
    tables = extractor.process_all_pdfs()

    if not tables:
        print("\nNo se encontraron tablas para procesar")
        return

    # Fase 2: Guardar datos
    print("\nFASE 2: Guardando datos")
    print("-"*60)

    # Decidir formato según tamaño
    if len(extractor.extracted_data) > 50000:
        print("Datos grandes detectados, usando SQLite...")
        extractor.save_to_sqlite()
    else:
        print("Guardando en CSV...")
        extractor.save_to_csv()

    # Fase 3: Generar resumen
    print("\nFASE 3: Generando resumen")
    print("-"*60)
    extractor.generate_summary()

    # Guardar errores si los hay
    if extractor.errors:
        errors_path = os.path.join(extractor.output_dir, 'errores.json')
        with open(errors_path, 'w', encoding='utf-8') as f:
            json.dump(extractor.errors, f, ensure_ascii=False, indent=2)
        print(f"\nErrores guardados en: {errors_path}")

    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)
    print(f"Directorio de salida: {extractor.output_dir}/")
    print()


if __name__ == "__main__":
    main()
