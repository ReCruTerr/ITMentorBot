from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from .models import Grade, Sphere, Language
from asgiref.sync import sync_to_async

async def get_grade_keyboard():
    # Получаем список грейдов из базы данных
    grades = await sync_to_async(list)(Grade.objects.all())
    # Формируем список кнопок (каждая кнопка в отдельном ряду)
    buttons = [[KeyboardButton(text=grade.name)] for grade in grades]
    # Создаём клавиатуру, передавая все кнопки сразу
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def get_language_keyboard():
    languages = await sync_to_async(list)(Language.objects.all())
    buttons = [[KeyboardButton(text=language.name)] for language in languages]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def get_sphere_keyboard(language):
    spheres = await sync_to_async(list)(Sphere.objects.filter(language=language))   
    buttons = [[KeyboardButton(text=sphere.name)] for sphere in spheres]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard