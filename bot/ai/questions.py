import aiohttp
import logging
from typing import List, Tuple
import re
# Настройка логгирования
logging.basicConfig(level=logging.INFO)

OLLAMA_API_URL = "http://localhost:11434/v1/chat/completions"
OLLAMA_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer ollama"
}


async def generate_questions(stack):
    questions = []
    answers = []

    prompt = (
        f"Сгенерируй 5 пар 'вопрос - ответ' по направлению {stack['sphere']}, "
        f"уровень {stack['grade']}, язык программирования: {stack['language']}. "
        f"Формат строго: Вопрос: ... Ответ: ..."
        f"Используй только русский язык!"

    )

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("http://localhost:11434/v1/chat/completions", json={
                "model": "mistral",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }) as response:
                if response.status != 200:
                    text = await response.text()
                    logging.error(f"Ollama API error: {response.status} - {text}")
                    return [], []

                data = await response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                logging.info(f"Ответ от Ollama: {content}")

                # Используем регулярку для извлечения всех пар вопрос-ответ
                qa_pairs = re.findall(r"Вопрос:\s*(.*?)\s*Ответ:\s*(.*?)(?=\n\d*\.?\s*Вопрос:|\Z)", content, re.DOTALL)
                for question, answer in qa_pairs:
                    questions.append(question.strip())
                    answers.append(answer.strip())

                return questions, answers

        except Exception as e:
            logging.error(f"Ошибка при обращении к Ollama: {e}")
            return [], []


# Функция оценки пользовательского ответа
async def assess_answer(user_answer: str, correct_answer: str) -> float:
    prompt = (
        f"Оцени правильность ответа на вопрос.\n"
        f"Ответ пользователя: '{user_answer}'\n"
        f"Правильный ответ: '{correct_answer}'\n"
        f"Оцени по шкале от 0 до 1. Просто число без объяснений."
    )

    payload = {
        "model": "mistral",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 10
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_API_URL, json=payload, headers=OLLAMA_HEADERS) as response:
                if response.status != 200:
                    logging.error(f"Ollama API error: {response.status} - {await response.text()}")
                    return 0.0

                data = await response.json()
                content = data['choices'][0]['message']['content'].strip()

                # Пытаемся распарсить число
                try:
                    score = float(content)
                    return max(0.0, min(1.0, score))  # Ограничение от 0 до 1
                except ValueError:
                    logging.warning(f"Не удалось преобразовать результат в число: {content}")
                    return 0.0

    except Exception as e:
        logging.error(f"Ошибка при оценке ответа: {str(e)}")
        return 0.0

async def generate_verdict(answers: List[str]) -> str:
    prompt = (
        "Ты — помощник-преподаватель. На основе ответов ученика проанализируй, какие темы он усвоил, а какие — нет.\n"
        "Для каждой ошибки или неточности укажи, в чём была проблема, и что стоит повторить. Не используй вводные фразы, говори чётко и по делу.\n"
        "Вот список вопросов и ответов:\n\n"
    )

    for ans in answers:
        prompt += (
            f"Вопрос: {ans["question"]}\n"
            f"Ответ ученика: {ans["your_answer"]}\n"
            f"Правильный ответ: {ans["correct_answer"]}\n"
            f"Уверенность: {ans["confidence_score"]:.2f}\n"
            f"Правильно: {'Да' if ans["is_correct"] else 'Нет'}\n\n" 
        )
    prompt += "Сформулируй чёткий итог: что получилось, что надо подтянуть, и на чём сосредоточиться в дальнейшем."
    
    payload = {
        "model": "mistral",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 500
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_API_URL, json=payload, headers=OLLAMA_HEADERS) as response:
                if response.status != 200:
                    logging.error(f"Ошибка при генерации вердикта: {response.status} - {await response.text()}")
                    return "Ошибка при анализе. Попробуйте позже."
                data = await response.json()
                content = data['choices'][0]['message']['content'].strip()
                return content
    except Exception as exc:
        logging.error(f"Ошибка при генерации вердикта: {exc}")
        return "Ошибка при анализе. Попробуйте позже."
