"""Diarios, codex y labels Ren'Py para v0.3.

Uso: python3 build_extra.py <repo/game/data> <nodos_v03.json> <events_v03.json>
Salidas: day_transitions_v03.json, codex_v03.json, scenes_v03.rpy
"""
import json, sys, copy, os

data, nodos_path, ev_path = sys.argv[1:4]
EV = json.load(open(ev_path))
NODOS = json.load(open(nodos_path))

# ------------------------------------------------------------------ diarios
dt = json.load(open(os.path.join(data, "day_transitions.json")))
NEW = {
    "OCT 18, 1962": [
        {"if": {"lied_to_senate": True}, "headline": "WHITE HOUSE SEES NO PROOF OF OFFENSIVE ARMS IN CUBA",
         "deck": "Keating stands by his charges; Gromyko calls on President", "photo": "rally"},
        {"if": {"congress_briefed": True}, "headline": "PRESIDENT MEETS CONGRESS LEADERS BEHIND CLOSED DOORS",
         "deck": "Gromyko calls at White House; no statement issued", "photo": "rally"},
    ],
    "OCT 24, 1962": [
        {"if": {"berlin_convoy": True}, "headline": "SOVIETS SEAL BERLIN; ALLIED CONVOY ON AUTOBAHN",
         "deck": "Raids on Cuba continue; NATO forces on alert", "photo": "destroyer"},
    ],
    "OCT 26, 1962": [
        {"if": {"invasion_launched": True}, "headline": "MARINES LAND IN CUBA",
         "deck": "Pentagon: resistance 'heavier than expected'", "photo": "destroyer"},
    ],
}
for paper in dt["newspapers"]:
    paper["variants"] = NEW.get(paper["after_date"], []) + paper["variants"]
    paper["variants"] = [v for v in paper["variants"] if v["if"] != {"hard_line_public": True}]
json.dump(dt, open("day_transitions_v03.json", "w"), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ codex
cx = json.load(open(os.path.join(data, "codex.json")))
REMAP = {"D04": "ROOT_1", "D05": "ROOT_2", "D07": "ROOT_1", "D08": "ATK_SCOPE", "D12": "TRK_SPEECH",
         "C01": "ATK_PREAUTH", "C02": "TRK_SUBMARINE", "C03": "TRK_U2", "C04": "TRK_U2",
         "D18": "TRK_TURKEY", "D19": "TRK_TURKEY", "D21": "NEG_CASTRO", "D22": "TRK_VERIFY"}
BY_ID = {"DEF-09": "TRK_MAULTSBY", "STA-08": "NEG_WHO", "PER-STEVENSON": "ROOT_2", "PER-GROMYKO": "NEG_WHO",
         "STA-09": "TRK_SHIP"}
log = []
for cat, entries in cx.items():
    for name, e in entries.items():
        sc = e.get("unlock", {}).get("scene")
        if sc is None:
            continue
        new = BY_ID.get(e["id"]) or REMAP.get(sc)
        if new and new != sc:
            e["unlock"]["scene"] = new
            log.append(f'{e["id"]}: {sc} -> {new}')
for cat, entries in NODOS["codex_new"].items():
    cx.setdefault(cat, {})
    for name, e in entries.items():
        e = copy.deepcopy(e)
        if isinstance(e["unlock"].get("scene"), list):
            e["unlock"]["scene"] = e["unlock"]["scene"][0]
        cx[cat][name] = e
        log.append(f'{e["id"]}: nueva ({e["unlock"]["scene"]})')
bad = [(e["id"], e["unlock"]["scene"]) for es in cx.values() for e in es.values()
       if "scene" in e.get("unlock", {}) and e["unlock"]["scene"] not in EV and e["unlock"]["scene"] != "start"]
json.dump(cx, open("codex_v03.json", "w"), ensure_ascii=False, indent=2)
print("codex:", len(log), "cambios; desbloqueos a escenas inexistentes:", bad or "ninguno")
open("codex_v03_cambios.txt", "w").write("\n".join(log) + "\n")

# ------------------------------------------------------------------ labels Ren'Py
CHAR = {"rusk": "dean", "mcnamara": "rob", "bundy": "bundy", "rfk": "rfk", "taylor": "taylor",
        "air_force": "air_force", "counsel": "counsel", "navy": "navy", "nato": "nato", "norad": "norad"}
SPRITE = {"rusk": "dean rusk", "mcnamara": "robert mcnamara", "bundy": "mcgeorge bundy",
          "rfk": "rfk", "taylor": "general maxwell taylor"}
BG = {"Office": ("bg_despacho", "init_pos_despacho"), "Decision": ("bg_decisions", "init_pos_decision"),
      "Crisis": ("bg_crisis_normal", "init_pos_crisis"),
      "Crisis_alert": ("bg_crisis_max", "init_pos_crisis")}

def esc(t):
    return t.replace('"', '\\"').replace("[", "[[")

out = ["# Escenas v0.3 generadas desde events_v03.json. Mismo esquema que las labels de script.rpy.",
       "# Personajes de voz nuevos (sin sprite propio todavia, mismo placeholder que air_force):",
       'define navy = Character("U.S. NAVY", image="/images/sprites/McGeorge Bundy.png", callback=type_sound, kind=bubble)',
       'define nato = Character("NATO COMMAND", image="/images/sprites/McGeorge Bundy.png", callback=type_sound, kind=bubble)',
       'define norad = Character("NORAD", image="/images/sprites/McGeorge Bundy.png", callback=type_sound, kind=bubble)',
       ""]
for eid, e in EV.items():
    if "line" not in e:
        continue
    bg, pos = BG[e["room"]]
    out += [f"label {eid}:", f'    $ current_scene = "{eid}"', "",
            f"    scene {bg} at bg_size with  Dissolve(0.2)", ""]
    if e["speaker"] in SPRITE:
        out += [f'    show expression "{SPRITE[e["speaker"]]}" at {pos}', ""]
    out += [f'    {CHAR[e["speaker"]]} "{esc(e["line"])}"', "",
            "    $ card_a = events[current_scene][cards_key][a_card_key]",
            "    $ card_b = events[current_scene][cards_key][b_card_key]", ""]
    if "crisis" in e:
        out += ["    $ seconds, default_card = crisis_info(current_scene)",
                "    call screen decision_folder(card_a, card_b, seconds, default_card)"]
    else:
        out += ["    call screen decision_folder(card_a, card_b)"]
    out += ["    $ choice = _return", "",
            "    $ aftermath=apply_choice(choice, current_scene)",
            '    narr_bubble "[aftermath]"',
            "    scene black with Fade(0.2,0.0, 0.2)",
            '    $ next_e = next_event(events[current_scene]["next"],events)',
            "    jump expression next_e", ""]
open("scenes_v03.rpy", "w").write("\n".join(out))
print("labels:", sum(1 for e in EV.values() if "line" in e))
