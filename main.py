# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberStatus
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import copy
from pprint import pprint

# Установка соединения с базой данных при помощи ORM
engine = create_engine('mysql://user1:1234@localhost/taro-bot')

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
end_survey_text = '🚫 Закончить опрос'
back_to_survey_text = '⬅️ Назад к анкете'
survey_is_finished_text = 'Заполнение анкеты завершено. Вы сможете отредактировать ее позднее, если захотите.'
survey_is_in_progress_text = f'Пожалуйста, выберите любой вопрос, на который Вы хотели бы дать ответ или закончите анкетирование:'
main_menu_text = 'Здесь Вы можете просмотреть услуги, которые мы предлагаем, контакты, по которым с нами можно связаться или же отредактировать анкету.'
arrow_up_text = "⬆️"
arrow_down_text = "⬇️"


#переменные
chat_id = -4139713338
current_part_of_survey = 0
commands = ['start', 'open', 'go']

main_menu_buttons = ["Список услуг","Наши контакты","Просмотр анкеты","Редактирование анкеты"]
main_menu_buttons_for_owners = ["Список пользователей","Просмотр анкеты пользователя"]
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

#состояния
class Form(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()



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

questions_part_3 = {'Какой вид консультации вы хотите выбрать?':'Какой вид консультации Вы хотите выбрать? (выберите одно)',
                    'Какой вид общения предпочитаете?':'Какой вид общения Вы предпочитаете? (выберите одно):'}

questions_part_4 = {'Ваш род деятельности':'Напишите, пожалуйста, чем Вы занимаетесь?',
                    'Ваши ожидания':'Какой результат Вы ожидаете от нашей с вами работы?',
                    'Почему решили обратиться ко мне':'Почему Вы решили пойти на консультацию/наставничество именно ко мне?',
                    'Почему мне стоит взять именно Вас':'Почему мне стоит взять именно Вас?'}

questions_part_5 = {'Понятие энергоценности':'Вам известно понятие энергоценность?',
                    'Степень доверия':'Насколько вы готовы довериться мне? (по 10-балльной шкале)'}

all_questions_dict = {'questions_part_1':questions_part_1,
                      'questions_part_2':questions_part_2,
                      'questions_part_3':questions_part_3,
                      'questions_part_4':questions_part_4,
                      'questions_part_5':questions_part_5}

all_questions_WITH_ANSWERS_dict = copy.deepcopy(all_questions_dict)
for every_subdict in all_questions_WITH_ANSWERS_dict:
    for every in all_questions_WITH_ANSWERS_dict[every_subdict]:
        question_text = all_questions_WITH_ANSWERS_dict[every_subdict][every] = 'без ответа'



#текущая часть анкеты
def process_current_questions_part_status(arg):
    current_part_of_survey_status = f'({arg}/5)'
    return current_part_of_survey_status


#секция с клавиатурами
button_main_agree = KeyboardButton('Да, хочу')
button_main_disagree = KeyboardButton('Нет, не хочу')
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
    elif current_part_of_survey == 5:
        questions_part = questions_part_5

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
        await bot.get_chat_member(chat_id, user_id)
        await bot.send_message(message.from_user.id, text="Вы состоите в группе :)", reply_markup=main_menu())
    except:
        await bot.send_message(message.from_user.id, text="Вы не состоите в группе :(", reply_markup=main_menu())
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
def main_menu():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*main_menu_buttons)
    if session.query(InformationAboutUsers).filter_by(is_owner=1):
        keyboard.add(KeyboardButton(text='Список пользователей'), (KeyboardButton(text='Просмотр анкеты пользователя')))
    return keyboard


def services_menu():
    keyboard = InlineKeyboardMarkup()
    services_buttons_dict = {"Услуга 1":'service_1',
                             "Услуга 2":'service_2',
                             "Услуга 3":'service_3'}
    for key, value in services_buttons_dict.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
    return keyboard


def contacts_menu():
    keyboard = InlineKeyboardMarkup()
    contacts_buttons_dict = {"Контакт 1":'contact_1',
                             "Контакт 2":'contact_2',
                             "Контакт 3":'contact_3'}
    for key, value in contacts_buttons_dict.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
    return keyboard

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
    part_of_survey = all_questions_WITH_ANSWERS_dict.get(questions_part)
    key = find_key_by_value(all_questions_dict[questions_part], question)
    part_of_survey[key] = answer_user

#отобразить полную анкету
async def show_answered_full_survey(id):
    question_number_in_survey = 0
    survey_answers_list = 'Ваша анкета\n'
    for key, value in all_questions_WITH_ANSWERS_dict.items():
        for question, answer in value.items():
            print()
            question_number_in_survey  += 1
            survey_answers_list+= f'{question_number_in_survey }.{question}\n"{all_questions_dict[key][question]}"\nВаш ответ: {answer}\n\n'
            if question_number_in_survey == 10:
                await bot.send_message(id, survey_answers_list)
                survey_answers_list = ''
    if survey_answers_list != '':
        await bot.send_message(id, survey_answers_list)


