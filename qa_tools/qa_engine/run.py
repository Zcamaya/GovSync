from __future__ import annotations

import sys
import traceback
from pathlib import Path

import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa_tools.qa_engine.accessibility import AccessibilityInspector
from qa_tools.qa_engine.config import QA_OUTPUT_DIR, REPORTS_DIR, SCREENSHOT_DIR, ensure_env
from qa_tools.qa_engine.crawler import UiCrawler
from qa_tools.qa_engine.dpi_tester import DpiTester
from qa_tools.qa_engine.forms import FormInspector
from qa_tools.qa_engine.layout_validator import LayoutValidator
from qa_tools.qa_engine.markdown_report import MarkdownReportBuilder
from qa_tools.qa_engine.navigation import NavigationInspector
from qa_tools.qa_engine.page_scanner import PageScanner
from qa_tools.qa_engine.performance import PerformanceInspector
from qa_tools.qa_engine.report import ReportWriter
from qa_tools.qa_engine.responsiveness import ResponsivenessInspector
from qa_tools.qa_engine.screenshot import ScreenshotCapture
from qa_tools.qa_engine.table_tests import TableInspector
from qa_tools.qa_engine.text_visibility import TextVisibilityInspector
from qa_tools.qa_engine.visual_analysis import VisualAnalyzer
from qa_tools.qa_engine.widget_tree import WidgetTreeAnalyzer
from qa_tools.qa_engine.visual_diff import compare_images


def _status(message: str) -> None:
    print(f"QA engine: {message}", flush=True)


