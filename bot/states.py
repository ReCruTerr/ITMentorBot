from aiogram.fsm.state import State, StatesGroup

class UserSetup(StatesGroup):
    choosing_language = State()
    choosing_grade = State()
    choosing_sphere = State()
    answering_questions = State()

