# PROMPT — Construir KPI-Tree desde métricas del flywheel y buyer journey

## Rol
Eres un Product Manager de datos. Quiero un **KPI-Tree** claro y accionable para el **buyer side**.

## Entradas
- **Key Metrics (3–5)**: {{gmv_per_session, orders_per_session, aov, ...}}
- **Leading candidates (buyer journey)**: {{search_to_pdp_rate, pdp_to_atc_rate, atc_to_checkout_rate, checkout_to_payment_rate, ...}}
- **Guardrails (2–3)**: {{pdp_latency_p95, checkout_error_rate, refund_rate_14d}}
- **Scope** (apples-to-apples): {{país=DE, device=Web, ventana=28d}}

## Reglas de salida
- Nombres en `snake_case`.
- Para cada métrica: **definición**, **fórmula**, **base**, **owner**, **frecuencia**.
- Marca **PM** (métrica principal) y **SM** (secundaria/s) y explica en **1 línea** por qué se conectan.

## Salida esperada
1) **Árbol (ASCII)** desde `gmv_per_session` → `aov` y `orders_per_session` → tasas del journey.  
2) **Tabla de métricas (Markdown)**:  
    | Tipo | Métrica | Definición | Fórmula | Frecuencia | Owner |
    |---|---|---|---|---|---|  
3) **Nota de conexión** (1–3 líneas): por qué la **PM** ancla al outcome y cómo la(s) **SM** ayudan a diagnosticar o a vigilar riesgos.

## Alcance
- No priorices ni propongas hipótesis; **solo** estructura causal y definiciones.