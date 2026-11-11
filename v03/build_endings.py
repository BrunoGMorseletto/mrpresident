"""Arma endings_v03.json: 10 familias, 23 variantes, en el formato de endings.json del repo.

Cada variante es una entrada completa (el motor la muestra tal cual). Campos nuevos:
- family: el final original (E01..E10). Logros, galeria y mini documental cuentan familias.
- variant_label: subtitulo del badge.
- sealed_by: lista de {if, text}. Se muestra la primera que se cumple, despues del recap.
  Nombra la decision que te condeno. Requiere unas lineas en label ENDING (ver LEEME).
Condicion: flag end_<variante>, que pone la ultima carta de la partida.
"""
import json, sys

old = {e["id"]: e for e in json.load(open(sys.argv[1]))}
out = sys.argv[2]

# Parte compartida: parrafos historicos de cada familia (los que no narran la partida).
SHARED = {
    "E01": old["E01"]["body"][1:],
    "E03": old["E03"]["body"][1:],
    "E04": [old["E04"]["body"][1]],
    "E05": old["E05"]["body"][1:],
    "E06": [
        "In the real October, Khrushchev announced on Radio Moscow on the 28th that the missiles would be dismantled and shipped home. In public, the United States promised not to invade Cuba. In private, Robert Kennedy had told Ambassador Dobrynin that the Jupiters in Turkey would be gone within months, on one condition: it could never be presented as part of the deal. The secret held for more than twenty years.",
        old["E06"]["body"][2],
    ],
    "E07": old["E07"]["body"][1:],
    "E08": old["E08"]["body"][1:],
    "E09": old["E09"]["body"][1:],
    "E10": [old["E10"]["body"][1]],
}

V = []
def variant(vid, label, tagline, how, recap, closing=None, sealed=None, recap_skip=None, **over):
    fam = vid[:3]
    base = old[fam]
    body = ([how] if how else []) + SHARED.get(fam, []) + ([closing] if closing else [])
    e = {
        "id": vid, "family": fam, "title": base["title"], "badge": base["badge"],
        "variant_label": label, "header": base["header"], "tagline": tagline,
        "body": body, "recap_template": recap,
        "condition": {"flags": {"end_" + vid: True}, "stats": {}},
        "icon": base["icon"], "recap_skip": recap_skip if recap_skip is not None else base.get("recap_skip", []),
        "background": base["background"],
    }
    if "stamp" in base:
        e["stamp"] = base["stamp"]
    if sealed:
        e["sealed_by"] = sealed
    e.update(over)
    V.append(e)

# ------------------------------------------------------------------ E01 LAST TRANSMISSION
variant("E01a", "Deliberate",
    "The invasion went ashore. So did the authority to answer.",
    "American troops were on the beaches when the first short-range rocket was fired at them. The authority you had delegated did exactly what it was built to do: nobody called Washington, because nobody had to. The answer was nuclear, and so was the answer to the answer. Within hours, the war was no longer about Cuba.",
    "You chose the strike, then the invasion, then handed the decision to fire to the men on the ground.",
    recap_skip=["invasion_ready", "strike_launched"])
variant("E01b", "Berlin",
    "It started in the Caribbean. It ended in Europe.",
    "The convoy on the autobahn was met by Soviet armor, and Norstad's forward units were overrun within a day. He used the authority you gave him. Tactical weapons fell on East German roads, and Moscow answered against NATO bases. Nobody in Washington or Moscow had decided to end the world over Berlin. Each side had only decided not to lose there.",
    "You struck Cuba, forced the road to Berlin, and released nuclear weapons to a general in Paris.")
variant("E01c", "Accident at sea",
    "Nobody ordered it. Nobody could stop it.",
    "The practice depth charges were meant as a signal. Sixty meters down, in a submarine that had lost contact with Moscow days earlier, they sounded like an attack. The captain prepared the torpedo he was not supposed to use without orders. This time no one in the control room talked him out of it. A destroyer disappeared, and the Navy reported a nuclear detonation in the Atlantic. Every routine on both sides did the rest.",
    "You closed the sea to everything, kept the line far out, and signalled a submarine you could not see.",
    sealed=[{"if": {"total_blockade": True, "far_line": True},
             "text": "On October 20 you made the quarantine total. On the 21st you kept the line at 800 miles. The destroyers reached her sooner, and harder."}])
variant("E01d", "False alarm",
    "The deal was done. The radar didn't know.",
    "Khrushchev had already said yes on the radio when Moorestown reported a missile headed for Tampa. It was a test tape. By the time anyone checked, a force that had been kept on maximum alert for days had already done what it was trained to do. Moscow saw the bombers move on the morning it had backed down, and could only read it one way.",
    "You won the crisis, kept every force leaning forward, and answered a radar before you answered the phone.",
    sealed=[{"if": {"forces_ready": True},
             "text": "On October 28 you kept the forces on full alert until the last missile left. Nobody took them off it before the radar spoke."}])

