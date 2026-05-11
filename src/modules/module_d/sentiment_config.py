"""
Configuration constants for Module D - Sentiment Analyzer
"""
from typing import Dict, List

# Weights for calculating sentiment score (-1 to +1)
SENTIMENT_WEIGHTS: Dict[str, int] = {
    "POSITIVE": 1,
    "NEUTRAL": 0,
    "NEGATIVE": -1
}

# Thresholds for trend detection (applied to slope of per-step numeric scores)
TREND_THRESHOLDS: Dict[str, float] = {
    "improving": 0.05,   # Slope > +0.05 per step = improving
    "declining": -0.05,  # Slope < -0.05 per step = declining
    "stable": 0.0        # Otherwise = stable
}

# Behavioral adjustments applied per step on top of resolved sentiment.
# Numeric, range [-1.0, +1.0], summed with sentiment weight then clamped.
BEHAVIORAL_ADJUSTMENTS: Dict[str, float] = {
    "failure": -0.4,            # Action did not succeed
    "backtrack": -0.25,         # Had to go back to previous page
    "stuck_on_page": -0.35,     # 3+ consecutive steps on the same URL
    "success_navigation": 0.10, # Successful click/navigate to a new page
}

# How many consecutive steps on the same URL count as "stuck"
STUCK_THRESHOLD_STEPS: int = 3

# Emotion categories for detailed analysis (Russian keywords)
EMOTION_CATEGORIES: Dict[str, List[str]] = {
    "frustration": [
        "не могу", "невозможно", "ужасно", "сложно", "раздражает",
        "бесит", "не работает", "ошибка", "проблема", "не получается"
    ],
    "confusion": [
        "непонятно", "где", "как найти", "не вижу", "потерялся",
        "запутался", "куда", "не понимаю", "странно", "неясно"
    ],
    "satisfaction": [
        "отлично", "нашёл", "удобно", "легко", "понятно",
        "хорошо", "быстро", "классно", "супер", "работает"
    ],
    "neutral": [
        "вижу", "наблюдаю", "перехожу", "кликаю", "ввожу",
        "страница", "открывается", "загружается", "есть", "содержит"
    ]
}

# Expected sentiment based on action status
STATUS_SENTIMENT_EXPECTATION: Dict[str, List[str]] = {
    "success": ["POSITIVE", "NEUTRAL"],
    "failure": ["NEGATIVE", "NEUTRAL"],
    "blocked": ["NEGATIVE"]
}

# Insight templates (Russian)
INSIGHT_TEMPLATES: Dict[str, str] = {
    "trend_improving": "📈 Эмоциональный тренд: улучшение к концу сессии",
    "trend_stable": "➡️ Эмоциональный тренд: стабильный на протяжении сессии",
    "trend_declining": "📉 Эмоциональный тренд: ухудшение к концу сессии",
    "high_negative": "😤 {percent}% шагов сопровождались негативными эмоциями",
    "low_negative": "😊 Только {percent}% шагов вызвали негативные эмоции",
    "pain_points": "🔴 Основные болевые точки: {points}",
    "no_pain_points": "✅ Серьёзных болевых точек не выявлено",
    "task_completed": "✅ Задача выполнена успешно",
    "task_not_completed": "⚠️ Задача не была выполнена - высокая корреляция с негативом",
    "high_failure_correlation": "📊 {percent}% неудачных действий сопровождались негативными эмоциями",
    "recommendation_navigation": "💡 Рекомендация: улучшить навигацию и структуру сайта",
    "recommendation_search": "💡 Рекомендация: добавить или улучшить функцию поиска",
    "recommendation_labels": "💡 Рекомендация: использовать более понятные названия разделов"
}

# Thresholds for generating insights
INSIGHT_THRESHOLDS: Dict[str, float] = {
    "high_negative_rate": 0.25,      # > 25% negative = high
    "high_failure_correlation": 0.6  # > 60% failures with negative = high
}
