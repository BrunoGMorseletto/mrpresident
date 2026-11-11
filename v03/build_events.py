"""Arma events_v03.json en el formato del motor de Bruno (Ren'Py).

Uso: python3 build_events.py <events.json v0.2 del repo> <salida>
Semantica que respeta:
- check_trigger: claves del mismo dict se combinan con AND; "any" es lista (OR); "not" es dict.
- next: lista de candidatos; gana el primero cuyo trigger de evento se cumple.
- card.trigger / card.else: si el trigger de la carta no se cumple, se aplican los efectos de else
  y se muestra aftermath_if_failed.
- Fin de partida: la carta pone game_over y end_<variante>. Requiere un cambio de dos lineas en
  next_event (ver LEEME).
"""
import json, sys, copy

src, out = sys.argv[1], sys.argv[2]
old = json.load(open(src))

def card(title, hint, icon, aftermath, flag=None, trigger=None, els=None, failed=None, **extra):
    c = {"title": title, "hint": hint, "icon": icon, "aftermath": aftermath,
         "stats": {}, "flag": flag or {}, "trigger": trigger or {}}
    if els is not None:
        c["else"] = {"stats": {}, "flag": els, "fail": True}
    if failed:
        c["aftermath_if_failed"] = failed
    c.update(extra)
    return c

def end(variant, **more):
    f = {"game_over": True, "end_" + variant: True}
    f.update(more)
    return f

def ev(date, trigger, a, b, nxt, speaker, line, room, note, crisis=None, document=None, kind="node"):
    e = {"date": date, "trigger": trigger, "cards": {"A": a, "B": b}, "next": nxt,
         "kind": kind, "speaker": speaker, "line": line, "room": room,
         "historical_note_es": note}
    if document:
        e["document"] = document
    if crisis:
        e["crisis"] = crisis
    return e

E = {}

# ---------------------------------------------------------------- tramos que se conservan
KEEP = ["D01", "D02", "D03", "D06", "D09", "D10", "D11", "D13", "D14", "D15", "D17", "D23", "S01", "S02"]
for k in KEEP:
    e = copy.deepcopy(old[k])
    e["kind"] = "tramo"
    for c in e["cards"].values():
        c["stats"] = {}
        if "else" in c:
            c["else"]["stats"] = {}
    E[k] = e

# Ruteo de los tramos. El trigger del evento decide por que rama aparece.
E["D01"]["trigger"] = {}; E["D01"]["next"] = ["D02"]
E["D02"]["trigger"] = {}; E["D02"]["next"] = ["D03"]
E["D03"]["trigger"] = {}; E["D03"]["next"] = ["ROOT_1"]
E["D06"]["trigger"] = {"any": [{"route_attack": True}, {"route_negotiate": True}]}
E["D06"]["next"] = ["ATK_SCOPE", "NEG_KEATING"]
E["D09"]["trigger"] = {"route_trunk": True}; E["D09"]["next"] = ["D10"]
E["D10"]["trigger"] = {"route_trunk": True}; E["D10"]["next"] = ["D11"]
E["D11"]["trigger"] = {"route_trunk": True}; E["D11"]["next"] = ["TRK_SPEECH"]
E["D11"]["cards"]["B"]["flag"]["far_line"] = True
E["D13"]["trigger"] = {"route_trunk": True}
E["D13"]["next"] = ["D14"]
E["D14"]["trigger"] = {"any": [{"route_attack": True}, {"route_trunk": True}]}
E["D14"]["next"] = ["D15"]
E["D15"]["trigger"] = {"any": [{"route_attack": True}, {"route_trunk": True}]}
E["D15"]["next"] = ["ATK_BERLIN", "ATK_LANDING", "TRK_SHIP"]
E["D17"]["trigger"] = {"route_trunk": True}; E["D17"]["next"] = ["TRK_U2"]
E["D23"]["trigger"] = {"soviet_withdrawal": True}; E["D23"]["next"] = ["TRK_FALSE_ALARM"]

# Rama oculta (E02). S01 aparece solo si NEG_TIME A activo secret_route.
E["S01"]["trigger"] = {"secret_route": True}
E["S01"]["next"] = ["S02", "ENDING"]
E["S01"]["cards"]["A"]["flag"] = {"soviet_access_dc": True}
E["S01"]["cards"]["B"]["flag"] = end("E08a")
E["S02"]["trigger"] = {"soviet_access_dc": True}
E["S02"]["next"] = ["ENDING"]
E["S02"]["cards"]["A"]["flag"] = end("E02", coalition_legalized=True)
E["S02"]["cards"]["B"]["flag"] = end("E08a")

