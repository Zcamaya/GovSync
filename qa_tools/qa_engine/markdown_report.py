from __future__ import annotations

from typing import Any, Dict, List


class MarkdownReportBuilder:
    def build(self, **kwargs: Any) -> str:
        parts: List[str] = ["# UI Audit Report\n"]
        if "snapshot" in kwargs:
            parts.append("## Snapshot\n")
            parts.append(f"Windows: {len(kwargs['snapshot'].get('windows', []))}\n")
        return "\n".join(parts)

    def format_layout_summary(self, layout_issues: List[Dict[str, Any]]) -> str:
        if not layout_issues:
            return "No layout issues found."
        return "\n".join([f"- {i['type']}: {i.get('object_name', i.get('widget'))}" for i in layout_issues])

    def format_accessibility_summary(self, accessibility_data: List[Dict[str, Any]]) -> str:
        if not accessibility_data:
            return "No accessibility findings."
        return "\n".join([f"- {d.get('type')}: {d.get('object_name', d.get('text',''))}" for d in accessibility_data])

    def format_text_visibility_summary(self, text_data: List[Dict[str, Any]]) -> str:
        if not text_data:
            return "No text visibility issues found."
        return "\n".join([f"- {d.get('type')} {d.get('object_name')}: {d.get('issue')}" for d in text_data])

    def _page_capture_category(self, label: str) -> str:
        normalized = label.replace("_debug", "")
        if normalized.startswith("startup"):
            return "Startup"
        if normalized.startswith("sidebar_"):
            return "Main sidebar"
        if normalized.startswith("admin_sidebar_"):
            return "Admin sidebar"
        if normalized.startswith("login_register_page"):
            return "Auth / account creation"
        if normalized.startswith("login_page"):
            return "Auth / login"
        if normalized.startswith("admin_page"):
            return "Admin landing"
        if normalized.startswith("dialog_"):
            return "Dialog boxes"
        if normalized.startswith("workspacestack_") or normalized.startswith("workspace_") or normalized.startswith("stackedwidget_"):
            return "Stacked pages"
        return "Other pages"

    def format_page_capture_summary(self, capture_data: List[Dict[str, Any]]) -> str:
        if not capture_data:
            return "No page capture data collected."

        grouped: Dict[str, List[Dict[str, Any]]] = {}
        order = [
            "Startup",
            "Main sidebar",
            "Admin sidebar",
            "Auth / login",
            "Auth / account creation",
            "Admin landing",
            "Stacked pages",
            "Other pages",
        ]
        for item in capture_data:
            label = item.get('label', '')
            category = self._page_capture_category(label)
            grouped.setdefault(category, []).append(item)

        sections: List[str] = []
        for category in order:
            items = grouped.get(category)
            if not items:
                continue
            sections.append(f"## {category}")
            for item in items:
                label = item.get('label')
                if item.get('captured'):
                    line = f"- {label}: captured at {item.get('path')}"
                    widget_info = item.get('widget_info')
                    if widget_info is not None:
                        title = widget_info.get('window_title')
                        class_name = widget_info.get('class')
                        object_name = widget_info.get('object_name')
                        geometry = widget_info.get('geometry')
                        extras: list[str] = []
                        if class_name:
                            extras.append(f"class={class_name}")
                        if object_name:
                            extras.append(f"object_name={object_name}")
                        if title:
                            extras.append(f"title={title}")
                        if geometry is not None:
                            extras.append(f"geometry={geometry['width']}x{geometry['height']}@{geometry['x']},{geometry['y']}")
                        if extras:
                            line += f" ({', '.join(extras)})"
                    sections.append(line)
                else:
                    line = f"- {label}: failed ({item.get('error', 'unknown error')})"
                    widget_info = item.get('widget_info')
                    if widget_info is not None:
                        class_name = widget_info.get('class')
                        object_name = widget_info.get('object_name')
                        if class_name or object_name:
                            line += f" [widget={class_name or 'unknown'} object_name={object_name or 'unknown'}]"
                    sections.append(line)
            sections.append("")

        remaining = [cat for cat in grouped.keys() if cat not in order]
        for category in remaining:
            items = grouped[category]
            sections.append(f"## {category}")
            for item in items:
                label = item.get('label')
                if item.get('captured'):
                    sections.append(f"- {label}: captured at {item.get('path')}")
                else:
                    sections.append(f"- {label}: failed ({item.get('error', 'unknown error')})")
            sections.append("")

        return "\n".join(sections).strip()

    def format_performance_summary(self, performance_data: List[Dict[str, Any]]) -> str:
        if not performance_data:
            return "No performance data collected."
        return "\n".join([f"- {p.get('class')}: children={p.get('children')} visible={p.get('visible')}" for p in performance_data])

    def format_fix_priority(self, layout_issues: List[Dict[str, Any]], accessibility_data: List[Dict[str, Any]], performance_data: List[Dict[str, Any]]) -> str:
        items = []
        items.extend([f"Layout: {i.get('object_name', i.get('widget'))}" for i in layout_issues])
        items.extend([f"Accessibility: {d.get('object_name', d.get('text',''))}" for d in accessibility_data])
        if not items:
            return "No fixes required."
        return "\n".join([f"- {it}" for it in items])

    def format_widget_tree(self, widget_tree: List[Dict[str, Any]]) -> str:
        return "Widget tree collected."

    def format_navigation_map(self, navigation_map: Any) -> str:
        return "Navigation map collected."

    def to_html(self, markdown: str) -> str:
        return f"<html><body><pre>{markdown}</pre></body></html>"
