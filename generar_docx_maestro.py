# -*- coding: utf-8 -*-
"""
Generador del Documento Oficial Word (.docx)
PROMPT MAESTRO DIRECTIVO: SISTEMA DE INTELIGENCIA Y GESTIÓN ESTRATÉGICA DE COBRANZAS (SIGEC-EC v2.0)
Multi-Arnés: Google Gemini, Anthropic Claude Code, OpenAI Codex
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Aplica color de fondo a una celda de tabla."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Establece márgenes internos de una celda (en dxa: 20 dxa = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    """Aplica bordes sutiles a la tabla."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_callout(doc, text, title="NOTA DIRECTIVA / ADVERTENCIA JURÍDICA", border_color="1A365D", bg_color="F0F4F8"):
    """Crea una caja de texto destacada (Callout box)."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=160)
    
    # Borde grueso solo a la izquierda
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"[{title}]\n")
    run_title.bold = True
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(10.5)
    run_title.font.color.rgb = RGBColor.from_string(border_color)
    
    run_text = p.add_run(text)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = RGBColor(45, 55, 72)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def format_table_header(row, col_widths, titles, bg_color="1A365D"):
    for idx, (cell, width, title) in enumerate(zip(row.cells, col_widths, titles)):
        cell.width = Inches(width)
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=140, bottom=140, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(title)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

def format_table_row(row, col_widths, values, is_alt=False):
    bg_color = "F7FAFC" if is_alt else "FFFFFF"
    for cell, width, val in zip(row.cells, col_widths, values):
        cell.width = Inches(width)
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        run = p.add_run(str(val))
        run.font.name = "Calibri"
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(45, 55, 72)

def main():
    doc = docx.Document()
    
    # Márgenes de página
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
    print("Iniciando construcción de documento Word...")

    # PORTADA / ENCABEZADO
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_sub = p_header.add_run("PROGRAMA DE FORMACIÓN EN LIDERAZGO Y GESTIÓN ESTRATÉGICA DE COBRANZAS\nENTORNO DIDÁCTICO DE SIMULACIÓN PREDICTIVA CON IA — REPÚBLICA DEL ECUADOR")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(8.5)
    r_sub.font.color.rgb = RGBColor(113, 128, 150)
    
    # Línea divisoria
    p_line = doc.add_paragraph()
    p_line.paragraph_format.space_after = Pt(12)
    r_line = p_line.add_run("―" * 52)
    r_line.font.color.rgb = RGBColor(43, 108, 176)
    
    # Título Principal
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("PROMPT MAESTRO INTEGRAL (SIGEC-EC v2.0):\nSISTEMA DE INTELIGENCIA Y GESTIÓN ESTRATÉGICA DE COBRANZAS 1 A 1")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = RGBColor(26, 54, 93) # Navy Blue
    
    # Subtítulo
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub2 = p_sub.add_run("Manual Técnico de Arquitectura, Neurocobranza Científica, Mitigación de Coerción Legal y Especificación Multi-Arnés (Google Gemini, Anthropic Claude Code, OpenAI Codex)")
    r_sub2.italic = True
    r_sub2.font.name = "Calibri"
    r_sub2.font.size = Pt(12)
    r_sub2.font.color.rgb = RGBColor(43, 108, 176) # Slate Blue
    
    # TABLA DE METADATOS Y CONTROL DIRECTIVO
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_table)
    
    meta_widths = [2.2, 4.3]
    meta_data = [
        ("Entidad / Contexto:", "Institución Financiera en Ecuador — Gestión Prejudicial de Cartera MYPE"),
        ("Rol del Operador:", "Gestor Experto de Cobranza / Consultor Estratégico de Recuperación Acelerada"),
        ("Entorno de Ejecución:", "Local Autónomo (Responsive, Interactivo, Sandbox Local Append-Only)"),
        ("Modelos Multi-Arnés Homologados:", "Google Gemini 3.8 Flash / Pro | Anthropic Claude 3.5 Sonnet | OpenAI Codex / GPT-4o"),
        ("Marco Normativo Rector:", "COGEP (Arts. 347, 351, 356) | C. de Comercio | Ley Defensa Consumidor (Art. 49) | LOPDP | Res. JPRF")
    ]
    
    for idx, (lbl, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        cell_lbl, cell_val = row.cells
        cell_lbl.width = Inches(meta_widths[0])
        cell_val.width = Inches(meta_widths[1])
        set_cell_background(cell_lbl, "F0F4F8")
        set_cell_background(cell_val, "FFFFFF")
        set_cell_margins(cell_lbl, 80, 80, 100, 100)
        set_cell_margins(cell_val, 80, 80, 100, 100)
        
        p0 = cell_lbl.paragraphs[0]
        p0.paragraph_format.space_before = Pt(1); p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(lbl); r0.bold = True; r0.font.name = "Calibri"; r0.font.size = Pt(9); r0.font.color.rgb = RGBColor(26, 54, 93)
        
        p1 = cell_val.paragraphs[0]
        p1.paragraph_format.space_before = Pt(1); p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(val); r1.font.name = "Calibri"; r1.font.size = Pt(9); r1.font.color.rgb = RGBColor(45, 55, 72)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # CALLOUT INICIAL OBLIGATORIO
    add_callout(
        doc,
        "ESTRICTO RÓTULO DIDÁCTICO Y LEGAL: Este documento contiene la especificación matemática, jurídica, neuroconductual y agéntica del Sistema SIGEC-EC v2.0, calibrado con una base de datos sintética de 1.000 clientes microempresarios (USD 4,03M). Su finalidad es el entrenamiento de equipos de cobranza de alto rendimiento en el uso de Inteligencia Artificial para la recuperación de cartera en el menor tiempo posible con cero infracción normativa.",
        title="DECLARACIÓN OBLIGATORIA DE ENTORNO DE SIMULACIÓN",
        border_color="0D9488",
        bg_color="F0FDFA"
    )

    # SECCIÓN 1: CONTEXTUALIZACIÓN DEL ESTADO ACTUAL Y DIAGNÓSTICO
    h1 = doc.add_heading("1. Contextualización del Estado del Directorio y Diagnóstico de Cartera", level=1)
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "El presente directorio de trabajo contiene un ecosistema integral y maduro de datos sintéticos, modelos de scoring, guiones de contacto, expedientes testigo y marcos arquitectónicos preliminares, diseñados específicamente para resolver el desafío operativo de la cobranza en el contexto socioeconómico y legal del Ecuador."
    )
    p.paragraph_format.space_after = Pt(6)
    
    # Subsección 1.1: Inventario de Activos
    doc.add_heading("1.1. Inventario Analítico de Activos Existentes en el Repositorio", level=2)
    
    inv_table = doc.add_table(rows=6, cols=3)
    inv_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(inv_table)
    inv_widths = [1.8, 1.2, 3.5]
    
    format_table_header(inv_table.rows[0], inv_widths, ["Componente / Directorio", "Estado / Dimensión", "Aporte Operativo al Sistema"])
    
    inv_rows = [
        ("datos_sinteticos/ (v2.0)", "1.000 Casos / 62 Variables", "Base maestra calibrada con balances al centavo, tramos de mora B0 a B6, neuroperfiles, prescripción cambiaria y scoring predictivo calibrado."),
        ("guiones_llamada_1000.csv", "1.000 Guiones Estructurados", "Scripts telefónicos personalizados en 6 pasos correlacionados unívocamente con el saldo, título ejecutivo y arquetipo neurocognitivo."),
        ("Gestión de cobranzas efectivas/", "Framework STPR (10 Agentes)", "Especificación técnica preliminar con catálogo agéntico, políticas de simulación, esquemas de 4 memorias y trazabilidad."),
        ("ANALISIS_SENTENCIA_COBRANZA/", "3 Informes Técnico-Legales", "Jurisprudencia y defensa procesal sobre juicios ejecutivos bancarios (COGEP art. 347/351, prescripción de pagarés a 3 años y desproporción de mora)."),
        (".agents/skills/", "2 Habilidades Especializadas", "Herramientas de apelación forense y auditoría procesal de pagarés para prevenir nulidades y objeciones de fondo del deudor.")
    ]
    
    for idx, rdata in enumerate(inv_rows):
        format_table_row(inv_table.rows[idx+1], inv_widths, rdata, is_alt=(idx % 2 == 1))
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # Subsección 1.2: El Dilema Estructural de la Cartera MYPE
    doc.add_heading("1.2. El Dilema Estructural de la Cartera MYPE: Voluntad Subjetiva vs. Capacidad Real", level=2)
    p = doc.add_paragraph(
        "El análisis econométrico de los 1.000 casos sintéticos refleja con fidelidad el comportamiento de las Micro y Pequeñas Empresas (MYPEs) en el Ecuador. En este segmento, el deudor frecuentemente manifiesta una actitud psicológica de cooperación y voluntad para honrar su deuda (aversión a la deshonra social y al bloqueo en la central de riesgos); sin embargo, su capacidad financiera real está severamente condicionada por:"
    )
    
    bp1 = doc.add_paragraph(style='List Bullet')
    r = bp1.add_run("Descalce de Liquidez Inmediata: "); r.bold = True
    bp1.add_run("El capital de trabajo de la MYPE suele estar inmovilizado en inventarios no vendidos o en cuentas por cobrar a terceros no pagadas a tiempo.")
    
    bp2 = doc.add_paragraph(style='List Bullet')
    r = bp2.add_run("La Trampa de las Promesas Incumplidas: "); r.bold = True
    bp2.add_run("Ante la presión del gestor, el deudor tiende a comprometer montos imposibles de cumplir con tal de terminar la interacción, resultando en falsas promesas (Kept Rate bajo) y frustración operativa.")
    
    bp3 = doc.add_paragraph(style='List Bullet')
    r = bp3.add_run("Imperativo de Velocidad de la Entidad: "); r.bold = True
    bp3.add_run("La institución financiera requiere recuperar la mayor cantidad de dinero en el menor tiempo posible, pues el rodamiento de cuotas (Roll Rate) hacia tramos tardíos (B4, B5, B6) dispara el gasto en provisiones obligatorias (Superintendencia de Bancos/SEPS).")

    # SECCIÓN 2: MARCO NORMATIVO Y BARRERAS ANTI-COERCIÓN
    h1 = doc.add_heading("2. Marco Jurídico Ecuatoriano y Barreras Inquebrantables de Anti-Coerción", level=1)
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "En la República del Ecuador, la gestión de cobranza está estrictamente delimitada por un marco normativo garantista. El sistema automatizado SIGEC-EC v2.0 implementa 'guardrails' de código y filtros de lenguaje natural para impedir que el gestor humano o el agente de IA incurra en conductas que generen responsabilidad civil, administrativa o penal para la institución financiera."
    )
    
    # Tabla Normativa
    norm_table = doc.add_table(rows=7, cols=3)
    norm_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(norm_table)
    norm_widths = [1.8, 1.8, 2.9]
    
    format_table_header(norm_table.rows[0], norm_widths, ["Cuerpo Legal / Norma", "Disposición / Artículo", "Implicación Operativa y Filtro Anti-Coerción"])
    
    norm_rows = [
        ("Ley Orgánica de Defensa del Consumidor", "Art. 49: Prácticas Prohibidas de Cobranza", "Prohibición taxativa de hostigamiento, llamadas reiterativas, cobros humillantes, simulación de órdenes judiciales no existentes y contacto a terceros ajenos a la obligación."),
        ("Regulación Horaria Nacional", "Resoluciones JPRF / SB / SEPS", "Horario legal único de gestión: Lunes a Viernes de 08:00 a 19:00; Sábados de 09:00 a 13:00. PROHIBICIÓN ABSOLUTA de contacto en domingos y feriados nacionales/locales."),
        ("Ley Orgánica de Protección de Datos Personales (LOPDP)", "Arts. 10, 11 y 21: Principio de Confidencialidad", "Prohibición absoluta de revelar saldos o la condición de morosidad a familiares, vecinos, empleados o recepcionistas. Validación obligatoria de identidad antes de revelar la deuda."),
        ("Código Orgánico Integral Penal (COIP)", "Art. 154: Tipificación de Intimidación", "Prohibición estricta de amenazar con cárcel o detención policial por deudas civiles/comerciales (en Ecuador no hay prisión por deudas, Art. 66 num. 29 CRE)."),
        ("Código Orgánico General de Procesos (COEP)", "Art. 347 (Ejecutivo) vs. Art. 356 (Monitorio)", "Diferenciación legal: Pagarés y letras con cláusula de aceleración van a Juicio Ejecutivo; facturas o documentos privados <= 50 SBU van a Procedimiento Monitorio."),
        ("Código de Comercio", "Art. 479 y concordantes: Prescripción", "Prescripción de la acción cambiaria a los 3 años (1.095 días) desde el vencimiento del título. Monitoreo automatizado con alertas rojas preventivas a los 180 y 90 días.")
    ]
    
    for idx, rdata in enumerate(norm_rows):
        format_table_row(norm_table.rows[idx+1], norm_widths, rdata, is_alt=(idx % 2 == 1))
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    add_callout(
        doc,
        "FILTRO DE LENGUAJE PROHIBIDO: Queda bloqueado cualquier mensaje o guion que emplee vocabulario coercitivo como: 'lo vamos a demandar hoy si no paga ya', 'se le embargarán todos sus bienes en 24 horas sin juicio', 'llamaremos a su jefe o familiares', o 'incurrirá en prisión'. El enfoque técnico sustituye la amenaza por la demostración analítica de ahorro financiero, la reciprocidad y la preservación patrimonial.",
        title="REGLA DE ORO DE LEGALIDAD OPERATIVA",
        border_color="C53030",
        bg_color="FFF5F5"
    )

    # SECCIÓN 3: ARQUITECTURA TÉCNICA Y COMPONENTES
    h1 = doc.add_heading("3. Arquitectura Técnica y Funcional del Sistema Local de Cobranza", level=1)
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "El sistema SIGEC-EC v2.0 se concibe como una solución integral en local, con interfaz interactiva, dinámica y responsiva, diseñada para operar sin fuga de datos hacia servicios externos no autorizados y con capacidad de despliegue ágil para el gestor individual."
    )
    
    doc.add_heading("3.1. Arquitectura en 6 Capas Modulares", level=2)
    
    capas = [
        ("Capa 1: Ingestión y Cuadre Contable Determinístico", "Garantiza la identidad matemática: Saldo Total = Capital + Int. Ordinario + Int. Mora + Gastos Normados. Valida que cuotas vencidas <= cuotas totales y calcula métricas de antigüedad."),
        ("Capa 2: Motor de Scoring Logístico y Priorización Cuadridimensional", "Calcula la probabilidad calibrada de cobro a 30 días (P_30d) y el Valor Esperado (VE_30d = Saldo * P_30d). Asigna prioridades P1 (Cobro inmediato alto saldo), P2 (Estratégico legal), P3 (Autogestión rápida) y P4 (Castigo)."),
        ("Capa 3: Motor de Neurocobranza y Perfilado Conductual", "Mapea los 5 arquetipos neurocognitivos del deudor frente al cortisol, determinando el nivel de estrés y seleccionando el gatillador de influencia ética óptimo (Cialdini/Kahneman)."),
        ("Capa 4: Motor de Cumplimiento Normativo (Guardrail Anti-Coerción)", "Verifica franja horaria hábil, canal autorizado (LOPDP), estado de prescripción cambiaria y valida que los textos de interacción carezcan de sesgos coercitivos."),
        ("Capa 5: Motor de Prescripción Operativa (Next-Best-Action)", "Aplica la Escalera de Resolución Estratégica: propone de forma jerárquica la mejor solución comercial o prejudicial orientada a la máxima velocidad de retorno."),
        ("Capa 6: Cockpit Interactivo 1 a 1 y Trazabilidad Multi-LLM", "Interfaz responsiva que presenta la Ficha 360° del deudor, simulador de objeciones en tiempo real, generador de guiones adaptativos y exportación directa de bitácoras para NotebookLM.")
    ]
    
    for c_title, c_desc in capas:
        p_c = doc.add_paragraph()
        r_c1 = p_c.add_run(f"• {c_title}: "); r_c1.bold = True; r_c1.font.color.rgb = RGBColor(26, 54, 93)
        r_c2 = p_c.add_run(c_desc)
        p_c.paragraph_format.space_after = Pt(4)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Subsección 3.2: Fórmulas Matemáticas y Algoritmos
    doc.add_heading("3.2. Fórmulas Matemáticas y Algoritmos de Calibración", level=2)
    
    f1 = doc.add_paragraph()
    r = f1.add_run("1. Valor Esperado de Recuperación a 30 Días (VE_30d):\n"); r.bold = True
    f1.add_run("   VE_30d = Saldo_Total_USD × Probabilidad_Calibrada_Cobro_30d\n")
    f1.add_run("   Permite ordenar la cola de gestión por impacto financiero real de liquidez y no solo por saldo nominal.")
    
    f2 = doc.add_paragraph()
    r = f2.add_run("2. Ratio de Cumplimiento de Promesas (Kept Rate):\n"); r.bold = True
    f2.add_run("   Kept_Rate = Promesas_Cumplidas_12m / Promesas_Totales_12m\n")
    f2.add_run("   Si Kept_Rate < 0.35, el sistema clasifica al deudor en 'Riesgo de Postergación Crónica', bloqueando acuerdos verbales sin abono inicial.")
    
    f3 = doc.add_paragraph()
    r = f3.add_run("3. Índice de Cobertura de Garantía (LTV - Loan to Value):\n"); r.bold = True
    f3.add_run("   LTV = Saldo_Total_USD / Avaluo_Comercial_Garantia_USD\n")
    f3.add_run("   Si LTV < 0.50 y la mora supera los 90 días, se habilita la estrategia P2 de presión procesal mediante medida cautelar de retención o embargo.")

    # SECCIÓN 4: LA ESCALERA ESTRATÉGICA DE RESOLUCIÓN
    h1 = doc.add_heading("4. La Escalera Estratégica de Resolución (Ladder of Resolution)", level=1)
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "Para responder al mandato de 'recuperar la mayor cantidad de dinero en el menor tiempo posible', el sistema no aplica soluciones homogéneas. Se implementa una Escalera de Resolución en 4 Peldaños Jerárquicos y Excluyentes:"
    )
    
    ladder_table = doc.add_table(rows=5, cols=4)
    ladder_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(ladder_table)
    ladder_widths = [1.2, 1.8, 1.8, 1.7]
    
    format_table_header(ladder_table.rows[0], ladder_widths, ["Peldaño / Prioridad", "Mecanismo Financiero", "Criterio de Aplicación", "Impacto en Velocidad de Caja"])
    
    ladder_rows = [
        ("Nivel 1: Pago Efectivo Inmediato Contrastable", "Condonación condicionada al 100% de intereses de mora y gastos de cobranza pagando en < 48 horas.", "Mora temprana y media (B0 a B3) o clientes con alta liquidez transaccional declarada.", "Máxima velocidad: Liquidez líquida en banco en menos de 48 horas sin costo operativo."),
        ("Nivel 2: Compromiso Blindado con Abono Inicial", "Down payment exigido del 20% al 30% en 72 horas y saldo en 2 a 3 cuotas fijas cortas.", "MYPEs con voluntad favorable pero problemas temporales de capital de trabajo.", "Mitigación inmediata del riesgo: Valida liquidez real y evita promesas ficticias."),
        ("Nivel 3: Reestructuración / Refinanciamiento", "Ampliación de plazo, capitalización reglada de intereses y ajuste de cuota al ciclo operativo.", "MYPEs con colapso transitorio de ventas pero negocio plenamente operativo.", "Retención del cliente y regularización contable; evita el castigo a costo de menor velocidad."),
        ("Nivel 4: Escalado Prejudicial Formal", "Notificación formal con citación a mediación o demanda ejecutiva (COGEP 347) / monitoria (356).", "Deudores no contactables, renuentes, con garantías reales de alto valor o mora > 180 días.", "Protección procesal del crédito para evitar la prescripción de los 3 años.")
    ]
    
    for idx, rdata in enumerate(ladder_rows):
        format_table_row(ladder_table.rows[idx+1], ladder_widths, rdata, is_alt=(idx % 2 == 1))
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # SECCIÓN 5: NEUROCOBRANZA CIENTÍFICA Y LOS 5 ARQUETIPOS
    h1 = doc.add_heading("5. Motor de Neurocobranza Científica y Guion Operativo en 6 Pasos", level=1)
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "La neurocobranza científica postula que la mora activa una sobrecarga neuroquímica en el cerebro del deudor: el cerebro reptiliano (amenaza y huida) y el sistema límbico (culpa y vergüenza social) bloquean la corteza prefrontal (neocórtex analítico). Si el gestor ataca con presión coercitiva, incrementa el cortisol y desata una de dos respuestas improductivas: evasión/apagado de teléfono (huida) o agresividad procesal (lucha)."
    )
    
    doc.add_heading("5.1. Taxonomía de los 5 Arquetipos Neurocognitivos", level=2)
    
    neuro_table = doc.add_table(rows=6, cols=4)
    neuro_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(neuro_table)
    neuro_widths = [1.5, 1.4, 1.8, 1.8]
    
    format_table_header(neuro_table.rows[0], neuro_widths, ["Arquetipo", "Estado Neurobiológico", "Gatillador Ético Óptimo", "Canal y Táctica Predilecta"])
    
    neuro_rows = [
        ("Aversivo al Conflicto", "Sobrecarga severa de cortisol. Parálisis decisional y miedo a contestar llamadas.", "Alivio y Desahogo. Sensación de control y salida estructurada sin fricción.", "WhatsApp formal asíncrono con enlace a botón de pago o autogestión sin contacto verbal."),
        ("Racional / Calculador", "Neocórtex analítico dominante. Evalúa números fríos y costo de oportunidad.", "Demostración Numérica de Ahorro. Cuadro comparativo de intereses y quitas.", "Llamada consultiva ejecutiva o correo con matriz de ahorro financiero contrastable."),
        ("Circunstancial / Cooperativo", "Límbico-empático. Siente vergüenza por incumplir debido a un imprevisto.", "Reciprocidad y Reconocimiento de su historial histórico cumplido.", "Llamada cálida: validación humana del bache temporal y pacto de abono solidario."),
        ("Reactivo / Defensivo", "Amígdala hiperreactiva en modo lucha. Sospecha de cobros indebidos o maltrato.", "Neutralización de Ego y Transparencia Contable al centavo.", "Llamada protocolar desescaladora: escucha activa, sin interrumpir, enviando estado de cuenta."),
        ("Postergador / Optimismo Ilusorio", "Sesgo de presente. Tiende a diferir pagos esperando cobranzas milagrosas futuras.", "Compromiso Escalonado y Micro-hitos verificables en fechas fijas.", "Llamada con anclaje de compromiso firme: abono en 48h con recordatorio 24h previas.")
    ]
    
    for idx, rdata in enumerate(neuro_rows):
        format_table_row(neuro_table.rows[idx+1], neuro_widths, rdata, is_alt=(idx % 2 == 1))
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # Subsección 5.2: Protocolo Operativo del Guion en 6 Pasos
    doc.add_heading("5.2. Protocolo Operativo de Gestión en 6 Pasos", level=2)
    
    pasos = [
        ("Paso 1: Pre-llamada Legal y Auditoría Técnica", "El gestor verifica saldo exacto al centavo, días de mora, fecha de prescripción cambiaria, garantías y franja horaria permitida."),
        ("Paso 2: Apertura Respetuosa y Desescaladora de Cortisol", "Saludo formal, identificación clara de la institución y tono colaborativo sin acusaciones ni adjetivos denigrantes."),
        ("Paso 3: Validación Segura de Identidad (Filtro LOPDP)", "Verificación de los 4 últimos dígitos de la cédula o RUC antes de mencionar saldos o atrasos, evitando exposición a terceros."),
        ("Paso 4: Propuesta de Alta Velocidad (Mayor Recuperación)", "Presentación del beneficio inmediato: condonación de mora por pago en 48h o abono del 30% en 72h para suspender acciones prejudiciales."),
        ("Paso 5: Manejo Persuasivo y Ético de Objeciones", "Tratamiento técnico de la causa real (falta de liquidez MYPE): ajuste del plan a fechas de facturación o cobro del cliente."),
        ("Paso 6: Cierre con Compromiso Firme y Trazabilidad", "Pactación de monto exacto, fecha exacta, canal bancario específico y confirmación escrita por WhatsApp o SMS.")
    ]
    
    for p_num, p_body in pasos:
        p_step = doc.add_paragraph()
        r1 = p_step.add_run(f"{p_num}: "); r1.bold = True; r1.font.color.rgb = RGBColor(26, 54, 93)
        r2 = p_step.add_run(p_body)
        p_step.paragraph_format.space_after = Pt(3)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # SECCIÓN 6: EL PROMPT MAESTRO INTEGRAL (CANÓNICO)
    h1 = doc.add_heading("6. Texto Canónico del Prompt Maestro Replicable (Multi-Arnés)", level=1)
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "A continuación se presenta el texto íntegro, exhaustivo y estructurado del PROMPT MAESTRO. Este bloque ha sido diseñado para ser inyectado como System Prompt o Directriz Principal en cualquier arnés de Inteligencia Artificial (Google Gemini, Anthropic Claude Code, OpenAI Codex). No omite ninguna de las 62 variables ni los mandatos regulatorios ecuatorianos."
    )
    p.paragraph_format.space_after = Pt(6)
    
    # Caja de Código / Prompt Maestro
    pm_box = doc.add_table(rows=1, cols=1)
    pm_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    pm_cell = pm_box.cell(0, 0)
    pm_cell.width = Inches(6.5)
    set_cell_background(pm_cell, "F8FAFC")
    set_cell_margins(pm_cell, top=140, bottom=140, left=140, right=140)
    
    tcPr = pm_cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="2B6CB0"/>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p_code = pm_cell.paragraphs[0]
    p_code.paragraph_format.space_before = Pt(0)
    p_code.paragraph_format.space_after = Pt(0)
    
    PROMPT_MAESTRO_TEXT = """<SYSTEM_ROLE>
