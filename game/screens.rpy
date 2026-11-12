################################################################################
## Initialization
################################################################################

init offset = -1


################################################################################
## Styles
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")


style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)



################################################################################
## In-game screens
################################################################################


## Say screen ##################################################################
##
## The say screen is used to display dialogue to the player. It takes two
## parameters, who and what, which are the name of the speaking character and
## the text to be displayed, respectively. (The who parameter can be None if no
## name is given.)
##
## This screen must create a text displayable with id "what", as Ren'Py uses
## this to manage text display. It can also create displayables with id "who"
## and id "window" to apply style properties.
##
## https://www.renpy.org/doc/html/screen_special.html#say

screen say(who, what):

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "namebox"
                text who id "who"

        text what id "what"


    ## If there's a side image, display it above the text. Do not display on the
    ## phone variant - there's no room.
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0

transform crt_flicker:
    

    choice:
        xoffset 0 yoffset 0
    choice:
        xoffset -3 yoffset 2
    
    choice:
        xoffset 1 yoffset -1

    pause 0.05 # Faster tick rate
    repeat

# 2. Define the CRT screen
screen crt_overlay():
    zorder 1000 # Ensures high priority over UI
    add "gui/overlay/CRT_Basic.png" at crt_flicker:
        fit "fill"

#init python:
#    config.overlay_screens.append("crt_overlay")

## Make the namebox available for styling through the Character object.
init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height

    background Image("gui/textbox.png", xalign=0.5, yalign=1.0)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5

style say_dialogue:
    properties gui.text_properties("dialogue")

    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos

    adjust_spacing False


## Input screen ################################################################
##
## This screen is used to display renpy.input. The prompt parameter is used to
## pass a text prompt in.
##
## This screen must create an input displayable with id "input" to accept the
## various input parameters.
##
## https://www.renpy.org/doc/html/screen_special.html#input

screen input(prompt):
    style_prefix "input"

    window:

        vbox:
            xanchor gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos

            text prompt style "input_prompt"
            input id "input"

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width


## Choice screen ###############################################################
##
## This screen is used to display the in-game choices presented by the menu
## statement. The one parameter, items, is a list of objects, each with caption
## and action fields.
##
## https://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 405
    yanchor 0.5

    spacing gui.choice_spacing

style choice_button is default:
    properties gui.button_properties("choice_button")

style choice_button_text is default:
    properties gui.text_properties("choice_button")


## Quick Menu screen ###########################################################
##
## The quick menu is displayed in-game to provide easy access to the out-of-game
## menus.

screen quick_menu():

    ## Ensure this appears on top of other screens.
    zorder 100

    # hidden while the cards are on the table: nothing on top of the decision
    if quick_menu and not renpy.get_screen("decision_folder"):

        hbox:
            style_prefix "quick"
            style "quick_menu"

            # T27: "Back" removed (it could roll back into a decision, T31). The log re-reads text without undoing anything.
            textbutton _("Log") action ShowMenu('history')
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Save") action ShowMenu('save')
            textbutton _("Q.Save") action QuickSave()
            textbutton _("Q.Load") action QuickLoad()
            textbutton _("Prefs") action ShowMenu('preferences')


## This code ensures that the quick_menu screen is displayed in-game, whenever
## the player has not explicitly hidden the interface.
## Quick menu removed at Julián's request (12/11): Esc gives Save/Load/History/Preferences.
# init python:
#     config.overlay_screens.append("quick_menu")

default quick_menu = False

style quick_menu is hbox
style quick_button is default
style quick_button_text is button_text

style quick_menu:
    # top right, small, on a dark strip (it used to sit on the bottom edge, over the cards)
    xalign 1.0
    yalign 0.0
    xoffset -12
    yoffset 12
    spacing 14
    background Frame(Solid("#000000a0"), 0, 0)

style quick_button:
    properties gui.button_properties("quick_button")

style quick_button_text:
    properties gui.text_properties("quick_button")


################################################################################
## Main and Game Menu Screens
################################################################################

## Navigation screen ###########################################################
##
## This screen is included in the main and game menus, and provides navigation
## to other menus, and to start the game.

screen navigation():

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.5

        spacing gui.navigation_spacing

        if main_menu:

            textbutton _("Start") action Start()

        else:

            # restart from the game menu; start resets flags, stats and the run log
            textbutton _("New Game") action Confirm(_("Start a new crisis? Anything you haven't saved will be lost."), Start())

            textbutton _("History") action ShowMenu("history")

            textbutton _("Save") action ShowMenu("save")

        textbutton _("Load") action ShowMenu("load")

        textbutton _("Preferences") action ShowMenu("preferences")

        if _in_replay:

            textbutton _("End Replay") action EndReplay(confirm=True)

        elif not main_menu:

            textbutton _("Main Menu") action MainMenu()

        textbutton _("About") action ShowMenu("about")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

            ## Help isn't necessary or relevant to mobile devices.
            textbutton _("Help") action ShowMenu("help")

        if renpy.variant("pc"):

            ## The quit button is banned on iOS and unnecessary on Android and
            ## Web.
            textbutton _("Quit") action Quit(confirm=not main_menu)


style navigation_button is gui_button
style navigation_button_text is gui_button_text

style navigation_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")

style navigation_button_text:
    properties gui.text_properties("navigation_button")


## Main Menu screen ############################################################
##
## Used to display the main menu when Ren'Py starts.
##
## https://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu():
   
    ## This ensures that any other menu screen is replaced.
    tag menu

    add "gui/mainmenu.png":
        fit "cover"

    vbox:
        xpos 80
        ypos 80
        spacing -70

        text "Mr." style "main_title_small"
        text "President" style "main_title_large"
        
        null height 15 # Espaciado antes del subtítulo
        
    hbox:
        xpos 80
        ypos 350
        spacing 10
        text "—------" style "subtitle_text_line"
        text "Come with us." style "subtitle_text"
        text "—------" style "subtitle_text_line"


    vbox:
        xpos 80
        ypos 450
        spacing 8

        textbutton _("New Game") action Start() style "custom_menu_button"
        textbutton _("Load Game") action ShowMenu("load") style "custom_menu_button"
        textbutton _("Endings") action ShowMenu("endings_menu") style "custom_menu_button"
        textbutton _("Codex") action ShowMenu("codex") style "custom_menu_button"
        textbutton _("Credits") action ShowMenu("credits") style "custom_menu_button"
        textbutton _("Settings") action ShowMenu("preferences") style "custom_menu_button"
        textbutton _("Exit") action Quit(confirm=False) style "custom_menu_button"


# --- ESTILOS DEL TÍTULO ---
style main_title_small:
    size 125
    color "#b5b5b5"
    font "gui/fonts/AbrilFatface-Regular.ttf"

style main_title_large:
    size 108
    color "#8a2424" 
    font "gui/fonts/AbrilFatface-Regular.ttf"

style subtitle_text:
    size 50
    color "#cccccc"
    font "gui/fonts/VT323-Regular.ttf" 

