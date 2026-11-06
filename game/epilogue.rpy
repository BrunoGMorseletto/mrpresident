## EPILOGUE: "What happened next"
## Se reproduce una sola vez, al terminar la partida en la que se completan los 10 finales.
## Se puede saltear con el botón SKIP (o con la tecla de skip de Ren'Py).
## Usa el mismo sonido de tipeo que la intro (type_sound, en script.rpy).
##
## Para engancharlo, en script.rpy, dentro de label ENDING, justo antes del "return" final:
##
##     if len(persistent.endings_seen) >= len(endings) and not persistent.epilogue_seen:
##         call epilogue
##
## Imágenes: game/images/epilogue/ep_01.png ... ep_08.png

default persistent.epilogue_seen = False

image ep_01 = "images/epilogue/ep_01.png"
image ep_02 = "images/epilogue/ep_02.png"
image ep_03 = "images/epilogue/ep_03.png"
image ep_04 = "images/epilogue/ep_04.png"
image ep_05 = "images/epilogue/ep_05.png"
image ep_06 = "images/epilogue/ep_06.png"
image ep_07 = "images/epilogue/ep_07.png"
image ep_08 = "images/epilogue/ep_08.png"

init python:
    def type_sound(event, interact=True, **kwargs):
        if not interact:
            return

        if event == "show":
            cps = preferences.text_cps or 30   # fall back if cps is "infinite"
            renpy.show_screen("typing_ticker", interval=1.0 / cps)

        elif event == "slow_done" or event == "end":
            renpy.hide_screen("typing_ticker")

# Texto centrado sobre negro, con el mismo tipeo y la misma fuente que el resto del juego
define ep_center = Character(None, kind=centered, callback=type_sound,
    what_font="gui/fonts/VT323-Regular.ttf", what_size=46, what_text_align=0.5)

# Texto sobre las láminas
define ep_narr = Character(None, callback=type_sound,
    what_font="gui/fonts/VT323-Regular.ttf")

# Zoom lento (efecto documental). t = duración en segundos
transform ep_zoom_in(t=24):
    xysize (1920, 1080)
    align (0.5, 0.5)
    zoom 1.0
    linear t zoom 1.08

transform ep_zoom_out(t=24):
    xysize (1920, 1080)
    align (0.5, 0.5)
    zoom 1.08
    linear t zoom 1.0

transform ep_pan_right(t=24):
    xysize (1920, 1080)
    zoom 1.1
    xalign 0.0 yalign 0.5
    linear t xalign 1.0

transform ep_still:
    xysize (1920, 1080)
    align (0.5, 0.5)

# Fecha arriba a la izquierda, estilo sello
screen ep_date(d):
    zorder 5
    text d:
        font "gui/fonts/VT323-Regular.ttf"
        size 54
        color "#e8dcc0"
        outlines [(3, "#000000aa", 0, 0)]
        xpos 70 ypos 50

screen ep_skip():
    zorder 10
    textbutton "SKIP >>":
        xalign 0.98 yalign 0.03
        text_font "gui/fonts/VT323-Regular.ttf"
        text_size 34
        text_color "#e8dcc055"
        text_hover_color "#e8dcc0"
        action Jump("epilogue_end")


