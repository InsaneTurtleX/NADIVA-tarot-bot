# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberStatus
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base



# Установка соединения с базой данных при помощи ORM
host = 'eporqep6b4b8ql12.chr7pe7iynqr.eu-west-1.rds.amazonaws.com'
username = 'hit9za4dgrwewfx1'
password = 'bs8790sarceyn0hv'
database = 'g09lyqcrg09g5exs'
engine = create_engine(f'mysql://{username}:{password}@{host}/{database}')

#базовый класс модели
Base = declarative_base()



#создание модели таблицы
class InformationAboutUsers(Base):
    __tablename__ = 'information_about_users'
    id = Column(Integer, primary_key=True)
    is_owner = Column(Boolean, default=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    text = Column(String)

class UserAnswer(Base):
    __tablename__ = 'user_answers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('information_about_users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer = Column(String)

    # Определяем отношения между таблицами
    user = relationship("InformationAboutUsers", back_populates="answers")
    question = relationship("Question")

# Добавляем обратное отношение для связи пользователей с ответами
InformationAboutUsers.answers = relationship("UserAnswer", back_populates="user")

# Создаем таблицы в базе данных (если они еще не существуют)
Base.metadata.create_all(engine)



#создание сессии для работы с БД
Session = sessionmaker(bind=engine)
session = Session()

#токен и объект бота, объект хранилища памяти, диспетчер (колбэков, сообщений, состояний и тд)
token = '7067592422:AAF-ch8SK5asSyxYmY-hEz6TcQ8vz6aJRZU'
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

#текстовые фразы
button_agree_text = 'Да'
button_disagree_text = 'Нет'
button_main_agree_text = '✅ Да, хочу'
button_main_disagree_text = '❌ Нет, не хочу'
end_survey_text = '🚫 Закончить опрос'
back_to_survey_text = '⬅️ Назад к анкете'
back = '⬅️ Назад'
cancel = '🚫 Отмена'
survey_is_finished_text = 'Заполнение анкеты завершено. Вы сможете отредактировать ее позднее, если захотите.'
survey_is_in_progress_text = f'Пожалуйста, выберите любой вопрос, на который Вы хотели бы дать ответ или закончите анкетирование:'
main_menu_text = 'Здесь Вы можете оформить заявку на консультацию, найти контакты, по которым со мной можно связаться, просмотреть свою анкету или отредактировать её.'
arrow_up_text = "⬆️"
arrow_down_text = "⬇️"


#переменные
#chat_id = -4139713338

chat_id = -1001670079714
current_part_of_survey = 0
commands = ['start', 'open', 'go']
chosen_subtopics = []
list_of_choices = ''
current_menu = 0
main_menu_buttons = ["✨ Заявка на консультацию","📞 Контакты","📋 Просмотр анкеты","✏️ Редактирование анкеты"]
main_menu_buttons_for_owners = ["Список пользователей","Просмотр анкеты пользователя","Добавить или удалить администратора"]
back_to_survey_buttons_dict = {back_to_survey_text: 'back_to_survey',
                                   end_survey_text: 'finish_survey'}

fastest_way_to_answer = {'WhatsApp':'whatsapp',
                         'Telegram':'telegram',
                         'Mail':'mail'}

yes_no_partially_buttons_dict = {button_agree_text: 'answer_yes_button',
                             button_disagree_text: 'answer_no_button',
                             "Частично": 'answer_partially_button',}

consultations_types = {'Таро':'service_1',
                       'Астрология':'service_2',
                       'Энергетические чистки':'service_3',
                       'Медитации':'service_4',
                        'Активации':'service_5',
                       'Настройки':'service_6',
                       'Работа с Родом':'service_7',
                       'Ангельская терапия':'service_8'}

prefered_way_to_communicate = {'Онлайн':'online',
                               'Офлайн':'offline',
                               'Видеосвязь':'video',
                               'Аудио':'audio',
                               'Письменно':'text'}

out_of_ten_scale = {'1':'1',
                    '2':'2',
                    '3':'3',
                    '4':'4',
                    '5':'5',
                    '6':'6',
                    '7':'7',
                    '8':'8',
                    '9':'9',
                    '10':'10'}

methods_dict = {"Астрология":'method_1',
                "Таро":'method_2'}

topics_dict = {"Вопросы личности":'topic_1',
                "Деньги, финансы, работа, бизнес":'topic_2',
                "Контакты, связи, информация":'topic_3',
                "Дом, семья, род, прошлое":'topic_4',
                "Любовь, отношения, дети, творчество":'topic_5',
                "Здоровье":'topic_6',
                "Брак, партнёры, конкуренция, соперницы":'topic_7',
                "Диагностики негатива, тайн, наследство, корпорации":'topic_8',
                "Переезды, партнеры из-за границы, расширение возможностей, духовный рост":'topic_9',
                "Карьера, достижения, жизненный успех":'topic_10',
                "Коллективы, коррекция судьбы, прогнозы на будущее":'topic_11',
                "Поиск пропавших вещей, все, что касается тайных дел, разоблачения. Вопросы о тюрьме, психических болезнях, карма":'topic_12',
                'Классическое бизнес-консультирование "УДАЧА притягивает УСПЕХ"':'topic_13',
                }

topics_dict_for_corps = {"Организация магической поддержки Вашей компании":'topic_14',
                         "Аналитический прогноз для корпораций":'topic_15',}

subtopics_dict_1 = {"Вопросы личности":{"Кто Вы есть на самом деле":'subtopic_1',
                                        "Саморазвитие":'subtopic_2',
                                        "Предназначение":'subtopic_3',
                                        "Лучшие черты, что нужно развивать":'subtopic_4',}}

subtopics_dict_2 = {'Классическое бизнес-консультирование "УДАЧА притягивает УСПЕХ"':{"Бизнес-консалтинг":'subtopic_1',
                                                                                      "Кризис-менеджер":'subtopic_2',
                                                                                      "Магический Адвокат":'subtopic_3',
                                                                                      "Нетрадиционный Трейдинг":'subtopic_4',
                                                                                      "Сопровождение судебных тяжб":'subtopic_5',
                                                                                      "Сопровождение крупных сделок (необычная поддержка)":'subtopic_6',
                                                                                      "Астро-таро-психологическая помощь и компенсаторика":'subtopic_7',}}

subtopics_dict_3 = {'Организация магической поддержки Вашей компании':{"Прогноз на любой срок":'subtopic_1',
                                                                        "Аналитика состояния и перспективы":'subtopic_2',
                                                                        " обращение в любой момент, по любому человеку для уточнения (семья, партнеры по бизнесу, сотрудники, любовники..)":'subtopic_3',
                                                                        "Судебные, спорные вопросы":'subtopic_4',
                                                                        "Рекомендации, пошаговое ведение по трудным участкам пути":'subtopic_5',
                                                                        "Сопровождение крупных сделок (необычная поддержка)":'subtopic_6',
                                                                        "Астро-таро-психологическая помощь и компенсаторика":'subtopic_7',}}

subtopics_dict_4 = {'Аналитический прогноз для корпораций':{"Конфликты":'subtopic_1',
                                                             "Геополитика":'subtopic_2',
                                                             "Экономика":'subtopic_3',
                                                             "Мировые финансы":'subtopic_4',
                                                             "Недвижимость":'subtopic_5',
                                                             "Победа на выборах":'subtopic_6',}}

#состояния
class Form(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()
    waiting_for_button = State()
    waiting_for_insert = State()
    waiting_for_method = State()
    waiting_for_topic = State()
    waiting_for_subtopic = State()
    waiting_for_insert_admin = State()



#список вопросов, предполагающих произвольный ответ
random_answer_expected_questions = ['Пожалуйста, напишите Ваше имя:',
                                    'Пожалуйста, напишите Вашу дату рождения:',
                                    'Пожалуйста, напишите Ваши текущие город и страну проживания:',
                                    'Напишите, пожалуйста, Ваш электронный почтовый адрес:',
                                    'Пожалуйста, напишите актуальный номер телефона, по которому с Вами можно связаться в WhatsApp:',
                                    'Напишите, пожалуйста, чем Вы занимаетесь?',
                                    'Какой результат Вы ожидаете от нашей с вами работы?',
                                    'Почему Вы решили пойти на консультацию/наставничество именно ко мне?',
                                    'Почему мне стоит взять именно Вас?']
#списки вопросов
questions_part_1 = {'Ваше имя':'Пожалуйста, напишите Ваше имя:', 'Ваша дата рождения':'Пожалуйста, напишите Вашу дату рождения:',
                    'Город, страна':'Пожалуйста, напишите Ваши текущие город и страну проживания:',
                    'Ваш электронный почтовый адрес':'Напишите, пожалуйста, Ваш электронный почтовый адрес:',
                    'Ваш номер телефона WhatsApp':'Пожалуйста, напишите актуальный номер телефона, по которому с Вами можно связаться в WhatsApp:',
                    'Наиболее актуальный способ связи':'Пожалуйста, выберите один наиболее удобный для вас способ связи, где вы быстрее всего увидите сообщение (выберите одно):'}

questions_part_2 = {'Ваш вопрос касается личной жизни?':'Ваш вопрос касается личной жизни?',
                    'Ваш вопрос касается бизнеса, работы, финансов?':'Ваш вопрос касается бизнеса, работы, финансов?',
                    'Ваш вопрос касается здоровья?':'Ваш вопрос касается здоровья?',
                    'Ваш вопрос касается духовного роста и предназначения?':'Ваш вопрос касается духовного роста и предназначения?',
                    'Ваш вопрос касается психологии?':'Ваш вопрос касается психологии?'}

questions_part_3 = {'Ваш род деятельности':'Напишите, пожалуйста, чем Вы занимаетесь?',
                    'Ваши ожидания':'Какой результат Вы ожидаете от нашей с вами работы?',
                    'Почему решили обратиться ко мне':'Почему Вы решили пойти на консультацию/наставничество именно ко мне?',
                    'Почему мне стоит взять именно Вас':'Почему мне стоит взять именно Вас?'}

questions_part_4 = {'Какой вид консультации вы хотите выбрать?':'Какой вид консультации Вы хотите выбрать? (выберите одно)',
                    'Какой вид общения предпочитаете?':'Какой вид общения Вы предпочитаете? (выберите одно):',
                    'Понятие энергоценности':'Вам известно понятие энергоценность?',
                    'Степень доверия':'Насколько вы готовы довериться мне? (по 10-балльной шкале)'}

all_questions_dict = {'questions_part_1':questions_part_1,
                      'questions_part_2':questions_part_2,
                      'questions_part_3':questions_part_3,
                      'questions_part_4':questions_part_4,
                      }


#текущая часть анкеты
def process_current_questions_part_status(arg):
    current_part_of_survey_status = f'({arg}/{len(all_questions_dict)})'
    return current_part_of_survey_status


#секция с клавиатурами
button_main_agree = KeyboardButton(button_main_agree_text)
button_main_disagree = KeyboardButton(button_main_disagree_text)
greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
greet_kb.row(button_main_agree, button_main_disagree)

#выводит часть анкеты + клавиатура для вопросов с произвольными ответами
def survey_part():
    global inline_button_questions_and_callbacks_dict
    inline_button_questions_and_callbacks_dict = {}
    inline_kb_survey = InlineKeyboardMarkup()
    if current_part_of_survey > 1:
        inline_kb_survey.add(InlineKeyboardButton(arrow_up_text, callback_data='prev_part_of_survey'))
    global questions_part
    questions_part = f'questions_part_{current_part_of_survey}'

    if current_part_of_survey == 1:
        questions_part = questions_part_1
    elif current_part_of_survey == 2:
        questions_part = questions_part_2
    elif current_part_of_survey == 3:
        questions_part = questions_part_3
    elif current_part_of_survey == 4:
        questions_part = questions_part_4


    for index, (key, value) in enumerate(questions_part.items()):
        callback_data = f'question_{index}'
        button = InlineKeyboardButton(text=key, callback_data=callback_data)
        inline_button_questions_and_callbacks_dict.update({value: callback_data})
        inline_kb_survey.add(button)
    if current_part_of_survey < 5:
        inline_kb_survey.add(InlineKeyboardButton(text=arrow_down_text, callback_data='next_part_of_survey'))
    inline_kb_survey.add(InlineKeyboardButton(text=end_survey_text, callback_data='finish_survey'))
    return inline_kb_survey

#клавиатура ответов на вопрос "самый быстрый способ связи"
def fastest_way_to_answer_menu():
    keyboard = InlineKeyboardMarkup()
    for key, value in fastest_way_to_answer.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
    row = []
    for key, value in back_to_survey_buttons_dict.items():
        row.append(InlineKeyboardButton(text=key, callback_data=value))
        if len(row) == 2:
            keyboard.add(*row)
            row = []
    return keyboard

#клавиатура для вопросов с ответами "да/нет/частично"
def yes_no_partially_menu():
    keyboard = InlineKeyboardMarkup()
    row = []
    for key, value in yes_no_partially_buttons_dict.items():
        row.append(InlineKeyboardButton(text=key, callback_data=value))
        if len(row) == 3:
            keyboard.add(*row)
            row = []
    for key, value in back_to_survey_buttons_dict.items():
        row.append(InlineKeyboardButton(text=key, callback_data=value))
        if len(row) == 2:
            keyboard.add(*row)
            row = []
    return keyboard

#клавиатура для вопроса "какой тип консультации продпочтителен"
def consultations_types_menu():
    keyboard = InlineKeyboardMarkup()
    for key, value in consultations_types.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
    row = []
    for key, value in back_to_survey_buttons_dict.items():
        row.append(InlineKeyboardButton(text=key, callback_data=value))
        if len(row) == 2:
            keyboard.add(*row)
            row = []
    return keyboard

#клавиатура для вопроса "предпочитаемый способ общения"
def prefered_way_to_communicate_menu():
    keyboard = InlineKeyboardMarkup()
    for key, value in prefered_way_to_communicate.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
    row = []
    for key, value in back_to_survey_buttons_dict.items():
        row.append(InlineKeyboardButton(text=key, callback_data=value))
        if len(row) == 2:
            keyboard.add(*row)
            row = []
    return keyboard

#клавиатура для вопрос со шкалой (1-10)
def out_of_ten_scale_menu():
    keyboard = InlineKeyboardMarkup(row_width=5)
    row = []
    for key, value in out_of_ten_scale.items():
        row.append(InlineKeyboardButton(text=key, callback_data=value))
        if len(row) == 5:
            keyboard.add(*row)
            row = []
    for key, value in back_to_survey_buttons_dict.items():
        row.append(InlineKeyboardButton(text=key, callback_data=value))
        if len(row) == 2:
            keyboard.add(*row)
            row = []
    return keyboard

#проверка на участие в группе
async def check_if_chat_member(message, user_id):
    try:
        info_chat_member = await bot.get_chat_member(chat_id, user_id)
        print(info_chat_member["status"])
        if info_chat_member["status"] != "left":
            print("Пользователь состоит в группе.")
        else:
            await bot.send_message(message.from_user.id,
                                   text='Подпишитесь на мою группу, там Вы найдете много интересного!\nhttps://t.me/+kx-uithPXXA3MWQy',
                                   reply_markup=main_menu(message))
            print("Пользователь не состоит в группе.")
    except:
        await bot.send_message(message.from_user.id, text="Пользователь не найден в группе.", reply_markup=main_menu(message))
        return


#пустое inline-меню
def empty_menu():
    keyboard = InlineKeyboardMarkup()
    return keyboard

#кнопки назад и завершить опрос под каждым отдельным вопросом
def back_to_survey_kb():
    keyboard = InlineKeyboardMarkup()
    back_to_survey_buttons_dict = {back_to_survey_text: 'back_to_survey',
                                   end_survey_text: 'finish_survey'}
    row = []
    for key, value in back_to_survey_buttons_dict.items():
        row.append(InlineKeyboardButton(text=key, callback_data=value))
        if len(row) == 2:
            keyboard.add(*row)
            row = []
    return keyboard

#клавиатура главного меню внизу
def main_menu(message):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*main_menu_buttons)
    result = session.query(InformationAboutUsers).filter_by(id=message.from_user.id).first()
    if result.is_owner == 1:
        keyboard.add(*main_menu_buttons_for_owners)
    return keyboard


def method_menu():
    keyboard = InlineKeyboardMarkup()
    for key, value in methods_dict.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
    keyboard.add(InlineKeyboardButton(text=cancel, callback_data='cancel'))
    return keyboard

def topic_menu():
    keyboard = InlineKeyboardMarkup()
    for key, value in topics_dict.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
    keyboard.add(InlineKeyboardButton(text='🏭 Для корпораций и компаний', callback_data='for corps'))
    keyboard.add(InlineKeyboardButton(text=back, callback_data='back'))
    return keyboard

def topic_corps_menu():
    keyboard = InlineKeyboardMarkup()
    for key, value in topics_dict_for_corps.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
    keyboard.add(InlineKeyboardButton(text='👨‍🦱 Для отдельных людей', callback_data='for people'))
    keyboard.add(InlineKeyboardButton(text=back, callback_data='back'))
    return keyboard


def subtopic_menu(subtopics_dict):
    keyboard = InlineKeyboardMarkup()
    for key, value in subtopics_dict.items():
        if key in chosen_subtopics:
            text=f'✅ {key}'
        else:
            text = f'❌ {key}'
        keyboard.add(InlineKeyboardButton(text=text, callback_data=value))
    keyboard.add(InlineKeyboardButton(text='Оформить заявку', callback_data='complete application'))
    keyboard.add(InlineKeyboardButton(text=back, callback_data='back'))
    return keyboard


# def contacts_menu():
#     keyboard = InlineKeyboardMarkup()
#     contacts_buttons_dict = {"Контакт 1":'contact_1',
#                              "Контакт 2":'contact_2',
#                              "Контакт 3":'contact_3'}
#     for key, value in contacts_buttons_dict.items():
#         keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
#     return keyboard

#найти ключ словаря по значению
def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None

#сохранение фиксированных ответов
def update_data(dict, data, current_part_of_survey, question):
    global all_questions_WITH_ANSWERS_dict
    answer_user = find_key_by_value(dict, data)
    questions_part = f'questions_part_{current_part_of_survey}'
    key = find_key_by_value(all_questions_dict[questions_part], question)
    all_questions_WITH_ANSWERS_dict[key] = answer_user

#отобразить полную анкету
async def show_answered_full_survey(id):
    question_number_in_survey = 0
    survey_answers_list = '<b>Ваша анкета</b>\n'
    for key, value in all_questions_dict.items():
        for question, answer in value.items():
            question_number_in_survey  += 1
            survey_answers_list+= f'<b>{question_number_in_survey }.{question}</b>\n"{all_questions_dict[key][question]}"\nВаш ответ: <i>{all_questions_WITH_ANSWERS_dict[question]}</i>\n\n'
            if question_number_in_survey == 10:
                await bot.send_message(id, survey_answers_list, parse_mode='HTML')
                survey_answers_list = ''
    if survey_answers_list != '':
        await bot.send_message(id, survey_answers_list, parse_mode='HTML')

#искать по введенному значению
async def info_about_user_for_owner(message):
    result = session.query(InformationAboutUsers).filter_by(id=message.text).first()
    if result is not None:
        parameter_to_search = 'id'
    else:
        result = session.query(InformationAboutUsers).filter_by(username=message.text).first()
        if result is not None:
            parameter_to_search = 'username'
        else:
            result = session.query(UserAnswer).filter_by(answer=message.text).first()
            if result is not None:
                parameter_to_search = 'phone_number'
            else:
                return
    all_registered_users = ""
    if parameter_to_search == 'phone_number':
        result = session.query(InformationAboutUsers).filter_by(id=result.user_id).first()
    id_value = result.id
    username_value = result.username
    first_name_value = result.first_name
    last_name_value = result.last_name
    all_registered_users += f"ID пользователя: {id_value}\n"
    if username_value is not None:
        all_registered_users += f"Username пользователя: @{username_value}\n"
    else:
        all_registered_users += f'Username пользователя: отсутствует\n'

    all_registered_users += f"Имя пользователя (в Telegram): {first_name_value}\n"

    if last_name_value is not None:
        all_registered_users += f'Фамилия пользователя (в Telegram): {last_name_value}\n\n'
    else:
        all_registered_users += f'Фамилия пользователя (в Telegram): отсутствует\n\n'

    if parameter_to_search == 'id':
        result = session.query(UserAnswer).filter_by(user_id=message.text).all()
    elif parameter_to_search == 'username':
        id = session.query(InformationAboutUsers).filter_by(username=message.text).first()
        result = session.query(UserAnswer).filter_by(user_id=id.id).all()
    elif parameter_to_search == 'phone_number':
        id = session.query(UserAnswer).filter_by(answer=message.text).first()
        result = session.query(UserAnswer).filter_by(user_id=id.user_id).all()
    all_registered_users += 'Анкета пользователя:'
    for every in result:
        question = session.query(Question).filter_by(id=every.question_id).first()
        all_registered_users += (f"\n{every.question_id}. Вопрос: {question.text}\nОтвет: {every.answer}")


    return all_registered_users
def save_data_to_db(id):
    user_id = session.query(InformationAboutUsers).filter_by(id=id).first()
    for question, answer_text in all_questions_WITH_ANSWERS_dict.items():
        question_id = session.query(Question).filter_by(text=all_questions_with_questions_text_dict[question]).first()
        answer = session.query(UserAnswer).filter_by(user_id=user_id.id, question_id=question_id.id).first()
        answer.answer = answer_text
    session.commit()
@dp.message_handler(commands=commands, state="*")
async def process_start_command(message: types.Message, ):
    await Form.waiting_for_button.set()
    # Вставляем основную запись с полем 'id'
    global user_id
    global all_questions_with_questions_text_dict
    global all_questions_WITH_ANSWERS_dict
    user_id = message.from_user.id
    data_from_message = ['id', 'username', 'first_name', 'last_name']
    values = [getattr(message.from_user, column) for column in data_from_message]
    existing_user = session.query(InformationAboutUsers).filter_by(id=values[0]).first()
    #если пользователь уже есть в базе, обновляем его данные
    if existing_user:
        existing_user.username = values[1]
        existing_user.first_name = values[2]
        existing_user.last_name = values[3]
        session.commit()
        #await bot.send_message(message.chat.id, text=f'Данные пользователя с id={values[0]} успешно обновлены.')
    #если пользователя нет в базе. добавляем его данные
    else:
        user_info = InformationAboutUsers(id=values[0], username=values[1], first_name=values[2], last_name=values[3])
        session.add(user_info)
        session.commit()
        #await bot.send_message(message.chat.id, text=f'Пользователь с id={values[0]} успешно добавлен в базу данных.')

    answers_are_exist = session.query(UserAnswer).filter_by(user_id=message.from_user.id).first()
    #если хотя бы один ответ есть в базе (а значит есть и все остальные)
    if answers_are_exist is not None:
        all_questions_WITH_ANSWERS_dict = {}
        all_questions_with_questions_text_dict = {}
        #берем ответы на вопросы и формируем из них словарь для дальнейшего редактирования
        for every_part in all_questions_dict:
            for question, text in all_questions_dict[every_part].items():
                question_id = session.query(Question).filter_by(text=text).first().id
                user_answer = session.query(UserAnswer).filter_by(user_id=message.from_user.id, question_id=question_id).first().answer
                all_questions_WITH_ANSWERS_dict[question] = user_answer
                all_questions_with_questions_text_dict[question] = text
        session.commit()
    #если ответов в базе нет вообще и это первое обращение пользователя к боту
    else:
        all_questions_WITH_ANSWERS_dict = {}
        all_questions_with_questions_text_dict = {}
        #формируем словарь анкеты с вопросами и ответами "без ответа" для сохранения
        for every_part in all_questions_dict:
            for question, text in all_questions_dict[every_part].items():
                question_id = session.query(Question).filter_by(text=text).first().id
                all_questions_WITH_ANSWERS_dict[question] = 'без ответа'
                all_questions_with_questions_text_dict[question] = text
                session.add(UserAnswer(user_id=values[0], question_id=question_id, answer='без ответа'))
        session.commit()


    await message.reply("Здравствуйте! Я - таро-бот, и с моей помощью Вы можете записаться на консультацию к @Elenanadiva. "
                        "Желаете заполнить анкету для улучшения взаимодействия?", reply_markup=greet_kb)

async def application(arg, state):
    if current_menu == 1:
        text = "Давайте сформируем Вашу заявку на консультацию. Выберите предпочтительную методику, пожалуйста:"
        reply_markup = method_menu()
        current_state = Form.waiting_for_method
        await bot.edit_message_text(text, arg.from_user.id,
                                    arg.message.message_id, reply_markup=reply_markup)
        async with state.proxy() as data:
            data['text'] = text
            data['reply_markup'] = reply_markup
            data['state'] = current_state
        await current_state.set()
    elif current_menu == 2:
        topics_list = ''
        for index, every_topic in enumerate(topics_dict.keys()):
            topics_list += f'{index + 1}. {every_topic}.\n'
        method = find_key_by_value(methods_dict, arg.data)

        text = f'Выбранная Вами методика - "{method}". Теперь выберите интересующую Вас тему. Список тем:\n{topics_list}'
        reply_markup = topic_menu()
        current_state = Form.waiting_for_topic
        await bot.edit_message_text(text, arg.from_user.id,
                                    arg.message.message_id, reply_markup=reply_markup)
        async with state.proxy() as data:
            data['method'] = method
            data['text'] = text
            data['reply_markup'] = reply_markup
            data['state'] = current_state
        await current_state.set()


# Обработчик кнопки "Заявка на консультацию"
@dp.message_handler(lambda message: message.text == main_menu_buttons[0], state=Form.waiting_for_button)
async def process_form_application(message: types.Message, state = FSMContext):
    global current_menu
    print(f'текущее меню равно {current_menu}')
    current_menu += 1
    print(f'текущее меню увеличилось на 1 и теперь равно {current_menu}')
    text = "Давайте сформируем Вашу заявку на консультацию. Выберите предпочтительную методику, пожалуйста:"
    reply_markup = method_menu()
    current_state = Form.waiting_for_method
    await message.answer(text, reply_markup=reply_markup)
    async with state.proxy() as data:
        data['text'] = text
        data['reply_markup'] = reply_markup
        data['state'] = current_state
    await current_state.set()

# Обработчик кнопки "Наши контакты"
@dp.message_handler(lambda message: message.text == main_menu_buttons[1], state=Form.waiting_for_button)
async def process_contacts_menu(message: types.Message):
    #await message.answer("Наши контакты:", reply_markup=contacts_menu())
    await bot.send_message(message.chat.id, 'Контакты, по которым со мной можно связаться.\n\n'
                                            'Мой телеграм:\n\n@Elenanadiva\n\n'
                                            'Моя электронная почта:\n\nhandozenkoelena82@gmail.com')

# Обработчик кнопки "Просмотр анкеты"
@dp.message_handler(lambda message: message.text == main_menu_buttons[2], state=Form.waiting_for_button)
async def show_survey_for_user(message: types.Message):
    await show_answered_full_survey(message.from_user.id)


# Обработчик кнопки "Редактирование анкеты"
@dp.message_handler(lambda message: message.text == main_menu_buttons[3], state= Form.waiting_for_button)
async def process_edit_survey(message: types.Message):
    await Form.waiting_for_question.set()
    await bot.send_message(message.from_user.id, f'{process_current_questions_part_status(current_part_of_survey)} {survey_is_in_progress_text}',
                           reply_markup=survey_part())

#обработчик кнопки вызова всех зарегистрированных пользователей
@dp.message_handler(lambda message: message.text == main_menu_buttons_for_owners[0] or
                                    message.text == main_menu_buttons_for_owners[1] or
                                    message.text == main_menu_buttons_for_owners[2], state=Form.waiting_for_button)
async def process_all_registered_users_button(message: types.Message):
    if message.text == main_menu_buttons_for_owners[0]:
        result = session.execute(select(InformationAboutUsers.id, InformationAboutUsers.username, InformationAboutUsers.first_name, InformationAboutUsers.last_name))
        all_registered_users = f"Все зарегистрированные пользователи:\n"
        for index, row in enumerate(result):
            id_value = row[0]
            username_value = row[1]
            first_name_value = row[2]
            last_name_value = row[3]
            all_registered_users += f"{index + 1}. ID пользователя: {id_value}\n"
            if username_value is not None:
                all_registered_users += f"Username пользователя: @{username_value}\n"
            else:
                all_registered_users += f'Username пользователя: отсутствует\n'


            all_registered_users += f"Имя пользователя (в Telegram): {first_name_value}\n"

            if last_name_value is not None:
                all_registered_users += f'Фамилия пользователя (в Telegram): {last_name_value}\n\n'
            else:
                all_registered_users += f'Фамилия пользователя (в Telegram): отсутствует\n\n'

            if (index + 1) % 50 == 0:
                await message.answer(text=all_registered_users, reply_markup=main_menu(message))
                all_registered_users = ''
            else:
                pass

        await message.answer(text=all_registered_users, reply_markup=main_menu(message))
    elif message.text == main_menu_buttons_for_owners[1]:
            await Form.waiting_for_insert.set()
            await message.answer(
                "Пожалуйста, введите id, username (без @) или номер телефона пользователя, анкету которого вы желаете просмотреть:",
                reply_markup=main_menu(message))
    elif message.text == main_menu_buttons_for_owners[2]:
        await Form.waiting_for_insert_admin.set()
        await message.answer(
            "Пожалуйста, введите id или username (без @) пользователя, которому Вы хотите назначить или снять статус администратора (помните, что для этого его данные должны быть в базе данных):",
                reply_markup=main_menu(message))


#поиск анкеты пользователя по id, username или номеру телефона
# @dp.message_handler(lambda message: message.text == main_menu_buttons_for_owners[1], state=Form.waiting_for_button)
# async def process_waiting_for_search_by(message: types.Message):
#     await Form.waiting_for_insert.set()
#     await message.answer("Пожалуйста, введите id, username (без @) или номер телефона пользователя, анкету которого вы желаете просмотреть:", reply_markup=main_menu(message))

#ожидание ввода id, username или номера телефона для поиска
@dp.message_handler(state=Form.waiting_for_insert)
async def process_waiting_for_insert_to_search(message: types.Message):
    await message.answer(text=f'Вы ввели "{message.text}". Осуществляю поиск...', reply_markup=main_menu(message))
    await try_to_search_user_by(message)

@dp.message_handler(state=Form.waiting_for_insert_admin)
async def process_waiting_for_insert_to_search(message: types.Message):
    if message.text == message.from_user.id:
        await message.answer(text=f'🚫 Вы не можете снять статус администратора с себя.', reply_markup=main_menu(message))
        return

    await message.answer(text=f'Вы ввели "{message.text}". Осуществляю поиск...', reply_markup=main_menu(message))
    await try_to_make_user_admin(message)

async def try_to_make_user_admin(message):
    result = session.query(InformationAboutUsers).filter_by(id=message.text).first()
    if result:
        if result.is_owner == 0:
            result.is_owner = 1
            session.commit()
            await bot.send_message(message.from_user.id, f'✅ Пользователь с таким id найден и назначен администратором.',
                                   reply_markup=main_menu(message))
        else:
            result.is_owner = 0
            session.commit()
            await bot.send_message(message.from_user.id,
                                   f'✅ Пользователь с таким id найден и лишен статуса администратора.',
                                   reply_markup=main_menu(message))


    else:
        print('Пользователя с таким id не существует в базе. Осуществляю поиск по username.')
        result = session.query(InformationAboutUsers).filter_by(username=message.text).first()
        if result:
            if result.is_owner == 0:
                result.is_owner = 1
                session.commit()
                await bot.send_message(message.from_user.id,
                                       f'✅ Пользователь с таким username найден и назначен администратором.',
                                       reply_markup=main_menu(message))
            else:
                result.is_owner = 0
                session.commit()
                await bot.send_message(message.from_user.id,
                                       f'✅ Пользователь с таким username найден и лишен статуса администратора.',
                                       reply_markup=main_menu(message))
        else:
            await bot.send_message(message.from_user.id, '🚫 Такого пользователя не существует в базе. '
                                                             'Пожалуйста, проверьте правильность введённых данных и попробуйте ещё раз.',
                                       reply_markup=main_menu(message))

    await Form.waiting_for_button.set()

#поиск пользователя по введённому значению
async def try_to_search_user_by(message):
    result = session.query(InformationAboutUsers).filter_by(id=message.text).first()
    if result:
        info = await info_about_user_for_owner(message)
        await bot.send_message(message.from_user.id, f'✅ Пользователь с таким id найден.\n{info}', reply_markup=main_menu(message))
    else:
        print('Пользователя с таким id не существует в базе. Осуществляю поиск по username.')
        result = session.query(InformationAboutUsers).filter_by(username=message.text).first()
        if result:
            print(result.username)
            info = await info_about_user_for_owner(message)
            await bot.send_message(message.from_user.id, f'✅ Пользователь с таким username найден.\n{info}',
                                   reply_markup=main_menu(message))
        else:
            print('Пользователя с таким username не существует в базе. Осуществляю поиск по номеру телефона.')
            result = session.query(UserAnswer).filter_by(answer=message.text).first()
            if result:
                info = await info_about_user_for_owner(message)
                await bot.send_message(message.from_user.id,
                                       f'✅ Пользователь с таким номером телефона найден.\n{info}',
                                       reply_markup=main_menu(message))
            else:
                await bot.send_message(message.from_user.id, '🚫 Такого пользователя не существует в базе. '
                                                             'Пожалуйста, проверьте правильность введённых данных и попробуйте ещё раз.',
                                       reply_markup=main_menu(message))

    await Form.waiting_for_button.set()

#обработка стартового выбора (проходить анкету или нет)
@dp.message_handler(state=Form.waiting_for_button)
async def process_start_command(message: types.Message):
    global current_part_of_survey
    current_part_of_survey = 0
    current_part_of_survey += 1
    if message.text == button_main_agree_text:
        await Form.waiting_for_question.set()
        await bot.send_message(message.from_user.id, f'{process_current_questions_part_status(current_part_of_survey)} {survey_is_in_progress_text}',
                               reply_markup=survey_part())

    elif message.text == button_main_disagree_text:
        await check_if_chat_member(message, message.from_user.id)
        await bot.send_message(message.from_user.id, main_menu_text, reply_markup=main_menu(message))







#обработка выбора вопроса из inline-меню анкеты
@dp.callback_query_handler(lambda c: c.data.startswith('question_'), state=Form.waiting_for_question)
async def process_question(callback_query: types.CallbackQuery, state: FSMContext):
    question_number = int(callback_query.data.split('_')[1])
    global question
    question = find_key_by_value(inline_button_questions_and_callbacks_dict, callback_query.data)
    await Form.waiting_for_answer.set()
    await state.update_data(question=question, question_number=question_number)
    if  'Ваш вопрос касается' in question:
        await callback_query.message.edit_text(
            question,
            reply_markup=yes_no_partially_menu())
    elif 'быстрее всего' in question:
        await callback_query.message.edit_text(
            question,
            reply_markup=fastest_way_to_answer_menu())
    elif 'консультации' in question:
        await callback_query.message.edit_text(
            question,
            reply_markup=consultations_types_menu())
    elif 'вид общения' in question:
        await callback_query.message.edit_text(
            question,
            reply_markup=prefered_way_to_communicate_menu())
    elif 'энергоценность' in question:
        await callback_query.message.edit_text(
            question,
            reply_markup=yes_no_partially_menu())
    elif 'по 10-балльной шкале' in question:
        await callback_query.message.edit_text(
            question,
            reply_markup=out_of_ten_scale_menu())
    else:
        await callback_query.message.edit_text(
            question,
            reply_markup=back_to_survey_kb())
    async with state.proxy() as data:
        data['question_message_id'] = callback_query.message.message_id


#ответы на вопросы, предполагающие произвольный ответ
@dp.message_handler(state=Form.waiting_for_answer)
async def process_answer(message: types.Message, state: FSMContext):
    # Обрабатываем полученный ответ
    answer = message.text
    async with state.proxy() as data:
        question = data['question']
    # Здесь можно сохранить ответ в базу данных
    if message.text in main_menu_buttons or message.text[1:] in commands:
        return
    if question:
        if question not in random_answer_expected_questions:
            return
        if 'question_message_id' in data:
            await bot.edit_message_text(text="Открыто более актуальное сообщение.",
                                        chat_id=message.chat.id,
                                        message_id=data['question_message_id'],
                                        reply_markup=empty_menu())
        await message.answer(f'Ваш ответ на вопрос "{find_key_by_value(questions_part, question)}": "{answer}". '
                             f'{survey_is_in_progress_text}',
                         reply_markup=survey_part())
        global all_questions_WITH_ANSWERS_dict
        #сохранение ответа в словарь
        answers_questions_part = f'questions_part_{current_part_of_survey}'
        key = find_key_by_value(all_questions_dict[answers_questions_part], question)
        all_questions_WITH_ANSWERS_dict[key] = answer
        await Form.waiting_for_question.set()
        async with state.proxy() as data:
            data['question'] = None
        return



#ответы на вопрос "предпочитаемый вид общения"
@dp.callback_query_handler(lambda c: find_key_by_value(prefered_way_to_communicate, c.data), state=Form.waiting_for_answer)
async def process_preffered_way_to_talk(callback_query: types.CallbackQuery):
    update_data(prefered_way_to_communicate, callback_query.data, current_part_of_survey, question)
    await Form.waiting_for_question.set()
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(prefered_way_to_communicate, callback_query.data)}". '
        f'{survey_is_in_progress_text}',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())


