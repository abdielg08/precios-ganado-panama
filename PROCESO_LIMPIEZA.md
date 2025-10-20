# Proceso de Limpieza del Proyecto

Este documento describe el proceso de limpieza realizado el 2025-10-20 y sirve como guía para futuras limpiezas.

## Objetivo

Mantener el proyecto limpio, organizado y solo con los archivos necesarios para su funcionamiento, facilitando el mantenimiento y reduciendo el tamaño del repositorio.

## Archivos Core del Proyecto (MANTENER SIEMPRE)

Estos son los archivos esenciales para el funcionamiento del sistema:

### Scripts Python
- `scraper.py` - Scraper principal para descargar PDFs
- `pdf_extractor.py` - Extractor de datos de PDFs
- `utils.py` - Funciones utilitarias compartidas
- `run_all.py` - Script principal que orquesta todo el pipeline

### Notebooks
- `dashboard.ipynb` - Dashboard interactivo de Jupyter para análisis

### Configuración
- `requirements.txt` - Dependencias del proyecto
- `setup_environment.sh` - Script de configuración del entorno
- `.gitignore` - Archivos a ignorar en git
- `.vscode/settings.json` - Configuración de VS Code para el proyecto

### Documentación
- `README.md` - Documentación principal del proyecto
- `PROCESO_LIMPIEZA.md` - Este archivo (guía de limpieza)

### Directorios de Datos (mantener estructura, contenido según .gitignore)
- `pdfs/` - PDFs descargados (ignorado en git)
- `data/` - Datos procesados (ignorado en git)

### Entorno Virtual (ignorado en git)
- `venv/` - Entorno virtual Python

## Proceso de Limpieza

### Paso 1: Crear Backup Completo

Antes de cualquier limpieza, crear un backup completo:

```bash
cd /home/ec2-user/projects/bnp
tar --exclude='precios_ganado_pty/venv' \
    --exclude='precios_ganado_pty/__pycache__' \
    -czf precios_ganado_pty_backup_$(date +%Y%m%d).tar.gz \
    precios_ganado_pty/
```

El backup se guardará en el directorio padre del proyecto.

### Paso 2: Crear Carpeta de Backup Interno

Dentro del proyecto, crear una carpeta para archivos a eliminar:

```bash
mkdir -p _backup_archivos_viejos
```

### Paso 3: Identificar Archivos Innecesarios

**Criterios para identificar archivos innecesarios:**

1. **Versiones antiguas de scripts** (ej: `*_v2.py`, `*_final.py`, `*_completo.py`)
2. **Archivos de prueba/test** (ej: `test_*.py`, `example_*.py`)
3. **Logs temporales** (ej: `*.log`)
4. **Scripts de análisis específicos** que no son parte del core
5. **Documentación redundante** (si ya está cubierta en README.md)
6. **Cache de Python** (`__pycache__/`, `*.pyc`)

### Paso 4: Mover Archivos al Backup Interno

```bash
# Mover versiones antiguas de scripts
mv scraper_v2.py scraper_completo.py scraper_final.py scraper_gdrive.py _backup_archivos_viejos/
mv pdf_extractor_v2.py _backup_archivos_viejos/

# Mover archivos de prueba y ejemplos
mv example_usage.py test_pdf_analysis.py test_single_page.py _backup_archivos_viejos/

# Mover scripts de análisis específicos
mv analisis_outliers.py _backup_archivos_viejos/

# Mover logs
mv *.log _backup_archivos_viejos/

# Mover documentación redundante
mv INSTRUCCIONES_JUPYTER.md _backup_archivos_viejos/

# Eliminar cache de Python
rm -rf __pycache__
```

### Paso 5: Verificar Funcionamiento

Después de la limpieza, verificar que todo funciona:

```bash
# Activar entorno virtual
source venv/bin/activate

# Verificar imports de scripts principales
python -c "from scraper import SubastaGanaderaScraper; print('✓ scraper.py OK')"
python -c "from pdf_extractor import PDFDataExtractor; print('✓ pdf_extractor.py OK')"
python -c "import utils; print('✓ utils.py OK')"

# Verificar que run_all.py inicia correctamente
python run_all.py --help

# Verificar que el dashboard se puede ejecutar
jupyter nbconvert --to notebook --execute dashboard.ipynb --output test_dashboard.ipynb
rm test_dashboard.ipynb
```

### Paso 6: Revisar Estructura Final

Verificar que la estructura final es limpia:

```bash
ls -la
```

**Estructura esperada:**
```
.
├── .claude/
├── .gitignore
├── .vscode/
│   └── settings.json
├── README.md
├── PROCESO_LIMPIEZA.md
├── _backup_archivos_viejos/    # Carpeta con archivos movidos
├── dashboard.ipynb
├── data/                       # Datos procesados
├── pdf_extractor.py
├── pdfs/                       # PDFs descargados
├── requirements.txt
├── run_all.py
├── scraper.py
├── setup_environment.sh
├── utils.py
└── venv/                       # Entorno virtual
```

## Limpieza de Archivos en Backup Interno

Después de verificar que todo funciona correctamente durante **al menos 1 semana**, se puede eliminar permanentemente la carpeta de backup:

```bash
# SOLO después de verificar que todo funciona bien
rm -rf _backup_archivos_viejos/
```

## Checklist de Limpieza

Usar esta checklist en cada limpieza:

- [ ] Crear backup completo externo (.tar.gz)
- [ ] Crear carpeta `_backup_archivos_viejos/`
- [ ] Identificar archivos innecesarios
- [ ] Mover archivos a backup interno
- [ ] Eliminar `__pycache__/`
- [ ] Verificar imports de scripts principales
- [ ] Verificar ejecución de `run_all.py`
- [ ] Verificar dashboard de Jupyter
- [ ] Documentar cambios (si hay nuevos tipos de archivos)
- [ ] Esperar 1 semana antes de eliminar backup interno

## Archivos que NUNCA se deben eliminar

- `scraper.py`
- `pdf_extractor.py`
- `utils.py`
- `run_all.py`
- `dashboard.ipynb`
- `requirements.txt`
- `README.md`
- `.gitignore`
- Directorios: `data/`, `pdfs/`, `venv/`

## Notas Importantes

1. **Siempre crear backup antes de limpiar**
2. **Verificar funcionamiento después de limpiar**
3. **No eliminar archivos de backup interno inmediatamente**
4. **Documentar cualquier archivo nuevo que se agregue al proyecto**
5. **Actualizar este documento si cambia la estructura del proyecto**

## Historial de Limpiezas

### 2025-10-20 - Limpieza Inicial
- **Archivos eliminados**: 9 scripts Python antiguos, 5 archivos log, 1 archivo de documentación
- **Espacio liberado**: ~200KB de código, ~100KB de logs
- **Resultado**: ✓ Todos los tests pasaron correctamente

---

**Última actualización**: 2025-10-20
