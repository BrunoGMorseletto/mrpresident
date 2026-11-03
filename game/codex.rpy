## ---------------------------------------------------------------------------
## codex.rpy  -  Codex for "Mr. President: Come with us"
##
## Needs:  data/codex.json
##         images/codex/codex.png            (the open folder)
##         gui/fonts/VT323-Regular.ttf
##         audio/codex_tab.ogg, audio/codex_page.ogg   (optional)
## Uses:   events (events.json, with "date"), current_scene,
##         persistent.endings_seen (from the ending unlock system)
##
## Hooks you must call from your own code (see the end of this file).
## ---------------------------------------------------------------------------

## ---- saved state ----------------------------------------------------------
default persistent.codex_scenes = set()   # event ids the player has reached, ever
default persistent.codex_day = 0          # latest October day reached (opens the calendar)
default persistent.codex_new = set()      # unlocked but not opened yet (red dots)
default persistent.codex_hint = False     # the "click the folder" hint was shown once

default codex_tab = 0
default codex_page = 0
default codex_sel = None
default codex_mode = "1962"


## ---- data and logic -------------------------------------------------------
init python:
    import json
    import math

    CODEX_BG_W, CODEX_BG_H = 1672, 941        # size of codex.png
    CODEX_PER_PAGE = 14                       # entries per list page (lines 2..15)

    # Tabs. Intelligence and CIA share one tab; "Excomm" is shown as "People".
    CODEX_TABS = [
        {"label": "Intelligence", "code": "INT", "cats": ["Intelligence", "CIA"]},
        {"label": "State",        "code": "STA", "cats": ["State"]},
        {"label": "Defense",      "code": "DEF", "cats": ["Defense"]},
        {"label": "People",       "code": "PPL", "cats": ["Excomm"]},
        {"label": "Calendar",     "code": "CAL", "cats": ["Calendar"]},
        {"label": "Top Secret",   "code": "TS",  "cats": ["Top Secret"]},
    ]

    # Clickable area of each tab on codex.png: (x, y, w, h)
    CODEX_TAB_RECTS = [
        (778, 162, 44, 90), (778, 272, 50, 95), (779, 388, 51, 94),
        (780, 503, 52, 97), (782, 621, 52, 100), (783, 732, 32, 84),
    ]

    # Ruled lines of the left page: (y at x=350, tilt in degrees).
    # Line 1 holds the tab title, lines 2..15 the entries, line 16 the pager.
    CODEX_LINES = [
        (140.6, 2.07), (180.6, 1.97), (216.7, 1.89), (253.3, 1.80),
        (290.2, 1.69), (327.8, 1.57), (365.5, 1.47), (403.5, 1.39),
        (442.3, 1.19), (480.7, 1.12), (519.6, 1.03), (558.7, 0.91),
        (597.8, 0.84), (637.5, 0.66), (677.5, 0.57), (717.6, 0.46),
        (758.9, 0.29),
    ]
    CODEX_LIST_X, CODEX_LIST_W, CODEX_ROW_H = 350, 395, 34

    # Right page (bg pixels)
    CODEX_R_X, CODEX_R_W = 935, 520
    CODEX_PHOTO = (1305, 194, 150, 150)       # x, y, w, h
    CODEX_MODELS = {
        "Rational Actor": "MODEL I",
        "Organizational Behavior": "MODEL II",
        "Governmental Politics": "MODEL III",
    }

    with renpy.file("data/codex.json") as f:
        codex_data = json.load(f)

    CODEX_INDEX = {}                          # id -> (title, entry, category)
    for _cat, _items in codex_data.items():
        for _title, _entry in _items.items():
            CODEX_INDEX[_entry["id"]] = (_title, _entry, _cat)

    # ---- geometry helpers ----
    def cz(v):
        """bg pixels -> screen pixels (always an int, never a float fraction)."""
        return int(round(v * config.screen_width / float(CODEX_BG_W)))

    def codex_row(line, w, h, lift=3):
        """Center x, center y (screen px) and tilt of a w x h box sitting on a ruled line."""
        y350, ang = CODEX_LINES[line]
        xc = CODEX_LIST_X + w / 2.0
        yc = y350 + (w / 2.0) * math.tan(math.radians(ang)) - lift - h / 2.0
        return cz(xc), cz(yc), ang

    def codex_esc(s):
        return s.replace("[", "[[").replace("{", "{{")

    # ---- tabs and lists ----
    def codex_tab_ids(tab):
        ids = []
        for cat in CODEX_TABS[tab]["cats"]:
            for title, entry in codex_data[cat].items():
                ids.append(entry["id"])
        return ids

    def codex_pages(tab):
        n = len(codex_tab_ids(tab))
        return max(1, (n + CODEX_PER_PAGE - 1) // CODEX_PER_PAGE)

    # ---- unlock rules ----
    def codex_endings():
        return len(persistent.endings_seen or ())

    def codex_unlocked(eid):
        entry = CODEX_INDEX[eid][1]
        if eid.startswith("CAL-") and eid[4:].isdigit():
            # calendar days open as the player reaches each day
            return persistent.codex_day >= int(eid[4:])
        rule = entry["unlock"]
        if "scene" in rule:
            return rule["scene"] == "start" or rule["scene"] in persistent.codex_scenes
        if "endings_found" in rule:
            return codex_endings() >= int(rule["endings_found"])
        return True

    def codex_declass_open(entry):
        gate = entry.get("unlock_declassified")
        if gate is None:
            return True
        return codex_endings() >= int(gate.get("endings_found", 0))

    def codex_unlocked_set():
        return set([eid for eid in CODEX_INDEX if codex_unlocked(eid)])

    def codex_count_in_tab(tab):
        ids = codex_tab_ids(tab)
        return len([eid for eid in ids if codex_unlocked(eid)]), len(ids)

    def codex_total():
        return len([eid for eid in CODEX_INDEX if codex_unlocked(eid)]), len(CODEX_INDEX)

    def codex_unread_in_tab(tab):
        return any([eid in persistent.codex_new for eid in codex_tab_ids(tab)])

    def codex_lock_hint(eid):
        rule = CODEX_INDEX[eid][1]["unlock"]
        if "endings_found" in rule:
            return "Reach an ending to open this file."
        if eid.startswith("CAL-"):
            return "This day has not happened yet."
        return "Not in the folder yet. Different decisions lead through different events."

    # ---- hooks (call these from your game code) ----
    def codex_check_new(before, silent=False):
        """Compare against the unlocked set from before; mark and announce new files."""
        new = [eid for eid in CODEX_INDEX if eid not in before and codex_unlocked(eid)]
        if not new:
            return
        if silent:
            renpy.save_persistent()
            return
        for eid in new:
            persistent.codex_new.add(eid)
        if len(new) == 1:
            msg = "Codex updated: " + codex_esc(CODEX_INDEX[new[0]][0])
        else:
            msg = "Codex updated: %d new files" % len(new)
        if not persistent.codex_hint:
            persistent.codex_hint = True
            msg += "\nClick the folder on the desk to read them."
        renpy.save_persistent()
        renpy.notify(msg)

    def codex_on_scene(scene_id, silent=False):
        """Call when an event starts (and once at game start with silent=True)."""
        before = codex_unlocked_set()
        persistent.codex_scenes.add(scene_id)
        info = events.get(scene_id)
        date = info.get("date") if info else None
        if date:
            day = int(date.replace(",", "").split()[1])
            if day > persistent.codex_day:
                persistent.codex_day = day
        codex_check_new(before, silent)

    # ---- navigation (all screen actions go through these) ----
    def codex_sfx(kind):
        path = {"tab": "audio/codex_tab.ogg", "page": "audio/codex_page.ogg"}.get(kind)
        if path and renpy.loadable(path):
            renpy.sound.play(path, channel="sound")

    def codex_first_open(ids):
        for eid in ids:
            if codex_unlocked(eid):
                return eid
        return ids[0] if ids else None

    def codex_select(eid, play=True):
        global codex_sel, codex_mode, codex_page
        if eid is None:
            return
        codex_sel = eid
        ids = codex_tab_ids(codex_tab)
        if eid in ids:
            codex_page = ids.index(eid) // CODEX_PER_PAGE
        entry = CODEX_INDEX[eid][1]
        codex_mode = "1962" if entry["description"].get("1962") else "declassified"
        if eid in persistent.codex_new and codex_unlocked(eid):
            persistent.codex_new.discard(eid)
            renpy.save_persistent()
        if play:
            codex_sfx("page")

    def codex_set_tab(i):
        global codex_tab, codex_page
        codex_tab = i % len(CODEX_TABS)
        codex_page = 0
        codex_select(codex_first_open(codex_tab_ids(codex_tab)), play=False)
        codex_sfx("tab")

    def codex_step_tab(d):
        codex_set_tab(codex_tab + d)

    def codex_step(d):
        ids = codex_tab_ids(codex_tab)
        i = ids.index(codex_sel) if codex_sel in ids else 0
        codex_select(ids[max(0, min(len(ids) - 1, i + d))])

    def codex_set_page(p):
        global codex_page
        codex_page = max(0, min(codex_pages(codex_tab) - 1, p))
        codex_sfx("page")

    def codex_set_mode(mode):
        global codex_mode
        codex_mode = mode
        codex_sfx("page")

    def codex_ensure():
        """When the codex opens: make sure the selection belongs to the current tab."""
        if codex_sel is None or codex_sel not in codex_tab_ids(codex_tab):
            codex_select(codex_first_open(codex_tab_ids(codex_tab)), play=False)
        else:
            codex_sfx("page")

    def codex_focus_scene(scene_id):
        """Open on the file that belongs to the event the player is in, if there is one."""
        global codex_tab, codex_page
        for t in range(len(CODEX_TABS)):
            for eid in codex_tab_ids(t):
                rule = CODEX_INDEX[eid][1]["unlock"]
                if rule.get("scene") == scene_id and codex_unlocked(eid):
                    codex_tab = t
                    codex_select(eid, play=False)
                    return

    # ---- content helpers for the right page ----
    def codex_photo(entry):
        path = "images/codex/" + entry["id"] +".png"
        return path if renpy.loadable(path) else None

    def codex_modes(entry):
        modes = []
        if entry["description"].get("1962"):
            modes.append(("1962", "1962 FILE"))
        if entry["description"].get("declassified"):
            modes.append(("declassified", "DECLASSIFIED" if codex_declass_open(entry) else "CLASSIFIED"))
        modes.append(("sources", "SOURCES"))
        return modes

    def codex_sources_text(entry):
        src = entry.get("sources") or []
        if not src:
            return "No sources listed for this file."
        return "\n".join(["%d. %s" % (i + 1, codex_esc(s)) for i, s in enumerate(src)])

    def codex_frac(eid, k):
        """Deterministic 0..1 value, used for the widths of the redaction bars."""
        return ((sum([ord(c) for c in eid]) * 37 + k * 53) % 100) / 100.0

    _codex_fit_cache = {}
    def codex_fit(s, style, w, h, max_size, min_size):
        """Largest font size (<= max_size) where s, wrapped to width w, fits in w x h."""
        key = (s, style, w, h, max_size, min_size)
        if key in _codex_fit_cache:
            return _codex_fit_cache[key]
        size = max_size
        while size > min_size:
            d = Text(s, style=style, size=size, xsize=w)
            rw, rh = renpy.render(d, w, h, 0, 0).get_size()
            if rw <= w and rh <= h:
                break
            size -= 1
        _codex_fit_cache[key] = size
        return size


## ---- styles and transforms ------------------------------------------------
style codex_text:
    font "gui/fonts/VT323-Regular.ttf"
    color "#2a1b10"

style codex_arrow_text is codex_text:
    hover_color "#9a2a1c"
    insensitive_color "#2a1b1040"

style codex_mode_text is codex_text:
    color "#2a1b10a0"
    hover_color "#9a2a1c"

style codex_mode_on_text is codex_text:
    color "#7a2316"
    underline True

style codex_close_text is codex_text:
    color "#d9c49a"
    hover_color "#ffffff"

transform codex_rot(cx, cy, ang):
    xcenter cx
    ycenter cy
    rotate ang

transform codex_stamp_t(cx, cy):
    xcenter cx
    ycenter cy
    rotate -12

transform codex_fade:
    on show:
        alpha 0.0
        linear 0.25 alpha 1.0
    on hide:
        linear 0.2 alpha 0.0


## ---- screens --------------------------------------------------------------
screen codex_redacted(eid, w, h, stamp, hint):
    ## black bars + a red stamp: used for locked files and classified text
    for k in range(7):
        $ bw = int(w * (0.55 + 0.45 * codex_frac(eid, k)))
        add Solid("#1c1410") xysize (bw, cz(18)) xpos 0 ypos (k * cz(32))
    text stamp style "codex_text" size cz(64) color "#a3281a" at codex_stamp_t(w // 2, int(h * 0.42))
    text hint style "codex_text" size cz(22) xsize w ypos (h - cz(64))


screen codex():
    tag menu
    modal True

    $ ids = codex_tab_ids(codex_tab)
    $ pages = codex_pages(codex_tab)
    $ page_ids = ids[codex_page * CODEX_PER_PAGE:(codex_page + 1) * CODEX_PER_PAGE]
    $ sel = CODEX_INDEX[codex_sel] if codex_sel else None

    on "show" action Function(codex_ensure)

    key "game_menu" action Return()
    key "K_LEFT" action Function(codex_step_tab, -1)
    key "K_RIGHT" action Function(codex_step_tab, 1)
    key "K_UP" action Function(codex_step, -1)
    key "K_DOWN" action Function(codex_step, 1)
    key "K_PAGEUP" action Function(codex_set_page, codex_page - 1)
    key "K_PAGEDOWN" action Function(codex_set_page, codex_page + 1)
    key "mousedown_4" action Function(codex_set_page, codex_page - 1)
    key "mousedown_5" action Function(codex_set_page, codex_page + 1)

    fixed at codex_fade:

        add Transform("images/codex/codex.png", xysize=(config.screen_width, config.screen_height))

        ## ---- tabs ----
        for i, tab in enumerate(CODEX_TABS):
            $ tx, ty, tw, th = [cz(v) for v in CODEX_TAB_RECTS[i]]
            button:
                area (tx, ty, tw, th)
                background (None if i == codex_tab else Solid("#2a1a0c38"))
                hover_background Solid("#ffffff26")
                action Function(codex_set_tab, i)
                text tab["code"] style "codex_text" size cz(24) align (.5, .5) color ("#8a1f14" if i == codex_tab else "#3a2412")
                if i == codex_tab:
                    add Solid("#a02a1e") xsize cz(5) xalign 1.0
                if codex_unread_in_tab(i):
                    add Solid("#d63a2a") xysize (cz(11), cz(11)) align (.9, .08)

        ## ---- left page: title line ----
        $ hx, hy, hang = codex_row(1, CODEX_LIST_W, CODEX_ROW_H)
        $ got, total = codex_count_in_tab(codex_tab)
        fixed at codex_rot(hx, hy, hang):
            xysize (cz(CODEX_LIST_W), cz(CODEX_ROW_H))
            text CODEX_TABS[codex_tab]["label"].upper() style "codex_text" size cz(34) color "#7a2316" yalign 1.0
            text ("%d/%d" % (got, total)) style "codex_text" size cz(28) xalign 1.0 yalign 1.0

        ## ---- left page: index on the ruled lines ----
        for i, eid in enumerate(page_ids):
            $ rx, ry, rang = codex_row(2 + i, CODEX_LIST_W, CODEX_ROW_H)
            $ rtitle = CODEX_INDEX[eid][0]
            $ ropen = codex_unlocked(eid)
            fixed at codex_rot(rx, ry, rang):
                xysize (cz(CODEX_LIST_W), cz(CODEX_ROW_H))
                button:
                    xysize (cz(CODEX_LIST_W), cz(CODEX_ROW_H))
                    background (Solid("#9a2a1c2e") if eid == codex_sel else None)
                    hover_background Solid("#0000001c")
                    action Function(codex_select, eid)
                    if ropen:
                        if eid in persistent.codex_new:
                            add Solid("#c0392b") xysize (cz(9), cz(9)) xpos cz(4) yalign .5
                        $ rs = codex_fit(codex_esc(rtitle), "codex_text", cz(CODEX_LIST_W - 40), cz(CODEX_ROW_H), cz(27), cz(15))
                        text codex_esc(rtitle) style "codex_text" size rs xpos cz(22) yalign .5
                    else:
                        add Solid("#1c1410") xysize (int(cz(CODEX_LIST_W - 60) * (0.35 + 0.65 * codex_frac(eid, 1))), cz(15)) xpos cz(22) yalign .5

        ## ---- left page: pager on the last line ----
        if pages > 1:
            $ px, py, pang = codex_row(16, CODEX_LIST_W, CODEX_ROW_H)
            fixed at codex_rot(px, py, pang):
                xysize (cz(CODEX_LIST_W), cz(CODEX_ROW_H))
                textbutton "<" action Function(codex_set_page, codex_page - 1) sensitive (codex_page > 0) xalign 0.0 yalign .5 text_style "codex_arrow_text" text_size cz(30)
                text ("%d / %d" % (codex_page + 1, pages)) style "codex_text" size cz(26) align (.5, .5)
                textbutton ">" action Function(codex_set_page, codex_page + 1) sensitive (codex_page < pages - 1) xalign 1.0 yalign .5 text_style "codex_arrow_text" text_size cz(30)

        ## ---- right page: the selected file ----
        if sel:
            $ stitle, sentry, scat = sel
            $ s_open = codex_unlocked(codex_sel)
            $ photo = codex_photo(sentry) if s_open else None
            $ photo_slot = s_open and (photo is not None or CODEX_TABS[codex_tab]["label"] == "People")
            $ title_w = 355 if photo_slot else CODEX_R_W
            $ title_h = 190 if photo_slot else 92
            $ body_y = 396 if photo_slot else 296
            $ body_h = 760 - body_y

            text ("FILE " + sentry["id"]) style "codex_text" size cz(20) color "#7a2316" xpos cz(CODEX_R_X) ypos cz(168)
            if s_open and sentry["allison_model"] in CODEX_MODELS:
                text CODEX_MODELS[sentry["allison_model"]] style "codex_text" size cz(20) color "#7a2316" xpos cz(CODEX_R_X + CODEX_R_W) xanchor 1.0 ypos cz(168)

            ## title (or a redaction bar while locked)
            fixed:
                area (cz(CODEX_R_X), cz(196), cz(title_w), cz(title_h))
                if s_open:
                    $ ts = codex_fit(codex_esc(stitle), "codex_text", cz(title_w), cz(title_h), cz(40), cz(20))
                    text codex_esc(stitle) style "codex_text" size ts xsize cz(title_w) yalign (0.5 if photo_slot else 0.0)
                else:
                    add Solid("#1c1410") xysize (cz(min(title_w, 300)), cz(26)) ypos cz(8)

            ## photo, or a "no photo" card for people
            if photo_slot:
                $ phx, phy, phw, phh = CODEX_PHOTO
                fixed at codex_rot(cz(phx + phw / 2.0), cz(phy + phh / 2.0), -2.5):
                    xysize (cz(phw), cz(phh))
                    add Solid("#efe6d0")
                    add Solid("#0000001a") xysize (cz(phw - 10), cz(phh - 10)) align (.5, .5)
                    if photo:
                        add photo fit "cover" xysize (cz(phw - 10), cz(phh - 10)) xalign (.5) ypos (5)
                    else:
                        text "NO PHOTO\nON FILE" style "codex_text" size cz(22) align (.5, .5) text_align .5 color "#7a2316"

            ## body
            fixed:
                area (cz(CODEX_R_X), cz(body_y), cz(CODEX_R_W), cz(body_h))
                if not s_open:
                    use codex_redacted(codex_sel, cz(CODEX_R_W), cz(body_h), "RESTRICTED", codex_lock_hint(codex_sel))
                elif codex_mode == "sources":
                    $ stext = codex_sources_text(sentry)
                    $ ss = codex_fit(stext, "codex_text", cz(CODEX_R_W), cz(body_h), cz(24), cz(14))
                    text stext style "codex_text" size ss xsize cz(CODEX_R_W)
                elif codex_mode == "declassified":
                    if codex_declass_open(sentry):
                        $ dtext = codex_esc(sentry["description"]["declassified"])
                        $ ds = codex_fit(dtext, "codex_text", cz(CODEX_R_W), cz(body_h), cz(26), cz(14))
                        text dtext style "codex_text" size ds xsize cz(CODEX_R_W)
                    else:
                        use codex_redacted(codex_sel, cz(CODEX_R_W), cz(body_h), "CLASSIFIED", "Reach an ending to declassify this file.")
                else:
                    $ ntext = codex_esc(sentry["description"].get("1962", ""))
                    $ ns = codex_fit(ntext, "codex_text", cz(CODEX_R_W), cz(body_h), cz(26), cz(14))
                    text ntext style "codex_text" size ns xsize cz(CODEX_R_W)

            ## mode buttons: 1962 file / declassified / sources
            if s_open:
                hbox:
                    area (cz(CODEX_R_X), cz(768), cz(CODEX_R_W), cz(34))
                    spacing cz(26)
                    for mkey, mlabel in codex_modes(sentry):
                        textbutton mlabel:
                            action Function(codex_set_mode, mkey)
                            text_style ("codex_mode_on_text" if codex_mode == mkey else "codex_mode_text")
                            text_size cz(24)

        ## ---- footer on the desk ----
        $ gt, gtotal = codex_total()
        text ("FILES %d / %d" % (gt, gtotal)) style "codex_close_text" size cz(28) xpos cz(210) ycenter cz(902)
        textbutton _("CLOSE") action Return() xcenter cz(836) ycenter cz(902) text_style "codex_close_text" text_size cz(30)


## ---------------------------------------------------------------------------
## HOOKS: what to add to the rest of your game
##
## 1) label start (after the reset):
##        $ codex_on_scene(current_scene, silent=True)
##
## 2) next_event: right before "return name":
##        codex_on_scene(name)
##
## 3) unlock_ending: first line and last line:
##        before = codex_unlocked_set()
##        ...                       (your existing code)
##        codex_check_new(before)
##
## 4) codex_hotspot screen: replace the button action and add the pulse:
##        action [Function(codex_focus_scene, current_scene), ShowMenu("codex")]
##    and, before the button, when there is something new:
##        if persistent.codex_new:
##            add Solid("#ffd27a") area spot at codex_pulse
##
##    transform codex_pulse:
##        alpha 0.10
##        linear 0.9 alpha 0.40
##        linear 0.9 alpha 0.10
##        repeat
## ---------------------------------------------------------------------------
