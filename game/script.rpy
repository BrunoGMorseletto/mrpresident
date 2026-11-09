# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#define e = Character("Eileen")


image folder_image = VBox("gui/interactives/folder.png")
transform pos:
    yalign -1.5
    xalign 0.5
transform bg_size:
    xsize 1920
    ysize 1080
transform init_pos_despacho(flip=False):
    xzoom (-1.0 if flip else 1.0)
    zoom 0.55
    align (0.5, -0.26)
    alpha 0.0
    ease 0.5 alpha 1.0
transform init_pos_decision(flip=False):
    xzoom (-1.0 if flip else 1.0)
    zoom 0.25
    xpos 950
    ypos 135
    alpha 0.0
    ease 0.5 alpha 1.0
transform duel_left:
    # T08: adviser on the left, mirrored to face the other one (Bruno: adjust xpos)
    zoom 0.25
    #xanchor 0.5
    xpos 825        # both advisers sit left of center so the speech bubble (top right) does not cover them
    ypos 145        # bottom of the sprite on the far edge of the table, like the single-adviser scenes
    xzoom -1.0
    alpha 0.0
    ease 0.5 alpha 1.0
transform duel_right(flip=False):
    # flip=True for sprites that already look to the right (Rusk), so both advisers face each other
    xzoom (-1.0 if flip else 1.0)
    zoom 0.25
    #xanchor 0.5
    xpos 1100
    ypos 145
    alpha 0.0
    ease 0.5 alpha 1.0
transform init_pos_crisis(flip=False):
    xzoom (-1.0 if flip else 1.0)
    zoom 0.55
    align (0.5, -0.05)
    alpha 0.0
    ease 0.5 alpha 1.0
transform init_pos_ending:
    zoom 0.75
    align (0.5, -0.05)
    alpha 0.0
    ease 0.5 alpha 1.0
define sounds = ['audio/A1.ogg', 'audio/A2.ogg', 'audio/A3.ogg', 'audio/A4.ogg', 'audio/A5.ogg', 'audio/B1.ogg', 'audio/B2.ogg', 'audio/B3.ogg', 'audio/B4.ogg', 'audio/B5.ogg']

define cards_key = "cards" #dict key related to the cards info in events.json
define a_card_key = "A" #dict key related to the A card info in events.json
define b_card_key = "B" #dict key related to the A card info in events.json
default flags = {}
default persistent.last_reports = {}   # ending id -> last end-of-run report (T14)
default choices_made = []      # [(scene, "A"/"B")] in order, for the end-of-run report
default timed_out = []         # scenes where the timer ran out and the default order went ahead
default stats = {}
default chosen_ending = None
default current_scene = "D01"
default current_date = None
default persistent.endings_seen = set()

