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

---

# Arreglos chicos (T09, T11, T13, T14, T18, T19)

- **T09** (`screens.rpy`, `decision_folder`): la carta de la izquierda se elige al azar en cada decisión. Los IDs A/B no cambian.
- **T11** (`screens.rpy`, `bubble`): el cargo aparece debajo del nombre (`SPEAKER_TITLES`). Como el namebox tiene `yoffset -35`, puede pisar el globo: ajustar si hace falta.
- **T13** (`screens.rpy`, screen `crisis_hud`): arriba a la izquierda se ve la fecha de la escena y "DAY X OF 13". Se activa al empezar D01 y se apaga en el final. No aparece en el diario ni en el códex. La posición es provisoria.
- **T14** (`script.rpy`, `label ENDING`): al terminar el expediente sale "END OF FILE" con el conteo de finales encontrados.
- **T18** (`events.json`, C03): con represalia automática, el timer baja a 15 s (antes quedaba igual, en 30).
- **T19**: en D01 decía "could... but They could". Corregido. El resto del texto coincide con el diseño y no tiene errores de tipeo.

---

# Imágenes nuevas

- `images/cutscenes/`: los 5 cuadros de la cutscene nuclear.
- `images/news/`: 11 fotos de diario. En `day_transitions.json`, cada titular apunta ahora a su foto. Siguen con las fotos viejas: OCT 17 y 19 (`rally`, que corresponde), OCT 22, 23 y 27 "WORLD WAITS" (`television`), "BOMBERS ON ALERT" y "MARINES LAND" (`destroyer`).
- La caja de foto del diario es casi 16:9 y las fotos son 4:3. Con `fit "cover"` se recortan arriba y abajo: revisar que no se corte nada importante.

---

# Hotspot del códex y última foto

- El rectángulo blanco del hotspot del códex se reemplazó por un contorno rojo, uno por fondo (`gui/codex_hotspot/`, PNG transparente estirado a toda la pantalla). Pulsa mientras hay archivos sin leer y queda fijo con el mouse encima. **Bruno: la posición final se ajusta a mano.** Para moverlo se edita el PNG. Para ver el área clickeable, poner `CODEX_DEBUG = True`.
- `CODEX_SPOTS` ahora coincide con cada contorno: lo que se ilumina es el área clickeable.
- `tv_window` es la foto de "WORLD WAITS ON MOSCOW".

- `images/codex/PER-LBJ.png`: retrato de Lyndon B. Johnson para el códex, recortado con `recortar_caras.py`.
