#!/bin/bash
# Script para configurar el entorno virtual de Python para el análisis de precios de ganado

echo "=========================================================================="
echo "CONFIGURACIÓN DE ENTORNO VIRTUAL - ANÁLISIS DE PRECIOS DE GANADO"
echo "=========================================================================="
echo ""

# 1. Verificar Python
echo "1. Verificando Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Python3 no está instalado"
    exit 1
fi
echo "✓ Python3 disponible"
echo ""

# 2. Crear entorno virtual
echo "2. Creando entorno virtual..."
if [ -d "venv" ]; then
    echo "⚠ El directorio venv ya existe. ¿Desea eliminarlo y crear uno nuevo? (y/n)"
    read -p "Respuesta: " answer
    if [ "$answer" = "y" ]; then
        rm -rf venv
        echo "✓ Directorio venv eliminado"
    else
        echo "✓ Usando venv existente"
    fi
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Entorno virtual creado en ./venv"
else
    echo "✓ Entorno virtual ya existe"
fi
echo ""

# 3. Activar entorno virtual
echo "3. Activando entorno virtual..."
source venv/bin/activate
echo "✓ Entorno virtual activado"
echo "  Python: $(which python)"
echo "  Pip: $(which pip)"
echo ""

# 4. Actualizar pip
echo "4. Actualizando pip..."
pip install --upgrade pip setuptools wheel -q
echo "✓ Pip actualizado a versión: $(pip --version)"
echo ""

# 5. Instalar dependencias
echo "5. Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ ERROR al instalar dependencias"
    exit 1
fi
echo "✓ Todas las dependencias instaladas"
echo ""

# 6. Verificar instalación de paquetes clave
echo "6. Verificando paquetes instalados..."
python3 << 'EOF'
import sys
packages = [
    'pandas', 'numpy', 'pdfplumber',
    'plotly', 'scipy', 'matplotlib', 'seaborn',
    'jupyter', 'notebook', 'ipywidgets'
]

missing = []
for package in packages:
    try:
        __import__(package)
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} - NO INSTALADO")
        missing.append(package)

if missing:
    print(f"\n❌ Faltan paquetes: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\n✓ Todos los paquetes necesarios están instalados")
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERROR: Algunos paquetes no están instalados correctamente"
    exit 1
fi
echo ""

# 7. Registrar kernel de Jupyter
echo "7. Registrando kernel de Jupyter..."
python -m ipykernel install --user --name=precios_ganado --display-name="Python (Precios Ganado)"
if [ $? -eq 0 ]; then
    echo "✓ Kernel 'Python (Precios Ganado)' registrado"
else
    echo "⚠ No se pudo registrar el kernel (puede que ya exista)"
fi
echo ""

# 8. Listar kernels disponibles
echo "8. Kernels de Jupyter disponibles:"
jupyter kernelspec list
echo ""

# 9. Verificar archivos de datos
echo "9. Verificando archivos de datos..."
if [ -f "data/precios_ganado_sin_outliers.csv" ]; then
    echo "  ✓ data/precios_ganado_sin_outliers.csv"
    wc -l data/precios_ganado_sin_outliers.csv
elif [ -f "data/precios_ganado_clean.csv" ]; then
    echo "  ✓ data/precios_ganado_clean.csv"
    wc -l data/precios_ganado_clean.csv
else
    echo "  ⚠ No se encontraron archivos de datos limpios"
    echo "    Ejecute: python3 pdf_extractor_v2.py && python3 analisis_outliers.py"
fi
echo ""

# 10. Instrucciones finales
echo "=========================================================================="
echo "✅ ENTORNO CONFIGURADO EXITOSAMENTE"
echo "=========================================================================="
echo ""
echo "Para usar el entorno virtual:"
echo "  1. Activar: source venv/bin/activate"
echo "  2. Iniciar Jupyter: jupyter notebook"
echo "  3. Abrir: dashboard.ipynb"
echo "  4. Seleccionar kernel: Python (Precios Ganado)"
echo ""
echo "Para desactivar el entorno:"
echo "  deactivate"
echo ""
echo "Archivos importantes:"
echo "  - dashboard.ipynb: Dashboard interactivo"
echo "  - data/precios_ganado_sin_outliers.csv: Datos limpios"
echo "  - data/outliers_identificados.csv: Outliers identificados"
echo ""