# ---------------------------------------------------------------- raiz (dos cartas binarias)
E["ROOT_1"] = ev("OCT 17, 1962", {},
    card("STRIKE BEFORE THEY'RE READY", "Act while the sites are unfinished.", "squadron",
         "The Joint Chiefs are told to plan for the earliest possible date.",
         {"route_attack": True, "ATTACK": True}),
    card("GIVE THEM AN EXIT", "Pressure first. Force held in reserve.", "hourglass",
         "Nobody in the room says 'blockade' yet. Everybody is thinking it.",
         {"route_pressure": True, "PRESSURE": True}),
    ["D06", "ROOT_2"], "mcnamara",
    "Two camps in this room, Mr. President. Hit the sites now, before they're ready, and accept we won't get all of them. Or squeeze them first and keep the planes for later. Whichever you pick, the other one stops being a plan.",
    "Decision",
    "Reemplaza D04 y D07. El ataque domino la discusion del 16 y 17/10 y la Fuerza Aerea no garantizo destruir todos los misiles (Allison, cap. 4). Kennedy eligio el 20/10; aca se adelanta.",
    document="TACTICAL AIR COMMAND ESTIMATE: SURGICAL STRIKE EFFECTIVENESS NOT GUARANTEED.")

E["ROOT_2"] = ev("OCT 18, 1962", {"route_pressure": True},
    card("QUARANTINE", "Ships, a speech, and the whole world watching.", "destroyer",
         "Navy staff start writing the rules for stopping a Soviet ship.",
         {"route_trunk": True, "blockade_ready": True}),
    card("TALK FIRST", "Quietly. Before anyone knows there's a crisis.", "envelope",
         "The photographs go back in the drawer. On the public schedule, only Gromyko's visit.",
         {"route_negotiate": True}),
    ["D09", "D06"], "rusk",
    "Stevenson sent you a memo last night. Before any blockade, he says, go to Khrushchev privately and put every base on the table, Turkey included. Gromyko is here at five. The Navy says it can have a quarantine ready in four days.",
    "Office",
    "El memo de Stevenson del 17/10 existio (Turquia incluida; el 20/10 sumo Guantanamo). Kennedy lo descarto. La cuarentena se eligio el 20/10; aca se adelanta dos dias.",
    document="MEMORANDUM, A. E. STEVENSON TO THE PRESIDENT, 17 OCT 62.")

# ---------------------------------------------------------------- rama ataque
d08 = old["D08"]
E["ATK_SCOPE"] = ev("OCT 19, 1962", {"route_attack": True},
    card(d08["cards"]["A"]["title"], d08["cards"]["A"]["hint"], d08["cards"]["A"]["icon"],
         d08["cards"]["A"]["aftermath"], {"air_strike_ready": True, "limited_strike": True, "strike_launched": True}),
    card(d08["cards"]["B"]["title"], d08["cards"]["B"]["hint"], d08["cards"]["B"]["icon"],
         d08["cards"]["B"]["aftermath"], {"air_strike_ready": True, "invasion_ready": True, "strike_launched": True}),
    ["D14"], "taylor",
    "If we go, we decide now how far. Hit only the missile sites and their fighters and SAMs stay up. Take those too and we are one step from invading. The Chiefs prefer the whole package.",
    "Decision",
    "Adaptada de D08. MISSILES ONLY lleva a ATK_BERLIN, THE WHOLE PACKAGE a ATK_LANDING. OPLAN 312 y 316 existieron.",
    document="JCS OPLAN 312 (AIR STRIKE) / OPLAN 316 (INVASION). COPY 4 OF 12.")