init python:
    import json
    events = {}
    endings = {}
    with renpy.file("data/events.json") as f:
        events = json.load(f)
    with renpy.file("data/state.json") as f:
        state = json.load(f)
    with renpy.file("data/endings.json") as f:
        endings = json.load(f)
    with renpy.file("data/day_transitions.json") as f:
        day_transitions = json.load(f)
    with renpy.file("data/newsreels.json") as f:
        newsreels = json.load(f)["newsreels"]
    with renpy.file("data/debrief.json") as f:
        debrief_data = json.load(f)
    import operator

    OPS = {
        "<=": operator.le,
        ">=": operator.ge,
        "==": operator.eq,
        "!=": operator.ne,
        "<":  operator.lt,
        ">":  operator.gt,
    }
    for e in endings:
        achievement.register("ending_" + e["id"].lower())
    achievement.register("all_endings", stat_max=len(endings), stat_modulo=1)
    def unlock_ending(ending_id):
        before = codex_unlocked_set()
        persistent.endings_seen.add(ending_id)
        achievement.grant("ending_" + ending_id.lower())
        achievement.progress("all_endings", len(persistent.endings_seen))
        renpy.save_persistent()
        codex_check_new(before)
    def get_value(name):
        if name in stats:
            return stats[name]
        return flags.get(name, False)

    def check_trigger(trigger):
        for key, cond in trigger.items():
            if key == "any":
                if not any(check_trigger(sub) for sub in cond):
                    return False
            elif key == "not":
                if check_trigger(cond):
                    return False
            elif isinstance(cond, bool):
                if bool(get_value(key)) != cond:
                    return False
            else:
                value = get_value(key)
                for op, n in cond.items():
                    if not OPS[op](value, n):
                        return False
        return True
    def condition_met(conditions):
        for ed_flag, boolean in conditions["flags"].items():
            if bool(flags.get(ed_flag, False)) != boolean:
                return False
        for ed_stat, stat_checks in conditions["stats"].items():
            for op, value in stat_checks.items():
                if not OPS[op](stats[ed_stat], value):
                    return False
        return True
    def decide_ending():
        # an ending wins if its main condition OR any of its "alt_conditions" is met
        for ending in endings:
            options = [ending["condition"]] + ending.get("alt_conditions", [])
            if any(condition_met(c) for c in options):
                return ending
        return endings[-1]
    def pick_variant(item):
        """First variant whose "if" is true (check_trigger syntax); the item itself if it has no variants."""
        if "variants" not in item:
            return item
        for v in item["variants"]:
            if check_trigger(v.get("if", {})):
                return v
        return item["variants"][-1]
    def ending_paragraphs(ending):
        """Ending body, with an opening paragraph that depends on how the player got there (intro_variants)."""
        # a body paragraph can be a string, or {"if": ..., "text": ...} shown only when its condition holds
        paras = [b["text"] if hasattr(b, "keys") else b for b in ending["body"]
        if not hasattr(b, "keys") or check_trigger(b.get("if", {}))]
        if ending.get("intro_variants"):
            intro = pick_variant({"variants": ending["intro_variants"]})
            if intro.get("text"):
                paras.insert(0, intro["text"])
        return paras
    def gallery_paragraphs(ending):
        """Body for the Endings menu (outside a run): conditional paragraphs marked "gallery": false are left out."""
        return [b["text"] if hasattr(b, "keys") else b for b in ending["body"]
                if not hasattr(b, "keys") or b.get("gallery", True)]
    def note_timeout():
        if current_scene not in timed_out:
            timed_out.append(current_scene)

    def build_debrief(ending):
        """Everything the end-of-run report shows, computed from this run."""
        d = {}
        # YOUR CRISIS
        skip = ending.get("recap_skip", [])
        frags = [f["text"] for f in debrief_data["recap_fragments"]
        if flags.get(f["flag"]) and f["flag"] not in skip]
        d["recap"] = ending.get("recap_template", "")
        d["fragments"] = frags[:3]
        # WHAT REALLY HAPPENED: where this run left the record (choices first, then things that never happened)
        diverged, never = [], []
        for scene, choice in choices_made:
            h = events[scene].get("in_1962")
            if not h:
                continue
            row = (scene, events[scene]["cards"][choice]["title"], h["text"])
            if h["choice"] == "none":
                never.append(row)
            elif h["choice"] in ("A", "B") and h["choice"] != choice:
                diverged.append(row)
        picked = (diverged + never)[:5]
        order = [sc for sc, _ in choices_made]
        picked.sort(key=lambda r: order.index(r[0]))
        d["history"] = picked
        d["followed"] = len(diverged) == 0 and len(never) == 0
        # THREE LENSES
        counts = {"rational": 0, "organizational": 0, "governmental": 0}
        for scene, choice in choices_made:
            m = events[scene].get("allison_model")
            if m in counts:
                counts[m] += 1
        d["lenses"] = counts
        # one card from this run for each lens, so the categories have a concrete example
        examples = {}
        for scene, choice in choices_made:
            m = events[scene].get("allison_model")
            if m in counts and m not in examples:
                examples[m] = events[scene]["cards"][choice]["title"]
        d["examples"] = examples
        top = max(counts.values())
        leaders = [k for k, v in counts.items() if v == top]
        d["dominant"] = leaders[0] if len(leaders) == 1 else None
        d["timeouts"] = len(timed_out)
        return d

    def show_last_report(eid):
        """Gallery: read again the last report written for this ending."""
        e = [x for x in endings if x["id"] == eid][0]
        renpy.call_in_new_context("show_last_report_label", e, persistent.last_reports[eid])

    def replay_ending(eid):
        """Gallery: watch an ending's newsreel and film again, in its main version."""
        renpy.call_in_new_context("replay_ending_label", eid)

    def find_newsreel(date):
        """First newsreel for that date whose "if" holds, or None (T06)."""
        for reel in newsreels:
            if reel["date"] == date and check_trigger(reel.get("if", {})):
                return reel
        return None
    def find_final_newsreel(ending_id):
        """Newsreel shown before the ending file: chosen by ending id, then by "if"."""
        for reel in newsreels:
            if reel["date"] == "FINAL" and ending_id in reel.get("endings", []) and check_trigger(reel.get("if", {})):
                return reel
        return None
    def newsreel_frames(reel):
        """Frames that apply to this run, with their variant merged in."""
        out = []
        for fr in reel["frames"]:
            if not check_trigger(fr.get("if", {})):
                continue
            base = dict((k, v) for k, v in fr.items() if k not in ("variants", "if"))
            if "variants" in fr:
                v = pick_variant(fr)
                base.update(dict((k, x) for k, x in v.items() if k != "if"))
            out.append(base)
        return out
    def check_nuclear():
        checks_passed = True
        conditions = endings[0]["condition"]
        active_flags=flags.keys()
        for ed_flag, boolean in conditions["flags"].items():
            if ed_flag not in active_flags:
                flags[ed_flag] = False
            if flags[ed_flag] != boolean:
                checks_passed = False
        for ed_stat, stat_checks in conditions["stats"].items():
            stat = stats[ed_stat]
            for op, value in stat_checks.items():
                if not OPS[op](stat, value):
                    checks_passed = False
        return checks_passed

    def next_event(possible_events, events):
        global chosen_ending, current_date
        if check_nuclear():
            chosen_ending = endings[0]
            return "ENDING"
        for name in possible_events:
            if name == "ENDING":
                chosen_ending = decide_ending()
                return "ENDING"
            if check_trigger(events[name]["trigger"]):
                new_date = events[name]["date"]
                if current_date and new_date and new_date != current_date:
                    
                    renpy.call_in_new_context("intermission", current_date)
                current_date = new_date or current_date
                codex_on_scene(name)
                # leaving the crisis room: back from the tension track to the office music
                if not events[name].get("crisis") and renpy.music.get_playing() == "audio/crisis.ogg":
                    renpy.music.play("audio/oval_office.ogg", fadeout=2.0, fadein=2.0)
                return name
        chosen_ending = decide_ending()
        return "ENDING"
    def change_stat(stat, value):
        stats[stat] += value
        if stats[stat] < state[stat]["min"]:
            stats[stat] =  state[stat]["min"]
        if stats[stat]> state[stat]["max"]:
            stats[stat] =  state[stat]["max"]
    def change_multiple_stats(stats_to_change):
        for stat,value in stats_to_change.items():
            change_stat(stat, value)
    def change_flag(flag, value):
        flags[flag] = value
    def change_multiple_flags(flags_to_change):
        for flag,value in flags_to_change.items():
            change_flag(flag, value)
    def nuclear_rule():
        if stats["escalation"] >= 7:
            triggers = (
                flags.get("auto_retaliation", False)
                + flags.get("defcon2", False)
                + (stats["control"] == 0)
            )
            if triggers >= 2:
                change_flag("nuclear_use", True)
            else:
                stats["escalation"] = 6
    def apply_choice(choice, current_scene):
        renpy.block_rollback()   # T27/T31: rolling back can re-read text, never undo a decision
        choices_made.append((current_scene, choice))
        card = events[current_scene][cards_key][choice]
        if check_trigger(card["trigger"]):
            effects = card
            aftermath = card["aftermath"]
        else:
            effects = card["else"]
            if card.get("aftermath_if_failed"):
                aftermath = card["aftermath_if_failed"]
            else:
                aftermath = card["aftermath"]          
        change_multiple_stats(effects["stats"])
        change_multiple_flags(effects["flag"])
        nuclear_rule()
        return aftermath
    _fit_cache = {}

    def fit_size(s, style, w, h, max_size, min_size=12):
        key = (s, style, w, h, max_size)
        if key in _fit_cache:
            return _fit_cache[key]
        size = max_size
        while size > min_size:
            d = Text(s, style=style, size=size, xsize=w)
            rw, rh = renpy.render(d, w, h, 0, 0).get_size()
            if rw <= w and rh <= h:
                break
            size -= 1
        _fit_cache[key] = size
        return size

    current_scene = ""
    renpy.music.register_channel("typing", mixer="sfx", loop=False)
    def play_click():
        renpy.sound.play(renpy.random.choice(sounds), channel="typing")

    def type_sound(event, interact=True, **kwargs):
        if not interact:
            return

        if event == "show":
            cps = preferences.text_cps or 30   # fall back if cps is "infinite"
            renpy.show_screen("typing_ticker", interval=1.0 / cps)

        elif event == "slow_done" or event == "end":
            renpy.hide_screen("typing_ticker")
