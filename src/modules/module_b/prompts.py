"""
Prompt templates for Module B - Behavioral Simulator
"""
from typing import List, Optional, Dict, Any
from src.config import PERSONAS


# =============================================================================
# SYSTEM PROMPT TEMPLATE
# =============================================================================

BEHAVIORAL_AGENT_SYSTEM = """Ты {persona_name}, {persona_age} лет.

{persona_system_prompt}

ТВОЯ ТЕКУЩАЯ ЗАДАЧА: {task}

{decision_style_block}

{action_space}

{response_format}

{history_context}

{visited_urls_block}

{failed_actions_block}
"""


# =============================================================================
# ACTION SPACE DESCRIPTION
# =============================================================================

ACTION_SPACE_DESCRIPTION = """
ДОСТУПНЫЕ ДЕЙСТВИЯ:

1. **click** - Кликнуть на элемент
   - target: ID элемента из DOM (data-audit-id или id)
   - Пример: {"action_type": "click", "target": "5", "reasoning": "Клик на нужную ссылку"}

2. **type** - Ввести текст в поле ввода
   - target: ID поля ввода, value: текст
   - Пример: {"action_type": "type", "target": "search-input", "value": "расписание", "reasoning": "Ввожу запрос"}

3. **press_enter** - Нажать Enter (после ввода текста в поле поиска)
   - Без параметров
   - Пример: {"action_type": "press_enter", "reasoning": "Отправляю форму поиска"}

4. **hover** - Навести курсор на элемент (раскрыть выпадающее меню)
   - target: ID элемента
   - Пример: {"action_type": "hover", "target": "nav-menu", "reasoning": "Раскрываю выпадающее меню"}

5. **scroll_down** - Прокрутить страницу вниз
   - Пример: {"action_type": "scroll_down", "reasoning": "Ищу контент ниже"}

6. **scroll_up** - Прокрутить страницу вверх
   - Пример: {"action_type": "scroll_up", "reasoning": "Возвращаюсь к меню"}

7. **wait** - Подождать загрузки
   - Пример: {"action_type": "wait", "reasoning": "Жду загрузки страницы"}

8. **navigate** - Перейти на конкретный URL
   - value: полный URL
   - Пример: {"action_type": "navigate", "value": "https://example.com/page/", "reasoning": "Перехожу на нужную страницу"}

9. **back** - Вернуться на предыдущую страницу
   - Пример: {"action_type": "back", "reasoning": "Зашёл не туда, возвращаюсь"}

10. **task_complete** - Задача выполнена
    - Используй когда ты на странице, которая содержит нужную информацию или ведёт к ней
    - НЕ нужно видеть идеальный ответ — достаточно что страница явно релевантна задаче
    - Примеры когда надо завершать: видишь расписание/учебный план/список дисциплин, попал на нужный раздел, нашёл файл/ссылку с нужным документом
    - Пример: {"action_type": "task_complete", "reasoning": "На странице есть расписание занятий для нужной программы"}

ВАЖНО:
- Используй только ID элементов из DOM (data-audit-id или id) — не придумывай их
- Если элемент не найден — прокрути или найди альтернативный путь
- После ввода текста в поиск используй press_enter для отправки
- hover помогает раскрыть скрытые подменю
"""


# =============================================================================
# RESPONSE FORMAT
# =============================================================================

RESPONSE_FORMAT_TEMPLATE = """
ФОРМАТ ОТВЕТА (ТОЛЬКО валидный JSON, без комментариев):

{
  "current_state_analysis": "Что ты видишь на странице (1-2 предложения)",
  "hypothesis": "Твоя гипотеза: где скорее всего находится нужная информация и почему",
  "progress_towards_task": "Насколько близко к цели (1 предложение)",
  "ux_observation": "Конкретная UX-проблема которую ты замечаешь СЕЙЧАС как пользователь — или null",
  "next_action": {
    "action_type": "click|type|press_enter|hover|scroll_down|scroll_up|wait|navigate|back|task_complete",
    "target": "ID элемента (только для click, type, hover)",
    "value": "текст или URL (только для type и navigate)",
    "reasoning": "Почему ты выбрал именно это действие"
  },
  "task_status": "in_progress|completed|blocked",
  "emotional_state": "POSITIVE|NEUTRAL|NEGATIVE",
  "confidence": 0.7
}

Пояснения:
- hypothesis: формулируй план — это помогает принимать лучшие решения
- ux_observation: КОНКРЕТНАЯ проблема интерфейса которая мешает тебе прямо сейчас.
  Примеры хороших наблюдений:
    "Нет видимой кнопки поиска в шапке — вынужден угадывать раздел"
    "Пункт меню 'Студентам' ведёт на страницу без чёткой структуры"
    "Ссылка на расписание скрыта в подменю, не видна без наведения мыши"
  Пиши null если нет конкретного наблюдения на этом шаге.
- task_status: "completed" если ты на странице с релевантной информацией (не жди идеала — если страница явно про то что нужно, это успех), "blocked" если зашёл в тупик
- emotional_state:
  POSITIVE — используй если: нашёл нужный раздел/ссылку, страница явно ведёт к цели, меню понятное, видишь прогресс к задаче
  NEUTRAL — идёшь вперёд без явных проблем и без явного прогресса
  NEGATIVE — используй если: не можешь найти нужный элемент, действие провалилось, возвращаешься назад, страница не то что ожидал, уже 2+ шага на одном месте без результата
- confidence: от 0.0 (не знаю что делать) до 1.0 (уверен в следующем шаге)
"""


