# Paquete Didáctico y Entorno de Simulación Calibrada de Cobranzas (v2.0)

Este entorno ha sido diseñado para la **preparación, entrenamiento y fortalecimiento de capacidades de equipos de cobranzas** mediante el uso de herramientas de **Inteligencia Artificial (NotebookLM, Modelos LLM, Python y Análisis Predictivo)**, orientado al objetivo estratégico de **recuperar la mayor cantidad de dinero en el menor tiempo posible** con estricto apego a la normativa jurídica ecuatoriana, las mejores prácticas financieras y la neurocobranza científica.

---

## 1. Inventario de Archivos del Entorno

1. `cartera_calibrada_multidimensional_1000.csv`:
   - **Tabla Maestra Completa (62 variables, 1.000 registros sintéticos)**.
   - Integra todas las dimensiones: demográfica, contable-financiera, procesal-jurídica (COGEP), neuroconductual, scoring probabilístico calibrado, guiones telefónicos en 6 pasos, mensajes WhatsApp y bitácoras narrativas de caso.
2. `cartera_demo_1000.csv`:
   - Versión estandarizada y corregida al 100% (cero cuotas inválidas, balance contable perfecto al centavo). Conserva compatibilidad con tableros y modelos previos.
3. `guiones_llamada_personalizados_1000.csv` / `guiones_llamada_simulados_calibrados.csv`:
   - 1.000 guiones de llamada estructurados en 6 pasos operativos, correlacionados unívocamente con el saldo, mora, título ejecutivo, arquetipo de neuroindividuo y estrategia de alta velocidad de recuperación.
4. `prompt_maestro_cobranza.json`:
   - Directrices del sistema (v2.0) para alimentar agentes de IA y NotebookLM con esquemas de salida JSON y análisis multidimensional.
5. `backup_original/`:
   - Respaldo de seguridad inmutable de los archivos iniciales previos a la calibración.

---

## 2. Marco Metodológico y Dimensiones Integradas

### A. Dimensión Financiera y Contable
* **Identidad Contable Rigurosa:**
  $$\text{Saldo Total} = \text{Capital Total} + \text{Interés Ordinario} + \text{Interés de Mora Legal} + \text{Gastos Normados}$$
* **Cuotas Estrictas:** $cuotas\_vencidas \le cuotas\_totales$ garantizado en el 100% de los casos.
* **Cubos de Mora Estandarizados (Aging Buckets):**
  - **B0:** Preventiva (1-15 días)
  - **B1:** Temprana (16-30 días)
  - **B2:** Administrativa (31-60 días)
  - **B3:** Media (61-90 días)
  - **B4:** Tardía / Prejudicial (91-180 días)
  - **B5:** Vencida / Deterioro Severo (181-360 días)
  - **B6:** Castigada (>360 días)

### B. Dimensión Jurídica y Procesal (República del Ecuador)
* **Títulos Ejecutivos vs. Monitorio (COGEP):**
  - *Juicio Ejecutivo (Art. 347 COGEP):* Pagarés a la orden con cláusula de aceleración y letras de cambio.
  - *Procedimiento Monitorio (Art. 356 COGEP):* Obligaciones dinerarias $\le 50 \text{ SBU}$ derivadas de facturas o documentos privados.
* **Prescripción Cambiaria (Código de Comercio):** 3 años (1.095 días) desde la fecha de vencimiento. Monitoreo de alertas preventivas (<12m) y críticas (<6m).
* **Garantías y Medidas Cautelares (Art. 351 COGEP):**
  - Garantía Hipotecaria (con cálculo de $LTV = \text{Saldo} / \text{Avalúo}$ y prohibición de enajenar).
  - Garantía Prendaria (con reserva de dominio y orden de embargo/aprehensión).
  - Codeudor Solidario (con renuncia a beneficios de orden y excusión).
  - Retención de fondos en el sistema financiero (vía SPE / Banco Central del Ecuador).
* **Protección al Deudor y LOPDP:** Contacto restringido a horarios legales (L-V 08h00-19h00, Sáb 09h00-13h00; domingos y feriados prohibidos) y verificación de consentimiento para canales electrónicos.

