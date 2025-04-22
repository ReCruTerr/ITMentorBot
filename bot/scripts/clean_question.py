import re

def clean_question(raw_question: str) -> str:
    """
    Удаляет номер вопроса и текст ответа, если они присутствуют в строке.
    """
    # Удаление ответа после слова 'Ответ' или 'Otvet'
    raw_question = re.split(r"(Ответ|Otvet)\s*:", raw_question, flags=re.IGNORECASE)[0]
    # Удаление номера вопроса в начале (например, "1. Вопрос: ..." или "2.")
    raw_question = re.sub(r"^\s*\d+\.\s*", "", raw_question)
    # Удаление лишнего слова "Вопрос", если есть
    raw_question = re.sub(r"Вопрос\s*:\s*", "", raw_question, flags=re.IGNORECASE)
    return raw_question.strip()