#ответы на вопрос "какой тип консультации вас интересует"
@dp.callback_query_handler(lambda c: find_key_by_value(consultations_types, c.data), state=Form.waiting_for_answer)
async def process_interested_type_of_consultation(callback_query: types.CallbackQuery):
    update_data(consultations_types, callback_query.data, current_part_of_survey, question)
    await Form.waiting_for_question.set()
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(consultations_types, callback_query.data)}". '
        f'{survey_is_in_progress_text}',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())


#ответы на вопрос "наиболее актуальный способ связи"
@dp.callback_query_handler(lambda c: find_key_by_value(fastest_way_to_answer, c.data), state=Form.waiting_for_answer)
async def process_way_to_connect(callback_query: types.CallbackQuery):
    update_data(fastest_way_to_answer, callback_query.data, current_part_of_survey, question)
    await Form.waiting_for_question.set()
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(fastest_way_to_answer, callback_query.data)}". '
        f'{survey_is_in_progress_text}',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())

#ответы на вопрос со шкалой
@dp.callback_query_handler(lambda c: find_key_by_value(out_of_ten_scale, c.data), state=Form.waiting_for_answer)
async def process_answer_with_scale(callback_query: types.CallbackQuery):
    update_data(out_of_ten_scale, callback_query.data, current_part_of_survey, question)
    await Form.waiting_for_question.set()
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(out_of_ten_scale, callback_query.data)}". '
        f'{survey_is_in_progress_text}',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())

