"""
Sentiment aggregation and insight generation for Module D
"""
import json
from typing import List, Dict, Any, Optional
from collections import Counter

from .sentiment_config import (
    SENTIMENT_WEIGHTS,
    TREND_THRESHOLDS,
    INSIGHT_TEMPLATES,
    INSIGHT_THRESHOLDS,
    BEHAVIORAL_ADJUSTMENTS,
    STUCK_THRESHOLD_STEPS,
)


class SentimentAggregator:
    """
    Aggregates sentiment analysis results and generates insights
    """

    def __init__(self, persona_key: Optional[str] = None):
        """
        Initialize aggregator

        Args:
            persona_key: Persona context for tailored insights
        """
        self.persona_key = persona_key

    @staticmethod
    def _resolve_sentiment(step: Dict[str, Any]) -> str:
        """Hybrid sentiment: trust agent's self-report (Module B) when it expressed
        a non-neutral feeling, otherwise fall back to DeepSeek classification."""
        original = (step.get("original_sentiment") or "").upper()
        if original in ("POSITIVE", "NEGATIVE"):
            return original
        return step.get("analyzed_sentiment", "NEUTRAL")

    @staticmethod
    def _was_navigation(step: Dict[str, Any]) -> bool:
        """Whether the step's action was a click or navigation (heuristic for new-page success)"""
        action_taken = step.get("action_taken", "")
        try:
            data = json.loads(action_taken) if isinstance(action_taken, str) else action_taken
            if isinstance(data, dict):
                return data.get("action_type") in ("navigate", "click")
        except (json.JSONDecodeError, TypeError):
            pass
        return False

    @staticmethod
    def _stuck_indices(step_analysis: List[Dict[str, Any]]) -> set:
        """Return set of indices where the agent was stuck (3+ consecutive same URLs).
        All steps inside such a run are marked, except the first one entering the URL."""
        stuck: set = set()
        if not step_analysis:
            return stuck
        run_start = 0
        for i in range(1, len(step_analysis) + 1):
            same = (
                i < len(step_analysis)
                and step_analysis[i].get("url")
                and step_analysis[i].get("url") == step_analysis[run_start].get("url")
            )
            if not same:
                run_len = i - run_start
                if run_len >= STUCK_THRESHOLD_STEPS:
                    # Mark steps from STUCK_THRESHOLD_STEPS onwards within the run
                    for j in range(run_start + STUCK_THRESHOLD_STEPS - 1, i):
                        stuck.add(j)
                run_start = i
        return stuck

    def _compute_step_score(
        self,
        step: Dict[str, Any],
        idx: int,
        stuck_set: set
    ) -> float:
        """Numeric per-step score in [-1, 1]: sentiment weight + behavioral adjustments, clamped."""
        sentiment = self._resolve_sentiment(step)
        score = float(SENTIMENT_WEIGHTS.get(sentiment, 0))

        if step.get("status") == "failure":
            score += BEHAVIORAL_ADJUSTMENTS["failure"]
        if step.get("is_backtrack"):
            score += BEHAVIORAL_ADJUSTMENTS["backtrack"]
        if idx in stuck_set:
            score += BEHAVIORAL_ADJUSTMENTS["stuck_on_page"]
        if step.get("status") == "success" and not step.get("is_backtrack") and self._was_navigation(step):
            score += BEHAVIORAL_ADJUSTMENTS["success_navigation"]

        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, score))

    def calculate_session_score(self, scores: List[float]) -> float:
        """Mean of per-step numeric scores, rounded to 2 decimals. Range [-1, 1]."""
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    def calculate_trend(self, scores: List[float]) -> str:
        """
        Trend = sign of the linear regression slope of per-step numeric scores.
        Slope is per-step delta; thresholds in TREND_THRESHOLDS are tuned for that scale.
        """
        n = len(scores)
        if n < 2:
            return "stable"

        # Least-squares slope with x = 0..n-1
        x_mean = (n - 1) / 2.0
        y_mean = sum(scores) / n
        num = sum((i - x_mean) * (s - y_mean) for i, s in enumerate(scores))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope = num / den if den else 0.0

        if slope > TREND_THRESHOLDS["improving"]:
            return "improving"
        elif slope < TREND_THRESHOLDS["declining"]:
            return "declining"
        else:
            return "stable"

    def calculate_distribution(self, sentiments: List[str]) -> Dict[str, int]:
        """
        Calculate sentiment distribution

        Args:
            sentiments: List of sentiment labels

        Returns:
            Count of each sentiment type
        """
        counter = Counter(sentiments)
        return {
            "POSITIVE": counter.get("POSITIVE", 0),
            "NEUTRAL": counter.get("NEUTRAL", 0),
            "NEGATIVE": counter.get("NEGATIVE", 0)
        }

    def find_pain_points(self, step_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find pain points: NEGATIVE sentiment OR objective behavioral signals
        (failure, backtrack, stuck on the same URL).

        Each step contributes at most one pain point with the dominant cause.
        """
        pain_points = []
        stuck_set = self._stuck_indices(step_analysis)

        for idx, step in enumerate(step_analysis):
            sentiment = self._resolve_sentiment(step)
            is_failure = step.get("status") == "failure"
            is_backtrack = bool(step.get("is_backtrack"))
            is_stuck = idx in stuck_set
            is_negative = sentiment == "NEGATIVE"

            if not (is_negative or is_failure or is_backtrack or is_stuck):
                continue

            # Pick the strongest signal as the pain-point cause
            if is_failure:
                cause = "failure"
                issue = "Действие не удалось выполнить"
            elif is_stuck:
                cause = "stuck"
                issue = "Застрял на одной странице на нескольких шагах подряд"
            elif is_backtrack:
                cause = "backtrack"
                issue = "Пришлось вернуться на предыдущую страницу"
            else:
                cause = "negative_sentiment"
                issue = step.get("text_analyzed", "Негативная эмоциональная реакция")

            keywords = step.get("keywords", {})
            emotion = cause
            if cause == "negative_sentiment":
                if "frustration" in keywords:
                    emotion = "frustration"
                elif "confusion" in keywords:
                    emotion = "confusion"

            pain_points.append({
                "step_id": step.get("step_id"),
                "url": step.get("url", ""),
                "issue": issue,
                "cause": cause,
                "emotion": emotion,
                "sentiment": sentiment,
                "keywords": keywords,
            })

        return pain_points

    def correlate_with_failures(
        self,
        step_analysis: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Correlate sentiment with action status

        Args:
            step_analysis: List of analyzed steps

        Returns:
            Correlation statistics
        """
        failures = [s for s in step_analysis if s.get("status") == "failure"]
        successes = [s for s in step_analysis if s.get("status") == "success"]

        # Calculate negative rate for failures
        failure_negative = sum(
            1 for s in failures
            if self._resolve_sentiment(s) == "NEGATIVE"
        )
        failure_negative_rate = (
            failure_negative / len(failures) if failures else 0
        )

        # Calculate negative rate for successes
        success_negative = sum(
            1 for s in successes
            if self._resolve_sentiment(s) == "NEGATIVE"
        )
        success_negative_rate = (
            success_negative / len(successes) if successes else 0
        )

        return {
            "total_failures": len(failures),
            "total_successes": len(successes),
            "failure_negative_rate": round(failure_negative_rate, 2),
            "success_negative_rate": round(success_negative_rate, 2),
            "correlation_difference": round(
                failure_negative_rate - success_negative_rate, 2
            )
        }

    def generate_insights(
        self,
        summary: Dict[str, Any],
        pain_points: List[Dict[str, Any]],
        correlation: Dict[str, Any],
        task_completed: bool = False
    ) -> List[str]:
        """
        Generate human-readable insights in Russian

        Args:
            summary: Session summary with scores and distribution
            pain_points: List of identified pain points
            correlation: Failure-sentiment correlation data
            task_completed: Whether the task was completed

        Returns:
            List of insight strings
        """
        insights = []

        # 1. Trend insight
        trend = summary.get("trend", "stable")
        if trend == "improving":
            insights.append(INSIGHT_TEMPLATES["trend_improving"])
        elif trend == "declining":
            insights.append(INSIGHT_TEMPLATES["trend_declining"])
        else:
            insights.append(INSIGHT_TEMPLATES["trend_stable"])

        # 2. Negative rate insight
        distribution = summary.get("distribution", {})
        total = sum(distribution.values())
        negative_count = distribution.get("NEGATIVE", 0)
        negative_rate = negative_count / total if total > 0 else 0

        if negative_rate > INSIGHT_THRESHOLDS["high_negative_rate"]:
            insights.append(
                INSIGHT_TEMPLATES["high_negative"].format(
                    percent=int(negative_rate * 100)
                )
            )
        else:
            insights.append(
                INSIGHT_TEMPLATES["low_negative"].format(
                    percent=int(negative_rate * 100)
                )
            )

        # 3. Pain points insight
        if pain_points:
            # Group by step_id
            step_ids = [str(p["step_id"]) for p in pain_points[:3]]
            points_str = f"шаги {', '.join(step_ids)}"
            insights.append(
                INSIGHT_TEMPLATES["pain_points"].format(points=points_str)
            )
        else:
            insights.append(INSIGHT_TEMPLATES["no_pain_points"])

        # 4. Task completion insight
        if task_completed:
            insights.append(INSIGHT_TEMPLATES["task_completed"])
        else:
            if negative_rate > 0.2:
                insights.append(INSIGHT_TEMPLATES["task_not_completed"])

        # 5. Failure correlation insight
        failure_neg_rate = correlation.get("failure_negative_rate", 0)
        if (
            correlation.get("total_failures", 0) > 0 and
            failure_neg_rate > INSIGHT_THRESHOLDS["high_failure_correlation"]
        ):
            insights.append(
                INSIGHT_TEMPLATES["high_failure_correlation"].format(
                    percent=int(failure_neg_rate * 100)
                )
            )

        # 6. Recommendation based on pain points
        if pain_points:
            # Analyze keywords to suggest recommendations
            all_keywords = {}
            for p in pain_points:
                for emotion, kws in p.get("keywords", {}).items():
                    if emotion not in all_keywords:
                        all_keywords[emotion] = []
                    all_keywords[emotion].extend(kws)

            if "confusion" in all_keywords:
                insights.append(INSIGHT_TEMPLATES["recommendation_navigation"])
            elif "frustration" in all_keywords:
                # Check for search-related frustration
                frustration_kws = " ".join(all_keywords.get("frustration", []))
                if "найти" in frustration_kws or "поиск" in frustration_kws:
                    insights.append(INSIGHT_TEMPLATES["recommendation_search"])
                else:
                    insights.append(INSIGHT_TEMPLATES["recommendation_labels"])

        return insights

    def aggregate(
        self,
        step_analysis: List[Dict[str, Any]],
        task_status: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Perform full aggregation of sentiment analysis

        Args:
            step_analysis: List of analyzed steps
            task_status: Final task status

        Returns:
            Complete aggregation result
        """
        # Hybrid sentiment labels (agent self-report wins over DeepSeek when non-neutral)
        sentiments = [self._resolve_sentiment(s) for s in step_analysis]

        # Numeric per-step scores (sentiment + behavioral adjustments, clamped to [-1, 1])
        stuck_set = self._stuck_indices(step_analysis)
        step_scores = [
            self._compute_step_score(s, idx, stuck_set)
            for idx, s in enumerate(step_analysis)
        ]

        # Calculate metrics
        session_score = self.calculate_session_score(step_scores)
        trend = self.calculate_trend(step_scores)
        distribution = self.calculate_distribution(sentiments)

        # Find pain points
        pain_points = self.find_pain_points(step_analysis)

        # Correlate with failures
        correlation = self.correlate_with_failures(step_analysis)

        # Pain points breakdown by cause (for richer UI display)
        pain_points_by_cause = Counter(p.get("cause", "negative_sentiment") for p in pain_points)

        # Per-step trajectory data (step_id, resolved sentiment, numeric score) for sparkline rendering
        step_trajectory = [
            {
                "step_id": s.get("step_id"),
                "sentiment": sent,
                "score": round(sc, 3),
            }
            for s, sent, sc in zip(step_analysis, sentiments, step_scores)
        ]

        # Build summary
        total = len(sentiments)
        summary = {
            "session_score": session_score,
            "trend": trend,
            "distribution": distribution,
            "positive_rate": round(distribution["POSITIVE"] / total, 2) if total else 0,
            "negative_rate": round(distribution["NEGATIVE"] / total, 2) if total else 0,
            "failure_negative_correlation": correlation["failure_negative_rate"],
            "step_scores": [round(s, 3) for s in step_scores],
            "step_trajectory": step_trajectory,
            "pain_points_by_cause": dict(pain_points_by_cause),
        }

        # Generate insights
        task_completed = task_status == "completed"
        insights = self.generate_insights(
            summary, pain_points, correlation, task_completed
        )

        return {
            "summary": summary,
            "pain_points": pain_points,
            "correlation": correlation,
            "insights": insights
        }


if __name__ == "__main__":
    # Quick test
    aggregator = SentimentAggregator(persona_key="student")

    test_analysis = [
        {"step_id": 1, "analyzed_sentiment": "NEUTRAL", "status": "success", "keywords": {}},
        {"step_id": 2, "analyzed_sentiment": "NEGATIVE", "status": "success", "keywords": {"confusion": ["где"]}},
        {"step_id": 3, "analyzed_sentiment": "NEUTRAL", "status": "success", "keywords": {}},
        {"step_id": 4, "analyzed_sentiment": "NEGATIVE", "status": "failure", "keywords": {"frustration": ["не могу"]}},
        {"step_id": 5, "analyzed_sentiment": "POSITIVE", "status": "success", "keywords": {"satisfaction": ["нашёл"]}}
    ]

    result = aggregator.aggregate(test_analysis, task_status="completed")

    print("Session Score:", result["summary"]["session_score"])
    print("Trend:", result["summary"]["trend"])
    print("Distribution:", result["summary"]["distribution"])
    print("Pain Points:", len(result["pain_points"]))
    print("\nInsights:")
    for insight in result["insights"]:
        print(f"  {insight}")