E["ATK_BERLIN"] = ev("OCT 24, 1962", {"route_attack": True, "limited_strike": True},
    card("LET BERLIN WAIT", "Keep the war in the Caribbean.", "hourglass",
         "West Berlin goes on rations. The allies ask who decided that.",
         end("E09a", berlin_conceded=True)),
    card("FORCE THE CORRIDOR", "Send a convoy and see who stops it.", "helmet",
         "British and French companies join the column at Helmstedt. Nobody expects them to be enough.",
         {"berlin_convoy": True}, trigger={"allies_briefed": True}, els={"berlin_convoy": True, "convoy_alone": True},
         failed="The column leaves Helmstedt under one flag. London and Paris were not asked."),
    ["ATK_TACTICAL"], "rusk",
    "Thirty hours after the strike, Soviet troops closed the autobahn to West Berlin. Checkpoint Charlie is shut. Moscow's note is one sentence long: a base for a base.",
    "Crisis",
    "Contrafactico. Berlin era el gran temor de Kennedy en el ExComm. LIVE OAK, el estado mayor aliado para contingencias en Berlin, existio. Jruschov no movio nada en Berlin durante la crisis. La 'falla' de la carta B no es una falla: solo cambia el aftermath si no informaste a los aliados (D06).",
    document="LIVE OAK CONTINGENCY PLANNING: BERLIN GROUND ACCESS.")

E["ATK_TACTICAL"] = ev("OCT 26, 1962", {"berlin_convoy": True},
    card("GIVE HIM RELEASE", "Stop them at the border. Whatever it takes.", "missile",
         "The authority goes out by cable to Norstad's headquarters outside Paris.",
         end("E01b", nato_release=True)),
    card("NO NUCLEAR RELEASE", "Fight it with what's on the ground.", "stop_hand",
         "Norstad acknowledges. He does not sound surprised. He does not sound relieved.",
         end("E03b")),
    ["ENDING"], "nato",
    "SACEUR to the President. Soviet armor is moving on the autobahn in strength. If my forward units are overrun, I need release authority for tactical nuclear weapons. Now, not when it happens.",
    "Crisis_alert",
    "Contrafactico. El pedido nunca existio; el dilema si: los planes de la OTAN contaban con armas nucleares tacticas temprano y solo el presidente podia liberarlas. Norstad era el comandante supremo aliado.",
    crisis={"timer": 60, "on_timeout": {"if": {"defcon2": True}, "then": "A", "else": "B"},
            "timer_override": {"if": {"defcon2": True}, "seconds": 30},
            "at_zero": "No reply. At DEFCON 2, standing procedures fill the silence."})

E["ATK_LANDING"] = ev("OCT 26, 1962", {"route_attack": True, "invasion_ready": True},
    card("STOP THE BOMBING", "Take the deal before anyone counts the dead.", "handshake",
         "The last sorties are recalled. The Pentagon starts counting anyway.",
         end("E04b", bombing_halted=True, soviet_withdrawal=True)),
    card("LAND", "Finish the job. No missiles, no Castro.", "helmet",
         "The fleet leaves Florida in the dark. The beaches have code names now.",
         {"invasion_launched": True, "strike_launched": True}),
    ["ATK_PREAUTH"], "taylor",
    "Three days of strikes, Mr. President. Through U Thant, Moscow offers to crate the missiles if the bombing stops. The Chiefs say finish it. The fleet is loaded and the beaches are marked. D-day is Monday.",
    "Decision",
    "Contrafactico. OPLAN 316 y la fuerza de invasion fueron reales (DEF-04). U Thant ofrecio mediar desde el 24/10.",
    document="JCS OPLAN 316. LANDING ZONES, NORTH COAST. D-DAY: 29 OCT 62.")

E["ATK_PREAUTH"] = ev("OCT 29, 1962", {"invasion_launched": True},
    card("PRE-AUTHORIZE", "If they fire, we fire. No delay.", "crosshair",
         "The authority goes down the chain of command. It will not come back up.",
         end("E01a", predelegated=True)),
    card("ONLY ON MY ORDER", "Every nuclear shot goes through you.", "stop_hand",
         "The Chiefs take it in silence. On the beach, nobody knows what was decided.",
         end("E04a")),
    ["ENDING"], "mcnamara",
    "First wave is ashore. Recon reports short-range rockets near the beaches, and the analysts can't rule out nuclear warheads. The Chiefs want authority to answer in kind if they're used on our troops. Without coming back to you first.",
    "Crisis_alert",
    "Contrafactico. Los Luna y sus ojivas estaban en Cuba y Washington no lo supo hasta 1992 (INT-05). El 22/10 el Presidium estuvo cerca de delegar su uso y lo prohibio sin orden de Moscu (CAL-22).",
    document="JCS FLASH. REQUEST: PREDELEGATED RELEASE AUTHORITY, CUBA THEATER.")