style subtitle_text_line:
    size 50
    color "#8a2424" 
    font "gui/fonts/AbrilFatface-Regular.ttf" 


# --- ESTILOS DE LOS BOTONES ---
style custom_menu_button:
    padding (12, 6, 20, 6)
    background None
    hover_background "#782222" 

style custom_menu_button_text:
    font "gui/fonts/VT323-Regular.ttf"
    size 55
    color "#7a7a7a"           
    hover_color "#ffffff"      
    selected_color "#ffffff"


## Endings Menu Screen ############################################################
image ending_clipboard = "images/ending.png"

screen endings_menu(new_ending=None, after_run=False):
    tag menu
    for input_key in CHEAT_CODE:
        key ("K_"+input_key) action Function(cheat_key, input_key)

    default current = new_ending if new_ending is not None else next((e for e in gallery_endings() if e["id"] in persistent.endings_seen), None)
    if current is not None:
        key "K_RETURN" action Function(replay_ending, current["id"])
        key "K_KP_ENTER" action Function(replay_ending, current["id"])
    default hint = None

    # --- Background: the selected ending's image, or plain black ---
    if current is not None:
        add "bg_" + current["background"].split(".")[0].lower():
            xysize (1920, 1080)
            fit "cover"
            nearest True
            at ending_fade
        add Solid("#0005")     # slight dim so the clipboard stands out
    else:
        add "gui/mainmenu.png":
            fit "cover"

    
    # --- Clipboard, centered ---
    fixed:
        xysize (832, 1040)
        align (0.5, 0.5)

        add "ending_clipboard" zoom 0.7418

        if current is not None:

            # Top left: badge
            fixed:
                pos (100, 136)
                xysize (246, 46)
                text current["badge"].upper():
                    align (0.5, 0.5)
                    size 24
                    color "#2a1d14"

            # Top right: file id
            fixed:
                pos (490, 136)
                xysize (248, 46)
                text "FILE " + current["id"]:
                    align (0.5, 0.5)
                    size 24
                    color "#2a1d14"

            # Big box: header + body text (scrolls if too long)
            viewport:
                pos (116, 210)
                xysize (606, 254)
                mousewheel True
                draggable True
                scrollbars "vertical"   # bigger text no longer fits: the file scrolls

                vbox:
                    spacing 14
                    text current["header"]:
                        size 22
                        color "#a01818"
                    for paragraph in gallery_paragraphs(current):
                        text paragraph:
                            size 24
                            color "#2a1d14"
                            xsize 570

            # Title box
            fixed:
                pos (100, 490)
                xysize (634, 66)
                text current["title"]:
                    align (0.5, 0.5)
                    size 40
                    color "#2a1d14"

            # Red box: tagline
            fixed:
                pos (100, 807)
                xysize (637, 59)
                text current["tagline"]:
                    align (0.5, 0.5)
                    size 26
                    color "#a01818"
                    xsize 610
                    text_align 0.5

        # --- Clue for a locked file, on the paper strip under the slots ---
        if hint:
            fixed:
                pos (100, 950)
                xysize (637, 42)
                text "{color=#a01818}LOCKED FILE:{/color} " + hint:
                    align (0.5, 0.5)
                    size 24
                    color "#2a1d14"
                    xsize 630
                    text_align 0.5

        # --- Bottom row: one slot per ending ---
        for i, e in enumerate(gallery_endings()):
            $ got = e["id"] in persistent.endings_seen
            $ slot_x = [100, 165, 230, 295, 360, 424, 487, 552, 616, 680][i]

            button:
                pos (slot_x, 884)
                xysize (59, 60)
                background None

                if got:
                    # first click selects the file; clicking the selected one again replays its film
                    action If(current is e, Function(replay_ending, e["id"]), SetScreenVariable("current", e))
                else:
                    # locked: no file, but hovering shows a clue
                    action NullAction()
                    hovered SetScreenVariable("hint", e.get("hint"))
                    unhovered SetScreenVariable("hint", None)

                if got:
                    image("/images/endings/" + e["icon"].lower() +".png"):
                        xysize (50, 50)
                        align (0.5, 0.5)
                        nearest True
                else:
                    image("/images/endings/locked.png"):
                        xysize (50, 50)
                        align (0.5, 0.5)
                        nearest True

                # highlight on selected / hover
                if current is e:
                    add Solid("#cc000055")
                elif got:
                    add Solid("#ffffff22") at ending_hover

    # --- Left column: the goal, the count, and clues for locked files ---
    vbox:
        pos (40, 40)
        xsize 480
        spacing 16
        text "OUTCOMES FOUND" size 30 color "#d8d0c0"
        text "%d / %d" % (len(persistent.endings_seen), len(endings)) size 72 color "#ffffff"
        text debrief_data["goal_line"] size 30 color "#d8d0c0"
        null height 16
        text "Double-click a file or press Enter to watch its ending again." size 26 color "#a89880"
        if current is not None and current["id"] in persistent.last_reports:
            null height 10
            textbutton "READ YOUR LAST REPORT" action Function(show_last_report, current["id"]) text_size 28 text_color "#e8dcc0" text_hover_color "#ffffff"
    
    if len(persistent.endings_seen) >= len(endings) and not after_run and current is not None:
            fixed:
                pos (650, 575)
                xysize (631, 226)
                textbutton "EPILOGUE":
                    align (0.5, 0.5)
                    action If(main_menu, Start("epilogue"), Jump("epilogue"))
                    text_size 150
                    text_idle_color "#c81e1e"
                    text_hover_color "#ff4a3a"
                    at epilogue_pulse

    # --- The ending you just reached gets a NEW stamp ---
    if new_ending is not None and current is new_ending:
        text "NEW" size 64 color "#c81e1e" bold True at Transform(rotate=-12):
            pos (1300, 120)

    if after_run:
        vbox:
            xalign 0.97
            yalign 0.92
            spacing 14
            # Jump, not Start(): Start() only works from the main menu context and crashed here
            textbutton "NEW CRISIS" action Jump("start") text_size 40
            textbutton "CODEX" action ShowMenu("codex") text_size 40
            textbutton "MAIN MENU" action MainMenu(confirm=False) text_size 40
    else:
        textbutton _("Return"):
            style "return_button"
            action Return()

transform ending_fade:
    alpha 0.0
    linear 0.4 alpha 1.0

transform ending_hover:
    alpha 0.0
    on hover:
        linear 0.1 alpha 1.0
    on idle:
        linear 0.1 alpha 0.0

transform epilogue_pulse:
    alpha 0.75
    linear 0.9 alpha 1.0
    linear 0.9 alpha 0.75
    repeat