#обработка ответов "да/нет/частично"
@dp.callback_query_handler(lambda c: c.data == 'answer_yes_button'
                                     or c.data == 'answer_no_button'
                                     or c.data == 'answer_partially_button'
                                     or c.data in consultations_types, state=Form.waiting_for_answer)
async def process_yes_no_partially_buttons(callback_query: types.CallbackQuery):
    update_data(yes_no_partially_buttons_dict, callback_query.data, current_part_of_survey, question)
    await Form.waiting_for_question.set()
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(yes_no_partially_buttons_dict, callback_query.data)}". '
        f'{survey_is_in_progress_text}',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())


#обработка кнопки "назад" из вопроса
@dp.callback_query_handler(lambda c: c.data == 'back_to_survey', state=Form.waiting_for_answer)
async def process_back_to_survey(callback_query: types.CallbackQuery):
    await Form.waiting_for_question.set()
    await callback_query.answer()
    await bot.edit_message_text(f'{process_current_questions_part_status(current_part_of_survey)} {survey_is_in_progress_text}',
                                callback_query.from_user.id,
                                callback_query.message.message_id,
                                reply_markup=survey_part())

#стрелка в предыдущую часть анкеты
@dp.callback_query_handler(lambda c: c.data == 'prev_part_of_survey', state=Form.waiting_for_question)
async def process_prev_part_of_survey(callback_query: types.CallbackQuery):
    await Form.waiting_for_question.set()
    global current_part_of_survey
    current_part_of_survey -= 1
    await callback_query.answer()
    await bot.edit_message_text(f"{process_current_questions_part_status(current_part_of_survey)} {survey_is_in_progress_text}",
                                callback_query.from_user.id,
                                callback_query.message.message_id,
                                reply_markup=survey_part())

