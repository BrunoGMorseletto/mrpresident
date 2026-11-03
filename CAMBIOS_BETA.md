# Cambios post beta test (rama beta-test-modification)

Reemplazar estos 4 archivos dentro de `game/`:

- `data/events.json`
- `data/endings.json`
- `data/day_transitions.json`
- `script.rpy`

Después correr **Lint** (launcher de Ren'Py → Check Script) y jugar las rutas de prueba de abajo.

## Qué cambia

**T17, orden del 27/10.** D17 → D19 → C03 → C04 → D18 → D21 → D22. D19 aparece siempre. D18 pide canal privado y que no se haya aceptado el canje en público.

**Rama de escalada.** Disparar cierra el mazo diplomático y abre cartas nuevas:

- Si salió el ataque aéreo (C01-B, o C01-A fallido), el jugador no ve más la carta de Khrushchev ni los canjes. Sigue X01 (25/10, desembarcar o no). Con desembarco va X03 (crisis, 30 s: replegarse o avanzar). Sin desembarco va X02 (26/10, Berlín: firmeza o alto el fuego). Después, final. La partida termina dos días antes.
- Si hubo represalia contra el sitio SAM (C03), C04 aparece siempre. Si no se acepta la pausa, aparece X04 (crisis, 30 s: frenar o no el ataque del amanecer). Si se frena, se puede seguir hacia D22. Si no, final.

**Código (`script.rpy`).**

- `decide_ending()` ahora acepta `"alt_conditions"` en un final: una lista de condiciones alternativas, y alcanza con que se cumpla una. Hoy lo usa solo E09 (alto el fuego después del ataque).
- 4 escenas nuevas: X01, X02, X03 y X04. Tienen el mismo formato que las demás y quedaron antes de `label D17`.
- C02 ahora lo dice `navy` ("U.S. NAVY"), un personaje nuevo, en lugar de Air Force.

**Endings.** E04 pide `landing_recalled: false` (si te replegaste de la playa no es "victoria"). E09 tiene la condición alternativa `strike_ceasefire`. El archivo quedó reformateado: el contenido es el mismo salvo esas dos cosas.

**Diarios.** Hay una tapa nueva para el 25/10 (desembarco o no). La del 24/10 también sale si el ataque fue parcial.

## Rutas de prueba

| Ruta | Final esperado |
|---|---|
| D01-A D02-A D03-A D04-A D05-A D06-A D07-A D08-B D12-A D13-A D14-A D15-B C01-B X01-A X03-B | E04 |
| D01-A D02-A D03-A D04-A D05-A D06-A D07-A D08-A D12-A D13-A D14-B D15-B C01-B X01-B X02-A | E03 |
| D01-A D02-A D03-A D04-A D05-A D06-A D07-A D08-A D12-B D13-A D14-B D15-B C01-B X01-B X02-B | E09 |

(Verificadas con una simulación que copia la lógica de `script.rpy`.)

---

# T03: final nuclear (E01) y cutscene

**Código (`script.rpy`).**

- `label ENDING`: si el final tiene `"cutscene"` en `endings.json`, la reproduce antes del expediente (`label ending_cutscene`). Si tiene `"intro_variants"`, el primer párrafo cambia según cómo llegó el jugador. Las dos funciones son genéricas y sirven para cualquier final (T04).
- Funciones nuevas: `pick_variant()` y `ending_paragraphs()`, junto a `check_nuclear()`. Las condiciones usan la misma sintaxis que los triggers (`check_trigger`).
- Las imágenes van en `game/images/cutscenes/` (ver LEEME.txt ahí). Mientras no estén, cada cuadro se ve en negro con su texto, así que se puede probar ya.

**Datos (`endings.json`, E01).** Texto nuevo. El primer párrafo dice dónde empezó la cadena: desembarco, ataque aéreo, represalia contra el SAM o submarino en el mar. Hay 4 cuadros de cutscene.

**Prueba rápida de E01:** D01-A D02-A D03-A D04-A D05-A D06-A D07-A D08-A D12-A D13-A D14-A D15-A C01-B X01-B X02-A

---

# D22-B

*FULL ACCESS NOW* ya no suma escalada. Antes, pedir inspecciones después del anuncio del retiro podía disparar la regla nuclear.