# ---------------------------------------------------------------- tronco
E["TRK_SPEECH"] = ev("OCT 22, 1962", {"route_trunk": True},
    card("DEMAND WITHDRAWAL", "Clear. Popular. Hard to walk back.", "microphone",
         "At seven, the country hears the word 'withdrawal'. So does Moscow.",
         {"public_ultimatum": True}),
    card("DEMAND A FREEZE", "Room to bargain. Looks softer on TV.", "stop_hand",
         "At seven, the country hears the word 'halt'. By morning, the Republicans have a better word for it.",
         end("E10a", freeze_offer=True)),
    ["D13"], "rfk",
    "Seven o'clock tonight, every network. The draft demands the missiles come out, full stop. Or you ask for a halt to the work, checked by the UN, and keep the harder words for later.",
    "Office",
    "Adaptada de D12. Discurso del 22/10 a las 19 h; el texto real exigio el retiro. Pedir solo congelar es salida temprana a E10a: en septiembre ya habia dicho que no se toleraria.",
    document="ADDRESS TO THE NATION, DRAFT NO. 6. HANDWRITTEN CORRECTIONS.")

E["TRK_SHIP"] = ev("OCT 24, 1962", {"route_trunk": True},
    card("ENFORCE THE LINE", "Stop the ships. Board if you have to.", "destroyer",
         "Rusk, quietly: 'We're eyeball to eyeball.' Nobody knows yet who will blink.",
         {"blockade": True, "ship_stopped": True}),
    card("ACCEPT U THANT'S PAUSE", "Two weeks of quiet. For everyone.", "hourglass",
         "The destroyers pull back. In Cuba, the work on the sites does not stop for a single night.",
         end("E08b", quarantine_suspended=True)),
    ["TRK_SUBMARINE"], "navy",
    "Soviet ships approaching the line, a submarine shadowing them. And a cable from U Thant: suspend the quarantine for two weeks, Moscow suspends its shipments, everybody talks. Destroyers request instructions.",
    "Crisis",
    "Adaptada de C02. El pedido de U Thant del 24/10 existio (STA-09) y Kennedy no suspendio la cuarentena. Los barcos con misiles ya habian dado la vuelta el 23/10 (DEF-02).",
    crisis={"timer": 75, "on_timeout": "A", "at_zero": "The Navy applies standing orders. It enforces the line."})

E["TRK_SUBMARINE"] = ev("OCT 26, 1962", {"route_trunk": True},
    card("SIGNAL HER UP", "Small charges. Down there, they won't sound small.", "destroyer",
         "After hours of it, she surfaces among the destroyers. Her crew looks like they've been in hell.",
         {"near_miss": True, "near_miss_sub": True},
         trigger={"not": {"total_blockade": True, "far_line": True}},
         els=end("E01c"),
         failed="The charges fall. At that depth, nobody can tell a signal from an attack."),
    card("TRACK AND WAIT", "Stay close. Don't touch.", "eye",
         "The destroyers circle her for hours. In the end, her batteries decide for her.",
         {"sub_tracked": True}),
    ["D17"], "navy",
    "Soviet submarine near the line. She won't come up. The destroyers request permission to drop practice depth charges as a signal to surface. Moscow was told about the procedure. We don't know if she was.",
    "Crisis",
    "B-59 emergio la noche del 27/10 (DEF-06); aca se adelanta un dia. La salida nuclear existe solo con cuarentena total (D10 B) y linea lejana (D11 B).",
    crisis={"timer": 60, "on_timeout": "A", "at_zero": "No order comes. The Navy follows the procedure it sent to Moscow."},
    kind="incident")

