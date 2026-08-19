import re


def clean_summary(summary: str) -> str:
    # Удаление лишних пробелов и переносов строк
    summary = re.sub(r'\s+', ' ', summary).strip()

    # Удаление повторяющихся знаков препинания
    summary = re.sub(r'\.{2,}', '.', summary)
    summary = re.sub(r'!{2,}', '!', summary)
    summary = re.sub(r'\?{2,}', '?', summary)

    # Убедимся, что текст заканчивается знаком препинания
    if summary and not summary.endswith(('.', '!', '?', '…')):
        summary += '.'

    # Удаление служебных фраз, которые иногда добавляет модель
    unwanted_phrases = [
        "Вот краткое содержание:",
        "Краткое содержание:",
        "Вот summary:",
        "Summary:",
        "Вот краткая выжимка:",
        "Краткая выжимка:"
    ]
    for phrase in unwanted_phrases:
        summary = summary.replace(phrase, "").strip()

    return summary

def test_clean_summary_removes_extra_spaces():
    assert clean_summary("  Hello   world.  ") == "Hello world."

def test_clean_summary_removes_unwanted_phrases():
    assert "Вот краткое содержание:" not in clean_summary("Вот краткое содержание: Текст")