# License AGPLv3, see main

import re
import os
import datetime
import itertools

from bs4 import BeautifulSoup

import aqt
from aqt import mw
from aqt.utils import getText, tooltip, showInfo
# from aqt.addcards import AddCards
# from aqt.editcurrent import EditCurrent

from .config import gc


def get_unused_new_name(mediafolder, base, ext):
    # getOnlyText doesn't offer default text
    text, r = getText("New Name:", None, None, None, base)
    if not r:
        return False
    else:
        newfilename = text + ext
        newpath = os.path.join(mediafolder, newfilename)
        if os.path.exists(newpath):
            tooltip('Error. Chosen filename already exists. Try again.')
            newfilename = get_unused_new_name(mediafolder, base + "_1", ext)
        return newfilename


def process_path(filename):
    mediafolder = os.path.join(mw.pm.profileFolder(), "collection.media")
    fileabspath = os.path.join(mediafolder, filename)
    split = os.path.splitext(filename)
    base = split[0]
    ext = split[1]
    return mediafolder, fileabspath, base, ext


def has_one_sound(text):
    # video and audio both have [sound:]
    # [sound:some file name.mp3]
    sounds = re.findall(r'\[sound:(.*?)\]', text)
    if len(sounds) == 0:
        return False
    elif len(sounds) > 1:
        if gc("sound__show_tooltip_two_soundfiles_selected"):
            tooltip("two sound files selected")
        return False
    else:
        return sounds[0]


def same_filename_in_just_one_editor(fname, type):
    try:    # add-on "Opening the same window multiple time"
            # so far I update only the current editor. If the same note is in other editors
            # these don't get updated.
        aqt.dialogs._openDialogs
    except:
        # only one browser allowed so it shouldn't be a problem?
        # builtin = aqt.dialogs._dialogs
        return True
    else:
        # about add-on "Opening the same window multiple time"
        windows = 0
        relevant = (aqt.browser.Browser, aqt.addcards.AddCards,
                    aqt.editcurrent.EditCurrent)
        for i in aqt.dialogs._openDialogs:
            if isinstance(i, relevant):
                try:
                    n = i.editor.note
                except:
                    pass
                else:
                    # browser can have editor that has note = None
                    if n:
                        if type == "image":
                            s = ' src="' + fname    # not perfect, sometimes there's   img src='
                        else:
                            s = '[sound:' + fname
                        for f in i.editor.note.fields:
                            if s in f:
                                windows += 1
                                break
        if windows > 1:
            str_ = "same note open in multiple editors (AddCards, Browser, EditCurrent).\n" + \
                   "Renaming in one editor doesn't update the other editors.\n " + \
                   "Aborting ...\n" + \
                   "To continue close another editor and try again."
            showInfo(str_)
            return False
        else:
            return True


def replace_sound_in_editor_and_reload(editor, searchstring, replacestring, field):
    for i, c in enumerate(editor.note.fields):
        new = c.replace(searchstring, replacestring)
        if c != new and not field:
            field = i
        editor.note.fields[i] = new
    editor.note.flush()
    if field:
        editor.loadNote(focusTo=field)
    else:
        editor.loadNote()


def field_entry_duplicate_img(html, oldname, newname):
    soup = BeautifulSoup(html, "html.parser")
    images = soup.findAll('img')
    for image in images:
        if image['src'] == oldname:
            new_tag = soup.new_tag("img", src=newname)
            image.insert_after(new_tag)
    return str(soup)


def field_entry_rename_img(html, oldname, newname):
    soup = BeautifulSoup(html, "html.parser")
    images = soup.findAll('img')
    for image in images:
        if image['src'] == oldname:
            image['src'] = newname
    return str(soup)


def replace_img_in_editor_and_reload(editor, oldname, newname, action, field):
    """bs4 is needed to handle tags like '<img draggable="false" src="past'"""
    changed = 0
    for i, c in enumerate(editor.note.fields):
        if oldname in c:
            changed += 1
            if action == "duplicate":
                new = field_entry_duplicate_img(c, oldname, newname)
            elif action == "rename":
                new = field_entry_rename_img(c, oldname, newname)
            else:
                print('Error')
            if c != new and not field:
                field = i
            editor.note.fields[i] = new
    if not changed == 0:
        editor.note.flush()
        if field:
            editor.loadNote(focusTo=field)
        else:
            editor.loadNote()


def time_now_fmt():
    CurrentDT = datetime.datetime.now()
    return CurrentDT.strftime("%Y-%m-%d__%H-%M-%S")


def osascript_to_args(script: str):
    commands = [("-e", l.strip()) for l in script.split('\n') if l.strip() != '']
    args = list(itertools.chain(*commands))
    return ["osascript"] + args
