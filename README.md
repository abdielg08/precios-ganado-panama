# Sistema de Análisis de Precios de Ganado - Panamá

Sistema completo para scraping, extracción, almacenamiento y análisis de datos de precios de ganado desde [subastaganadera.com](https://subastaganadera.com/blog/).

## Características

- **Scraping automático**: Descarga todos los PDFs de reportes de precios del sitio web
- **Extracción inteligente**: Extrae tablas de los PDFs con reconocimiento automático de estructura
- **Base de datos estructurada**: Organiza los datos cronológicamente en CSV o SQLite
- **Dashboard interactivo**: Visualización y análisis en Jupyter Notebook con filtros dinámicos
- **Exportación flexible**: Descarga datos filtrados en CSV o Excel

## Estructura del Proyecto

```
precios_ganado_pty/
├── scraper.py              # Script para descargar PDFs
├── pdf_extractor.py        # Script para extraer datos de PDFs
├── dashboard.ipynb         # Dashboard interactivo de Jupyter
├── run_all.py             # Script principal para ejecutar todo
├── requirements.txt        # Dependencias del proyecto
├── pdfs/                  # Directorio de PDFs descargados
│   └── metadata.json      # Metadata de PDFs
├── data/                  # Directorio de datos procesados
│   ├── precios_ganado.csv # Base de datos en CSV
│   ├── precios_ganado.db  # Base de datos SQLite (si es grande)
│   └── resumen.json       # Resumen estadístico
└── README.md              # Este archivo
```

## Instalación

### 1. Requisitos del Sistema

- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- Java (para tabula-py, opcional)

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- `requests` y `beautifulsoup4`: Para web scraping
- `pdfplumber`: Para extracción de tablas de PDFs
- `pandas` y `numpy`: Para procesamiento de datos
- `plotly`: Para visualizaciones interactivas
- `jupyter` y `ipywidgets`: Para el dashboard
- `openpyxl`: Para exportar a Excel

## Uso

### Opción 1: Ejecutar Todo el Pipeline (Recomendado)

```bash
python3 run_all.py
```

Este script ejecutará automáticamente:
1. Descarga de todos los PDFs
2. Extracción y procesamiento de datos
3. Creación de base de datos
4. Lanzamiento del dashboard

### Opción 2: Ejecutar Paso por Paso

#### Paso 1: Descargar PDFs

```bash
python3 scraper.py
```

Esto descargará todos los PDFs en el directorio `pdfs/` y creará un archivo `metadata.json` con información sobre cada PDF.

#### Paso 2: Extraer Datos

```bash
python3 pdf_extractor.py
```

Esto procesará todos los PDFs y creará:
- `data/precios_ganado.csv` o `data/precios_ganado.db` (dependiendo del tamaño)
- `data/resumen.json` con estadísticas generales

#### Paso 3: Lanzar Dashboard

```bash
jupyter notebook dashboard.ipynb
```

Esto abrirá el dashboard interactivo en su navegador.

## Uso del Dashboard

El dashboard incluye las siguientes secciones:

### 1. Panel de Control

Filtros interactivos para:
- **Rango de fechas**: Seleccione período de análisis
- **Lugares**: Filtre por ferias o mercados específicos
- **Categorías**: Filtre por tipo de ganado
- **Rango de precios**: Defina límites mínimo y máximo

### 2. Visualizaciones

- **Evolución temporal**: Gráfico de líneas con precios promedio, máximo y mínimo
- **Precios por lugar**: Comparación entre diferentes mercados
- **Precios por categoría**: Análisis por tipo de ganado
- **Distribución de precios**: Box plots y histogramas
- **Mapa de calor**: Relación entre lugares y categorías
- **Tendencias mensuales**: Análisis de patrones temporales

### 3. Exportación de Datos

Botones para exportar datos filtrados:
- **CSV**: Para análisis adicional en Excel/Python
- **Excel**: Formato .xlsx con formato

### 4. Estadísticas

- Métricas descriptivas (media, mediana, desviación estándar)
- Top rankings por lugar y categoría
- Conteos y frecuencias

## Estructura de Datos

### Esquema de la Base de Datos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fecha_desde` | DATE | Fecha inicial del período de reporte |
| `fecha_hasta` | DATE | Fecha final del período de reporte |
| `lugar` | TEXT | Ubicación de la feria o mercado |
| `categoria` | TEXT | Tipo/categoría de ganado |
| `precio` | FLOAT | Precio en Balboas (B/.) |
| `fuente_pdf` | TEXT | Nombre del PDF fuente |
| `tipo_tabla` | TEXT | Tipo de tabla (por_lugar, por_categoria, general) |

### Ejemplo de Datos

```
fecha_desde  | fecha_hasta | lugar      | categoria  | precio | fuente_pdf
-------------|-------------|------------|------------|--------|------------------
2024-10-03   | 2024-10-07  | Divisa     | Novillo    | 1250.00| del-3-10-22.pdf
2024-10-03   | 2024-10-07  | Aguadulce  | Ternera    | 980.50 | del-3-10-22.pdf
```

## Personalización

### Modificar el Scraper

Edite `scraper.py` para:
- Cambiar el número máximo de páginas a rastrear (línea 277)
- Ajustar los delays entre requests (línea 210)
- Modificar patrones de búsqueda de PDFs

### Modificar el Extractor

Edite `pdf_extractor.py` para:
- Ajustar patrones de extracción de fechas (líneas 24-45)
- Modificar lógica de identificación de tablas (línea 81)
- Cambiar umbrales para CSV vs SQLite (línea 349)

### Personalizar el Dashboard

Edite `dashboard.ipynb` para:
- Agregar nuevas visualizaciones
- Modificar colores y estilos de gráficos
- Agregar análisis estadísticos adicionales

## Solución de Problemas

### Error: No se encuentran PDFs

**Problema**: El scraper no encuentra PDFs en el sitio web.

**Solución**:
1. Verifique su conexión a internet
2. Confirme que el sitio web esté accesible
3. Revise si la estructura del sitio ha cambiado

### Error: No se pueden extraer tablas

**Problema**: pdfplumber no puede extraer tablas de los PDFs.

**Soluciones**:
1. Verifique que los PDFs no estén protegidos
2. Intente con otro extractor (tabula-py)
3. Revise manualmente algunos PDFs para entender su estructura

### Error: Jupyter no inicia

**Problema**: `jupyter notebook` falla al iniciarse.

**Soluciones**:
```bash
# Reinstalar Jupyter
pip install --upgrade jupyter notebook

# O usar JupyterLab
pip install jupyterlab
jupyter lab dashboard.ipynb
```

### Problema: Datos inconsistentes

**Problema**: Los datos extraídos parecen incorrectos.

**Soluciones**:
1. Revise el archivo `data/errores.json` para ver qué PDFs fallaron
2. Examine manualmente algunos PDFs problemáticos
3. Ajuste los patrones de extracción en `pdf_extractor.py`

## Mantenimiento

### Actualizar Datos

Para mantener la base de datos actualizada:

```bash
# Ejecutar solo el scraper (descarga nuevos PDFs)
python3 scraper.py

# Ejecutar solo el extractor (procesa PDFs nuevos)
python3 pdf_extractor.py
```

### Limpiar Proyecto

Para limpiar archivos temporales y cache:

```bash
# Ejecutar script de limpieza automática
./limpiar_proyecto.sh
```

Este script:
- Crea un backup completo del proyecto
- Elimina cache de Python (__pycache__, *.pyc)
- Limpia checkpoints de Jupyter
- Verifica integridad del proyecto

Para más detalles sobre el proceso de limpieza, consulte [PROCESO_LIMPIEZA.md](PROCESO_LIMPIEZA.md)

### Limpiar Datos

```bash
# Eliminar PDFs descargados
rm -rf pdfs/

# Eliminar datos procesados
rm -rf data/
```

## Contribuir

Este es un proyecto de análisis de datos. Sugerencias de mejora:

1. **Mejoras al scraper**:
   - Implementar caché de URLs visitadas
   - Agregar validación de PDFs
   - Paralelizar descargas

2. **Mejoras al extractor**:
   - Usar OCR para PDFs escaneados
   - Implementar validación de datos extraídos
   - Agregar más patrones de reconocimiento

3. **Mejoras al dashboard**:
   - Agregar predicciones de precios
   - Implementar comparaciones año-a-año
   - Agregar exportación a otros formatos

## Licencia

Este proyecto es de código abierto y está disponible para uso educativo y de investigación.

## Contacto

Para preguntas, sugerencias o reportar problemas, por favor abra un issue en el repositorio del proyecto.

## Notas Importantes

- Los datos son extraídos automáticamente y pueden contener errores
- Siempre verifique los datos críticos con las fuentes originales
- Este sistema es para fines de análisis e investigación
- Respete los términos de servicio del sitio web fuente

---

**Última actualización**: Octubre 2024
**Versión**: 1.0.0
