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

---

# Noticiero (T06) y opinión pública

**Cómo funciona.** El noticiero **reemplaza** al diario en los días en que pasa algo grande. No se suma.

- **Al cambiar de día**, `intermission` busca en `data/newsreels.json` un noticiero de esa fecha cuyo `if` se cumpla. Si encuentra uno, lo muestra en lugar del diario. Si no, sale el diario como siempre.
  - 22/10: va siempre (el discurso).
  - 24/10: si hubo ataque o abordaje.
  - 25/10: si hubo desembarco.
  - 27/10: si hubo represalia contra el SAM o canje público.
- **Antes del expediente final** (`label ENDING`), sale el noticiero `FINAL` que corresponde al final obtenido. Se elige por `endings` y `if`. E01 tiene su cutscene y E02 no lleva noticiero.
- **Cuadros "classified"**: tarjeta roja con lo que el público no supo. Por ejemplo, la promesa sobre Turquía en E06, o el canal de Robert Kennedy el 22/10.
- Se puede saltear con "SKIP NEWS" o avanzar con click. Cada cuadro dura 9 s, o lo que diga `seconds`.

**Archivos.**

- `script.rpy`: `find_newsreel`, `find_final_newsreel`, `newsreel_frames`, `label newsreel`, y los ganchos en `intermission` y en `ENDING`.
- `screens.rpy`: screen `newsreel_frame` y sus estilos. `NR_SCREEN` es el área de la imagen dentro del televisor.
- `gui/newsreel/`: `bezel.png` (marco de TV) y `scanlines.png`, dibujados por código.
- Las imágenes van en `images/newsreel/<nombre>.png`. Mientras falten, el cuadro se ve gris con el texto.
- Audio del 22/10: `audio/jfk_1962-10-22_excerpt.mp3`. Si no existe, no suena nada y el cuadro queda igual.

**Códex.** Entrada nueva en State: "The Public" (STA-10). Se desbloquea con D12.

---

# T08: halcón y paloma en D07

- D07 ahora tiene dos asesores en pantalla. Taylor, a la izquierda y espejado para que mire hacia el centro, pide el ataque. McNamara, a la derecha, defiende la cuarentena. Cada uno dice su línea antes de las cartas.
- Hay dos transforms nuevos, `duel_left` y `duel_right`. Bruno: ajustar `xpos` a ojo.
- Como las dos líneas son nuevas, los globos salen en la posición por defecto. Hay que ubicarlos con el editor de bubbles (Shift+B).
- Pasan a ser debates D11 (Anderson contra Rusk), D14 (Taylor contra Bundy) y D23 (LeMay contra McNamara). Hay dos personajes nuevos, `anderson` y `lemay`, con su cargo en `SPEAKER_TITLES`.
- Anderson y LeMay todavía no tienen sprite. El código los muestra solo si existe la imagen (`renpy.has_image`). Cuando estén, van a `images/sprites/` como `Admiral George Anderson.png` y `General Curtis LeMay.png`, y aparecen solos.
- Las 6 líneas nuevas necesitan ubicar los globos con Shift+B.

---

# T07, T04, T23

- **T07 (`day_transitions.json`)**: tapas con filtraciones del 16 al 21/10, según lo que decidió el jugador. Si ampliaste el círculo (D02-B) o compartiste las pruebas (D06-A), la prensa empieza a saber. Los movimientos militares (preparar el ataque o la invasión) se ven igual, decidas lo que decidas. Si mantuviste el círculo chico, salen las tapas de siempre.
- **T04 (`endings.json`)**: `intro_variants` en E03, E04, E06, E07, E09 y E10. El primer párrafo cambia según el camino.
- **T23 (`script.rpy`)**: `init_pos_despacho`, `init_pos_decision`, `init_pos_crisis` y `duel_right` aceptan `flip`. RFK aparece espejado en sus escenas sueltas, y Rusk en D11, para que mire a Anderson. Bruno: chequear que `xzoom -1` no corra el sprite de lugar.
- **Sprites nuevos**: `General Curtis LeMay.png` y `Admiral George Anderson.png`, con fondo transparente.

---

# E08 reescrito

- E08 ahora es "acuerdo inconcluso" (badge "Unfinished deal"): retiro anunciado, pero sin acuerdo escrito. Casi todas las rutas que llegan a E08 tienen el retiro anunciado, y el texto viejo decía lo contrario.
- Los párrafos de `body` pueden ser `{"if": ..., "text": ...}` (`ending_paragraphs` en `script.rpy`). En el raro caso sin retiro, el primer párrafo y el segundo cambian.
- En el menú Endings, `gallery_paragraphs()` muestra la versión principal y omite los párrafos marcados `"gallery": false`.