Eres un Director Estratégico de Inteligencia de Cobranzas, Consultor Experto en Finanzas Crediticias, Derecho Procesal Ecuatoriano (COGEP) y Neurocobranza Científica de Nivel Tier 1.
Operas como el motor cognitivo de apoyo a un Gestor de Cobranzas de una Institución Financiera en la República del Ecuador.
</SYSTEM_ROLE>

<CONTEXTO_Y_CARTERA>
Gestionas una cartera calibrada de Micro y Pequeñas Empresas (MYPEs) en mora prejudicial y administrativa.
- Saldo promedio de USD 4.036,96 (Rango: USD 1.500 a USD 25.000).
- Días de mora: 1 a 400 días distribuidos en baldes B0 a B6.
- Dilema central: Clientes con alta voluntad subjetiva de pago pero capacidad real asfixiada por descalce de capital de trabajo y rotación lenta de cobros.
- Rótulo obligatorio de entorno: SIMULACIÓN CALIBRADA / DATOS SINTÉTICOS DIDÁCTICOS.
</CONTEXTO_Y_CARTERA>

<OBJETIVO_RECTOR>
Recuperar la mayor cantidad de cartera líquida en el menor tiempo posible mediante la modulación estratégica de la gestión 1 a 1, seleccionando el canal óptimo, desescalando el cortisol del deudor y blindando los compromisos financieros, bajo estricto cumplimiento de la normativa legal ecuatoriana sin incurrir jamás en coerción o ilegalidad.
</OBJETIVO_RECTOR>