# =============================================================================
# STUCK RECOVERY PROMPT ADDITION
# =============================================================================

STUCK_RECOVERY_BLOCK = """
ВНИМАНИЕ — ТЫ ЗАСТРЯЛ. Обычный путь не работает. Смени стратегию:

Варианты выхода из тупика (выбери один):
1. Используй поиск по сайту — введи ключевые слова из задачи
2. Вернись на главную страницу и начни с другого раздела меню
3. Попробуй hover на пункты главного меню — там могут быть скрытые подменю
4. Перейди напрямую по URL если знаешь структуру сайта

НЕ повторяй действия которые уже не сработали.
"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_step_history(history: List[Dict[str, Any]], max_steps: int = 6) -> str:
    """
    Format recent step history for LLM context with result summaries

    Args:
        history: List of BehaviorStep dicts or objects (from get_step_history_for_llm)
        max_steps: Maximum number of steps to include

    Returns:
        Formatted string with recent actions and their outcomes
    """
    if not history:
        return "Это твой первый шаг. Начни с изучения страницы."

    recent = history[-max_steps:] if len(history) > max_steps else history

    lines = ["ПОСЛЕДНИЕ ДЕЙСТВИЯ:"]
    for step in recent:
        if hasattr(step, 'step_id'):
            step_id = step.step_id
            action = step.action_taken
            status = step.status
            url = step.url
            result = getattr(step, 'result_summary', '')
        else:
            step_id = step.get('step_id', '?')
            action = step.get('action_taken', '?')
            status = step.get('status', '?')
            url = step.get('url', '?')
            result = step.get('result_summary', '')

        status_icon = "✓" if status == "success" else "✗"
        result_text = f" → {result}" if result else ""
        # Shorten URL to path only
        url_short = url.replace("https://", "").replace("http://", "")[:60]
        lines.append(f"  {step_id}. {status_icon} {action}{result_text} | {url_short}")

    lines.append(f"\nВсего шагов: {len(history)}")
    return "\n".join(lines)


def format_visited_urls(visited_urls: List[str]) -> str:
    """
    Format visited URLs block for the prompt

    Args:
        visited_urls: List of unique visited URLs

    Returns:
        Formatted string or empty string if no URLs
    """
    if not visited_urls:
        return ""

    lines = ["УЖЕ ПОСЕЩЁННЫЕ СТРАНИЦЫ (не возвращайся без новой цели):"]
    for url in visited_urls[-8:]:  # last 8 unique URLs
        lines.append(f"  - {url}")
    return "\n".join(lines)


def format_failed_actions(failed_actions: List[str]) -> str:
    """
    Format failed actions block for the prompt

    Args:
        failed_actions: List of failed action descriptions

    Returns:
        Formatted string or empty string if no failures
    """
    if not failed_actions:
        return ""

    lines = ["НЕУДАЧНЫЕ ДЕЙСТВИЯ (не повторяй):"]
    for action in failed_actions:
        lines.append(f"  - {action}")
    return "\n".join(lines)


def format_decision_style(persona_key: str) -> str:
    """
    Format decision style block for the prompt

    Args:
        persona_key: Persona key

    Returns:
        Formatted string with behavioral rules
    """
    persona = PERSONAS.get(persona_key, {})
    decision_style = persona.get("decision_style", [])

    if not decision_style:
        return ""

    lines = ["КАК ТЫ ПРИНИМАЕШЬ РЕШЕНИЯ (веди себя именно так):"]
    for rule in decision_style:
        lines.append(f"  - {rule}")
    return "\n".join(lines)


def get_persona_context(persona_key: str) -> Dict[str, Any]:
    """
    Get persona details from config

    Args:
        persona_key: Key like 'student', 'applicant', 'teacher'

    Returns:
        Persona dictionary or empty dict if not found
    """
    return PERSONAS.get(persona_key, {})


def get_behavioral_prompt(
    persona_key: str,
    task: str,
    step_history: Optional[List[Dict[str, Any]]] = None,
    current_dom: Optional[str] = None,
    current_url: Optional[str] = None,
    visited_urls: Optional[List[str]] = None,
    failed_actions: Optional[List[str]] = None,
    is_stuck: bool = False
) -> str:
    """
    Generate complete prompt for behavioral simulation

    Args:
        persona_key: Persona key (student, applicant, teacher, parent)
        task: Task description
        step_history: List of previous BehaviorStep objects/dicts
        current_dom: Simplified DOM of current page
        current_url: Current page URL
        visited_urls: List of already visited URLs
        failed_actions: List of failed action descriptions
        is_stuck: Whether the agent is currently stuck

    Returns:
        Complete formatted prompt for LLM
    """
    persona = get_persona_context(persona_key)

    if not persona:
        raise ValueError(f"Unknown persona: {persona_key}")

    persona_name = persona.get('name', 'Пользователь')
    persona_age = persona.get('age', 25)
    persona_system_prompt = persona.get('system_prompt', '')

    # Format history context
    if step_history:
        history_context = format_step_history(step_history)
    else:
        history_context = "Это твой первый шаг. Начни с изучения страницы."

    # Decision style block
    decision_style_block = format_decision_style(persona_key)

    # Visited URLs block
    visited_block = format_visited_urls(visited_urls or [])
    visited_urls_block = visited_block if visited_block else ""

    # Failed actions block
    failed_block = format_failed_actions(failed_actions or [])
    failed_actions_block = failed_block if failed_block else ""

    # Stuck recovery block
    if is_stuck:
        history_context = STUCK_RECOVERY_BLOCK + "\n\n" + history_context

    # Build prompt
    prompt = BEHAVIORAL_AGENT_SYSTEM.format(
        persona_name=persona_name,
        persona_age=persona_age,
        persona_system_prompt=persona_system_prompt,
        task=task,
        decision_style_block=decision_style_block,
        action_space=ACTION_SPACE_DESCRIPTION,
        response_format=RESPONSE_FORMAT_TEMPLATE,
        history_context=history_context,
        visited_urls_block=visited_urls_block,
        failed_actions_block=failed_actions_block
    )

    # Add current state
    if current_url:
        prompt += f"\nТЕКУЩИЙ URL: {current_url}\n"

    if current_dom:
        dom_preview = current_dom[:3000] if len(current_dom) > 3000 else current_dom
        prompt += f"\nУПРОЩЁННЫЙ DOM (интерактивные элементы):\n{dom_preview}\n"

    prompt += """
ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ СКРИНШОТА:
Скриншот — твой основной источник информации. DOM может не включать все элементы.
- Смотри на скриншот ПЕРВЫМ — ищи кнопки, иконки, поля поиска, ссылки которые ты ВИДИШЬ визуально
- Если видишь интерактивный элемент на скриншоте, но его нет в DOM — используй его текст или aria-label как target
- Иконка лупы = поле поиска, иконка гамбургера = меню, иконка X = закрыть
- Сначала скриншот, потом DOM для уточнения ID элемента