### C. Dimensión del Neuroindividuo y Neurocobranza Científica
* **Tríada Cerebral en Mora:** Regulación del cerebro reptil (instinto de amenaza y huida/lucha), límbico (vergüenza social, culpa) y activación del neocórtex mediante la desescalada del cortisol.
* **Taxonomía de 5 Arquetipos Neurocognitivos:**
  1. *Aversivo al conflicto (Sobrecarga de cortisol):* Parálisis por estrés. Canal óptimo: WhatsApp formal asíncrono y portal de autogestión sin fricción.
  2. *Racional / Calculador (Neocórtex analítico):* Evalúa costo-beneficio. Canal óptimo: Cuadros comparativos de ahorro financiero de intereses de mora y quitas al contado.
  3. *Circunstancial / Cooperativo (Empático-Límbico):* Intención de pago afectada por shock fortuito. Estrategia: Reciprocidad y abono inicial con micro-cuotas.
  4. *Reactivo / Defensivo (Cerebro reactivo/lucha):* Inconformidad y desconfianza. Estrategia: Transparencia contable, validación de objeciones y neutralización de ego.
  5. *Postergador / Optimismo Ilusorio:* Sesgo de presente y promesas diferidas. Estrategia: Compromiso y coherencia de Cialdini con hitos de pago fijos y recordatorios 24h antes.

### D. Estrategia de Alta Velocidad (Mayor Recuperación en Menor Tiempo)
Cada registro contiene la estrategia óptima para acelerar la entrada de liquidez:
* **Condonación del 100% de gastos/mora por pago total en 48 horas:** Incentivo inmediato de caja líquida en mora temprana y media.
* **Abono inicial del 30% en 72 horas y saldo en 3 cuotas fijas:** Entrada inmediata de capital y mitigación de mora.
* **Quitas condicionales sobre intereses en cartera vencida:** Recuperación de capital estancado antes del castigo contable.
* **Mediación y Medidas Cautelares Rápidas:** Para casos de alta capacidad económica con reticencia de pago.

---

## 3. Diccionario Resumido de Variables Clave

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id_caso` | String | Identificador unívoco sintético (`SIM-00001` a `SIM-01000`). |
| `saldo_usd` | Float | Saldo total exacto ($Capital + Interés + Mora + Gastos$). |
| `dias_mora` | Integer | Días transcurridos desde el vencimiento de la cuota más antigua impaga. |
| `bucket_mora` | String | Tramo técnico normativo (B0 a B6). |
| `titulo_ejecutivo_tipo` | String | Instrumento que respalda la obligación (Pagaré, Letra, Factura). |
| `via_procesal_idonea` | String | Vía según COGEP (Ejecutivo, Monitorio, Ordinario). |
| `arquetipo_neurocognitivo` | String | Perfil psicológico y conductual del deudor. |
| `nivel_estres_cortisol` | String | Nivel de estrés y reactividad fisiológica inferida. |
| `gatillador_persuasivo_optimo` | String | Palanca de persuasión e influencia ética (Cialdini/Kahneman). |
| `prob_pago_30d_calibrada` | Float | Probabilidad logística calibrada ($P \in [0.02, 0.95]$). |
| `recuperacion_esperada_30d_usd` | Float | Valor esperado en USD a recuperar en los próximos 30 días. |
| `estrategia_recuperacion_maxima` | String | Oferta financiera orientada a la máxima velocidad de cobro. |
| `next_best_action` | String | Acción prescriptiva operativa inmediata para el gestor o bot IA. |
| `guion_llamada_personalizado` | Text | Guion telefónico estructurado en 6 pasos hiper-personalizado. |
| `mensaje_whatsapp_personalizado` | Text | Mensaje digital persuasivo omnicanal con botón de pago. |
| `bitacora_narrativa_caso` | Text | Resumen ejecutivo del expediente para análisis en NotebookLM. |

---

## 4. Guía de Uso para Entrenamiento con Inteligencia Artificial

### Uso en NotebookLM:
1. Cargue `cartera_calibrada_multidimensional_1000.csv` o `README.md` como fuente de conocimiento.
2. Solicite a NotebookLM:
   - *"Identifica los 10 casos con mayor recuperación esperada inmediata y dime el guion y canal que debe usar el asesor hoy mismo."*
   - *"Compara la estrategia para un deudor Aversivo al conflicto frente a un Racional Calculador en mora de 45 días."*
   - *"Genera un informe de riesgo procesal sobre las cuentas que están a menos de 180 días de prescribir la acción cambiaria."*

### Uso en Modelos LLM y Chatbots de Simulación:
- Inyecte el archivo `prompt_maestro_cobranza.json` como System Prompt.
- Entrene a los asesores haciendo roleplay donde la IA interpreta a un deudor según el `arquetipo_neurocognitivo` y evalúa si el gestor sigue los 6 pasos del guion personalizado.

---
*Rótulo obligatorio: SIMULACIÓN CALIBRADA / DATOS SINTÉTICOS DIDÁCTICOS / NO APTO PARA DECISIONES REALES.*