<MARCO_NORMATIVO_Y_GUARDRAILS_ANTI_COERCION_ECUADOR>
Debes aplicar como barreras infranqueables de código y lenguaje:
1. Ley Orgánica de Defensa del Consumidor (Art. 49): Prohibición de hostigamiento, llamadas reiterativas que perturben la intimidad, cobranza vejatoria, exhibición ante terceros y cartas simulando mandatos judiciales inexistentes.
2. Horarios Legales Nacionales: Lunes a Viernes de 08:00 a 19:00; Sábados de 09:00 a 13:00. Queda terminantemente bloqueado todo contacto en domingos y feriados.
3. Ley Orgánica de Protección de Datos Personales (LOPDP): Valida identidad (últimos dígitos de cédula/RUC) antes de revelar saldos. Jamás expongas deudas a cónyuges, familiares, socios o empleados sin autorización expresa.
4. Código Orgánico Integral Penal (COIP Art. 154): Prohibición absoluta de intimidación. Ninguna deuda civil conlleva privación de libertad (Art. 66 num. 29 Constitución del Ecuador).
5. Código Orgánico General de Procesos (COGEP):
   - Art. 347: Títulos Ejecutivos (Pagaré a la orden con aceleración, letra de cambio) -> Vía Ejecutiva con medidas cautelares (Art. 351).
   - Art. 356: Documentos privados, facturas impagas <= 50 SBU -> Procedimiento Monitorio.
   - Monitorea la prescripción de la acción cambiaria (3 años / 1.095 días según Código de Comercio).
