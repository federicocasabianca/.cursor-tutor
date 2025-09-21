# Experiment Brief — PDP → ATC (Plantilla v2.1)

> **Objetivo:** Diseñar un A/B para aumentar **`pdp_to_atc_rate`** (base = *sesiones con PDP*) con **un solo cambio** en la variante. Completa y adjunta 1 slide con la síntesis.

---

## 0) Metadatos
- **Equipo:** {{equipo}}
- **Owner:** {{owner}}
- **Fecha:** {{YYYY-MM-DD}}
- **ID experimento:** {{exp_pdp_atc_###}}
- **Tipo de PDP:** {{Unitario | Bundle | Interactivo}}
- **Plataforma / device:** {{Web Desktop | Web Mobile | App}}
- **Unidad de aleatorización:** {{usuario | cookie persistente}}
- **Scope (apples-to-apples):** {{País}}, {{canal}}, {{device}}, {{población}}, **ventana** {{días}}  
  _Ejemplo_: DE · Web · Desktop · **sesiones con PDP** · 14 días
- **Exclusiones:** {{bots, staff, tráfico QA, …}}

---

## 1) Problema y objetivo
**Contexto (datos):**  
- `gmv_per_session` cayó {{-X%}} ({{M0}}→{{M1}}). El funnel muestra deterioro en **{{paso_culpable}}**.  
- Baseline `pdp_to_atc_rate` = **{{p0}}**.  
**Objetivo de negocio:** revertir la caída en `gmv_per_session` actuando sobre **PDP→ATC**.

> **Evidencia**: añade 1 screenshot de una PDP real (anota fricción) o enlace.

---

## 2) Hipótesis (causa → efecto → porqué)
**Si** hacemos **{{cambio_unico_en_PDP}}**, **entonces** `pdp_to_atc_rate` **{{sube/baja}}** porque **{{mecanismo}}** en **{{segmento}}**.

- **Causa (cambio):** {{ej. CTA “Añadir al carrito” sticky en PDP}}  
- **Efecto (métrica):** {{pdp_to_atc_rate ↑}}  
- **Racional:** {{visibilidad/jerarquía/menos fricción ⇒ más ATC}}

---

## 3) Métricas
### 3.1 Principal (decide el test)
- **Nombre:** `pdp_to_atc_rate`  
- **Definición:** sesiones con **ATC** / **sesiones con PDP**  
- **Base:** sesiones con PDP  
- **Ventana:** {{misma ventana que scope}}

### 3.2 Secundarias *(para que completes)*
> **Instrucción:** Elige **máx. 2** métricas que **contextualicen** la principal (impacto en negocio o pasos adyacentes).  
> **Pistas (elige solo si aplica):** `orders_per_session`, `gmv_per_session`, `checkout_start_rate`, `payment_success_rate`, *(interactivos)* `try_demo_rate`, *(bundles)* `bundle_attach_rate`.

- Secundaria 1: ____________________ (definición breve)  
- Secundaria 2: ____________________ (definición breve)

### 3.3 Counter / Guardrails *(para que completes)*
> **Instrucción:** Define **2–3** guardrails para proteger **salud técnica** y **experiencia/negocio**.  
> **Pistas (elige 2–3):** `pdp_latency_p95`, `checkout_error_rate`, `refund_rate_14d`, `margin_rate`, *(interactivos)* `interactive_error_rate`.

| Guardrail | Definición (1 línea) | Umbral / alerta |
|---|---|---|
| ____________________ | ____________________ | ____________________ |
| ____________________ | ____________________ | ____________________ |
| ____________________ | ____________________ | ____________________ |

---

## 4) Parámetros del test
### 4.1 Baseline (p0)
> **Qué es:** la tasa **actual** de la métrica principal.  
> **Cómo se obtiene:** del **análisis de funnel** con el mismo **scope** (país, device, ventana, definiciones).  
> **Si no hay baseline:** usa una **referencia razonable**:  
> - **Histórico reciente** (2–4 semanas comparables) y toma **mediana** o **p75** (top quartil) para evitar outliers.  
> - **Benchmark externo** de e‑commerce/retail si el histórico es insuficiente.  
> **Ejemplo didáctico:** `p0 = 0,18` (18%).

### 4.2 MDE (Minimal Detectable Effect)
> **Definición:** el **cambio mínimo** que te importa **detectar** con fiabilidad.  
> **Tipos:** **absoluto (p.p.)** y **relativo (%)**.  
> **Para qué sirve:** fija expectativas y determina **N** y **duración**.  
> **Si no tienes target claro:** usa el **mínimo cambio valioso** para negocio o ajusta al **tráfico disponible** (con poco N, MDE mayor).  
> **Ejemplo:** MDE_abs **+2 p.p.** (18%→20%) = **+11,1%** relativo.

### 4.3 “n por variante” (¿qué es N?)
> **Definición:** número de **observaciones por variante** (control y experimento) necesarias para detectar el **MDE** con la **confianza** deseada.  
> **Unidad en este ejercicio:** **sesión con PDP** (o usuario si así se define).  
> **Ejemplo guía:** `p0=18%`, **MDE=+2 p.p.**, **α=0,05**, **potencia=80%** ⇒ **N ≈ 6.000 por variante**.  
> **Calculadoras recomendadas:** [Evan Miller — Sample Size](https://www.evanmiller.org/ab-testing/sample-size.html) (dos colas).

### 4.4 Duración mínima
> **Depende de:** (a) **tráfico** diario por variante **y** (b) tu **confianza estadística** (α y potencia).  
**Fórmula práctica:** `duración ≈ ceil(N_por_variante / (tráfico_diario_total × split))`  
**Recomendación:** aunque llegues al N, **ejecuta** **≥ 2 semanas** para cubrir ciclos (laborables/fines).

### 4.5 ¿Qué son α, potencia y “dos colas”? (versión directa)
- **α (alfa)**: umbral de **riesgo de falso positivo** (error tipo I). Típico: **0,05**.  
  *Interpretación*: aceptas hasta un **5%** de probabilidad de declarar “hay efecto” cuando en realidad **no lo hay**.
- **Potencia (1−β)**: probabilidad de **detectar** un efecto **real** del tamaño del **MDE**. Típico: **80%**.  
  *Interpretación*: si el efecto verdadero es tu MDE, lo detectarás **8 de cada 10** veces.
- **Prueba “de dos colas”**: evalúa **mejoras y empeoramientos** (no solo subidas). Es el estándar si cualquier dirección importa.
- **p-value vs α**: el **p-value** es la probabilidad (bajo “no hay efecto”) de observar una diferencia **tan grande o mayor** que la medida. Si **p ≤ α**, decimos **“significativo”**. [Qué es un p‑value (explicado simple)](https://www.simplypsychology.org/p-value.html)
- **IC 95%**: rango de valores compatibles con los datos al 95%. Si el **IC 95%** de la diferencia **no incluye 0**, el resultado es **significativo** a **α=0,05**.
- **Relación con N y duración**: **menor α** (más estricto) **y/o mayor potencia** ⇒ **más N por variante** ⇒ normalmente **más duración**.
- **Ejemplo guía**: `p0=18%`, **MDE=+2 p.p.**, **α=0,05**, **potencia=80%** ⇒ **~6.000 observaciones por variante**.

---

## 5) Diseño de variantes (un solo cambio)
| Variante | Descripción del cambio | Mock / screenshot | Riesgo técnico |
|---|---|---|---|
| **Control** | PDP actual | {{link}} | — |
| **Variante** | {{cambio_unico}} | {{link}} | {{bajo/medio/alto}} |

---

## 6) Sanity & Monitoreo
- **SRM** diario (split observado ≈ split esperado).  
- **Instrumentación**: eventos `pdp_view`, `cta_atc_click`, `cart_created`, `checkout_start`, `payment_success`.  
- **Guardrails**: monitoreo continuo; pausa si se supera el umbral ≥ 2 días.

---

## 7) Plan de análisis
### 7.1 “Freeze” y lectura
> **Freeze:** no cambies reglas ni **te dejes llevar por resultados prematuros**; **lee** al final del periodo acordado.

### 7.2 ¿Qué es “prueba de 2 proporciones”?
> Comparar **dos tasas** (control vs **variante**) de la métrica principal para ver si la diferencia es **real** o podría ser **azar**.  
Reporta **Δ en p.p. y %**, y el **p-value/IC 95%** que devuelva tu herramienta (no necesitas la fórmula).

---

## 8) Criterios de decisión (con Future Work)
| Caso | Condiciones | Acción (Future Work) |
|---|---|---|
| **Significativo (éxito de la variante)** | PM mejora y es significativa; guardrails OK; MDE alcanzado | **Despliegue gradual** (25%→50%→100%), define **grupos** y **monitoriza** guardrails. Documenta el impacto estimado en negocio. |
| **Significativo (fracaso de la variante)** | PM empeora significativamente **o** guardrails KO | **No-Go** y **reversión**. Analiza qué funcionó/no, documenta **aprendizajes** y decide si **iterar** con otro cambio o pasar a otra palanca. |
| **No significativo** | Efecto no concluyente | Valora **re-test** (más N/duración) o **ajustar MDE/diseño**. Si no re-test, documenta el **learning** y decisión de **prioridad** frente a otras palancas. |

---

## 9) Riesgos y dependencias
- **Riesgos:** {{tracking, performance, tráfico insuficiente, cambios paralelos}}  
- **Mitigación:** {{plan}}  
- **Dependencias:** {{UX/FE/Infra/Legal/Finance}} (si aplica)

---

## 10) Aprendizaje esperado
> **Genera las preguntas que esperas responder con este A/B test.** Como guía, considera:  
- ¿La variante **mueve** `pdp_to_atc_rate` al menos el **MDE**?  
- ¿Cuál es el **impacto estimado** en `gmv_per_session` y `orders_per_session`?  
- ¿Se mantuvieron **guardrails** dentro de umbrales?  
- ¿En qué **segmentos** (máx. 2–3) funcionó mejor/peor?

---

### Checklist rápido (antes de lanzar)
- [ ] Scope bloqueado y documentado
- [ ] Un solo cambio por variante
- [ ] PM/guardrails definidos con umbrales
- [ ] MDE, N y duración estimados
- [ ] SRM y monitoreo configurados
- [ ] Plan de análisis y criterios de decisión claros
