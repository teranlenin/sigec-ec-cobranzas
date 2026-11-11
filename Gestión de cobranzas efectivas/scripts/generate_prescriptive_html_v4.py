# -*- coding: utf-8 -*-
"""
Genera el reporte HTML dinámico, autónomo e interactivo v4 con:
1) Diagnóstico conductual 1 a 1 real desde `events.jsonl` y `cases.csv` (`reporting_synthetic_v3`),
2) Comparativo macro Antes -> Después (v3) -> Proyección Estocástica con Estrategia 1 a 1 (SEPS / NIIF 9 / Gestores),
3) Catálogo interactivo de opciones (condonación, suavización de tasa, reducción de cuotas, abono vinculante,
   período de gracia, indicador VPN y gobernanza Gestor/Supervisor),
4) Matriz de medidas Preventivas, Coercitivas Lícitas (Prejudiciales / Mediación) y Acción Legal (COGEP Ecuador),
5) Guiones de Neurocobranza 4 Fases + SMS/WhatsApp + Email + Citación Mediación listos para copiar,
6) Síntesis integrada de los 4 cuadernos de NotebookLM (207 fuentes).

IMPORTANTE: No modifica ni sobrescribe el archivo previo v3.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "Gestión de cobranzas efectivas" / "data" / "reporting_synthetic_v3"
CASES_CSV = DATA_DIR / "cases.csv"
EVENTS_JSONL = DATA_DIR / "events.jsonl"
OUT_REPORT_HTML = DATA_DIR / "reports" / "comparativo_prescriptivo_1a1_quito_2026-11-10_v4.html"
OUT_VERCEL_HTML = ROOT / "public" / "comparativo_v4.html"

CHANNEL_LABELS = {
    "whatsapp_message": "WhatsApp Formal",
    "phone_call": "Llamada Consultiva",
    "email": "Correo Electrónico",
    "sms": "SMS Recordatorio",
    "written_notice": "Notificación Escrita / Mediación",
    "none": "Bloqueado / Sin Canal",
}


def _cents(val: Any) -> int:
    return round(float(val or 0.0) * 100)


def _usd(cents: int) -> float:
    return round(cents / 100.0, 2)


def _aging_bucket(dpd: int, cured: bool) -> str:
    if cured:
        return "CURADO_SIMULADO"
    if dpd <= 30:
        return "DPD_001_030"
    if dpd <= 60:
        return "DPD_031_060"
    if dpd <= 90:
        return "DPD_061_090"
    if dpd <= 120:
        return "DPD_091_120"
    if dpd <= 180:
        return "DPD_121_180"
    if dpd <= 360:
        return "DPD_181_360"
    return "DPD_361_560"


def _seps_and_ifrs9(dpd: int, cured: bool) -> tuple[str, str]:
    """Calificación referencial SEPS (escala Consumo/Microcrédito) y Etapa NIIF 9."""
    if cured or dpd == 0:
        return ("Normal A1 (0d)", "Etapa 1 (12m ECL)")
    if dpd <= 15:
        return ("Normal A2 (1-15d)", "Etapa 1 (12m ECL)")
    if dpd <= 30:
        return ("Normal A3 (16-30d)", "Etapa 1 (12m ECL)")
    if dpd <= 45:
        return ("Potencial B1 (31-45d)", "Etapa 2 (SICR Lifetime)")
    if dpd <= 60:
        return ("Potencial B2 (46-60d)", "Etapa 2 (SICR Lifetime)")
    if dpd <= 75:
        return ("Deficiente C1 (61-75d)", "Etapa 2 (Lifetime ECL)")
    if dpd <= 90:
        return ("Deficiente C2 (76-90d)", "Etapa 2 (Límite Pre-Default)")
    if dpd <= 120:
        return ("Dudoso Recaudo D (91-120d)", "Etapa 3 (Default NIIF 9)")
    return ("Pérdida E (>120d)", "Etapa 3 (Default NIIF 9)")


def build_case_records() -> list[dict[str, Any]]:
    with CASES_CSV.open("r", encoding="utf-8-sig") as f:
        raw_cases = list(csv.DictReader(f))

    events_by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with EVENTS_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            cid = ev.get("case_id")
            if cid:
                events_by_case[cid].append(ev)

    processed: list[dict[str, Any]] = []

    for row in raw_cases:
        cid = row["case_id"]
        evs = sorted(events_by_case[cid], key=lambda x: (x["occurred_at"], x["event_id"]))

        open_prin = _cents(row["opening_principal_usd"])
        open_int = _cents(row["opening_interest_usd"])
        open_oth = _cents(row["opening_other_usd"])
        open_bal = _cents(row["opening_balance_usd"])
        dpd_start = int(row["days_past_due_at_start"])

        paid_tot = 0
        paid_prin = 0
        paid_int = 0
        paid_oth = 0
        pay_cnt = 0

        commitments: dict[str, dict[str, Any]] = {}
        replied_ch: list[str] = []
        failed_ch: list[str] = []
        draft_ch: list[str] = []
        dispute_open = row.get("dispute_status", "") == "open"
        human_review = False
        updates_cnt = 0
        findings: list[str] = []
        timeline: list[dict[str, str]] = []

        for ev in evs:
            et = ev.get("event_type", "")
            dt_short = ev.get("occurred_at", "")[:10]
            if et == "payment_recorded_simulated":
                amt = _cents(ev.get("amount_usd"))
                paid_tot += amt
                paid_prin += _cents(ev.get("allocation_principal_usd"))
                paid_int += _cents(ev.get("allocation_interest_usd"))
                paid_oth += _cents(ev.get("allocation_other_usd"))
                pay_cnt += 1
                timeline.append({"d": dt_short, "t": "Pago", "x": f"${amt/100:,.2f}"})
            elif et in ("commitment_created_simulated", "commitment_status_changed_simulated"):
                com_id = ev.get("commitment_id")
                if com_id:
                    commitments[com_id] = ev
                st = ev.get("commitment_status", "")
                if et == "commitment_created_simulated":
                    timeline.append({"d": dt_short, "t": "Compromiso creado", "x": f"${float(ev.get('amount_due_usd',0)):,.2f}"})
                else:
                    timeline.append({"d": dt_short, "t": "Estado compromiso", "x": str(st)})
            elif et == "channel_attempt_simulated":
                ch = ev.get("channel", "unknown")
                out = ev.get("outcome", "")
                if out == "reply_simulated":
                    replied_ch.append(ch)
                elif out == "no_response_simulated":
                    failed_ch.append(ch)
                else:
                    draft_ch.append(ch)
                timeline.append({"d": dt_short, "t": f"Canal ({ch})", "x": out})
            elif et == "dispute_opened_simulated":
                dispute_open = True
                timeline.append({"d": dt_short, "t": "Disputa abierta", "x": "Requiere auditoría"})
            elif et == "internal_review_simulated":
                human_review = True
                timeline.append({"d": dt_short, "t": "Revisión humana", "x": str(ev.get("review_outcome", ""))})
            elif et == "contact_data_update_simulated":
                updates_cnt += 1
                timeline.append({"d": dt_short, "t": "Dato actualizado", "x": str(ev.get("field_name", ""))})
            elif et == "research_finding_simulated":
                ft = str(ev.get("finding_type", "hallazgo"))
                findings.append(ft)
                timeline.append({"d": dt_short, "t": "Investigación", "x": ft})

        close_bal = max(0, open_bal - paid_tot)
        cured = close_bal == 0
        rem_prin = max(0, open_prin - paid_prin)
        rem_int = max(0, open_int - paid_int)
        rem_oth = max(0, open_oth - paid_oth)
        if cured:
            rem_prin = rem_int = rem_oth = 0
        else:
            diff = close_bal - (rem_prin + rem_int + rem_oth)
            rem_prin = max(0, rem_prin + diff)

        dpd_curr = 0 if cured else dpd_start + 8
        bucket_start = _aging_bucket(dpd_start, False)
        bucket_end = _aging_bucket(dpd_curr, cured)
        seps_cat, ifrs9_stage = _seps_and_ifrs9(dpd_curr, cured)

        c_states = Counter(v.get("commitment_status", "unknown") for v in commitments.values())
        kept = c_states["kept"]
        missed = c_states["missed"]
        pending = c_states["pending"] + c_states["accepted"]
        cancelled = c_states["cancelled"]

        # 1. Perfil Conductual 1 a 1 (basado en trazabilidad de eventos reales)
        if cured:
            profile = "Curado Simulado (Saldo $0)"
        elif dispute_open or human_review:
            profile = "Bloqueado Normativo (Disputa / Revisión)"
        elif missed > 0:
            profile = "Postergador con Promesa Rota"
        elif kept > 0 or pay_cnt > 0:
            profile = "Cooperativo Activo (Cumplidor / Pagador)"
        elif len(replied_ch) > 0:
            profile = "Receptivo sin Pago Concretado"
        elif len(failed_ch) > 0:
            profile = "Silencio / Canal Remoto Agotado"
        else:
            profile = "Sin Contacto Efectivo Previo"

        # 2. Canal Óptimo Recomendado (Fallback WhatsApp -> Llamada -> Email -> Escrito, pivotando fuera de fallidos)
        all_channels_priority = ["whatsapp_message", "phone_call", "email", "sms", "written_notice"]
        if cured:
            rec_channel = "email"
        elif dispute_open or human_review:
            rec_channel = "none"
        elif replied_ch:
            rec_channel = replied_ch[-1]
        else:
            untried = [ch for ch in all_channels_priority if ch not in failed_ch]
            if dpd_curr <= 60:
                pref = ["whatsapp_message", "sms", "email", "phone_call", "written_notice"]
            elif dpd_curr <= 180:
                pref = ["phone_call", "whatsapp_message", "email", "written_notice", "sms"]
            else:
                pref = ["written_notice", "phone_call", "whatsapp_message", "email", "sms"]
            rec_channel = next((ch for ch in pref if ch in untried), pref[0])

        # 3. Medida (Preventiva / Coercitiva Lícita / Acción Legal COGEP) y Paso Recomendado 1 a 1
        close_usd = _usd(close_bal)
        # Ref. Art. 356 COGEP: hasta 50 SBU (se anota como [P] sujeto a SBU vigente) vs. Art. 347 Título Ejecutivo
        via_cogep = (
            "Procedimiento Monitorio (Art. 356 COGEP, ref. ≤50 SBU)"
            if close_usd <= 23500
            else "Juicio Ejecutivo / Ordinario (Art. 347 COGEP + Cautelares Art. 351)"
        )

        if cured:
            measure = "Cierre / Paz y Salvo"
            best_step = "Emitir certificación de cancelación y fidelizar cliente sin fricción."
            prob_base = 1.0
            prob_action = 1.0
        elif dispute_open or human_review:
            measure = "Bloqueo Normativo (Abstención)"
            best_step = "CONGELAR cobro y coerción. Resolver auditoría documental / revisión humana (Art. 49 LODC)."
            prob_base = 0.08
            prob_action = 0.28
        elif profile == "Cooperativo Activo (Cumplidor / Pagador)":
            if dpd_curr <= 90:
                measure = "Preventiva / Facilitadora"
                best_step = (
                    f"Evitar migración a Etapa 2-3 NIIF 9: suavización de mora (75%) o reducción de cuota "
                    f"vía {CHANNEL_LABELS[rec_channel]} (Choice Architecture: 2 opciones)."
                )
                prob_base = 0.58
                prob_action = 0.84
            else:
                measure = "Preventiva / Facilitadora"
                best_step = (
                    f"Reestructuración con extensión 18-24m y reducción de cuota real (sin capitalización artificial) "
                    f"vía {CHANNEL_LABELS[rec_channel]}."
                )
                prob_base = 0.44
                prob_action = 0.72
        elif profile == "Postergador con Promesa Rota":
            if dpd_curr <= 180:
                measure = "Coercitiva Lícita (Prejudicial)"
                best_step = (
                    f"Exigir abono inicial vinculante (25%-30% en 72h) + convenio escrito vía {CHANNEL_LABELS[rec_channel]}; "
                    f"advertencia objetiva de Buró y citación a Centro de Mediación Quito."
                )
                prob_base = 0.24
                prob_action = 0.54
            else:
                measure = "Acción Legal COGEP"
                best_step = (
                    f"Auditar ejecutabilidad de títulos y emitir última citación a Mediación Quito (72h, Acta = Sentencia Art. 235 COGEP) "
                    f"previa a {via_cogep}."
                )
                prob_base = 0.16
                prob_action = 0.42
        elif dpd_curr <= 60:
            measure = "Preventiva / Facilitadora"
            best_step = (
                f"Contacto empático en horario legal (L-V 07h-20h, máx. 1/día) vía {CHANNEL_LABELS[rec_channel]} "
                f"con enlace de autoatención o suavización de tasa (proteger Etapa 1 NIIF 9)."
            )
            prob_base = 0.52
            prob_action = 0.78
        elif dpd_curr <= 180:
            if profile == "Receptivo sin Pago Concretado":
                measure = "Preventiva / Facilitadora"
                best_step = (
                    f"Aplicar Neurocobranza sobre canal receptivo ({CHANNEL_LABELS[rec_channel]}): "
                    f"cuota reducida (18m) o micro-meta de entrada verificando flujo de caja real."
                )
                prob_base = 0.36
                prob_action = 0.65
            else:
                measure = "Coercitiva Lícita (Prejudicial)"
                best_step = (
                    f"Consolidar acervo probatorio: requerimiento escrito formal al titular (sin terceros/trabajo) "
                    f"+ citación a Mediación Quito vía {CHANNEL_LABELS[rec_channel]}."
                )
                prob_base = 0.22
                prob_action = 0.48
        elif dpd_curr <= 360:
            if close_usd >= 10000 or profile == "Silencio / Canal Remoto Agotado":
                measure = "Coercitiva Lícita (Prejudicial)"
                best_step = (
                    f"Notificación escrita formal (sin simular embargo) + oferta aprobada por Supervisor de quita 100% mora "
                    f"contra abono 30% en 72h; evaluar retención/prohibición Art. 126/130 COGEP."
                )
                prob_base = 0.17
                prob_action = 0.41
            else:
                measure = "Coercitiva Lícita (Prejudicial)"
                best_step = (
                    f"Citación a Centro de Mediación Quito y plan de cuotas reducidas a 24m vía {CHANNEL_LABELS[rec_channel]}."
                )
                prob_base = 0.20
                prob_action = 0.45
        else:
            # > 360 DPD
            measure = "Acción Legal COGEP"
            best_step = (
                f"Evaluar Cost-to-Collect vs. solvencia y prescripción cambiaria; iniciar {via_cogep} "
                f"(mantener salida de finiquito aprobado con 30% de entrada)."
            )
            prob_base = 0.10
            prob_action = 0.33

        processed.append({
            "id": cid,
            "mgr": row["manager_id"],
            "op": _usd(open_prin),
            "oi": _usd(open_int),
            "oo": _usd(open_oth),
            "ob": _usd(open_bal),
            "paid": _usd(paid_tot),
            "cb": close_usd,
            "rp": _usd(rem_prin),
            "ri": _usd(rem_int),
            "ro": _usd(rem_oth),
            "dpd0": dpd_start,
            "dpd": dpd_curr,
            "b0": bucket_start,
            "b1": bucket_end,
            "seps": seps_cat,
            "ifrs": ifrs9_stage,
            "pc": pay_cnt,
            "ck": kept,
            "cm": missed,
            "cp": pending,
            "cx": cancelled,
            "rep": replied_ch,
            "fail": failed_ch,
            "drf": draft_ch,
            "disp": 1 if dispute_open else 0,
            "rev": 1 if human_review else 0,
            "upd": updates_cnt,
            "fnd": len(findings),
            "prof": profile,
            "ch": rec_channel,
            "meas": measure,
            "step": best_step,
            "via": via_cogep,
            "pb": round(prob_base, 2),
            "pa": round(prob_action, 2),
            "tl": timeline[-8:],
        })

    return processed


HTML_TEMPLATE = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SIGEC-EC v4 | Comparativo Prescriptivo 1 a 1 &amp; Catálogo de Recuperación (Quito, Ecuador)</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚖️</text></svg>">
<style>
:root{
  --navy:#0b1f35;--navy2:#133858;--teal:#0e9f87;--teal-soft:#e6f7f4;--ink:#162b3a;--muted:#5b6e7f;
  --paper:#f3f6f8;--card:#ffffff;--line:#d9e2e8;--amber:#d97706;--amber-bg:#fffbeb;--red:#dc2626;--red-bg:#fef2f2;--blue:#1d4ed8;--blue-bg:#eff6ff;
  --shadow:0 8px 28px rgba(11,31,53,.07);--radius:14px;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:14px/1.5 "Segoe UI",Inter,system-ui,sans-serif}
button,select,input{font:inherit}button{cursor:pointer}
.wrap{max-width:1480px;margin:0 auto;padding:0 22px 48px}
.hero{margin:0 -22px 18px;padding:26px max(22px,calc((100vw - 1436px)/2));background:linear-gradient(125deg,var(--navy),#143c58 70%,#0f5c64);color:#f3f9fb}
.hero-grid{display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center}
.eyebrow{font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#8de0c8}
.hero h1{margin:6px 0 8px;font-size:clamp(22px,3vw,36px);line-height:1.1;letter-spacing:-.02em}
.hero p{margin:0;color:#c8dce5;max-width:900px;font-size:13.5px}
.stamp{padding:14px 18px;border-radius:12px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.2);text-align:right;min-width:250px}
.stamp span{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#bfd6df}
.stamp strong{display:block;font-size:24px;color:#c8f169;margin-top:3px}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.pill{padding:5px 10px;border-radius:999px;font-size:11px;font-weight:700;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);color:#e2eef2}
.pill.warn{background:rgba(245,158,11,.18);border-color:rgba(245,158,11,.55);color:#fde68a}

.view-bar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;align-items:center;justify-content:space-between}
.view-tabs{display:flex;flex-wrap:wrap;gap:8px}
.vtab{padding:9px 15px;border-radius:10px;border:1px solid var(--line);background:#fff;color:var(--navy);font-weight:700;font-size:13px;box-shadow:0 2px 6px rgba(11,31,53,.04)}
.vtab.active{background:var(--navy);color:#fff;border-color:var(--navy)}
.vview{display:none}.vview.active{display:block}

.kpis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;margin-bottom:16px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:13px 14px;box-shadow:0 3px 12px rgba(11,31,53,.04)}
.kpi-lbl{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}
.kpi-val{font-size:20px;font-weight:800;color:var(--navy);margin-top:4px;font-variant-numeric:tabular-nums}
.kpi-sub{font-size:11px;color:var(--muted);margin-top:3px}
.kpi.teal .kpi-val{color:var(--teal)}

.filters{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.96);backdrop-filter:blur(10px);border:1px solid var(--line);border-radius:var(--radius);padding:12px 14px;margin-bottom:16px;box-shadow:var(--shadow)}
.fgrid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;align-items:end}
.fcol label{display:block;font-size:10px;font-weight:800;text-transform:uppercase;color:var(--muted);margin-bottom:4px}
.fcol select,.fcol input{width:100%;padding:8px 9px;border:1px solid var(--line);border-radius:8px;background:#fff;color:var(--ink);font-size:12px;font-weight:600}
.btn{padding:8px 12px;border-radius:8px;border:1px solid var(--line);background:#fff;color:var(--navy);font-size:12px;font-weight:700}
.btn:hover{border-color:var(--teal);background:var(--teal-soft)}
.btn-primary{background:var(--navy);color:#fff;border-color:var(--navy)}
.btn-primary:hover{background:var(--navy2)}
.btn-teal{background:var(--teal);color:#fff;border-color:var(--teal)}
.btn-teal:hover{background:#0b8570}

.main-split{display:grid;grid-template-columns:minmax(0,1.08fr) minmax(0,1.18fr);gap:16px;align-items:start}
.panel{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow)}
.panel-head{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.panel-head h2{margin:0;font-size:16px;color:var(--navy)}
.table-wrap{max-height:660px;overflow:auto;border:1px solid var(--line);border-radius:10px}
table{width:100%;border-collapse:collapse;font-size:12px}
th{position:sticky;top:0;background:var(--navy);color:#fff;text-align:left;padding:9px 8px;font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;z-index:2}
td{padding:8px;border-bottom:1px solid #eef2f5;vertical-align:middle}
tr.case-row{cursor:pointer;transition:background .12s}
tr.case-row:hover{background:#f0f9ff}
tr.case-row.selected{background:#e0f2fe;outline:2px solid var(--teal)}
.num{text-align:right;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:3px 7px;border-radius:999px;font-size:10px;font-weight:800;white-space:nowrap}
.b-prev{background:var(--teal-soft);color:#0f766e}
.b-coer{background:var(--amber-bg);color:#92400e;border:1px solid #fde68a}
.b-legal{background:var(--red-bg);color:#991b1b;border:1px solid #fecaca}
.b-lock{background:#fee2e2;color:#7f1d1d;border:1px solid #fca5a5}
.b-cur{background:#dcfce7;color:#166534}

.detail-sticky{position:sticky;top:86px;max-height:calc(100vh - 104px);overflow-y:auto}
.mini-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.mini-box{background:#f8fafc;border:1px solid var(--line);border-radius:9px;padding:9px}
.mini-box span{display:block;font-size:10px;color:var(--muted);font-weight:700}
.mini-box strong{display:block;font-size:13px;color:var(--navy);margin-top:2px}
.rec-banner{padding:12px 14px;border-radius:10px;background:linear-gradient(120deg,#ecfdf5,#f0f9ff);border:1px solid #a7f3d0;margin:10px 0}
.rec-banner h3{margin:0 0 4px;font-size:14px;color:#065f46}
.rec-banner p{margin:0;font-size:12.5px;color:#1e3a8a}

.tabs{display:flex;flex-wrap:wrap;gap:5px;border-bottom:1px solid var(--line);margin-top:10px}
.tab{border:0;background:transparent;padding:8px 10px;font-size:11.5px;font-weight:700;color:var(--muted);border-bottom:3px solid transparent}
.tab.active{color:var(--navy);border-bottom-color:var(--teal);background:#f8fafc}
.tab-pane{padding:12px 0;display:none}
.tab-pane.active{display:block}
.opt-card{border:1px solid var(--line);border-radius:10px;padding:12px;background:#fafcff;margin-bottom:10px}
.opt-card h4{margin:0 0 6px;font-size:13px;color:var(--navy);display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.gov-tag{font-size:10px;padding:2px 7px;border-radius:999px;background:#e0e7ff;color:#3730a3;font-weight:800}
.gov-tag.sup{background:#fef3c7;color:#92400e}
.ctrl-row{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:8px 0}
.ctrl-row label{font-size:11px;font-weight:700;color:var(--muted)}
.res-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:8px}
.res-box{background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px}
.res-box span{display:block;font-size:10px;color:var(--muted)}
.res-box strong{font-size:14px;color:var(--teal);font-variant-numeric:tabular-nums}
.alert-note{margin-top:8px;padding:7px 10px;border-radius:8px;background:var(--blue-bg);border:1px solid #bfdbfe;color:#1e40af;font-size:11px}
.script-box{width:100%;padding:10px;border:1px solid var(--line);border-radius:8px;background:#fff;font-family:Consolas,monospace;font-size:11.5px;color:var(--ink)}
.tl-list{display:grid;gap:5px;max-height:200px;overflow:auto}
.tl-item{display:flex;justify-content:space-between;font-size:11px;padding:5px 8px;background:#f8fafc;border-radius:6px;border:1px solid #eef2f5}

.comp-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-bottom:16px}
.bar-row{display:grid;grid-template-columns:165px 1fr 125px;gap:10px;align-items:center;margin-bottom:8px;font-size:11.5px}
.bar-track{height:16px;border-radius:999px;background:#e2e8f0;overflow:hidden;position:relative}
.bar-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--navy2),var(--teal))}
.nb-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.nb-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:15px;box-shadow:0 3px 10px rgba(11,31,53,.04)}
.nb-card h3{margin:0 0 8px;font-size:15px;color:var(--navy);display:flex;justify-content:space-between;align-items:center}
.nb-card ul{margin:6px 0 0;padding-left:18px;font-size:12.5px}
.nb-card li{margin-bottom:5px}

.footer{margin-top:26px;padding-top:14px;border-top:1px solid var(--line);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;font-size:11px;color:var(--muted)}
@media(max-width:1180px){.kpis{grid-template-columns:repeat(3,minmax(0,1fr))}.fgrid{grid-template-columns:repeat(3,minmax(0,1fr))}.main-split,.comp-grid,.nb-grid{grid-template-columns:1fr}.detail-sticky{position:static;max-height:none}}
@media(max-width:680px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.fgrid{grid-template-columns:1fr}.mini-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.res-grid{grid-template-columns:1fr}.hero-grid{grid-template-columns:1fr}.bar-row{grid-template-columns:1fr}}
@media print{.filters,.view-bar,.tabs,#caseTbody{font-size:11px}.detail-sticky{position:static;max-height:none}}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="hero-grid">
      <div>
        <div class="eyebrow">SIGEC-EC v4 · Motor Prescriptivo 1 a 1 · Comparativo v3 + Catálogo Ecuador · Base NotebookLM (207 Fuentes)</div>
        <h1>De Comparativo v3 a Gestión Prescriptiva 1 a 1 y Catálogo de Recuperación</h1>
        <p>Evolución operativa sobre <strong>comparativo_antes_despues_interactivo_2026-11-10_v3.html</strong> (Quito, Ecuador): identifica el perfil conductual real de cada cliente en el libro de eventos, proyecta la mejora incremental de recaudo y entrega un portafolio accionable (suavización de tasas, reducción de cuotas, abono vinculante, período de gracia, medidas preventivas, coercitivas lícitas y COGEP).</p>
        <div class="pills">
          <span class="pill warn">SIMULACIÓN — NO USAR EN PRODUCCIÓN / NO ENVIAR</span>
          <span class="pill">Datos: reporting_synthetic_v3 (1.000 casos · 3.231 eventos)</span>
          <span class="pill">Regla Ecuador (LODC / JB-2010-1782): Máx. 1 contacto/día · L-V 07h00–20h00 · 0 fines de semana/terceros · 0 visitas laborales (Art. 151 COMYF)</span>
        </div>
      </div>
      <div class="stamp">
        <span>Saldo Actual Filtrado</span>
        <strong id="heroClosing">—</strong>
        <span id="heroProj" style="margin-top:6px;color:#8de0c8">—</span>
      </div>
    </div>
  </header>

  <nav class="view-bar" aria-label="Vistas principales del sistema">
    <div class="view-tabs">
      <button class="vtab active" data-view="viewOper">🎯 1. Operación 1 a 1 &amp; Catálogo de Opciones</button>
      <button class="vtab" data-view="viewComp">📊 2. Comparativo Antes → Después (v3) → Proyección 1 a 1</button>
      <button class="vtab" data-view="viewNB">🧠 3. Base de Conocimiento NotebookLM (4 Cuadernos · 207 Fuentes)</button>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap">
      <button class="btn" id="btnPrint" title="Imprimir o guardar PDF de la ficha actual">🖨️ Imprimir / PDF</button>
      <button class="btn btn-primary" id="btnExportCsv" title="Exportar lista filtrada 1 a 1 en CSV">📥 Exportar CSV 1 a 1</button>
    </div>
  </nav>

  <section class="kpis" id="kpiRow"></section>

  <section class="filters" aria-label="Filtros multidimensionales 1 a 1">
    <div class="fgrid">
      <div class="fcol"><label for="fManager">Gestor de Cobranza</label><select id="fManager"></select></div>
      <div class="fcol"><label for="fChannel">Canal Recomendado</label><select id="fChannel"></select></div>
      <div class="fcol"><label for="fDpd">Tiempo de Mora (DPD) / SEPS</label>
        <select id="fDpd">
          <option value="all">Todos los tramos SEPS</option>
          <option value="CURADO">Curado ($0 · Paz y Salvo)</option>
          <option value="1-30">1 – 30 días (Normal A2-A3 · Preventiva)</option>
          <option value="31-90">31 – 90 días (Potencial B / Deficiente C)</option>
          <option value="91-180">91 – 180 días (Dudoso D / Pérdida E)</option>
          <option value="181-360">181 – 360 días (Pérdida E · Severa)</option>
          <option value="361+">&gt; 360 días (Pérdida E · Crítica)</option>
        </select>
      </div>
      <div class="fcol"><label for="fAmount">Rango de Monto (Saldo)</label>
        <select id="fAmount">
          <option value="all">Todos los montos</option>
          <option value="low">Bajo (&lt; $5.000 · Monitorio)</option>
          <option value="mid">Medio ($5.000 – $15.000)</option>
          <option value="high">Alto (&gt; $15.000)</option>
        </select>
      </div>
      <div class="fcol"><label for="fMeasure">Tipo de Medida / Perfil</label><select id="fMeasure"></select></div>
      <div class="fcol" style="display:flex;gap:6px">
        <div style="flex:1"><label for="fSearch">Buscar ID o Perfil</label><input id="fSearch" type="text" placeholder="Ej. 00832 o Rota"></div>
        <button class="btn" id="btnReset" title="Limpiar filtros">↺</button>
      </div>
    </div>
  </section>

  <!-- VISTA 1: OPERACIÓN 1 A 1 -->
  <div id="viewOper" class="vview active">
    <section class="main-split">
      <div class="panel">
        <div class="panel-head">
          <div>
            <h2>Cartera 1 a 1 (<span id="tblCount">0</span> clientes)</h2>
            <div style="font-size:11px;color:var(--muted)">Haz clic en cualquier cliente para abrir su diagnóstico conductual, opciones financieras y guion.</div>
          </div>
          <div style="display:flex;gap:6px;align-items:center">
            <select id="sortSelect" class="btn" style="padding:6px 8px">
              <option value="cb_desc">Orden: Mayor Saldo</option>
              <option value="dpd_desc">Orden: Mayor Mora (DPD)</option>
              <option value="pa_desc">Orden: Mayor Prob. Recuperación</option>
              <option value="id_asc">Orden: ID Caso</option>
            </select>
            <button class="btn" id="btnShowAllRows" title="Alternar límite visual de filas">Ver todas</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Caso / Gestor</th>
                <th class="num">Saldo Actual</th>
                <th class="num">Mora · SEPS</th>
                <th>Perfil Real</th>
                <th>Medida / Canal</th>
                <th class="num">Prob.</th>
              </tr>
            </thead>
            <tbody id="caseTbody"></tbody>
          </table>
        </div>
      </div>

      <div class="panel detail-sticky" id="detailPanel"></div>
    </section>
  </div>

  <!-- VISTA 2: COMPARATIVO MACRO V3 + PROYECCIÓN -->
  <div id="viewComp" class="vview">
    <div class="comp-grid">
      <div class="panel">
        <div class="panel-head"><h2>Comparativo Antes vs. Después (v3) vs. Estrategia 1 a 1</h2></div>
        <div id="compSummaryBars"></div>
      </div>
      <div class="panel">
        <div class="panel-head"><h2>Distribución por Tramo SEPS &amp; Mix de Canales Recomendados</h2></div>
        <div id="compChannelMix"></div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-head">
        <h2>Desempeño y Potencial Incremental por Gestor (Haz clic en un gestor para filtrar)</h2>
      </div>
      <div class="table-wrap" style="max-height:460px">
        <table>
          <thead>
            <tr>
              <th>Gestor</th>
              <th class="num">Cuentas</th>
              <th class="num">Saldo Apertura</th>
              <th class="num">Pagos v3</th>
              <th class="num">Saldo Actual</th>
              <th class="num">Proy. Base</th>
              <th class="num">Proy. 1 a 1</th>
              <th class="num">Lift Incremental</th>
              <th class="num">Bloqueos</th>
            </tr>
          </thead>
          <tbody id="mgrTbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- VISTA 3: SÍNTESIS NOTEBOOKLM -->
  <div id="viewNB" class="vview">
    <div class="nb-grid">
      <article class="nb-card">
        <h3><span>⚖️ 1. AGENTES COBRANZAS</span><span class="badge b-prev">25 fuentes</span></h3>
        <ul>
          <li><strong>Jerarquía y Fallback Multicanal:</strong> WhatsApp &rarr; Llamada &rarr; Correo Electrónico con control estricto de consentimiento (`consent / do_not_contact`), cooldown y evidencia digital.</li>
          <li><strong>Gobernanza (Separación de Funciones):</strong> El gestor aplica políticas estándar; quitas o plazos extraordinarios requieren escalamiento y aprobación del <em>Supervisor Estratégico</em> con sustento de capacidad de pago.</li>
          <li><strong>COGEP Ecuador (Coerción Lícita Reglada):</strong> Actas de Mediación y transacciones constituyen título de ejecución (Arts. 235 y 363 núms. 3 y 6). Procedimiento Monitorio ≤50 SBU (Art. 356) y Ejecutivo (Arts. 347-348). Providencias preventivas reales: prohibición de enajenar (Art. 126), retención de fondos (Art. 130) y secuestro (Arts. 124/129), bajo proporcionalidad (Art. 134). Prohibición absoluta de apremio personal por deudas comerciales/civiles.</li>
          <li><strong>Trampa de Iliquidez y Neuroderecho:</strong> Evitar sobrecarga cognitiva (*Scarcity Mindset*) y descuento hiperbólico ("barajado" o usura) mediante cuotas realistas y respeto estricto a horas hábiles (Art. 78 COGEP).</li>
        </ul>
      </article>
      <article class="nb-card">
        <h3><span>🤝 2. gestion de cobranzas</span><span class="badge b-prev">107 fuentes</span></h3>
        <ul>
          <li><strong>Efectividad Empírica de Canales:</strong> WhatsApp alcanza 90%–98% de tasa de apertura y +12% en pagos frente a llamadas en frío; combinar canal digital + llamada reduce -30% los intentos fallidos y eleva +14% la recuperación.</li>
          <li><strong>Reglas Operativas Ecuador (LODC / Res. JB-2010-1782):</strong> Máximo <strong>1 contacto efectivo por día</strong>; horario hábil <strong>L-V 07h00–20h00</strong>; prohibido fines de semana y feriados; prohibido contactar terceros/familiares/empleadores y <strong>prohibidas visitas en lugar de trabajo (Art. 151 COMYF)</strong>. Sanciones documentadas entre $4,600 y $4,820 (doble en reincidencia).</li>
          <li><strong>Derecho al Prepago &amp; Método Harvard:</strong> Todo acuerdo preserva el derecho a cancelar anticipadamente sin penalización ni cobro de intereses no devengados (`JB-2010-1782`). Negociación basada en intereses reales de liquidez y criterios objetivos.</li>
          <li><strong>Alerta Crítica:</strong> Evitar la <em>refinanciación artificial</em> que capitaliza intereses moratorios sin verificar capacidad real de flujo de caja.</li>
        </ul>
      </article>
      <article class="nb-card">
        <h3><span>📄 3. FINANCIERO_COBRANZA</span><span class="badge b-coer">42 fuentes</span></h3>
        <ul>
          <li><strong>Matriz Oficial SEPS (Calificación y Tipo de Cobranza):</strong> Normal `A1–A3` (0–30d Cons/Micro) &rarr; Preventiva; Potencial `B1–B2` (31–60d) &rarr; Administrativa; Deficiente `C1–C2` (61–90d) &rarr; Extrajudicial; Dudoso Recaudo `D` (91–120d) y Pérdida `E` (&gt;120d Cons/Micro; &gt;360d Productivo) &rarr; Judicial.</li>
          <li><strong>Provisiones NIIF 9 &amp; Impacto en ROE:</strong> `EL = PD × LGD × EAD` y `PV(EL) = EL × (1 + IR)^(-T)`. Evidencia documentada en cooperativa ecuatoriana (dic. 2023): gasto de provisión de `$24,204.49` redujo el ROE de `3.12%` a `0.67%`.</li>
          <li><strong>Cadenas de Markov 5×5 &amp; Roll Rates:</strong> Medir la probabilidad condicional de migración entre baldes para priorizar acciones que frenen el pase a castigo.</li>
          <li><strong>Justicia Procedimental e Interaccional:</strong> Desglose transparente de capital/interés/otros, vías visibles de objeción y cero <em>Dark Patterns</em>.</li>
        </ul>
      </article>
      <article class="nb-card">
        <h3><span>📱 4. YOUTUBE_COBRANZA</span><span class="badge b-legal">33 fuentes</span></h3>
        <ul>
          <li><strong>Neurocobranza (Desescalamiento de Amígdala):</strong> Sustituir el tono punitivo (que activa defensa/huida) por rol de asesor facilitador. Reencuadrar la deuda como inversión en estabilidad financiera mediante micro-metas alcanzables.</li>
          <li><strong>Guion Telefónico Relacional en 4 Fases:</strong> 1) Apertura y marco (pedir 2 min); 2) Empatía y escucha activa; 3) <em>Choice Architecture</em> (presentar <strong>exactamente 2 opciones concretas</strong> de pago/reestructuración y preguntar cuál encaja en su flujo); 4) Cierre con monto, fecha límite y comprobante.</li>
          <li><strong>Mensajería Digital Corta (100–140 car.):</strong> Recordatorio claro + enlace de pago directo en un clic + opción gratuita de exclusión (*opt-out*). Si hay buzón de voz, usar <em>Limited Content Message</em> sin revelar deuda a terceros.</li>
          <li><strong>NIIF 9 en 3 Etapas Operativas:</strong> Contener clientes antes de cruzar los 30d (Etapa 1 &rarr; Etapa 2 SICR) y los 90d (Etapa 3 Default), multiplicando el ahorro de reservas de capital.</li>
        </ul>
      </article>
    </div>
  </div>

  <footer class="footer">
    <span><strong>SIMULACIÓN — NO USAR EN PRODUCCIÓN</strong> · Contexto normativo de referencia: Quito, Ecuador (LODC Art. 49, LOPDP, COMYF Art. 151, Res. JB-2010-1782, COGEP Arts. 124-134, 235, 347, 351, 356, 363).</span>
    <span>Construido sobre <code>reporting_synthetic_v3</code> · Pagos registrados v3: $2,505,955.85 · Enriquecido con 4 cuadernos NotebookLM (207 fuentes).</span>
  </footer>
</div>

<script>
const CASES = __CASES_JSON__;
const CHANNEL_LABELS = __CHANNEL_LABELS_JSON__;

const money = new Intl.NumberFormat("es-EC", {style:"currency", currency:"USD", minimumFractionDigits:2});
const pct = v => `${(v*100).toFixed(0)}%`;
const $ = id => document.getElementById(id);

let filtered = [...CASES];
let selectedId = CASES[0] ? CASES[0].id : null;
let showAllRows = false;

function badgeClass(m) {
  if (m.includes("Preventiva")) return "b-prev";
  if (m.includes("Coercitiva")) return "b-coer";
  if (m.includes("Legal")) return "b-legal";
  if (m.includes("Bloqueo")) return "b-lock";
  return "b-cur";
}

function initFilters() {
  const mgrs = [...new Set(CASES.map(c => c.mgr))].sort();
  $("fManager").innerHTML = '<option value="all">Todos los gestores (' + mgrs.length + ')</option>' + mgrs.map(m => `<option value="${m}">${m}</option>`).join("");

  const chs = [...new Set(CASES.map(c => c.ch))];
  $("fChannel").innerHTML = '<option value="all">Todos los canales</option>' + chs.map(ch => `<option value="${ch}">${CHANNEL_LABELS[ch] || ch}</option>`).join("");

  const meas = [...new Set(CASES.map(c => c.meas))];
  $("fMeasure").innerHTML = '<option value="all">Todas las medidas</option>' + meas.map(m => `<option value="${m}">${m}</option>`).join("");
}

function applyFilters() {
  const mgr = $("fManager").value;
  const ch = $("fChannel").value;
  const dpd = $("fDpd").value;
  const amt = $("fAmount").value;
  const meas = $("fMeasure").value;
  const q = $("fSearch").value.trim().toLowerCase();
  const sort = $("sortSelect").value;

  filtered = CASES.filter(c => {
    if (mgr !== "all" && c.mgr !== mgr) return false;
    if (ch !== "all" && c.ch !== ch) return false;
    if (meas !== "all" && c.meas !== meas) return false;
    if (q && !c.id.toLowerCase().includes(q) && !c.prof.toLowerCase().includes(q) && !c.seps.toLowerCase().includes(q)) return false;
    if (dpd === "CURADO" && c.cb > 0) return false;
    if (dpd === "1-30" && (c.dpd < 1 || c.dpd > 30)) return false;
    if (dpd === "31-90" && (c.dpd < 31 || c.dpd > 90)) return false;
    if (dpd === "91-180" && (c.dpd < 91 || c.dpd > 180)) return false;
    if (dpd === "181-360" && (c.dpd < 181 || c.dpd > 360)) return false;
    if (dpd === "361+" && c.dpd < 361) return false;
    if (amt === "low" && c.cb >= 5000) return false;
    if (amt === "mid" && (c.cb < 5000 || c.cb > 15000)) return false;
    if (amt === "high" && c.cb <= 15000) return false;
    return true;
  });

  filtered.sort((a,b) => {
    if (sort === "cb_desc") return b.cb - a.cb;
    if (sort === "dpd_desc") return b.dpd - a.dpd;
    if (sort === "pa_desc") return b.pa - a.pa;
    return a.id.localeCompare(b.id);
  });

  if (!filtered.some(c => c.id === selectedId)) {
    selectedId = filtered.length ? filtered[0].id : null;
  }
  renderKpis();
  renderTable();
  renderDetail();
  renderComparative();
}

function renderKpis() {
  const ob = filtered.reduce((s,c) => s + c.ob, 0);
  const paid = filtered.reduce((s,c) => s + c.paid, 0);
  const cb = filtered.reduce((s,c) => s + c.cb, 0);
  const projBase = filtered.reduce((s,c) => s + c.cb * c.pb, 0);
  const projAct = filtered.reduce((s,c) => s + c.cb * c.pa, 0);
  const lift = projAct - projBase;
  const bloq = filtered.filter(c => c.disp || c.rev).length;

  $("heroClosing").textContent = money.format(cb);
  $("heroProj").textContent = `Potencial 1 a 1 proyectado: ${money.format(projAct)} (+${money.format(lift)} incremental)`;

  $("kpiRow").innerHTML = [
    ["Saldo Apertura (v3)", money.format(ob), `${filtered.length} cuentas filtradas`, ""],
    ["Pagos Registrados (v3)", money.format(paid), `${filtered.filter(c=>c.pc>0).length} cuentas con abonos`, "teal"],
    ["Saldo Pendiente Actual", money.format(cb), `${filtered.filter(c=>c.cb>0).length} activas · ${filtered.filter(c=>c.cb===0).length} curadas`, ""],
    ["Recuperación Base (Sin Acción)", money.format(projBase), `Prob. media base: ${pct(filtered.length?filtered.reduce((s,c)=>s+c.pb,0)/filtered.length:0)}`, ""],
    ["Potencial Estrategia 1 a 1", money.format(projAct), `+${money.format(lift)} lift incremental`, "teal"],
    ["Bloqueos / Disputas", `${bloq}`, "Abstención obligatoria (Art. 49 LODC)", ""]
  ].map(([l,v,s,cls]) => `<div class="kpi ${cls}"><div class="kpi-lbl">${l}</div><div class="kpi-val">${v}</div><div class="kpi-sub">${s}</div></div>`).join("");
}

function renderTable() {
  $("tblCount").textContent = filtered.length;
  const limit = showAllRows ? filtered.length : Math.min(filtered.length, 300);
  $("btnShowAllRows").textContent = showAllRows || filtered.length <= 300 ? `Mostrando ${limit}` : `Ver todas (${filtered.length})`;
  $("caseTbody").innerHTML = filtered.slice(0, limit).map(c => `
    <tr class="case-row ${c.id === selectedId ? "selected" : ""}" data-id="${c.id}">
      <td><strong>${c.id}</strong><div style="font-size:10px;color:var(--muted)">${c.mgr}</div></td>
      <td class="num"><strong>${money.format(c.cb)}</strong><div style="font-size:10px;color:var(--muted)">Pagó: ${money.format(c.paid)}</div></td>
      <td class="num"><strong>${c.dpd} d</strong><div style="font-size:10px;color:var(--muted)">${c.seps.split("(")[0].trim()}</div></td>
      <td><div style="font-size:11px;font-weight:700">${c.prof}</div><div style="font-size:10px;color:var(--muted)">Kept: ${c.ck} · Missed: ${c.cm}</div></td>
      <td><span class="badge ${badgeClass(c.meas)}">${c.meas}</span><div style="font-size:10px;color:var(--muted);margin-top:2px">${CHANNEL_LABELS[c.ch] || c.ch}</div></td>
      <td class="num"><span style="font-weight:800;color:var(--teal)">${pct(c.pa)}</span><div style="font-size:10px;color:var(--muted)">antes ${pct(c.pb)}</div></td>
    </tr>
  `).join("");

  document.querySelectorAll("tr.case-row").forEach(tr => {
    tr.addEventListener("click", () => {
      selectedId = tr.dataset.id;
      document.querySelectorAll("tr.case-row").forEach(r => r.classList.toggle("selected", r.dataset.id === selectedId));
      renderDetail();
    });
  });
}

function renderDetail() {
  const host = $("detailPanel");
  const c = filtered.find(x => x.id === selectedId);
  if (!c) { host.innerHTML = "<p>No hay casos bajo el filtro actual.</p>"; return; }

  const isLocked = c.disp === 1 || c.rev === 1;
  const tlHtml = c.tl.length ? c.tl.map(i => `<div class="tl-item"><span><strong>${i.d}</strong> · ${i.t}</span><span>${i.x}</span></div>`).join("") : '<div class="tl-item">Sin eventos adicionales al registro inicial.</div>';

  host.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;flex-wrap:wrap">
      <div>
        <span class="badge ${badgeClass(c.meas)}">${c.meas}</span>
        <span class="badge" style="background:#eef2ff;color:#3730a3;margin-left:4px">${c.ifrs}</span>
        <h2 style="margin:6px 0 2px;font-size:19px;color:var(--navy)">${c.id} · ${c.mgr}</h2>
        <div style="font-size:12px;color:var(--muted)">${c.prof} · <strong>${c.seps}</strong></div>
      </div>
      <div style="text-align:right">
        <div style="font-size:11px;color:var(--muted);font-weight:700">SALDO PENDIENTE</div>
        <div style="font-size:24px;font-weight:800;color:var(--navy)">${money.format(c.cb)}</div>
      </div>
    </div>

    <div class="mini-grid" style="margin-top:10px">
      <div class="mini-box"><span>Capital / Interés / Otros</span><strong>${money.format(c.rp)} / ${money.format(c.ri)} / ${money.format(c.ro)}</strong></div>
      <div class="mini-box"><span>Pagos v3 (${c.pc})</span><strong>${money.format(c.paid)}</strong></div>
      <div class="mini-box"><span>Mora Actual / Inicial</span><strong>${c.dpd} d (inicio ${c.dpd0} d)</strong></div>
      <div class="mini-box"><span>Prob. Base &rarr; Acción 1 a 1</span><strong style="color:var(--teal)">${pct(c.pb)} &rarr; ${pct(c.pa)}</strong></div>
    </div>

    <div class="rec-banner" style="${isLocked ? 'background:#fef2f2;border-color:#fecaca' : ''}">
      <h3 style="${isLocked ? 'color:#991b1b' : ''}">${isLocked ? '🛑 ALERTA NORMATIVA (ABSTENCIÓN OBLIGATORIA)' : '🎯 Acción Más Recomendada 1 a 1 · Canal: ' + (CHANNEL_LABELS[c.ch] || c.ch)}</h3>
      <p style="${isLocked ? 'color:#7f1d1d' : ''}">${c.step}</p>
    </div>

    <div class="tabs">
      <button class="tab active" data-t="paneCat">💼 Catálogo de Opciones (Quito)</button>
      <button class="tab" data-t="paneMed">⚖️ Preventivas, Coercitivas &amp; Legal</button>
      <button class="tab" data-t="paneMsg">💬 Guion Neurocobranza 1 a 1</button>
      <button class="tab" data-t="paneHist">🕒 Historial (${c.tl.length})</button>
    </div>

    <div id="paneCat" class="tab-pane active">
      ${c.cb <= 0 ? '<p><strong>Cuenta Saldada ($0.00):</strong> Emitir certificado de paz y salvo simulado y cerrar seguimiento.</p>' : isLocked ? '<p style="color:#991b1b"><strong>Opciones de cobro deshabilitadas:</strong> El caso registra disputa abierta o revisión humana pendiente. Escalar a auditoría interna.</p>' : `
      <div class="opt-card">
        <h4><span>Opción 1 · Liquidación Rápida con Condonación de Interés y Gastos (48–72h)</span><span class="gov-tag" id="govOpt1">Política Gestor</span></h4>
        <div class="ctrl-row">
          <label>Condonación sobre Interés (${money.format(c.ri)}) + Otros (${money.format(c.ro)}): <strong id="lblDesc">${c.dpd > 180 ? 100 : 75}%</strong></label>
          <input id="slDesc" type="range" min="0" max="100" step="5" value="${c.dpd > 180 ? 100 : 75}">
        </div>
        <div class="res-grid" id="resOpt1"></div>
      </div>

      <div class="opt-card">
        <h4><span>Opción 2 · Suavización de Interés + Reducción de Cuotas &amp; Control VPN</span><span class="gov-tag" id="govOpt2">Política Gestor</span></h4>
        <div class="ctrl-row">
          <label>Plazo (meses): <select id="selPlazo"><option>6</option><option>12</option><option selected>18</option><option>24</option><option>36</option></select></label>
          <label>Tasa Anual Suavizada (%): <input id="inpTasa" type="number" min="8" max="18" step="0.5" value="12.5" style="width:70px;padding:3px 6px"></label>
        </div>
        <div class="res-grid" id="resOpt2"></div>
        <div class="alert-note"><strong>Salvaguarda Ecuador (JB-2010-1782 &amp; Gestión):</strong> Evitar refinanciación artificial capitalizando mora sin verificar ingreso real. El cliente conserva derecho al <strong>prepago anticipado sin penalización</strong> ni intereses no devengados.</div>
      </div>

      <div class="opt-card">
        <h4><span>Opción 3 · Convenio Escalonado con Abono Inicial Vinculante (Anti-Postergación)</span><span class="gov-tag">Ejecución Inmediata</span></h4>
        <div class="ctrl-row">
          <label>Entrada (72h): <strong id="lblEnt">${c.cm > 0 ? 30 : 20}%</strong></label>
          <input id="slEnt" type="range" min="15" max="45" step="5" value="${c.cm > 0 ? 30 : 20}">
          <label>Cuotas saldo: <select id="selCuot"><option>3</option><option selected>6</option><option>9</option></select></label>
        </div>
        <div class="res-grid" id="resOpt3"></div>
      </div>

      <div class="opt-card">
        <h4><span>Opción 4 · Período de Gracia Parcial (2 meses solo interés) + Plan Regular</span><span class="gov-tag sup">Requiere Supervisor</span></h4>
        <div class="res-grid" id="resOpt4"></div>
      </div>`}
    </div>

    <div id="paneMed" class="tab-pane">
      <div class="opt-card">
        <h4><span>1. Medidas Preventivas y de Alivio (0–90 DPD · SEPS A/B/C)</span></h4>
        <p style="margin:0;font-size:12px">• Contención temprana para evitar migración de <strong>Etapa 1 a Etapa 2-3 NIIF 9</strong> (reduciendo consumo de provisiones sobre ROE).<br>• Suavización de mora, extensión hasta 24–36m y arquitectura de 2 opciones claras (Choice Architecture) en horario legal <strong>L-V 07h00–20h00</strong> (máx. 1 contacto/día).</p>
      </div>
      <div class="opt-card">
        <h4><span>2. Medidas Coercitivas Lícitas / Prejudiciales (Promesas Rotas / 91–360 DPD)</span></h4>
        <p style="margin:0;font-size:12px">• <strong>Prohibiciones Terminantes (LODC Art. 49, LOPDP, COMYF Art. 151, Res. JB-2010-1782):</strong> Prohibido contactar fines de semana/feriados, llamar a familiares o jefes, realizar visitas laborales o simular órdenes de embargo (sanciones $4,600–$4,820).<br>• <strong>Presión Reglada Admisible:</strong> Notificación escrita formal con término perentorio, reporte objetivo en Buró y <strong>citación a Centro de Mediación Quito</strong> (Acta con fuerza de sentencia ejecutoriada: COGEP Arts. 235 y 363 núms. 3 y 6).</p>
      </div>
      <div class="opt-card">
        <h4><span>3. Escalado a Acción Legal Formal (COGEP Ecuador)</span></h4>
        <p style="margin:0;font-size:12px">• <strong>Vía Procesal Sugerida:</strong> ${c.via}.<br>• <strong>Providencias Preventivas Reales (COGEP Arts. 124–134, 351):</strong> Prohibición de enajenar inmuebles (Art. 126), retención de fondos financieros (Art. 130) y secuestro judicial (Arts. 124/129). Prohibido apremio personal por deudas comerciales.<br>• <strong>Control de Prescripción &amp; Cost-to-Collect:</strong> En mora de ${c.dpd} días, auditar fecha de vencimiento del título y salidas alternativas (Concurso Preventivo Arts. 414–428 o fórmula de pago Art. 361/374).</p>
      </div>
    </div>

    <div id="paneMsg" class="tab-pane">
      <div class="ctrl-row" style="justify-content:space-between">
        <label>Canal / Plantilla:
          <select id="selMsgCh">
            <option value="phone_call">Guion Llamada 4 Fases (Neurocobranza)</option>
            <option value="whatsapp_message">WhatsApp / SMS (100–140 car. + Enlace)</option>
            <option value="email">Correo Electrónico (Desglose Transparente)</option>
            <option value="written_notice">Citación Prejudicial / Mediación Quito</option>
          </select>
        </label>
        <button class="btn btn-teal" id="btnCopyScript">📋 Copiar guion</button>
      </div>
      <textarea id="txtScript" rows="13" class="script-box" readonly></textarea>
    </div>

    <div id="paneHist" class="tab-pane">
      <div style="font-size:12px;margin-bottom:8px">
        <strong>Canales con respuesta:</strong> ${c.rep.length ? c.rep.join(", ") : "Ninguno"} |
        <strong>Sin respuesta:</strong> ${c.fail.length ? c.fail.join(", ") : "Ninguno"} |
        <strong>Datos actualizados:</strong> ${c.upd} | <strong>Hallazgos:</strong> ${c.fnd}
      </div>
      <div class="tl-list">${tlHtml}</div>
    </div>
  `;

  host.querySelectorAll(".tab").forEach(t => {
    t.addEventListener("click", () => {
      host.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
      host.querySelectorAll(".tab-pane").forEach(x => x.classList.remove("active"));
      t.classList.add("active");
      $(t.dataset.t).classList.add("active");
    });
  });

  if (c.cb > 0 && !isLocked) {
    const calcOpts = () => {
      // Opción 1
      const dPct = Number($("slDesc").value) / 100;
      $("lblDesc").textContent = `${Math.round(dPct*100)}%`;
      const ahorro = (c.ri + c.ro) * dPct;
      const neto = Math.max(0, c.cb - ahorro);
      $("govOpt1").textContent = dPct > 0.5 ? "Aprobación Supervisor Estratégico" : "Política Estándar Gestor";
      $("govOpt1").className = dPct > 0.5 ? "gov-tag sup" : "gov-tag";
      $("resOpt1").innerHTML = `
        <div class="res-box"><span>Pago Contado 48-72h</span><strong>${money.format(neto)}</strong></div>
        <div class="res-box"><span>Condonación Mora/Otros</span><strong>${money.format(ahorro)}</strong></div>
        <div class="res-box"><span>Capital Preservado</span><strong>100% (${money.format(c.rp)})</strong></div>`;

      // Opción 2 + VPN Estimado (desc. institucional ref. 11% anual)
      const plazo = Number($("selPlazo").value);
      const tasaA = Number($("inpTasa").value) / 100;
      const tm = tasaA / 12;
      const td = 0.11 / 12;
      const cuotaBase6m = c.cb / 6;
      const cuotaSuav = tm > 0 ? (c.cb * tm) / (1 - Math.pow(1 + tm, -plazo)) : c.cb / plazo;
      const alivioPct = Math.max(0, (1 - cuotaSuav / cuotaBase6m) * 100);
      let vpn = 0;
      for (let m = 1; m <= plazo; m++) vpn += cuotaSuav / Math.pow(1 + td, m);
      $("govOpt2").textContent = plazo >= 24 ? "Aprobación Supervisor (≥24m)" : "Política Estándar Gestor";
      $("govOpt2").className = plazo >= 24 ? "gov-tag sup" : "gov-tag";
      $("resOpt2").innerHTML = `
        <div class="res-box"><span>Cuota Mensual (${plazo}m)</span><strong>${money.format(cuotaSuav)}</strong></div>
        <div class="res-box"><span>Alivio Cuota vs. 6m</span><strong>-${alivioPct.toFixed(0)}%</strong></div>
        <div class="res-box"><span>VPN Estimado (11% desc.)</span><strong>${money.format(vpn)}</strong></div>`;

      // Opción 3
      const entPct = Number($("slEnt").value) / 100;
      const nCuot = Number($("selCuot").value);
      $("lblEnt").textContent = `${Math.round(entPct*100)}%`;
      const entUsd = c.cb * entPct;
      const cuotaRem = (c.cb - entUsd) / nCuot;
      $("resOpt3").innerHTML = `
        <div class="res-box"><span>Abono Entrada (72h)</span><strong>${money.format(entUsd)}</strong></div>
        <div class="res-box"><span>Saldo Diferido</span><strong>${money.format(c.cb - entUsd)}</strong></div>
        <div class="res-box"><span>${nCuot} Cuotas Fijas</span><strong>${money.format(cuotaRem)}</strong></div>`;

      // Opción 4
      const cuotaGracia = c.cb * tm;
      const cuotaPost = tm > 0 ? (c.cb * tm) / (1 - Math.pow(1 + tm, -Math.max(1, plazo - 2))) : c.cb / plazo;
      $("resOpt4").innerHTML = `
        <div class="res-box"><span>Mes 1 y 2 (Solo Interés)</span><strong>${money.format(cuotaGracia)}</strong></div>
        <div class="res-box"><span>Mes 3 a ${plazo}</span><strong>${money.format(cuotaPost)}</strong></div>
        <div class="res-box"><span>Objetivo NIIF 9</span><strong>Contener Roll Rate</strong></div>`;
    };
    ["slDesc","selPlazo","inpTasa","slEnt","selCuot"].forEach(id => $(id).addEventListener("input", calcOpts));
    calcOpts();
  }

  if (CHANNEL_LABELS[c.ch] && c.ch !== "none" && $("selMsgCh").querySelector(`option[value="${c.ch}"]`)) {
    $("selMsgCh").value = c.ch;
  }
  const updateScript = () => {
    const ch = $("selMsgCh").value;
    const neto75 = Math.max(0, c.cb - (c.ri + c.ro) * 0.75);
    const cuota18 = (c.cb * (0.125/12)) / (1 - Math.pow(1 + 0.125/12, -18));
    const abono25 = c.cb * 0.25;
    if (isLocked) {
      $("txtScript").value = `[SIMULACIÓN — NO ENVIAR]\nCUENTA BLOQUEADA (${c.id}): Disputa o revisión humana pendiente.\nAbstención obligatoria de gestión de cobro o coerción (Art. 49 LODC).`;
      return;
    }
    if (ch === "whatsapp_message") {
      $("txtScript").value = `[SIMULACIÓN — NO ENVIAR] · L-V 07h00–20h00 (Máx. 1 contacto/día)\n\n[OPCIÓN CORTA 100–140 CAR. — Autoatención]:\nHola Ref. ${c.id}, tu saldo de ${money.format(c.cb)} presenta ${c.dpd}d de mora. Evita cargos: liquida hoy con alivio o activa convenio aquí [ENLACE]. Resp. STOP para excluir.\n\n[VERSIÓN WHATSAPP CON CHOICE ARCHITECTURE]:\nEstimado/a titular (Ref. ${c.id}), le saluda ${c.mgr} desde Quito. Para evitar recargos y proteger su historial, hoy tiene 2 alternativas vigentes:\n1) Pago de contado (48h) con suavización 75% en mora/gastos: ${money.format(neto75)}.\n2) Reducción de cuota a 18 meses: cuotas de ${money.format(cuota18)}/mes (derecho a prepago sin penalización).\n¿Cuál se ajusta mejor a su flujo de caja?`;
    } else if (ch === "phone_call") {
      $("txtScript").value = `[SIMULACIÓN — NO ENVIAR] · GUION RELACIONAL EN 4 FASES (NEUROCOBRANZA) · ${c.id}\nContexto real: Saldo ${money.format(c.cb)} | Mora ${c.dpd}d (${c.seps}) | Promesas Cumplidas: ${c.ck} / Rotas: ${c.cm}\n\n1. APERTURA Y MARCO (Boundary Setting — sin amenazas):\n"Buenos días, le saluda ${c.mgr}. El motivo de mi llamada es revisar alternativas viables para proteger su historial respecto al saldo de ${money.format(c.cb)}. ¿Dispone de 2 minutos?"\n\n2. VALIDACIÓN LOPDP & ESCUCHA ACTIVA (Desescalamiento de amígdala):\n"Por seguridad de datos, confírmeme los 4 últimos dígitos de su cédula/RUC. Valoramos su diálogo; queremos ajustar una salida acorde a su liquidez actual sin cargos innecesarios."\n\n3. PROPUESTA EN CHOICE ARCHITECTURE (Exactamente 2 opciones concretas):\n"Para no exigir el total de golpe, tengo habilitadas 2 opciones hoy:\n  A) Abono inicial de ${money.format(abono25)} en 72h y saldo en cuotas fijas; o\n  B) Reprogramación con suavización de tasa y cuota reducida de ${money.format(cuota18)}/mes a 18 meses.\nDe estas dos, ¿cuál se ajusta mejor a su flujo de caja?"\n\n4. CIERRE CON COMPROMISO FIRME:\n"Excelente decisión. Registramos [Monto] para el [Fecha] por canal digital y le enviamos el comprobante formal (recuerde su derecho a prepagar anticipadamente sin multa)."`;
    } else if (ch === "email") {
      $("txtScript").value = `[SIMULACIÓN — NO ENVIAR] · JUSTICIA PROCEDIMENTAL (Desglose Transparente)\nAsunto: Estado de Cuenta Auditado y Opciones de Alivio Financiero — Ref. ${c.id}\n\nEstimado/a titular,\nCompartimos el desglose transparente de su operación en Quito:\n- Capital remanente: ${money.format(c.rp)}\n- Interés remanente: ${money.format(c.ri)}\n- Otros cargos: ${money.format(c.ro)}\n- Total pendiente: ${money.format(c.cb)} (${c.dpd} días · ${c.seps})\n\nAlternativas disponibles (sujetas a política):\n- Opción A (Liquidación 72h con condonación 75% mora/gastos): ${money.format(neto75)}\n- Opción B (Reducción de cuota a 18 meses al 12.5%): ${money.format(cuota18)}/mes (prepago libre sin penalización JB-2010-1782).\nSi detecta alguna inconsistencia en su liquidación, responda este correo para activar auditoría inmediata.\n\nAtentamente, ${c.mgr}.`;
    } else {
      $("txtScript").value = `[SIMULACIÓN — NO ENVIAR] · NOTIFICACIÓN FORMAL Y CITACIÓN A MEDIACIÓN (QUITO, ECUADOR)\nExpediente: ${c.id} | Saldo Exigible: ${money.format(c.cb)} | Mora: ${c.dpd} días (${c.seps})\n\nEn observancia de la Ley Orgánica de Defensa del Consumidor (Art. 49), la Ley de Arbitraje y Mediación (Art. 47) y el COGEP (Arts. 235 y 363 núm. 3), notificamos formalmente el requerimiento de regularización extrajudicial dentro de las próximas 72 horas.\n\nAlternativa de acuerdo antes de instancia procesal (${c.via}):\n- Suscripción de Acta de Mediación en Centro autorizado de Quito con entrada de ${money.format(abono25)} y cuotas adaptadas.\nNota: Se excluye estrictamente toda comunicación a terceros o lugar de trabajo (Art. 151 COMYF).`;
    }
  };
  $("selMsgCh").addEventListener("change", updateScript);
  $("btnCopyScript").addEventListener("click", () => {
    const txt = $("txtScript").value;
    const ok = () => { $("btnCopyScript").textContent = "✅ ¡Copiado!"; setTimeout(()=>{$("btnCopyScript").textContent = "📋 Copiar guion";}, 1600); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(ok).catch(() => { $("txtScript").select(); document.execCommand("copy"); ok(); });
    } else {
      $("txtScript").select(); document.execCommand("copy"); ok();
    }
  });
  updateScript();
}

function renderComparative() {
  const ob = filtered.reduce((s,c) => s + c.ob, 0) || 1;
  const paid = filtered.reduce((s,c) => s + c.paid, 0);
  const cb = filtered.reduce((s,c) => s + c.cb, 0);
  const pBase = filtered.reduce((s,c) => s + c.cb * c.pb, 0);
  const pAct = filtered.reduce((s,c) => s + c.cb * c.pa, 0);

  const bars = [
    ["1. Saldo Apertura v3", ob, ob, "#133858"],
    ["2. Pagado en Libro v3", paid, ob, "#0e9f87"],
    ["3. Saldo Actual Pendiente", cb, ob, "#64748b"],
    ["4. Proyección Sin Acción 1a1", pBase, ob, "#d97706"],
    ["5. Proyección Con Estrategia 1a1", pAct, ob, "#059669"]
  ];
  $("compSummaryBars").innerHTML = bars.map(([lbl, val, maxv, col]) => `
    <div class="bar-row">
      <strong>${lbl}</strong>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.min(100,(val/maxv)*100).toFixed(1)}%;background:${col}"></div></div>
      <div class="num"><strong>${money.format(val)}</strong> (${((val/maxv)*100).toFixed(1)}%)</div>
    </div>
  `).join("") + `<p style="font-size:12px;color:var(--muted);margin-top:10px">Ganancia incremental esperada al pasar de gestión genérica a portafolio prescriptivo 1 a 1 sobre los casos filtrados: <strong style="color:var(--teal)">+${money.format(pAct - pBase)}</strong>.</p>`;

  // Mix por canal y SEPS
  const sepsMap = {};
  filtered.forEach(c => {
    const key = c.seps.split("(")[0].trim();
    if (!sepsMap[key]) sepsMap[key] = {n:0, cb:0};
    sepsMap[key].n++; sepsMap[key].cb += c.cb;
  });
  const chMap = {};
  filtered.forEach(c => { const l = CHANNEL_LABELS[c.ch] || c.ch; chMap[l] = (chMap[l] || 0) + 1; });

  const sepsHtml = Object.entries(sepsMap).map(([k,v]) => `
    <div class="bar-row">
      <span>${k}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.min(100,(v.cb/Math.max(1,cb))*100).toFixed(1)}%"></div></div>
      <div class="num">${v.n} cta · ${money.format(v.cb)}</div>
    </div>`).join("");
  const chHtml = Object.entries(chMap).sort((a,b)=>b[1]-a[1]).map(([k,n]) => `<span class="badge b-prev" style="margin:3px">${k}: ${n}</span>`).join("");
  $("compChannelMix").innerHTML = sepsHtml + `<div style="margin-top:12px;padding-top:10px;border-top:1px solid var(--line)"><strong style="font-size:11px;display:block;margin-bottom:4px">DISTRIBUCIÓN DE CANAL ÓPTIMO 1 A 1:</strong>${chHtml}</div>`;

  // Tabla por Gestor
  const byMgr = {};
  filtered.forEach(c => {
    if (!byMgr[c.mgr]) byMgr[c.mgr] = {n:0,ob:0,paid:0,cb:0,pb:0,pa:0,bloq:0};
    const m = byMgr[c.mgr];
    m.n++; m.ob += c.ob; m.paid += c.paid; m.cb += c.cb;
    m.pb += c.cb * c.pb; m.pa += c.cb * c.pa;
    if (c.disp || c.rev) m.bloq++;
  });
  $("mgrTbody").innerHTML = Object.entries(byMgr).sort((a,b)=>b[1].cb - a[1].cb).map(([mgr,m]) => `
    <tr class="case-row mgr-row" data-mgr="${mgr}">
      <td><strong>${mgr}</strong></td>
      <td class="num">${m.n}</td>
      <td class="num">${money.format(m.ob)}</td>
      <td class="num" style="color:var(--teal);font-weight:700">${money.format(m.paid)}</td>
      <td class="num">${money.format(m.cb)}</td>
      <td class="num">${money.format(m.pb)}</td>
      <td class="num" style="color:var(--teal);font-weight:800">${money.format(m.pa)}</td>
      <td class="num"><strong>+${money.format(m.pa - m.pb)}</strong></td>
      <td class="num">${m.bloq}</td>
    </tr>
  `).join("");
  document.querySelectorAll(".mgr-row").forEach(tr => {
    tr.addEventListener("click", () => {
      $("fManager").value = tr.dataset.mgr;
      applyFilters();
      document.querySelector('.vtab[data-view="viewOper"]').click();
    });
  });
}

// Vistas superiores
document.querySelectorAll(".vtab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".vtab").forEach(x => x.classList.remove("active"));
    document.querySelectorAll(".vview").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");
    $(btn.dataset.view).classList.add("active");
  });
});

["fManager","fChannel","fDpd","fAmount","fMeasure","sortSelect"].forEach(id => $(id).addEventListener("change", applyFilters));
$("fSearch").addEventListener("input", applyFilters);
$("btnReset").addEventListener("click", () => {
  ["fManager","fChannel","fDpd","fAmount","fMeasure","sortSelect"].forEach(id => $(id).selectedIndex = 0);
  $("fSearch").value = "";
  applyFilters();
});
$("btnShowAllRows").addEventListener("click", () => { showAllRows = !showAllRows; renderTable(); });
$("btnPrint").addEventListener("click", () => window.print());
$("btnExportCsv").addEventListener("click", () => {
  const cols = ["id","mgr","ob","paid","cb","dpd","seps","ifrs","prof","meas","ch","pb","pa","step"];
  const csv = [cols.join(","), ...filtered.map(c => cols.map(k => `"${String(c[k]).replaceAll('"','""')}"`).join(","))].join("\n");
  const blob = new Blob(["\uFEFF" + csv], {type:"text/csv;charset=utf-8"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "catalogo_prescriptivo_1a1_quito_v4.csv";
  a.click();
});

initFilters();
applyFilters();
</script>
</body>
</html>
"""


def main() -> None:
    records = build_case_records()
    cases_json = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    ch_json = json.dumps(CHANNEL_LABELS, ensure_ascii=False)

    html = (
        HTML_TEMPLATE
        .replace("__CASES_JSON__", cases_json)
        .replace("__CHANNEL_LABELS_JSON__", ch_json)
    )

    OUT_REPORT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT_HTML.write_text(html, encoding="utf-8")

    OUT_VERCEL_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_VERCEL_HTML.write_text(html, encoding="utf-8")

    print(f"Generado HTML interactivo v4 ({len(records)} casos):")
    print(f" - Local Reports: {OUT_REPORT_HTML} ({OUT_REPORT_HTML.stat().st_size:,} bytes)")
    print(f" - Vercel Public: {OUT_VERCEL_HTML} ({OUT_VERCEL_HTML.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
