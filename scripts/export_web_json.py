# -*- coding: utf-8 -*-
"""
Exporta el dataset calibrado a JSON estático para el despliegue Web en Vercel,
aplicando exactamente la misma lógica de contención y perfilado que app_cobranzas.py.
"""

import json
import os
import pandas as pd


def asignar_perfil_observado(row: pd.Series) -> str:
    if row["ratio_cumplimiento_promesas"] >= 0.50:
        if "Solicitó" in str(row["respuesta_ultimo_contacto"]) or "Racional" in str(
            row["arquetipo_neurocognitivo"]
        ):
            return "Perfil 2: Comerciante Analítico (Costo-Beneficio)"
        return "Perfil 1: MYPE con Descalce Temporal (Cooperativo)"
    if row["ratio_cumplimiento_promesas"] < 0.35 and row["promesas_12m"] >= 2:
        return "Perfil 3: Postergador Crónico (Promesas Rotas)"
    if row["respuesta_ultimo_contacto"] in [
        "No respondió / Buzón",
        "Rechazó contacto / Evasivo",
    ]:
        return "Perfil 4: Evasivo / Incontactable Crítico"
    return "Perfil 1: MYPE con Descalce Temporal (Cooperativo)"


def main() -> None:
    csv_path = os.path.join("datos_sinteticos", "cartera_calibrada_multidimensional_1000.csv")
    out_dir = os.path.join("public", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "cartera.json")

    df = pd.read_csv(csv_path)

    df["bloqueo_legal"] = (
        (df["disputa_saldo"] == "En auditoría de liquidación")
        | (df["consentimiento_contacto_simulado"] == "En revisión de vigencia")
    )
    df["solo_canal_digital"] = (
        df["consentimiento_contacto_simulado"] == "Restringido (solo canal digital escrito)"
    )
    df["elegible_visita_campo"] = (
        (~df["bloqueo_legal"])
        & (~df["solo_canal_digital"])
        & (
            (
                (df["saldo_usd"] >= 3000)
                & (df["bucket_mora"].str.contains("B2|B3|B4|B5"))
                & (
                    df["respuesta_ultimo_contacto"].isin(
                        ["No respondió / Buzón", "Rechazó contacto / Evasivo"]
                    )
                )
            )
            | (df["estado_prescripcion"].str.contains("Alerta"))
        )
    )
    df["perfil_conductual_observado"] = df.apply(asignar_perfil_observado, axis=1)

    records = json.loads(df.to_json(orient="records", force_ascii=False))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Exportados {len(records)} registros a {out_path} ({os.path.getsize(out_path):,} bytes)")


if __name__ == "__main__":
    main()

