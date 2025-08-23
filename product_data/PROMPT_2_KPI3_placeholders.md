# PROMPT 2 — KPI-3 por etapa del Buyer Journey (a partir de un lagging) · CON PLACEHOLDERS

## Rol
Eres un PM senior en marketplaces. Tu trabajo es traducir un **lagging** de negocio centrado en buyer a **KPI-3 por etapa del journey** (máx. 3 leading por etapa) y definir **1 guardrail global**. Responde en español claro.

## Contexto
- Foco: **{{foco}}** (buyer / seller). Para este ejercicio usa "buyer".
- Este prompt **no** diseña instrumentación técnica ni herramientas; solo definiciones métricas accionables.

## Entradas
- **Lagging objetivo (buyer, versión por sesión):** `{{lagging_objetivo}}`  
  - Def: `sessions_with_search_that_end_in_order / sessions_with_search`
  - Variante (si la pides): `orders_attributed_to_search / total_search_queries`
- **Fases del buyer journey:** `{{fases}}`  
  _Ej.: ["Descubrimiento","Interés/Consideración","Intención/Decisión","Compra/Conversión","Engagement/Retención"]_
- **Mercado/país (opcional):** `{{mercado}}` (DE / ES / …)

## Instrucciones
1) Para **cada fase**, propone **hasta 3 métricas leading (KPI-3)** que muevan `{{lagging_objetivo}}`.  
2) Añade **1 guardrail global** que proteja el camino crítico (Search→PDP→Carrito→Checkout→Pago).  
3) Para cada métrica, incluye: **nombre (snake_case)**, **definición**, **fórmula** (numerador/denominador + ventana temporal), **owner**, **frecuencia** (semanal/mensual).  
4) Evita métricas de vanidad y duplicadas. Si dos son casi idénticas, elige **una** y justifica en 1 línea.  
5) Si una fase no necesita 3 métricas, usa solo las esenciales (calidad > cantidad).

## Salida esperada (tablas Markdown)

### A) KPI-3 por etapa del buyer journey
| Fase | Métrica (leading) | Definición | Fórmula | Owner | Frecuencia |
|---|---|---|---|---|---|

### B) Guardrail global (camino crítico)
| Guardrail | Definición | Fórmula | Umbral/Alerta (placeholder) | Owner | Frecuencia |
|---|---|---|---|---|---|

### C) Notas / Supuestos (1–5 bullets)
- …

## Criterios de calidad (checklist)
- Cada leading **traza causalmente** al `{{lagging_objetivo}}`.  
- Máx. **3** por fase; sin duplicados.  
- Fórmulas **calculables**; owners claros; frecuencia definida.  
- Guardrail global **relevante** para todo el funnel.
