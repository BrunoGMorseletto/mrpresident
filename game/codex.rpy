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
default codex_desk = False      # DAYS tab: the calendar lying on the desk, full screen
default codex_prev_tab = 0


## ---- data and logic -------------------------------------------------------
init python:
    import json
    import math

    CODEX_BG_W, CODEX_BG_H = 1672, 941        # size of codex.png
    CODEX_PER_PAGE = 14                       # entries per list page (lines 2..15)

    # Tabs. Intelligence and CIA share one tab; "Excomm" is shown as "People".
    CODEX_TABS = [
        # "tab": word written sideways on the tab; "full": shown on hover (T29)
        {"label": "Intelligence", "code": "INT", "tab": "INTEL",    "full": "Intelligence and the CIA", "cats": ["Intelligence", "CIA"]},
        {"label": "State",        "code": "STA", "tab": "STATE",    "full": "State Department: diplomacy", "cats": ["State"]},
        {"label": "Defense",      "code": "DEF", "tab": "DEFENSE",  "full": "Defense: the military", "cats": ["Defense"]},
        {"label": "People",       "code": "PPL", "tab": "PEOPLE",   "full": "People of the crisis", "cats": ["Excomm"]},
        {"label": "Calendar",     "code": "CAL", "tab": "DAYS",     "full": "Calendar: October 1962, day by day", "cats": ["Calendar"]},
        {"label": "Top Secret",   "code": "TS",  "tab": "SECRET",   "full": "Top Secret: unlocked by finding endings", "cats": ["Top Secret"]},
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
            # one scene, or a list (any of them): e.g. a fact that opens after the decision, whatever branch follows
            scenes = rule["scene"] if isinstance(rule["scene"], (list, tuple)) or hasattr(rule["scene"], "append") else [rule["scene"]]
            return "start" in scenes or any(sc in persistent.codex_scenes for sc in scenes)
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
        global codex_tab, codex_page, codex_desk, codex_prev_tab
        i = i % len(CODEX_TABS)
        if CODEX_TABS[i]["label"] == "Calendar":
            if CODEX_TABS[codex_tab]["label"] != "Calendar":
                codex_prev_tab = codex_tab
            codex_desk = True
        else:
            codex_desk = False
        codex_tab = i
        codex_page = 0
        codex_select(codex_first_open(codex_tab_ids(codex_tab)), play=False)
        codex_sfx("tab")

    def codex_desk_open(eid):
        """A day on the desk calendar: read its file in the folder."""
        global codex_desk
        codex_select(eid)
        codex_desk = False

    def codex_desk_show():
        global codex_desk
        codex_desk = True
        codex_sfx("page")

    def codex_desk_back():
        """Back to the tab you were on before the calendar."""
        codex_set_tab(codex_prev_tab)

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

    def codex_open_entry(eid):
        """Open the codex on a given file (used by the end-of-run report)."""
        global codex_tab
        for t in range(len(CODEX_TABS)):
            if eid in codex_tab_ids(t):
                codex_tab = t
                codex_select(eid, play=False)
                return

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
        if renpy.loadable(path):
            return path
        # archival photos: images/codex/real_photos/<ID>_<name>.jpg (credits in CREDITOS_fotos.csv)
        pre = "images/codex/real_photos/" + entry["id"] + "_"
        for f in renpy.list_files():
            if f.startswith(pre) and f.lower().endswith((".jpg", ".png")):
                return f
        return None

    def codex_photo_box(photo):
        """The print takes the photo's own shape (archival photos are rarely square), top right of the page."""
        right, top = CODEX_PHOTO[0] + CODEX_PHOTO[2], CODEX_PHOTO[1]
        max_w, max_h = 165, 175
        try:
            iw, ih = renpy.image_size(photo) if photo else (1, 1)
        except Exception:
            iw, ih = 1, 1
        a = iw / float(ih)
        if abs(a - 1.0) < 0.02:
            w = h = CODEX_PHOTO[2]
        elif a > 1:
            w, h = max_w, max(90, int(max_w / a))
        else:
            h = max_h
            w = min(max_w, int(max_h * a))
        return (right - w, top, w + 10, h + 10)

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
    default tab_tip = None
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
                hovered SetScreenVariable("tab_tip", i)
                unhovered SetScreenVariable("tab_tip", None)
                # the full word, written sideways so it fits the narrow tab (T29)
                text tab["tab"] style "codex_text" size cz(20) align (.5, .5) color ("#8a1f14" if i == codex_tab else "#3a2412") at Transform(rotate=90, rotate_pad=False)
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

        if CODEX_TABS[codex_tab]["label"] == "Calendar":
            fixed at codex_rot(hx, hy, hang):
                xysize (cz(CODEX_LIST_W), cz(CODEX_ROW_H))
                textbutton "OPEN CALENDAR" action Function(codex_desk_show) xalign 0.62 yalign 1.0 text_style "codex_text" text_size cz(24) text_color "#7a2316" text_hover_color "#2a1d14" text_underline True

        if True:
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
        ## (when the desk calendar is open it covers the whole folder: see the end of the screen)
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
                text CODEX_MODELS[sentry["allison_model"]] style "codex_text" size cz(20) color "#7a2316" xpos cz(CODEX_R_X + CODEX_R_W - 70) xanchor 1.0 ypos cz(168)

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
                $ phx, phy, phw, phh = codex_photo_box(photo)
                fixed at codex_rot(cz(phx + phw / 2.0), cz(phy + phh / 2.0), -2.5):
                    xysize (cz(phw), cz(phh))
                    add Solid("#efe6d0")
                    add Solid("#0000001a") xysize (cz(phw - 10), cz(phh - 10)) align (.5, .5)
                    if photo:
                        add photo fit "contain" xysize (cz(phw - 10), cz(phh - 10)) align (.5, .5)
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

        ## ---- DAYS: the calendar on the desk covers the folder ----
        if codex_desk:
            use codex_desk_calendar(ids)

        ## ---- tooltip with the tab's full name: drawn last, so nothing covers it ----
        if tab_tip is not None:
            $ ttx, tty, ttw, tth = [cz(v) for v in CODEX_TAB_RECTS[tab_tip]]
            frame:
                pos (ttx - cz(8), tty + tth // 2)
                anchor (1.0, 0.5)
                background Solid("#1a120bdd")
                padding (cz(14), cz(6))
                text CODEX_TABS[tab_tip]["full"] style "codex_text" size cz(24) color "#f0e6d0"


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


## ---- Calendar tab: a real October 1962 month grid ---------------------------------
## October 1, 1962 was a Monday. Days with a file (CAL-14 ... CAL-28) are clickable;
## the thirteen days of the crisis (16-28) are tinted. "Before" and "After" sit below the grid.
init python:
    def codex_calendar_days(ids):
        days = {}
        for eid in ids:
            tail = eid.split("-")[-1]
            if tail.isdigit() and int(tail) > 0:
                days[int(tail)] = eid
        return days

define CAL_IMG = "gui/codex_calendar.png"                 # generated sheet, grid detected from its lines
define CAL_SIZE = (981, 1204)
define CAL_ROWS = [333, 408, 554, 700, 846, 990, 1139]      # header band top, grid top, week lines... (image px)
define CAL_COLS = [21, 157, 292, 426, 558, 692, 824, 962]   # column lines (image px)
define CAL_BOX = (344, 190, 407)                            # x, y, width on the codex page (bg px)
define CAL_TILT = 1.4                                       # the left page is slightly rotated

init python:
    def cal_px(v):
        """Calendar image px -> screen px. (A lambda inside the screen cannot see screen variables.)"""
        return cz(v * CAL_BOX[2] / float(CAL_SIZE[0]))

screen codex_calendar(ids):
    $ days = codex_calendar_days(ids)
    $ bx, by, bw = CAL_BOX
    $ k = bw / float(CAL_SIZE[0])
    $ bh = CAL_SIZE[1] * k

    fixed at codex_rot(cz(bx + bw / 2.0), cz(by + bh / 2.0), CAL_TILT):
        xysize (cz(bw), cz(bh))
        add CAL_IMG xysize (cz(bw), cz(bh))

        # month title; the arrows open the files before and after October
        text "OCTOBER 1962" style "codex_text" size cal_px(104) color "#2a1d14" xalign 0.5 ycenter cal_px(230)
        for eid, arrow, ax in (("CAL-00", "<", 0.08), ("CAL-AFTER", ">", 0.92)):
            if eid in ids:
                textbutton arrow:
                    xcenter ax
                    ycenter cal_px(230)
                    padding (cal_px(14), 0)
                    background (Solid("#9a2a1c40") if eid == codex_sel else None)
                    hover_background Solid("#0000002a")
                    text_style "codex_text"
                    text_size cal_px(110)
                    text_color ("#7a2316" if codex_unlocked(eid) else "#b8a890")
                    action Function(codex_select, eid)

        for c, wd in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
            text wd style "codex_text" size cal_px(44) color "#7a2316" xcenter cal_px((CAL_COLS[c] + CAL_COLS[c + 1]) / 2.0) ycenter cal_px((CAL_ROWS[0] + CAL_ROWS[1]) / 2.0)

        for w in range(5):
            for c in range(7):
                $ d = w * 7 + c + 1          # October 1, 1962 was a Monday
                if d <= 31:
                    $ x0 = cal_px(CAL_COLS[c]) + 2
                    $ y0 = cal_px(CAL_ROWS[w + 1]) + 2
                    $ cw = cal_px(CAL_COLS[c + 1]) - cal_px(CAL_COLS[c]) - 4
                    $ ch = cal_px(CAL_ROWS[w + 2]) - cal_px(CAL_ROWS[w + 1]) - 4
                    $ crisis = 16 <= d <= 28
                    $ passed = crisis and persistent.codex_day >= d
                    fixed:
                        pos (x0, y0)
                        xysize (cw, ch)
                        # the thirteen days: a pale red wash, so the span reads at a glance
                        if crisis:
                            add Solid("#b0201a18") xysize (cw, ch)
                        if d in days:
                            $ eid = days[d]
                            $ dopen = codex_unlocked(eid)
                            button:
                                xfill True
                                yfill True
                                hover_background Solid("#0000001e")
                                action Function(codex_select, eid)
                                text str(d) style "codex_text" size cal_px(64) align (.5, .5) color ("#1c120c" if dopen else "#a89880")
                            # days already lived get crossed out in pen; the open file gets circled
                            if passed:
                                add "gui/codex_cal_x.png" fit "contain" xysize (int(cw * 0.78), int(ch * 0.78)) align (.5, .52)
                            if eid == codex_sel:
                                add "gui/codex_cal_ring.png" fit "contain" xysize (int(cw * 1.02), int(ch * 1.02)) align (.5, .5)
                            if dopen and eid in persistent.codex_new:
                                add Solid("#c0392b") xysize (cal_px(16), cal_px(16)) align (.9, .12)
                        else:
                            text str(d) style "codex_text" size cal_px(52) align (.5, .5) color "#b0a08a"

        # legend under the grid
        text "THE THIRTEEN DAYS:  OCT 16 - 28" style "codex_text" size cal_px(40) color "#7a2316" xalign 0.5 ycenter cal_px(CAL_ROWS[-1] + 34)



## ---- DAYS tab: a 1962 desk calendar lying on the same desk (Julián's sheet, 12/11) ----------
## Grid measured on gui/codex_calendar_desk.png (same 1672x941 frame as the codex): the column
## lines lean a little, so each x is interpolated between the top and the bottom of the grid.
define DESK_CAL_IMG = "gui/codex_calendar_desk.png"
define DESK_ROWS = [271, 317, 417, 518, 620, 722, 824]          # header band, then the five weeks
define DESK_COLS_TOP = [238, 412, 584, 758, 928, 1099, 1275, 1447]   # at y = 295
define DESK_COLS_BOT = [226, 406, 580, 758, 932, 1108, 1288, 1467]   # at y = 802

init python:
    def desk_x(i, y):
        f = (y - 295.0) / (802.0 - 295.0)
        return DESK_COLS_TOP[i] + (DESK_COLS_BOT[i] - DESK_COLS_TOP[i]) * f

    def desk_cell(c, r):
        """Cell (column c, grid row r: 0 = weekday band) in bg px: x, y, w, h."""
        y0, y1 = DESK_ROWS[r], DESK_ROWS[r + 1]
        ym = (y0 + y1) / 2.0
        x0, x1 = desk_x(c, ym), desk_x(c + 1, ym)
        return x0, y0, x1 - x0, y1 - y0

screen codex_desk_calendar(ids):
    $ days = codex_calendar_days(ids)

    # blocks clicks to the folder underneath
    button:
        xysize (config.screen_width, config.screen_height)
        background None
        action NullAction()

    add Transform(DESK_CAL_IMG, xysize=(config.screen_width, config.screen_height))

    # back to the tab you came from
    textbutton "< BACK TO FILES":
        action Function(codex_desk_back)
        xpos cz(28)
        ypos cz(24)
        background Solid("#1a120bcc")
        hover_background Solid("#3a2412ee")
        padding (cz(16), cz(8))
        text_style "codex_close_text"
        text_size cz(28)

    # month, with the files before and after October on its sides
    text "OCTOBER 1962" style "codex_text" size cz(64) color "#2a1d14" xcenter cz(840) ycenter cz(220)
    for eid, label, cx in (("CAL-00", "< BEFORE", 470), ("CAL-AFTER", "AFTER >", 1210)):
        if eid in ids:
            textbutton label:
                xcenter cz(cx)
                ycenter cz(222)
                padding (cz(10), cz(4))
                hover_background Solid("#0000001e")
                text_style "codex_text"
                text_size cz(30)
                text_color ("#7a2316" if codex_unlocked(eid) else "#b0a08a")
                action Function(codex_desk_open, eid)

    # weekday band
    for c, wd in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
        $ x, y, w, h = desk_cell(c, 0)
        text wd style "codex_text" size cz(28) color "#7a2316" xcenter cz(x + w / 2.0) ycenter cz(y + h / 2.0)

    # the days: October 1, 1962 was a Monday
    for wk in range(5):
        for c in range(7):
            $ d = wk * 7 + c + 1
            if d <= 31:
                $ x, y, w, h = desk_cell(c, wk + 1)
                $ crisis = 16 <= d <= 28
                $ passed = crisis and persistent.codex_day >= d
                fixed:
                    pos (cz(x + 3), cz(y + 3))
                    xysize (cz(w - 6), cz(h - 6))
                    if crisis:
                        add Solid("#b0201a16")
                    if d in days:
                        $ eid = days[d]
                        $ dopen = codex_unlocked(eid)
                        button:
                            xfill True
                            yfill True
                            hover_background Solid("#00000020")
                            action Function(codex_desk_open, eid)
                            text str(d) style "codex_text" size cz(40) xpos cz(10) ypos cz(4) color ("#1c120c" if dopen else "#a89880")
                        if passed:
                            add "gui/codex_cal_x.png" fit "contain" xysize (cz(h * 0.8), cz(h * 0.8)) align (.55, .6)
                        if eid == codex_sel:
                            add "gui/codex_cal_ring.png" fit "contain" xysize (cz(w * 0.62), cz(h * 0.98)) align (.5, .5)
                        if dopen and eid in persistent.codex_new:
                            add Solid("#c0392b") xysize (cz(12), cz(12)) align (.94, .1)
                    else:
                        text str(d) style "codex_text" size cz(34) xpos cz(10) ypos cz(4) color "#8a7860"

    text "THE THIRTEEN DAYS: OCT 16 - 28   ·   CLICK A DAY TO READ ITS FILE" style "codex_text" size cz(22) color "#7a2316" xcenter cz(840) ycenter cz(846)
