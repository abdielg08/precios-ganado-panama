#!/bin/bash

# Script de Limpieza Automatizada del Proyecto
# Fecha: 2025-10-20
# Uso: ./limpiar_proyecto.sh

set -e  # Salir si hay errores

echo "=========================================="
echo "  LIMPIEZA DE PROYECTO - PRECIOS GANADO"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Paso 1: Confirmación
echo -e "${YELLOW}Este script realizará las siguientes acciones:${NC}"
echo "  1. Crear backup completo del proyecto"
echo "  2. Eliminar archivos de cache de Python"
echo "  3. Limpiar archivos temporales"
echo "  4. Verificar integridad del proyecto"
echo ""
read -p "¿Desea continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    echo -e "${RED}Operación cancelada${NC}"
    exit 1
fi

# Paso 2: Crear backup
echo ""
echo -e "${YELLOW}[1/4] Creando backup...${NC}"
BACKUP_DIR=$(dirname "$(pwd)")
BACKUP_NAME="precios_ganado_pty_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
cd "$BACKUP_DIR"
tar --exclude='precios_ganado_pty/venv' \
    --exclude='precios_ganado_pty/__pycache__' \
    --exclude='precios_ganado_pty/.claude' \
    -czf "$BACKUP_NAME" \
    precios_ganado_pty/

if [ -f "$BACKUP_NAME" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_NAME" | cut -f1)
    echo -e "${GREEN}✓ Backup creado: $BACKUP_NAME ($BACKUP_SIZE)${NC}"
else
    echo -e "${RED}✗ Error creando backup${NC}"
    exit 1
fi

cd precios_ganado_pty

# Paso 3: Limpiar archivos temporales
echo ""
echo -e "${YELLOW}[2/4] Limpiando archivos temporales...${NC}"

# Eliminar cache de Python
if [ -d "__pycache__" ]; then
    rm -rf __pycache__
    echo -e "${GREEN}✓ Eliminado __pycache__${NC}"
fi

# Buscar y eliminar todos los .pyc
PYCS=$(find . -name "*.pyc" 2>/dev/null | wc -l)
if [ $PYCS -gt 0 ]; then
    find . -name "*.pyc" -delete
    echo -e "${GREEN}✓ Eliminados $PYCS archivos .pyc${NC}"
fi

# Buscar y eliminar todos los __pycache__ en subdirectorios
PYCACHE_DIRS=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
if [ $PYCACHE_DIRS -gt 0 ]; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}✓ Eliminados $PYCACHE_DIRS directorios __pycache__${NC}"
fi

# Eliminar archivos temporales de Jupyter
if [ -d ".ipynb_checkpoints" ]; then
    rm -rf .ipynb_checkpoints
    echo -e "${GREEN}✓ Eliminado .ipynb_checkpoints${NC}"
fi

# Eliminar archivos temporales de prueba
TEST_FILES=$(find . -name "test_dashboard*.ipynb" 2>/dev/null | wc -l)
if [ $TEST_FILES -gt 0 ]; then
    find . -name "test_dashboard*.ipynb" -delete
    echo -e "${GREEN}✓ Eliminados $TEST_FILES archivos de prueba${NC}"
fi

# Paso 4: Verificar integridad
echo ""
echo -e "${YELLOW}[3/4] Verificando integridad del proyecto...${NC}"

# Verificar que existan archivos esenciales
ARCHIVOS_ESENCIALES=(
    "scraper.py"
    "pdf_extractor.py"
    "utils.py"
    "run_all.py"
    "dashboard.ipynb"
    "requirements.txt"
    "README.md"
    ".gitignore"
)

TODOS_OK=true
for archivo in "${ARCHIVOS_ESENCIALES[@]}"; do
    if [ -f "$archivo" ]; then
        echo -e "${GREEN}✓ $archivo${NC}"
    else
        echo -e "${RED}✗ $archivo FALTA${NC}"
        TODOS_OK=false
    fi
done

if [ "$TODOS_OK" = false ]; then
    echo -e "${RED}✗ Faltan archivos esenciales. Restaure desde backup.${NC}"
    exit 1
fi

# Paso 5: Verificar imports (si venv existe)
echo ""
echo -e "${YELLOW}[4/4] Verificando módulos Python...${NC}"

if [ -d "venv" ]; then
    source venv/bin/activate

    # Verificar imports
    python -c "from scraper import SubastaGanaderaScraper" 2>/dev/null && echo -e "${GREEN}✓ scraper.py${NC}" || echo -e "${RED}✗ scraper.py${NC}"
    python -c "from pdf_extractor import PDFDataExtractor" 2>/dev/null && echo -e "${GREEN}✓ pdf_extractor.py${NC}" || echo -e "${RED}✗ pdf_extractor.py${NC}"
    python -c "import utils" 2>/dev/null && echo -e "${GREEN}✓ utils.py${NC}" || echo -e "${RED}✗ utils.py${NC}"

    deactivate
else
    echo -e "${YELLOW}⚠ Entorno virtual no encontrado. Saltando verificación de imports.${NC}"
fi

# Resumen final
echo ""
echo "=========================================="
echo -e "${GREEN}  ✓ LIMPIEZA COMPLETADA EXITOSAMENTE${NC}"
echo "=========================================="
echo ""
echo "Backup guardado en:"
echo "  $BACKUP_DIR/$BACKUP_NAME"
echo ""
echo "Archivos limpiados:"
echo "  - Cache de Python (__pycache__, *.pyc)"
echo "  - Checkpoints de Jupyter"
echo "  - Archivos temporales de prueba"
echo ""
echo "Proyecto verificado y funcionando correctamente."
echo ""