---

# Cierre de partida: informe y galería

**Flujo al terminar:** noticiero final → expediente → **informe** (screen `debrief`) → **galería de finales** (`endings_menu`, que se abre sola).

- **Informe** (`screens.rpy`, screen `debrief`; fondo `gui/debrief/folder.png`). Una carpeta con tres pestañas:
  - YOUR CRISIS: `recap_template` del final y hasta 3 fragmentos de `debrief.json`.
  - WHAT REALLY HAPPENED: hasta 5 momentos en los que la partida se apartó de 1962, sacados de `in_1962` en `events.json`.
  - THREE LENSES: cuántas decisiones caen en cada modelo de Allison (`allison_model`), cuál domina y cuántas decidió el reloj.
  - Las posiciones están en `DB_TABS`, `DB_LEFT`, `DB_RIGHT` y `DB_STAMP`, en píxeles de la imagen. Ajustar si el texto no cae en las hojas.
- **`script.rpy`**:
  - `choices_made` y `timed_out` registran la partida. El timer llama a `note_timeout()`.
  - `build_debrief()` arma los datos del informe.
  - Se sacó la línea "END OF FILE".
- **Galería** (`endings_menu(new_ending, after_run)`):
  - A la izquierda, el conteo, la frase del objetivo y, al pasar el mouse por un final bloqueado, su pista (`hint` en `endings.json`).
  - Sello "NEW" sobre el final recién obtenido.
  - Al terminar una partida, en lugar de "Return" hay tres botones: NEW CRISIS, CODEX y MAIN MENU.

---

# Ajustes después de la primera prueba en Ren'Py

- **Debates:** `duel_left` y `duel_right` corridos a la izquierda (`xpos` 680 y 1000), para que el globo de arriba a la derecha no tape al asesor.
- **Aviso del códex:** `gui.notify_ypos` pasa de 68 a 150, debajo de la fecha.
- **Hotspot debajo de las cartas:** `decision_folder` tiene ahora `zorder 95`, y el hotspot sigue en 90.
- **Sprites de Anderson y LeMay:** normalizados a la altura de cabeza y la escala de los demás, porque flotaban.
- **Fotos `destroyer` y `television`:** sin el borde claro.
- **`PER-SORENSEN`:** alejado, para que entre la cabeza.
- **Informe:** se sacó el sello rojo, tanto el texto como el dibujo de `folder.png`.
- **NEW CRISIS:** usa `Jump("start")`. `Start()` solo anda desde el menú principal, y por eso crasheaba.
- **Intro:** las esperas después de cada línea bajan a 2 s.

---

# Segunda ronda de prueba

- **Crash en E08** ("Character expects its what argument to be a string"): en el store de Ren'Py, `dict` es `RevertableDict`, así que `isinstance(b, dict)` daba falso con los datos del JSON. Ahora se usa `hasattr(b, "keys")`.
- **Cartas en los debates:** la carta que defiende el asesor de la izquierda queda a la izquierda (`duel_left_card` en `events.json`: D07, D11, D14 y D23). En el resto de las decisiones sigue siendo al azar.
- **Asesores en los debates:** bajan a `ypos 165` para que no floten sobre la mesa.
- **Pestaña Calendar del códex:** es un calendario de octubre de 1962 (screen `codex_calendar`). Los días con archivo se pueden clickear, los trece días de la crisis van sombreados, y "Before" y "After" quedan abajo.
- **Pista de los finales bloqueados:** va en la franja de papel debajo de los casilleros de la planilla.
- **Sala de crisis:** la carta que se ejecuta si se acaba el tiempo lleva una etiqueta roja, "IF THE CLOCK RUNS OUT", y la línea de abajo del reloj la nombra ("IF THE CLOCK RUNS OUT: LET THEM GO. Aircraft take off as planned.").
- **Calendario:** se arma sobre `gui/codex_calendar.png`, la hoja generada por Julián. Las líneas de la grilla se detectaron de la imagen (`CAL_ROWS`, `CAL_COLS`). Números, días y "OCTOBER 1962" van por código. Los trece días de la crisis aparecen tachados con una X roja. "Before" y "After" quedan en las dos últimas líneas.

---

# Créditos y cinemáticas de todos los finales

- Créditos: "Music: Thiago Chalon and Gastón Posse".
- Los diez finales tienen cutscene (`cutscene` en `endings.json`), de 2 a 4 cuadros con texto. Las imágenes van en `images/cutscenes/end_eXX_N.png`. Mientras falten, cada cuadro se ve en negro con su texto.
- Orden en `label ENDING`: noticiero final (la versión pública), después la cutscene (lo que pasó de verdad), después el expediente. E01 no tiene noticiero.
