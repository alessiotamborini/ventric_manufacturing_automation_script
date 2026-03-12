# setup.py
import os
import sys
sys.setrecursionlimit(10000)
from setuptools import setup

APP = ['cuffldt.py']                       # your main script
APP_NAME = 'CuffLDT'
ICON = 'CuffLDT.icns'                      # optional generated icon

# helper to include PyQt5 Qt plugins
def find_qt_plugins():
    try:
        import PyQt5
        qt_root = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt')
        plugins_src = os.path.join(qt_root, 'plugins')
        if os.path.isdir(plugins_src):
            # py2app expects resources as a list of (src, dest) pairs
            return [(plugins_src, 'plugins')]
    except Exception:
        pass
    return []

DATA_FILES = find_qt_plugins()

OPTIONS = {
    'argv_emulation': False,
    'packages': ['PyQt5', 'numpy', 'pandas', 'matplotlib', 'openpyxl'],  # include packages you need
    'resources': DATA_FILES,   # include Qt plugins
    'iconfile': ICON,
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.yourcompany.cuffldt'
    },
    # 'optimize': 2,
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)