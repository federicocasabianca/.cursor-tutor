# PROMPT 1 — Derivar Lagging / Leading / Guardrails desde un Flywheel (solo nodos y transiciones)

## Rol
Eres un Product Manager senior especializado en **marketplaces EdTech de dos lados**. Tu tarea es convertir un **flywheel** (con nodos y transiciones, sin métricas predefinidas) en un set claro de **métricas**: *lagging* (resultados), *leading* (palancas) y *guardrails* (salud/calidad). Responde en **español claro**.

## Contexto
- Compañía/analogía: **{{empresa}}** (marketplace EdTech tipo eduki.com/de).
- Dispones **solo** de los **nodos** del flywheel y sus **transiciones** (origen → destino). **Ignora gráficas o valores.**
- Objetivo de esta fase: **anclar métricas al modelo de negocio**. **No** diseñes KPI-3, **no** instrumentes eventos, **no** propongas herramientas.

## Entradas
- **Nodos del flywheel (lista, snake_case):** `{{nodos}}`  
  _Ej.: ["more_materials","better_choice","more_orders","happy_sellers"]_
- **Transiciones (origen -> destino, snake_case):** `{{transiciones}}`  
  _Ej.: ["upload_frequency -> more_materials","more_materials -> better_choice", ...]_
- **Lado de mercado en foco:** `{{lado_del_mercado}}` (buyer / author / ambos)
- **Mercado/país:** `{{mercado}}` (DE / ES / …)
- **Outcome global (opcional):** `{{outcome_global}}` (ej.: gmv_per_session)

## Instrucciones
1) Para **cada nodo**, propone:
   - **Lagging (1–2):** resultados que reflejan el éxito del nodo.
   - **Leading (3–5):** palancas **operables por producto** (≤8 semanas). Si un leading nace de una **transición**, indícalo como “desde _origen->destino_”.
   - **Guardrails (1–2):** salud/calidad/coste para evitar “ganar y romper”.
2) **No inventes nodos**; usa exactamente los de `{{nodos}}`.
3) Si una métrica podría pertenecer a varios nodos, colócala donde **mejor represente su uso operativo** y justifica en **1 línea**.
4) Cada métrica debe incluir **Definición**, **Fórmula sugerida** (numerador/denominador y ventana temporal), **Owner** y **Frecuencia** (semanal/mensual). Nombres en `snake_case`. Evita vanity metrics.
5) Si definiste `{{outcome_global}}`, añade la columna **contribución_al_outcome_global** con valores **(+ / 0 / –)** y una justificación de 1 línea.

## Salida esperada (tablas Markdown)

### A) Métricas por nodo del flywheel
| Nodo del flywheel | Tipo (lagging/leading/guardrail) | Métrica | Definición | Fórmula sugerida | Relación con transiciones (si aplica) | Contribución al {{outcome_global}} (+/0/–) | Owner | Frecuencia |
|---|---|---|---|---|---|---|---|---|

> Ejemplo de “Relación con transiciones”: `leading` = `upload_frequency_rate` · “desde `upload_frequency -> more_materials`”.

### B) Mapeo de transiciones → drivers (leading)
| Transición (origen -> destino) | Driver/Proxy (métrica leading propuesta) | Cómo empuja el nodo destino | Supuestos / notas |
|---|---|---|---|

### C) Ambigüedades / Puntos a confirmar
| Tema | Pregunta | Impacto si cambia |
|---|---|---|

### D) Observaciones (1–5 bullets)
- …

### E) Glosario exprés (si introduces siglas como GMV, AOV, CTR)
| Sigla | Definición (1 línea) | Nota / ¿confirmar? |
|---|---|---|

## Criterios de calidad (checklist)
- **Lagging** = resultado del nodo; **Leading** = palancas operables; **Guardrails** = salud/calidad/coste.  
- Cada **leading** traza a **≥1 transición** concreta del flywheel.  
- Métricas con **fórmulas calculables**, **owner** y **frecuencia** definidos.  
- **Sin** KPI-3, **sin** mapa de eventos, **sin** herramientas en esta fase.