def main() -> int:
    _status("starting QA scan")
    _status("ensuring offscreen environment")
    ensure_env()
    _status("creating Qt application")
    app = QApplication.instance() or QApplication([])

    # Try to register a common system font so offscreen screenshots render text.
    def _try_register_font():
        # common Windows font locations
        candidates = []
        windir = os.environ.get("WINDIR")
        if windir:
            font_dir = os.path.join(windir, "Fonts")
            # scan for likely font files (Segoe, Arial)
            try:
                for fn in os.listdir(font_dir):
                    lower = fn.lower()
                    if "segoe" in lower or "arial" in lower or "dejavu" in lower or "liberation" in lower:
                        candidates.append(os.path.join(font_dir, fn))
            except Exception:
                pass
        # fallback: try system-wide font dirs
        candidates += ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]

        for path in candidates:
            try:
                if path and os.path.exists(path):
                    QFontDatabase.addApplicationFont(path)
                    return True
            except Exception:
                continue
        return False

    _try_register_font()

    try:
        _status("instantiating GovSync application")
        from core.application import GovSyncApplication

        application = GovSyncApplication()
        _status("creating main window")
        window = application.create_main_window()
        _status("showing application window")
        window.show()
        app.processEvents()
        # If QA_LAYOUT_DEBUG environment variable is set, enable the built-in layout debug overlay
        if os.environ.get("QA_LAYOUT_DEBUG", "0") in ("1", "true", "True"):
            try:
                if getattr(application, "layout_debug_manager", None) is not None:
                    application.layout_debug_manager.enable()
                    app.processEvents()
                    # Optionally enable label overlays when QA_LAYOUT_LABELS=1
                    if os.environ.get("QA_LAYOUT_LABELS", "0") in ("1", "true", "True"):
                        try:
                            application.layout_debug_manager.toggle_labels()
                            app.processEvents()
                        except Exception:
                            pass
            except Exception:
                pass
    except Exception as exc:
        print(f"QA engine could not instantiate application UI: {exc}")
        traceback.print_exc()
        return 1

    _status("initializing QA inspectors")
    crawler = UiCrawler(app)
    navigation = NavigationInspector(app)
    widget_tree = WidgetTreeAnalyzer(app)
    layout_validator = LayoutValidator(app)
    screenshot_capture = ScreenshotCapture(app)
    page_scanner = PageScanner(app, window)
    accessibility = AccessibilityInspector(app)
    text_visibility = TextVisibilityInspector(app)
    performance = PerformanceInspector(app)
    responsiveness = ResponsivenessInspector(app)
    forms = FormInspector(app)
    tables = TableInspector(app)
    visual = VisualAnalyzer(app)
    dpi_tester = DpiTester(app)
    report_writer = ReportWriter()
    markdown_builder = MarkdownReportBuilder()

    try:
        _status("discovering UI snapshot")
        snapshot = crawler.discover()
        _status("discovering navigation map")
        navigation_map = navigation.discover_navigation()
        _status("collecting widget tree")
        widget_tree_data = widget_tree.collect_widget_tree()
        _status("validating layout")
        layout_issues = layout_validator.validate()
        _status("inspecting accessibility")
        accessibility_data = accessibility.inspect()
        _status("inspecting performance")
        performance_data = performance.inspect()
        _status("inspecting responsiveness")
        responsiveness_data = responsiveness.inspect()
        _status("inspecting forms")
        form_data = forms.inspect()
        _status("inspecting tables")
        table_data = tables.inspect()
        _status("inspecting visuals")
        visual_data = visual.inspect()
        _status("running DPI inspection")
        dpi_data = dpi_tester.inspect()

        if app.topLevelWidgets():
            try:
                _status("capturing startup screenshot")
                screenshot_capture.capture("startup")
            except Exception as exc:
                print(f"QA engine: screenshot capture skipped: {exc}", flush=True)

        _status("scanning page captures")
        page_capture_results = page_scanner.scan_all_pages()
        _status("scanning debug page captures")
        debug_capture_results = page_scanner.scan_all_pages(debug=True)
        _status("inspecting text visibility")
        text_visibility_data = text_visibility.inspect()

        # If a baseline screenshot exists, attempt a visual diff to exercise comparator
        try:
            baseline = Path(SCREENSHOT_DIR) / "baseline" / "startup.png"
            current = Path(SCREENSHOT_DIR) / "startup.png"
            diff_out = Path(SCREENSHOT_DIR) / "diff" / "startup.diff.png"
            if baseline.exists() and current.exists():
                identical = compare_images(baseline, current, out_path=diff_out)
                print(f"Visual diff identical: {identical}")
        except Exception:
            pass

        _status("writing JSON reports")
        report_writer.write_json("crawler_snapshot", snapshot)
        report_writer.write_json("navigation_map", navigation_map)
        report_writer.write_json("widget_tree", widget_tree_data)
        report_writer.write_json("layout_issues", layout_issues)
        report_writer.write_json("accessibility", accessibility_data)
        report_writer.write_json("text_visibility", text_visibility_data)
        report_writer.write_json("page_capture", page_capture_results)
        report_writer.write_json("page_capture_debug", debug_capture_results)
        report_writer.write_json("performance", performance_data)
        report_writer.write_json("responsiveness", responsiveness_data)
        report_writer.write_json("forms", form_data)
        report_writer.write_json("tables", table_data)
        report_writer.write_json("visual_analysis", visual_data)
        report_writer.write_json("dpi_results", dpi_data)

        _status("building markdown summary")
        markdown = markdown_builder.build(
            snapshot=snapshot,
            navigation_map=navigation_map,
            widget_tree=widget_tree_data,
            layout_issues=layout_issues,
            accessibility=accessibility_data,
            performance=performance_data,
            responsiveness=responsiveness_data,
            forms=form_data,
            tables=table_data,
            visual=visual_data,
            dpi=dpi_data,
        )
        _status("writing markdown reports")
        report_writer.write_markdown("UI_AUDIT_REPORT", markdown)
        report_writer.write_markdown("LAYOUT_REPORT", "# Layout Report\n\n" + markdown_builder.format_layout_summary(layout_issues))
        report_writer.write_markdown("ACCESSIBILITY_REPORT", "# Accessibility Report\n\n" + markdown_builder.format_accessibility_summary(accessibility_data))
        report_writer.write_markdown("TEXT_VISIBILITY_REPORT", "# Text Visibility Report\n\n" + markdown_builder.format_text_visibility_summary(text_visibility_data))
        report_writer.write_markdown("PAGE_CAPTURE_REPORT", "# Page Capture Report\n\n" + markdown_builder.format_page_capture_summary(page_capture_results))
        report_writer.write_markdown("PAGE_CAPTURE_DEBUG_REPORT", "# Page Capture Debug Report\n\n" + markdown_builder.format_page_capture_summary(debug_capture_results))
        report_writer.write_markdown("PERFORMANCE_REPORT", "# Performance Report\n\n" + markdown_builder.format_performance_summary(performance_data))
        report_writer.write_markdown("FIX_PRIORITY", "# Fix Priority\n\n" + markdown_builder.format_fix_priority(layout_issues, accessibility_data, performance_data))
        report_writer.write_markdown("WIDGET_TREE", "# Widget Tree\n\n" + markdown_builder.format_widget_tree(widget_tree_data))
        report_writer.write_markdown("NAVIGATION_MAP", "# Navigation Map\n\n" + markdown_builder.format_navigation_map(navigation_map))
        report_writer.write_markdown("SCREENSHOT_INDEX", "# Screenshot Index\n\n- Screenshots are stored in " + str(SCREENSHOT_DIR.relative_to(QA_OUTPUT_DIR)) + "\n")

        html_report = markdown_builder.to_html(markdown)
        (REPORTS_DIR / "VISUAL_REPORT.html").write_text(html_report, encoding="utf-8")

        _status("QA engine completed successfully")
        return 0
    except Exception as exc:
        print(f"QA engine: failure at stage {exc}", flush=True)
        traceback.print_exc()
        return 1


def _pause_for_user() -> None:
    # Only pause for interactive input if explicitly requested via env var.
    if os.environ.get("QA_WAIT_FOR_INPUT", "0") in ("1", "true", "True") and sys.stdin.isatty():
        try:
            input("\nQA engine finished. Press Enter to exit... ")
        except EOFError:
            pass


if __name__ == "__main__":
    exit_code = main()
    if exit_code == 0:
        _pause_for_user()
    else:
        _pause_for_user()
    raise SystemExit(exit_code)