init python:
    # display order in the gallery (the order in endings.json is the resolver's priority and must not change):
    # the historical outcome first, the nuclear one second, the satirical secret last
    GALLERY_ORDER = ["E06", "E01", "E07", "E09", "E10", "E08", "E05", "E04", "E03", "E02"]
    def gallery_endings():
        by_id = dict((e["id"], e) for e in endings)
        return [by_id[i] for i in GALLERY_ORDER if i in by_id] + [e for e in endings if e["id"] not in GALLERY_ORDER]

    CHEAT_CODE = list("arkhipov")
    cheat_buffer = []

    def cheat_key(k):
        cheat_buffer.append(k)
        del cheat_buffer[:-len(CHEAT_CODE)]          # keep only the last keys pressed
        if cheat_buffer == CHEAT_CODE:
            del cheat_buffer[:]
            unlock_all_endings()

    def unlock_all_endings():
        for e in endings:
            persistent.endings_seen.add(e["id"])
            achievement.grant("ending_" + e["id"].lower())
        achievement.progress("all_endings", len(persistent.endings_seen))
        # the code also opens the whole codex: every scene counts as visited, every day as reached
        for sid in events:
            persistent.codex_scenes.add(sid)
        persistent.codex_day = 31
        renpy.save_persistent()
        renpy.notify("All endings and files unlocked")
        renpy.restart_interaction()   

## Credits Menu Screen ############################################################
init python:
    credits_list = [
        ("Game by", "Julián Stordeur and Bruno Gabriel Morseletto"),
        ("Script", "Julián Stordeur"),
        ("Programming", "Bruno Gabriel Morseletto"),
        ("Music", "Thiago Chalon and Gastón Posse"),
        ("Special thanks to", "Jesus Godoy Savoia, Luciano Micael Leone y Franco Ceriani")

    ]

screen credits():
    tag menu

    add gui.main_menu_background   # or gui.game_menu_background

    # optional dark overlay so text is readable
    add Solid("#0008")
    vbox:
        xalign 0.5
        text "utdt gaming lab".upper() size 100 color "#ffcc66" font "gui/fonts/VT323-Regular.ttf" xalign 0.5
        spacing 55
        vpgrid:
            cols 2
            xalign 0.5
            yalign 0.45
            xsize 1400
            ysize 800
            spacing 60
            mousewheel True
            draggable True

            for role, name in credits_list:
                vbox:
                    xsize 650
                    spacing 8
                    text role size 40 color "#ffcc66" font "gui/fonts/VT323-Regular.ttf"
                    text name size 32 font "gui/fonts/VT323-Regular.ttf"

    textbutton _("Return"):
        style "return_button"
        action Return()

## Game Menu screen ############################################################
##
## This lays out the basic common structure of a game menu screen. It's called
## with the screen title, and displays the background, title, and navigation.
##
## The scroll parameter can be None, or one of "viewport" or "vpgrid".
## This screen is intended to be used with one or more children, which are
## transcluded (placed) inside it.

screen game_menu(title, scroll=None, yinitial=0.0, spacing=0):

    style_prefix "game_menu"

    add gui.game_menu_background

    frame:
        style "game_menu_outer_frame"

        hbox:

            ## Reserve space for the navigation section.
            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        yinitial yinitial
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        vbox:
                            spacing spacing

                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial yinitial

                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        spacing spacing

                        transclude

                else:

                    transclude

    use navigation

    textbutton _("Return"):
        style "return_button"

        action Return()

    label title

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 45
    top_padding 180

    background "gui/overlay/game_menu.png"

style game_menu_navigation_frame:
    xsize 420
    yfill True

style game_menu_content_frame:
    left_margin 60
    right_margin 30
    top_margin 15

style game_menu_viewport:
    xsize 1380

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 15

style game_menu_label:
    xpos 75
    ysize 180

style game_menu_label_text:
    size 75
    color gui.accent_color
    yalign 0.5

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -45


## About screen ################################################################
##
## This screen gives credit and copyright information about the game and Ren'Py.
##
## There's nothing special about this screen, and hence it also serves as an
## example of how to make a custom screen.

screen about():

    tag menu

    ## This use statement includes the game_menu screen inside this one. The
    ## vbox child is then included inside the viewport inside the game_menu
    ## screen.
    use game_menu(_("About"), scroll="viewport"):

        style_prefix "about"

        vbox:

            label "[config.name!t]"
            text _("Version [config.version!t]\n")

            ## gui.about is usually set in options.rpy.
            if gui.about:
                text "[gui.about!t]\n"

            text _("Made with {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only].\n\n[renpy.license!t]")


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text

style about_label_text:
    size gui.label_text_size


## Load and Save screens #######################################################
##
## These screens are responsible for letting the player save the game and load
## it again. Since they share nearly everything in common, both are implemented
## in terms of a third screen, file_slots.
##
## https://www.renpy.org/doc/html/screen_special.html#save https://
## www.renpy.org/doc/html/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("Save"))


screen load():

    tag menu

    use file_slots(_("Load"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))

    use game_menu(title):

        fixed:

            ## This ensures the input will get the enter event before any of the
            ## buttons do.
            order_reverse True

            ## The page name, which can be edited by clicking on a button.
            button:
                style "page_label"

                key_events True
                xalign 0.5
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("EMPTY FILE")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        key "save_delete" action FileDelete(slot)

            ## Buttons to access other pages.
            vbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                hbox:
                    xalign 0.5

                    spacing gui.page_spacing

                    textbutton _("<") action FilePagePrevious()
                    key "save_page_prev" action FilePagePrevious()

                    if config.has_autosave:
                        textbutton _("{#auto_page}A") action FilePage("auto")

                    if config.has_quicksave:
                        textbutton _("{#quick_page}Q") action FilePage("quick")

                    ## range(1, 10) gives the numbers from 1 to 9.
                    for page in range(1, 10):
                        textbutton "[page]" action FilePage(page)

                    textbutton _(">") action FilePageNext()
                    key "save_page_next" action FilePageNext()

                if False and config.has_sync:   # cloud sync hidden: not used by this game
                    if CurrentScreenName() == "save":
                        textbutton _("Upload Sync"):
                            action UploadSync()
                            xalign 0.5
                    else:
                        textbutton _("Download Sync"):
                            action DownloadSync()
                            xalign 0.5


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 75
    ypadding 5
    xalign 0.5

style page_label_text:
    textalign 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.text_properties("page_button")

style slot_button:
    properties gui.button_properties("slot_button")

style slot_button_text:
    properties gui.text_properties("slot_button")