</MARCO_NORMATIVO_Y_GUARDRAILS_ANTI_COERCION_ECUADOR>

<MOTOR_DE_NEUROCOBRANZA_Y_ARQUETIPOS>
Identifica y modula la interacción según el perfil neurocognitivo del cliente:
1. Aversivo al Conflicto (Cortisol alto / Bloqueo): Canal WhatsApp asíncrono con botón de autogestión directa. Tono empático, alivio de estrés, sin confrontación.
2. Racional / Calculador (Neocórtex analítico): Canal llamada consultiva o correo formal. Matriz de ahorro financiero: demuéstrale el ahorro exacto en dólares por condonación de intereses de mora y honorarios.
3. Circunstancial / Cooperativo (Límbico-empático): Canal llamada telefónica. Reconoce su historial crediticio impecable previo, genera reciprocidad y pacta un abono solidario.
4. Reactivo / Defensivo (Amígdala en lucha): Canal llamada protocolar. Escucha activa, neutraliza el ego, desglosa el saldo contable al centavo y elimina cualquier indicio de juicio personal.
5. Postergador / Optimismo Ilusorio (Sesgo del presente): Canal llamada con anclaje firme. Exige abono inicial del 20-30% en 72h con fechas e hitos fijos verificables.
</MOTOR_DE_NEUROCOBRANZA_Y_ARQUETIPOS>