# ------------------------------------------------------------------ E02 (secreto, sin cambios)
e02 = dict(old["E02"])
e02.update({"family": "E02", "variant_label": "Secret",
            "condition": {"flags": {"end_E02": True}, "stats": {}},
            "recap_template": "You kept it quiet, let everyone in, and waited for November."})
V.append(e02)

# ------------------------------------------------------------------ E03 THE GUNS OF OCTOBER
variant("E03a", "Retaliation",
    "One plane. Then four. Then everyone.",
    "The SAM site that killed Major Anderson was destroyed within the hour. The Soviet officers who manned it had fired without Moscow's orders; the ones who died answering the strike had orders to defend themselves. Moscow could not let it pass, and neither could you. By Monday, the air war over Cuba was general, and the troops in Florida were boarding ships.",
    "You answered the U-2 shootdown with force, and nobody found the way back.",
    sealed=[{"if": {"order_failed": True},
             "text": "On October 23 you let the military retaliate without asking you. On the 24th you went to DEFCON 2. On the 27th, your order to hold arrived after the planes."}])
variant("E03b", "Berlin",
    "Nobody pressed the button. Everybody went to war anyway.",
    "You refused Norstad the weapons he asked for, and NATO fought on the ground with what it had. West Berlin fell in four days. The front stopped somewhere in West Germany, held by divisions that had trained for years to fight a war they were told would go nuclear in the first hour. It hadn't, yet.",
    "You struck Cuba, forced the road to Berlin, and kept the war conventional.")
variant("E03c", "Over Chukotka",
    "A lost pilot. Two air forces. No one in charge.",
    "Maultsby was still gliding home when the Soviet fighters and the F-102s found each other over the Bering Sea. With Strategic Air Command at DEFCON 2, the American pilots had orders that did not include waiting. Two MiGs went down off the Soviet coast. Moscow read it as the start of something larger, and answered in Cuba.",
    "You sent nuclear-armed fighters after a lost spy plane, with the whole Air Force one step from war.",
    sealed=[{"if": {"defcon2": True},
             "text": "On October 24 you raised the alert to DEFCON 2. Three days later, it was the alert that decided what the escort did."}])

# ------------------------------------------------------------------ E04 VICTORY AT ANY PRICE
variant("E04a", "Invasion",
    "The missiles are gone. So is everything that stood in the way.",
    old["E04"]["body"][0],
    "You prepared the invasion, launched it, and kept the nuclear decision for yourself.",
    closing=old["E04"]["body"][2],
    recap_skip=["invasion_ready", "strike_launched"])
variant("E04b", "Bombing halt",
    "The missiles left under fire. The dead stayed.",
    "Three days of strikes destroyed most of the sites and killed several hundred Soviet soldiers and technicians, along with Cuban gunners and civilians near the bases. Then you stopped, and Moscow took the deal it had been offered. The missiles left on Soviet ships under American escort. In the Kremlin, the men who had opposed Khrushchev's gamble began counting their own dead, and his days.",
    "You bombed for three days, then stopped when Moscow offered to pull out.",
    closing="The invasion force never landed. That is the only reason the weapons waiting for it were never used.")

# ------------------------------------------------------------------ E05 CUBA DECIDES
variant("E05", "Speculative",
    old["E05"]["tagline"], old["E05"]["body"][0],
    "You talked to Havana instead of Moscow, promised not to invade, and called off the CIA.")

# ------------------------------------------------------------------ E06 THIRTEEN DAYS
variant("E06a", "Historical outcome",
    old["E06"]["tagline"],
    "You kept the quarantine, gave Moscow a way out it could accept, and paid for it with a promise that could never be public. When the radar said Tampa on the last morning, you waited. Nothing came.",
    "You imposed a quarantine, promised not to invade, made a secret promise about Turkey, and waited when the radar said Tampa.",
    recap_skip=["blockade", "turkey_secret", "non_invasion"])
variant("E06b", "Historical outcome · Too close",
    "The crisis ended. You'll never know how close it was.",
    "You kept the quarantine and made the promise about Turkey in private. Then, on the morning Khrushchev said yes, a radar said Tampa and you put the bombers on their engines. They stood down a few minutes later. In Moscow, someone watched the alert go up and asked whether the radio broadcast had been heard at all.",
    "You reached the historical deal, then answered a false alarm with the bombers.",
    recap_skip=["blockade", "turkey_secret", "non_invasion"])
variant("E06c", "Never public",
    "The crisis ended before it began. Nobody counted the days.",
    "There was no speech, no quarantine and no line at sea. Khrushchev took the deadline seriously, and the missiles began coming down before most Americans knew they had been there. The Times kept its word, and so did you: no blood, no war. The Jupiters left Turkey the next spring, for reasons nobody in Washington would discuss.",
    "You talked to Moscow in private, set a deadline, and convinced the Times to wait.",
    closing="Without the fright of October, nobody needed a hotline in 1963 or a test ban that summer. In this timeline, both took longer. A crisis nobody saw taught nobody anything.",
    header="OCTOBER 1962 · ALTERNATE OUTCOME", badge="Secret deal")

