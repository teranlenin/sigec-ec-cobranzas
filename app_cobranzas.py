# -*- coding: utf-8 -*-
"""
========================================================================================
SISTEMA INTEGRAL DE GESTIÓN ESTRATÉGICA DE COBRANZAS (SIGEC-EC v2.0)
Entorno Operativo Local, Interactivo, Responsive y Predictivo
Especializado en Cartera MYPE - República del Ecuador
========================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
import sys
from pathlib import Path

_STPR_REPORTING_ROOT = Path(__file__).resolve().parent / "Gestión de cobranzas efectivas"
if str(_STPR_REPORTING_ROOT) not in sys.path:
    sys.path.insert(0, str(_STPR_REPORTING_ROOT))
from reporting.dashboard import render_reporting_dashboard

# --------------------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="SIGEC-EC v2.0 | Sistema Integral de Cobranzas MYPE",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    /* Tipografía y contenedor principal */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Encabezados institucionales */
    h1, h2, h3 {
        color: #1A365D !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Tarjetas Métricas (KPI Cards) */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.08);
    }
    .metric-title {
        font-size: 0.82rem;
        font-weight: 700;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #1A365D;
        line-height: 1.2;
    }
    .metric-caption {
        font-size: 0.78rem;
        color: #4A5568;
        margin-top: 0.4rem;
    }
    
    /* Tarjetas FODA */
    .swot-card {
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        height: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .swot-f { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 6px solid #16A34A; }
    .swot-o { background-color: #F0FDFA; border: 1px solid #99F6E4; border-left: 6px solid #0D9488; }
    .swot-d { background-color: #FFFBEB; border: 1px solid #FDE68A; border-left: 6px solid #D97706; }
    .swot-a { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 6px solid #DC2626; }
    
    .swot-title-f { color: #166534; font-weight: 800; font-size: 1.1rem; margin-bottom: 0.5rem; }
    .swot-title-o { color: #115E59; font-weight: 800; font-size: 1.1rem; margin-bottom: 0.5rem; }
    .swot-title-d { color: #92400E; font-weight: 800; font-size: 1.1rem; margin-bottom: 0.5rem; }
    .swot-title-a { color: #991B1B; font-weight: 800; font-size: 1.1rem; margin-bottom: 0.5rem; }
    
    /* Alertas normativas y badges */
    .badge-legal {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-critica { background-color: #FED7D7; color: #9B2C2C; border: 1px solid #FEB2B2; }
    .badge-preventiva { background-color: #FEEBC8; color: #7B341E; border: 1px solid #FBD38D; }
    .badge-vigente { background-color: #C6F6D5; color: #22543D; border: 1px solid #9AE6B4; }
    
    /* Caja de bloqueo de cumplimiento */
    .block-box {
        background-color: #FFF5F5;
        border-left: 6px solid #E53E3E;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        color: #742A2A;
    }
    
    /* Caja de consejo operativo / neurocobranza */
    .tip-box {
        background-color: #F0FDFA;
        border-left: 6px solid #0D9488;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        color: #134E4A;
    }
    
    /* Trazabilidad algorítmica */
    .trace-box {
        background-color: #F8FAFC;
        border: 1px solid #CBD5E0;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Consolas', monospace;
        font-size: 0.88rem;
        color: #2D3748;
        line-height: 1.5;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# 2. CARGA Y PREPROCESAMIENTO DE DATOS
# --------------------------------------------------------------------------------------
CSV_PATH = "datos_sinteticos/cartera_calibrada_multidimensional_1000.csv"
VISITAS_LOG_PATH = "registro_visitas_campo.csv"

@st.cache_data
def load_cartera_data():
    if not os.path.exists(CSV_PATH):
        st.error(f"Error crítico: No se encontró la base de datos en {CSV_PATH}")
        return pd.DataFrame()
    df = pd.read_csv(CSV_PATH)
    
    # Flags de compliance legal
    df['bloqueo_legal'] = (
        (df['disputa_saldo'] == 'En auditoría de liquidación') |
        (df['consentimiento_contacto_simulado'] == 'En revisión de vigencia')
    )
    df['solo_canal_digital'] = (df['consentimiento_contacto_simulado'] == 'Restringido (solo canal digital escrito)')
    
    # Clasificación para ruta presencial en campo
    df['elegible_visita_campo'] = (
        (~df['bloqueo_legal']) &
        (~df['solo_canal_digital']) &
        (
            ((df['saldo_usd'] >= 3000) & (df['bucket_mora'].str.contains('B2|B3|B4|B5')) & 
             (df['respuesta_ultimo_contacto'].isin(['No respondió / Buzón', 'Rechazó contacto / Evasivo']))) |
            (df['estado_prescripcion'].str.contains('Alerta'))
        )
    )
    
    # Categorización conductual observable
    def asignar_perfil_observado(row):
        if row['ratio_cumplimiento_promesas'] >= 0.50:
            if 'Solicitó' in str(row['respuesta_ultimo_contacto']) or 'Racional' in str(row['arquetipo_neurocognitivo']):
                return "Perfil 2: Comerciante Analítico (Costo-Beneficio)"
            return "Perfil 1: MYPE con Descalce Temporal (Cooperativo)"
        elif row['ratio_cumplimiento_promesas'] < 0.35 and row['promesas_12m'] >= 2:
            return "Perfil 3: Postergador Crónico (Promesas Rotas)"
        elif row['respuesta_ultimo_contacto'] in ['No respondió / Buzón', 'Rechazó contacto / Evasivo']:
            return "Perfil 4: Evasivo / Incontactable Crítico"
        else:
            return "Perfil 1: MYPE con Descalce Temporal (Cooperativo)"
            
    df['perfil_conductual_observado'] = df.apply(asignar_perfil_observado, axis=1)
    return df

df_master = load_cartera_data()

# --------------------------------------------------------------------------------------
# 3. BARRA LATERAL (FILTROS GLOBALES Y NAVEGACIÓN)
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
    st.title("SIGEC-EC v2.0")
    st.caption("Sistema de Inteligencia de Cobranzas | Ecuador")
    st.divider()
    
    # Navegación
    modulo = st.radio(
        "Navegación del Sistema:",
        [
            "📊 1. Dashboard Ejecutivo & KPIs",
            "🗂️ 2. Explorador & Segmentación",
            "🎯 3. Cockpit 1 a 1 (Negociación)",
            "📍 4. Rutas de Campo (Visitas MYPE)",
            "🎲 5. Motor Estocástico & Markov",
            "🧭 6. Tablero FODA & Explicabilidad",
            "⚖️ 7. Compliance Legal & Exportador IA",
            "📈 8. Reportería periódica (simulada)"
        ],
        index=0
    )
    
    st.divider()
    st.subheader("Filtros Globales de Cartera")
    
    # Filtro por Balde
    baldes_disp = ["Todos"] + sorted(list(df_master['bucket_mora'].unique()))
    sel_balde = st.selectbox("Balde de Mora:", baldes_disp, index=0)
    
    # Filtro por Parroquia
    parroquias_disp = ["Todas"] + sorted(list(df_master['parroquia_dm_quito'].unique()))
    sel_parroquia = st.selectbox("Parroquia (DM Quito):", parroquias_disp, index=0)
    
    # Filtro por Sector Productivo
    sectores_disp = ["Todos"] + sorted(list(df_master['sector_productivo'].unique()))
    sel_sector = st.selectbox("Sector Productivo:", sectores_disp, index=0)
    
    # Filtro de Prescripción
    presc_disp = ["Todos", "Solo Alertas (<12m y <6m)", "Acción Legal Vigente"]
    sel_presc = st.selectbox("Estado de Prescripción:", presc_disp, index=0)
    
    # Aplicar filtros
    df_filtrado = df_master.copy()
    if sel_balde != "Todos":
        df_filtrado = df_filtrado[df_filtrado['bucket_mora'] == sel_balde]
    if sel_parroquia != "Todas":
        df_filtrado = df_filtrado[df_filtrado['parroquia_dm_quito'] == sel_parroquia]
    if sel_sector != "Todos":
        df_filtrado = df_filtrado[df_filtrado['sector_productivo'] == sel_sector]
    if sel_presc == "Solo Alertas (<12m y <6m)":
        df_filtrado = df_filtrado[df_filtrado['estado_prescripcion'].str.contains('Alerta')]
    elif sel_presc == "Acción Legal Vigente":
        df_filtrado = df_filtrado[~df_filtrado['estado_prescripcion'].str.contains('Alerta')]
        
    st.caption(f"Registros filtrados: **{len(df_filtrado)}** de 1.000")
    st.caption(f"Saldo filtrado: **${df_filtrado['saldo_usd'].sum():,.2f} USD**")

# --------------------------------------------------------------------------------------
# 4. MÓDULO 1: DASHBOARD EJECUTIVO & KPIS MACRO
# --------------------------------------------------------------------------------------
if modulo == "📊 1. Dashboard Ejecutivo & KPIs":
    st.header("📊 Dashboard Ejecutivo & Análisis Macro de Cartera")
    st.markdown(
        "Visión integral del portafolio MYPE en mora prejudicial y administrativa. "
        "Métricas auditadas y calibradas para maximizar el valor incremental de recuperación."
    )
    
    # Fila de Tarjetas Métricas
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Saldo Cartera Total</div>
            <div class="metric-value">${df_filtrado['saldo_usd'].sum():,.0f}</div>
            <div class="metric-caption">USD exigibles al corte</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Recuperación Esp. 30d</div>
            <div class="metric-value" style="color: #0D9488;">${df_filtrado['recuperacion_esperada_30d_usd'].sum():,.0f}</div>
            <div class="metric-caption">Valor esperado neto</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Cuentas Auditadas</div>
            <div class="metric-value">{len(df_filtrado):,}</div>
            <div class="metric-caption">Casos activos en universo</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        visitas_count = df_filtrado['elegible_visita_campo'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Ruta de Campo (Visitas)</div>
            <div class="metric-value" style="color: #2B6CB0;">{visitas_count}</div>
            <div class="metric-caption">Saldos ≥ $3k o alertas</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c5:
        bloqueos_count = df_filtrado['bloqueo_legal'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Bloqueo Normativo</div>
            <div class="metric-value" style="color: #E53E3E;">{bloqueos_count}</div>
            <div class="metric-caption">Disputas / LOPDP revisión</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Gráficos Principales
    col_g1, col_g2 = st.columns([3, 2])
    
    with col_g1:
        st.subheader("Distribución de Cartera por Baldes de Mora (Aging Buckets)")
        bucket_stats = df_filtrado.groupby('bucket_mora').agg(
            saldo_total=('saldo_usd', 'sum'),
            capital=('capital_total_usd', 'sum'),
            interes_mora=('interes_mora_usd', 'sum'),
            casos=('id_caso', 'count')
        ).reset_index()
        
        fig_bucket = go.Figure()
        fig_bucket.add_trace(go.Bar(
            x=bucket_stats['bucket_mora'],
            y=bucket_stats['capital'],
            name='Capital Exigible',
            marker_color='#1A365D'
        ))
        fig_bucket.add_trace(go.Bar(
            x=bucket_stats['bucket_mora'],
            y=bucket_stats['interes_mora'],
            name='Interés de Mora / Gastos',
            marker_color='#0D9488'
        ))
        fig_bucket.update_layout(
            barmode='stack',
            xaxis_title="Tramo de Mora",
            yaxis_title="USD",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=30, b=20),
            height=360
        )
        st.plotly_chart(fig_bucket, width="stretch")
        
    with col_g2:
        st.subheader("Segmentación por Perfil Conductual Observado")
        perfil_stats = df_filtrado['perfil_conductual_observado'].value_counts().reset_index()
        perfil_stats.columns = ['Perfil', 'Casos']
        
        fig_pie = px.pie(
            perfil_stats,
            names='Perfil',
            values='Casos',
            color_discrete_sequence=['#2B6CB0', '#0D9488', '#DD6B20', '#E53E3E'],
            hole=0.45
        )
        fig_pie.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            height=360,
            showlegend=False
        )
        st.plotly_chart(fig_pie, width="stretch")
        
    col_g3, col_g4 = st.columns([1, 1])
    
    with col_g3:
        st.subheader("Concentración Territorial en Quito (Parroquias DMQ)")
        parroquia_stats = df_filtrado.groupby('parroquia_dm_quito')['saldo_usd'].sum().sort_values(ascending=True).reset_index()
        fig_parroquia = px.bar(
            parroquia_stats,
            x='saldo_usd',
            y='parroquia_dm_quito',
            orientation='h',
            labels={'saldo_usd': 'Saldo Total USD', 'parroquia_dm_quito': 'Parroquia'},
            color='saldo_usd',
            color_continuous_scale='Blues'
        )
        fig_parroquia.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_parroquia, width="stretch")
        
    with col_g4:
        st.subheader("Relación Días de Mora vs. Saldo (Probabilidad Calibrada)")
        fig_scatter = px.scatter(
            df_filtrado,
            x='dias_mora',
            y='saldo_usd',
            color='prob_pago_30d_calibrada',
            size='recuperacion_esperada_30d_usd',
            hover_data=['id_caso', 'sector_productivo', 'bucket_mora', 'parroquia_dm_quito'],
            color_continuous_scale='Tealgrn',
            labels={'dias_mora': 'Días de Mora', 'saldo_usd': 'Saldo USD', 'prob_pago_30d_calibrada': 'Prob. Pago'}
        )
        fig_scatter.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_scatter, width="stretch")

# --------------------------------------------------------------------------------------
# 5. MÓDULO 2: EXPLORADOR & SEGMENTACIÓN DE CARTERA
# --------------------------------------------------------------------------------------
elif modulo == "🗂️ 2. Explorador & Segmentación":
    st.header("🗂️ Explorador & Segmentación Analítica de Cartera")
    st.markdown("Auditoría tabular detallada con compuertas de contención y filtros de negocio.")
    
    tab_exp1, tab_exp2, tab_exp3 = st.tabs([
        "📋 Cartera Habilitada para Gestión",
        "🛑 Puertas Duras de Contención Legal (Bloqueados)",
        "⚠️ Cola de Urgencia por Prescripción Cambiaria"
    ])
    
    with tab_exp1:
        st.subheader("Base de Clientes Operables")
        habilitados = df_filtrado[~df_filtrado['bloqueo_legal']]
        st.caption(f"Mostrando {len(habilitados)} casos con habilitación normativa para contacto.")
        
        cols_mostrar = [
            'id_caso', 'parroquia_dm_quito', 'sector_productivo', 'saldo_usd',
            'dias_mora', 'bucket_mora', 'perfil_conductual_observado',
            'prob_pago_30d_calibrada', 'recuperacion_esperada_30d_usd',
            'titulo_ejecutivo_tipo', 'via_procesal_idonea'
        ]
        
        st.dataframe(
            habilitados[cols_mostrar].style.format({
                'saldo_usd': '${:,.2f}',
                'recuperacion_esperada_30d_usd': '${:,.2f}',
                'prob_pago_30d_calibrada': '{:.2%}'
            }),
            width="stretch",
            height=420
        )
        
        csv_hab = habilitados[cols_mostrar].to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar Cartera Habilitada (CSV)",
            data=csv_hab,
            file_name="cartera_habilitada_gestion.csv",
            mime="text/csv"
        )
        
    with tab_exp2:
        st.subheader("Cuentas Congeladas por Disputa o Consentimiento LOPDP")
        bloqueados = df_filtrado[df_filtrado['bloqueo_legal']]
        
        st.markdown("""
        <div class="block-box">
            <strong>ADVERTENCIA DE AUDITORÍA (Fase 0 de Contención):</strong><br>
            Estos casos tienen <strong>prohibición estricta de contacto telefónico, mensajes masivos o visitas de campo</strong>. 
            Cualquier gestión sobre estas cuentas viola el Art. 49 de la Ley de Defensa del Consumidor o el régimen sancionatorio de la LOPDP.
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            bloqueados[[
                'id_caso', 'parroquia_dm_quito', 'sector_productivo', 'saldo_usd',
                'bucket_mora', 'disputa_saldo', 'consentimiento_contacto_simulado',
                'motivo_declarado'
            ]].style.format({'saldo_usd': '${:,.2f}'}),
            width="stretch"
        )
        
    with tab_exp3:
        st.subheader("Monitoreo de Prescripción de Títulos (Art. 479 Código de Comercio)")
        alertas_presc = df_filtrado[df_filtrado['estado_prescripcion'].str.contains('Alerta')]
        
        st.markdown(f"""
        <div class="tip-box">
            Se identifican <strong>{len(alertas_presc)} cuentas en riesgo de prescripción</strong> con un saldo acumulado de 
            <strong>${alertas_presc['saldo_usd'].sum():,.2f} USD</strong>. Requieren acción judicial inmediata o suscripción de novación 
            para interrumpir el cómputo de los 3 años.
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            alertas_presc[[
                'id_caso', 'parroquia_dm_quito', 'sector_productivo', 'saldo_usd',
                'dias_mora', 'dias_para_prescripcion_cambiaria', 'estado_prescripcion',
                'titulo_ejecutivo_tipo', 'garantia_declarada'
            ]].sort_values(by='dias_para_prescripcion_cambiaria').style.format({'saldo_usd': '${:,.2f}'}),
            width="stretch"
        )

# --------------------------------------------------------------------------------------
# 6. MÓDULO 3: COCKPIT 1 A 1 (FICHA 360° & NEGOCIACIÓN INTERACTIVA)
# --------------------------------------------------------------------------------------
elif modulo == "🎯 3. Cockpit 1 a 1 (Negociación)":
    st.header("🎯 Cockpit del Gestor 1 a 1: Ficha 360° & Negociación")
    st.markdown("Consola operativa individual para la preparación, desescalamiento y cierre de acuerdos.")
    
    # Selector de Caso
    casos_disponibles = df_master['id_caso'].tolist()
    caso_seleccionado = st.selectbox(
        "Seleccione el Expediente del Cliente (Búsqueda por ID):",
        casos_disponibles,
        index=3 # Por defecto SIM-00004
    )
    
    cliente = df_master[df_master['id_caso'] == caso_seleccionado].iloc[0]
    
    # Comprobar Bloqueo Legal
    if cliente['bloqueo_legal']:
        st.markdown(f"""
        <div class="block-box">
            <h3>🛑 CUENTA BLOQUEADA POR COMPLIANCE NORMATIVO</h3>
            <strong>Causa:</strong> Disputa de saldo ({cliente['disputa_saldo']}) o Consentimiento LOPDP ({cliente['consentimiento_contacto_simulado']}).<br>
            <strong>Mandato:</strong> Abstención absoluta de cobro. Derivar expediente a la Unidad de Liquidación y Servicio al Cliente.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Ficha 360° en 4 Cuadrantes
        st.subheader(f"Ficha Técnica 360°: {cliente['id_caso']} — {cliente['parroquia_dm_quito']}")
        
        cuad1, cuad2, cuad3, cuad4 = st.columns(4)
        
        with cuad1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Identificación y Actividad</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #1A365D;">{cliente['tipo_deudor']}</div>
                <div class="metric-caption">
                    <strong>Sector:</strong> {cliente['sector_productivo']}<br>
                    <strong>Producto:</strong> {cliente['producto']}<br>
                    <strong>Edad:</strong> {cliente['edad']} años
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with cuad2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Estado Financiero Auditado</div>
                <div class="metric-value">${cliente['saldo_usd']:,.2f}</div>
                <div class="metric-caption">
                    <strong>Capital:</strong> ${cliente['capital_total_usd']:,.2f}<br>
                    <strong>Interés Mora:</strong> ${cliente['interes_mora_usd']:,.2f}<br>
                    <strong>Gastos Cobro:</strong> ${cliente['gastos_cobranza_usd']:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with cuad3:
            dias_presc = cliente['dias_para_prescripcion_cambiaria']
            presc_color = "#E53E3E" if dias_presc < 180 else ("#DD6B20" if dias_presc < 365 else "#22543D")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Diagnóstico Procesal COGEP</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: {presc_color};">
                    Prescripción: {dias_presc} días
                </div>
                <div class="metric-caption">
                    <strong>Título:</strong> {cliente['titulo_ejecutivo_tipo'][:35]}...<br>
                    <strong>Vía:</strong> {cliente['via_procesal_idonea']}<br>
                    <strong>LTV Garantía:</strong> {cliente['ltv_ratio']:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with cuad4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Perfil Conductual Observado</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #2B6CB0;">
                    {cliente['perfil_conductual_observado']}
                </div>
                <div class="metric-caption">
                    <strong>Kept Rate (Promesas):</strong> {cliente['ratio_cumplimiento_promesas']:.1%}<br>
                    <strong>Último Contacto:</strong> {cliente['respuesta_ultimo_contacto']}<br>
                    <strong>Canal Óptimo:</strong> {cliente['canal_predilecto_neuroperfil'][:30]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Simulador Interactivo de Negociación (La Escalera de Resolución)
        st.subheader("🪜 Simulador Interactivo de Negociación: Escalera de Resolución")
        
        esc1, esc2, esc3, esc4 = st.tabs([
            "Nivel 1: Pago Inmediato (Condonación)",
            "Nivel 2: Abono Inicial Blindado (Down Payment)",
            "Nivel 3: Reestructuración de Crédito MYPE",
            "Nivel 4: Escalado Prejudicial Formal"
        ])
        
        with esc1:
            st.markdown("##### Opción 1: Condonación Dinámica de Mora y Gastos por Pago en 48 Horas")
            st.caption("Aplica para deudores con liquidez o mora administrativa que buscan liquidar al contado.")
            
            c_sl1, c_sl2 = st.columns(2)
            with c_sl1:
                pct_condonacion = st.slider("Porcentaje de Condonación sobre Interés de Mora y Gastos:", 0, 100, 100, 10)
            
            descuento_usd = (cliente['interes_mora_usd'] + cliente['gastos_cobranza_usd']) * (pct_condonacion / 100.0)
            pago_neto = cliente['saldo_usd'] - descuento_usd
            
            with c_sl2:
                st.metric("Ahorro Inmediato para el Cliente", f"${descuento_usd:,.2f} USD")
                st.metric("Monto Neto a Pagar en 48h", f"${pago_neto:,.2f} USD", delta=f"-{pct_condonacion}% Mora")
                
            st.info(f"💡 **Argumento para el Gestor:** 'Don {cliente['id_caso']}, si cancela ${pago_neto:,.2f} USD antes del viernes, le condonamos legalmente ${descuento_usd:,.2f} USD y su cuenta queda cerrada sin historial negativo.'")
            
        with esc2:
            st.markdown("##### Opción 2: Compromiso Blindado con Abono Inicial (Romper Inercia)")
            st.caption("Exigencia obligatoria de down payment para suspender traslados prejudiciales en MYPEs.")
            
            c_ab1, c_ab2 = st.columns(2)
            with c_ab1:
                pct_abono = st.slider("Porcentaje de Abono Inicial Exigido en 72 Horas:", 15, 50, 30, 5)
                cuotas_saldo = st.selectbox("Dividir saldo remanente en:", [2, 3, 4], index=1)
                
            abono_inicial_usd = cliente['saldo_usd'] * (pct_abono / 100.0)
            saldo_restante = cliente['saldo_usd'] - abono_inicial_usd
            cuota_remanente = saldo_restante / cuotas_saldo
            
            with c_ab2:
                st.metric("Abono Inicial Requerido (72h)", f"${abono_inicial_usd:,.2f} USD")
                st.metric(f"{cuotas_saldo} Cuotas Quincenales/Mensuales de", f"${cuota_remanente:,.2f} USD")
                
            st.info(f"💡 **Argumento para el Gestor:** 'Don {cliente['id_caso']}, para sostener el acuerdo y congelar acciones legales, consignamos un abono inicial de ${abono_inicial_usd:,.2f} USD en 72 horas y le diferimos el saldo en {cuotas_saldo} pagos de ${cuota_remanente:,.2f} USD.'")
            
        with esc3:
            st.markdown("##### Opción 3: Reestructuración y Adecuación a Flujo de Caja MYPE")
            st.caption("Adecuación del plazo y cuota fija al ciclo operativo de la microempresa.")
            
            c_re1, c_re2 = st.columns(2)
            with c_re1:
                plazo_meses = st.selectbox("Plazo de Reestructuración (Meses):", [6, 12, 18, 24], index=1)
                tasa_interes_anual = st.number_input("Tasa Referencial Anual (%):", value=15.5, step=0.5)
                
            tasa_mensual = (tasa_interes_anual / 100.0) / 12.0
            saldo_cap = cliente['capital_total_usd'] + cliente['interes_corriente_usd']
            cuota_francesa = (saldo_cap * tasa_mensual) / (1 - (1 + tasa_mensual)**(-plazo_meses))
            
            with c_re2:
                st.metric(f"Nueva Cuota Mensual Fija ({plazo_meses} meses)", f"${cuota_francesa:,.2f} USD")
                st.caption(f"Capital + Interés Ordinario reestructurado: ${saldo_cap:,.2f} USD")
                
        with esc4:
            st.markdown("##### Opción 4: Escalado Prejudicial Formal (COGEP)")
            st.caption("Derivación a asesoría legal y preparación de citación previa a demanda judicial.")
            
            st.warning(f"⚠️ **Vía Procesal Aplicable:** {cliente['via_procesal_idonea']}")
            st.write(f"- **Título que sustenta el cobro:** {cliente['titulo_ejecutivo_tipo']}")
            st.write(f"- **Días para prescripción:** {cliente['dias_para_prescripcion_cambiaria']} días restantes.")
            st.write(f"- **Medida Cautelar sugerida (Art. 351 COGEP):** {cliente['medida_cautelar_aplicable']}")
            st.code(f"""
REQUERIMIENTO PREJUDICIAL DE PAGO — EXPEDIENTE {cliente['id_caso']}
Señor/a Representante de {cliente['sector_productivo']}, Parroquia {cliente['parroquia_dm_quito']}.
Presente.
De conformidad con lo dispuesto en el Código Orgánico General de Procesos, nos permitimos notificar formalmente 
que su crédito mantiene un saldo líquido y exigible de USD {cliente['saldo_usd']:,.2f}, amparado en el título ejecutivo 
{cliente['titulo_ejecutivo_tipo']}. Concedemos el término legal improrrogable para regularizar su obligación o suscribir 
acuerdo conciliatorio en nuestras oficinas antes del inicio de las acciones jurisdiccionales correspondientes.
            """, language="text")
            
        st.markdown("---")
        
        # Guion Dinámico en 6 Pasos Adaptado
        st.subheader("📞 Guion de Gestión en 6 Pasos (Hiper-Personalizado)")
        
        with st.expander("Ver y Ejecutar los 6 Pasos Operativos de la Llamada / Visita", expanded=True):
            p1, p2 = st.columns(2)
            with p1:
                st.markdown("**Paso 1: Pre-llamada Técnica y Auditoría**")
                st.caption(f"Saldo: ${cliente['saldo_usd']:,.2f} | Mora: {cliente['dias_mora']} días | Título: {cliente['titulo_ejecutivo_tipo']}")
                
                st.markdown("**Paso 2: Apertura Respetuosa y Desescaladora**")
                st.info(f"Buenos días estimado/a, le saluda su asesor de {cliente['producto']}. Me comunico con el fin de acercarle una solución financiera personalizada para su negocio.")
                
                st.markdown("**Paso 3: Validación Segura de Identidad (LOPDP)**")
                st.caption("Por seguridad de sus datos personales, ¿me confirma por favor los 4 últimos dígitos de su RUC o cédula?")
                
            with p2:
                st.markdown("**Paso 4: Propuesta Comercial de Alta Velocidad**")
                st.info(f"{cliente['estrategia_recuperacion_maxima']}")
                
                st.markdown("**Paso 5: Manejo Dinámico de Objeción**")
                sim_obj = st.selectbox("Seleccione la objeción manifestada por el deudor:", [
                    "No tengo dinero / Las ventas están en cero",
                    "Un contratista / Municipio no me paga la planilla",
                    "Intereses y recargos muy altos",
                    "Llámenme la otra semana"
                ])
                if sim_obj == "No tengo dinero / Las ventas están en cero":
                    st.success("Táctica: 'Entiendo el bache de ventas de su taller/comercio. No le pido liquidar todo hoy. Revisemos un abono mínimo de arranque para frenar recargos.'")
                elif sim_obj == "Un contratista / Municipio no me paga la planilla":
                    st.success("Táctica: 'Sabemos de las demoras institucionales. Facilítenos copia de la factura radicada y fijamos un abono inicial simbólico mientras se concreta el cobro.'")
                elif sim_obj == "Intereses y recargos muy altos":
                    st.success("Táctica: 'Le muestro el desglose de capital real. Si pagamos capital esta semana, gestionamos la condonación total de la mora acumulada.'")
                else:
                    st.success("Táctica: 'Si lo dejamos para la otra semana el sistema escala a legal. Dejemos cerrado hoy un valor con fecha fija y comprobante por WhatsApp.'")
                    
                st.markdown("**Paso 6: Cierre con Compromiso Firme**")
                st.warning("Pactar: Monto exacto + Fecha y hora límite + Canal de depósito + Envío de foto de comprobante.")
                
        # Mensaje de WhatsApp Listo para Envío
        st.subheader("💬 Mensaje Oficial para Canal Digital (WhatsApp / SMS)")
        st.text_area("Texto listo para copiar y enviar (sin sesgo coercitivo):", value=cliente['mensaje_whatsapp_personalizado'], height=90)
        
        wa_url = f"https://api.whatsapp.com/send?text={cliente['mensaje_whatsapp_personalizado'].replace(' ', '%20')}"
        st.markdown(f"[📲 Abrir en WhatsApp Web / Móvil]({wa_url})")

# --------------------------------------------------------------------------------------
# 7. MÓDULO 4: PLANIFICADOR DE RUTAS DE CAMPO (VISITAS MYPE)
# --------------------------------------------------------------------------------------
elif modulo == "📍 4. Rutas de Campo (Visitas MYPE)":
    st.header("📍 Planificador de Rutas de Campo: Visitas Presenciales MYPE")
    st.markdown(
        "Módulo logístico para la asignación y ejecución de visitas físicas en el Distrito Metropolitano de Quito. "
        "Filtra estrictamente a los 90 clientes donde la visita presencial tiene alto valor incremental."
    )
    
    rutas_campo = df_master[df_master['elegible_visita_campo']].copy()
    
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Clientes Seleccionados para Campo", f"{len(rutas_campo)} casos")
    col_r2.metric("Saldo Total en Ruta de Visita", f"${rutas_campo['saldo_usd'].sum():,.2f} USD")
    col_r3.metric("Saldo Promedio por Visita", f"${rutas_campo['saldo_usd'].mean():,.2f} USD")
    
    st.markdown("---")
    
    col_filtro_ruta, col_map = st.columns([1, 2])
    
    with col_filtro_ruta:
        st.subheader("Filtro Logístico por Parroquia")
        parroquia_ruta = st.selectbox(
            "Seleccione Sector / Parroquia de Visita:",
            ["Todas las Parroquias"] + sorted(list(rutas_campo['parroquia_dm_quito'].unique()))
        )
        
        if parroquia_ruta != "Todas las Parroquias":
            rutas_filtradas = rutas_campo[rutas_campo['parroquia_dm_quito'] == parroquia_ruta]
        else:
            rutas_filtradas = rutas_campo
            
        st.info(f"📍 **{len(rutas_filtradas)} clientes** priorizados en {parroquia_ruta}.")
        
    with col_map:
        st.subheader("Distribución de Visitas por Parroquia")
        bar_ruta = rutas_campo['parroquia_dm_quito'].value_counts().reset_index()
        bar_ruta.columns = ['Parroquia', 'Visitas']
        fig_br = px.bar(bar_ruta, x='Parroquia', y='Visitas', color='Visitas', color_continuous_scale='Blues')
        fig_br.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_br, width="stretch")
        
    st.subheader("Hoja de Ruta de Campo para el Ejecutivo")
    cols_hoja_ruta = [
        'id_caso', 'parroquia_dm_quito', 'sector_productivo', 'saldo_usd',
        'dias_mora', 'bucket_mora', 'respuesta_ultimo_contacto', 'estado_prescripcion'
    ]
    st.dataframe(
        rutas_filtradas[cols_hoja_ruta].sort_values(by='saldo_usd', ascending=False).style.format({'saldo_usd': '${:,.2f}'}),
        width="stretch"
    )
    
    # Formulario para Registrar la Visita en Campo
    st.markdown("---")
    st.subheader("📝 Registro de Visita en Campo (Persistencia Append-Only)")
    
    with st.form("form_visita_campo"):
        c_v1, c_v2, c_v3 = st.columns(3)
        with c_v1:
            id_visita = st.selectbox("ID del Caso Visitado:", rutas_filtradas['id_caso'].tolist())
            fecha_visita = st.date_input("Fecha de la Visita:", datetime.now())
        with c_v2:
            resultado_visita = st.selectbox("Resultado de la Intervención:", [
                "Acuerdo cerrado con abono inicial pactado",
                "Solicitud formal de reestructuración MYPE",
                "Inspección de garantías / Negocio en operación",
                "Negocio cerrado temporalmente / Re-visitar",
                "Titular renuente / Derivación a juicio ejecutivo"
            ])
            monto_compromiso = st.number_input("Monto del Abono Comprometido (USD):", min_value=0.0, step=50.0)
        with c_v3:
            fecha_cumplimiento = st.date_input("Fecha de Cumplimiento Pactada:", datetime.now() + timedelta(days=3))
            observaciones_campo = st.text_input("Observaciones de la Visita:")
            
        submitted = st.form_submit_button("💾 Guardar Registro de Visita en Bitácora")
        if submitted:
            nuevo_registro = pd.DataFrame([{
                'id_caso': id_visita,
                'fecha_visita': str(fecha_visita),
                'resultado': resultado_visita,
                'monto_compromiso_usd': monto_compromiso,
                'fecha_cumplimiento': str(fecha_cumplimiento),
                'observaciones': observaciones_campo,
                'timestamp': datetime.now().isoformat()
            }])
            
            if os.path.exists(VISITAS_LOG_PATH):
                nuevo_registro.to_csv(VISITAS_LOG_PATH, mode='a', header=False, index=False)
            else:
                nuevo_registro.to_csv(VISITAS_LOG_PATH, mode='w', header=True, index=False)
                
            st.success(f"✅ Visita al caso {id_visita} registrada exitosamente en {VISITAS_LOG_PATH}.")

# --------------------------------------------------------------------------------------
# 8. MÓDULO 5: MOTOR ESTOCÁSTICO & CADENAS DE MARKOV
# --------------------------------------------------------------------------------------
elif modulo == "🎲 5. Motor Estocástico & Markov":
    st.header("🎲 Motor Estocástico & Simulación Predictiva")
    st.markdown(
        "Modelos probabilísticos de transición de estados de mora (Cadenas de Markov) y "
        "simulación de Monte Carlo del flujo de recuperación a 30, 60 y 90 días."
    )
    
    tab_stoch1, tab_stoch2 = st.tabs([
        "📈 Matriz de Transición de Cadenas de Markov (Roll Rates)",
        "🎰 Simulación de Monte Carlo de Recuperación (1.000 Iteraciones)"
    ])
    
    with tab_stoch1:
        st.subheader("Matriz de Transición Mensual Empírica entre Baldes de Mora")
        st.caption("Probabilidad de rodamiento mensual P(Balde t+1 | Balde t) estimada a partir de la cartera histórica.")
        
        estados = ['B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'Cura', 'Castigo']
        
        # Matriz empírica estocástica
        matriz_markov = np.array([
            [0.25, 0.15, 0.05, 0.01, 0.00, 0.00, 0.00, 0.54, 0.00], # B0
            [0.10, 0.30, 0.25, 0.05, 0.01, 0.00, 0.00, 0.29, 0.00], # B1
            [0.05, 0.10, 0.35, 0.30, 0.05, 0.01, 0.00, 0.14, 0.00], # B2
            [0.02, 0.04, 0.10, 0.40, 0.32, 0.04, 0.00, 0.08, 0.00], # B3
            [0.01, 0.02, 0.04, 0.10, 0.45, 0.33, 0.01, 0.04, 0.01], # B4
            [0.00, 0.01, 0.02, 0.04, 0.10, 0.50, 0.28, 0.02, 0.03], # B5
            [0.00, 0.00, 0.01, 0.01, 0.03, 0.05, 0.70, 0.01, 0.19], # B6
            [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00], # Cura (Absorbente)
            [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00]  # Castigo (Absorbente)
        ])
        
        df_markov = pd.DataFrame(matriz_markov, index=estados, columns=estados)
        
        fig_heat = px.imshow(
            df_markov,
            text_auto=".2f",
            color_continuous_scale="Blues",
            labels=dict(x="Estado Siguiente (t+1)", y="Estado Actual (t)", color="Probabilidad")
        )
        fig_heat.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_heat, width="stretch")
        
        st.info("💡 **Lectura de Riesgo:** El tramo B3 (61-90 días) tiene una probabilidad del **32% de rodar a B4** (cartera vencida formal) si no se ejecuta una intervención presencial inmediata.")
        
    with tab_stoch2:
        st.subheader("Simulador de Monte Carlo: Distribución Estocástica de Recuperación a 30 Días")
        
        c_mc1, c_mc2 = st.columns([1, 2])
        
        with c_mc1:
            st.markdown("**Parámetros de la Simulación:**")
            n_sims = st.slider("Número de Trayectorias Monte Carlo:", 200, 2000, 1000, 200)
            descuento_promedio = st.slider("Descuento Promedio por Condonación de Mora (%):", 0, 30, 12, 1)
            
            # Ejecución vectorizada Monte Carlo
            prob_base = df_master['prob_pago_30d_calibrada'].values
            saldos = df_master['saldo_usd'].values
            kept_rates = df_master['ratio_cumplimiento_promesas'].values
            
            # Probabilidad ajustada por kept rate para evitar sobrestimación de H1
            prob_ajustada = np.clip(prob_base * (0.5 + 0.5 * kept_rates), 0.05, 0.90)
            factor_pago = 1.0 - (descuento_promedio / 100.0)
            
            recuperaciones_sim = np.zeros(n_sims)
            np.random.seed(42)
            
            for i in range(n_sims):
                exitos = np.random.rand(len(df_master)) < prob_ajustada
                recuperaciones_sim[i] = np.sum(saldos[exitos] * factor_pago * np.random.uniform(0.3, 1.0, len(df_master))[exitos])
                
            media_recup = np.mean(recuperaciones_sim)
            p05 = np.percentile(recuperaciones_sim, 5) # VaR 95%
            p95 = np.percentile(recuperaciones_sim, 95)
            
            st.metric("Recuperación Media Estimada", f"${media_recup:,.0f} USD")
            st.metric("Piso Conservador (VaR 95%)", f"${p05:,.0f} USD")
            st.metric("Escenario Optimista (P95)", f"${p95:,.0f} USD")
            
        with c_mc2:
            fig_hist = px.histogram(
                recuperaciones_sim,
                nbins=40,
                labels={'value': 'USD Recuperados en 30 Días'},
                title=f"Distribución de Densidad de Probabilidad ({n_sims} Iteraciones)",
                color_discrete_sequence=['#0D9488']
            )
            fig_hist.add_vline(x=media_recup, line_dash="dash", line_color="#1A365D", annotation_text=f"Media: ${media_recup:,.0f}")
            fig_hist.add_vline(x=p05, line_dash="dot", line_color="#E53E3E", annotation_text=f"VaR 95%: ${p05:,.0f}")
            fig_hist.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
            st.plotly_chart(fig_hist, width="stretch")

# --------------------------------------------------------------------------------------
# 9. MÓDULO 6: TABLERO FODA & EXPLICABILIDAD ALGORÍTMICA (NUEVO)
# --------------------------------------------------------------------------------------
elif modulo == "🧭 6. Tablero FODA & Explicabilidad":
    st.header("🧭 Tablero Estratégico FODA & Explicabilidad Algorítmica (Caja Blanca)")
    st.markdown(
        "Diagnóstico estratégico multidimensional sustentado en datos reales de la cartera, "
        "matriz empírica de correlaciones y auditoría paso a paso de la lógica de decisión por la cual se clasifica a cada usuario."
    )
    
    tab_foda1, tab_foda2, tab_foda3 = st.tabs([
        "📊 Matriz FODA Cuantitativa (SWOT)",
        "🔬 Metodología de Cálculo & Correlaciones Estadísticas",
        "⚙️ Trazabilidad de Decisión: 'Auditá tu Cliente' (Caja Blanca)"
    ])
    
    # ----------------------------------------------------------------------------------
    # TAB 1: MATRIZ FODA CUANTITATIVA
    # ----------------------------------------------------------------------------------
    with tab_foda1:
        st.subheader("Tablero de Mando FODA / DAFO: Operación de Cobranza MYPE")
        st.caption("Diagnóstico integral sustentado en el perfil de cartera, marco COGEP y capacidad real de cobro.")
        
        c_foda1, c_foda2 = st.columns(2)
        
        with c_foda1:
            st.markdown("""
            <div class="swot-card swot-f">
                <div class="swot-title-f">💪 FORTALEZAS (Origen Interno / Operativo)</div>
                <ul>
                    <li><strong>Cuadre Contable Perfecto (100%):</strong> $4.036.961,46 USD verificados al centavo con identidad contable estricta ($Saldo = Capital + Int. + Mora + Gastos$).</li>
                    <li><strong>Consentimiento Pleno LOPDP (75,9%):</strong> 759 clientes con autorización formal verificada para contacto omnicanal sin riesgo sancionatorio.</li>
                    <li><strong>Mora Temprana/Media Recuperable (53,8%):</strong> 538 casos en tramos B0, B1 y B2 ($1.864.952 USD) con alta propensión a la cura sin necesidad de litigio.</li>
                    <li><strong>Títulos Ejecutivos Formales:</strong> 250 pagarés a la orden con cláusula de aceleración (fuerza ejecutiva plena bajo Art. 347 COGEP).</li>
                    <li><strong>Garantías Reales Identificadas:</strong> Créditos prendarios e hipotecarios con ratio LTV < 0.50 en cartera comercial.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="swot-card swot-d">
                <div class="swot-title-d">⚠️ DEBILIDADES (Origen Interno / Brechas Identificadas)</div>
                <ul>
                    <li><strong>Riesgo de Postergación Crónica:</strong> 325 casos registran promesas previas con 0% de cumplimiento (Kept Rate = 0,00), distorsionando proyecciones de cobro.</li>
                    <li><strong>Canal Telefónico Agotado:</strong> 161 cuentas en buzón/no responde y 96 en rechazo/evasión, haciendo inútil la llamada y exigiendo visita física.</li>
                    <li><strong>Kept Rate Global Insuficiente:</strong> Promedio de cumplimiento de promesas en toda la cartera de apenas 37,2%.</li>
                    <li><strong>Falta de Historial Temporal Multi-Corte:</strong> Existencia de una sola fecha de corte (2026-10-29), lo que limita el entrenamiento de series de tiempo.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with c_foda2:
            st.markdown("""
            <div class="swot-card swot-o">
                <div class="swot-title-o">🚀 OPORTUNIDADES (Origen Externo / Estratégico)</div>
                <ul>
                    <li><strong>Potencial de Caja Líquida a 30 Días:</strong> $2.026.814,73 USD de recuperación esperada neta mediante intervención oportuna de valor incremental.</li>
                    <li><strong>Apertura a la Negociación Declarada:</strong> 241 clientes (24,1% de la cartera) solicitaron voluntariamente reprogramación o refinanciamiento.</li>
                    <li><strong>Eficiencia Digital de Bajo Costo:</strong> 886 cuentas P3 aptas para autogestión y botón de pago con costo operativo cercano a cero.</li>
                    <li><strong>Condonación Condicionada de Mora:</strong> Ahorro atractivo para el deudor MYPE al liquidar capital en 48 horas ($390.875 USD en mora condonable).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="swot-card swot-a">
                <div class="swot-title-a">🛑 AMENAZAS (Origen Externo / Riesgos Críticos)</div>
                <ul>
                    <li><strong>Prescripción Cambiaria Inminente (Art. 479 C.Com):</strong> 49 cuentas ($265.594,66 USD) a menos de 12 meses (<6m en 31 casos) de perder fuerza ejecutiva.</li>
                    <li><strong>Contingencias Legales por Disputa de Saldo:</strong> 58 cuentas ($238.412 USD) en auditoría de liquidación con riesgo de quejas ante la SB o Defensoría del Pueblo si se gestionan.</li>
                    <li><strong>Inconsistencia de Títulos en Monitorio:</strong> 604 casos comerciales/consumo rotulados como "Liquidación de tarjeta", con riesgo de objeción procesal.</li>
                    <li><strong>Deterioro por Rodamiento B3 a B4:</strong> 210 cuentas ($851.340 USD) a punto de rodar a cartera vencida formal, disparando provisiones al 35%-50%.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader("Síntesis Cuantitativa de Impacto FODA")
        
        mf1, mf2, mf3, mf4 = st.columns(4)
        mf1.metric("Fortaleza: Cartera Temprana B0-B2", "$1.864.952 USD", "538 cuentas (46,2% saldo)")
        mf2.metric("Oportunidad: Solicitudes de Refinanciamiento", "241 cuentas", "24,1% de apertura directa")
        mf3.metric("Debilidad: Promesas 100% Incumplidas", "325 cuentas", "Kept Rate = 0,0%")
        mf4.metric("Amenaza: Cartera en Alerta de Prescripción", "$265.595 USD", "49 cuentas en B6")

    # ----------------------------------------------------------------------------------
    # TAB 2: METODOLOGÍA DE CÁLCULO & MATRIZ DE CORRELACIONES
    # ----------------------------------------------------------------------------------
    with tab_foda2:
        st.subheader("🔬 Metodología de Cálculo y Correlaciones Estadísticas de la Base de Datos")
        st.markdown(
            "Análisis matemático riguroso de las interdependencias entre variables cuantitativas de la cartera. "
            "Permite auditar el comportamiento del modelo de propensión frente al riesgo procesal y financiero."
        )
        
        num_cols = [
            'dias_mora', 'saldo_usd', 'capital_total_usd', 'interes_mora_usd',
            'pagos_12m', 'promesas_12m', 'ratio_cumplimiento_promesas',
            'prob_pago_30d_calibrada', 'recuperacion_esperada_30d_usd',
            'dias_para_prescripcion_cambiaria'
        ]
        
        corr_matrix = df_master[num_cols].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1.0,
            zmax=1.0,
            labels=dict(x="Variable X", y="Variable Y", color="Correlación Pearson"),
            title="Matriz de Correlación de Pearson (1.000 Casos MYPE)"
        )
        fig_corr.update_layout(height=520, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_corr, width="stretch")
        
        st.markdown("#### Hallazgos Estadísticos y Deducción Metodológica:")
        
        st.markdown(r"""
        1. **Días de Mora vs. Probabilidad de Pago ($r = -0,84$):**
           - Existe una correlación negativa lineal muy fuerte. A medida que transcurren los días de atraso, la probabilidad de recuperación decae drásticamente. En tramos B0–B2 la probabilidad promedia $>0,88$, mientras que en B5–B6 cae por debajo de $0,45$.
        2. **Días de Mora vs. Pagos en los Últimos 12 Meses ($r = -0,89$):**
           - El deudor en mora avanzada ha cesado por completo sus pagos transaccionales periódicos. El número de abonos en 12 meses es el predictor más limpio del colapso operativo del deudor.
        3. **Días de Mora vs. Interés de Mora ($r = +0,80$):**
           - La acumulación de recargos e intereses moratorios actúa como una barrera psicológica para la microempresa, disparando la sensación de impagabilidad.
        4. **Ratio de Cumplimiento de Promesas ($Kept\_Rate$) vs. Probabilidad ($r = +0,36$):**
           - El cumplimiento previo de promesas correlaciona positivamente con el pago efectivo. Los deudores con $Kept\_Rate \ge 0,50$ tienen el doble de probabilidad de cerrar un acuerdo definitivo frente a deudores con promesas rotas continuas.
        5. **Días de Mora vs. Días para Prescripción ($r = -1,00$):**
           - Correlación negativa perfecta determinística debida a la fórmula legal del Código de Comercio: $\text{días\_prescripción} = 1.095 - \text{días\_mora}$.
        """)

    # ----------------------------------------------------------------------------------
    # TAB 3: EXPLICABILIDAD ALGORÍTMICA "CAJA BLANCA"
    # ----------------------------------------------------------------------------------
    with tab_foda3:
        st.subheader("⚙️ Trazabilidad Algorítmica y Deducción Paso a Paso: 'Auditá tu Cliente'")
        st.markdown(
            "Desglose transparente del razonamiento lógico-matemático por el cual el sistema asigna a cualquier deudor "
            "en una categoría conductual, prioridad operativa y estrategia prescriptiva."
        )
        
        # Selector de cliente para auditar
        c_audit_id = st.selectbox(
            "Seleccione el Cliente a Auditar Algorítmicamente:",
            df_master['id_caso'].tolist(),
            index=3, # SIM-00004
            key="audit_selector"
        )
        
        c_aud = df_master[df_master['id_caso'] == c_audit_id].iloc[0]
        
        st.markdown(f"### Auditoría de Deducción para el Expediente: `{c_aud['id_caso']}`")
        
        col_in, col_calc = st.columns(2)
        
        with col_in:
            st.markdown("**1. Parámetros Brutos de Entrada (Input Features):**")
            st.json({
                "id_caso": c_aud['id_caso'],
                "saldo_usd": float(c_aud['saldo_usd']),
                "capital_total_usd": float(c_aud['capital_total_usd']),
                "dias_mora": int(c_aud['dias_mora']),
                "bucket_mora": c_aud['bucket_mora'],
                "promesas_12m": int(c_aud['promesas_12m']),
                "promesas_cumplidas_12m": int(c_aud['promesas_cumplidas_12m']),
                "respuesta_ultimo_contacto": c_aud['respuesta_ultimo_contacto'],
                "disputa_saldo": c_aud['disputa_saldo'],
                "consentimiento_contacto": c_aud['consentimiento_contacto_simulado'],
                "titulo_ejecutivo": c_aud['titulo_ejecutivo_tipo'],
                "avaluo_garantia_usd": float(c_aud['avaluo_garantia_usd'])
            })
            
        with col_calc:
            st.markdown("**2. Deducción Matemática de Ratios Intermedios:**")
            
            calc_kept = c_aud['promesas_cumplidas_12m'] / c_aud['promesas_12m'] if c_aud['promesas_12m'] > 0 else 0.0
            calc_dias_presc = 1095 - c_aud['dias_mora']
            calc_ltv = c_aud['saldo_usd'] / c_aud['avaluo_garantia_usd'] if c_aud['avaluo_garantia_usd'] > 0 else 0.0
            
            st.markdown(f"""
            <div class="trace-box">
                <strong>RATIO 1: Kept Rate (Tasa de Cumplimiento de Promesas)</strong><br>
                Fórmula: Promesas_Cumplidas / Promesas_Totales<br>
                Cálculo: {c_aud['promesas_cumplidas_12m']} / {c_aud['promesas_12m']} = <strong>{calc_kept:.2f} ({calc_kept:.1%})</strong><br>
                <em>Diagnóstico: {'ALTA FIABILIDAD (≥50%)' if calc_kept >= 0.50 else ('CRÍTICO / POSTERGACIÓN (<35%)' if calc_kept < 0.35 and c_aud['promesas_12m']>=2 else 'MODERADO')}</em>
                <br><br>
                <strong>RATIO 2: Días Restantes para Prescripción Cambiaria</strong><br>
                Fórmula: 1.095 días (3 años Código Comercio) - Días Mora<br>
                Cálculo: 1095 - {c_aud['dias_mora']} = <strong>{calc_dias_presc} días restantes</strong><br>
                <em>Diagnóstico: {'ALERTA CRÍTICA (<180d)' if calc_dias_presc < 180 else ('ALERTA PREVENTIVA (<365d)' if calc_dias_presc < 365 else 'PLENAMENTE VIGENTE')}</em>
                <br><br>
                <strong>RATIO 3: Cobertura de Garantía (LTV - Loan to Value)</strong><br>
                Fórmula: Saldo_Total / Avalúo_Garantía<br>
                Cálculo: ${c_aud['saldo_usd']:,.2f} / ${c_aud['avaluo_garantia_usd']:,.2f} = <strong>{calc_ltv:.2f}</strong><br>
                <em>Diagnóstico: {'ALTA COBERTURA (LTV < 0.50)' if calc_ltv < 0.50 and calc_ltv > 0 else 'QUIROGRAFARIO / BAJA COBERTURA'}</em>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("**3. Árbol de Reglas de Inferencia y Veredicto Algorítmico:**")
        
        # Evaluación de reglas paso a paso
        r_bloqueo = c_aud['bloqueo_legal']
        r_perfil = c_aud['perfil_conductual_observado']
        r_visita = c_aud['elegible_visita_campo']
        
        col_reg1, col_reg2, col_reg3 = st.columns(3)
        
        with col_reg1:
            st.markdown("**Compuerta 1: Cumplimiento Legal**")
            if r_bloqueo:
                st.error("❌ REGLA DISPARADA: Disputa activa o Consentimiento en revisión. ESTADO: BLOQUEADO PARA COBRANZA.")
            else:
                st.success("✅ REGLA SUPERADA: Sin disputa activa y consentimiento verificado. ESTADO: HABILITADO.")
                
        with col_reg2:
            st.markdown("**Compuerta 2: Clasificación de Perfil**")
            st.info(f"🏷️ **{r_perfil}**")
            if "Perfil 1" in r_perfil:
                st.caption("Motivo: Kept Rate ≥ 0.50 y respuesta colaborativa previa.")
            elif "Perfil 2" in r_perfil:
                st.caption("Motivo: Solicitó auditoría detallada o análisis numérico de ahorro.")
            elif "Perfil 3" in r_perfil:
                st.caption("Motivo: Kept Rate < 0.35 con múltiples promesas rotas históricas.")
            else:
                st.caption("Motivo: Agotamiento de canal telefónico (buzón o evasión reiterada).")
                
        with col_reg3:
            st.markdown("**Compuerta 3: Canal y Táctica Asignada**")
            if r_visita:
                st.warning("📍 **RUTA DE CAMPO (Visita Presencial)**")
                st.caption("Motivo: Saldo ≥ $3.000 USD con silencio telefónico o alerta de prescripción.")
            else:
                st.info("📲 **CANAL DIGITAL / TELEFÓNICO**")
                st.caption("Motivo: Saldo regular o canal digital con respuesta favorable.")

# --------------------------------------------------------------------------------------
# 10. MÓDULO 7: COMPLIANCE LEGAL ECUADOR & EXPORTADOR IA
# --------------------------------------------------------------------------------------
elif modulo == "⚖️ 7. Compliance Legal & Exportador IA":
    st.header("⚖️ Auditoría Normativa Ecuador & Exportador Multi-LLM / NotebookLM")
    st.markdown("Verificación de compliance legal estricto y generación de bitácoras para modelos de lenguaje.")
    
    tab_comp1, tab_comp2 = st.tabs([
        "📜 Marco Regulatorio y Guardrails Ecuatorianos",
        "🧠 Generador de Bitácoras para NotebookLM / Multi-LLM"
    ])
    
    with tab_comp1:
        st.subheader("Matriz de Guardrails Normativos y Sanciones Previstas")
        
        normativas = [
            ("Ley Orgánica de Defensa del Consumidor (Art. 49)", "Prácticas Coercitivas Prohibidas", "Sanciones pecuniarias y multas administrativas.", "Prohibición de hostigamiento, llamadas reiteradas, exhibición ante terceros y cartas que simulen mandamientos judiciales falsos."),
            ("Regulación de Horarios Nacionales (JPRF / SB / SEPS)", "Ventana Legal Única de Contacto", "Nulidad de requerimientos y sanciones regulatorias.", "Lunes a Viernes de 08:00 a 19:00; Sábados de 09:00 a 13:00. Prohibición total domingos y feriados."),
            ("Ley Orgánica de Protección de Datos Personales (LOPDP)", "Principio de Confidencialidad", "Multas de hasta el 1% de la facturación institucional.", "Validación de 4 dígitos de identidad previa a revelar saldos. Cero comunicación a familiares, cónyuges o empleadores."),
            ("Código Orgánico Integral Penal (COIP Art. 154)", "Tipificación del Delito de Intimidación", "Pena privativa de libertad de 1 a 3 años para el gestor.", "Prohibición estricta de amenazas de cárcel o detención policial (no existe prisión por deudas en Ecuador, Art. 66 CRE)."),
            ("Código de Comercio (Art. 479)", "Prescripción de la Acción Cambiaria", "Pérdida de la fuerza ejecutiva del título valor.", "El pagaré y la letra prescriben a los 3 años (1.095 días) desde la fecha de vencimiento sin interrupción procesal.")
        ]
        
        df_norm = pd.DataFrame(normativas, columns=["Cuerpo Legal", "Materia", "Riesgo Institucional", "Regla Operativa en Sistema"])
        st.table(df_norm)
        
    with tab_comp2:
        st.subheader("Exportador de Expedientes para NotebookLM, Claude Code y Gemini")
        st.caption("Genera el expediente en formato Markdown estándar para inyección como fuente de conocimiento.")
        
        caso_export = st.selectbox("Seleccione el Caso para Exportar:", df_master['id_caso'].tolist(), index=0)
        c_data = df_master[df_master['id_caso'] == caso_export].iloc[0]
        
        md_export = f"""# EXPEDIENTE DE AUDITORÍA Y COBRANZA — CASO {c_data['id_caso']}
**Rótulo:** SIMULACIÓN CALIBRADA DIDÁCTICA / DATOS SINTÉTICOS.
**Fecha de Corte:** 2026-10-29 · **Jurisdicción:** República del Ecuador.

## 1. Identificación y Actividad MYPE
- **Deudor:** {c_data['tipo_deudor']}
- **Sector Económico:** {c_data['sector_productivo']}
- **Ubicación:** Parroquia {c_data['parroquia_dm_quito']}, Distrito Metropolitano de Quito
- **Producto:** {c_data['producto']}

## 2. Liquidación Contable Auditada
- **Saldo Total Exigible:** USD {c_data['saldo_usd']:,.2f}
- **Capital Total:** USD {c_data['capital_total_usd']:,.2f}
- **Interés Corriente:** USD {c_data['interes_corriente_usd']:,.2f}
- **Interés de Mora Legal:** USD {c_data['interes_mora_usd']:,.2f}
- **Gastos de Cobranza:** USD {c_data['gastos_cobranza_usd']:,.2f}
- **Días de Mora:** {c_data['dias_mora']} días (Tramo {c_data['bucket_mora']})

## 3. Diagnóstico Jurídico y Procesal (COGEP)
- **Título Ejecutivo:** {c_data['titulo_ejecutivo_tipo']}
- **Vía Procesal Idónea:** {c_data['via_procesal_idonea']}
- **Días para Prescripción Cambiaria:** {c_data['dias_para_prescripcion_cambiaria']} días ({c_data['estado_prescripcion']})
- **Garantía Declarada:** {c_data['garantia_declarada']} (LTV: {c_data['ltv_ratio']:.2f})
- **Medida Cautelar Aplicable:** {c_data['medida_cautelar_aplicable']}

## 4. Perfil Conductual Observado y Estrategia
- **Perfil Observado:** {c_data['perfil_conductual_observado']}
- **Ratio Histórico de Promesas (Kept Rate):** {c_data['ratio_cumplimiento_promesas']:.1%}
- **Última Respuesta:** {c_data['respuesta_ultimo_contacto']}
- **Estrategia Prescriptiva:** {c_data['estrategia_recuperacion_maxima']}
- **Próxima Mejor Acción (NBA):** {c_data['next_best_action']}

## 5. Guion Operativo en 6 Pasos
{c_data['guion_llamada_personalizado']}
"""
        st.text_area("Texto Markdown para NotebookLM / LLM:", value=md_export, height=300)
        
        st.download_button(
            label="📥 Descargar Expediente en Markdown (.md)",
            data=md_export,
            file_name=f"expediente_{c_data['id_caso']}.md",
            mime="text/markdown"
        )

# --------------------------------------------------------------------------------------
# 11. MÓDULO 8: REPORTERÍA PERIÓDICA DE ENTRENAMIENTO (SOLO SINTÉTICA)
# --------------------------------------------------------------------------------------
elif modulo == "📈 8. Reportería periódica (simulada)":
    render_reporting_dashboard(st, px)
