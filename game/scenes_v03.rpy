# Escenas v0.3 generadas desde events_v03.json. Mismo esquema que las labels de script.rpy.
# Personajes de voz nuevos (sin sprite propio todavia, mismo placeholder que air_force):
# navy is already defined in script.rpy
define nato = Character("NATO COMMAND", image="/images/sprites/McGeorge Bundy.png", callback=type_sound, kind=bubble)
define norad = Character("NORAD", image="/images/sprites/McGeorge Bundy.png", callback=type_sound, kind=bubble)

label ROOT_1:
    $ current_scene = "ROOT_1"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "robert mcnamara" at init_pos_decision

    rob "Two camps in this room, Mr. President. Hit the sites now, before they're ready, and accept we won't get all of them. Or squeeze them first and keep the planes for later. Whichever you pick, the other one stops being a plan."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label ROOT_2:
    $ current_scene = "ROOT_2"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_despacho

    dean "Stevenson sent you a memo last night. Before any blockade, he says, go to Khrushchev privately and put every base on the table, Turkey included. Gromyko is here at five. The Navy says it can have a quarantine ready in four days."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label ATK_SCOPE:
    $ current_scene = "ATK_SCOPE"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "general maxwell taylor" at init_pos_decision

    taylor "If we go, we decide now how far. Hit only the missile sites and their fighters and SAMs stay up. Take those too and we are one step from invading. The Chiefs prefer the whole package."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label ATK_BERLIN:
    $ current_scene = "ATK_BERLIN"

    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_crisis

    dean "Thirty hours after the strike, Soviet troops closed the autobahn to West Berlin. Checkpoint Charlie is shut. Moscow's note is one sentence long: a base for a base."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label ATK_TACTICAL:
    $ current_scene = "ATK_TACTICAL"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_max at bg_size with  Dissolve(0.2)

    nato "SACEUR to the President. Soviet armor is moving on the autobahn in strength. If my forward units are overrun, I need release authority for tactical nuclear weapons. Now, not when it happens."

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

label ATK_LANDING:
    $ current_scene = "ATK_LANDING"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "general maxwell taylor" at init_pos_decision

    taylor "Three days of strikes, Mr. President. Through U Thant, Moscow offers to crate the missiles if the bombing stops. The Chiefs say finish it. The fleet is loaded and the beaches are marked. D-day is Monday."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label ATK_PREAUTH:
    $ current_scene = "ATK_PREAUTH"

    scene bg_crisis_max at bg_size with  Dissolve(0.2)

    show expression "robert mcnamara" at init_pos_crisis

    rob "First wave is ashore. Recon reports short-range rockets near the beaches, and the analysts can't rule out nuclear warheads. The Chiefs want authority to answer in kind if they're used on our troops. Without coming back to you first."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label TRK_SPEECH:
    $ current_scene = "TRK_SPEECH"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "rfk" at init_pos_despacho

    rfk "Seven o'clock tonight, every network. The draft demands the missiles come out, full stop. Or you ask for a halt to the work, checked by the UN, and keep the harder words for later."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label TRK_SHIP:
    $ current_scene = "TRK_SHIP"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    navy "Soviet ships approaching the line, a submarine shadowing them. And a cable from U Thant: suspend the quarantine for two weeks, Moscow suspends its shipments, everybody talks. Destroyers request instructions."

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

label TRK_SUBMARINE:
    $ current_scene = "TRK_SUBMARINE"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    navy "Soviet submarine near the line. She won't come up. The destroyers request permission to drop practice depth charges as a signal to surface. Moscow was told about the procedure. We don't know if she was."

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

label TRK_U2:
    $ current_scene = "TRK_U2"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    air_force "A U-2 is down over Cuba. The pilot is dead. The retaliation strike on the SAM site is ready."

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

label TRK_MAULTSBY:
    $ current_scene = "TRK_MAULTSBY"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_normal at bg_size with  Dissolve(0.2)

    air_force "One of our U-2s on an air-sampling run near the Pole is lost. The pilot navigated by the stars and got it wrong. He's over Soviet territory, Chukotka. MiGs are up. Alaska wants to launch F-102s to bring him home. Their missiles are nuclear."

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

label TRK_TURKEY:
    $ current_scene = "TRK_TURKEY"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "rfk" at init_pos_despacho

    rfk "Jack, Radio Moscow wants the Jupiters out of Turkey, in public, and the crisis ends today. Dobrynin sees me tonight. I can give him the Jupiters in private instead, on one condition: they never say it was part of the deal."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label TRK_VERIFY:
    $ current_scene = "TRK_VERIFY"

    scene bg_decisions at bg_size with  Dissolve(0.2)

    show expression "mcgeorge bundy" at init_pos_decision

    bundy "Radio Moscow again. Khrushchev says the work will stop and the missiles will be crated and shipped home. Now we decide how we check. Surveillance and inspectors, or full access right now."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label TRK_FALSE_ALARM:
    $ current_scene = "TRK_FALSE_ALARM"

    play music "audio/crisis.ogg" fadeout 0.5 fadein 0.3 if_changed
    scene bg_crisis_max at bg_size with  Dissolve(0.2)

    norad "NORAD to the White House. The Moorestown radar reports a missile launched from Cuba. Projected impact: Tampa. Minutes, not hours. No detonation reported yet."

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

label NEG_KEATING:
    $ current_scene = "NEG_KEATING"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    counsel "Senator Keating is on the Senate floor again. Last week he said 'rocket bases'. Today he has locations. The press office needs a line before noon, and Gromyko is due at five."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label NEG_WHO:
    $ current_scene = "NEG_WHO"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_despacho

    dean "Gromyko will sit in that chair at five and tell you the weapons are defensive. You can let him, or you can open the drawer. Or we leave Moscow out and go through the Brazilians. Castro is the one who has to live next to those missiles."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label NEG_TIME:
    $ current_scene = "NEG_TIME"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_despacho

    dean "Moscow's answer, through Dobrynin. Khrushchev no longer denies it. He'll discuss everything when he comes to New York for the UN, late November. Until then he asks for quiet. By late November, every site will be operational."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label NEG_LEAK:
    $ current_scene = "NEG_LEAK"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "mcgeorge bundy" at init_pos_despacho

    bundy "Reston at the Times has it. Not all of it. Enough. Dryfoos, the publisher, is holding the front page for your call. If it runs tomorrow, your seven days are over, and so is everything said in private."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label NEG_CASTRO:
    $ current_scene = "NEG_CASTRO"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_despacho

    dean "Through the Brazilians, Castro answers. He will send the Soviet weapons home himself if Washington guarantees no invasion and recognizes Cuba as sovereign. And he wants the sabotage to stop. He means Mongoose."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e

label NEG_OFFER:
    $ current_scene = "NEG_OFFER"

    scene bg_despacho at bg_size with  Dissolve(0.2)

    show expression "dean rusk" at init_pos_despacho

    dean "Radio Moscow, Mr. President, an hour ago. Khrushchev will take his missiles out of Cuba if we take ours out of Turkey. He said it in public, so whatever we answer, we answer in public too."

    $ card_a = events[current_scene][cards_key][a_card_key]
    $ card_b = events[current_scene][cards_key][b_card_key]

    call screen decision_folder(card_a, card_b)
    $ choice = _return

    $ aftermath=apply_choice(choice, current_scene)
    narr_bubble "[aftermath]"
    scene black with Fade(0.2,0.0, 0.2)
    $ next_e = next_event(events[current_scene]["next"],events)
    jump expression next_e
