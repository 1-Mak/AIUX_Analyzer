"""
Module E - Report Generator
Generates structured reports from all module results
"""
import json
import math
import re
import logging
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


logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive UX audit reports"""

    def __init__(self, session_dir: Path, audit_results: Dict[str, Any]):
        self.session_dir = Path(session_dir)
        self.audit_results = audit_results
        self.report_data = {}
        self._llm = None  # lazy init

    def generate_report(self) -> Dict[str, Any]:
        # Build step-by-step so LLM summary can access overall_score
        self.report_data["metadata"] = self._generate_metadata()
        self.report_data["behavioral_metrics"] = self._calculate_behavioral_metrics()
        self.report_data["overall_score"] = self._calculate_overall_score()
        self.report_data["executive_summary"] = self._generate_executive_summary()
        self.report_data["module_summaries"] = self._generate_module_summaries()
        self.report_data["behavioral_timeline"] = self._generate_behavioral_timeline()
        self.report_data["all_issues"] = self._collect_all_issues()
        self.report_data["recommendations"] = self._generate_recommendations()
        self.report_data["generated_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")
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

    def _load_behavioral_steps(self) -> List[Dict[str, Any]]:
        """Load behavioral log steps from Module B output file"""
        log_file = self.session_dir / "module_b_behavioral_log.json"
        if not log_file.exists():
            return []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _calculate_behavioral_metrics(self) -> Dict[str, Any]:
        """
        Calculate 13 formal UX metrics (M1-M13) from module outputs.

        Groups:
        - Task Effectiveness (M1-M5): completion, steps, efficiency, errors, backtracks
        - Interface Quality (M6-M9): lostness, visual/accessibility issues
        - Subjective Experience (M10-M13): sentiment score, trend, pain points, SUS proxy
        """
        config = self.audit_results.get("config", {})
        module_b = self.audit_results.get("module_b_results", {}) or {}
        module_a = self.audit_results.get("module_a_results", {}) or {}
        module_c = self.audit_results.get("module_c_results", {}) or {}
        module_d = self.audit_results.get("module_d_results", {}) or {}

        steps = self._load_behavioral_steps()
        task_status = self._normalize_task_status(module_b.get("task_status", ""))
        actual_steps = module_b.get("total_steps", len(steps))
        optimal_steps = config.get("optimal_steps")
        min_pages = config.get("min_pages_required")

        # Count from behavioral log
        error_count = sum(1 for s in steps if s.get("status") == "failure")
        backtrack_count = sum(1 for s in steps if s.get("is_backtrack"))

        # Unique pages and total page visits (for lostness)
        urls = [s.get("url", "") for s in steps if s.get("url")]
        unique_pages = len(set(urls))
        total_page_visits = len(urls)

        # === M1: Task Completed ===
        m1_task_completed = task_status == "completed"

        # === M2: Steps to Goal ===
        m2_steps_to_goal = actual_steps

        # === M3: Relative Efficiency (Bevan VUUM 2008) ===
        m3_relative_efficiency = None
        if optimal_steps and actual_steps > 0:
            m3_relative_efficiency = round(min(optimal_steps / actual_steps, 1.0), 3)

        # === M4: Error Count ===
        m4_error_count = error_count

        # === M5: Backtrack Count ===
        m5_backtrack_count = backtrack_count

        # === M6: Lostness (Smith 1996) ===
        # L = sqrt((N/S - 1)^2 + (R/N - 1)^2)
        # N = unique pages, S = total page visits, R = min pages required
        m6_lostness = None
        if min_pages and unique_pages > 0 and total_page_visits > 0:
            n_over_s = unique_pages / total_page_visits
            r_over_n = min_pages / unique_pages
            m6_lostness = round(math.sqrt((n_over_s - 1) ** 2 + (r_over_n - 1) ** 2), 3)

        # === M7: Visual Issues Count (Module A) ===
        m7_visual_issues = module_a.get("total_issues", 0) if "error" not in module_a and "skipped" not in module_a else None

        # === M8: Accessibility Issues Count (Module C) ===
        m8_accessibility_issues = module_c.get("total_issues", 0) if "error" not in module_c and "skipped" not in module_c else None

        # === M9: Critical Issues Count (A + C combined) ===
        m9_critical = 0
        if m7_visual_issues is not None:
            m9_critical += module_a.get("severity_breakdown", {}).get("critical", 0)
        if m8_accessibility_issues is not None:
            m9_critical += module_c.get("by_impact", {}).get("critical", 0)
        m9_critical_issues = m9_critical if (m7_visual_issues is not None or m8_accessibility_issues is not None) else None

        # === M10: Session Score (Module D) ===
        m10_session_score = module_d.get("session_score") if "error" not in module_d and "skipped" not in module_d else None

        # === M11: Emotional Trend ===
        m11_trend = module_d.get("trend") if m10_session_score is not None else None

        # === M12: Pain Points Count ===
        m12_pain_points = module_d.get("pain_points_count", 0) if m10_session_score is not None else None

        # === M13: SUS Proxy ===
        # Normalized: (session_score + 1) * 50 → scale 0-100
        m13_sus_proxy = None
        if m10_session_score is not None:
            m13_sus_proxy = round((m10_session_score + 1) * 50, 1)

        return {
            "task_effectiveness": {
                "M1_task_completed": m1_task_completed,
                "M2_steps_to_goal": m2_steps_to_goal,
                "M3_relative_efficiency": m3_relative_efficiency,
                "M4_error_count": m4_error_count,
                "M5_backtrack_count": m5_backtrack_count,
            },
            "interface_quality": {
                "M6_lostness": m6_lostness,
                "M7_visual_issues": m7_visual_issues,
                "M8_accessibility_issues": m8_accessibility_issues,
                "M9_critical_issues": m9_critical_issues,
            },
            "subjective_experience": {
                "M10_session_score": m10_session_score,
                "M11_trend": m11_trend,
                "M12_pain_points": m12_pain_points,
                "M13_sus_proxy": m13_sus_proxy,
            },
            "reference": {
                "optimal_steps": optimal_steps,
                "min_pages_required": min_pages,
                "unique_pages": unique_pages,
                "total_page_visits": total_page_visits,
            }
        }

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

        # Module B score — based on behavioral metrics (M3 + M1 + penalties)
        module_b = self.audit_results.get("module_b_results", {})
        bm = self.report_data.get("behavioral_metrics", {})
        if module_b and "error" not in module_b and "skipped" not in module_b:
            te = bm.get("task_effectiveness", {})
            m1 = te.get("M1_task_completed", False)
            m3 = te.get("M3_relative_efficiency")
            m4 = te.get("M4_error_count", 0)
            m5 = te.get("M5_backtrack_count", 0)

            # Base: efficiency if available, else status-based fallback
            if m3 is not None:
                base = m3
            else:
                task_status = self._normalize_task_status(module_b.get("task_status", "failed"))
                base = {"completed": 0.8, "partial": 0.5, "failed": 0.2, "max_steps_reached": 0.3}.get(task_status, 0.4)

            # Task completion bonus/penalty
            if m1:
                base = min(base + 0.15, 1.0)
            else:
                base *= 0.6

            # Error & backtrack penalties (diminishing)
            penalty = min(m4 * 0.04 + m5 * 0.03, 0.3)
            scores["behavioral"] = round(max(0, base - penalty), 3)
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

        # Module A — aggregated visual findings
        module_a = self.audit_results.get("module_a_results", {})
        if module_a and "total_issues" in module_a:
            total = module_a["total_issues"]
            severity = module_a.get("severity_breakdown", {})
            critical_count = severity.get("critical", 0)
            high = severity.get("high", 0)

            if critical_count > 0 or high > 0:
                # Collect top heuristic violations for summary
                top_heuristics = []
                module_a_file = self.session_dir / "module_a_visual_analysis.json"
                if module_a_file.exists():
                    try:
                        with open(module_a_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        for issue in data.get("issues", []):
                            h = issue.get("heuristic", "")
                            if h and h not in top_heuristics and issue.get("severity", "").lower() in ("critical", "high"):
                                top_heuristics.append(h)
                            if len(top_heuristics) >= 3:
                                break
                    except Exception:
                        pass

                detail = f"Критических: {critical_count}, серьёзных: {high}"
                if top_heuristics:
                    detail += f". Нарушены эвристики: {'; '.join(top_heuristics)}"
                critical_findings.append({
                    "title": f"Интерфейс: {critical_count + high} серьёзных проблем юзабилити",
                    "detail": detail,
                    "source": "Визуальный анализ",
                    "recommendation": "Пересмотреть дизайн критичных элементов с учётом эвристик Нильсена"
                })

            summary_points.append(f"Визуальный анализ выявил {total} проблем интерфейса (критических: {critical_count}, серьёзных: {high})")

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
                    "source": "Поведенческий анализ",
                    "recommendation": "Упростить навигационный путь к целевому контенту, добавить подсказки и хлебные крошки"
                })
            elif status == "max_steps_reached":
                critical_findings.append({
                    "title": f"Задача не завершена за {steps} шагов",
                    "detail": "Навигация слишком сложная — пользователь не нашёл путь к цели",
                    "source": "Поведенческий анализ",
                    "recommendation": "Сократить глубину навигации, добавить поиск и быстрые ссылки на ключевые разделы"
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
                        "source": "Поведенческий анализ",
                        "recommendation": "Уменьшить количество кликов до ключевого контента, рассмотреть реструктуризацию меню"
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

        # Module C — aggregated summary instead of per-rule listing
        module_c = self.audit_results.get("module_c_results", {})
        if module_c and "total_issues" in module_c:
            total = module_c["total_issues"]
            by_impact = module_c.get("by_impact", {})
            critical_count = by_impact.get("critical", 0)
            serious = by_impact.get("serious", 0)
            moderate = by_impact.get("moderate", 0)

            # Count total affected elements from detailed scan
            total_elements = 0
            top_rules_ru = []
            module_c_file = self.session_dir / "module_c_accessibility_scan.json"
            if module_c_file.exists():
                try:
                    with open(module_c_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for issue in data.get("issues", data.get("all_issues", [])):
                        occ = issue.get("total_occurrences", len(issue.get("nodes", [])))
                        total_elements += occ
                        if issue.get("impact") in ("critical", "serious") and len(top_rules_ru) < 3:
                            rule_id = issue.get("id", "")
                            ru = translate_axe_rule(rule_id)
                            if ru:
                                top_rules_ru.append(ru.lower())
                except Exception:
                    pass

            if critical_count > 0 or serious > 0:
                detail_parts = []
                if critical_count:
                    detail_parts.append(f"критических: {critical_count}")
                if serious:
                    detail_parts.append(f"серьёзных: {serious}")
                detail = f"Затронуто {total_elements} элементов ({', '.join(detail_parts)})"
                if top_rules_ru:
                    detail += f". Основные: {'; '.join(top_rules_ru)}"
                critical_findings.append({
                    "title": f"Доступность: {critical_count + serious} критических и серьёзных нарушений WCAG",
                    "detail": detail,
                    "source": "Аудит доступности",
                    "recommendation": "Провести аудит доступности с помощью WAVE/axe и исправить в первую очередь критические нарушения"
                })

            if total > 0:
                summary_points.append(f"Аудит доступности выявил {total} проблем ({critical_count} критических, {serious} серьёзных)")

        # Module D
        module_d = self.audit_results.get("module_d_results", {})
        if module_d and "session_score" in module_d:
            score = module_d["session_score"]
            trend = module_d.get("trend", "stable")
            pain_points = module_d.get("pain_points_count", 0)

            if score < -0.3:
                trend_ru = {"improving": "улучшение", "stable": "стабильно", "declining": "ухудшение"}.get(trend, trend)
                detail = f"Оценка сессии: {score:+.2f}, тренд: {trend_ru}"
                if pain_points > 0:
                    detail += f", болевых точек: {pain_points}"
                critical_findings.append({
                    "title": "Негативный эмоциональный опыт пользователя",
                    "detail": detail,
                    "source": "Анализ эмоций",
                    "recommendation": "Провести юзабилити-тестирование с реальными пользователями для выявления причин фрустрации"
                })

            if trend == "declining":
                summary_points.append("Эмоциональный тренд: ухудшение к концу сессии")
            if pain_points > 0:
                summary_points.append(f"Выявлено {pain_points} болевых точек")

        modules_analyzed = sum(1 for m in ["module_a", "module_b", "module_c", "module_d"]
                               if self.audit_results.get(f"{m}_results", {})
                               and "error" not in self.audit_results.get(f"{m}_results", {})
                               and "skipped" not in self.audit_results.get(f"{m}_results", {}))

        # Replace rule-based bullet points with LLM-generated summary
        llm_points = self._llm_generate_summary_points(summary_points, critical_findings)
        if llm_points:
            summary_points = llm_points

        return {
            "summary_points": summary_points,
            "critical_findings": critical_findings,
            "modules_analyzed": modules_analyzed
        }

    def _get_llm(self):
        """Lazy-init OpenAIHelper for report generation."""
        if self._llm is None:
            try:
                from src.utils.openai_helper import OpenAIHelper
                from src.config import OPENAI_API_KEY
                self._llm = OpenAIHelper(api_key=OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Cannot init LLM for report: {e}")
        return self._llm

    def _llm_generate_summary_points(
        self,
        fallback_points: List[str],
        critical_findings: List[Dict]
    ) -> Optional[List[str]]:
        """Generate executive summary bullet points via LLM. Returns None on failure."""
        try:
            llm = self._get_llm()
            if not llm:
                return None

            config = self.audit_results.get("config", {})
            score = self.report_data.get("overall_score", {}) if self.report_data else {}
            overall_pct = int(score.get("overall", 0) * 100) if score else 0
            rating_label = score.get("rating_label", "") if score else ""

            module_a = self.audit_results.get("module_a_results", {}) or {}
            module_b = self.audit_results.get("module_b_results", {}) or {}
            module_c = self.audit_results.get("module_c_results", {}) or {}
            module_d = self.audit_results.get("module_d_results", {}) or {}

            task_status_raw = module_b.get("task_status", "")
            task_status = self._normalize_task_status(task_status_raw)
            nav = self._compute_navigation_metrics()

            facts = [
                f"Сайт: {config.get('url', 'N/A')}",
                f"Задача пользователя: {config.get('task', 'N/A')}",
                f"Общий UX-балл: {overall_pct}/100 ({rating_label})",
                f"Задача {'выполнена' if task_status == 'completed' else 'не выполнена'} за {module_b.get('total_steps', '?')} шагов",
            ]
            if nav.get("navigation_efficiency") is not None:
                facts.append(f"Навигационная эффективность: {int(nav['navigation_efficiency'] * 100)}% (оптимум {nav.get('optimal_steps', '?')} шагов)")
            if module_a.get("total_issues"):
                facts.append(f"Визуальный анализ: {module_a['total_issues']} проблем (критических: {module_a.get('severity_breakdown', {}).get('critical', 0)})")
            if module_c.get("total_issues"):
                by = module_c.get("by_impact", {})
                facts.append(f"Доступность (WCAG): {module_c['total_issues']} нарушений, критических: {by.get('critical', 0)}, серьёзных: {by.get('serious', 0)}")
            if module_d.get("session_score") is not None:
                facts.append(f"Эмоциональный опыт: {module_d.get('trend', 'stable')}, оценка сессии {module_d['session_score']:.2f}, болевых точек: {module_d.get('pain_points_count', 0)}")
            if critical_findings:
                top = "; ".join(f['title'] for f in critical_findings[:3])
                facts.append(f"Топ критических находок: {top}")

            facts_text = "\n".join(f"- {f}" for f in facts)
            prompt = f"""Ты UX-аналитик. На основе данных аудита напиши 4–6 аналитических тезисов на русском языке.