## Preferences screen ##########################################################
##
## The preferences screen allows the player to configure the game to better suit
## themselves.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    use game_menu(_("Preferences"), scroll="viewport"):

        vbox:

            hbox:
                box_wrap True

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        label _("Display")
                        textbutton _("Window") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")

                vbox:
                    style_prefix "check"
                    label _("Skip")
                    textbutton _("Unseen Text") action Preference("skip", "toggle")
                    textbutton _("After Choices") action Preference("after choices", "toggle")
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))

                ## Additional vboxes of type "radio_pref" or "check_pref" can be
                ## added here, to add additional creator-defined preferences.

            null height (4 * gui.pref_spacing)

            hbox:
                style_prefix "slider"
                box_wrap True

                vbox:

                    label _("Text Speed")

                    bar value Preference("text speed")

                    label _("Auto-Forward Time")

                    bar value Preference("auto-forward time")

                vbox:

                    if config.has_music:
                        label _("Music Volume")

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        label _("Sound Volume")

                        hbox:
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("Test") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        label _("Voice Volume")

                        hbox:
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("Test") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("Mute All"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 3

style pref_label_text:
    yalign 1.0

style pref_vbox:
    xsize 338

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    properties gui.text_properties("radio_button")

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.text_properties("check_button")

style slider_slider:
    xsize 525

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 15

style slider_button_text:
    properties gui.text_properties("slider_button")

style slider_vbox:
    xsize 675


## History screen ##############################################################
##
## This is a screen that displays the dialogue history to the player. While
## there isn't anything special about this screen, it does have to access the
## dialogue history stored in _history_list.
##
## https://www.renpy.org/doc/html/history.html

screen history():

    tag menu

    ## Avoid predicting this screen, as it can be very large.
    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport"), yinitial=1.0, spacing=gui.history_spacing):

        style_prefix "history"

        for h in _history_list:

            window:

                ## This lays things out properly if history_height is None.
                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"
                        substitute False

                        ## Take the color of the who text from the Character, if
                        ## set.
                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                text what:
                    substitute False

        if not _history_list:
            label _("The dialogue history is empty.")


## This determines what tags are allowed to be displayed on the history screen.

define gui.history_allow_tags = { "alt", "noalt", "rt", "rb", "art" }


style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    textalign gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    textalign gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## Help screen #################################################################
##
## A screen that gives information about key and mouse bindings. It uses other
## screens (keyboard_help, mouse_help, and gamepad_help) to display the actual
## help.

screen help():

    tag menu

    default device = "keyboard"

    use game_menu(_("Help"), scroll="viewport"):

        style_prefix "help"

        vbox:
            spacing 23

            hbox:

                textbutton _("Keyboard") action SetScreenVariable("device", "keyboard")
                textbutton _("Mouse") action SetScreenVariable("device", "mouse")

                if GamepadExists():
                    textbutton _("Gamepad") action SetScreenVariable("device", "gamepad")

            if device == "keyboard":
                use keyboard_help
            elif device == "mouse":
                use mouse_help
            elif device == "gamepad":
                use gamepad_help


screen keyboard_help():

    hbox:
        label _("Enter")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Space")
        text _("Advances dialogue without selecting choices.")

    hbox:
        label _("Arrow Keys")
        text _("Navigate the interface.")

    hbox:
        label _("Escape")
        text _("Accesses the game menu.")

    hbox:
        label _("Ctrl")
        text _("Skips dialogue while held down.")

    hbox:
        label _("Tab")
        text _("Toggles dialogue skipping.")

    hbox:
        label _("Page Up")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Page Down")
        text _("Rolls forward to later dialogue.")

    hbox:
        label "H"
        text _("Hides the user interface.")

    hbox:
        label "S"
        text _("Takes a screenshot.")

    hbox:
        label "V"
        text _("Toggles assistive {a=https://www.renpy.org/l/voicing}self-voicing{/a}.")

    hbox:
        label "Shift+A"
        text _("Opens the accessibility menu.")


screen mouse_help():

    hbox:
        label _("Left Click")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Middle Click")
        text _("Hides the user interface.")

    hbox:
        label _("Right Click")
        text _("Accesses the game menu.")

    hbox:
        label _("Mouse Wheel Up")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Mouse Wheel Down")
        text _("Rolls forward to later dialogue.")


screen gamepad_help():

    hbox:
        label _("Right Trigger\nA/Bottom Button")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Left Trigger\nLeft Shoulder")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Right Shoulder")
        text _("Rolls forward to later dialogue.")

    hbox:
        label _("D-Pad, Sticks")
        text _("Navigate the interface.")

    hbox:
        label _("Start, Guide, B/Right Button")
        text _("Accesses the game menu.")

    hbox:
        label _("Y/Top Button")
        text _("Hides the user interface.")

    textbutton _("Calibrate") action GamepadCalibrate()


style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 12

style help_button_text:
    properties gui.text_properties("help_button")

style help_label:
    xsize 375
    right_padding 30

style help_label_text:
    size gui.text_size
    xalign 1.0
    textalign 1.0



################################################################################
## Additional screens
################################################################################


