# Rama v03-arbol

Sale de `beta-test-modification` (9574f71), con todo lo de las rondas de beta, y le monta encima el árbol de decisiones v0.3. Los archivos originales del paquete v0.3 están en esta carpeta.

## Qué se hizo
- **`data/events.json`:** es el de v0.3. A las cartas que siguen (D01 a D17, D23, S01, S02) les quedaron los agregados de beta: `question`, `visibility`, `in_1962`, `allison_model` y `duel_left_card`. Los nodos que reusan decisiones viejas también los heredaron (ROOT_1 de D07, ATK_SCOPE de D08, TRK_SPEECH de D12, TRK_U2 de C03, TRK_VERIFY de D22). Los otros 15 nodos nuevos tienen pregunta y sello nuevos, para revisar.
- **`data/endings.json`:** son las 23 variantes de v0.3. Cada una hereda `cutscene`, `hint` y `stamp` de su familia.
- **`data/codex.json`:** es el de v0.3, que usaba DEF-10 y STA-10 para otras entradas. Las dos de la ronda 2 volvieron con id nuevo:
  - DEF-13 "DEFCON 2", que se abre en TRK_SHIP o ATK_BERLIN;
  - STA-13 "The Public", que se abre en TRK_SPEECH o NEG_LEAK.
- **`data/day_transitions.json`:** son los diarios de la rama de beta. Adelante de cada fecha se agregaron las variantes nuevas de v0.3.
- **`scenes_v03.rpy`:** son las 20 labels nuevas. `navy` ya estaba definido en `script.rpy`, así que se sacó de acá. Las crisis tienen la música de crisis, como el resto.
- **Motor:** `game_over` corta la partida, y galería, logros, contador, epílogo e informe guardado se cuentan por familia (`FAMILIES`, `family_endings()`). Además, la pantalla del final muestra `variant_label` y la línea de `sealed_by`.

## Verificado
`python3 v03/simulate.py game/data/events.json` recorre las 11.736 rutas sin problemas. Las 23 variantes son alcanzables y las 23 rutas de `rutas_de_prueba.json` llegan a su final.

## Falta
- Probarlo en Ren'Py (Lint).
- Ubicar los globos de los personajes de voz nuevos.
- Las cinemáticas y los noticieros finales se eligen por familia, con condiciones del sistema viejo. Hay que revisar que cada variante muestre algo que tenga sentido.
- Las labels viejas que ya no se usan (D04, D05, D07, D08, D12, D18, D19, D21, D22, C01 a C04, X01 a X04) siguen en `script.rpy`. Nunca se llega a ellas.
