# Mr. President v0.3: el árbol de decisiones

Bruno, esto reemplaza la lógica de v0.2. Los testers dijeron que las decisiones no se sentían y que no había rejugabilidad. El problema era estructural: 27 cartas casi en línea recta, una sola bifurcación real y seis números ocultos que decidían el final recién al terminar. En v0.3 el juego es un árbol: cada decisión importante cambia de rama y la partida puede terminar en cualquier punto.

Todo está armado en **tu formato** (`events.json` como diccionario por id, `trigger`, `else`, `next`, `crisis.timer`), así que casi no hay que tocar el motor. Son cuatro cambios chicos, abajo.

## Archivos

| Archivo | Qué es | Reemplaza a |
|---|---|---|
| `events_v03.json` | Los 34 eventos: 14 cartas viejas que se quedan y 20 nodos nuevos o adaptados | `data/events.json` |
| `endings_v03.json` | 23 variantes de los 10 finales originales | `data/endings.json` |
| `day_transitions_v03.json` | Diarios con variantes nuevas para las ramas de ataque y negociación | `data/day_transitions.json` |
| `codex_v03.json` | Códex con los desbloqueos remapeados y 8 entradas nuevas | `data/codex.json` |
| `scenes_v03.rpy` | Las 20 labels de las escenas nuevas, con el mismo esquema que `script.rpy`, y 3 personajes de voz nuevos | se suma a `script.rpy` |
| `simulate.py` | Recorre todas las rutas con la misma semántica que tu motor | el viejo `mr_president_engine.py` |
| `rutas_de_prueba.json` | Una ruta verificada por variante de final. **Son los tests.** | la hoja "Rutas de prueba" |

`nodos_v03.json` fue un borrador intermedio; ya está todo volcado en estos archivos.

## Cómo funciona ahora

- **Nodos**: decisiones que cambian de rama. Las cartas ponen flags de ruta (`route_attack`, `route_trunk`, `route_negotiate`) y el `next` de cada evento lista candidatos; gana el primero cuyo `trigger` se cumple, como ya hacía tu `next_event`.
- **Tramos**: las cartas viejas que quedan (D01 a D03, D06, D09 a D11, D13 a D15, D17, D23) ya no mueven números. Solo ponen flags, y esos flags **habilitan, bloquean o hacen fallar** opciones en los nodos siguientes (con `available_if` o con `trigger`/`else` de la carta).
- **Fin de partida**: la carta final pone `game_over: true` y `end_<variante>: true` (por ejemplo `end_E01c`). `decide_ending()` sigue funcionando igual: cada variante tiene como condición su flag `end_`.
- **Sin números**: `stats` va vacío en todas las cartas. `state.json` puede quedar como está; nadie lo usa.

Las tres ramas:

- **Ataque**: ROOT_1 A, D06, ATK_SCOPE, D14, D15, y después ATK_BERLIN → ATK_TACTICAL o ATK_LANDING → ATK_PREAUTH.
- **Tronco (cuarentena)**: ROOT_1 B, ROOT_2 A, D09, D10, D11, TRK_SPEECH, D13, D14, D15, TRK_SHIP, TRK_SUBMARINE, D17, TRK_U2, TRK_MAULTSBY, TRK_TURKEY, TRK_VERIFY, D23, TRK_FALSE_ALARM.
- **Negociación**: ROOT_1 B, ROOT_2 B, D06, NEG_KEATING, NEG_WHO, y después NEG_TIME → NEG_LEAK (con la rama oculta S01 → S02) o NEG_CASTRO.

Las fechas nunca retroceden dentro de una ruta, así que los diarios de transición salen en orden.

## Los cuatro cambios de motor

**1. Fin de partida temprano.** Al principio de `next_event`, antes de `check_nuclear()`:

```python
if flags.get("game_over"):
    chosen_ending = decide_ending()
    return "ENDING"
```

**2. Logros y galería por familia, no por variante.** Cada final tiene `family` (E01 a E10). La galería, el contador "x / 10" y el mini documental cuentan familias:

```python
FAMILIES = sorted(set(e.get("family", e["id"]) for e in endings))
for f in FAMILIES:
    achievement.register("ending_" + f.lower())
achievement.register("all_endings", stat_max=len(FAMILIES), stat_modulo=1)

def unlock_ending(ending):
    before = codex_unlocked_set()
    fam = ending.get("family", ending["id"])
    persistent.endings_seen.add(fam)
    persistent.variants_seen.add(ending["id"])   # default persistent.variants_seen = set()
    achievement.grant("ending_" + fam.lower())
    achievement.progress("all_endings", len(persistent.endings_seen))
    renpy.save_persistent()
    codex_check_new(before)
```

En `label ENDING`, llamar `unlock_ending(chosen_ending)` en vez de `unlock_ending(name)`. En `screens.rpy` (líneas 541, 572 y 605), la galería tiene que iterar `FAMILIES` en vez de `endings`. Si querés, cada casillero puede mostrar "2/4" con las variantes encontradas de esa familia.

**3. Pantalla de final.** Mostrar `variant_label` debajo del título, y después del cuerpo la primera línea de `sealed_by` que se cumpla. Es la línea que le dice al jugador qué decisión de turnos anteriores lo condenó, y sin ella las muertes tardías se sienten aleatorias:

```python
for s in chosen_ending.get("sealed_by", []):
    if check_trigger(s["if"]):
        ending_nvl("{i}%s{/i}" % s["text"])
        break
```

**4. Personajes de voz.** `scenes_v03.rpy` define `navy`, `nato` y `norad` igual que `air_force`: sin sprite en pantalla, solo el cartel con el nombre (el `image=` de Bundy es solo la etiqueta que posiciona el globo; si el globo queda apuntando a la nada, conviene darles una posición propia en el editor de globos). Las labels viejas de eventos que ya no existen (D04, D05, D07, D08, D12, D18, D19, D21, D22, C01 a C04) se pueden borrar: nunca se llega a ellas.

## Cómo testear

```
python3 simulate.py events_v03.json
```

Recorre las 11.736 rutas posibles y comprueba que todas terminen en exactamente un final, que no queden eventos huérfanos y que las 23 variantes sean alcanzables. También informa la probabilidad de cada final jugando al azar. Para reproducir una partida:

```
python3 simulate.py events_v03.json --route "D01-A D02-A D03-A ROOT_1-A D06-A ATK_SCOPE-A D14-A D15-A ATK_BERLIN-A"
```

Si tu implementación recibe cualquiera de las rutas de `rutas_de_prueba.json` y no llega al mismo final, algo está mal.

## Ojo con esto

- En `historical_notes.json` del repo hay una coma de más (línea 7) y el archivo no parsea.
- ATK_TACTICAL, ATK_PREAUTH y TRK_FALSE_ALARM usan `bg_crisis_max`; el resto de las crisis, `bg_crisis_normal`.
- Las voces institucionales (Air Force, Navy, Operator, Counsel, NATO, NORAD) no llevan imagen, a propósito: hablan con el cartel del nombre y nada más.
- `kind`, `speaker`, `line`, `room`, `document` y `historical_note_es` en los eventos son para el equipo; el motor los ignora.
