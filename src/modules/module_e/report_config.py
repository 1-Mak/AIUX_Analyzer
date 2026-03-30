"""
Module E Configuration - Report Synthesis Settings
"""

# Report sections configuration
REPORT_SECTIONS = {
    "executive_summary": {
        "title": "Executive Summary",
        "title_ru": "Краткое резюме",
        "order": 1,
        "required": True
    },
    "visual_analysis": {
        "title": "Visual Analysis (Module A)",
        "title_ru": "Визуальный анализ (Модуль A)",
        "order": 2,
        "required": False,
        "source": "module_a_results"
    },
    "behavioral_analysis": {
        "title": "Behavioral Analysis (Module B)",
        "title_ru": "Поведенческий анализ (Модуль B)",
        "order": 3,
        "required": False,
        "source": "module_b_results"
    },
    "accessibility_audit": {
        "title": "Accessibility Audit (Module C)",
        "title_ru": "Аудит доступности (Модуль C)",
        "order": 4,
        "required": False,
        "source": "module_c_results"
    },
    "sentiment_analysis": {
        "title": "Sentiment Analysis (Module D)",
        "title_ru": "Анализ эмоций (Модуль D)",
        "order": 5,
        "required": False,
        "source": "module_d_results"
    },
    "recommendations": {
        "title": "Recommendations",
        "title_ru": "Рекомендации",
        "order": 6,
        "required": True
    }
}

# Severity levels for prioritization
SEVERITY_ORDER = ["critical", "high", "serious", "medium", "moderate", "low", "minor"]

# Score thresholds for overall rating
RATING_THRESHOLDS = {
    "excellent": {"min_score": 0.8, "label": "Excellent", "label_ru": "Отлично", "color": "#22c55e"},
    "good": {"min_score": 0.6, "label": "Good", "label_ru": "Хорошо", "color": "#84cc16"},
    "fair": {"min_score": 0.4, "label": "Fair", "label_ru": "Удовлетворительно", "color": "#eab308"},
    "poor": {"min_score": 0.2, "label": "Poor", "label_ru": "Плохо", "color": "#f97316"},
    "critical": {"min_score": 0.0, "label": "Critical", "label_ru": "Критично", "color": "#ef4444"}
}

# Weight factors for overall score calculation
SCORE_WEIGHTS = {
    "visual": 0.25,        # Module A weight
    "behavioral": 0.25,    # Module B weight
    "accessibility": 0.30, # Module C weight (higher - compliance matters)
    "sentiment": 0.20      # Module D weight
}

# Issue type icons (ASCII-safe for Windows console)
ISSUE_ICONS = {
    "critical": "[!!!]",
    "high": "[!!]",
    "serious": "[!]",
    "medium": "[~]",
    "moderate": "[~]",
    "low": "[.]",
    "minor": "[.]"
}

# Module status icons
MODULE_STATUS = {
    "success": "[OK]",
    "partial": "[~]",
    "skipped": "[--]",
    "error": "[X]"
}

# Persona descriptions for report context
PERSONA_CONTEXT = {
    "student": {
        "name": "Student",
        "name_ru": "Студент",
        "description": "Active user looking for information quickly",
        "description_ru": "Активный пользователь, ищет информацию быстро"
    },
    "applicant": {
        "name": "Applicant",
        "name_ru": "Абитуриент",
        "description": "First-time visitor exploring options",
        "description_ru": "Новичок на сайте, изучает условия и требования"
    },
    "teacher": {
        "name": "Teacher",
        "name_ru": "Преподаватель",
        "description": "Experienced user managing content",
        "description_ru": "Опытный пользователь, работает с контентом"
    },
    "parent": {
        "name": "Parent",
        "name_ru": "Родитель абитуриента",
        "description": "Helping child choose a university",
        "description_ru": "Помогает ребёнку с выбором вуза, низкий уровень техграмотности"
    }
}