E["TRK_U2"] = ev("OCT 27, 1962", {"route_trunk": True},
    card("HOLD AND VERIFY", "Find out who fired, and why.", "eye",
         "The strike is held. The pilot was Major Rudolf Anderson.",
         {"shootdown_absorbed": True}, trigger={"not": {"auto_retaliation": True, "defcon2": True}},
         els=end("E03a", sam_strike=True, order_failed=True),
         failed="The hold order arrives late. Under the standing rule, the first aircraft have already fired."),
    card("EXECUTE RETALIATION", "Hit the site. Answer fire with fire.", "crosshair",
         "Four aircraft cross into Cuban airspace. In Moscow, it is already night.",
         end("E03a", sam_strike=True)),
    ["TRK_MAULTSBY"], "air_force",
    "A U-2 is down over Cuba. The pilot is dead. The retaliation strike on the SAM site is ready.",
    "Crisis",
    "Adaptada de C03. El mayor Rudolf Anderson murio el 27/10. Kennedy no ejecuto la represalia acordada. Regla de dos rutinas, como el umbral nuclear de v0.2: con represalia automatica (D14 A) y DEFCON 2 (D15 A) a la vez, esperar falla. Con una sola, la orden de frenar llega a tiempo.",
    crisis={"timer": 60, "on_timeout": {"if": {"auto_retaliation": True}, "then": "B", "else": "A"},
            "timer_override": {"if": {"auto_retaliation": True}, "seconds": 35},
            "at_zero": "Retaliation proceeds if it was pre-authorized. Otherwise, it waits."},
    kind="incident")

E["TRK_MAULTSBY"] = ev("OCT 27, 1962", {"route_trunk": True},
    card("SEND THE ESCORT", "Bring him home. Armed as they are.", "squadron",
         "The F-102s find him gliding over the Bering Sea, engine dead. He lands on the ice at Kotzebue.",
         {"near_miss": True, "near_miss_maultsby": True}, trigger={"defcon2": False},
         els=end("E03c"),
         failed="The MiGs and the F-102s find each other first."),
    card("TELL MOSCOW IT'S A MISTAKE", "Explain it before they decide what it means.", "telephone",
         "A message goes to Moscow through the embassy. It will take hours. The pilot glides home alone.",
         {"maultsby_explained": True}),
    ["TRK_TURKEY"], "air_force",
    "One of our U-2s on an air-sampling run near the Pole is lost. The pilot navigated by the stars and got it wrong. He's over Soviet territory, Chukotka. MiGs are up. Alaska wants to launch F-102s to bring him home. Their missiles are nuclear.",
    "Crisis",
    "Hechos confirmados (DEF-09). Los F-102 despegaron por procedimiento, sin consultar al presidente: por eso el timeout los lanza. Con DEFCON 2 (D15 A), la escolta termina en combate.",
    crisis={"timer": 45, "on_timeout": "A", "at_zero": "Alaskan Air Command launches under standing orders. Nobody asked you."},
    kind="incident")

E["TRK_TURKEY"] = ev("OCT 27, 1962", {"route_trunk": True},
    card("MAKE THE SECRET PROMISE", "Deniable. Binding. Never public.", "padlock",
         "Robert Kennedy leaves for the Justice Department. Nothing is written down.",
         {"turkey_secret": True},
         available_if={"private_channel": True}, locked_text="No one can carry it to Dobrynin tonight."),
    card("ACCEPT IN PUBLIC", "End it now. Pay with the alliance.", "handshake",
         "In Ankara, the government asks why it heard it on the radio.",
         end("E07a", turkey_public=True)),
    ["TRK_VERIFY"], "rfk",
    "Jack, Radio Moscow wants the Jupiters out of Turkey, in public, and the crisis ends today. Dobrynin sees me tonight. I can give him the Jupiters in private instead, on one condition: they never say it was part of the deal.",
    "Office",
    "Une D18 y D19. La segunda carta se transmitio el 27/10 a la manana; el encuentro RFK-Dobrynin fue esa noche. Sin canal (D13 A), la promesa secreta queda bloqueada.",
    document="FBIS TRANSCRIPT: RADIO MOSCOW, 27 OCT 62, 10:00 EST.")

old22 = old["D22"]["cards"]
E["TRK_VERIFY"] = ev("OCT 28, 1962", {"route_trunk": True},
    card(old22["A"]["title"], old22["A"]["hint"], old22["A"]["icon"], old22["A"]["aftermath"],
         {"soviet_withdrawal": True}, trigger={"non_invasion": True},
         els=end("E09b"), failed=old22["A"]["aftermath_if_failed"]),
    card(old22["B"]["title"], old22["B"]["hint"], old22["B"]["icon"], old22["B"]["aftermath"],
         {"soviet_withdrawal": True, "forces_ready": True}, trigger={"non_invasion": True},
         els=end("E09b"), failed=old22["B"]["aftermath_if_failed"]),
    ["D23"], "bundy",
    "Radio Moscow again. Khrushchev says the work will stop and the missiles will be crated and shipped home. Now we decide how we check. Surveillance and inspectors, or full access right now.",
    "Decision",
    "Adaptada de D22. Sin promesa de no invasion (D17 B), Moscu se traba y cobra en Berlin (E09b). FULL ACCESS NOW mantiene las fuerzas en alerta (forces_ready), que pesa en la falsa alarma.",
    document="FBIS TRANSCRIPT: RADIO MOSCOW, 28 OCT 62, 09:00 EST.")