#стрелка в следующую часть анкеты
@dp.callback_query_handler(lambda c: c.data == 'next_part_of_survey', state=Form.waiting_for_question)
async def process_next_part_of_survey(callback_query: types.CallbackQuery):
    await Form.waiting_for_question.set()
    global current_part_of_survey
    current_part_of_survey += 1
    await callback_query.answer()
    await bot.edit_message_text(f"{process_current_questions_part_status(current_part_of_survey)} {survey_is_in_progress_text}",
                                callback_query.from_user.id,
                                callback_query.message.message_id,
                                reply_markup=survey_part())


#завершение заполнения анкеты
@dp.callback_query_handler(lambda c: c.data == 'finish_survey', state="*")
async def process_finish_survey(callback_query: types.CallbackQuery):
    await Form.waiting_for_button.set()
    save_data_to_db(callback_query.from_user.id)
    await check_if_chat_member(callback_query, callback_query.from_user.id)
    await bot.edit_message_text(survey_is_finished_text,
                            callback_query.from_user.id,
                            callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, main_menu_text, reply_markup=main_menu(callback_query))


#выбор методики
@dp.callback_query_handler(lambda c: c.data in methods_dict.values() or c.data == 'cancel', state=Form.waiting_for_method)
async def process_chosen_method_button(callback_query: types.CallbackQuery, state = FSMContext):
    global current_menu
    if callback_query.data == 'cancel':
        current_menu = 0
        print(f'текущее меню обнулилось и стало {current_menu}')
        await bot.edit_message_text('Формирование заявки на консультацию отменено.',
                                    callback_query.from_user.id,
                                    callback_query.message.message_id, reply_markup=empty_menu())
        await Form.waiting_for_button.set()
    else:

        current_menu += 1
        print(f'текущее меню увеличилось на 1 и теперь равно {current_menu}')
        await application(callback_query, state)