# Axe accessibility rule translations (English -> Russian)
AXE_RULES_RU = {
    "button-name": "Кнопки должны иметь понятный текст",
    "color-contrast": "Элементы должны иметь достаточный цветовой контраст",
    "image-alt": "Изображения должны иметь альтернативный текст",
    "link-name": "Ссылки должны иметь понятный текст",
    "html-has-lang": "Элемент <html> должен иметь атрибут lang",
    "html-lang-valid": "Атрибут lang должен содержать допустимое значение",
    "document-title": "Страница должна иметь заголовок <title>",
    "label": "Поля форм должны иметь подписи (label)",
    "input-image-alt": "Кнопки-изображения должны иметь alt-текст",
    "meta-viewport": "Масштабирование не должно быть отключено",
    "aria-allowed-attr": "ARIA-атрибуты должны быть допустимыми",
    "aria-required-attr": "Обязательные ARIA-атрибуты должны быть указаны",
    "aria-valid-attr": "ARIA-атрибуты должны быть валидными",
    "aria-roles": "ARIA-роли должны быть валидными",
    "duplicate-id": "Значения id должны быть уникальными",
    "heading-order": "Заголовки должны идти в правильном порядке",
    "list": "Списки должны быть правильно структурированы",
    "listitem": "Элементы списка должны быть внутри <ul> или <ol>",
    "region": "Контент должен быть внутри landmark-регионов",
    "bypass": "Должен быть способ пропустить повторяющийся контент",
    "tabindex": "tabindex не должен быть больше 0",
    "frame-title": "Фреймы должны иметь атрибут title",
    "nested-interactive": "Интерактивные элементы не должны быть вложенными",
    "select-name": "Выпадающие списки должны иметь подписи",
}


def translate_axe_rule(rule_id: str, fallback: str = "") -> str:
    """Translate axe rule ID or help text to Russian"""
    return AXE_RULES_RU.get(rule_id, fallback)


# Behavioral metrics display configuration (M1-M13)
# Each metric: name_ru, format, thresholds (green/yellow/red)
METRICS_DISPLAY = {
    "M1_task_completed": {
        "name_ru": "Задача выполнена",
        "group": "task_effectiveness",
        "format": "bool",
    },
    "M2_steps_to_goal": {
        "name_ru": "Шагов до цели",
        "group": "task_effectiveness",
        "format": "int",
        "thresholds": {"green": 7, "yellow": 12},  # <=green good, <=yellow fair, else bad
        "lower_is_better": True,
    },
    "M3_relative_efficiency": {
        "name_ru": "Относительная эффективность",
        "group": "task_effectiveness",
        "format": "percent",
        "thresholds": {"green": 0.7, "yellow": 0.4},
        "lower_is_better": False,
    },
    "M4_error_count": {
        "name_ru": "Ошибки (неудачные действия)",
        "group": "task_effectiveness",
        "format": "int",
        "thresholds": {"green": 0, "yellow": 2},
        "lower_is_better": True,
    },
    "M5_backtrack_count": {
        "name_ru": "Возвраты назад",
        "group": "task_effectiveness",
        "format": "int",
        "thresholds": {"green": 1, "yellow": 3},
        "lower_is_better": True,
    },
    "M6_lostness": {
        "name_ru": "Потерянность (Lostness)",
        "group": "interface_quality",
        "format": "float",
        "thresholds": {"green": 0.4, "yellow": 0.7},
        "lower_is_better": True,
    },
    "M7_visual_issues": {
        "name_ru": "Визуальные проблемы",
        "group": "interface_quality",
        "format": "int",
        "thresholds": {"green": 3, "yellow": 7},
        "lower_is_better": True,
    },
    "M8_accessibility_issues": {
        "name_ru": "Проблемы доступности",
        "group": "interface_quality",
        "format": "int",
        "thresholds": {"green": 3, "yellow": 8},
        "lower_is_better": True,
    },
    "M9_critical_issues": {
        "name_ru": "Критические проблемы",
        "group": "interface_quality",
        "format": "int",
        "thresholds": {"green": 0, "yellow": 1},
        "lower_is_better": True,
    },
    "M10_session_score": {
        "name_ru": "Оценка сессии",
        "group": "subjective_experience",
        "format": "signed_float",
        "thresholds": {"green": 0.1, "yellow": -0.2},
        "lower_is_better": False,
    },
    "M11_trend": {
        "name_ru": "Эмоциональный тренд",
        "group": "subjective_experience",
        "format": "trend",
    },
    "M12_pain_points": {
        "name_ru": "Болевые точки",
        "group": "subjective_experience",
        "format": "int",
        "thresholds": {"green": 0, "yellow": 2},
        "lower_is_better": True,
    },
    "M13_sus_proxy": {
        "name_ru": "SUS-прокси",
        "group": "subjective_experience",
        "format": "score100",
        "thresholds": {"green": 68, "yellow": 50},
        "lower_is_better": False,
    },
}

METRICS_GROUP_NAMES = {
    "task_effectiveness": "Эффективность задачи",
    "interface_quality": "Качество интерфейса",
    "subjective_experience": "Субъективный опыт",
}

# HTML template settings
HTML_SETTINGS = {
    "theme": "light",
    "primary_color": "#3b82f6",
    "font_family": "system-ui, -apple-system, sans-serif",
    "max_width": "1200px"
}