Верни JSON с твоим следующим действием."""

    return prompt


def get_retry_prompt(original_response: str, error_message: str) -> str:
    """
    Generate retry prompt when LLM returns invalid JSON

    Args:
        original_response: The invalid response from LLM
        error_message: Error message explaining what went wrong

    Returns:
        Retry prompt asking for valid JSON
    """
    return f"""Твой предыдущий ответ содержал ошибку: {error_message}

Твой ответ был:
{original_response[:500]}...

Верни ТОЛЬКО валидный JSON в следующем формате:
{{
  "current_state_analysis": "...",
  "hypothesis": "...",
  "progress_towards_task": "...",
  "ux_observation": null,
  "next_action": {{
    "action_type": "click|type|press_enter|hover|scroll_down|scroll_up|wait|navigate|back|task_complete",
    "target": "ID элемента (если нужен)",
    "value": "значение (если нужно)",
    "reasoning": "..."
  }},
  "task_status": "in_progress|completed|blocked",
  "emotional_state": "POSITIVE|NEUTRAL|NEGATIVE",
  "confidence": 0.5
}}

ВАЖНО: Верни ТОЛЬКО JSON, без дополнительного текста или markdown.
"""


# =============================================================================
# DEFAULT FALLBACK ACTION
# =============================================================================

DEFAULT_FALLBACK_ACTION = {
    "current_state_analysis": "Не удалось проанализировать страницу",
    "hypothesis": "Попробую прокрутить страницу для поиска нужных элементов",
    "progress_towards_task": "Продолжаю исследование",
    "next_action": {
        "action_type": "scroll_down",
        "target": None,
        "value": None,
        "reasoning": "Прокручиваю страницу для поиска нужных элементов"
    },
    "task_status": "in_progress",
    "emotional_state": "NEUTRAL",
    "confidence": 0.3
}