screen typing_ticker(interval):
    timer interval repeat True action Function(play_click)

define dean =  Character("DEAN RUSK", image="/images/sprites/Dean Rusk.png",kind=bubble, retain=True, callback=type_sound)
define bundy = Character("McGEORGE BUNDY",image="/images/sprites/McGeorge Bundy.png", kind=bubble, retain=True,  callback=type_sound)
define narr =  Character("", callback=type_sound, what_font="gui/fonts/VT323-Regular.ttf")
define air_force = Character("U.S. AIR FORCE", image="/images/sprites/McGeorge Bundy.png",callback=type_sound, kind=bubble,)
define rfk = Character("ROBERT F. KENNEDY",image="/images/sprites/rfk.png", kind=bubble, retain=True,  callback=type_sound)
define rob = Character("ROBERT McNAMARA",image="/images/sprites/Robert McNamara.png", kind=bubble, retain=True,  callback=type_sound)
define taylor = Character("GEN. MAXWELL TAYLOR",image="/images/sprites/General Maxwell Taylora.png", kind=bubble, retain=True,  callback=type_sound)
define anderson = Character("ADM. GEORGE ANDERSON", image="/images/sprites/Admiral George Anderson.png",kind=bubble, retain=True, callback=type_sound)
define lemay = Character("GEN. CURTIS LeMAY",  image="/images/sprites/General Curtis LeMay.png",kind=bubble, retain=True, callback=type_sound)
define navy = Character("U.S. NAVY", image="/images/sprites/McGeorge Bundy.png",callback=type_sound, kind=bubble,)
define operator = Character("WHITE HOUSE OPERATOR", image="/images/sprites/McGeorge Bundy.png",callback=type_sound, kind=bubble)
define counsel = Character("WHITE HOUSE COUNSEL", image="/images/sprites/McGeorge Bundy.png",callback=type_sound, kind=bubble)
define narr_bubble = Character("", image="/images/sprites/McGeorge Bundy.png",callback=type_sound, kind=bubble)
define ending_nvl = Character(None, kind=nvl, callback=type_sound, what_font="gui/fonts/VT323-Regular.ttf",what_xalign=0.5,)