Каждый тезис — законченная мысль (1–2 предложения), раскрывающая ключевой вывод для владельца сайта.
Не пересказывай цифры механически — делай выводы. Не используй маркеры или нумерацию.
Верни JSON-массив строк: ["тезис 1", "тезис 2", ...]

Данные аудита:
{facts_text}
"""
            response = llm.complete_text(prompt, max_tokens=600)
            # Extract JSON array
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            points = json.loads(response)
            if isinstance(points, list) and all(isinstance(p, str) for p in points):
                return points
        except Exception as e:
            logger.warning(f"LLM summary generation failed: {e}")
        return None

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
                    "reasoning": step.get("agent_thought", ""),
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
        all_issues = self._deduplicate_issues(all_issues)
        return all_issues

    def _deduplicate_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove cross-source duplicate issues using word-overlap (Jaccard similarity).
        Same source issues are never merged. Within a duplicate pair, keeps higher severity.
        """
        severity_rank = {
            "critical": 0, "high": 1, "serious": 1,
            "medium": 2, "moderate": 2, "low": 3, "minor": 3
        }

        def word_set(text: str):
            return set(re.sub(r'[^\w\s]', '', text.lower()).split())

        def jaccard(a: set, b: set) -> float:
            if not a or not b:
                return 0.0
            return len(a & b) / len(a | b)

        kept: List[Dict[str, Any]] = []
        for issue in issues:
            iwords = word_set(issue.get("title", ""))
            merged = False
            for idx, existing in enumerate(kept):
                # Only deduplicate across different sources
                if issue.get("source") == existing.get("source"):
                    continue
                ewords = word_set(existing.get("title", ""))
                if jaccard(iwords, ewords) >= 0.35:
                    # Keep higher severity
                    i_rank = severity_rank.get(issue.get("severity", "medium").lower(), 99)
                    e_rank = severity_rank.get(existing.get("severity", "medium").lower(), 99)
                    if i_rank < e_rank:
                        kept[idx] = issue
                    merged = True
                    break
            if not merged:
                kept.append(issue)

        return kept

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