## Confirm screen ##############################################################
##
## The confirm screen is called when Ren'Py wants to ask the player a yes or no
## question.
##
## https://www.renpy.org/doc/html/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 45

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 150

                textbutton _("Yes") action yes_action
                textbutton _("No") action no_action

    ## Right-click and escape answer "no".
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame([ "gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    xalign .5
    yalign .5

style confirm_prompt_text:
    textalign 0.5
    layout "subtitle"

style confirm_button:
    properties gui.button_properties("confirm_button")

style confirm_button_text:
    properties gui.text_properties("confirm_button")


## Skip indicator screen #######################################################
##
## The skip_indicator screen is displayed to indicate that skipping is in
## progress.
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 9

            text _("Skipping")

            text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


## This transform is used to blink the arrows one after another.
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## We have to use a font that has the BLACK RIGHT-POINTING SMALL TRIANGLE
    ## glyph in it.
    font "DejaVuSans.ttf"


## Notify screen ###############################################################
##
## The notify screen is used to show the player a message. (For example, when
## the game is quicksaved or a screenshot has been taken.)
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")


## NVL screen ##################################################################
##
## This screen is used for NVL-mode dialogue and menus.
##
## https://www.renpy.org/doc/html/screen_special.html#nvl


screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        ## Displays dialogue in either a vpgrid or the vbox.
        if gui.nvl_height:

            vpgrid:
                cols 1
                yinitial 1.0

                use nvl_dialogue(dialogue)

        else:

            use nvl_dialogue(dialogue)

        ## Displays the menu, if given. The menu may be displayed incorrectly if
        ## config.narrator_menu is set to True.
        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


## This controls the maximum number of NVL-mode entries that can be displayed at
## once.
define config.nvl_list_length = gui.nvl_list_length

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text


style nvl_window:
    xfill True
    yfill True
    background Fixed(Transform("gui/nvl5.png", xpos=460, ypos=0, alpha=0.75))
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    textalign gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    textalign gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    textalign gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.text_properties("nvl_button")


## Bubble screen ###############################################################
##
## The bubble screen is used to display dialogue to the player when using speech
## bubbles. The bubble screen takes the same parameters as the say screen, must
## create a displayable with the id of "what", and can create displayables with
## the "namebox", "who", and "window" ids.
##
## https://www.renpy.org/doc/html/bubble.html#bubble-screen

screen bubble(who, what):
    style_prefix "bubble"

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "bubble_namebox"

                vbox:
                    text who:
                        id "who"
                    if who in SPEAKER_TITLES:
                        text SPEAKER_TITLES[who] style "bubble_title"

        text what:
            id "what"

        default ctc = None
        showif ctc:
            add ctc

style bubble_window is empty
style bubble_namebox is empty
style bubble_who is default
style bubble_what is default

style bubble_window:
    xpadding 30
    top_padding 5
    bottom_padding 5

style bubble_namebox:
    xalign 0
    yoffset -35
    background Solid("#1A1A1A")

style bubble_who:
    font "gui/fonts/VT323-Regular.ttf"
    xalign 0
    textalign 0
    color "#ffffff"
    size 35

style bubble_title:
    font "gui/fonts/VT323-Regular.ttf"
    color "#b8b8b8"
    size 24

init python:
    # T11: role shown under each speaker's name
    SPEAKER_TITLES = {
        "ROBERT F. KENNEDY": "Attorney General",
        "DEAN RUSK": "Secretary of State",
        "ROBERT McNAMARA": "Secretary of Defense",
        "McGEORGE BUNDY": "National Security Advisor",
        "GEN. MAXWELL TAYLOR": "Chairman, Joint Chiefs of Staff",
        "ADM. GEORGE ANDERSON": "Chief of Naval Operations",
        "GEN. CURTIS LeMAY": "Chief of Staff, U.S. Air Force",
    }

style bubble_what:
    font "gui/fonts/VT323-Regular.ttf"
    align (0.1, 0.5)
    text_align 0.1
    layout "subtitle"
    color "#ffffff"


define bubble.frame = Frame("gui/bubble.png", 55, 55, 55, 95)
define bubble.thoughtframe = Frame("gui/thoughtbubble.png", 55, 55, 55, 55)
define bubble.dbox = Frame("gui/thoughtbubble2.png", 20, 20, 20, 20)
define bubble.clear = Frame("gui/bubble_clear.png", 20, 20, 20, 20)

define bubble.properties = {
    "clear":{
        "window_background" : bubble.clear,
    },
    "Adbox":{
        "window_background" : bubble.dbox,
    }
}

define bubble.expand_area = {
    "bottom_left" : (0, 0, 0, 22),
    "bottom_right" : (0, 0, 0, 22),
    "top_left" : (0, 22, 0, 0),
    "top_right" : (0, 22, 0, 0),
    "thought" : (0, 0, 0, 0),
    "Adbox":(22, 0, 0, 0),
    "clear":(22, 0, 0, 0),
}



################################################################################
## Mobile Variants
################################################################################

style pref_vbox:
    variant "medium"
    xsize 675

## Since a mouse may not be present, we replace the quick menu with a version
## that uses fewer and bigger buttons that are easier to touch.
screen quick_menu():
    variant "touch"

    zorder 100

    if quick_menu:

        hbox:
            style "quick_menu"
            style_prefix "quick"

            textbutton _("Back") action Rollback()
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Menu") action ShowMenu()


style window:
    variant "small"
    background "gui/phone/textbox.png"

style radio_button:
    variant "small"
    foreground "gui/phone/button/radio_[prefix_]foreground.png"

style check_button:
    variant "small"
    foreground "gui/phone/button/check_[prefix_]foreground.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    background "gui/phone/overlay/game_menu.png"

style game_menu_navigation_frame:
    variant "small"
    xsize 510

style game_menu_content_frame:
    variant "small"
    top_margin 0

style game_menu_viewport:
    variant "small"
    xsize 1305

style pref_vbox:
    variant "small"
    xsize 600

style bar:
    variant "small"
    ysize gui.bar_size
    left_bar Frame("gui/phone/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/phone/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    variant "small"
    xsize gui.bar_size
    top_bar Frame("gui/phone/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/phone/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    variant "small"
    ysize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    variant "small"
    xsize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    variant "small"
    ysize gui.slider_size
    base_bar Frame("gui/phone/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/horizontal_[prefix_]thumb.png"

style vslider:
    variant "small"
    xsize gui.slider_size
    base_bar Frame("gui/phone/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/vertical_[prefix_]thumb.png"

style slider_vbox:
    variant "small"
    xsize None

style slider_slider:
    variant "small"
    xsize 900

### decision folder ###


init python:
    def crisis_info(event_id):
        """(seconds, default card) for crisis events; (0, None) for normal events."""
        crisis = events[event_id].get("crisis")
        if crisis is None:
            return 0, None
        seconds = crisis["timer"]
        override = crisis.get("timer_override")
        if override and check_trigger(override["if"]):
            seconds = override["seconds"]            
        default_card = crisis["on_timeout"]
        if isinstance(default_card, str) == False:          
            default_card = default_card["then"] if check_trigger(default_card["if"]) else default_card["else"]
        return seconds, default_card
    crisis_last_sec = [None]

    def crisis_tick(left):
        """Plays a tick each time the displayed second changes (louder beep in the last 10)."""
        sec = int(left + 0.99)
        if sec == crisis_last_sec[0]:
            return
        crisis_last_sec[0] = sec
        path = "audio/beep.ogg"
        if renpy.loadable(path):
            renpy.music.set_volume(0.5, channel="sound")
            renpy.sound.play(path, channel="sound")

init python:
    CARD_IMG_W, CARD_IMG_H = 922, 1240            # real size of blank_decision_card.png

    # regions as fractions of the card: (x, y, w, h)
    CARD_TITLE = (0.100, 0.082, 0.800, 0.105)     # top box
    CARD_ART   = (0.107, 0.214, 0.787, 0.465)     # big picture area
    CARD_TEXT  = (0.117, 0.720, 0.766, 0.180)     # ruled lines at the bottom

    def card_rect(region, w, h):
        fx, fy, fw, fh = region
        return (int(fx*w), int(fy*h), int(fw*w), int(fh*h))

style card_title_text:
    font "gui/fonts/VT323-Regular.ttf"
    color "#050505"
    text_align 0.5

style card_hint_text is card_title_text:
    text_align 0.0
    justify True

screen folder_card(card, cid, zoom, xoff=0, is_default=False):
    $ w = int(CARD_IMG_W * zoom)
    $ h = int(CARD_IMG_H * zoom)
    $ k = zoom / 0.45                                 
    $ locked = "available_if" in card and not check_trigger(card["available_if"])
    $ tx, ty, tw, th = card_rect(CARD_TITLE, w, h)
    $ ax, ay, aw, ah = card_rect(CARD_ART, w, h)
    $ hx, hy, hw, hh = card_rect(CARD_TEXT, w, h)

    button:
        xpos xoff
        xysize (w, h)
        background Transform("gui/interactives/blank_decision_card.png", zoom=zoom)
        hover_background Transform("gui/interactives/blank_decision_card_selected.png", zoom=zoom)
        insensitive_background Transform("gui/interactives/blank_decision_card.png", zoom=zoom)
        focus_mask True
        sensitive not locked
        action Return(cid)

        fixed:
            area (tx, ty, tw, th)
            $ title_size = fit_size(card["title"], "card_title_text", tw, th, int(50*k), int(14*k))
            text card["title"] style "card_title_text" size title_size xsize tw align (.5, .5)

        fixed:
            area (ax, ay, aw, ah)
            # a locked card looks dead: greyed-out art and a NOT AVAILABLE band across it
            if locked:
                add Transform("gui/interactives/%s.png" % card["icon"], matrixcolor=SaturationMatrix(0.0) * OpacityMatrix(0.35)) fit "contain" xysize (aw, ah) align (.5, .5)
            else:
                add "gui/interactives/%s.png" % card["icon"] fit "contain" xysize (aw, ah) align (.5, .5)
            # T07: who will know about this order (eye = public, crossed eye = secret)
            if card.get("visibility"):
                add "gui/interactives/vis_%s.png" % card["visibility"] fit "contain" xysize (int(aw * 0.42), int(ah * 0.22)) align (1.0, 0.0) offset (int(6*k), -int(6*k))

        fixed:
            area (hx, hy, hw, hh)
            $ hint_txt = card["locked_text"] if locked else card["hint"]
            $ hint_size = fit_size(hint_txt, "card_hint_text", hw, hh, int(35*k), int(14*k))
            text hint_txt style "card_hint_text" size hint_size xsize hw color ("#7a1010" if locked else "#050505")

    if locked:
        frame:
            xpos xoff + w // 2
            xanchor 0.5
            ypos ay + ah // 2
            yanchor 0.5
            xsize int(w * 0.9)
            background Solid("#a01818e6")
            padding (10, 6)
            at Transform(rotate=-8)
            text "NOT AVAILABLE" font "gui/fonts/VT323-Regular.ttf" size int(48 * k) color "#ffffff" xalign 0.5

    # crisis room: mark the card that will be carried out if the clock runs out
    # (inside the card, along the bottom of the picture: above the card it ran into the question)
    if is_default:
        frame:
            xpos xoff + ax + aw // 2
            xanchor 0.5
            ypos ay + ah - int(8 * k)
            yanchor 1.0
            background Solid("#a01818e8")
            padding (int(12 * k), int(3 * k))
            text "IF THE CLOCK RUNS OUT" font "gui/fonts/VT323-Regular.ttf" size int(26 * k) color "#ffffff"

transform folder_fade:
    on show:
        alpha 0.0
        linear 0.4 alpha 1.0
    on hide:
        linear 0.3 alpha 0.0

transform folder_slide:
    on show:
        yoffset 575                          
        easeout_back 0.5 yoffset 0           
    on hide:
        easein_back 0.3 yoffset 900 

screen decision_folder(card_a, card_b, seconds=0, default_card=None):
    zorder 95   # above the codex hotspot (90): the outline stays under the cards
    default left = seconds
    # T09: which card goes on the left is random, so players have to read them.
    # IDs A/B never change (endings and timers use them), only the position on screen.
    # In two-adviser scenes the hawk's card sits on the hawk's side (duel_left_card); elsewhere it is random.
    default swap = (events[current_scene]["duel_left_card"] == "B") if events.get(current_scene, {}).get("duel_left_card") else (renpy.random.random() < 0.5)
    $ card_zoom = 0.45
    $ card_w = int(CARD_IMG_W * card_zoom)
    # T28: one line that sums up the decision, above the cards
    $ dq = events.get(current_scene, {}).get("question")
    if dq:
        frame:
            xalign 0.5
            ypos 455
            background Solid("#000000bb")
            padding (28, 8)
            text dq.upper() font "gui/fonts/VT323-Regular.ttf" size 38 color "#f0e6d0"
    fixed at folder_fade:
        xpos 545
        ypos 505
        use folder_card(card_a, "A", card_zoom, card_w if swap else 0, seconds > 0 and default_card == "A")
        use folder_card(card_b, "B", card_zoom, 0 if swap else card_w, seconds > 0 and default_card == "B")
    if seconds > 0:
        timer 0.1 repeat True action If(left <= 0.1, true=[Function(note_timeout), Return(default_card)], false=[Function(crisis_tick, left), SetScreenVariable("left", left - 0.1)])
        use crisis_bar(left, seconds, (card_a if default_card == "A" else card_b)["title"])

screen crisis_bar(left, total, default_title=None):
    $ secs = int(left + 0.99)
    $ low = secs <= 10
    $ colon = ":" if (left % 1.0) > 0.5 else " "
    $ clock = "%02d%s%02d" % (secs // 60, colon, secs % 60)

    $ pw = 720                          # panel width on screen; the height follows
    $ z = pw / 1476.0
    $ ph = int(662 * z)

    fixed:
        xalign 0.5
        ypos 20
        xysize (pw, ph)

        add Transform("gui/countdown.png", zoom=z)

        text clock:
            font "gui/fonts/VT323-Regular.ttf"
            size int(300 * z)
            color ("#ff5a4a" if low else "#d8281a")
            outlines [(int(3 * z) + 1, "#40000080", 0, 0)]
            xcenter int(0.4993 * pw)
            ycenter int(0.4230 * ph)

    # what happens if the timer runs out (design rule: always visible). Organizations follow their routine.
    $ at_zero = events.get(current_scene, {}).get("crisis", {}).get("at_zero")
    if at_zero:
        frame:
            xalign 0.5
            ypos 20 + ph + 6
            background Solid("#000000bb")
            padding (24, 8)
            text ("IF THE CLOCK RUNS OUT: " + (default_title + ". " if default_title else "") + at_zero):
                font "gui/fonts/VT323-Regular.ttf"
                size 30
                color "#ff8a7a"

init python:
    NEWS_W, NEWS_H = 1672, 941                     # real size of bg_news.png
    NEWS_PHOTO_SHEAR = 0.05 
    # (center x, center y, width, height, angle) in bg_news.png pixels
    NEWS_MAST  = (797, 181, 700, 72,  -5.85)       # top box: newspaper name + date
    NEWS_HEAD  = (834, 329, 940, 140, -5.9)        # big box: headline + deck
    NEWS_PHOTO = (561, 591, 420, 235, -5.9)        # dark photo box

    def news_rect(region, z):
        cx, cy, w, h, ang = region
        return int(cx*z), int(cy*z), int(w*z), int(h*z), ang   # ints: a float would mean "fraction"

    def news_photo(name):
        path = "images/news/%s.png" % name
        return path if renpy.loadable(path) else "gui/news/Prensa_1.png"   # fallback while you add photos

transform news_shear(k):
    matrixanchor (0.5, 0.5)
    matrixtransform Matrix([1.0, k,   0.0, 0.0,
                            0.0, 1.0, 0.0, 0.0,
                            0.0, 0.0, 1.0, k,
                            0.0, 0.0, 0.0, 1.0])

style news_mast:
    font "gui/fonts/VT323-Regular.ttf"
    color "#1b1208"
    text_align 0.5

style news_date is news_mast
style news_headline is news_mast
style news_deck is news_mast

transform news_place(cx, cy, ang):
    xcenter cx
    ycenter cy
    rotate ang

screen newspaper(paper, variant, date):
    $ z = config.screen_width / float(NEWS_W)
    $ mx, my, mw, mh, ma = news_rect(NEWS_MAST, z)
    $ hx, hy, hw, hh, ha = news_rect(NEWS_HEAD, z)
    $ px, py, pw, ph, pa = news_rect(NEWS_PHOTO, z)
    $ masthead = day_transitions["masthead"]

    #add Transform("gui/news/bg_news.png", xysize=(config.screen_width, config.screen_height))

    # photo, cropped to fill the dark box
    fixed at news_shear(NEWS_PHOTO_SHEAR), news_place(px, py, pa):
        xysize (pw, ph)
        clipping True
        add news_photo(variant["photo"]) fit "cover" xysize (pw, ph) align (.5, .5)

    # newspaper name + date
    fixed at news_place(mx, my, ma):
        xysize (mw, mh)
        $ ms = fit_size(masthead, "news_mast", mw, int(mh*0.58), int(34*z), int(12*z))
        $ ds = fit_size(date, "news_date", mw, int(mh*0.38), int(24*z), int(10*z))
        vbox:
            align (.5, .5)
            text masthead style "news_mast" size ms xsize mw
            text date style "news_date" size ds xsize mw

    # headline + deck
    fixed at news_place(hx, hy, ha):
        xysize (hw, hh)
        $ h1 = int(hh*0.62)
        $ h2 = int(hh*0.34)
        fixed:
            area (0, 0, hw, h1)
            $ s1 = fit_size(variant["headline"], "news_headline", hw, h1, int(64*z), int(18*z))
            text variant["headline"] style "news_headline" size s1 xsize hw align (.5, .5)
        fixed:
            area (0, int(hh*0.64), hw, h2)
            $ s2 = fit_size(variant["deck"], "news_deck", hw, h2, int(30*z), int(12*z))
            text variant["deck"] style "news_deck" size s2 xsize hw align (.5, .5)

    key "dismiss" action Return()

    #### CODEX #############################################################################
default codex_locked = False

init python:
    CODEX_DEBUG = False                      
    CODEX_BG_SIZE = (1672, 941)             

    CODEX_SPOTS = {                          # image tag: (x, y, w, h) in background pixels
        "bg_despacho":      (35, 615, 244, 140),  # stack of papers
        "bg_crisis_normal": (0, 755, 504, 186),   # folder with the seal
        "bg_decisions":     (0, 751, 472, 190),   # TOP SECRET folder
    }
    # Outline images can be any size: they are stretched to the full screen.
    # To move one, edit the PNG (or set CODEX_DEBUG = True to see the clickable area in red).
    # red outline drawn over the clickable object, one per background (transparent PNG)
    CODEX_OUTLINES = {tag: "gui/codex_hotspot/%s.png" % tag for tag in CODEX_SPOTS}

    def codex_bg_tag():
        for tag in CODEX_SPOTS:
            if renpy.showing(tag):
                return tag
        return None

    def codex_spot():
        """Hotspot rectangle in screen pixels for the background being shown, or None."""
        tag = codex_bg_tag()
        if tag is None:
            return None
        x, y, w, h = CODEX_SPOTS[tag]
        zx = config.screen_width / float(CODEX_BG_SIZE[0])
        zy = config.screen_height / float(CODEX_BG_SIZE[1])
        return int(x*zx), int(y*zy), int(w*zx), int(h*zy)

    config.overlay_screens.append("codex_hotspot")

screen codex_hotspot():
    zorder 90
    default hot = False
    $ spot = codex_spot()
    if spot and not codex_locked:
        $ outline = CODEX_OUTLINES.get(codex_bg_tag())
        # outline: solid on hover, pulsing while there are unread files, hidden otherwise
        if outline and renpy.loadable(outline):
            if hot:
                add Transform(outline, xysize=(config.screen_width, config.screen_height))
            elif persistent.codex_new:
                add Transform(outline, xysize=(config.screen_width, config.screen_height)) at codex_pulse
        button:
            area spot
            background (Solid("#ff000050") if CODEX_DEBUG else None)
            hovered SetScreenVariable("hot", True)
            unhovered SetScreenVariable("hot", False)
            action [SetScreenVariable("hot", False), Function(codex_focus_scene, current_scene), ShowMenu("codex")]

transform codex_pulse:
    alpha 0.25
    linear 0.9 alpha 1.0
    linear 0.9 alpha 0.25
    repeat

#### HUD: date and day of the crisis (T13) ###############################
default hud_on = False

init python:
    def crisis_day(date):
        """'OCT 24, 1962' -> 9 (October 16 is day 1 of 13)."""
        try:
            return int(date.replace(",", "").split()[1]) - 15
        except Exception:
            return None
    config.overlay_screens.append("crisis_hud")

screen crisis_hud():
    zorder 80
    $ hud_date = events.get(current_scene, {}).get("date") if hud_on else None
    if hud_date and not renpy.get_screen("newspaper") and not renpy.get_screen("codex"):
        frame:
            pos (30, 24)
            padding (18, 10)
            background Solid("#000000aa")
            vbox:
                text hud_date font "gui/fonts/VT323-Regular.ttf" size 34 color "#ffffff"
                text "DAY %d OF 13" % crisis_day(hud_date) font "gui/fonts/VT323-Regular.ttf" size 24 color "#b8b8b8"
                # T07: secret until one of your decisions makes it public (speech, leak, strike)
                if not flags.get("crisis_public"):
                    text "CRISIS: SECRET" font "gui/fonts/VT323-Regular.ttf" size 24 color "#d8b04a"
                else:
                    text "CRISIS: PUBLIC" font "gui/fonts/VT323-Regular.ttf" size 24 color "#e05a4a"


#### NEWSREEL (T06) ######################################################
# TV frame and scanlines are drawn by code (gui/newsreel/), footage images stay clean.
define NR_SCREEN = (424, 152, 891, 700)          # x, y, w, h of the TV picture, matches the magenta hole of bezel.png

style nr_lower is default:
    font "gui/fonts/VT323-Regular.ttf"
    color "#ffffff"
    size 40
style nr_caption is default:
    font "gui/fonts/VT323-Regular.ttf"
    color "#e8e2d6"
    size 32
    text_align 0.5
    xalign 0.5
style nr_classified is default:
    font "gui/fonts/VT323-Regular.ttf"
    color "#e8e2d6"
    size 36
    text_align 0.5
    xalign 0.5

screen newsreel_frame(fr):
    modal True
    zorder 100
    $ nx, ny, nw, nh = NR_SCREEN
    add Solid("#000000")

    if fr.get("classified"):
        # what the public was not told
        vbox:
            xalign 0.5
            yalign 0.45
            xsize 1100
            spacing 30
            text "CLASSIFIED · NOT FOR BROADCAST" style "nr_classified" color "#c81e1e" size 52
            text fr.get("caption", "") style "nr_classified"
    else:
        fixed:
            pos (nx, ny)
            xysize (nw, nh)
            clipping True
            $ img = "images/newsreel/%s.png" % fr.get("image", "")
            if renpy.loadable(img):
                add img fit "cover" xysize (nw, nh) align (.5, .5)
            else:
                add Solid("#1a1a1a")
            add "gui/newsreel/scanlines.png" pos (-nx, -ny)
            if fr.get("lower_third"):
                frame:
                    xfill True
                    yalign 0.88
                    background Solid("#000000cc")
                    padding (90, 12)     # wide side padding: the screen corners are rounded
                    text fr["lower_third"] style "nr_lower" xalign 0.5
        add "gui/newsreel/bezel.png"
        if fr.get("caption"):
            frame:
                xalign 0.5
                ypos 960
                xmaximum 1600
                background Solid("#000000cc")
                padding (24, 10)
                text fr["caption"] style "nr_caption"

    textbutton "SKIP NEWS" action Return("skip") align (0.97, 0.03) text_font "gui/fonts/VT323-Regular.ttf" text_size 30
    # T30: visible timer and how to advance
    bar value AnimatedValue(0, fr.get("seconds", 9), fr.get("seconds", 9), fr.get("seconds", 9)) xysize (600, 6) xalign 0.5 ypos 1050 left_bar Solid("#e8e2d6") right_bar Solid("#ffffff22")
    text "CLICK TO CONTINUE" font "gui/fonts/VT323-Regular.ttf" size 24 color "#a89880" xalign 0.97 yalign 0.97
    timer fr.get("seconds", 9) action Return("next")
    key "dismiss" action Return("next")


#### END-OF-RUN REPORT (debrief) #########################################
# Background: gui/debrief/folder.png (1672x941). Coordinates below are in that image's pixels,
# scaled to the screen by DB_Z. Bruno: nudge DB_* rectangles if the text does not sit on the pages.
define DB_Z = 1920 / 1672.0
define DB_TABS = [(440, 35, 235, 57), (680, 35, 220, 57), (905, 35, 210, 57)]   # x, y, w, h of each tab
define DB_LEFT = (285, 215, 520, 615)      # left page text area (starts below the paper clip)
define DB_RIGHT = (880, 140, 520, 690)     # right page text area
define DB_TAB_NAMES = ["YOUR CRISIS", "WHAT REALLY HAPPENED", "THREE LENSES"]
# the tab art is light on the first tab and dark on the other two: text color per tab (normal, selected)
define DB_TAB_INK = [("#2a1d14", "#a01818"), ("#d8c8a8", "#ffd27a"), ("#d8c8a8", "#ffd27a")]

init python:
    def db(r):
        return tuple(int(v * DB_Z) for v in r)

style db_ink is default:
    font "gui/fonts/VT323-Regular.ttf"
    color "#2a1d14"
    size 30
style db_head is db_ink:
    size 40
    color "#5a1010"
style db_small is db_ink:
    size 26
    color "#4a3a2a"

screen debrief(ending, d):
    modal True
    default tab = 0
    add "gui/debrief/folder.png" xysize (config.screen_width, config.screen_height)

    # tabs
    for i, name in enumerate(DB_TAB_NAMES):
        $ tx, ty, tw, th = db(DB_TABS[i])
        button:
            pos (tx, ty)
            xysize (tw, th)
            background (None if tab == i else Solid("#00000055"))
            hover_background Solid("#ffffff22")
            action SetScreenVariable("tab", i)
            text name style "db_ink" size (26 if tab == i else 24) align (0.5, 0.6) color DB_TAB_INK[i][1 if tab == i else 0] underline (tab == i)

    $ lx, ly, lw, lh = db(DB_LEFT)
    $ rx, ry, rw, rh = db(DB_RIGHT)

    if tab == 0:
        # YOUR CRISIS
        vbox:
            pos (lx, ly)
            xsize lw
            spacing 24
            text "AFTER-ACTION REPORT" style "db_small"
            text ending["title"] style "db_head" size 48
            text d["recap"] style "db_ink" size 34
        vbox:
            pos (rx, ry + 120)
            xsize rw
            spacing 22
            text "WHAT TIPPED IT" style "db_small"
            for f in d["fragments"]:
                text "- " + f style "db_ink"

    elif tab == 1:
        # WHAT REALLY HAPPENED
        $ rows = d["history"]
        vbox:
            pos (lx, ly)
            xsize lw
            spacing 20
            text "WHAT REALLY HAPPENED" style "db_head"
            if d["followed"]:
                text "Your October followed 1962 closely." style "db_ink"
                text "In 1962: Washington did not know that nuclear warheads were already in Cuba, some of them meant for the beaches." style "db_ink"
            for scene, title, fact in rows[:3]:
                vbox:
                    spacing 4
                    text "You: " + title style "db_small"
                    text "In 1962: " + fact style "db_ink" size 28
        vbox:
            pos (rx, ry + 120)
            xsize rw
            spacing 20
            for scene, title, fact in rows[3:]:
                vbox:
                    spacing 4
                    text "You: " + title style "db_small"
                    text "In 1962: " + fact style "db_ink" size 28

    else:
        # THREE LENSES (Allison & Zelikow), explained on the page itself
        vbox:
            pos (lx, ly)
            xsize lw
            spacing 14
            text "THREE LENSES" style "db_head"
            text debrief_data["lenses_intro"] style "db_small"
            $ total = sum(d["lenses"].values())
            text "You made %d decisions in this run:" % total style "db_ink" size 26
            null height 2
            for lk in ("rational", "organizational", "governmental"):
                $ lens = debrief_data["lenses"][lk]
                hbox:
                    spacing 20
                    # how many of this run's decisions fall under this lens
                    vbox:
                        xsize 70
                        text str(d["lenses"][lk]) style "db_head" size 56 color ("#a01818" if d["dominant"] == lk else "#2a1d14") xalign 0.5
                        text ("decision" if d["lenses"][lk] == 1 else "decisions") style "db_small" size 18 xalign 0.5
                    vbox:
                        xsize lw - 90
                        text "{b}" + lens["plain"] + "{/b}  (" + lens["name"] + ")" style "db_ink" size 28
                        text lens["line"] style "db_small" size 24
                        if lk in d["examples"]:
                            text "From your run: " + d["examples"][lk] style "db_small" size 22 color "#7a2316"
        vbox:
            pos (rx, ry + 60)
            xsize rw
            spacing 22
            text "WHAT IT SAYS ABOUT YOUR CRISIS" style "db_small"
            if d["dominant"]:
                text debrief_data["lenses"][d["dominant"]]["dominant"] style "db_ink"
            else:
                text debrief_data["lenses_tie"] style "db_ink"
            if d["timeouts"]:
                text debrief_data["timeout_line"] % d["timeouts"] style "db_ink" color "#a01818"
            text debrief_data["lenses_note"] style "db_small"
            textbutton "More in the codex" action [Function(codex_open_entry, "TS-01"), ShowMenu("codex")] text_style "db_small" text_underline True

    textbutton "CONTINUE":
        align (0.97, 0.97)
        text_font "gui/fonts/VT323-Regular.ttf"
        text_size 42
        text_color "#e8e2d6"
        text_hover_color "#ffffff"
        action Return()


# T30: during ending films, say how to advance
screen cutscene_hint():
    zorder 90
    text "CLICK TO CONTINUE" font "gui/fonts/VT323-Regular.ttf" size 24 color "#a89880aa" xalign 0.97 yalign 0.97
