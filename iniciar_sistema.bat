@echo off
chcp 65001 >nul
title SIGEC-EC v2.0 - Sistema Integral de Gestión de Cobranzas
color 0B

echo ===============================================================================
echo      SISTEMA INTEGRAL DE GESTIÓN ESTRATÉGICA DE COBRANZAS (SIGEC-EC v2.0)
echo            Entorno Local Interactivo, Predictivo y Neurocobranza
echo                     República del Ecuador - Cartera MYPE
echo ===============================================================================
echo.
echo [1/3] Verificando instalación de Python en el sistema...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se encontró Python en el PATH del sistema.
    echo Por favor instale Python 3.10 o superior y vuelva a ejecutar.
    pause
    exit /b 1
)
python --version

echo.
echo [2/3] Verificando módulos requeridos (streamlit, pandas, plotly, numpy)...
python -c "import streamlit, pandas, plotly, numpy" >nul 2>nul
if %errorlevel% neq 0 (
    echo [AVISO] Faltan módulos. Instalando dependencias necesarias...
    pip install streamlit pandas plotly numpy
) else (
    echo [OK] Todas las dependencias se encuentran instaladas correctamente.
)

echo.
echo [3/3] Iniciando servidor local en http://localhost:8501 ...
echo Presione Ctrl + C en esta ventana para detener el servidor.
echo.

start "" "http://localhost:8501"
streamlit run app_cobranzas.py --server.port=8501 --server.headless=true

pause

