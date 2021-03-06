# License AGPLv3, see main

import os
from shutil import which
import subprocess

from anki.utils import isMac, isWin, isLin, noBundledLibs
from aqt.qt import *
from aqt.utils import showInfo, openFolder

from .config import gc
from .helper import process_path, osascript_to_args


"""
from aqt.utils
def openFolder(path):
    if isWin:
        subprocess.Popen(["explorer", "file://" + path])
    else:
        with noBundledLibs():
            QDesktopServices.openUrl(QUrl("file://" + path))

"""

def myOpenFolder(path):
    """mod of aqt.utils openFolder"""
    if isWin:
        # subprocess.Popen(["explorer", ])  # original version, doesn't work in 2019-12
        subprocess.Popen('explorer /select, {}'.format("file://"+path))
    elif isMac:
        with noBundledLibs():
            script = """
            tell application \"Finder\"
                activate
                select POSIX file \"{}\"
            end tell
            """.format(path)
            subprocess.Popen(osascript_to_args(script))
    elif isLin:
        us = gc("File Manager in Linux and its args")
        env = os.environ.copy()
        toremove = ['LD_LIBRARY_PATH', 'QT_PLUGIN_PATH', 'QML2_IMPORT_PATH']
        for e in toremove:
            env.pop(e, None)
        if us:
            us.append("file://"+path)
            subprocess.Popen(us, env=env)
        else:
            if which("dolphin") is not None:
                subprocess.Popen(["dolphin", "--select", "file://"+path], env=env)
            elif which("nautilus") is not None:
                # caja 1.20 doesn't have "--select"
                subprocess.Popen(["nautilus", "--select", "file://"+path], env=env)
            else:
                filename = os.path.dirname(path)
                showInfo("The file manager will show your media folder. The name of the file you "
                        "clicked is:\n\n{}".format(filename))
                dirname = os.path.dirname(path)
                QDesktopServices.openUrl(QUrl("file://" + dirname))


def show_in_filemanager(filename):
    _, fileabspath, _, _ = process_path(filename)
    # openFolder(fileabspath)
    # BUT doens't help: mp3 files are opened in the default audio player, images in imageviewer
    # I had this problem in 2019 and it still persists in 2020-07.
    # BUT in 2019-05 (in KDE) openFolder doesn't work for me in the prebuilt/compiled version
    # from Ankiweb. If I use runanki with my local PyQt it works
    # I tried in 2.1.12 without add-ons and in Preferences -> Backups I clicked
    # on "Open Backup Folder". I got this:
    # qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
    # This application failed to start because no Qt platform plugin could be initialized.
    # Reinstalling the application may fix this problem.
    # Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc,
    # wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, xcb.
    # /usr/bin/xdg-open: line 613:  8817 Aborted  (core dumped) kde-open${KDE_SESSION_VERSION} "$1"
    myOpenFolder(fileabspath)
