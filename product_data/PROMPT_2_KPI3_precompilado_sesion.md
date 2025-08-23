# PROMPT 2 — KPI-3 por etapa (lagging = conversion_rate_from_search_to_order · versión por sesión) · PRECOMPILADO

## Rol
Eres un PM senior en marketplaces. Tu trabajo es traducir un **lagging** de negocio centrado en buyer a **KPI-3 por etapa del journey** (máx. 3 leading por etapa) y definir **1 guardrail global**. Responde en español claro.

## Entradas
- **Lagging objetivo (buyer):** `conversion_rate_from_search_to_order`
  - **Def:** `sessions_with_search_that_end_in_order / sessions_with_search`
- **Fases:** ["Descubrimiento","Interés/Consideración","Intención/Decisión","Compra/Conversión","Engagement/Retención"]
- **Foco:** buyer
- **Mercado:** DE

## Instrucciones
1) Para **cada fase**, propone **hasta 3 métricas leading (KPI-3)** que muevan `conversion_rate_from_search_to_order`.  
2) Añade **1 guardrail global** que proteja el camino crítico (Search→PDP→Carrito→Checkout→Pago).  
3) Para cada métrica, incluye: **nombre (snake_case)**, **definición**, **fórmula** (numerador/denominador + ventana temporal), **owner**, **frecuencia** (semanal/mensual).  
4) Evita métricas de vanidad y duplicadas. Si dos son casi idénticas, elige **una** y justifica en 1 línea.  
5) Si una fase no necesita 3 métricas, usa solo las esenciales.

## Salida esperada (tablas)

### A) KPI-3 por etapa del buyer journey
| Fase | Métrica (leading) | Definición | Fórmula | Owner | Frecuencia |
|---|---|---|---|---|---|

<!-- Sugerencias de arranque (ejemplos, puedes ignorarlas o mejorarlas):
Descubrimiento:
- search_to_pdp_click_rate — % de sesiones con búsqueda que hacen ≥1 click a PDP
- zero_results_rate (↓) — % de consultas con 0 resultados
- avg_rank_of_first_click — posición media del primer click

Interés/Consideración:
- add_to_cart_rate_from_pdp — % de sesiones con búsqueda que añaden al carrito desde PDP
- back_to_results_rate (↓) — % de veces que el usuario vuelve a SERP sin añadir al carrito
- pdp_views_per_session_with_search — PDP vistas por sesión con búsqueda

Intención/Decisión:
- checkout_start_rate — % de sesiones con búsqueda que inician checkout
- cart_abandonment_rate (↓) — % de carritos que no llegan a checkout
- time_to_checkout_start_median — mediana de tiempo desde el primer PDP hasta iniciar checkout

Compra/Conversión:
- payment_success_rate — % de checkouts que terminan en pago
- checkout_error_rate (↓) — errores por 100 checkouts
- payment_latency_p95 — p95 de tiempo desde “pagar” a confirmación

Engagement/Retención:
- buyer_return_rate_30d — % de compradores que vuelven en 30 días
- post_purchase_nps_promoters_share — % de promotores en NPS post-compra
- email_click_back_to_site_rate — % de clics de emails que regresan al sitio
-->

### B) Guardrail global (camino crítico)
| Guardrail | Definición | Fórmula | Umbral/Alerta (placeholder) | Owner | Frecuencia |
|---|---|---|---|---|---|
| critical_path_error_rate | Fallos en el camino crítico (Search→PDP→Carrito→Checkout→Pago) | `sessions_with_critical_errors / sessions_with_search_or_checkout` **o** `total_error_responses_4xx_5xx / total_requests` | **[Define tu umbral]** | Platform/Eng | Semanal |

### C) Notas / Supuestos (1–5 bullets)
- Indica si los cálculos se basan en **sesiones con búsqueda**.
- Define **ventanas** (p. ej., 7/30 días) para consistencia.
- Evita contar múltiples **reformulaciones** como sesiones distintas.

## Criterios de calidad (checklist)
- Cada leading **conecta causalmente** con la conversión desde búsqueda.  
- Máx. **3** por fase; sin duplicados ni vanity metrics.  
- Fórmulas **calculables**; owners claros; frecuencia definida.  
- Guardrail global **relevante** y accionable.
