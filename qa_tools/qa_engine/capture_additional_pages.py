from pathlib import Path
import os
import time

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in __import__('sys').path:
    __import__('sys').path.insert(0, str(ROOT))

from qa_tools.qa_engine.screenshot import ScreenshotCapture
from qa_tools.qa_engine.config import ensure_env, SCREENSHOT_DIR


def _try_register_font():
    candidates = []
    windir = os.environ.get("WINDIR")
    if windir:
        font_dir = os.path.join(windir, "Fonts")
        try:
            for fn in os.listdir(font_dir):
                lower = fn.lower()
                if "segoe" in lower or "arial" in lower or "dejavu" in lower or "liberation" in lower:
                    candidates.append(os.path.join(font_dir, fn))
        except Exception:
            pass
    candidates += ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    for path in candidates:
        try:
            if path and os.path.exists(path):
                print('Found font', path)
                return True
        except Exception:
            continue
    return False


def enable_debug_overlay(application, app):
    manager = getattr(application, "layout_debug_manager", None)
    if manager is None:
        return False
    try:
        manager.enable()
        if not manager.labels_enabled:
            manager.toggle_labels()
        app.processEvents()
        time.sleep(0.2)
        return True
    except Exception as exc:
        print('Could not enable debug overlay', exc)
        return False


def capture_with_suffix(sc, label, suffix=""):
    name = f"{label}{suffix}"
    try:
        sc.capture(name)
        print('Captured', name)
    except Exception as exc:
        print('Failed to capture', name, exc)


def main():
    ensure_env()
    print('ensure_env set')
    _try_register_font()
    print('font registration attempted')
    app = QApplication.instance() or QApplication([])
    print('QApplication created')

    from core.application import GovSyncApplication
    application = GovSyncApplication()
    print('GovSyncApplication instantiated')
    window = application.create_main_window()
    window.show()
    app.processEvents()
    print('Main window created and shown')
    sc = ScreenshotCapture(app)

    time.sleep(0.2)
    app.processEvents()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    capture_with_suffix(sc, 'startup')

    sidebar = getattr(window, 'sidebar_column', None)

    def capture_sidebar_index(idx, name, suffix=""):
        try:
            if sidebar is not None and hasattr(sidebar, 'list_widget'):
                sidebar.list_widget.setCurrentRow(idx)
                app.processEvents()
                time.sleep(0.15)
            capture_with_suffix(sc, name, suffix)
        except Exception as exc:
            print('Failed to capture', name, exc)

    capture_sidebar_index(3, 'philhealth_panel')
    capture_sidebar_index(5, 'sss_panel')

    nav = getattr(window, 'navigation_controller', None)
    if nav is not None:
        try:
            nav.on_authenticated('admin', 'superadmin')
            app.processEvents()
            time.sleep(0.15)
            capture_with_suffix(sc, 'admin_page')
            nav.show_login()
            app.processEvents()
        except Exception as exc:
            print('admin capture failed', exc)

    if nav is not None:
        try:
            nav.show_login()
            app.processEvents()
            time.sleep(0.15)
            capture_with_suffix(sc, 'login_page')
        except Exception as exc:
            print('login capture failed', exc)

    print('Capturing debug-layout versions...')
    if enable_debug_overlay(application, app):
        capture_with_suffix(sc, 'startup', '_debug')
        capture_sidebar_index(3, 'philhealth_panel', '_debug')
        capture_sidebar_index(5, 'sss_panel', '_debug')
        if nav is not None:
            try:
                nav.on_authenticated('admin', 'superadmin')
                app.processEvents()
                time.sleep(0.15)
                capture_with_suffix(sc, 'admin_page', '_debug')
                nav.show_login()
                app.processEvents()
            except Exception as exc:
                print('admin debug capture failed', exc)
            try:
                nav.show_login()
                app.processEvents()
                time.sleep(0.15)
                capture_with_suffix(sc, 'login_page', '_debug')
            except Exception as exc:
                print('login debug capture failed', exc)

    print('Done')


if __name__ == '__main__':
    main()
