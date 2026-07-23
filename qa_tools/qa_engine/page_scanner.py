from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List
import shiboken6
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QWidget, QFrame, QListWidget, QPushButton, QStackedWidget, QTableWidget, QToolButton

from qa_tools.qa_engine.screenshot import ScreenshotCapture


class PageScanner:
    def __init__(self, app: QApplication, window: QWidget):
        self.app = app
        self.window = window
        self.screenshot = ScreenshotCapture(app)
        self._screenshot_hashes: Dict[str, str] = {}

    def _widget_metadata(self, widget: QWidget | None) -> Dict[str, Any] | None:
        if widget is None:
            return None
        try:
            geometry = widget.geometry()
            return {
                "class": widget.__class__.__name__,
                "object_name": widget.objectName(),
                "window_title": widget.windowTitle() if hasattr(widget, "windowTitle") else None,
                "visible": widget.isVisible(),
                "enabled": widget.isEnabled() if hasattr(widget, "isEnabled") else None,
                "geometry": {
                    "x": geometry.x(),
                    "y": geometry.y(),
                    "width": geometry.width(),
                    "height": geometry.height(),
                },
            }
        except Exception:
            return {
                "class": widget.__class__.__name__,
                "object_name": widget.objectName(),
            }

    def _capture_label(self, label: str, widget: QWidget | None = None) -> Dict[str, Any] | None:
        self.app.processEvents()
        try:
            target = widget or self.window
            path = self.screenshot.capture(label, widget=target)
            image_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if image_hash in self._screenshot_hashes:
                return None
            self._screenshot_hashes[image_hash] = str(path)
            result: Dict[str, Any] = {
                "label": label,
                "path": str(path),
                "captured": True,
            }
            metadata = self._widget_metadata(target)
            if metadata is not None:
                result["widget_info"] = metadata
            return result
        except Exception as exc:
            result = {
                "label": label,
                "captured": False,
                "error": str(exc),
            }
            metadata = self._widget_metadata(widget or self.window)
            if metadata is not None:
                result["widget_info"] = metadata
            return result

    def _apply_debug_overlay(self, enable: bool) -> bool:
        manager = getattr(self.window, "layout_debug_manager", None)
        if manager is None:
            return False
        try:
            if enable:
                manager.enable()
                if not manager.labels_enabled:
                    manager.toggle_labels()
            else:
                manager.disable()
            self.app.processEvents()
            time.sleep(0.2)
            return True
        except Exception:
            return False

    def _capture_sidebar_pages(self, suffix: str = "") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        sidebar = getattr(self.window, "sidebar_column", None)
        nav = getattr(self.window, "navigation_controller", None)
        if sidebar is None or not hasattr(sidebar, "list_widget"):
            return results

        previous_widget = None
        if nav is not None and hasattr(nav, "page_stack") and hasattr(self.window, "app_page"):
            try:
                previous_widget = nav.page_stack.currentWidget()
                nav.page_stack.setCurrentWidget(self.window.app_page)
                self.app.processEvents()
                time.sleep(0.15)
            except Exception:
                previous_widget = None

        nav_list: QListWidget = sidebar.list_widget
        for index in range(nav_list.count()):
            item = nav_list.item(index)
            if item is None:
                continue
            nav_list.setCurrentRow(index)
            self.app.processEvents()
            time.sleep(0.15)
            label = item.text().strip().lower().replace(" ", "_")
            captured = self._capture_label(f"sidebar_{index}_{label}{suffix}")
            if captured is not None:
                results.append(captured)

        if previous_widget is not None:
            try:
                nav.page_stack.setCurrentWidget(previous_widget)
                self.app.processEvents()
            except Exception:
                pass

        return results

    def _capture_admin_sidebar_pages(self, suffix: str = "") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        admin_page = getattr(self.window, "admin_page", None)
        nav = getattr(self.window, "navigation_controller", None)
        if admin_page is None or nav is None or not hasattr(admin_page, "nav_list"):
            return results

        previous_index = None
        try:
            previous_index = nav.page_stack.currentIndex()
        except Exception:
            previous_index = None

        try:
            nav.on_authenticated("admin", "superadmin")
            self.app.processEvents()
            time.sleep(0.15)
        except Exception:
            pass

        current_row = admin_page.nav_list.currentRow()
        for index in range(admin_page.nav_list.count()):
            item = admin_page.nav_list.item(index)
            if item is None:
                continue
            admin_page.nav_list.setCurrentRow(index)
            self.app.processEvents()
            time.sleep(0.15)
            label = item.text().strip().lower().replace(" ", "_")
            captured = self._capture_label(f"admin_sidebar_{index}_{label}{suffix}")
            if captured is not None:
                results.append(captured)

        try:
            admin_page.nav_list.setCurrentRow(current_row)
            self.app.processEvents()
        except Exception:
            pass

        if previous_index is not None:
            try:
                nav.page_stack.setCurrentIndex(previous_index)
                self.app.processEvents()
            except Exception:
                pass

        return results

    def _capture_stacked_widget_pages(self, suffix: str = "") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        workspace_stack = getattr(self.window, "workspace_stack", None)
        nav = getattr(self.window, "navigation_controller", None)
        if not isinstance(workspace_stack, QStackedWidget):
            return results

        previous_page = None
        previous_sidebar_row = None
        try:
            if nav is not None and hasattr(nav, "page_stack") and hasattr(self.window, "app_page"):
                previous_page = nav.page_stack.currentWidget()
                nav.page_stack.setCurrentWidget(self.window.app_page)
                self.app.processEvents()
                time.sleep(0.15)
                sidebar = getattr(self.window, "sidebar_column", None)
                if sidebar is not None and hasattr(sidebar, "list_widget"):
                    previous_sidebar_row = sidebar.list_widget.currentRow()
        except Exception:
            previous_page = None
            previous_sidebar_row = None

        current_index = workspace_stack.currentIndex()
        prefix = workspace_stack.objectName() or "workspace_stack"
        prefix = prefix.lower().replace(" ", "_")
        for index in range(workspace_stack.count()):
            try:
                if nav is not None and hasattr(nav, "on_sidebar_changed"):
                    nav.on_sidebar_changed(index)
                else:
                    workspace_stack.setCurrentIndex(index)
                self.app.processEvents()
                time.sleep(0.15)
            except Exception:
                pass

            page = workspace_stack.widget(index)
            label = f"{prefix}_{index}"
            if page is not None and hasattr(page, "objectName"):
                name = page.objectName().strip()
                if name:
                    label = f"{prefix}_{name.lower().replace(' ', '_')}"
            captured = self._capture_label(f"{label}{suffix}")
            if captured is not None:
                results.append(captured)

        try:
            workspace_stack.setCurrentIndex(current_index)
            self.app.processEvents()
            if previous_sidebar_row is not None and getattr(self.window, "sidebar_column", None) is not None:
                sidebar = getattr(self.window, "sidebar_column")
                if hasattr(sidebar, "list_widget"):
                    sidebar.list_widget.setCurrentRow(previous_sidebar_row)
                    self.app.processEvents()
        except Exception:
            pass

        if previous_page is not None:
            try:
                nav.page_stack.setCurrentWidget(previous_page)
                self.app.processEvents()
            except Exception:
                pass

        return results

    def _capture_auth_pages(self, suffix: str = "") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        nav = getattr(self.window, "navigation_controller", None)
        if nav is None:
            return results

        login_page = getattr(self.window, "login_page", None)
        if login_page is None or not hasattr(login_page, "stack"):
            return results

        initial_widget = None
        if nav is not None and hasattr(nav, "page_stack"):
            try:
                initial_widget = nav.page_stack.currentWidget()
            except Exception:
                initial_widget = None

        should_capture_login = True
        if initial_widget is login_page:
            should_capture_login = False

        should_capture_login = True
        if initial_widget is login_page:
            should_capture_login = False

        if should_capture_login:
            try:
                nav.show_login()
                self.app.processEvents()
                time.sleep(0.15)
                captured = self._capture_label(f"login_page{suffix}")
                if captured is not None:
                    results.append(captured)
            except Exception as exc:
                results.append({"label": f"login_page{suffix}", "error": str(exc)})

        try:
            login_page.stack.setCurrentIndex(1)
            self.app.processEvents()
            time.sleep(0.15)
            captured = self._capture_label(f"login_register_page{suffix}")
            if captured is not None:
                results.append(captured)
        except Exception as exc:
            results.append({"label": f"login_register_page{suffix}", "error": str(exc)})
        finally:
            try:
                login_page.stack.setCurrentIndex(0)
                self.app.processEvents()
            except Exception:
                pass

        return results

    def _is_safe_dialog_button(self, button: QPushButton) -> bool:
        object_name = button.objectName().strip().lower()
        if "note" in object_name:
            return False

        text = button.text().strip().lower()
        if not text:
            return False

        unsafe_keywords = [
            "delete",
            "remove",
            "logout",
            "sign out",
            "exit",
            "cancel",
            "discard",
            "close",
            "deny",
            "decline",
            "no",
            "stop",
            "clear",
            "reset",
            "save",
            "submit",
            "confirm",
            "ok",
            "yes",
            "apply",
            "download",
            "upload",
            "export",
            "import",
        ]
        for keyword in unsafe_keywords:
            if keyword in text:
                return False

        safe_prefixes = ["create", "new", "open", "show", "view", "details", "edit"]
        for prefix in safe_prefixes:
            if text.startswith(prefix) or prefix in text:
                return True

        return False

    def _visible_dialogs(self) -> List[QDialog]:
        return [w for w in self.app.topLevelWidgets() if isinstance(w, QDialog) and shiboken6.isValid(w)]

    def _trigger_employee_table_dialog(self, table: QTableWidget) -> bool:
        try:
            parent = table.parent()
            while parent is not None:
                if hasattr(parent, "_show_details") and getattr(parent, "table", None) is table:
                    employee = table.get_current_employee(0)
                    if employee is not None:
                        parent._show_details(employee)
                        return True
                parent = parent.parent()
        except Exception:
            return False

        try:
            table.setCurrentCell(0, 0)
            table.cellDoubleClicked.emit(0, 0)
            return True
        except Exception:
            return False

    def _close_dialog(self, dialog: QDialog) -> None:
        try:
            dialog.reject()
        except Exception:
            try:
                dialog.close()
            except Exception:
                pass

    def _capture_dialogs_from_buttons(self, suffix: str = "") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_labels: set[str] = set()

        def capture_dialog(dialog: QDialog) -> None:
            name = dialog.objectName().strip().lower().replace(" ", "_") or dialog.__class__.__name__.lower()
            label = f"dialog_{name}{suffix}"
            if label in seen_labels:
                self._close_dialog(dialog)
                return
            captured = self._capture_label(label, widget=dialog)
            if captured is not None:
                results.append(captured)
                seen_labels.add(label)
            self._close_dialog(dialog)

        for widget in self.app.allWidgets():
            if not shiboken6.isValid(widget):
                continue

            perform_click = None
            if isinstance(widget, (QPushButton, QToolButton)):
                if not widget.isVisible() or not widget.isEnabled():
                    continue
                if not self._is_safe_dialog_button(widget):
                    continue
                perform_click = lambda target=widget: QTest.mouseClick(target, Qt.LeftButton)
            elif isinstance(widget, QTableWidget):
                if not widget.isVisible() or widget.rowCount() == 0:
                    continue
                perform_click = lambda target=widget: self._trigger_employee_table_dialog(target)
            else:
                continue

            visible_before = set(self._visible_dialogs())
            perform_click()
            self.app.processEvents()
            time.sleep(0.25)

            for dialog in self._visible_dialogs():
                if dialog in visible_before:
                    continue
                capture_dialog(dialog)

        return results

    def _capture_non_dialog_popups(self, suffix: str = "") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_labels: set[str] = set()
        for widget in self.app.topLevelWidgets():
            if widget is self.window:
                continue
            if not shiboken6.isValid(widget):
                continue
            if not widget.isVisible() or not widget.size().isValid():
                continue
            if isinstance(widget, QDialog):
                continue
            name = widget.objectName().strip().lower().replace(" ", "_") or widget.__class__.__name__.lower()
            label = f"popup_{name}{suffix}"
            if label in seen_labels:
                continue
            captured = self._capture_label(label, widget=widget)
            if captured is not None:
                captured["capture_type"] = "popup"
                results.append(captured)
                seen_labels.add(label)
        return results

    def _capture_dialogs(self, suffix: str = "") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_labels: set[str] = set()

        def add_result(capture: Dict[str, Any] | None) -> None:
            if capture is None:
                return
            label = capture.get("label")
            if label in seen_labels:
                return
            if label is not None:
                seen_labels.add(label)
            capture["capture_type"] = "dialog"
            results.append(capture)

        for widget in self.app.topLevelWidgets():
            if isinstance(widget, QDialog) and shiboken6.isValid(widget) and widget.isVisible():
                name = widget.objectName().strip().lower().replace(" ", "_") or widget.__class__.__name__.lower()
                label = f"dialog_{name}{suffix}"
                captured = self._capture_label(label, widget=widget)
                add_result(captured)

        nav = getattr(self.window, "navigation_controller", None)
        current_page = None
        if nav is not None and hasattr(nav, "page_stack"):
            try:
                current_page = nav.page_stack.currentWidget()
            except Exception:
                current_page = None

        def capture_on_page(show_page):
            try:
                show_page()
                self.app.processEvents()
                time.sleep(0.15)
                return self._capture_dialogs_from_buttons(suffix=suffix)
            except Exception:
                return []

        sidebar = getattr(self.window, "sidebar_column", None)
        sidebar_row = None
        if sidebar is not None and hasattr(sidebar, "list_widget"):
            try:
                sidebar_row = sidebar.list_widget.currentRow()
            except Exception:
                sidebar_row = None

        if nav is not None:
            if hasattr(self.window, "admin_page"):
                for item in capture_on_page(lambda: nav.on_authenticated("admin", "superadmin")):
                    add_result(item)
            if hasattr(self.window, "app_page") and hasattr(nav, "page_stack"):
                for item in capture_on_page(lambda: nav.page_stack.setCurrentWidget(self.window.app_page)):
                    add_result(item)

        if sidebar is not None and hasattr(sidebar, "list_widget"):
            for index in range(sidebar.list_widget.count()):
                try:
                    sidebar.list_widget.setCurrentRow(index)
                    self.app.processEvents()
                    time.sleep(0.12)
                    for item in self._capture_dialogs_from_buttons(suffix=suffix):
                        add_result(item)
                except Exception:
                    continue

            if sidebar_row is not None:
                try:
                    sidebar.list_widget.setCurrentRow(sidebar_row)
                    self.app.processEvents()
                except Exception:
                    pass

        for item in self._capture_dialogs_from_buttons(suffix=suffix):
            add_result(item)
        for item in self._capture_non_dialog_popups(suffix=suffix):
            add_result(item)

        if nav is not None and current_page is not None:
            try:
                nav.page_stack.setCurrentWidget(current_page)
                self.app.processEvents()
            except Exception:
                pass

        return results

    def scan_all_pages(self, debug: bool = False) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        suffix = "_debug" if debug else ""
        if debug:
            self._apply_debug_overlay(True)

        results.append(self._capture_label(f"startup{suffix}"))
        results.extend(self._capture_sidebar_pages(suffix=suffix))
        results.extend(self._capture_admin_sidebar_pages(suffix=suffix))
        results.extend(self._capture_stacked_widget_pages(suffix=suffix))
        results.extend(self._capture_auth_pages(suffix=suffix))
        results.extend(self._capture_dialogs(suffix=suffix))

        if debug:
            self._apply_debug_overlay(False)
        return results
