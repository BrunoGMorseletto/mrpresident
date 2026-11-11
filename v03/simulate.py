"""Recorre todas las rutas de events_v03.json con la misma semantica que script.rpy.

Uso: python3 simulate.py events_v03.json [--route "D01-A D02-B ..."]
Comprueba: toda ruta termina en exactamente un final, ningun evento queda huerfano,
todas las variantes son alcanzables. Informa cantidad de rutas y largo (en cartas) por final.
"""
import json, sys
from collections import defaultdict

EV = json.load(open(sys.argv[1]))
OPS = {"<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b, "==": lambda a, b: a == b,
       "!=": lambda a, b: a != b, "<": lambda a, b: a < b, ">": lambda a, b: a > b}

def check(trigger, flags):
    for key, cond in trigger.items():
        if key == "any":
            if not any(check(s, flags) for s in cond):
                return False
        elif key == "not":
            if check(cond, flags):
                return False
        elif isinstance(cond, bool):
            if bool(flags.get(key, False)) != cond:
                return False
        else:
            v = flags.get(key, False)
            for op, n in cond.items():
                if not OPS[op](v, n):
                    return False
    return True

def next_event(cands, flags):
    if flags.get("game_over"):
        return "ENDING"
    for name in cands:
        if name == "ENDING":
            return "ENDING"
        if check(EV[name]["trigger"], flags):
            return name
    return "ENDING"

def apply(eid, choice, flags):
    c = EV[eid]["cards"][choice]
    f = dict(flags)
    eff = c if check(c["trigger"], f) else c["else"]
    f.update(eff["flag"])
    return f

def ending_of(flags):
    ends = [k[4:] for k, v in flags.items() if k.startswith("end_") and v]
    return ends

results = defaultdict(list)
seen = set()
problems = []

def walk(eid, flags, route):
    if eid == "ENDING":
        ends = ending_of(flags)
        if len(ends) != 1:
            problems.append((route, ends))
        else:
            results[ends[0]].append(route)
        return
    seen.add(eid)
    for ch in "AB":
        c = EV[eid]["cards"][ch]
        if "available_if" in c and not check(c["available_if"], flags):
            continue
        f = apply(eid, ch, flags)
        walk(next_event(EV[eid]["next"], f), f, route + [eid + "-" + ch])

if "--route" in sys.argv:
    route = sys.argv[sys.argv.index("--route") + 1].split()
    flags, eid = {}, "D01"
    for step in route:
        e, ch = step.split("-")
        assert e == eid, f"esperaba {eid}, vino {e}"
        flags = apply(eid, ch, flags)
        eid = next_event(EV[eid]["next"], flags)
    print("termina en:", ending_of(flags), "| siguiente:", eid)
    sys.exit()

walk("D01", {}, [])
total = sum(len(v) for v in results.values())
print(f"rutas totales: {total}")
for k in sorted(results):
    lens = [len(r) for r in results[k]]
    print(f"{k:5s} rutas {len(lens):5d}  cartas min {min(lens):2d}  max {max(lens):2d}")
orph = set(EV) - seen
print("eventos que nunca aparecen:", sorted(orph) or "ninguno")
print("rutas con problema:", len(problems))
for r, e in problems[:5]:
    print("  ", e, " ".join(r))
expected = {"E01a","E01b","E01c","E01d","E02","E03a","E03b","E03c","E04a","E04b","E05",
            "E06a","E06b","E06c","E07a","E07b","E08a","E08b","E09a","E09b","E10a","E10b","E10c"}
print("variantes que faltan:", sorted(expected - set(results)) or "ninguna")
print("variantes de mas:", sorted(set(results) - expected) or "ninguna")
# ruta de ejemplo mas corta por variante (sirven como tests)
json.dump({k: " ".join(min(v, key=len)) for k, v in sorted(results.items())},
          open("rutas_de_prueba.json", "w"), indent=1)

# probabilidad de cada final si el jugador elige al azar (50/50 en cada carta disponible)
prob = defaultdict(float)
def walkp(eid, flags, p):
    if eid == "ENDING":
        prob[ending_of(flags)[0]] += p; return
    opts = [ch for ch in "AB" if not ("available_if" in EV[eid]["cards"][ch]
            and not check(EV[eid]["cards"][ch]["available_if"], flags))]
    for ch in opts:
        f = apply(eid, ch, flags)
        walkp(next_event(EV[eid]["next"], f), f, p / len(opts))
walkp("D01", {}, 1.0)
print("\nprobabilidad jugando al azar:")
fam = defaultdict(float)
for k in sorted(prob):
    fam[k[:3]] += prob[k]
    print(f"  {k:5s} {prob[k]*100:5.1f}%")
print("por familia:", {k: round(v*100, 1) for k, v in sorted(fam.items())})