@dp.callback_query_handler(lambda c: c.data == 'for corps' or c.data == 'for people', state=Form.waiting_for_topic)
async def process_for_corporations_button(callback_query: types.CallbackQuery, state = FSMContext):
    async with state.proxy() as data:
        method = data['method']
    topics_list = ''
    if callback_query.data == 'for corps':
        for index, every_topic in enumerate(topics_dict_for_corps.keys()):
            topics_list += f'{index + 1}. {every_topic}.\n'
        reply_markup = topic_corps_menu()
    else:
        for index, every_topic in enumerate(topics_dict.keys()):
            topics_list += f'{index + 1}. {every_topic}.\n'
        reply_markup = topic_menu()

    await bot.edit_message_text(f'Выбранная Вами методика - "{method}".'
                                f' Теперь выберите интересующую Вас тему. Список тем:\n{topics_list}',
                                callback_query.from_user.id,
                                callback_query.message.message_id,
                                reply_markup=reply_markup)



#обработка выбора темы
@dp.callback_query_handler(lambda c: c.data in topics_dict.values() or c.data in topics_dict_for_corps.values(), state=Form.waiting_for_topic)
async def process_chosen_topic(callback_query: types.CallbackQuery, state=FSMContext):
    global current_menu
    current_menu += 1
    print(f'текущее меню увеличилось на 1 и теперь равно {current_menu}')
    if callback_query.data in topics_dict.values():
        topic = find_key_by_value(topics_dict, callback_query.data)
    else:
        topic = find_key_by_value(topics_dict_for_corps, callback_query.data)



    async with state.proxy() as data:
        data['topic'] = topic



    if topic in subtopics_dict_1.keys():
        subtopic_dict = subtopics_dict_1[topic]
    elif topic in subtopics_dict_2.keys():
        subtopic_dict = subtopics_dict_2[topic]
    elif topic in subtopics_dict_3.keys():
        subtopic_dict = subtopics_dict_3[topic]
    elif topic in subtopics_dict_4.keys():
        subtopic_dict = subtopics_dict_4[topic]
    else:
        username_and_id = await just_info(callback_query.from_user.id)
        await bot.edit_message_text(f"{username_and_id}\n<b>Моя заявка на консультацию</b>:\n <b>Методика</b> - <i>{data['method']}</i>\n <b>Тема</b> - <i>{data['topic']}</i>", callback_query.from_user.id, callback_query.message.message_id, reply_markup=empty_menu(), parse_mode='HTML')

        await bot.send_message(callback_query.from_user.id,
                               "Перешлите заявку [мне](https://t.me/Elenanadiva) в личные сообщения, когда будете готовы начать работу над Вашей проблемой\!",
                               parse_mode='markdownV2')

        await Form.waiting_for_button.set()
        current_menu = 0
        print(f'текущее меню обнулилось и стало {current_menu}')
        return

    async with state.proxy() as data:
        data['subtopic_dict'] = subtopic_dict
    subtopics = ''

    for index, every_subtopic in enumerate(subtopic_dict.keys()):
        subtopics += f'{index + 1}. {every_subtopic}\n'

    await bot.edit_message_text(f'Выбранная Вами тема - "{topic}". '
                                f'Теперь можете выбрать одну или несколько интересующих вас подтем, или нажать кнопку "Оформить заявку". Список подтем:\n\n{subtopics}', callback_query.from_user.id,
                                callback_query.message.message_id, reply_markup=subtopic_menu(subtopic_dict))
    await Form.waiting_for_subtopic.set()

