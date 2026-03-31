"""
Module E - HTML Report Template
Generates detailed HTML reports from report data
"""
import base64
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .report_config import RATING_THRESHOLDS, ISSUE_ICONS, METRICS_DISPLAY, METRICS_GROUP_NAMES


class HTMLReportGenerator:
    """Generates comprehensive HTML reports from report data"""

    def __init__(self, report_data: Dict[str, Any], session_dir: Optional[Path] = None):
        self.data = report_data
        self.session_dir = Path(session_dir) if session_dir else None

    def generate_html(self) -> str:
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UX Audit Report</title>
    <style>
{self._get_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._render_header()}
        {self._render_overall_score()}
        {self._render_task_metrics()}
        {self._render_executive_summary()}
        {self._render_behavioral_timeline()}
        {self._render_navigation_map()}
        {self._render_detailed_findings()}
        {self._render_module_details()}
        {self._render_all_issues_detailed()}
        {self._render_recommendations_detailed()}
        {self._render_footer()}
    </div>
</body>
</html>"""

    def _get_styles(self) -> str:
        return """
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
            line-height: 1.7;
            color: #1f2937;
            background: #f3f4f6;
            font-size: 15px;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 24px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.05);
        }

        /* Header */
        .header {
            text-align: center;
            padding: 48px 24px;
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            color: white;
            border-radius: 12px;
            margin-bottom: 24px;
        }
        .header h1 { font-size: 2.2em; margin-bottom: 16px; font-weight: 700; }
        .header .meta { opacity: 0.95; font-size: 1em; }
        .header .meta div { margin: 6px 0; }
        .header .task-box {
            background: rgba(255,255,255,0.15);
            padding: 12px 20px;
            border-radius: 8px;
            margin-top: 16px;
            display: inline-block;
        }

        /* Score Section */
        .score-card { padding: 36px; }
        .score-top {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 48px;
            flex-wrap: wrap;
        }
        .score-donut-wrap { text-align: center; }
        .score-radar-wrap { text-align: center; }
        .score-label { font-size: 1.6em; font-weight: 600; margin: 8px 0 4px; }
        .score-description { color: #6b7280; max-width: 320px; margin: 0 auto; font-size: 0.9em; }

        /* Emotion Bar */
        .emotion-bar-wrap {
            margin: 16px 0 8px;
            padding: 12px 0;
        }
        .emotion-bar-label {
            font-size: 0.8em;
            color: #9ca3af;
            margin-bottom: 6px;
        }
        .emotion-bar {
            display: flex;
            height: 10px;
            border-radius: 5px;
            overflow: hidden;
            background: #e5e7eb;
        }
        .emotion-bar .seg {
            height: 100%;
            transition: width 0.3s;
        }

        /* Screenshot thumbnails in timeline */
        .timeline-screenshot {
            width: 120px;
            height: 68px;
            object-fit: cover;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            cursor: pointer;
            flex-shrink: 0;
            transition: transform 0.2s;
        }
        .timeline-screenshot:hover {
            transform: scale(2.5);
            z-index: 100;
            position: relative;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }

        /* Navigation Map */
        .nav-map { margin: 16px 0; overflow-x: auto; }
        .nav-map svg text { font-family: system-ui, sans-serif; }

        /* Metric progress bar */
        .metric-bar-wrap {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .metric-bar {
            flex: 1;
            height: 7px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            max-width: 120px;
        }
        .metric-bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }

        /* Typography */
        h2 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #111827;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 10px;
            font-weight: 600;
        }
        h3 {
            font-size: 1.2em;
            margin: 20px 0 12px;
            color: #374151;
            font-weight: 600;
        }
        h4 {
            font-size: 1em;
            margin: 16px 0 8px;
            color: #4b5563;
            font-weight: 600;
        }

        /* Summary Points */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .summary-box {
            background: #f9fafb;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #e5e7eb;
        }
        .summary-box h4 { margin-top: 0; }
        .summary-box ul { margin-left: 20px; }
        .summary-box li { margin: 8px 0; }

        /* Critical Findings */
        .critical-section {
            background: linear-gradient(135deg, #fef2f2, #fee2e2);
            border: 2px solid #ef4444;
            border-radius: 12px;
            padding: 24px;
            margin: 24px 0;
        }
        .critical-section h3 {
            color: #dc2626;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .critical-item {
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
            border-left: 4px solid #ef4444;
        }
        .critical-item .title { font-weight: 600; color: #991b1b; }
        .critical-item .detail { margin-top: 8px; color: #4b5563; }
        .critical-item .source-tag {
            font-size: 0.75em;
            color: white;
            background: #991b1b;
            padding: 2px 8px;
            border-radius: 4px;
            margin-left: 8px;
            vertical-align: middle;
        }

        /* Module Cards */
        .module-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        @media (max-width: 768px) {
            .module-grid { grid-template-columns: 1fr; }
        }
        .module-card {
            background: #f9fafb;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #e5e7eb;
        }
        .module-card h3 {
            font-size: 1.1em;
            margin: 0 0 16px;
            color: #1f2937;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .module-card .icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
        }
        .module-card .stats { margin-bottom: 12px; }
        .module-card .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        .module-card .stat-row:last-child { border-bottom: none; }
        .module-card .stat-label { color: #6b7280; }
        .module-card .stat-value { font-weight: 600; }
        .module-card .description {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #e5e7eb;
            color: #4b5563;
            font-size: 0.9em;
        }

        /* Issues List */
        .issues-section { margin-top: 16px; }
        .issue-group { margin-bottom: 24px; }
        .issue-group-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }
        .issue-group-header .badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .issue-group-header .badge.critical { background: #fee2e2; color: #991b1b; }
        .issue-group-header .badge.high, .issue-group-header .badge.serious { background: #ffedd5; color: #9a3412; }
        .issue-group-header .badge.medium, .issue-group-header .badge.moderate { background: #fef3c7; color: #92400e; }
        .issue-group-header .badge.low, .issue-group-header .badge.minor { background: #dcfce7; color: #166534; }
        .badge.green { background: #dcfce7; color: #166534; }
        .badge.yellow { background: #fef3c7; color: #92400e; }
        .badge.red { background: #fee2e2; color: #991b1b; }
        .badge.gray { background: #f3f4f6; color: #6b7280; }

        .issue-item {
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            border: 1px solid #e5e7eb;
            border-left: 4px solid;
        }
        .issue-item.critical { border-left-color: #ef4444; }
        .issue-item.high, .issue-item.serious { border-left-color: #f97316; }
        .issue-item.medium, .issue-item.moderate { border-left-color: #eab308; }
        .issue-item.low, .issue-item.minor { border-left-color: #22c55e; }

        .issue-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }
        .issue-title { font-weight: 600; color: #1f2937; }
        .issue-source {
            font-size: 0.8em;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            background: #6b7280;
            white-space: nowrap;
            flex-shrink: 0;
            margin-left: 12px;
        }
        .issue-description { color: #4b5563; margin-bottom: 12px; }
        .issue-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 0.85em;
            color: #6b7280;
        }
        .issue-meta span {
            background: #f3f4f6;
            padding: 4px 10px;
            border-radius: 4px;
        }
        .wcag-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
        .wcag-tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.78em;
            font-weight: 600;
            font-family: monospace;
            background: #ede9fe;
            color: #5b21b6;
            border: 1px solid #c4b5fd;
        }
        .wcag-tag.level-a { background: #dbeafe; color: #1e40af; border-color: #93c5fd; }
        .wcag-tag.level-aa { background: #fef3c7; color: #92400e; border-color: #fcd34d; }
        .wcag-tag.rule-id { background: #f3f4f6; color: #4b5563; border-color: #d1d5db; }

        /* Recommendations */
        .rec-item {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid #e5e7eb;
            border-left: 5px solid #3b82f6;
        }
        .rec-item.critical { border-left-color: #ef4444; background: #fef2f2; }
        .rec-item.high { border-left-color: #f97316; background: #fff7ed; }
        .rec-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .rec-priority {
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            padding: 4px 10px;
            border-radius: 4px;
        }
        .rec-priority.critical { background: #fee2e2; color: #991b1b; }
        .rec-priority.high { background: #ffedd5; color: #9a3412; }
        .rec-priority.medium { background: #e0e7ff; color: #3730a3; }
        .rec-category { font-size: 0.85em; color: #6b7280; }
        .rec-title { font-weight: 600; font-size: 1.05em; margin-bottom: 8px; }
        .rec-source { font-size: 0.85em; color: #9ca3af; margin-top: 8px; }

        /* Insights */
        .insights-list { margin-top: 16px; }
        .insight-item {
            padding: 12px 16px;
            background: #eff6ff;
            border-radius: 8px;
            margin-bottom: 8px;
            border-left: 3px solid #3b82f6;
        }

        /* Timeline */
        .timeline { margin: 16px 0; }
        .timeline-item {
            display: flex;
            gap: 16px;
            padding: 12px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        .timeline-item:last-child { border-bottom: none; }
        .timeline-item.backtrack { background: #fffbeb; border-radius: 8px; padding: 12px; margin-bottom: 2px; }
        .timeline-step {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.9em;
            flex-shrink: 0;
            background: #e0e7ff;
            color: #3730a3;
        }
        .timeline-step.backtrack { background: #fef3c7; color: #92400e; }
        .timeline-step.negative { background: #fee2e2; color: #991b1b; }
        .timeline-step.positive { background: #dcfce7; color: #166534; }
        .timeline-content { flex: 1; }
        .timeline-action { font-weight: 500; font-size: 0.95em; }
        .timeline-detail { color: #6b7280; font-size: 0.85em; margin-top: 4px; }
        .timeline-url { color: #9ca3af; font-size: 0.8em; margin-top: 2px; word-break: break-all; }
        .timeline-ux-obs {
            margin-top: 8px;
            padding: 8px 12px;
            background: #fef2f2;
            border-left: 3px solid #ef4444;
            border-radius: 0 6px 6px 0;
            font-size: 0.85em;
            color: #991b1b;
        }
        .timeline-backtrack-badge {
            display: inline-block;
            font-size: 0.75em;
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fcd34d;
            padding: 1px 8px;
            border-radius: 4px;
            margin-left: 8px;
            vertical-align: middle;
        }

        /* Metrics Table */
        .metrics-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.95em;
        }
        .metrics-table th {
            background: #f9fafb;
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #e5e7eb;
            color: #374151;
        }
        .metrics-table td {
            padding: 10px 14px;
            border-bottom: 1px solid #f3f4f6;
        }
        .metrics-table tr:last-child td { border-bottom: none; }
        .metrics-table .group-header td {
            background: #f0f4ff;
            font-weight: 600;
            color: #1e40af;
            padding: 8px 14px;
            border-bottom: 1px solid #dbeafe;
        }
        .metric-value {
            font-weight: 600;
            font-size: 1.05em;
        }
        .metric-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
        }
        .metric-dot.green { background: #22c55e; }
        .metric-dot.yellow { background: #eab308; }
        .metric-dot.red { background: #ef4444; }
        .metric-dot.gray { background: #9ca3af; }
        .metric-ref {
            font-size: 0.8em;
            color: #9ca3af;
            margin-left: 6px;
        }

        /* Weights Table */
        .weights-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
            margin-top: 16px;
        }
        .weights-table th, .weights-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #f3f4f6;
            text-align: left;
        }
        .weights-table th {
            background: #f9fafb;
            font-weight: 600;
            color: #6b7280;
        }
        .weights-table .formula {
            font-family: monospace;
            font-size: 0.85em;
            color: #6b7280;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 24px;
            color: #6b7280;
            font-size: 0.9em;
        }

        /* Print / PDF */
        @media print {
            @page {
                size: A4;
                margin: 18mm 15mm 18mm 15mm;
            }
            * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
            body { background: white !important; font-size: 11pt; color: #1f2937; }
            .container { max-width: none; padding: 0; }

            /* Cards */
            .card {
                box-shadow: none !important;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                margin-bottom: 14px;
                page-break-inside: avoid;
            }

            /* Header — keep gradient */
            .header { padding: 24px 20px; border-radius: 6px; page-break-after: avoid; }

            /* Score section — keep on one page */
            .score-card { page-break-inside: avoid; }
            .score-breakdown { gap: 24px; }

            /* Issues — allow breaking between groups, not inside items */
            .issue-item { page-break-inside: avoid; }
            .issue-group { page-break-inside: avoid; }

            /* Recommendations */
            .rec-item { page-break-inside: avoid; }

            /* Timeline — allow long timelines to break */
            .timeline-item { page-break-inside: avoid; }

            /* Critical section */
            .critical-section { page-break-inside: avoid; }
            .critical-item { page-break-inside: avoid; }

            /* Module grid — stack on narrow page */
            .module-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }

            /* Remove interactive link styles */
            a { color: #3b82f6 !important; text-decoration: none; }
            a[href]:after { content: ""; } /* don't print URLs */

            /* Summary grid */
            .summary-grid { grid-template-columns: 1fr; }

            /* Footer */
            .footer { padding: 12px; font-size: 9pt; border-top: 1px solid #e5e7eb; }

            /* Page break hints */
            h2 { page-break-after: avoid; }
            .card:nth-child(1) { page-break-before: avoid; }
        }
        """

    def _render_header(self) -> str:
        meta = self.data.get("metadata", {})
        persona = meta.get("persona", {})

        return f"""
        <div class="header">
            <h1>UX Audit Report</h1>
            <div class="meta">
                <div><strong>URL:</strong> {meta.get('url', 'N/A')}</div>
                <div><strong>Персона:</strong> {persona.get('name', 'N/A')} &mdash; {persona.get('description', '')}</div>
                <div class="task-box">
                    <strong>Задача:</strong> {meta.get('task', 'N/A')}
                </div>
            </div>
        </div>
        """

    def _render_svg_donut(self, overall: float, breakdown: dict, color: str) -> str:
        """Generate SVG donut chart with segments for each module score"""
        import math
        pct = int(overall * 100)
        # Donut parameters
        cx, cy, r = 90, 90, 70
        stroke_w = 18
        circumference = 2 * math.pi * r

        # Background ring
        svg = f'''<svg width="180" height="180" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg">
            <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e5e7eb" stroke-width="{stroke_w}"/>'''

        # Colored arc — overall score
        dash = circumference * overall
        gap = circumference - dash
        svg += f'''
            <circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
                stroke="{color}" stroke-width="{stroke_w}"
                stroke-dasharray="{dash:.1f} {gap:.1f}"
                stroke-linecap="round"
                transform="rotate(-90 {cx} {cy})"
                style="transition: stroke-dasharray 0.6s ease;"/>'''

        # Center text
        svg += f'''
            <text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="36" font-weight="700" fill="{color}">{pct}</text>
            <text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="13" fill="#6b7280">из 100</text>
        </svg>'''
        return svg

    def _render_radar_chart(self, breakdown: dict) -> str:
        """Generate SVG radar/spider chart for 4 component scores"""
        import math
        labels_cfg = {
            "visual": ("Визуал", "#8b5cf6"),
            "behavioral": ("Поведение", "#3b82f6"),
            "accessibility": ("Доступность", "#10b981"),
            "sentiment": ("Эмоции", "#f59e0b")
        }
        keys = ["visual", "behavioral", "accessibility", "sentiment"]
        values = [breakdown.get(k, 0) for k in keys]
        n = len(keys)
        cx, cy, max_r = 120, 120, 85

        svg = f'<svg width="240" height="260" viewBox="0 0 240 260" xmlns="http://www.w3.org/2000/svg">'

        # Grid rings
        for level in (0.25, 0.5, 0.75, 1.0):
            r = max_r * level
            points = []
            for i in range(n):
                angle = (2 * math.pi * i / n) - math.pi / 2
                points.append(f"{cx + r * math.cos(angle):.1f},{cy + r * math.sin(angle):.1f}")
            svg += f'<polygon points="{" ".join(points)}" fill="none" stroke="#e5e7eb" stroke-width="1"/>'

        # Axis lines
        for i in range(n):
            angle = (2 * math.pi * i / n) - math.pi / 2
            x2 = cx + max_r * math.cos(angle)
            y2 = cy + max_r * math.sin(angle)
            svg += f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#e5e7eb" stroke-width="1"/>'

        # Data polygon
        data_points = []
        for i in range(n):
            angle = (2 * math.pi * i / n) - math.pi / 2
            r = max_r * values[i]
            data_points.append(f"{cx + r * math.cos(angle):.1f},{cy + r * math.sin(angle):.1f}")
        svg += f'<polygon points="{" ".join(data_points)}" fill="rgba(59,130,246,0.15)" stroke="#3b82f6" stroke-width="2.5"/>'

        # Data dots + labels
        for i in range(n):
            angle = (2 * math.pi * i / n) - math.pi / 2
            r = max_r * values[i]
            dx = cx + r * math.cos(angle)
            dy = cy + r * math.sin(angle)
            _, dot_color = labels_cfg.get(keys[i], ("", "#6b7280"))
            svg += f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="4" fill="{dot_color}" stroke="white" stroke-width="2"/>'

            # Label position (outside the chart)
            lr = max_r + 22
            lx = cx + lr * math.cos(angle)
            ly = cy + lr * math.sin(angle)
            label_name, label_color = labels_cfg.get(keys[i], (keys[i], "#6b7280"))
            anchor = "middle"
            if lx < cx - 10:
                anchor = "end"
            elif lx > cx + 10:
                anchor = "start"
            pct_val = int(values[i] * 100)
            svg += f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-size="11" fill="{label_color}" font-weight="600">{label_name}</text>'
            svg += f'<text x="{lx:.1f}" y="{ly + 14:.1f}" text-anchor="{anchor}" font-size="11" fill="#9ca3af">{pct_val}%</text>'

        svg += '</svg>'
        return svg

    def _render_overall_score(self) -> str:
        score = self.data.get("overall_score", {})
        overall = score.get("overall", 0)
        color = score.get("rating_color", "#6b7280")
        label = score.get("rating_label", "N/A")
        breakdown = score.get("breakdown", {})

        descriptions = {
            "excellent": "Интерфейс демонстрирует отличное качество UX. Минимальные проблемы, высокая доступность.",
            "good": "Хороший уровень UX с некоторыми областями для улучшения. Основной функционал работает корректно.",
            "fair": "Удовлетворительный UX, но есть заметные проблемы, влияющие на пользовательский опыт.",
            "poor": "Серьёзные проблемы с UX, требующие немедленного внимания. Пользователи испытывают затруднения.",
            "critical": "Критические проблемы юзабилити и доступности. Интерфейс требует существенной переработки."
        }
        desc = descriptions.get(score.get("rating", "fair"), "")

        # SVG donut chart
        donut_svg = self._render_svg_donut(overall, breakdown, color)

        # SVG radar chart
        radar_svg = self._render_radar_chart(breakdown)

        # Weights transparency table
        weights = score.get("weights", {})
        weight_labels = {
            "visual": "Визуальный анализ (A)",
            "behavioral": "Поведенческий анализ (B)",
            "accessibility": "Доступность (C)",
            "sentiment": "Эмоции (D)"
        }
        weights_rows = ""
        for wk, wv in weights.items():
            component_score = breakdown.get(wk, 0)
            weighted = component_score * wv
            bar_pct = int(component_score * 100)
            bar_color = {"visual": "#8b5cf6", "behavioral": "#3b82f6", "accessibility": "#10b981", "sentiment": "#f59e0b"}.get(wk, "#6b7280")
            weights_rows += f"""
            <tr>
                <td>{weight_labels.get(wk, wk)}</td>
                <td>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="flex:1; height:6px; background:#e5e7eb; border-radius:3px; overflow:hidden;">
                            <div style="width:{bar_pct}%; height:100%; background:{bar_color}; border-radius:3px;"></div>
                        </div>
                        <span class="formula">{bar_pct}%</span>
                    </div>
                </td>
                <td class="formula">&times;{wv}</td>
                <td class="formula" style="font-weight:600;">= {weighted:.2f}</td>
            </tr>
            """
        weights_html = ""
        if weights_rows:
            total_w = sum(weights.values())
            weights_html = f"""
            <div style="margin-top: 20px;">
                <table class="weights-table">
                    <thead><tr><th>Компонент</th><th>Балл</th><th>Вес</th><th>Вклад</th></tr></thead>
                    <tbody>
                        {weights_rows}
                        <tr style="border-top: 2px solid #d1d5db; font-weight: 600;">
                            <td>Итого</td><td></td><td>{total_w:.2f}</td><td>= {int(overall * 100)}%</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """

        return f"""
        <div class="card score-card">
            <div class="score-top">
                <div class="score-donut-wrap">
                    {donut_svg}
                    <div class="score-label">{label}</div>
                    <p class="score-description">{desc}</p>
                </div>
                <div class="score-radar-wrap">
                    {radar_svg}
                </div>
            </div>
            {weights_html}
        </div>
        """

    def _render_task_metrics(self) -> str:
        """Render formal metrics table (M1-M13) with color-coded thresholds"""
        bm = self.data.get("behavioral_metrics", {})
        if not bm:
            return ""

        # Flatten all metrics into one dict
        all_metrics = {}
        for group_key in ("task_effectiveness", "interface_quality", "subjective_experience"):
            all_metrics.update(bm.get(group_key, {}))

        ref = bm.get("reference", {})

        def format_value(key: str, value) -> str:
            cfg = METRICS_DISPLAY.get(key, {})
            fmt = cfg.get("format", "")
            if value is None:
                return '<span style="color:#9ca3af;">N/A</span>'
            if fmt == "bool":
                return "Да" if value else "Нет"
            if fmt == "percent":
                return f"{int(value * 100)}%"
            if fmt == "signed_float":
                return f"{value:+.2f}"
            if fmt == "float":
                return f"{value:.2f}"
            if fmt == "score100":
                return f"{value:.0f}/100"
            if fmt == "trend":
                labels = {"improving": "Улучшение", "stable": "Стабильно", "declining": "Ухудшение"}
                return labels.get(value, str(value))
            if fmt == "int":
                return str(int(value))
            return str(value)

        def get_color(key: str, value) -> str:
            cfg = METRICS_DISPLAY.get(key, {})
            thresholds = cfg.get("thresholds")
            if value is None or thresholds is None:
                # Special cases
                if cfg.get("format") == "bool":
                    return "green" if value else "red"
                if cfg.get("format") == "trend":
                    return {"improving": "green", "stable": "yellow", "declining": "red"}.get(value, "gray")
                return "gray"
            lower_better = cfg.get("lower_is_better", False)
            g = thresholds["green"]
            y = thresholds["yellow"]
            if lower_better:
                if value <= g:
                    return "green"
                elif value <= y:
                    return "yellow"
                else:
                    return "red"
            else:
                if value >= g:
                    return "green"
                elif value >= y:
                    return "yellow"
                else:
                    return "red"

        rows_html = ""
        current_group = None

        for key in METRICS_DISPLAY:
            cfg = METRICS_DISPLAY[key]
            group = cfg["group"]

            # Group header
            if group != current_group:
                current_group = group
                group_name = METRICS_GROUP_NAMES.get(group, group)
                rows_html += f'''
                <tr class="group-header"><td colspan="3">{group_name}</td></tr>
                '''

            value = all_metrics.get(key)
            color = get_color(key, value)
            formatted = format_value(key, value)
            name = cfg["name_ru"]

            # Reference info for some metrics
            ref_html = ""
            if key == "M3_relative_efficiency" and ref.get("optimal_steps"):
                ref_html = f'<span class="metric-ref">норма: {ref["optimal_steps"]} шагов</span>'
            elif key == "M6_lostness" and ref.get("min_pages_required"):
                ref_html = f'<span class="metric-ref">мин. страниц: {ref["min_pages_required"]}</span>'
            elif key == "M2_steps_to_goal" and ref.get("optimal_steps"):
                ref_html = f'<span class="metric-ref">оптимум: {ref["optimal_steps"]}</span>'

            # Progress bar for percentage/ratio metrics
            bar_html = ""
            bar_colors = {"green": "#22c55e", "yellow": "#eab308", "red": "#ef4444", "gray": "#9ca3af"}
            fmt = cfg.get("format", "")
            if fmt == "percent" and value is not None:
                bar_pct = int(value * 100)
                bar_html = f'''<div class="metric-bar"><div class="metric-bar-fill" style="width:{bar_pct}%; background:{bar_colors[color]};"></div></div>'''
            elif fmt == "score100" and value is not None:
                bar_html = f'''<div class="metric-bar"><div class="metric-bar-fill" style="width:{min(int(value), 100)}%; background:{bar_colors[color]};"></div></div>'''
            elif fmt == "float" and value is not None:
                # Lostness: 0 = best, 1.5+ = worst → invert
                bar_pct = max(0, min(100, int((1 - value / 1.5) * 100)))
                bar_html = f'''<div class="metric-bar"><div class="metric-bar-fill" style="width:{bar_pct}%; background:{bar_colors[color]};"></div></div>'''
            elif fmt == "signed_float" and value is not None:
                bar_pct = int((value + 1) * 50)  # -1..+1 → 0..100
                bar_html = f'''<div class="metric-bar"><div class="metric-bar-fill" style="width:{bar_pct}%; background:{bar_colors[color]};"></div></div>'''

            value_cell = f'''<div class="metric-bar-wrap"><span class="metric-dot {color}"></span><span class="metric-value">{formatted}</span>{ref_html}{bar_html}</div>'''

            rows_html += f'''
            <tr>
                <td>{name}</td>
                <td>{value_cell}</td>
                <td style="text-align:center;"><span class="badge {color}" style="font-size:0.75em; padding:2px 8px; border-radius:4px;">{key.split("_")[0]}</span></td>
            </tr>
            '''

        return f"""
        <div class="card">
            <h2>Метрики задачи</h2>
            <p style="color: #6b7280; margin-bottom: 16px;">
                Формальные UX-метрики, рассчитанные по результатам всех модулей анализа.
            </p>
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th style="width:45%;">Метрика</th>
                        <th style="width:40%;">Значение</th>
                        <th style="width:15%; text-align:center;">Код</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """

    def _render_executive_summary(self) -> str:
        summary = self.data.get("executive_summary", {})
        points = summary.get("summary_points", [])
        critical = summary.get("critical_findings", [])
        modules_analyzed = summary.get("modules_analyzed", 0)

        points_html = "".join(f"<li>{p}</li>" for p in points)

        critical_html = ""
        if critical:
            critical_items = ""
            for c in critical:
                if isinstance(c, dict):
                    title = c.get("title", "Критическая проблема")
                    detail = c.get("detail", "Требует немедленного внимания")
                    source = c.get("source", "")
                    recommendation = c.get("recommendation", "")
                    source_tag = f'<span class="source-tag">{source}</span>' if source else ""
                else:
                    title = c
                    detail = "Требует немедленного внимания."
                    source_tag = ""
                    recommendation = ""

                rec_html = ""
                if recommendation:
                    rec_html = f'''
                    <div style="margin-top: 8px; padding: 8px 12px; background: rgba(255,255,255,0.7); border-radius: 6px; font-size: 0.9em; border-left: 3px solid #16a34a;">
                        <strong style="color: #166534;">Рекомендация:</strong> {recommendation}
                    </div>
                    '''

                critical_items += f"""
                <div class="critical-item">
                    <div class="title">{title}{source_tag}</div>
                    <div class="detail">{detail}</div>
                    {rec_html}
                </div>
                """
            critical_html = f"""
            <div class="critical-section">
                <h3>Ключевые находки ({len(critical)})</h3>
                {critical_items}
            </div>
            """

        return f"""
        <div class="card">
            <h2>Краткое резюме</h2>
            <p style="color: #6b7280; margin-bottom: 16px;">
                Проанализировано модулей: {modules_analyzed}. Ниже представлены ключевые выводы аудита.
            </p>
            <div class="summary-grid">
                <div class="summary-box">
                    <h4>Основные выводы</h4>
                    <ul>{points_html}</ul>
                </div>
            </div>
            {critical_html}
        </div>
        """

    def _get_screenshot_base64(self, step_id: int) -> str:
        """Load step screenshot as base64 data URI for embedding in HTML"""
        if not self.session_dir:
            return ""
        screenshot_path = self.session_dir / f"step_{step_id:02d}_screenshot.png"
        if not screenshot_path.exists():
            return ""
        try:
            data = screenshot_path.read_bytes()
            b64 = base64.b64encode(data).decode("ascii")
            return f"data:image/png;base64,{b64}"
        except Exception:
            return ""

    def _render_emotion_bar(self, timeline: list) -> str:
        """Render horizontal emotion gradient bar from timeline sentiments"""
        if not timeline:
            return ""
        colors = {"POSITIVE": "#22c55e", "NEUTRAL": "#94a3b8", "NEGATIVE": "#ef4444"}
        n = len(timeline)
        segments = ""
        for step in timeline:
            sentiment = step.get("sentiment", "NEUTRAL")
            c = colors.get(sentiment, "#94a3b8")
            w = 100 / n
            segments += f'<div class="seg" style="width:{w:.2f}%; background:{c};" title="Шаг {step.get("step_id", "")} — {sentiment}"></div>'

        return f"""
        <div class="emotion-bar-wrap">
            <div class="emotion-bar-label">Эмоциональный профиль сессии</div>
            <div class="emotion-bar">{segments}</div>
            <div style="display:flex; justify-content:space-between; font-size:0.75em; color:#9ca3af; margin-top:4px;">
                <span>Шаг 1</span>
                <div style="display:flex; gap:12px;">
                    <span><span style="color:#22c55e;">&#9679;</span> Позитив</span>
                    <span><span style="color:#94a3b8;">&#9679;</span> Нейтрал</span>
                    <span><span style="color:#ef4444;">&#9679;</span> Негатив</span>
                </div>
                <span>Шаг {n}</span>
            </div>
        </div>
        """

    def _render_behavioral_timeline(self) -> str:
        timeline = self.data.get("behavioral_timeline", [])
        if not timeline:
            return ""

        # Translate action types
        action_labels = {
            "click": "Клик",
            "scroll": "Скролл",
            "type": "Ввод текста",
            "navigate": "Переход",
            "hover": "Наведение",
            "unknown": "Действие",
        }

        # Emotion bar
        emotion_bar_html = self._render_emotion_bar(timeline)

        items_html = ""
        for step in timeline:
            step_id = step.get("step_id", 0)
            action_type = step.get("action_type", "unknown")
            target = step.get("action_target", "")
            reasoning = step.get("reasoning", "")
            url = step.get("url", "")
            sentiment = step.get("sentiment", "NEUTRAL")
            ux_observation = step.get("ux_observation")
            is_backtrack = step.get("is_backtrack", False)

            label = action_labels.get(action_type, action_type)
            target_text = f" &rarr; {target}" if target else ""

            # Step circle style
            step_class = "backtrack" if is_backtrack else ("negative" if sentiment == "NEGATIVE" else ("positive" if sentiment == "POSITIVE" else ""))
            item_class = "backtrack" if is_backtrack else ""

            # Backtrack badge
            backtrack_badge = '<span class="timeline-backtrack-badge">возврат</span>' if is_backtrack else ""

            # UX observation block
            ux_html = ""
            if ux_observation:
                ux_html = f'<div class="timeline-ux-obs">UX: {ux_observation}</div>'

            # Screenshot thumbnail
            screenshot_html = ""
            screenshot_data = self._get_screenshot_base64(step_id)
            if screenshot_data:
                screenshot_html = f'<img class="timeline-screenshot" src="{screenshot_data}" alt="Шаг {step_id}" loading="lazy"/>'

            items_html += f"""
            <div class="timeline-item {item_class}">
                <div class="timeline-step {step_class}">{step_id}</div>
                <div class="timeline-content">
                    <div class="timeline-action">{label}{target_text}{backtrack_badge}</div>
                    {f'<div class="timeline-detail">{reasoning}</div>' if reasoning else ''}
                    {f'<div class="timeline-url">{url}</div>' if url else ''}
                    {ux_html}
                </div>
                {screenshot_html}
            </div>
            """

        summaries = self.data.get("module_summaries", {})
        module_b = summaries.get("module_b", {})
        status = module_b.get("task_status", "")
        total = module_b.get("total_steps", len(timeline))

        status_labels = {
            "completed": "Задача выполнена",
            "failed": "Задача не выполнена",
            "max_steps_reached": "Лимит шагов достигнут",
            "partial": "Частично выполнена"
        }
        status_text = status_labels.get(status, status)

        return f"""
        <div class="card">
            <h2>Путь пользователя ({total} шагов)</h2>
            <p style="color: #6b7280; margin-bottom: 8px;">
                Результат: <strong>{status_text}</strong>
            </p>
            {emotion_bar_html}
            <div class="timeline">
                {items_html}
            </div>
        </div>
        """

    def _render_navigation_map(self) -> str:
        """Render SVG navigation path showing URL transitions with loops highlighted"""
        from urllib.parse import urlparse
        timeline = self.data.get("behavioral_timeline", [])
        if not timeline:
            return ""

        # Extract unique URLs in visit order, track transitions
        urls_sequence = []
        for step in timeline:
            url = step.get("url", "")
            if url:
                urls_sequence.append(url)

        if len(urls_sequence) < 2:
            return ""

        # Shorten URLs to path only
        def short_url(url: str) -> str:
            try:
                parsed = urlparse(url)
                path = parsed.path.rstrip("/")
                if not path or path == "":
                    return parsed.netloc or url[:30]
                # Keep last 2 path segments
                parts = path.split("/")
                short = "/".join(parts[-2:]) if len(parts) > 2 else path
                return short if len(short) <= 35 else short[:32] + "..."
            except Exception:
                return url[:30]

        # Build unique nodes and edges
        unique_urls = []
        url_to_idx = {}
        for u in urls_sequence:
            if u not in url_to_idx:
                url_to_idx[u] = len(unique_urls)
                unique_urls.append(u)

        # Count visits per URL
        visit_counts = {}
        for u in urls_sequence:
            visit_counts[u] = visit_counts.get(u, 0) + 1

        # Build edges with counts
        edges = {}
        for i in range(len(urls_sequence) - 1):
            a, b = urls_sequence[i], urls_sequence[i + 1]
            if a != b:
                key = (url_to_idx[a], url_to_idx[b])
                edges[key] = edges.get(key, 0) + 1

        n = len(unique_urls)
        if n > 12:
            return ""  # Too many nodes — skip to avoid clutter

        # Layout: horizontal flow
        node_w = 140
        node_h = 36
        gap_x = 40
        cols = min(n, 4)
        rows_count = (n + cols - 1) // cols
        svg_w = cols * (node_w + gap_x) + 40
        svg_h = rows_count * 80 + 60

        # Node positions (snake layout)
        positions = []
        for i in range(n):
            row = i // cols
            col = i % cols
            if row % 2 == 1:
                col = cols - 1 - col  # snake: reverse odd rows
            x = 20 + col * (node_w + gap_x)
            y = 30 + row * 80
            positions.append((x, y))

        svg = f'<svg width="100%" viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg" style="max-width:{svg_w}px;">'

        # Draw edges
        for (a_idx, b_idx), count in edges.items():
            ax, ay = positions[a_idx]
            bx, by = positions[b_idx]
            ax_c, ay_c = ax + node_w / 2, ay + node_h / 2
            bx_c, by_c = bx + node_w / 2, by + node_h / 2

            is_back = b_idx < a_idx  # backtrack
            stroke_color = "#ef4444" if is_back else "#94a3b8"
            stroke_w = 2 if count == 1 else 3
            opacity = "0.5" if count == 1 else "0.8"

            # Curved path for backtracks
            if is_back:
                mid_y = min(ay_c, by_c) - 30
                svg += f'<path d="M{ax_c:.0f},{ay_c:.0f} Q{(ax_c + bx_c) / 2:.0f},{mid_y:.0f} {bx_c:.0f},{by_c:.0f}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}" opacity="{opacity}" stroke-dasharray="6,4" marker-end="url(#arrow-back)"/>'
            else:
                svg += f'<line x1="{ax_c:.0f}" y1="{ay_c:.0f}" x2="{bx_c:.0f}" y2="{by_c:.0f}" stroke="{stroke_color}" stroke-width="{stroke_w}" opacity="{opacity}" marker-end="url(#arrow)"/>'

        # Arrow markers
        svg += '''
        <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/>
            </marker>
            <marker id="arrow-back" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444"/>
            </marker>
        </defs>'''

        # Draw nodes
        for i, url in enumerate(unique_urls):
            x, y = positions[i]
            visits = visit_counts[url]
            label = short_url(url)
            is_loop = visits > 1

            fill = "#fef2f2" if is_loop else "#f0f4ff"
            border = "#ef4444" if is_loop else "#93c5fd"
            text_color = "#991b1b" if is_loop else "#1e40af"

            svg += f'<rect x="{x}" y="{y}" width="{node_w}" height="{node_h}" rx="8" fill="{fill}" stroke="{border}" stroke-width="1.5"/>'
            svg += f'<text x="{x + node_w / 2}" y="{y + node_h / 2 + 1}" text-anchor="middle" dominant-baseline="middle" font-size="10" fill="{text_color}" font-weight="500">{label}</text>'
            if is_loop:
                svg += f'<circle cx="{x + node_w - 8}" cy="{y + 8}" r="9" fill="#ef4444"/>'
                svg += f'<text x="{x + node_w - 8}" y="{y + 8}" text-anchor="middle" dominant-baseline="central" font-size="9" fill="white" font-weight="700">{visits}</text>'

        svg += '</svg>'

        return f"""
        <div class="card">
            <h2>Карта навигации</h2>
            <p style="color: #6b7280; margin-bottom: 12px;">
                Схема переходов между страницами. Красные стрелки — возвраты, красные кружки — повторные посещения.
            </p>
            <div class="nav-map">{svg}</div>
        </div>
        """

    def _render_detailed_findings(self) -> str:
        summaries = self.data.get("module_summaries", {})
        module_d = summaries.get("module_d", {})
        insights = module_d.get("insights", [])

        if not insights:
            return ""

        # Strip emoji prefixes for cleaner look
        clean_insights = []
        for insight in insights:
            clean = insight.lstrip("+-~!@#$%^&*() \t")
            for emoji_prefix in ["->", "=>", "-->", "==>", "!!!"]:
                clean = clean.lstrip(emoji_prefix).strip()
            clean_insights.append(clean)

        insights_html = "".join(f'<div class="insight-item">{i}</div>' for i in clean_insights)

        return f"""
        <div class="card">
            <h2>Анализ пользовательского опыта</h2>
            <p style="color: #6b7280; margin-bottom: 16px;">
                На основе анализа эмоционального состояния и поведения пользователя:
            </p>
            <div class="insights-list">
                {insights_html}
            </div>
        </div>
        """

    def _module_icon(self, module: str) -> str:
        """Return inline SVG icon for each module"""
        icons = {
            "a": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
            "b": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3l14 9-14 9V3z"/></svg>',
            "c": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 8l-8 8M8 8l8 8"/></svg>',
            "d": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
        }
        return icons.get(module, module.upper())

    def _render_module_details(self) -> str:
        summaries = self.data.get("module_summaries", {})
        cards_html = ""

        # Module A
        if "module_a" in summaries:
            m = summaries["module_a"]
            severity = m.get("severity", {})
            assessment = m.get("assessment", "")[:300]
            cards_html += f"""
            <div class="module-card">
                <h3>
                    <span class="icon" style="background: #ede9fe; color: #7c3aed;">{self._module_icon('a')}</span>
                    Визуальный анализ
                </h3>
                <div class="stats">
                    <div class="stat-row">
                        <span class="stat-label">Всего проблем</span>
                        <span class="stat-value">{m.get('total_issues', 0)}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Критичные</span>
                        <span class="stat-value" style="color: #dc2626;">{severity.get('critical', 0)}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Высокие</span>
                        <span class="stat-value" style="color: #ea580c;">{severity.get('high', 0)}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Средние</span>
                        <span class="stat-value">{severity.get('medium', 0)}</span>
                    </div>
                </div>
                <div class="description">
                    <strong>Оценка:</strong> {assessment}{'...' if len(m.get('assessment', '')) > 300 else ''}
                </div>
            </div>
            """

        # Module B
        if "module_b" in summaries:
            m = summaries["module_b"]
            status_labels = {
                "completed": ("Выполнена", "#16a34a"),
                "failed": ("Не выполнена", "#dc2626"),
                "max_steps_reached": ("Прервана (лимит шагов)", "#ea580c"),
                "partial": ("Частично выполнена", "#ca8a04")
            }
            status_text, color = status_labels.get(m.get('task_status'), ("Неизвестно", "#6b7280"))

            reason = m.get("termination_reason", "")
            reason_labels = {
                "max_steps_reached": "Достигнут лимит шагов",
                "task_completed": "Задача выполнена",
                "task_failed": "Задача не выполнена",
                "navigation_error": "Ошибка навигации"
            }
            reason_text = reason_labels.get(reason, reason)

            backtrack_count = m.get("backtrack_count", 0)
            ux_obs_count = m.get("ux_observations_count", 0)
            backtrack_color = "#dc2626" if backtrack_count >= 3 else "#ea580c" if backtrack_count > 0 else "#16a34a"

            # Navigation efficiency rows
            nav_eff = m.get("navigation_efficiency")
            optimal_steps = m.get("optimal_steps")
            total_steps = m.get("total_steps", 0)
            unique_pages = m.get("unique_pages", 0)
            min_pages = m.get("min_pages_required")
            pages_ok = m.get("pages_ok")

            eff_rows = ""
            if nav_eff is not None and optimal_steps:
                eff_pct = int(nav_eff * 100)
                eff_color = "#16a34a" if nav_eff >= 0.7 else "#ca8a04" if nav_eff >= 0.4 else "#dc2626"
                eff_rows += f"""
                    <div class="stat-row">
                        <span class="stat-label">Эффективность пути</span>
                        <span class="stat-value" style="color:{eff_color};">{eff_pct}%
                            <span style="font-weight:400; font-size:0.85em; color:#6b7280;">
                                ({total_steps} из {optimal_steps} опт.)
                            </span>
                        </span>
                    </div>
                """
            if min_pages is not None:
                pages_color = "#16a34a" if pages_ok else "#dc2626"
                pages_label = "выполнено" if pages_ok else "не выполнено"
                eff_rows += f"""
                    <div class="stat-row">
                        <span class="stat-label">Охват страниц</span>
                        <span class="stat-value" style="color:{pages_color};">
                            {unique_pages} / {min_pages}
                            <span style="font-weight:400; font-size:0.85em; color:#6b7280;">({pages_label})</span>
                        </span>
                    </div>
                """

            cards_html += f"""
            <div class="module-card">
                <h3>
                    <span class="icon" style="background: #dbeafe; color: #2563eb;">{self._module_icon('b')}</span>
                    Поведенческий анализ
                </h3>
                <div class="stats">
                    <div class="stat-row">
                        <span class="stat-label">Шагов выполнено</span>
                        <span class="stat-value">{total_steps}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Статус задачи</span>
                        <span class="stat-value" style="color: {color};">{status_text}</span>
                    </div>
                    {eff_rows}
                    <div class="stat-row">
                        <span class="stat-label">Возвратов на страницы</span>
                        <span class="stat-value" style="color: {backtrack_color};">{backtrack_count}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">UX-наблюдений</span>
                        <span class="stat-value">{ux_obs_count}</span>
                    </div>
                </div>
                <div class="description">
                    <strong>Причина завершения:</strong> {reason_text}
                    {f'<br><span style="color: #dc2626;">Высокий бэктрекинг ({backtrack_count} возврата) — признак дезориентации в навигации</span>' if backtrack_count >= 3 else ''}
                </div>
            </div>
            """

        # Module C
        if "module_c" in summaries:
            m = summaries["module_c"]
            impact = m.get("by_impact", {})
            cards_html += f"""
            <div class="module-card">
                <h3>
                    <span class="icon" style="background: #d1fae5; color: #059669;">{self._module_icon('c')}</span>
                    Аудит доступности (WCAG {m.get('wcag_level', 'AA')})
                </h3>
                <div class="stats">
                    <div class="stat-row">
                        <span class="stat-label">Всего проблем</span>
                        <span class="stat-value">{m.get('total_issues', 0)}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Критичные</span>
                        <span class="stat-value" style="color: #dc2626;">{impact.get('critical', 0)}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Серьёзные</span>
                        <span class="stat-value" style="color: #ea580c;">{impact.get('serious', 0)}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Страниц проверено</span>
                        <span class="stat-value">{m.get('pages_scanned', 0)}</span>
                    </div>
                </div>
                <div class="description">
                    Проверка соответствия стандартам WCAG 2.1 уровня {m.get('wcag_level', 'AA')}.
                    {'<br><strong style="color: #dc2626;">Критические проблемы требуют немедленного исправления!</strong>' if impact.get('critical', 0) > 0 else ''}
                </div>
            </div>
            """

        # Module D
        if "module_d" in summaries:
            m = summaries["module_d"]
            trend_info = {
                "improving": ("Улучшение", "#16a34a", "Пользователь становился более удовлетворён"),
                "stable": ("Стабильно", "#6b7280", "Эмоциональное состояние не менялось значительно"),
                "declining": ("Ухудшение", "#dc2626", "Пользователь испытывал нарастающую фрустрацию")
            }
            trend, trend_color, trend_desc = trend_info.get(m.get('trend'), ("N/A", "#6b7280", ""))
            score = m.get("session_score", 0)
            dist = m.get("distribution", {})

            cards_html += f"""
            <div class="module-card">
                <h3>
                    <span class="icon" style="background: #fef3c7; color: #d97706;">{self._module_icon('d')}</span>
                    Анализ эмоций
                </h3>
                <div class="stats">
                    <div class="stat-row">
                        <span class="stat-label">Оценка сессии</span>
                        <span class="stat-value" style="color: {'#16a34a' if score > 0 else '#dc2626' if score < 0 else '#6b7280'};">{score:+.2f}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Тренд</span>
                        <span class="stat-value" style="color: {trend_color};">{trend}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Болевые точки</span>
                        <span class="stat-value" style="color: #dc2626;">{m.get('pain_points_count', 0)}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Распределение</span>
                        <span class="stat-value" style="font-size: 0.85em;">
                            +{dist.get('POSITIVE', 0)} / ~{dist.get('NEUTRAL', 0)} / -{dist.get('NEGATIVE', 0)}
                        </span>
                    </div>
                </div>
                <div class="description">
                    {trend_desc}
                </div>
            </div>
            """

        return f"""
        <div class="card">
            <h2>Результаты по модулям</h2>
            <p style="color: #6b7280; margin-bottom: 20px;">
                Детальная разбивка результатов каждого модуля анализа.
            </p>
            <div class="module-grid">
                {cards_html}
            </div>
        </div>
        """

    def _render_all_issues_detailed(self) -> str:
        issues = self.data.get("all_issues", [])

        if not issues:
            return """
            <div class="card">
                <h2>Выявленные проблемы</h2>
                <p style="color: #16a34a; text-align: center; padding: 20px;">
                    Критических проблем не обнаружено.
                </p>
            </div>
            """

        grouped = {}
        for issue in issues:
            sev = issue.get("severity", "medium").lower()
            grouped.setdefault(sev, []).append(issue)

        severity_order = ["critical", "high", "serious", "medium", "moderate", "low", "minor"]
        severity_names = {
            "critical": "Критические",
            "high": "Высокие",
            "serious": "Серьёзные",
            "medium": "Средние",
            "moderate": "Умеренные",
            "low": "Низкие",
            "minor": "Минорные"
        }

        groups_html = ""
        for sev in severity_order:
            if sev not in grouped:
                continue

            issues_html = ""
            for issue in grouped[sev]:
                source = issue.get("source", "")
                title = issue.get("title", "")
                desc = issue.get("description", "")

                # Use title as header, description as body (no duplication)
                display_title = title if title else desc[:120]
                display_desc = desc if desc != title else ""

                # Metadata
                meta_items = []
                if issue.get("location"):
                    meta_items.append(f"Локация: {issue['location']}")
                if issue.get("heuristic"):
                    meta_items.append(f"Эвристика: {issue['heuristic']}")
                if issue.get("affected_nodes"):
                    meta_items.append(f"Затронуто элементов: {issue['affected_nodes']}")
                if issue.get("emotion"):
                    meta_items.append(f"Эмоция: {issue['emotion']}")
                if issue.get("step_id"):
                    meta_items.append(f"Шаг #{issue['step_id']}")
                if issue.get("help_url"):
                    meta_items.append(f'<a href="{issue["help_url"]}" target="_blank" style="color: #3b82f6;">Подробнее</a>')

                meta_html = "".join(f"<span>{m}</span>" for m in meta_items)

                # WCAG tags as separate badges
                wcag_html = ""
                wcag_tags = issue.get("wcag_tags", [])
                rule_id = issue.get("rule_id", "")
                if wcag_tags or rule_id:
                    tags_html = ""
                    if rule_id:
                        tags_html += f'<span class="wcag-tag rule-id">{rule_id}</span>'
                    for tag in wcag_tags:
                        level_class = "level-aa" if "aa" in tag else "level-a"
                        tags_html += f'<span class="wcag-tag {level_class}">{tag.upper()}</span>'
                    wcag_html = f'<div class="wcag-tags">{tags_html}</div>'

                rec = issue.get("recommendation", "")
                rec_html = ""
                if rec:
                    rec_html = f'''
                    <div style="margin-top: 12px; padding: 12px; background: #f0fdf4; border-radius: 6px; border-left: 3px solid #22c55e;">
                        <strong style="color: #166534;">Рекомендация:</strong> {rec}
                    </div>
                    '''

                issues_html += f"""
                <div class="issue-item {sev}">
                    <div class="issue-header">
                        <div class="issue-title">{display_title}</div>
                        <span class="issue-source">{source}</span>
                    </div>
                    {f'<div class="issue-description">{display_desc}</div>' if display_desc else ''}
                    {wcag_html}
                    {f'<div class="issue-meta">{meta_html}</div>' if meta_items else ''}
                    {rec_html}
                </div>
                """

            groups_html += f"""
            <div class="issue-group">
                <div class="issue-group-header">
                    <span class="badge {sev}">{severity_names.get(sev, sev).upper()}</span>
                    <span style="color: #6b7280;">{len(grouped[sev])}</span>
                </div>
                {issues_html}
            </div>
            """

        return f"""
        <div class="card">
            <h2>Все выявленные проблемы ({len(issues)})</h2>
            <p style="color: #6b7280; margin-bottom: 20px;">
                Проблемы сгруппированы по серьёзности. Рекомендуется начать с критических.
            </p>
            <div class="issues-section">
                {groups_html}
            </div>
        </div>
        """

    def _render_recommendations_detailed(self) -> str:
        recs = self.data.get("recommendations", [])

        if not recs:
            return ""

        rationales = {
            "Доступность": "Проблемы доступности исключают часть пользователей и могут нарушать законодательные требования.",
            "Интерфейс": "Визуальные проблемы влияют на первое впечатление и доверие пользователей к сайту.",
            "Навигация": "Проблемы навигации напрямую влияют на способность пользователей достигать своих целей.",
            "UX": "Эмоциональный опыт пользователя определяет лояльность и вероятность повторного визита."
        }

        priority_labels_ru = {
            "critical": "КРИТИЧНО",
            "high": "ВЫСОКИЙ",
            "medium": "СРЕДНИЙ",
            "low": "НИЗКИЙ"
        }

        recs_html = ""
        for i, rec in enumerate(recs, 1):
            priority = rec.get("priority", "medium")
            category = rec.get("category", "")
            text = rec.get("text", "")
            source = rec.get("source", "")
            priority_label = priority_labels_ru.get(priority, priority.upper())

            recs_html += f"""
            <div class="rec-item {priority}">
                <div class="rec-header">
                    <span class="rec-category">{category}</span>
                    <span class="rec-priority {priority}">{priority_label}</span>
                </div>
                <div class="rec-title">{i}. {text}</div>
                <div class="rec-source">{source}</div>
            </div>
            """

        return f"""
        <div class="card">
            <h2>Рекомендации по улучшению ({len(recs)})</h2>
            <p style="color: #6b7280; margin-bottom: 20px;">
                Приоритизированный список действий. Рекомендуется выполнять в указанном порядке.
            </p>
            {recs_html}
        </div>
        """

    def _render_footer(self) -> str:
        generated = self.data.get("generated_at", "")

        return f"""
        <div class="footer">
            <p><strong>UX AI Audit System</strong></p>
            <p>Дата генерации: {generated}</p>
        </div>
        """

    def save_html(self, output_path: Path) -> Path:
        html = self.generate_html()
        output_path = Path(output_path)
        output_path.write_text(html, encoding="utf-8")
        return output_path

    def save_pdf(self, output_path: Path, html_path: Path = None) -> Path:
        """
        Generate PDF report.

        Saves HTML first (if html_path provided), then converts to PDF via Playwright.

        Args:
            output_path: Destination PDF path
            html_path: Optional path for intermediate HTML (defaults to same dir as pdf)

        Returns:
            Path to generated PDF, or raises RuntimeError on failure
        """
        from .pdf_exporter import generate_pdf

        output_path = Path(output_path)

        # Save HTML to a temp location if not specified
        if html_path is None:
            html_path = output_path.with_suffix(".html")

        self.save_html(html_path)

        success = generate_pdf(html_path, output_path)
        if not success:
            raise RuntimeError(f"PDF generation failed. HTML saved at: {html_path}")

        return output_path
