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


# Concept keywords (Russian, will be 5-char-stemmed at compare time) for each axe rule.
# Used by M9 cross-module agreement to detect when Module A's prose covers the same
# UX concept as a Module C accessibility rule.
RULE_KEYWORDS_RU = {
    "color-contrast": {"контраст", "цвет", "читаем", "различ", "тускл", "блекл"},
    "image-alt": {"изображ", "картин", "альтер", "alt", "описан"},
    "input-image-alt": {"изображ", "альтер", "alt", "кнопк"},
    "button-name": {"кнопк", "подпис", "назван", "понятн", "label"},
    "link-name": {"ссылк", "назван", "понятн", "якорь"},
    "html-has-lang": {"язык", "lang"},
    "html-lang-valid": {"язык", "lang"},
    "document-title": {"заголов", "title", "назван", "вкладк"},
    "label": {"подпис", "форма", "поле", "ввод", "label"},
    "meta-viewport": {"масштаб", "viewport", "мобиль", "адаптив"},
    "tabindex": {"клавиа", "фокус", "tab", "табул"},
    "scrollable-region-focusable": {"клавиа", "фокус", "скролл", "прокру"},
    "region": {"навига", "ландма", "регион", "header", "footer", "структу", "шапк", "подвал"},
    "bypass": {"пропус", "skip", "клавиа", "навига"},
    "heading-order": {"заголов", "иерарх", "h1", "h2", "уровен"},
    "list": {"список", "перечен"},
    "listitem": {"список", "перечен", "пункт"},
    "duplicate-id": {"дублир", "уникаль"},
    "frame-title": {"фрейм", "iframe", "заголов"},
    "select-name": {"выпада", "select", "подпис", "форма"},
    "nested-interactive": {"вложен", "интерак", "кнопк", "ссылк"},
    "aria-allowed-attr": {"aria", "роль", "атрибу"},
    "aria-required-attr": {"aria", "роль", "атрибу", "обязат"},
    "aria-valid-attr": {"aria", "роль", "атрибу"},
    "aria-roles": {"aria", "роль"},
    "aria-command-name": {"aria", "кнопк", "ссылк", "меню", "назван"},
}


# Average step time in seconds for proxy task time calculation (M7).
# Agent doesn't measure real time, so we use a constant per step.
AVG_STEP_TIME_SEC = 8.0

# Map WCAG impact (axe-core) to unified severity scale used in M8
WCAG_IMPACT_TO_SEVERITY = {
    "critical": "critical",
    "serious": "high",
    "moderate": "medium",
    "minor": "low",
}

# Behavioral metrics display configuration (M1-M12)
# Each metric: name_ru, format, thresholds (green/yellow/red)
METRICS_DISPLAY = {
    # === Group 1: Task Effectiveness (M1-M7) ===
    "M1_task_completed": {
        "name_ru": "Завершённость задачи",
        "group": "task_effectiveness",
        "format": "bool",
    },
    "M2_steps_to_goal": {
        "name_ru": "Количество шагов",
        "group": "task_effectiveness",
        "format": "int",
        "thresholds": {"green": 7, "yellow": 12},
        "lower_is_better": True,
    },
    "M3_relative_efficiency": {
        "name_ru": "Относительная эффективность",
        "group": "task_effectiveness",
        "format": "ratio",  # actual/optimal, 1.0=ideal, >1=worse
        "thresholds": {"green": 1.4, "yellow": 2.0},
        "lower_is_better": True,
    },
    "M4_error_count": {
        "name_ru": "Количество ошибок",
        "group": "task_effectiveness",
        "format": "int",
        "thresholds": {"green": 0, "yellow": 2},
        "lower_is_better": True,
    },
    "M5_backtrack_count": {
        "name_ru": "Количество возвратов",
        "group": "task_effectiveness",
        "format": "int",
        "thresholds": {"green": 1, "yellow": 3},
        "lower_is_better": True,
    },
    "M6_lostness": {
        "name_ru": "Потерянность",
        "group": "task_effectiveness",
        "format": "float",
        "thresholds": {"green": 0.4, "yellow": 0.7},
        "lower_is_better": True,
    },
    "M7_task_time": {
        "name_ru": "Время выполнения",
        "group": "task_effectiveness",
        "format": "seconds",
        "thresholds": {"green": 60, "yellow": 120},
        "lower_is_better": True,
    },
    # === Group 2: Interface Quality (M8-M9) ===
    "M8_interface_issues": {
        "name_ru": "Проблемы интерфейса",
        "group": "interface_quality",
        "format": "issues_breakdown",  # composite display
    },
    "M9_issue_overlap": {
        "name_ru": "Пересечение с реальными пользователями",
        "group": "interface_quality",
        "format": "overlap_placeholder",
    },
    # === Group 3: Subjective Experience (M10-M12) ===
    "M10_sus_proxy": {
        "name_ru": "SUS-прокси",
        "group": "subjective_experience",
        "format": "score100",
        "thresholds": {"green": 68, "yellow": 50},
        "lower_is_better": False,
    },
    "M11_emotional_trend": {
        "name_ru": "Эмоциональный тренд",
        "group": "subjective_experience",
        "format": "trend",
    },
    "M12_pain_points_count": {
        "name_ru": "Болевые точки",
        "group": "subjective_experience",
        "format": "int",
        "thresholds": {"green": 0, "yellow": 2},
        "lower_is_better": True,
    },
}

METRICS_GROUP_NAMES = {
    "task_effectiveness": "Эффективность (M1–M7)",
    "interface_quality": "Качество интерфейса (M8–M9)",
    "subjective_experience": "Субъективный опыт (M10–M12)",
}

# HTML template settings
HTML_SETTINGS = {
    "theme": "light",
    "primary_color": "#3b82f6",
    "font_family": "system-ui, -apple-system, sans-serif",
    "max_width": "1200px"
}