# ------------------------------------------------------------------ E07 MISSILES FOR MISSILES
variant("E07a", "In the crisis",
    old["E07"]["tagline"], old["E07"]["body"][0],
    "You accepted Khrushchev's public offer and ended the crisis on the radio.",
    sealed=[{"if": {"private_channel": False},
             "text": "On October 22 you kept everything on the record. On the 27th, there was nobody who could carry a secret to Dobrynin."}])
variant("E07b", "Before the crisis",
    "The crisis lasted a week. The trade will last longer.",
    "You went on television before the Times could print it, with no quarantine ready and nothing to bargain with but the truth. Khrushchev made his offer on the radio the next morning: his missiles out of Cuba, yours out of Turkey. You took it. The world never got close to the edge. The allies spent the next year asking what else Washington would trade if someone asked in public.",
    "You negotiated in secret, then went public before the paper did.")

# ------------------------------------------------------------------ E08 THE NEW NORMAL
variant("E08a", "Waiting for November",
    "Khrushchev came to New York. The missiles were already ready.",
    "You gave him the quiet he asked for. In late November Khrushchev arrived at the United Nations, every site in Cuba operational, and offered to talk about everything except the missiles. The elections were over. So was the moment when removing them would have been simple. Within a year, Americans had learned to live with Soviet missiles ninety miles away, the way they already lived with the ones in Siberia.",
    "You let Khrushchev set the calendar, and waited for a conversation that came too late.")
variant("E08b", "The pause",
    old["E08"]["tagline"],
    "You accepted U Thant's pause. The ships stopped, the destroyers pulled back, and the talks began. The work on the sites never stopped. Two weeks became four, and the quarantine you had announced on television was never reimposed. Nobody could say for certain what was still in Cuba. Within a year, the country had stopped asking.",
    "You declared a quarantine, then suspended it before anything was settled.")

# ------------------------------------------------------------------ E09 CHECKMATE IN BERLIN
variant("E09a", "After the strike",
    "You hit Cuba. They collected in Berlin.",
    "Your strike destroyed most of the missiles in Cuba. Khrushchev answered where Kennedy had always feared he would: the roads to West Berlin closed, and you chose not to force them. The city lived on an airlift and then on concessions, one at a time. Cuba became an American victory. Berlin became the price nobody in Washington would name.",
    "You struck the missile sites, and when Moscow closed the road to Berlin, you let it stay closed.")
variant("E09b", "Stalled deal",
    "The crisis ended in Cuba. It was never about Cuba.",
    old["E09"]["body"][0],
    "You won the confrontation at sea, but never promised what Moscow needed to say it had won something.",
    sealed=[{"if": {"non_invasion": False},
             "text": "On October 26 Khrushchev asked for one thing: a promise not to invade Cuba. You gave him none. On the 28th, that was the detail he stalled on."}])

# ------------------------------------------------------------------ E10 CRUCIFIED BY CUBA
variant("E10a", "The freeze",
    old["E10"]["tagline"],
    "You asked on television for a halt to the work, not for the missiles to leave. You had said in September that offensive weapons would not be tolerated, and now everyone could see they were. By Election Day the opposition had a single message, the cabinet was leaking against itself, and Congress stopped returning the White House's calls. Kennedy stayed in office. He no longer governed.",
    "You had drawn a line in September, then asked only for a freeze.",
    closing="In 1962 the promise was kept. Here, it wasn't.")
variant("E10b", "The lie",
    "It wasn't the missiles. It was what you said about them.",
    "Your press office told the country there was no evidence of offensive weapons in Cuba. That evening Senator Keating had a photograph, and the photograph came from someone inside your own circle. The negotiation with Moscow died the same night. A President caught lying to the Senate two weeks before an election does not get to negotiate anything, with anyone.",
    "You let too many people in, then denied in public what they all knew.",
    closing="The lie was the kind every administration told. This one had too many witnesses.",
    sealed=[{"if": {"broad_consultation": True},
             "text": "On October 16 you widened the room. Two days later, one of the people in it had a set of prints and a senator's phone number."}])
variant("E10c", "The double game",
    "Peace with Castro, by cable. War on Castro, by night.",
    "Castro accepted your guarantee. Three nights later his militia captured a CIA sabotage team near a copper mine in Pinar del Río, with Agency radios and explosives. He went on television with the prisoners and the text of your cable side by side. To the left you had lied to Castro; to the right you had negotiated with him. By Election Day, nobody in Congress defended either one.",
    "You negotiated with Havana and kept the sabotage running at the same time.",
    closing="Operation Mongoose was real, and in October 1962 its teams were still active. Negotiating with Castro, in secret or in public, was something no American President of the time could survive.")

json.dump(V, open(out, "w"), ensure_ascii=False, indent=1)
print(len(V), "variantes;", len({v["family"] for v in V}), "familias")