label start:
    $ quick_menu = True
    $ flags.clear()
    $ choices_made = []
    $ timed_out = []
    $ chosen_ending = None
    $ current_date = None
    $ codex_on_scene(current_scene, silent=True)
    python:
        for stat, info in state.items():
            stats[stat] = info["init"]
    $ current_scene = "intro"
    # intro theme (starts 20 s into the track); it is cut the moment the player reaches the Oval Office
    play music "audio/intro.ogg" fadeout 1.0 fadein 0.5 noloop

    # first run only: say what the game is about before it starts
    if not persistent.endings_seen:
        scene black
        narr "October 1962 could have ended ten different ways.{w=1} Find them all.{w=2}{nw}"

    scene bg_intro_1 at bg_size
    narr "Washington. October 16, 1962. 8:45 a.m.{w=2}{nw}"

    scene bg_intro_2 at bg_size
    bundy "Mr. President, there is now hard photographic evidence that the Russians have offensive missiles in Cuba.{w=2}{nw}"

    scene bg_intro_3 at bg_size
    bundy "Mr. President... come with us.{w=2}{nw}"

    scene black with Fade(0.2, 0.0, 0.2)

    $ hud_on = True
    play music "audio/oval_office.ogg" fadeout 0.5 fadein 1.0
    jump expression "D01"

 

