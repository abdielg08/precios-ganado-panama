#!/usr/bin/env python3
"""
Script para descargar todos los PDFs de reportes de precios de ganado
desde https://subastaganadera.com/blog/
"""

import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
import json

class SubastaGanaderaScraper:
    def __init__(self, base_url="https://subastaganadera.com/blog/", output_dir="pdfs"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.pdf_links = []
        self.metadata = []

        # Crear directorio de salida
        os.makedirs(self.output_dir, exist_ok=True)

    def get_page_content(self, url, retries=3):
        """Obtiene el contenido HTML de una página"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                print(f"Error obteniendo {url} (intento {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None

    def extract_pdf_links(self, html_content, page_url):
        """Extrae todos los enlaces a PDFs de una página"""
        soup = BeautifulSoup(html_content, 'html.parser')
        pdf_links = []

        # Buscar todos los enlaces
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Verificar si es un PDF
            if '.pdf' in href.lower():
                full_url = urljoin(page_url, href)
                pdf_links.append(full_url)

        # También buscar en iframes y embeds
        for iframe in soup.find_all(['iframe', 'embed']):
            src = iframe.get('src', '')
            if '.pdf' in src.lower():
                full_url = urljoin(page_url, src)
                pdf_links.append(full_url)

        return pdf_links

    def extract_metadata(self, html_content, page_url):
        """Extrae metadata de la página (fecha, título, categorías)"""
        soup = BeautifulSoup(html_content, 'html.parser')
        metadata = []

        # Buscar posts/artículos
        articles = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|article'))

        for article in articles:
            meta = {
                'url': page_url,
                'title': '',
                'date': '',
                'categories': [],
                'pdf_links': []
            }

            # Extraer título
            title_elem = article.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'title|heading'))
            if title_elem:
                meta['title'] = title_elem.get_text(strip=True)

            # Extraer fecha del título (formato: Del DD-MM-YY al DD-MM-YY)
            date_match = re.search(r'Del\s+(\d{1,2}-\d{1,2}-\d{2,4})\s+al\s+(\d{1,2}-\d{1,2}-\d{2,4})',
                                  meta['title'], re.IGNORECASE)
            if date_match:
                meta['date_from'] = date_match.group(1)
                meta['date_to'] = date_match.group(2)

            # Extraer fecha de publicación
            date_elem = article.find(['time', 'span'], class_=re.compile(r'date|time|published'))
            if date_elem:
                meta['published_date'] = date_elem.get_text(strip=True)

            # Extraer categorías
            cat_elems = article.find_all(['a', 'span'], class_=re.compile(r'categor|tag'))
            meta['categories'] = [cat.get_text(strip=True) for cat in cat_elems]

            # Buscar PDFs dentro del artículo
            for link in article.find_all('a', href=True):
                if '.pdf' in link['href'].lower():
                    meta['pdf_links'].append(urljoin(page_url, link['href']))

            if meta['pdf_links']:
                metadata.append(meta)

        return metadata

    def get_pagination_links(self, html_content, base_url):
        """Encuentra enlaces de paginación"""
        soup = BeautifulSoup(html_content, 'html.parser')
        page_links = set()

        # Buscar enlaces de paginación
        pagination = soup.find_all(['a', 'link'], href=re.compile(r'page|paged|/\d+/?$'))
        for link in pagination:
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                page_links.add(full_url)

        # También buscar patrones comunes de paginación
        for link in soup.find_all('a', href=True):
            href = link['href']
            if re.search(r'/page/\d+|paged=\d+|\?pg=\d+', href):
                full_url = urljoin(base_url, href)
                page_links.add(full_url)

        return list(page_links)

    def download_pdf(self, url, filename=None):
        """Descarga un archivo PDF"""
        try:
            if filename is None:
                # Generar nombre de archivo desde URL
                filename = os.path.basename(urlparse(url).path)
                if not filename or not filename.endswith('.pdf'):
                    filename = f"documento_{len(self.pdf_links)}.pdf"

            filepath = os.path.join(self.output_dir, filename)

            # Evitar descargar si ya existe
            if os.path.exists(filepath):
                print(f"  Ya existe: {filename}")
                return filepath

            print(f"  Descargando: {filename}")
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"  ✓ Descargado: {filename} ({os.path.getsize(filepath) / 1024:.1f} KB)")
            return filepath

        except Exception as e:
            print(f"  ✗ Error descargando {url}: {e}")
            return None

    def crawl_site(self, max_pages=100):
        """Rastrea el sitio completo buscando PDFs"""
        visited = set()
        to_visit = [self.base_url]

        print(f"Iniciando rastreo desde: {self.base_url}\n")

        page_count = 0
        while to_visit and page_count < max_pages:
            url = to_visit.pop(0)

            if url in visited:
                continue

            print(f"[{page_count + 1}] Analizando: {url}")
            visited.add(url)
            page_count += 1

            # Obtener contenido
            html = self.get_page_content(url)
            if not html:
                continue

            # Extraer PDFs
            pdf_links = self.extract_pdf_links(html, url)
            if pdf_links:
                print(f"  Encontrados {len(pdf_links)} PDFs")
                self.pdf_links.extend(pdf_links)

            # Extraer metadata
            metadata = self.extract_metadata(html, url)
            if metadata:
                print(f"  Extraída metadata de {len(metadata)} posts")
                self.metadata.extend(metadata)

            # Buscar más páginas (paginación)
            pagination = self.get_pagination_links(html, url)
            for page_link in pagination:
                if page_link not in visited and page_link not in to_visit:
                    # Solo seguir enlaces del mismo dominio
                    if urlparse(page_link).netloc == urlparse(self.base_url).netloc:
                        to_visit.append(page_link)

            # Delay para no sobrecargar el servidor
            time.sleep(1)

        # Eliminar duplicados
        self.pdf_links = list(set(self.pdf_links))
        print(f"\n{'='*60}")
        print(f"Rastreo completado:")
        print(f"  - Páginas visitadas: {len(visited)}")
        print(f"  - PDFs encontrados: {len(self.pdf_links)}")
        print(f"  - Posts con metadata: {len(self.metadata)}")
        print(f"{'='*60}\n")

    def download_all_pdfs(self):
        """Descarga todos los PDFs encontrados"""
        if not self.pdf_links:
            print("No se encontraron PDFs para descargar")
            return

        print(f"Descargando {len(self.pdf_links)} PDFs...\n")

        downloaded = []
        for i, pdf_url in enumerate(self.pdf_links, 1):
            print(f"[{i}/{len(self.pdf_links)}] {pdf_url}")
            filepath = self.download_pdf(pdf_url)
            if filepath:
                downloaded.append({
                    'url': pdf_url,
                    'filepath': filepath,
                    'filename': os.path.basename(filepath)
                })
            time.sleep(0.5)

        print(f"\n{'='*60}")
        print(f"Descarga completada: {len(downloaded)}/{len(self.pdf_links)} PDFs")
        print(f"{'='*60}\n")

        return downloaded

    def save_metadata(self, filename="metadata.json"):
        """Guarda la metadata recolectada"""
        metadata_file = os.path.join(self.output_dir, filename)

        data = {
            'scrape_date': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_pdfs': len(self.pdf_links),
            'pdf_links': self.pdf_links,
            'posts_metadata': self.metadata
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Metadata guardada en: {metadata_file}")
        return metadata_file


def main():
    print("="*60)
    print("SCRAPER DE PRECIOS DE GANADO - SUBASTA GANADERA")
    print("="*60)
    print()

    scraper = SubastaGanaderaScraper()

    # Fase 1: Rastrear el sitio
    print("FASE 1: Rastreo del sitio web")
    print("-"*60)
    scraper.crawl_site(max_pages=200)  # Aumentado para cubrir más páginas

    # Fase 2: Descargar PDFs
    print("\nFASE 2: Descarga de PDFs")
    print("-"*60)
    downloaded = scraper.download_all_pdfs()

    # Fase 3: Guardar metadata
    print("\nFASE 3: Guardando metadata")
    print("-"*60)
    scraper.save_metadata()

    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)
    print(f"Directorio de salida: {scraper.output_dir}/")
    print()


if __name__ == "__main__":
    main()
