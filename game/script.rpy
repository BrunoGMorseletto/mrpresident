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
transform init_pos_despacho:
    zoom 0.55
    align (0.5, -0.26)
    alpha 0.0
    ease 0.5 alpha 1.0
transform init_pos_decision:
    zoom 0.25
    xpos 950
    ypos 135
    alpha 0.0
    ease 0.5 alpha 1.0
transform init_pos_crisis:
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
    def decide_ending():
        for ending in endings:
            checks_passed = True
            conditions = ending["condition"]
            active_flags=flags.keys()
            for ed_flag, boolean in conditions["flags"].items():
                if ed_flag not in active_flags:
                    flags[ed_flag] = False
                if flags[ed_flag] != boolean:
                    checks_passed = False
            if checks_passed == False:
                continue
            for ed_stat, stat_checks in conditions["stats"].items():
                stat = stats[ed_stat]
                for op, value in stat_checks.items():
                    if not OPS[op](stat, value):
                        checks_passed = False
            if checks_passed:
                return ending
        return endings[-1]
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
define operator = Character("WHITE HOUSE OPERATOR", image="/images/sprites/McGeorge Bundy.png",callback=type_sound, kind=bubble)
define counsel = Character("WHITE HOUSE COUNSEL", image="/images/sprites/McGeorge Bundy.png",callback=type_sound, kind=bubble)
define narr_bubble = Character("", image="/images/sprites/McGeorge Bundy.png",callback=type_sound, kind=bubble)
define ending_nvl = Character(None, kind=nvl, callback=type_sound, what_font="gui/fonts/VT323-Regular.ttf",what_xalign=0.5,)

label start:
    $ flags.clear()
    $ chosen_ending = None
    $ current_date = None
    $ codex_on_scene(current_scene, silent=True)
    python:
        for stat, info in state.items():
            stats[stat] = info["init"]
    $ current_scene = "intro"
    play music "audio/oval_office.ogg" fadeout 2.0 fadein 0.0

    scene bg_intro_1 at bg_size
    narr "Washington. October 16, 1962. 8:45 a.m.{w=2}{nw}"

    scene bg_intro_2 at bg_size
    bundy "Mr. President, there is now hard photographic evidence that the Russians have offensive missiles in Cuba.{w=7.0}{nw}"

    scene bg_intro_3 at bg_size
    bundy "Mr. President... come with us.{w=6}{nw}"

    scene black with Fade(0.2, 0.0, 0.2)

    jump expression "D01"

 

label D01:
    $ current_scene = "D01"
    
    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "mcgeorge bundy" at init_pos_despacho

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]


    bundy "Mr. President, Sunday's U-2 pass over San Cristóbal. The analysts say medium-range missile sites. From seventy thousand feet we can't tell if they're ready. Low-level runs could... but They could also lose us a pilot."
    
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

    show expression "rfk" at init_pos_despacho

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

    rob "Whatever we decide, the services need a plan they can actually execute. The Air Force can be ready to hit the sites within days. The Navy can stand up a quarantine. I can't make both the priority."

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

    show expression "robert mcnamara" at init_pos_decision

    rob "The Air Force says a strike gets most of the missiles. Most. They won't promise all of them, and every one left standing is a missile that can still be fired."

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

    show expression "robert mcnamara" at init_pos_decision

    rob "The Navy wants to intercept eight hundred miles out, beyond the range of Cuban jets. Pull the line in to five hundred and Khrushchev gets more hours to think before a ship has to stop."

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

    show expression "rfk" at init_pos_decision

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

    show expression "robert mcnamara" at init_pos_decision

    rob "If they shoot down one of our planes, the Air Force wants standing permission to hit the SAM site that fired, without calling you first. Otherwise every response waits for your order, however long that takes."

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

    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    #show expression "general maxwell taylor" at init_pos_decision

    air_force "Soviet freighter approaching the line. A submarine is shadowing her. Destroyers request instructions."

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

    show expression "rfk" at init_pos_despacho

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

    show expression "robert mcnamara" at init_pos_decision

    rob "The Chiefs are asking whether to stand down. Some of them think we just gave something away. They want full readiness until the last missile is at sea."

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
    scene black with fade 
    $name = chosen_ending["id"]
    $bg = "bg_" + chosen_ending["background"].split(".")[0].lower()
    $body = "\n\n".join(chosen_ending["body"])
    $title = chosen_ending["title"]
    $tagline = chosen_ending["tagline"]
    scene expression bg at bg_size with dissolve
    nvl clear
    nvl show dissolve
    $ ending_nvl("{size=60}{i}%s{/i}" % chosen_ending["title"])
    $ ending_nvl("{i}%s{/i}" % chosen_ending["tagline"])

    python:
        unlock_ending(name)
        for para in chosen_ending["body"]:
            ending_nvl(para)
        if "stamp" in chosen_ending:
            ending_nvl("{i}%s{/i}" % chosen_ending["stamp"])
    scene black with fade
    nvl hide
    nvl clear
    
    return

label intermission(date):
    scene  bg_news at bg_size with Dissolve(0.2)
    $ paper = next((n for n in day_transitions["newspapers"] if n["after_date"] == date), None)
    if paper is None:
        return
    $ variant = next(v for v in paper["variants"] if check_trigger(v["if"]))
    call screen newspaper(paper, variant, date)

    scene black with Fade(0.2,0.0, 0.2)

    return