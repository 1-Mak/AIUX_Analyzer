"""
Module E - Report Generator
Generates structured reports from all module results
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from .report_config import (
    REPORT_SECTIONS,
    SEVERITY_ORDER,
    RATING_THRESHOLDS,
    SCORE_WEIGHTS,
    ISSUE_ICONS,
    MODULE_STATUS,
    PERSONA_CONTEXT,
    translate_axe_rule
)


class ReportGenerator:
    """Generates comprehensive UX audit reports"""

    def __init__(self, session_dir: Path, audit_results: Dict[str, Any]):
        self.session_dir = Path(session_dir)
        self.audit_results = audit_results
        self.report_data = {}

    def generate_report(self) -> Dict[str, Any]:
        self.report_data = {
            "metadata": self._generate_metadata(),
            "overall_score": self._calculate_overall_score(),
            "executive_summary": self._generate_executive_summary(),
            "module_summaries": self._generate_module_summaries(),
            "behavioral_timeline": self._generate_behavioral_timeline(),
            "all_issues": self._collect_all_issues(),
            "recommendations": self._generate_recommendations(),
            "generated_at": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        return self.report_data

    def _generate_metadata(self) -> Dict[str, Any]:
        config = self.audit_results.get("config", {})
        persona_key = config.get("persona", "student")
        persona_info = PERSONA_CONTEXT.get(persona_key, PERSONA_CONTEXT["student"])

        return {
            "session_id": self.audit_results.get("session_id", "unknown"),
            "url": config.get("url", "N/A"),
            "task": config.get("task", "N/A"),
            "persona": {
                "key": persona_key,
                "name": persona_info["name_ru"],
                "description": persona_info["description_ru"]
            },
            "modules_run": self._get_modules_status()
        }

    def _get_modules_status(self) -> Dict[str, str]:
        status = {}
        for module in ["module_a", "module_b", "module_c", "module_d"]:
            result = self.audit_results.get(f"{module}_results", {})
            if not result:
                status[module] = "not_run"
            elif "error" in result:
                status[module] = "error"
            elif "skipped" in result:
                status[module] = "skipped"
            else:
                status[module] = "success"
        return status

    def _normalize_task_status(self, status: str) -> str:
        """Normalize various task_status values to canonical form"""
        mapping = {
            "max_steps": "max_steps_reached",
            "max_steps_reached": "max_steps_reached",
            "completed": "completed",
            "failed": "failed",
            "partial": "partial",
            "in_progress": "max_steps_reached",
        }
        return mapping.get(status, status)

    def _compute_navigation_metrics(self) -> Dict[str, Any]:
        """
        Compute scenario-specific navigation efficiency metrics.
        Requires optimal_steps and min_pages_required in config.
        """
        config = self.audit_results.get("config", {})
        optimal_steps = config.get("optimal_steps")
        min_pages_required = config.get("min_pages_required")

        module_b = self.audit_results.get("module_b_results", {})
        actual_steps = module_b.get("total_steps", 0)
        task_status = self._normalize_task_status(module_b.get("task_status", ""))

        # Count unique pages from behavioral log
        unique_pages = 0
        log_file = self.session_dir / "module_b_behavioral_log.json"
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    steps = json.load(f)
                unique_pages = len(set(s.get("url", "") for s in steps if s.get("url")))
            except Exception:
                pass

        # Navigation efficiency: optimal / actual, penalised if task not done
        nav_efficiency = None
        if optimal_steps and actual_steps > 0:
            raw = optimal_steps / actual_steps
            if task_status not in ("completed",):
                raw *= 0.6  # penalty for incomplete task
            nav_efficiency = round(min(raw, 1.0), 2)

        # Pages coverage: unique pages visited vs minimum required
        pages_coverage = None
        pages_ok = None
        if min_pages_required:
            pages_coverage = round(min(unique_pages / min_pages_required, 1.0), 2) if unique_pages else 0.0
            pages_ok = unique_pages >= min_pages_required

        return {
            "scenario_id": config.get("scenario_id"),
            "optimal_steps": optimal_steps,
            "actual_steps": actual_steps,
            "unique_pages": unique_pages,
            "min_pages_required": min_pages_required,
            "navigation_efficiency": nav_efficiency,
            "pages_coverage": pages_coverage,
            "pages_ok": pages_ok
        }

    def _calculate_overall_score(self) -> Dict[str, Any]:
        scores = {}
        weights_used = {}

        # Module A score
        module_a = self.audit_results.get("module_a_results", {})
        if module_a and "error" not in module_a and "skipped" not in module_a:
            severity = module_a.get("severity_breakdown", {})
            critical = severity.get("critical", 0)
            high = severity.get("high", 0)
            total_issues = module_a.get("total_issues", 0)
            deductions = critical * 20 + high * 10 + (total_issues - critical - high) * 5
            scores["visual"] = max(0, min(1, 1 - deductions / 100))
            weights_used["visual"] = SCORE_WEIGHTS["visual"]

        # Module B score
        module_b = self.audit_results.get("module_b_results", {})
        if module_b and "error" not in module_b and "skipped" not in module_b:
            task_status = self._normalize_task_status(module_b.get("task_status", "failed"))
            status_scores = {"completed": 1.0, "partial": 0.6, "failed": 0.3, "max_steps_reached": 0.4}
            scores["behavioral"] = status_scores.get(task_status, 0.5)
            weights_used["behavioral"] = SCORE_WEIGHTS["behavioral"]

        # Module C score
        module_c = self.audit_results.get("module_c_results", {})
        if module_c and "error" not in module_c and "skipped" not in module_c:
            by_impact = module_c.get("by_impact", {})
            critical = by_impact.get("critical", 0)
            serious = by_impact.get("serious", 0)
            moderate = by_impact.get("moderate", 0)
            if critical > 0:
                scores["accessibility"] = 0.2
            elif serious > 3:
                scores["accessibility"] = 0.4
            elif serious > 0:
                scores["accessibility"] = 0.6
            elif moderate > 0:
                scores["accessibility"] = 0.8
            else:
                scores["accessibility"] = 1.0
            weights_used["accessibility"] = SCORE_WEIGHTS["accessibility"]

        # Module D score
        module_d = self.audit_results.get("module_d_results", {})
        if module_d and "error" not in module_d and "skipped" not in module_d:
            session_score = module_d.get("session_score", 0)
            scores["sentiment"] = (session_score + 1) / 2
            weights_used["sentiment"] = SCORE_WEIGHTS["sentiment"]

        # Weighted average
        if scores and weights_used:
            total_weight = sum(weights_used.values())
            weighted_sum = sum(scores[k] * weights_used[k] for k in scores)
            overall = weighted_sum / total_weight if total_weight > 0 else 0
        else:
            overall = 0

        rating = "critical"
        for level, cfg in sorted(RATING_THRESHOLDS.items(), key=lambda x: x[1]["min_score"], reverse=True):
            if overall >= cfg["min_score"]:
                rating = level
                break

        nav = self._compute_navigation_metrics()

        return {
            "overall": round(overall, 2),
            "rating": rating,
            "rating_label": RATING_THRESHOLDS[rating]["label_ru"],
            "rating_color": RATING_THRESHOLDS[rating]["color"],
            "breakdown": {k: round(v, 2) for k, v in scores.items()},
            "weights": weights_used,
            "navigation_metrics": nav
        }

    def _generate_executive_summary(self) -> Dict[str, Any]:
        summary_points = []
        critical_findings = []

        # Module A
        module_a = self.audit_results.get("module_a_results", {})
        if module_a and "total_issues" in module_a:
            total = module_a["total_issues"]
            severity = module_a.get("severity_breakdown", {})
            critical_count = severity.get("critical", 0)
            high = severity.get("high", 0)

            module_a_file = self.session_dir / "module_a_visual_analysis.json"
            if module_a_file.exists() and (critical_count > 0 or high > 0):
                try:
                    with open(module_a_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for issue in data.get("issues", []):
                            sev = issue.get("severity", "").lower()
                            if sev == "critical":
                                critical_findings.append({
                                    "title": issue.get("title", "Критическая визуальная проблема"),
                                    "detail": issue.get("description", "")[:200],
                                    "source": "Визуальный анализ"
                                })
                            elif sev == "high" and len(critical_findings) < 5:
                                critical_findings.append({
                                    "title": issue.get("title", "Серьёзная проблема юзабилити"),
                                    "detail": issue.get("description", "")[:200],
                                    "source": "Визуальный анализ"
                                })
                except Exception:
                    if critical_count > 0:
                        critical_findings.append({
                            "title": f"Найдено {critical_count} критических визуальных проблем",
                            "detail": "Проблемы требуют немедленного внимания",
                            "source": "Визуальный анализ"
                        })

            if high > 0:
                summary_points.append(f"Визуальный анализ: {high} серьёзных проблем юзабилити")
            summary_points.append(f"Всего выявлено {total} проблем интерфейса")

        # Module B
        module_b = self.audit_results.get("module_b_results", {})
        if module_b and "task_status" in module_b:
            status = self._normalize_task_status(module_b["task_status"])
            steps = module_b.get("total_steps", 0)
            reason = module_b.get("termination_reason", "")

            if status == "completed":
                summary_points.append(f"Задача выполнена за {steps} шагов")
            elif status == "failed":
                critical_findings.append({
                    "title": "Задача не была выполнена",
                    "detail": f"Пользователь не смог достичь цели. Причина: {reason}",
                    "source": "Поведенческий анализ"
                })
            elif status == "max_steps_reached":
                critical_findings.append({
                    "title": f"Задача не завершена за {steps} шагов",
                    "detail": "Навигация слишком сложная — пользователь не нашёл путь к цели",
                    "source": "Поведенческий анализ"
                })

            # Navigation efficiency insight
            nav = self._compute_navigation_metrics()
            nav_eff = nav.get("navigation_efficiency")
            optimal = nav.get("optimal_steps")
            if nav_eff is not None and optimal:
                if nav_eff < 0.4:
                    critical_findings.append({
                        "title": f"Низкая навигационная эффективность: {int(nav_eff * 100)}%",
                        "detail": f"Пользователь затратил {steps} шагов при оптимальных {optimal} — путь в {round(steps / optimal, 1)}× длиннее нормы",
                        "source": "Поведенческий анализ"
                    })
                elif nav_eff < 0.7:
                    summary_points.append(
                        f"Эффективность навигации: {int(nav_eff * 100)}% ({steps} шагов при норме {optimal})"
                    )
                else:
                    summary_points.append(
                        f"Навигация близка к оптимальной: {steps} шагов при норме {optimal}"
                    )

            pages_ok = nav.get("pages_ok")
            min_pages = nav.get("min_pages_required")
            unique = nav.get("unique_pages", 0)
            if pages_ok is False:
                summary_points.append(
                    f"Охват страниц недостаточен: посещено {unique} из {min_pages} минимально необходимых"
                )

        # Module C — fix: use "issues" key (actual axe output format)
        module_c = self.audit_results.get("module_c_results", {})
        if module_c and "total_issues" in module_c:
            total = module_c["total_issues"]
            by_impact = module_c.get("by_impact", {})
            critical_count = by_impact.get("critical", 0)
            serious = by_impact.get("serious", 0)

            module_c_file = self.session_dir / "module_c_accessibility_scan.json"
            if module_c_file.exists() and (critical_count > 0 or serious > 0):
                try:
                    with open(module_c_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for issue in data.get("issues", data.get("all_issues", [])):
                            impact = issue.get("impact", "")
                            occurrences = issue.get("total_occurrences", len(issue.get("nodes", [])))
                            rule_id = issue.get("id", "")
                            title_ru = translate_axe_rule(rule_id, issue.get("help", ""))
                            if impact == "critical":
                                critical_findings.append({
                                    "title": title_ru,
                                    "detail": f"Затронуто элементов: {occurrences}",
                                    "source": "Аудит доступности"
                                })
                            elif impact == "serious" and len(critical_findings) < 7:
                                critical_findings.append({
                                    "title": title_ru,
                                    "detail": f"Затронуто элементов: {occurrences}",
                                    "source": "Аудит доступности"
                                })
                except Exception:
                    if critical_count > 0:
                        critical_findings.append({
                            "title": f"Найдено {critical_count} критических проблем доступности",
                            "detail": "Нарушения WCAG требуют немедленного исправления",
                            "source": "Аудит доступности"
                        })

            if serious > 0:
                summary_points.append(f"Доступность: {serious} серьёзных нарушений WCAG")
            summary_points.append(f"Аудит доступности выявил {total} проблем")

        # Module D
        module_d = self.audit_results.get("module_d_results", {})
        if module_d and "session_score" in module_d:
            score = module_d["session_score"]
            trend = module_d.get("trend", "stable")
            pain_points = module_d.get("pain_points_count", 0)

            if score < -0.3:
                module_d_file = self.session_dir / "module_d_sentiment_analysis.json"
                if module_d_file.exists():
                    try:
                        with open(module_d_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            for point in data.get("pain_points", [])[:2]:
                                critical_findings.append({
                                    "title": f"Фрустрация на шаге #{point.get('step_id', '?')}",
                                    "detail": point.get("issue", "")[:150],
                                    "source": "Анализ эмоций"
                                })
                    except Exception:
                        critical_findings.append({
                            "title": "Негативный эмоциональный опыт пользователя",
                            "detail": f"Оценка сессии: {score:.2f}",
                            "source": "Анализ эмоций"
                        })

            if trend == "declining":
                summary_points.append("Эмоциональный тренд: ухудшение к концу сессии")
            if pain_points > 0:
                summary_points.append(f"Выявлено {pain_points} болевых точек")

        return {
            "summary_points": summary_points,
            "critical_findings": critical_findings,
            "modules_analyzed": sum(1 for m in ["module_a", "module_b", "module_c", "module_d"]
                                    if self.audit_results.get(f"{m}_results", {})
                                    and "error" not in self.audit_results.get(f"{m}_results", {})
                                    and "skipped" not in self.audit_results.get(f"{m}_results", {}))
        }

    def _generate_module_summaries(self) -> Dict[str, Any]:
        summaries = {}

        module_a = self.audit_results.get("module_a_results", {})
        if module_a and "error" not in module_a and "skipped" not in module_a:
            summaries["module_a"] = {
                "title": REPORT_SECTIONS["visual_analysis"]["title_ru"],
                "status": "success",
                "total_issues": module_a.get("total_issues", 0),
                "severity": module_a.get("severity_breakdown", {}),
                "assessment": module_a.get("overall_assessment", "")
            }

        module_b = self.audit_results.get("module_b_results", {})
        if module_b and "error" not in module_b and "skipped" not in module_b:
            # Count backtracks and UX observations from behavioral log
            backtrack_count = 0
            ux_obs_count = 0
            log_file = self.session_dir / "module_b_behavioral_log.json"
            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        steps = json.load(f)
                    backtrack_count = sum(1 for s in steps if s.get("is_backtrack"))
                    ux_obs_count = sum(1 for s in steps if s.get("ux_observation"))
                except Exception:
                    pass

            nav = self._compute_navigation_metrics()
            summaries["module_b"] = {
                "title": REPORT_SECTIONS["behavioral_analysis"]["title_ru"],
                "status": "success",
                "total_steps": module_b.get("total_steps", 0),
                "task_status": self._normalize_task_status(module_b.get("task_status", "unknown")),
                "termination_reason": module_b.get("termination_reason", ""),
                "backtrack_count": backtrack_count,
                "ux_observations_count": ux_obs_count,
                "navigation_efficiency": nav.get("navigation_efficiency"),
                "optimal_steps": nav.get("optimal_steps"),
                "unique_pages": nav.get("unique_pages", 0),
                "min_pages_required": nav.get("min_pages_required"),
                "pages_ok": nav.get("pages_ok")
            }

        module_c = self.audit_results.get("module_c_results", {})
        if module_c and "error" not in module_c and "skipped" not in module_c:
            summaries["module_c"] = {
                "title": REPORT_SECTIONS["accessibility_audit"]["title_ru"],
                "status": "success",
                "total_issues": module_c.get("total_issues", 0),
                "by_impact": module_c.get("by_impact", {}),
                "wcag_level": module_c.get("wcag_level", "AA"),
                "pages_scanned": module_c.get("pages_scanned", 0)
            }

        module_d = self.audit_results.get("module_d_results", {})
        if module_d and "error" not in module_d and "skipped" not in module_d:
            summaries["module_d"] = {
                "title": REPORT_SECTIONS["sentiment_analysis"]["title_ru"],
                "status": "success",
                "session_score": module_d.get("session_score", 0),
                "trend": module_d.get("trend", "stable"),
                "distribution": module_d.get("distribution", {}),
                "pain_points_count": module_d.get("pain_points_count", 0),
                "insights": module_d.get("insights", [])
            }

        return summaries

    def _generate_behavioral_timeline(self) -> List[Dict[str, Any]]:
        """Load behavioral steps from Module B log for timeline rendering"""
        timeline = []
        log_file = self.session_dir / "module_b_behavioral_log.json"
        if not log_file.exists():
            return timeline

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                steps = json.load(f)

            if not isinstance(steps, list):
                return timeline

            for step in steps:
                step_id = step.get("step_id", 0)
                action_taken = step.get("action_taken", "")
                action_type = "unknown"
                action_target = ""

                # Parse action_taken (JSON string from agent)
                try:
                    action_data = json.loads(action_taken) if isinstance(action_taken, str) else action_taken
                    if isinstance(action_data, dict):
                        action_type = action_data.get("action_type", "unknown")
                        action_target = str(action_data.get("target", action_data.get("value", "")))[:60]
                except Exception:
                    action_type = str(action_taken)[:30]

                timeline.append({
                    "step_id": step_id,
                    "action_type": action_type,
                    "action_target": action_target,
                    "reasoning": step.get("agent_thought", "")[:200],
                    "url": step.get("url", ""),
                    "status": step.get("status", ""),
                    "sentiment": step.get("sentiment", "NEUTRAL"),
                    "ux_observation": step.get("ux_observation"),
                    "is_backtrack": step.get("is_backtrack", False)
                })
        except Exception:
            pass

        return timeline

    def _collect_all_issues(self) -> List[Dict[str, Any]]:
        all_issues = []

        # Module A issues
        module_a_file = self.session_dir / "module_a_visual_analysis.json"
        if module_a_file.exists():
            try:
                with open(module_a_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for issue in data.get("issues", []):
                        title = issue.get("title", "")
                        desc = issue.get("description", "")
                        all_issues.append({
                            "source": "Визуальный анализ",
                            "type": "visual",
                            "severity": issue.get("severity", "medium").lower(),
                            "title": title,
                            "description": desc,
                            "location": issue.get("location", ""),
                            "heuristic": issue.get("heuristic", ""),
                            "recommendation": issue.get("recommendation", "")
                        })
            except Exception:
                pass

        # Module C issues — fix: use "issues" key
        module_c_file = self.session_dir / "module_c_accessibility_scan.json"
        if module_c_file.exists():
            try:
                with open(module_c_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for issue in data.get("issues", data.get("all_issues", [])):
                        impact = issue.get("impact", "moderate")
                        severity_map = {"critical": "critical", "serious": "high", "moderate": "medium", "minor": "low"}
                        occurrences = issue.get("total_occurrences", len(issue.get("nodes", [])))
                        rule_id = issue.get("id", "")
                        title_ru = translate_axe_rule(rule_id, issue.get("help", "Проблема доступности"))
                        desc_ru = issue.get("description_ru", "")
                        wcag_tags = [t for t in issue.get("tags", []) if t.startswith("wcag")]
                        all_issues.append({
                            "source": "Аудит доступности",
                            "type": "accessibility",
                            "severity": severity_map.get(impact, impact),
                            "title": title_ru,
                            "description": desc_ru if desc_ru != title_ru else "",
                            "wcag_tags": wcag_tags,
                            "rule_id": rule_id,
                            "affected_nodes": occurrences,
                            "help_url": issue.get("help_url", "")
                        })
            except Exception:
                pass

        # Module B UX observations (live annotations from agent)
        module_b_log = self.session_dir / "module_b_behavioral_log.json"
        if module_b_log.exists():
            try:
                with open(module_b_log, "r", encoding="utf-8") as f:
                    steps = json.load(f)
                for step in steps:
                    obs = step.get("ux_observation")
                    if not obs:
                        continue
                    # Severity: NEGATIVE emotion → high, backtrack → medium, else low
                    sentiment = step.get("sentiment", "NEUTRAL")
                    is_backtrack = step.get("is_backtrack", False)
                    if sentiment == "NEGATIVE":
                        sev = "high"
                    elif is_backtrack:
                        sev = "medium"
                    else:
                        sev = "low"
                    all_issues.append({
                        "source": "Поведенческий анализ",
                        "type": "behavioral_ux",
                        "severity": sev,
                        "title": obs,
                        "description": "",
                        "step_id": step.get("step_id", 0),
                        "url": step.get("url", ""),
                        "is_backtrack": is_backtrack
                    })
            except Exception:
                pass

        # Module D pain points
        module_d_file = self.session_dir / "module_d_sentiment_analysis.json"
        if module_d_file.exists():
            try:
                with open(module_d_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for point in data.get("pain_points", []):
                        all_issues.append({
                            "source": "Анализ эмоций",
                            "type": "sentiment",
                            "severity": "high",
                            "title": f"Болевая точка на шаге #{point.get('step_id', '?')}",
                            "description": point.get("issue", ""),
                            "emotion": point.get("emotion", ""),
                            "step_id": point.get("step_id", 0)
                        })
            except Exception:
                pass

        # Sort by severity
        def severity_key(issue):
            severity = issue.get("severity", "medium").lower()
            return SEVERITY_ORDER.index(severity) if severity in SEVERITY_ORDER else 99

        all_issues.sort(key=severity_key)
        return all_issues

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        recommendations = []

        module_a = self.audit_results.get("module_a_results", {})
        module_b = self.audit_results.get("module_b_results", {})
        module_c = self.audit_results.get("module_c_results", {})
        module_d = self.audit_results.get("module_d_results", {})

        # Critical accessibility
        if module_c and module_c.get("by_impact", {}).get("critical", 0) > 0:
            recommendations.append({
                "priority": "critical",
                "category": "Доступность",
                "text": "Немедленно исправить критические проблемы доступности (WCAG)",
                "source": "Аудит доступности"
            })

        # Critical visual
        if module_a and module_a.get("severity_breakdown", {}).get("critical", 0) > 0:
            recommendations.append({
                "priority": "critical",
                "category": "Интерфейс",
                "text": "Исправить критические проблемы визуального дизайна",
                "source": "Визуальный анализ"
            })

        # Task completion
        task_status = self._normalize_task_status(module_b.get("task_status", "")) if module_b else ""
        if task_status in ("failed", "max_steps_reached"):
            recommendations.append({
                "priority": "high",
                "category": "Навигация",
                "text": "Улучшить навигацию — пользователь не смог выполнить задачу",
                "source": "Поведенческий анализ"
            })

        # Load specific recommendations from Module A issues
        module_a_file = self.session_dir / "module_a_visual_analysis.json"
        if module_a_file.exists():
            try:
                with open(module_a_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for issue in data.get("issues", []):
                        rec = issue.get("recommendation", "")
                        sev = issue.get("severity", "").lower()
                        if rec and sev in ("critical", "high"):
                            recommendations.append({
                                "priority": "high" if sev == "high" else "critical",
                                "category": "Интерфейс",
                                "text": rec,
                                "source": f"Визуальный анализ — {issue.get('title', '')}"
                            })
            except Exception:
                pass

        # Negative sentiment
        if module_d and module_d.get("session_score", 0) < -0.3:
            recommendations.append({
                "priority": "high",
                "category": "UX",
                "text": "Провести глубокий анализ болевых точек пользователя",
                "source": "Анализ эмоций"
            })

        # Accessibility serious
        if module_c and module_c.get("by_impact", {}).get("serious", 0) > 2:
            recommendations.append({
                "priority": "medium",
                "category": "Доступность",
                "text": "Устранить серьёзные нарушения WCAG для соответствия стандартам",
                "source": "Аудит доступности"
            })

        # Module D insights as recommendations
        if module_d:
            for insight in module_d.get("insights", [])[:3]:
                clean = insight.lstrip("+-~!@#$%^&*() \t")
                if any(kw in clean.lower() for kw in ["рекомендация", "добавить", "улучшить", "исправить"]):
                    recommendations.append({
                        "priority": "medium",
                        "category": "UX",
                        "text": clean,
                        "source": "Анализ эмоций"
                    })

        return recommendations

    def save_json_report(self, filename: str = "module_e_final_report.json") -> Path:
        if not self.report_data:
            self.generate_report()

        output_path = self.session_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)

        return output_path