ALARM_DOOM = {"forces_ready": True, "any": [{"auto_retaliation": True}, {"defcon2": True}]}
E["TRK_FALSE_ALARM"] = ev("OCT 28, 1962", {"route_trunk": True},
    card("VERIFY FIRST", "Wait for a detonation that may never come.", "eye",
         "Nothing hits Tampa. Later, someone at Moorestown finds a test tape running in the machine.",
         end("E06a", alarm_verified=True)),
    card("ALERT THE BOMBERS", "If it's real, every minute counts.", "missile",
         "The bombers go to their engines. Then the news from Tampa: nothing. They stand down. Moscow saw all of it.",
         end("E06b", alarm_overreaction=True), trigger={"not": ALARM_DOOM},
         els=end("E01d"),
         failed="The alert meets a force already leaning forward. Nobody waits for Tampa."),
    ["ENDING"], "norad",
    "NORAD to the White House. The Moorestown radar reports a missile launched from Cuba. Projected impact: Tampa. Minutes, not hours. No detonation reported yet.",
    "Crisis_alert",
    "Hecho confirmado: el 28/10 una cinta de prueba en Moorestown produjo la alarma (DEF-12). Lo contrafactico es que llegue al presidente.",
    crisis={"timer": 40, "on_timeout": {"if": ALARM_DOOM, "then": "B", "else": "A"},
            "timer_override": {"if": {"forces_ready": True}, "seconds": 20},
            "at_zero": "Standing procedures take over."},
    kind="incident")

# ---------------------------------------------------------------- rama negociacion
E["NEG_KEATING"] = ev("OCT 18, 1962", {"route_negotiate": True},
    card("DENY IT", "No evidence of offensive weapons. Officially.", "microphone",
         "The statement is read at noon. Keating says he can wait.",
         {"lied_to_senate": True}, trigger={"broad_consultation": False},
         els=end("E10b", lied_to_senate=True),
         failed="By evening Keating has a photograph. Someone who sat in the Cabinet Room gave it to him."),
    card("BRIEF THE LEADERS", "Tell Congress in secret. More people will know.", "people",
         "The congressional leaders sit in the Cabinet Room. Two of them take notes.",
         {"congress_briefed": True}),
    ["NEG_WHO"], "counsel",
    "Senator Keating is on the Senate floor again. Last week he said 'rocket bases'. Today he has locations. The press office needs a line before noon, and Gromyko is due at five.",
    "Office",
    "Confirmado: Keating denuncio tropas el 31/08 y bases de 'cohetes' el 10/10. Que vuelva el 18/10 con ubicaciones es contrafactico. Kennedy reunio a los lideres del Congreso el 22/10.",
    document="CONGRESSIONAL RECORD, SENATE, 10 OCT 62. REMARKS OF MR. KEATING (EXCERPT).",
    kind="incident")

E["NEG_WHO"] = ev("OCT 18, 1962", {"route_negotiate": True},
    card("SHOW GROMYKO THE PHOTOS", "Make Moscow answer to you, in private.", "papers",
         "Gromyko looks at the photographs for a long time. Then he asks for a telephone.",
         {"moscow_channel": True}),
    card("GO THROUGH HAVANA", "Talk to the island, not the empire.", "envelope",
         "A message is drafted for the Brazilian ambassador in Havana.",
         {"castro_channel": True}),
    ["NEG_TIME", "NEG_CASTRO"], "rusk",
    "Gromyko will sit in that chair at five and tell you the weapons are defensive. You can let him, or you can open the drawer. Or we leave Moscow out and go through the Brazilians. Castro is the one who has to live next to those missiles.",
    "Office",
    "Gromyko visito a Kennedy el 18/10 y nego todo; Kennedy no mostro las fotos (CAL-18). El canal brasileno se aprobo recien el 26/10 y nunca se uso (STA-08).")