# def save_data_to_db():


@dp.message_handler(commands=commands)
async def process_start_command(message: types.Message):
    # Вставляем основную запись с полем 'id'
    global user_id
    user_id = message.from_user.id
    data_from_message = ['id', 'username', 'first_name', 'last_name']
    values = [getattr(message.from_user, column) for column in data_from_message]
    existing_user = session.query(InformationAboutUsers).filter_by(id=values[0]).first()
    if existing_user:
        existing_user.username = values[1]
        existing_user.first_name = values[2]
        existing_user.last_name = values[3]
        session.commit()
        await bot.send_message(message.chat.id, text=f'Данные пользователя с id={values[0]} успешно обновлены.')
    else:
        user_info = InformationAboutUsers(id=values[0], username=values[1], first_name=values[2], last_name=values[3])
        session.add(user_info)
        session.commit()
        await bot.send_message(message.chat.id, text=f'Пользователь с id={values[0]} успешно добавлен в базу данных.')
    await message.reply("Здравствуйте! Я - бот, и я помогу Вам с тем, что Вам нужно. "
                        "Желаете заполнить анкету для улучшения взаимодействия?", reply_markup=greet_kb)

# Обработчик кнопки "Список услуг"
@dp.message_handler(lambda message: message.text == main_menu_buttons[0], state="*")
async def process_services_menu(message: types.Message):
    await message.answer("Здесь Вы можете найти список наших услуг:", reply_markup=services_menu())

# Обработчик кнопки "Наши контакты"
@dp.message_handler(lambda message: message.text == main_menu_buttons[1], state="*")
async def process_contacts_menu(message: types.Message):
    await message.answer("Наши контакты:", reply_markup=contacts_menu())

# Обработчик кнопки "Просмотр анкеты"
@dp.message_handler(lambda message: message.text == main_menu_buttons[2], state="*")
async def show_survey_for_user(message: types.Message):
    await show_answered_full_survey(message.from_user.id)


# Обработчик кнопки "Редактирование анкеты"
@dp.message_handler(lambda message: message.text == main_menu_buttons[3], state="*")
async def process_edit_survey(message: types.Message):
    await bot.send_message(message.from_user.id, f'{process_current_questions_part_status(current_part_of_survey)} {survey_is_in_progress_text}',
                           reply_markup=survey_part())

@dp.message_handler(lambda message: message.text == main_menu_buttons_for_owners[0], state="*")
async def process_all_registered_users(message: types.Message):
    result = session.execute(select(InformationAboutUsers.id, InformationAboutUsers.username, InformationAboutUsers.first_name, InformationAboutUsers.last_name))
    all_registered_users = f"Все зарегистрированные пользователи:\n"
    for index, row in enumerate(result):
        print(index)
        print(row)
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
            await message.answer(text=all_registered_users, reply_markup=main_menu())
            all_registered_users = ''
        else:
            pass

    await message.answer(text=all_registered_users, reply_markup=main_menu())


@dp.message_handler(lambda message: message.text == main_menu_buttons_for_owners[1], state="*")
async def process_contacts_menu(message: types.Message):
    await message.answer("Пожалуйста, введите id пользователя, анкету которого вы желаете просмотреть:", reply_markup=main_menu())


#обработка стартового выбора (проходить анкету или нет)
@dp.message_handler()
async def process_start_command(message: types.Message):
    global current_part_of_survey
    current_part_of_survey = 0
    current_part_of_survey += 1
    if message.text == 'Да, хочу':
        await bot.send_message(message.from_user.id, f'{process_current_questions_part_status(current_part_of_survey)} {survey_is_in_progress_text}',
                               reply_markup=survey_part())

    elif message.text == 'Нет, не хочу':
        await bot.send_message(message.from_user.id, main_menu_text, reply_markup=main_menu())







#обработка выбора вопроса из inline-меню анкеты
@dp.callback_query_handler(lambda c: c.data.startswith('question_'), state='*')
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
    # elif 'Подписаны' in question:
    #     await callback_query.message.edit_text(
    #         question,
    #         reply_markup=check_if_chat_member_menu())
    else:
        await callback_query.message.edit_text(
            question,
            reply_markup=back_to_survey_kb())

    async with state.proxy() as data:
        data['question_message_id'] = callback_query.message.message_id