label D01:
    $ current_scene = "D01"
    
    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "mcgeorge bundy" at init_pos_despacho

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]


    bundy "Mr. President, Sunday's U-2 pass over San Cristóbal. The analysts say medium-range missile sites. From seventy thousand feet we can't tell if they're ready. Low-level runs could. They could also lose us a pilot."
    
    call screen decision_folder(card_a, card_b)
    $ choice = _return

    
    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D02:
    $ current_scene = "D02"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "rfk" at init_pos_despacho(True)  # T23: mirrored, so not every portrait looks left

    rfk "Jack, the minute this gets past a dozen people it's in the Times. Keep it small and we decide on our own clock. Bring in the whole cabinet and the allies, and we decide on theirs."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    
    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D03:
    $ current_scene = "D03"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_decision

    dean "You told the country in September that offensive weapons in Cuba would not be tolerated. We can say it again now and hold ourselves to it. Or say nothing until we know what we are dealing with."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    
    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)

    
    jump expression next_e

label D04:
    $ current_scene = "D04"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "robert mcnamara" at init_pos_decision

    rob "You'll decide later what we actually do. Today the services need to know which plan to get ready first. The Air Force can be ready to hit the sites within days. The Navy can stand up a quarantine. I can't make both the priority."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    
    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D05:
    $ current_scene = "D05"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_decision

    dean "There is another door. The Brazilians talk to Castro. Through them we could tell him his real problem is the missiles, not us. Or we treat this as Moscow's move and deal only with Moscow."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)

    jump expression next_e

label D06:
    $ current_scene = "D06"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "mcgeorge bundy" at init_pos_decision

    bundy "London, Paris and Bonn will want proof before they stand with us. Show them the photographs and they are in. So is everyone they decide to tell."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D07:
    $ current_scene = "D07"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    # T08: two advisers, two positions. Hawk on the left (mirrored so he faces the room), dove on the right.
    show expression "general maxwell taylor" as hawk at duel_left
    show expression "robert mcnamara" as dove at duel_right

    taylor "Mr. President, every day we wait, more of those sites are ready to fire. Hit them now, while they're unfinished. The Chiefs are unanimous."

    # two retained bubbles land on the same spot: drop the first one before the second adviser speaks
    $ renpy.clear_retain()

    rob "The Air Force says a strike gets most of the missiles. Most. Every one left standing can still be fired. A quarantine keeps the strike in reserve, and a strike cannot be taken back."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)

    
    jump expression next_e

label D08:
    $ current_scene = "D08"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "general maxwell taylor" at init_pos_decision

    taylor "If we go, we decide now how far. Hit only the missile sites and their fighters and SAMs stay up. Take those too and we are one step from invading. The Chiefs prefer the whole package."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D09:
    $ current_scene = "D09"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "robert mcnamara" at init_pos_decision

    rob "The quarantine is agreed. What it's for isn't. It can freeze the situation while we talk, or open an ultimatum. The Navy runs it the same either way. Moscow won't read it the same."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)

    jump expression next_e