#Обработка выбора подтемы
@dp.callback_query_handler(lambda c: c.data != 'back', state=Form.waiting_for_subtopic)
async def process_chosen_subtopic(callback_query: types.CallbackQuery, state = FSMContext):
    global list_of_choices
    global chosen_subtopics
    global current_menu

    async with state.proxy() as data:
        subtopic_dict = data['subtopic_dict']

    if callback_query.data == 'complete application':
        if chosen_subtopics == []:
            list_of_choices = 'не выбрано ни одной подтемы.'
        else:
            element_to_remove = '"'
            list_of_choices = list_of_choices.replace(element_to_remove, "")
            pass
        subtopic_amount = 'Подтема'
        username_and_id = await just_info(callback_query.from_user.id)
        if len(chosen_subtopics) > 1:
            subtopic_amount = 'Подтемы'
        await bot.edit_message_text(f"{username_and_id}\n <b>Моя заявка на консультацию</b>:\n <b>Методика</b> - <i>{data['method']}</i>.\n <b>Тема</b> - <i>{data['topic']}</i>.\n <b>{subtopic_amount}</b> - <i>{list_of_choices}</i>",
                                    callback_query.from_user.id,
                                    callback_query.message.message_id,
                                    reply_markup=empty_menu(), parse_mode='HTML')
        await bot.send_message( callback_query.from_user.id, "Перешлите заявку [мне](https://t.me/Elenanadiva) в личные сообщения, когда будете готовы начать работу над Вашей проблемой\!", parse_mode='markdownV2')
        chosen_subtopics = []
        await Form.waiting_for_button.set()
        current_menu = 0
        print(f'текущее меню обнулилось и стало {current_menu}')
        return
    else:
        pass

    if callback_query.data in subtopic_dict.values():
        if find_key_by_value(subtopic_dict, callback_query.data) in chosen_subtopics:
            chosen_subtopics.remove(find_key_by_value(subtopic_dict, callback_query.data))
        else:
            chosen_subtopics.append(find_key_by_value(subtopic_dict, callback_query.data))

    list_of_choices = ''
    for index, subtopic in enumerate(chosen_subtopics):
        if index + 1 < len(chosen_subtopics):
            list_of_choices += f'"{subtopic}", '
        else:
            list_of_choices += f'"{subtopic}".'


    if len(chosen_subtopics) == 0:
        text = f'Вы пока что не выбрали ни одной подтемы. Сделайте выбор или нажмите "оформить заявку".'
    elif len(chosen_subtopics) == 1:
        text = f'Выбранная Вами подтема - {list_of_choices} Продолжите выбор подтем или нажмите "оформить заявку".'
    else:
        text = f'Выбранные Вами подтемы - {list_of_choices} Продолжите выбор подтем или нажмите "оформить заявку".'

    await bot.edit_message_text(text,
                                callback_query.from_user.id,
                                callback_query.message.message_id, reply_markup=subtopic_menu(subtopic_dict))

#обработка кнопки "назад" в заявке
@dp.callback_query_handler(lambda c: c.data == 'back', state="*")
async def back_from_application_button(callback_query: types.CallbackQuery, state = FSMContext):
    global current_menu
    current_menu -= 1
    print(f'текущее меню уменьшилось на 1 и теперь равно {current_menu}')
    await application(callback_query, state)


async def just_info(arg):
    user_info = ''
    result = session.query(InformationAboutUsers).filter_by(id=arg).first()
    id_value = result.id
    username_value = result.username
    user_info += f"Мой ID: {id_value}\n"
    if username_value is not None:
        user_info += f"Мой Username: @{username_value}\n"
    else:
        pass
    return(user_info)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)