#ответы на вопросы, предполагающие произвольный ответ
@dp.message_handler(state='*')
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
                             f'Выберите вопрос или нажмите "{end_survey_text[2:]}".',
                         reply_markup=survey_part())
        global all_questions_WITH_ANSWERS_dict
        #сохранение ответа в словарь
        answers_questions_part = f'questions_part_{current_part_of_survey}'
        key = find_key_by_value(all_questions_dict[answers_questions_part], question)
        all_questions_WITH_ANSWERS_dict[answers_questions_part][key] = answer
        await Form.waiting_for_question.set()
        async with state.proxy() as data:
            data['question'] = None
        return



#ответы на вопрос "предпочитаемый вид общения"
@dp.callback_query_handler(lambda c: find_key_by_value(prefered_way_to_communicate, c.data), state="*")
async def process_back_to_survey(callback_query: types.CallbackQuery):
    update_data(prefered_way_to_communicate, callback_query.data, current_part_of_survey, question)
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(prefered_way_to_communicate, callback_query.data)}". '
        f'Выберите вопрос или нажмите "{end_survey_text[2:]}".',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())


#ответы на вопрос "какой тип консультации вас интересует"
@dp.callback_query_handler(lambda c: find_key_by_value(consultations_types, c.data), state="*")
async def process_back_to_survey(callback_query: types.CallbackQuery):
    update_data(consultations_types, callback_query.data, current_part_of_survey, question)
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(consultations_types, callback_query.data)}". '
        f'Выберите вопрос или нажмите "{end_survey_text[2:]}".',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())


#ответы на вопрос "наиболее актуальный способ связи"
@dp.callback_query_handler(lambda c: find_key_by_value(fastest_way_to_answer, c.data), state="*")
async def process_back_to_survey(callback_query: types.CallbackQuery):
    update_data(fastest_way_to_answer, callback_query.data, current_part_of_survey, question)
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(fastest_way_to_answer, callback_query.data)}". '
        f'Выберите вопрос или нажмите "{end_survey_text[2:]}".',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())

#ответы на вопрос со шкалой
@dp.callback_query_handler(lambda c: find_key_by_value(out_of_ten_scale, c.data), state="*")
async def process_back_to_survey(callback_query: types.CallbackQuery):
    update_data(out_of_ten_scale, callback_query.data, current_part_of_survey, question)
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(out_of_ten_scale, callback_query.data)}". '
        f'Выберите вопрос или нажмите "{end_survey_text[2:]}".',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())

#обработка ответов "да/нет/частично"
@dp.callback_query_handler(lambda c: c.data == 'answer_yes_button'
                                     or c.data == 'answer_no_button'
                                     or c.data == 'answer_partially_button'
                                     or c.data in consultations_types, state="*")
async def process_back_to_survey(callback_query: types.CallbackQuery):
    update_data(yes_no_partially_buttons_dict, callback_query.data, current_part_of_survey, question)
    await callback_query.answer()
    await bot.edit_message_text(
        f'{process_current_questions_part_status(current_part_of_survey)} Ваш ответ на вопрос "{question}":'
        f' "{find_key_by_value(yes_no_partially_buttons_dict, callback_query.data)}". '
        f'Выберите вопрос или нажмите "{end_survey_text[2:]}".',
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=survey_part())


#обработка кнопки "назад" из вопроса
@dp.callback_query_handler(lambda c: c.data == 'back_to_survey', state="*")
async def process_back_to_survey(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await bot.edit_message_text(f'{process_current_questions_part_status(current_part_of_survey)} {survey_is_in_progress_text}',
                                callback_query.from_user.id,
                                callback_query.message.message_id,
                                reply_markup=survey_part())

#стрелка в предыдущую часть анкеты
@dp.callback_query_handler(lambda c: c.data == 'prev_part_of_survey', state="*")
async def process_prev_part_of_survey(callback_query: types.CallbackQuery):
    global current_part_of_survey
    current_part_of_survey -= 1
    await callback_query.answer()
    await bot.edit_message_text(f"{process_current_questions_part_status(current_part_of_survey)} {survey_is_in_progress_text}",
                                callback_query.from_user.id,
                                callback_query.message.message_id,
                                reply_markup=survey_part())

#стрелка в следующую часть анкеты
@dp.callback_query_handler(lambda c: c.data == 'next_part_of_survey', state="*")
async def process_next_part_of_survey(callback_query: types.CallbackQuery):
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
    # if user_in_group is False:
    #     await bot.send_message(callback_query.from_user.id, 'Подпишитесь, пожалуйста, на мою группу. Там Вы сможете найти много интересного!\nhttps://t.me/+kx-uithPXXA3MWQy')
    #
    # else:
    #     pass
    await check_if_chat_member(callback_query, callback_query.from_user.id)
    await bot.edit_message_text(survey_is_finished_text,
                            callback_query.from_user.id,
                            callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, main_menu_text, reply_markup=main_menu())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)