label D10:
    $ current_scene = "D10"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_decision

    dean "The lawyers want to know what the quarantine actually stops. Offensive weapons only, and we have a legal case the OAS can sign. Everything, fuel included, and it's a blockade in all but name."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D11:
    $ current_scene = "D11"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "admiral george anderson" as hawk at duel_left
    show expression "dean rusk" as dove at duel_right(True)

    anderson "Mr. President, the Navy has been running blockades since John Paul Jones. Eight hundred miles keeps my ships out of range of Cuban jets. Pull the line in and you put sailors under their guns."

    # two retained bubbles land on the same spot: drop the first one before the second adviser speaks
    $ renpy.clear_retain()

    dean "The British ambassador made a point to you last night: every extra hour is time Khrushchev can use to turn his ships around."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D12:
    $ current_scene = "D12"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "rfk" at init_pos_decision(True)  # T23: mirrored, so not every portrait looks left

    rfk "Seven o'clock tonight, every network. The draft demands the missiles come out, full stop. Or you ask for a halt to the work, checked by the UN, and keep the harder words for later."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D13:
    $ current_scene = "D13"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "mcgeorge bundy" at init_pos_decision

    bundy "What you say on television is for everyone. Moscow can also get a second message, off the record, through your brother and Dobrynin. It helps if they trust it. It hurts if it leaks."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D14:
    $ current_scene = "D14"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    # T08: hawk on the left, dove on the right
    show expression "general maxwell taylor" as hawk at duel_left
    show expression "mcgeorge bundy" as dove at duel_right

    taylor "If they shoot down one of our planes, the pilots need to know the answer is already given. Standing permission to hit the SAM site that fired. No waiting for Washington."

    # two retained bubbles land on the same spot: drop the first one before the second adviser speaks
    $ renpy.clear_retain()

    bundy "Then the decision to start shooting gets made by a missile crew in Cuba and a squadron leader in Florida. Every response should come through you, however long that takes."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D15:
    $ current_scene = "D15"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "general maxwell taylor" at init_pos_decision

    taylor "Strategic Air Command can go to DEFCON 2. Bombers airborne around the clock, missiles on alert. Moscow will see it. So will every unit that now has less time between an order and a launch."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e


label C01:
    #TODO TIMEOUT SYSTEM
    $ current_scene = "C01"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    #show expression "general maxwell taylor" at init_pos_decision

    air_force "Aircraft on the runway, waiting for release. Unless the order is suspended, they launch as planned."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    $ seconds, default_card = crisis_info(current_scene)
    call screen decision_folder(card_a, card_b, seconds, default_card)
    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label C02:
    #TODO TIMEOUT SYSTEM
    $ current_scene = "C02"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    #show expression "general maxwell taylor" at init_pos_decision

    navy "Soviet freighter approaching the line. A submarine is shadowing her. Destroyers request instructions."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    $ seconds, default_card = crisis_info(current_scene)
    call screen decision_folder(card_a, card_b, seconds, default_card)
    $ choice = _return

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

# ---- rama de escalada (T01/T02): se abre al disparar ----

label X01:
    $ current_scene = "X01"

    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    show expression "robert mcnamara" at init_pos_crisis

    rob "Damage reports are in. Most of the launch sites are gone. Most. Soviet troops are firing on our planes, and Moscow has said nothing for twelve hours. The Chiefs want to land before whatever is left can be used."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)

    jump expression next_e

label X02:
    $ current_scene = "X02"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_decision

    dean "Moscow has answered, and not in Cuba. Soviet troops have closed the roads into West Berlin. Khrushchev says they reopen when the bombing stops and we promise never to land."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)

    jump expression next_e

label X03:
    $ current_scene = "X03"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    show expression "general maxwell taylor" at init_pos_crisis

    taylor "The first wave is ashore. They are taking fire from weapons that are not on any of our lists. Our people think the Soviet commanders on the island have lost contact with Moscow."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    $ seconds, default_card = crisis_info(current_scene)
    call screen decision_folder(card_a, card_b, seconds, default_card)

    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)

    jump expression next_e

label X04:
    $ current_scene = "X04"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    show expression "general maxwell taylor" at init_pos_crisis

    taylor "Every Soviet battery on the island has orders to fire on anything that flies. Two more of our planes are overdue. The Chiefs have the air strike set for dawn, and they are not asking."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    $ seconds, default_card = crisis_info(current_scene)
    call screen decision_folder(card_a, card_b, seconds, default_card)

    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)

    jump expression next_e

label D17:
    $ current_scene = "D17"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_decision

    dean "A letter from Khrushchev, long and personal. He says if we promise not to invade Cuba, the reason for the missiles disappears. It reads like a man looking for a way out."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D18:
    $ current_scene = "D18"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "rfk" at init_pos_despacho(True)  # T23: mirrored, so not every portrait looks left

    rfk "Jack, Dobrynin sees me tonight. I can tell him the Jupiters in Turkey will be gone in a few months, on one condition: they never say it was part of the deal."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D19:
    $ current_scene = "D19"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_decision

    dean "Radio Moscow just broadcast a new letter. Missiles out of Cuba if ours come out of Turkey, and they said it publicly. Accept, and the crisis ends today. The Turks and NATO will remember how."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e