label epilogue:
    $ persistent.epilogue_seen = True
    $ renpy.save_persistent()
    $ _skipping = True

    stop music fadeout 2.0
    scene black with Fade(1.0, 1.0, 1.0)
    show screen ep_skip
    # TODO Gaso: reemplazar por el tema del epílogo (audio/epilogue.ogg)
    play music "audio/main_menu.ogg" fadein 6.0

    pause 1.5
    ep_center "OCTOBER 28, 1962.{w=1.5}{nw}"
    ep_center "The missiles are leaving Cuba.\nThe world is told how the crisis ended.{w=2.5}{nw}"
    ep_center "This is what happened next.{w=2.5}{nw}"

    # ---- PLATE 1: el carguero sale de La Habana
    scene ep_01 at ep_zoom_in(30) with Dissolve(2.0)
    show screen ep_date("NOVEMBER 20, 1962")
    pause 1.0
    ep_narr "Moscow agrees to withdraw its bombers from Cuba. Kennedy lifts the quarantine. The crisis is over.{w=3.0}{nw}"
    ep_narr "General LeMay has already told the President it is \"the greatest defeat in our history.\"{w=3.0}{nw}"
    ep_narr "In Cuba, ninety-eight Soviet nuclear warheads are still waiting for a ship. Washington does not know they are there.{w=4.0}{nw}"

    # ---- PLATE 2: los Júpiter en Turquía
    hide screen ep_date
    scene ep_02 at ep_pan_right(30) with Dissolve(1.5)
    show screen ep_date("APRIL 1963")
    pause 1.0
    ep_narr "An American submarine visits Izmir, and the newspapers are pleased. The next day, crews begin taking down the Jupiter missiles.{w=3.0}{nw}"
    ep_narr "Officially, it is a modernization. Rusk and McNamara have told Congress there was no deal.{w=3.0}{nw}"
    ep_narr "On April 24, the last missile comes down.{w=3.0}{nw}"

    # ---- PLATE 3: American University
    hide screen ep_date
    scene ep_03 at ep_zoom_in(28) with Dissolve(1.5)
    show screen ep_date("JUNE 10, 1963")
    pause 1.0
    ep_narr "Eight months after the crisis, Kennedy talks about living alongside the Soviet Union.{w=2.5}{nw}"
    ep_narr "\"Our most basic common link is that we all inhabit this small planet.\"{w=3.5}{nw}"
    ep_narr "In Moscow, the newspapers print the entire speech.{w=3.0}{nw}"

    # ---- PLATE 4: la línea directa
    hide screen ep_date
    scene ep_04 at ep_zoom_in(32) with Dissolve(1.5)
    show screen ep_date("JUNE 20, 1963")
    pause 1.0
    ep_narr "The two governments agree to a direct line. It is not a red telephone. It is a teletype.{w=3.0}{nw}"
    ep_narr "On August 5, a treaty is signed in Moscow. Nuclear tests will end in the air, in space and under water. They will continue underground.{w=3.5}{nw}"
    ep_narr "When the line is tested, Washington sends a typing exercise. Moscow answers with a description of the sunset.{w=4.0}{nw}"

    # ---- PLATE 5: el Salón Oval vacío
    hide screen ep_date
    scene ep_05 at ep_zoom_in(30) with Dissolve(2.0)
    show screen ep_date("NOVEMBER 22, 1963")
    pause 1.5
    ep_narr "While Kennedy is in Dallas, a new carpet is laid in the Oval Office. He helped choose it.{w=2.5}{nw}"
    ep_narr "He never sees the room.{w=3.5}{nw}"
    ep_narr "That same day, in Paris, a CIA officer hands a Cuban official a pen built to kill Fidel Castro.{w=4.0}{nw}"

    # ---- PLATE 6: el Kremlin
    hide screen ep_date
    scene ep_06 at ep_zoom_out(28) with Dissolve(1.5)
    show screen ep_date("OCTOBER 1964")
    pause 1.0
    ep_narr "Khrushchev's colleagues remove him from power. The Soviet public is told it is a matter of age and health.{w=3.0}{nw}"
    ep_narr "The charges drawn up in private include Cuba. He had presented a defeat as a victory.{w=4.0}{nw}"

    # ---- PLATE 7: el pabellón de caza
    hide screen ep_date
    scene ep_07 at ep_zoom_in(36) with Dissolve(1.5)
    show screen ep_date("SPRING 1963")
    pause 1.0
    ep_narr "No one had asked Fidel Castro. He heard about the deal from the news, and he took it as a betrayal.{w=3.0}{nw}"
    ep_narr "At a hunting lodge, Khrushchev reads him messages from Washington. By Castro's account, one mentions missiles in Turkey.{w=3.0}{nw}"
    ep_narr "He asks Khrushchev to read it again. Khrushchev laughs.{w=3.0}{nw}"
    ep_narr "Castro stays in power for another forty-five years.{w=3.5}{nw}"

    # ---- PLATE 8: Moscú, 1989
    hide screen ep_date
    scene ep_08 at ep_zoom_in(36) with Dissolve(1.5)
    show screen ep_date("MOSCOW, JANUARY 1989")
    pause 1.0
    ep_narr "In 1969, Robert Kennedy's account of the crisis is published after his death. It is called {i}Thirteen Days{/i}. For a generation, it is how the story is told.{w=3.5}{nw}"
    ep_narr "In 1982, six of Kennedy's advisers write that Turkey was an assurance, not a deal.{w=3.0}{nw}"
    ep_narr "In January 1989, in Moscow, Theodore Sorensen admits that he edited it out of Robert Kennedy's diary before the book came out.{w=4.0}{nw}"

    # ---- Cierre: negro, sin música
    hide screen ep_date
    stop music fadeout 3.0
    scene black with Fade(1.5, 2.0, 0.0)
    pause 2.0
    ep_center "A handful of men knew how it ended.{w=2.5}{nw}"
    ep_center "You have seen it end ten ways.{w=5.0}{nw}"

label epilogue_end:
    hide screen ep_skip
    hide screen ep_date
    stop music fadeout 1.5
    scene black with Dissolve(1.0)
    return