<ESCALERA_ESTRATEGICA_DE_RESOLUCION_LADDER>
Aplica la jerarquía de prioridades de menor a mayor esfuerzo procesal:
- PRIORIDAD 1 (Pago Efectivo Inmediato Contrastable): Condonación total de gastos de cobranza e intereses de mora a cambio de liquidación total o parcial en < 48 horas.
- PRIORIDAD 2 (Compromiso Fuerte con Abono Inicial): Exigencia de un down payment del 20% al 30% en 72 horas para suspender la derivación legal, difiriendo el remanente en 2 a 3 cuotas fijas cortas.
- PRIORIDAD 3 (Reestructuración / Refinanciamiento MYPE): Adecuación del plazo y cuotas al ciclo productivo real del microempresario, preservando la viabilidad económica del negocio.
- PRIORIDAD 4 (Escalado Prejudicial y Notificación Formal): Envío de requerimiento notarial previo o ingreso de demanda ejecutiva (COGEP 347) / monitoria (COGEP 356) con solicitud de medidas cautelares sobre cuentas bancarias o garantías.
</ESCALERA_ESTRATEGICA_DE_RESOLUCION_LADDER>

<PROTOCOLO_OPERATIVO_DEL_GUION_EN_6_PASOS>
Cada interacción telefónica o digital debe cumplir estrictamente:
Paso 1: Pre-llamada (revisión de saldo, mora, pagaré, prescripción y LTV).
Paso 2: Apertura respetuosa y desescaladora de cortisol.
Paso 3: Validación segura de identidad según LOPDP.
Paso 4: Propuesta comercial de alta velocidad (mayor recuperación en menor tiempo).
Paso 5: Manejo persuasivo y ético de la objeción específica de la MYPE.
Paso 6: Cierre con compromiso firme (monto exacto, fecha límite, cuenta bancaria y trazabilidad).
</PROTOCOLO_OPERATIVO_DEL_GUION_EN_6_PASOS>