label C03:
    #TODO TIMEOUT SYSTEM
    $ current_scene = "C03"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    #show expression "general maxwell taylor" at init_pos_decision

    air_force "A U-2 is down over Cuba. The pilot is dead. The retaliation strike on the SAM site is ready."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    $ seconds, default_card = crisis_info(current_scene)
    call screen decision_folder(card_a, card_b, seconds, default_card)
    $ choice = _return

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label C04:
    #TODO TIMEOUT SYSTEM
    $ current_scene = "C04"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    show expression "mcgeorge bundy" at init_pos_crisis

    bundy "Moscow says it did not order the shootdown. They're asking for an immediate mutual pause. It may be true. It may be cover."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    $ seconds, default_card = crisis_info(current_scene)
    call screen decision_folder(card_a, card_b, seconds, default_card)
    $ choice = _return

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e


label D21:
    $ current_scene = "D21"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_decision

    dean "Through the Brazilians, Castro asks one question. If Cuba sends the Soviet weapons home itself, will Washington recognize Cuba as sovereign, not as Moscow's base or ours?"

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label D22:
    $ current_scene = "D22"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "mcgeorge bundy" at init_pos_decision

    bundy "Radio Moscow again. Khrushchev says the work will stop and the missiles will be crated and shipped home. Now we decide how we check. Surveillance and inspectors, or full access right now."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label D23:
    $ current_scene = "D23"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    # T08: hawk on the left, dove on the right. LeMay's sprite is optional until it exists.
    show expression "general curtis lemay" as hawk at duel_left
    show expression "robert mcnamara" as dove at duel_right

    lemay "We have been had. It's the greatest defeat in our history. They'll stall and hide what's left. I say we hit them Monday anyway, or at least keep every bomber up until the last missile is at sea."

    # two retained bubbles land on the same spot: drop the first one before the second adviser speaks
    $ renpy.clear_retain()

    rob "Khrushchev just gave us what we asked for. If the bombers stay up, Moscow reads it as a threat, and someone on our side reads it as permission. Stand them down."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label S01:
    $ current_scene = "S01"

    scene bg_despacho at bg_size with  Dissolve(0.2)


    operator "Mr. President, the Soviet embassy on line two. They request a permanent coordination office. Here, in the White House. They say, and I quote, it is for the peace."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label S02:
    $ current_scene = "S02"

    scene bg_despacho at bg_size with  Dissolve(0.2)


    counsel "Congress is deadlocked and the cabinet has resigned twice. A coalition proposes an emergency government, shared with new friends. It is unconstitutional. They want your signature anyway."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)

    $ choice = _return

    $ stats_to_change =  events[current_scene][cards_key][choice]["stats"]
    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    
    jump expression next_e

label ENDING:
    $ renpy.block_rollback()
    $ quick_menu = False
    $ hud_on = False
    scene black with fade
    $name = chosen_ending["id"]
    # first the public version (newsreel), then what really happened (cutscene), then the file
    if find_final_newsreel(name):
        call newsreel(find_final_newsreel(name)) from _call_newsreel
        scene black with fade
    if chosen_ending.get("cutscene"):
        call ending_cutscene(chosen_ending["cutscene"]) from _call_ending_cutscene
    $bg = "bg_" + chosen_ending["background"].split(".")[0].lower()
    $title = chosen_ending["title"]
    $tagline = chosen_ending["tagline"]
    $paragraphs = ending_paragraphs(chosen_ending)
    scene expression bg at bg_size with dissolve
    nvl clear
    nvl show dissolve
    $ ending_nvl("{size=60}{i}%s{/i}" % chosen_ending["title"])
    $ ending_nvl("{i}%s{/i}" % chosen_ending["tagline"])

    python:
        unlock_ending(name)
        for para in paragraphs:
            ending_nvl(para)
        if "stamp" in chosen_ending:
            ending_nvl("{i}%s{/i}" % chosen_ending["stamp"])
    scene black with fade
    nvl hide
    nvl clear

    # end-of-run report, then the endings gallery (the goal: find all ten)
    $ renpy.block_rollback()
    $ last_report = build_debrief(chosen_ending)
    # T14: keep the last report of each ending, to read it again from the gallery
    $ persistent.last_reports = dict(persistent.last_reports, **{name: last_report})   # reassign so it is saved
    call screen debrief(chosen_ending, last_report)
    #call screen endings_menu(new_ending=chosen_ending, after_run=True)

    if len(persistent.endings_seen) >= len(endings) and not persistent.epilogue_seen:
        call epilogue

    return

