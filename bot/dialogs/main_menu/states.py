from aiogram.fsm.state import State, StatesGroup

class MainMenu(StatesGroup):
    start = State()
    main_menu = State()
    start_question = State()
    waiting_answer = State()
    question_history = State()
    often_questions = State()
    start_support = State()
    support = State()
    