SECRET = {"broad_consultation": True, "congress_briefed": True, "public_ultimatum": False}
E["NEG_TIME"] = ev("OCT 20, 1962", {"moscow_channel": True},
    card("WAIT FOR NOVEMBER", "Quiet now. Missiles later.", "hourglass",
         "The last week of November is cleared on the calendar. Nothing else is decided.",
         {"waited": True, "secret_route": True}, trigger=SECRET,
         els=end("E08a", waited=True)),
    card("SET A DEADLINE", "Seven days, privately. Then you go public.", "stop_hand",
         "Robert Kennedy delivers the deadline to Dobrynin in person. Nothing is written down.",
         {"private_deadline": True}),
    ["S01", "NEG_LEAK"], "rusk",
    "Moscow's answer, through Dobrynin. Khrushchev no longer denies it. He'll discuss everything when he comes to New York for the UN, late November. Until then he asks for quiet. By late November, every site will be operational.",
    "Office",
    "Confirmado: el 16/10 Jruschov le confirmo a Kohler que iria a Nueva York a fines de noviembre (FRUS 1961-63, vol. V, doc. 248). Que pensara revelar ahi los misiles es interpretacion. La carta A usa trigger/else al reves: el 'exito' es la rama oculta S01; el 'else' es el final E08a, sin aftermath_if_failed para que se vea el mismo texto.",
    document="AMEMBASSY MOSCOW, 16 OCT 62: CHAIRMAN CONFIRMED INTENTION TO COME TO NEW YORK LATTER PART OF NOVEMBER.")

E["NEG_LEAK"] = ev("OCT 21, 1962", {"private_deadline": True},
    card("ASK THEM TO HOLD", "One phone call. A promise in return.", "telephone",
         "Dryfoos agrees. Reston asks for one thing in return: no blood and no war while the Times stays quiet.",
         end("E06c", press_held=True, turkey_secret=True, non_invasion=True, soviet_withdrawal=True),
         available_if={"broad_consultation": False, "congress_briefed": False},
         locked_text="Too many people know. Someone else will print it."),
    card("GO PUBLIC", "Tell the country before the paper does.", "microphone",
         "The networks clear seven o'clock. Moscow listens, then makes its offer on the radio.",
         end("E07b", went_public=True, turkey_public=True, soviet_withdrawal=True)),
    ["ENDING"], "bundy",
    "Reston at the Times has it. Not all of it. Enough. Dryfoos, the publisher, is holding the front page for your call. If it runs tomorrow, your seven days are over, and so is everything said in private.",
    "Office",
    "Confirmado: Kennedy convencio a Reston y Dryfoos de no publicar y Reston pidio la promesa de no sangre ni guerra (archivo Reston, UIUC). Fecha 21/10 segun Stern (CAL-21).",
    kind="incident")

E["NEG_CASTRO"] = ev("OCT 20, 1962", {"castro_channel": True},
    card("ALL OF IT, MONGOOSE TOO", "Recognize him. Call off the CIA.", "handshake",
         "A cable goes to Rio. Lansdale is told to stand down his teams. Nobody in Moscow is copied.",
         end("E05", cuba_neutral_offer=True, non_invasion=True, mongoose_stopped=True)),
    card("THE GUARANTEE, ON PAPER", "Promise him peace. Keep the teams running.", "padlock",
         "The cable promises no invasion. In Pinar del Rio, a CIA team is still waiting for its signal.",
         end("E10c", non_invasion=True, mongoose_kept=True)),
    ["ENDING"], "rusk",
    "Through the Brazilians, Castro answers. He will send the Soviet weapons home himself if Washington guarantees no invasion and recognizes Cuba as sovereign. And he wants the sabotage to stop. He means Mongoose.",
    "Office",
    "Adaptada de D21. Especulacion: el mensaje via Brasil se aprobo el 26/10 y nunca se entrego; Castro nunca ofrecio expulsar las armas (CIA-04, STA-08). Mongoose existio (CIA-03).",
    document="CABLE, AMEMBASSY RIO DE JANEIRO. EYES ONLY THE SECRETARY.")

# ---------------------------------------------------------------- incidente en rama ataque? no: ruteo final
json.dump(E, open(out, "w"), ensure_ascii=False, indent=1)
print(len(E), "eventos")
