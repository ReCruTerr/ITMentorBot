from aiogram import Router, types, F
from aiogram.filters import Command
import asyncio
from aiogram.fsm.context import FSMContext
from .states import UserSetup
from .keyboards import get_grade_keyboard, get_language_keyboard, get_sphere_keyboard
from .models import Grade, Language, Sphere, User, User_Answer
from asgiref.sync import sync_to_async
import logging
from .ai.questions import generate_questions, assess_answer, generate_verdict

logging.basicConfig(level=logging.INFO)
router = Router()



@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    try:
        greeting = (
        "👋 Привет, друг!\n\n"
        "Добро пожаловать в бота, который поможет тебе прокачаться в IT.\n\n"
        "Здесь ты сможешь определить свой текущий уровень знаний, получить рекомендации по темам для изучения, "
        "а также отслеживать свой прогресс со временем.\n\n"
        "Сейчас я задам тебе несколько вопросов — это займёт не больше пары минут.\n"
        "Всё просто: отвечаешь честно, а я на основе твоих ответов сформирую твои точки роста.\n\n"
            "Для начала — выбери свой уровень:"
        )
        await message.answer(greeting, reply_markup=await get_grade_keyboard())
        await state.set_state(UserSetup.choosing_grade)
    except Exception as exc:
        logging.error(f"Ошибка при обработке /start: {exc}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

@router.message(UserSetup.choosing_grade)
async def process_grade(message: types.Message, state: FSMContext):
    grade = await sync_to_async(Grade.objects.filter(name=message.text).first)()
    if grade:
        await sync_to_async(User.objects.update_or_create)(
            user_id=message.from_user.id,
            defaults={"grade": grade}
        )
        await message.answer("Сфера выбрана✅")
        await message.answer("Теперь выбери язык: ", reply_markup=await get_language_keyboard())
        await state.set_state(UserSetup.choosing_language)
    else:
        await message.answer("Грейд не найден. Выбери пожалуйста из списка.")

@router.message(UserSetup.choosing_language)
async def process_language(message: types.Message, state: FSMContext):
    language = await sync_to_async(Language.objects.filter(name=message.text).first)()
    if language:
        await sync_to_async(User.objects.update_or_create)(
            user_id=message.from_user.id,
            defaults={"language": language}
        )
        keyboard = await get_sphere_keyboard(language)
        if not keyboard.keyboard:
            await message.answer("Для выбранного языка нет доступных сфер. Пожалуйста, выберите другой язык.")
            return
        await message.answer("Язык выбран✅")
        await message.answer("Далее выбери сферу: ", reply_markup=keyboard)
        await state.set_state(UserSetup.choosing_sphere)
    else:
        await message.answer("Язык не найден. Пожалуйста, выбери из списка.")

@router.message(UserSetup.choosing_sphere)
async def process_sphere(message: types.Message, state: FSMContext):
    try:
        # Логируем запрос пользователя
        logging.info(f"Пользователь {message.from_user.id} выбрал сферу: {message.text}")
        user = await sync_to_async(User.objects.select_related('language').get)(user_id=message.from_user.id)
        # Проверяем наличие сферы в базе данных
        sphere = await sync_to_async(Sphere.objects.filter(name=message.text).first)()
        
        if sphere:
            # Обновляем или создаём пользователя с выбранной сферой
            await sync_to_async(User.objects.update_or_create)(
                user_id=message.from_user.id,
                defaults={"sphere": sphere}
            )

            await message.answer("Настройка завершена✅ \nПодготавливаю вопросы....")
            
            # Получаем пользователя с предзагруженными связанными полями
            user = await sync_to_async(
                User.objects.select_related('grade', 'language', 'sphere').get
            )(user_id=message.from_user.id)
            
            # Безопасный доступ к связанным полям в синхронном контексте
            stack = {
                "grade": await sync_to_async(lambda: user.grade.name if user.grade else None)(),
                "language": await sync_to_async(lambda: user.language.name if user.language else None)(),
                "sphere": await sync_to_async(lambda: user.sphere.name if user.sphere else None)()
            }
            logging.info(f"Stack для генерации вопросов: {stack}")

            questions, correct_answers = await generate_questions(stack)
            
            if not questions:
                # Логируем и сообщаем, если вопросы не были сгенерированы
                logging.error(f"Не удалось сгенерировать вопросы для сферы: {message.text}")
                await message.answer("Не удалось сгенерировать вопросы. Попробуйте позже.")
                return

            # Обновляем данные в состоянии
            await state.update_data(questions=questions, current_question=0, correct_answers=correct_answers, answers=[])
            await message.answer(f"Вопрос: {questions[0]}")   
            await state.set_state(UserSetup.answering_questions)  # Используем класс состояния
        else:
            # Логируем и информируем пользователя о невозможности найти сферу
            logging.warning(f"Сфера не найдена: {message.text}")
            await message.answer("Сфера не найдена. Пожалуйста, выбери из списка.")
    except Exception as exc:
        # Логируем исключение для дальнейшего анализа
        logging.error(f"Ошибка при обработке сферы: {exc}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


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


@router.message(UserSetup.answering_questions)
async def process_answers(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        questions = data.get("questions", [])
        correct_answers = data.get("correct_answers", [])
        current = data.get("current_question", 0)
        answers = data.get("answers", [])

        # Валидация данных
        if not questions or not correct_answers or current >= len(questions):
            await message.answer("Нет доступных вопросов или произошла ошибка.")
            await state.clear()
            return

        # Очистка вопроса от номера и ответа, если есть
        raw_question = questions[current]
        question_text = clean_question(raw_question)

        user = await sync_to_async(User.objects.get)(user_id=message.from_user.id)
        user_answer = message.text
        correct_answer = correct_answers[current]

        # Анализ нейросетью
        confidence_score = await assess_answer(user_answer, correct_answer)
        is_correct = confidence_score >= 0.75

        # Сохраняем ответ
        await sync_to_async(User_Answer.objects.create)( 
            user=user, 
            question=question_text, 
            answer=user_answer, 
            is_correct=is_correct, 
            confidence_score=confidence_score
        )

        answers.append({
            "question": question_text,
            "your_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "confidence_score": confidence_score
        })

        current += 1

        if current < len(questions):
            # Перед отправкой следующего вопроса, уведомляем пользователя, что анализируем ответ
            await message.answer(f"⌛ Анализирую твой ответ... Подготавливаю вопрос ({current + 1} из {len(questions)})...")
            
            # Пауза перед отправкой следующего вопроса
            await asyncio.sleep(2)  # Задержка 2 секунды перед отправкой следующего вопроса

            await state.update_data(current_question=current, answers=answers)
            next_question = clean_question(questions[current])
            await message.answer(f"Вопрос ({current + 1} из {len(questions)}):\n{next_question}")
        else:
            # Завершаем сессию после всех ответов
            await message.answer("Ответы приняты, провожу итоговый анализ....")
            await state.clear()
            correct_count = sum(1 for a in answers if a["is_correct"])
            total = len(answers)
            percent = (correct_count / total) * 100

            if percent >= 80:
                verdict = "🎉 Отлично! Вы успешно освоили материал."
            elif percent >= 50:
                verdict = "🙂 Неплохо, но стоит повторить некоторые темы."
            else:
                verdict = "😕 Нужно ещё поработать над этим материалом."

            result_msg = (
                f"✅ Правильных ответов: {correct_count} из {total} ({percent:.0f}%)\n"
                f"📌 {verdict}"
            )
            detailed_verdict = await generate_verdict(answers)

            await message.answer("Ты ответил на все вопросы! Вот твой результат:")
            await message.answer(result_msg)
            await message.answer(f"📊 Анализ твоих ответов:\n{detailed_verdict}")

    except Exception as exc:
        logging.error(f"Ошибка в процессе ответа на вопрос: {exc}")
        await message.answer("Произошла ошибка при обработке ответа. Попробуйте позже.")
        await state.clear()