# Newsreel (T06): a few TV frames. Images live in images/newsreel/<image>.png (black if missing).
# "classified" frames show what the public was NOT told.
label newsreel(reel):
    $ hud_was_on = hud_on
    $ hud_on = False
    scene black with Dissolve(0.4)
    python:
        for fr in newsreel_frames(reel):
            speaking = fr.get("audio") and renpy.loadable(fr["audio"])
            if speaking:
                renpy.music.set_volume(0.25, delay=0.5, channel="music")   # duck the music under the speech
                renpy.music.play(fr["audio"], channel="voice", loop=False)
            result = renpy.call_screen("newsreel_frame", fr=fr)
            if speaking:
                renpy.music.stop(channel="voice")
                renpy.music.set_volume(1.0, delay=1.0, channel="music")
            if result == "skip":
                break
    $ hud_on = hud_was_on
    return

label show_last_report_label(e, rep):
    call screen debrief(e, rep) from _call_screen_last_report
    return

# Gallery replay: the ending's newsreel and film, without touching the run in progress.
label replay_ending_label(eid):
    python:
        _saved_flags = dict(flags)
        _saved_music = renpy.music.get_playing()
        _rep = [x for x in endings if x["id"] == eid][0]
        # flags that select the main version of each film (e.g. E08 with the withdrawal announced)
        flags.clear()
        flags.update(_rep["condition"]["flags"])
        if eid == "E08":
            flags["soviet_withdrawal"] = True
    if find_final_newsreel(eid):
        call newsreel(find_final_newsreel(eid)) from _call_replay_newsreel
    if _rep.get("cutscene"):
        call ending_cutscene(_rep["cutscene"]) from _call_replay_cutscene
    python:
        flags.clear()
        flags.update(_saved_flags)
        if _saved_music:
            renpy.music.play(_saved_music, fadeout=1.0, fadein=1.0)
        else:
            renpy.music.stop(fadeout=1.0)
    return

# Cutscene before an ending. Each frame: {"image", "text"} or {"variants": [{"if", "image", "text"}, ...]}.
# Images live in images/cutscenes/<image>.png; if one is missing, the frame is shown on black.
label ending_cutscene(frames):
    play music "audio/crisis.ogg" fadeout 1.5 fadein 1.5
    show screen cutscene_hint
    python:
        for frame in frames:
            v = pick_variant(frame)
            path = "images/cutscenes/%s.png" % v.get("image", "")
            renpy.scene()
            if renpy.loadable(path):
                renpy.show("cutscene_frame", what=Transform(path, xysize=(config.screen_width, config.screen_height)))
            else:
                renpy.show("black")
            renpy.with_statement(Dissolve(0.8))
            if v.get("text"):
                narr(v["text"])
            else:
                renpy.pause(2.5)
    hide screen cutscene_hint
    scene black with Fade(0.2, 0.6, 0.2)
    play music "audio/oval_office.ogg" fadeout 2.0 fadein 2.0
    return

label intermission(date):
    # T06: if there is a newsreel for this day, it replaces the newspaper
    $ reel = find_newsreel(date)
    if reel:
        call newsreel(reel) from _call_newsreel_1
        scene black with Fade(0.2,0.0, 0.2)
        return
    scene  bg_news at bg_size with Dissolve(0.2)
    $ paper = next((n for n in day_transitions["newspapers"] if n["after_date"] == date), None)
    if paper is None:
        return
    $ variant = next(v for v in paper["variants"] if check_trigger(v["if"]))
    call screen newspaper(paper, variant, date)

    scene black with Fade(0.2,0.0, 0.2)

    return