<FORMATO_DE_RESPUESTA_JSON_REQUERIDO>
Cuando se solicite el análisis de un caso o lote de cartera, responde con la siguiente estructura JSON válida:
{
  "rotulo": "SIMULACIÓN CALIBRADA — NO APTO PARA DECISIONES REALES",
  "id_caso": "SIM-XXXXX",
  "diagnostico_financiero": {
    "saldo_total_usd": 0.0,
    "capital_usd": 0.0,
    "interes_mora_usd": 0.0,
    "gastos_cobranza_usd": 0.0,
    "bucket_mora": "B0-B6",
    "cuadre_contable_valido": true
  },
  "diagnostico_legal_cogep": {
    "via_procesal": "Ejecutivo (347) | Monitorio (356)",
    "dias_para_prescripcion": 0,
    "riesgo_prescripcion": "Crítico (<180d) | Medio | Bajo",
    "garantia_ejecutable": "Hipotecaria | Prendaria | Codeudor | Ninguna",
    "medida_cautelar_optima": "Retención fondos BCE/SPE | Prohibición enajenar"
  },
  "perfil_neurocognitivo": {
    "arquetipo": "Aversivo | Racional | Circunstancial | Reactivo | Postergador",
    "nivel_cortisol": "Alto | Medio | Controlado",
    "gatillador_etico": "Ahorro financiero | Reciprocidad | Alivio de estrés | Anclaje",
    "canal_optimo": "WhatsApp | Llamada telefónica | Portal web"
  },
  "prescripcion_operativa": {
    "prioridad_estrategica": "P1 | P2 | P3 | P4",
    "escalon_resolucion": "Pago Inmediato 48h | Abono 30% 72h | Reestructuración | Prejudicial",
    "next_best_action": "Acción inmediata prescriptiva para el gestor"
  },
  "guion_operativo_6_pasos": {
    "paso_1_preparacion": "...",
    "paso_2_apertura": "...",
    "paso_3_validacion_lopdp": "...",
    "paso_4_propuesta_alta_velocidad": "...",
    "paso_5_manejo_objecion": "...",
    "paso_6_cierre_compromiso": "..."
  },
  "mensaje_digital_whatsapp": "Texto persuasivo listo con enlace de pago seguro",
  "bitacora_para_notebooklm": "Síntesis narrativa ejecutiva del caso para análisis RAG"
}
</FORMATO_DE_RESPUESTA_JSON_REQUERIDO>"""
    
    r_code = p_code.add_run(PROMPT_MAESTRO_TEXT)
    r_code.font.name = "Consolas"
    r_code.font.size = Pt(8.5)
    r_code.font.color.rgb = RGBColor(26, 54, 93)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # SECCIÓN 7: GUÍA DE DESPLIEGUE MULTI-ARNÉS
    h1 = doc.add_heading("7. Guía de Adaptación Operativa Multi-Arnés (Gemini, Claude, Codex)", level=1)
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "Dado que el equipo de trabajo opera simultáneamente sobre distintos entornos de modelos de lenguaje de última generación, a continuación se establecen las pautas de inyección y optimización para cada arnés específico:"
    )
    
    # 7.1 Google Gemini
    doc.add_heading("7.1. Inyección en Google Gemini (Gemini 1.5 Pro / 2.0 / 3.8 Flash)", level=2)
    p = doc.add_paragraph()
    p.add_run("• Ubicación de Inyección: ").bold = True
    p.add_run("Configurar en la sección 'System Instructions' de Google AI Studio o pasar como parámetro system_instruction en el SDK de Python de Google GenAI.\n")
    p.add_run("• Ventaja Estratégica: ").bold = True
    p.add_run("Aprovechar la ventana de contexto de 1 millón a 2 millones de tokens para subir íntegramente la tabla de 1.000 registros sintéticos (cartera_calibrada_multidimensional_1000.csv) en una sola llamada, permitiendo consultas cruzadas instantáneas de toda la cartera.\n")
    p.add_run("• Temperatura Recomendada: ").bold = True
    p.add_run("0.2 para análisis contable/legal determinístico; 0.4 para generación de guiones adaptativos y roleplay de cobranza.")
    
    # 7.2 Anthropic Claude Code
    doc.add_heading("7.2. Inyección en Anthropic Claude Code (Claude 3.5 Sonnet / Opus)", level=2)
    p = doc.add_paragraph()
    p.add_run("• Ubicación de Inyección: ").bold = True
    p.add_run("Integrar como directriz de sistema en el archivo CLAUDE.md en la raíz del proyecto o invocar como system prompt.\n")
    p.add_run("• Ventaja Estratégica: ").bold = True
    p.add_run("Excepcional rigor en el seguimiento de etiquetas XML y cumplimiento de directrices éticas y legales negativas (cero alucinación normativa y respeto estricto a las prohibiciones de la Ley de Defensa del Consumidor).\n")
    p.add_run("• Temperatura Recomendada: ").bold = True
    p.add_run("0.1 a 0.25 para mantener consistencia lógica estricta y cuadre financiero al centavo.")
    
    # 7.3 OpenAI Codex / ChatGPT
    doc.add_heading("7.3. Inyección en OpenAI Codex / ChatGPT (GPT-4o / o1 / o3-mini)", level=2)
    p = doc.add_paragraph()
    p.add_run("• Ubicación de Inyección: ").bold = True
    p.add_run("Configurar en el campo 'Developer Message' de la API o 'Custom Instructions' de ChatGPT.\n")
    p.add_run("• Ventaja Estratégica: ").bold = True
    p.add_run("Uso de la modalidad 'Structured Outputs' (response_format: json_schema) para forzar que el modelo siempre retorne el JSON estricto sin texto adicional ni preámbulos.\n")
    p.add_run("• Temperatura Recomendada: ").bold = True
    p.add_run("0.2 para operaciones de filtrado y scoring predictivo.")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # SECCIÓN 8: CASOS DIDÁCTICOS DE ENTRENAMIENTO Y ROLEPLAY
    h1 = doc.add_heading("8. Casos Didácticos de Entrenamiento y Roleplay para el Equipo", level=1)
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "A continuación se extraen 3 casos representativos de la cartera calibrada de 1.000 clientes para guiar las sesiones de simulación y entrenamiento del equipo de gestores:"
    )
    
    cases = [
        ("Caso 1: SIM-00142 | Transporte Escolar y Logística (Mora 48 días)",
         "Saldo: USD 3.840,00 | Bucket: B2 (Administrativa) | Título: Pagaré a la orden | Arquetipo: Racional / Calculador\n"
         "Situación: El cliente posterga el pago porque un contrato institucional no le ha liquidado su planilla. Si el gestor lo presiona agresivamente, el cliente se cierra.\n"
         "Estrategia SIGEC-EC: Canal llamada telefónica. El gestor presenta un cuadro numérico: condonación de USD 214,00 en mora y recargos si cancela el capital vencido en 48 horas mediante transferencia directa, ahorrándole un 15% del costo de financiamiento. Resultado: Compromiso cerrado con fecha fija."),
        ("Caso 2: SIM-00518 | Comercio Minorista de Alimentos (Mora 115 días)",
         "Saldo: USD 1.950,00 | Bucket: B4 (Tardía) | Título: Facturas (Monitorio) | Arquetipo: Aversivo al Conflicto\n"
         "Situación: El cliente no atiende llamadas por miedo al cobrador y vergüenza social; nivel de cortisol al tope.\n"
         "Estrategia SIGEC-EC: Canal WhatsApp asíncrono con mensaje empático y desescalador. Se le ofrece suspender el envío a asesoría jurídica externa si abona USD 400,00 en 72 horas y difiere el saldo en 3 microcuotas quincenales, adjuntando botón de pago DeUna/Transferencia. Resultado: Lectura positiva y pago del abono en 24 horas."),
        ("Caso 3: SIM-00891 | Taller de Metalmecánica (Mora 210 días)",
         "Saldo: USD 12.450,00 | Bucket: B5 (Vencida) | Título: Pagaré con Garantía Prendaria (LTV 0.42) | Arquetipo: Postergador Crónico\n"
         "Situación: Registra 5 promesas incumplidas en los últimos 12 meses (Kept Rate: 0.15). Manifiesta siempre 'la próxima semana cobro y les paso todo'.\n"
         "Estrategia SIGEC-EC: Canal notificación formal y llamada ejecutiva. Se le notifica de la auditoría del pagaré y la viabilidad de aprehensión del bien prendado (COGEP Art. 351), condicionando cualquier reestructuración a la consignación inmediata del 30% del saldo (USD 3.735,00) en 72 horas. Resultado: Ruptura del patrón de postergación y recuperación líquida de USD 3.735,00.")
    ]
    
    for c_title, c_body in cases:
        p_c = doc.add_paragraph()
        r1 = p_c.add_run(f"• {c_title}\n"); r1.bold = True; r1.font.color.rgb = RGBColor(26, 54, 93)
        r2 = p_c.add_run(c_body)
        p_c.paragraph_format.space_after = Pt(6)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # SECCIÓN 9: CONCLUSIONES Y PRÓXIMOS PASOS
    h1 = doc.add_heading("9. Conclusiones y Hoja de Ruta para el Despliegue Local", level=1)
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "La implementación de este sistema automatizado permite dar el salto cualitativo de una cobranza reactiva, mecánica y potencialmente coercitiva, hacia una gestión estratégica de alta precisión quirúrgica, donde cada minuto del gestor se invierte en el cliente con mayor probabilidad de retorno y con el mensaje neuroconductual exacto para cerrar el pago."
    )
    
    p_steps = doc.add_paragraph()
    r = p_steps.add_run("Hoja de Ruta Inmediata para el Equipo:\n"); r.bold = True
    p_steps.add_run("1. Distribuir este documento a los docentes, instructores y miembros del equipo de cobranzas.\n")
    p_steps.add_run("2. Cargar el Prompt Maestro de la Sección 6 en sus respectivos arneses de IA (Gemini, Claude o Codex).\n")
    p_steps.add_run("3. Vincular la base calibrada de 1.000 clientes (datos_sinteticos/cartera_calibrada_multidimensional_1000.csv) en NotebookLM o en el script de visualización local.\n")
    p_steps.add_run("4. Ejecutar las sesiones de entrenamiento guiadas con los casos didácticos y medir la tasa de conversión simulada.")
    
    # GUARDADO DEL ARCHIVO
    output_path = "D:\\MEGA\\2026\\LIDERAZGO\\diplomado cobranzas\\PROMPT_MAESTRO_SISTEMA_GESTION_COBRANZA_ECUADOR.docx"
    doc.save(output_path)
    print(f"Documento generado exitosamente en: {output_path}")

if __name__ == "__main__":
    main()

