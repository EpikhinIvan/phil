from django.core.management.base import BaseCommand
from telebot import TeleBot, types
from telebot.types import Message, CallbackQuery
from mybot.models import *
from django.core.files.base import ContentFile
from django.core.files import File
import os
from datetime import datetime


ADMIN_TELEGRAM_ID = 865127428
bot = TeleBot('6122302252:AAHEre4ween54cvQtZn3bQ9Nsv20dEO7QMo')


# Сюда можно команды пихнуть
@bot.message_handler(commands=['help'])
def help_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f'/start - перезапуск бота')
    

# Это старт и потом создание клавы подать заявки
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Добро пожаловать в главное меню бота 'Название Организации'.\n"
                              "Здесь вы можете подать свои обращения, жалобы и вопросы на предмет экологии города Алматы.")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    request_button = types.KeyboardButton("Подать заявку")
    markup.add(request_button)

    bot.send_message(chat_id, "Вы можете подать заявку, нажав на кнопку ниже:", reply_markup=markup)
    


# Это обработчик текста Подать Заявку
@bot.message_handler(func=lambda message: message.text == 'Подать заявку')
def request_application(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Для начала, пожалуйста, напишите ваше ФИО", reply_markup=markup)
    
    bot.register_next_step_handler(message, process_name_step)




# Это фунция обработки имени юзера
def process_name_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.text is None:
        bot.send_message(chat_id, "Пожалуйста, напишите имя текстом")
        bot.register_next_step_handler(message, process_name_step)
        return
    
    full_name = message.text.strip()

    if not all(char.isalpha() or char.isspace() for char in full_name):
        bot.send_message(chat_id, "Пожалуйста, введите ваше имя в правильном формате.")
        bot.register_next_step_handler(message, process_name_step)
        return
    
    user_request = UserRequest(user_id=user_id, full_name=full_name)
    user_request.save()

    markup = types.ReplyKeyboardMarkup()
    categories = ['Свалка', 'Задымление', 'Вырубка деревьев', 'Незаконный выброс естественных отходов', 'Другое']

    for category in categories:
        markup.add(types.KeyboardButton(category))

    bot.send_message(chat_id, "Отлично! Теперь выберите категорию:", reply_markup=markup)
    bot.register_next_step_handler(message, process_category_step)




# Это функция обработки категории
def process_category_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.text is None:
        bot.send_message(chat_id, "Пожалуйста, выберите категорию из списка.")
        bot.register_next_step_handler(message, process_category_step)
        return

    category = message.text

    if category not in ['Свалка', 'Задымление', 'Вырубка деревьев', 'Незаконный выброс естественных отходов', 'Другое']:
        bot.send_message(chat_id, "Пожалуйста, выберите категорию из списка.")
        bot.register_next_step_handler(message, process_category_step)
        return
    
    # вот такую фигню с latest нужно обязательно использовать иначе сломается
    user_request = UserRequest.objects.filter(user_id=user_id).latest('time')
    
    user_request.report_category = category
    user_request.save()

    markup = types.ReplyKeyboardRemove()

    bot.send_message(chat_id, "Отлично! Теперь напишите описание вашего запроса.", reply_markup=markup)
    bot.register_next_step_handler(message, process_description_step)



# это функция для обработки описания
def process_description_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.text is None:
        bot.send_message(chat_id, "Пожалуйста напишите описание.")
        bot.register_next_step_handler(message, process_description_step)
        return

    description = message.text.strip()

    user_request = UserRequest.objects.filter(user_id=user_id).latest('time')
    
    user_request.report_text = description
    user_request.save()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Отправить свою локацию", request_location=True)
    markup.add(button)

    bot.send_message(chat_id, "Спасибо! Теперь отправьте мне свою геопозицию.", reply_markup=markup)
    bot.register_next_step_handler(message, process_location_step)



# это функция обработки геопозиции
def process_location_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    markup = types.ReplyKeyboardRemove()

    if message.location:
        location_lat = message.location.latitude
        location_lon = message.location.longitude

        user_request = UserRequest.objects.filter(user_id=user_id).latest('time')
        user_request.location_lat = location_lat
        user_request.location_lon = location_lon
        user_request.save()

        bot.send_message(chat_id, "Спасибо! Теперь отправьте мне фотографию.", reply_markup=markup)
        bot.register_next_step_handler(message, process_photo_step)
    else:
        bot.send_message(chat_id, "Пожалуйста, отправьте ваше местоположение.")
        bot.register_next_step_handler(message, process_location_step)


# это функция обработки фотографии
def process_photo_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Вот эту фигню тоже не трогай иначе фотографии не будут сохраняться туда куда я хочу
    if message.photo:
        photo = message.photo[-1]

        file_info = bot.get_file(photo.file_id)
        file_path = file_info.file_path
        
        downloaded_file = bot.download_file(file_path)

        photo_content = ContentFile(downloaded_file)

        photo_file = File(photo_content)

        image_path = os.path.join('report_photos', file_path.split('/')[-1])

        with open(image_path, 'wb') as f:
            f.write(photo_file.read())

        user_request = UserRequest.objects.filter(user_id=user_id).latest('time')
        
        user_request.report_photo = image_path
        user_request.save()

        bot.send_message(chat_id, "Отлично! Ваша заявка успешно сохранена.")
        create_report_message(message)
    else:
        bot.send_message(chat_id, "Пожалуйста, отправьте фотографию.")
        bot.register_next_step_handler(message, process_photo_step)

    
def create_report_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_request = UserRequest.objects.filter(user_id=user_id).latest('time')

    formatted_time = user_request.time.strftime('%Y-%m-%d %H:%M:%S')

    with open(user_request.report_photo.path, 'rb') as photo_file:
        bot.send_photo(chat_id, photo=photo_file,
                       caption=(f'<b>ФИО:</b> {user_request.full_name}'
                                f'\n<b>Дата обращения:</b> {formatted_time}'
                                f'\n<b>Категория обращения:</b> {user_request.report_category}'
                                f'\n<b>Описание:</b>\n{user_request.report_text}'),
                       parse_mode='HTML')

    bot.send_location(chat_id, latitude=user_request.location_lat, longitude=user_request.location_lon)




# # тУТА аДМиНсКаЯ ЧаСтЬ


# ADMIN_TELEGRAM_ID = 943230099
 
# # команда для админа типа старт
# @bot.message_handler(commands=['show_requests'])
# def show_requests(message):
#     if message.from_user.id == ADMIN_TELEGRAM_ID:
#         send_all_requests(message.chat.id)
#     else:
#         bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")


# # высылаются все задачи непрочитанные
# def send_all_requests(chat_id):
#     requests = UserRequest.objects.filter(status=True)
#     if requests:
#         for request in requests:
#             send_request(chat_id, request)
#     else:
#         bot.send_message(chat_id, "Нет непрочитанных заявок.")



# # выбранная заявка
# def send_request(chat_id, request):
#     formatted_time = request.time.strftime('%Y-%m-%d %H:%M:%S')
#     bot.send_photo(chat_id, photo=open(request.report_photo.path, 'rb'),
#                    caption=(f'<b>ФИО:</b> {request.full_name}'
#                             f'\n<b>Дата обращения:</b> {formatted_time}'
#                             f'\n<b>Категория обращения:</b> {request.report_category}'
#                             f'\n<b>Описание:</b>\n{request.report_text}'),
#                    parse_mode='HTML',
#                    reply_markup=generate_reply_markup(request.id))
    


# # Функция для генерации клавиатуры с кнопкой выбора заявки
# def generate_reply_markup(request_id):
#     markup = types.InlineKeyboardMarkup()
#     button = types.InlineKeyboardButton("Выбрать заявку", callback_data=f"select_request:{request_id}")
#     markup.add(button)
#     return markup



# # Обработчик нажатия кнопки "Выбрать заявку"
# @bot.callback_query_handler(func=lambda call: call.data.startswith('select_request'))
# def select_request(call):
#     request_id = int(call.data.split(':')[1])
#     request = UserRequest.objects.get(id=request_id)
#     send_request_to_admin(call.message.chat.id, request)
#     update_request_status(request_id)



# # Функция для отправки выбранной заявки администратору и изменения ее статуса
# def send_request_to_admin(chat_id, request):
#     formatted_time = request.time.strftime('%Y-%m-%d %H:%M:%S')
#     bot.send_photo(chat_id, photo=open(request.report_photo.path, 'rb'),
#                    caption=(f'<b>ФИО:</b> {request.full_name}'
#                             f'\n<b>Дата обращения:</b> {formatted_time}'
#                             f'\n<b>Категория обращения:</b> {request.report_category}'
#                             f'\n<b>Описание:</b>\n{request.report_text}'),
#                    parse_mode='HTML',
#                    reply_markup=generate_answer_markup(request.id))
    


# # Функция для генерации клавиатуры с кнопкой ответа на заявку
# def generate_answer_markup(request_id):
#     markup = types.InlineKeyboardMarkup()
#     button = types.InlineKeyboardButton("Ответить на заявку", callback_data=f"answer_request:{request_id}")
#     markup.add(button)
#     return markup



# # Функция для изменения статуса заявки на False
# def update_request_status(request_id):
#     request = UserRequest.objects.get(id=request_id)
#     request.status = False
#     request.save()



# # Обработчик нажатия кнопки "Ответить на заявку"
# @bot.callback_query_handler(func=lambda call: call.data.startswith('answer_request'))
# def answer_request(call):
#     request_id = int(call.data.split(':')[1])
#     bot.send_message(call.message.chat.id, "Введите ваше имя:")
#     bot.register_next_step_handler(call.message, process_name_step, request_id)

# # Обработчик имени администратора
# def process_name_step(message, request_id):
#     name = message.text.strip()
#     bot.send_message(message.chat.id, "Введите описание вашего действия:")
#     bot.register_next_step_handler(message, process_description_step, request_id, name)

# # Обработчик описания действия
# def process_description_step(message, request_id, name):
#     description = message.text.strip()
#     bot.send_message(message.chat.id, "Отправьте фотографию вашего действия:")
#     bot.register_next_step_handler(message, process_photo_step2, request_id, name, description)

# # Обработчик фотографии действия
# def process_photo_step2(message, request_id, name, description):
#     if message.photo:
#         photo = message.photo[-1]
#         file_info = bot.get_file(photo.file_id)
#         file_path = file_info.file_path
#         downloaded_file = bot.download_file(file_path)
        
#         # Сохранение фотографии на сервере
#         with open(f'{file_path}.jpg', 'wb') as new_file:
#             new_file.write(downloaded_file)
        
#         # Создание ответа администратора
#         admin_response = AdminResponse.objects.create(user_request_id=request_id, admin_full_name=name,
#                                                        admin_response_text=description, admin_response_photo=f'{file_path}.jpg')
#         admin_response.save()
        
#         # Отправка сообщения пользователю с полным сообщением
#         send_full_response_to_user(message, name, description, f'{file_path}.jpg')

#     else:
#         bot.send_message(message.chat.id, "Пожалуйста, отправьте фотографию вашего действия.")
#         bot.register_next_step_handler(message, process_photo_step, request_id, name, description)

# # Функция для отправки полного сообщения пользователю
# def send_full_response_to_user(message, name, description, photo_path):
#     user_request = UserRequest.objects.get(id=message.from_user.id)
#     formatted_time = user_request.time.strftime('%Y-%m-%d %H:%M:%S')

#     bot.send_photo(message.chat.id, photo=open(photo_path, 'rb'),
#                    caption=(f'<b>ФИО администратора:</b> {name}'
#                             f'\n<b>Описание действия:</b> {description}'
#                             f'\n<b>Фотография действия:</b>'),
#                    parse_mode='HTML')








# прикольный шлак

@bot.message_handler(content_types='photo')
def get_photo(message):
    bot.send_message(message.chat.id, 'У меня нет возможности просматривать фото :(')


@bot.message_handler(content_types='text')
def get_photo(message):
    bot.send_message(message.chat.id, 'Простите, я не умею читать :(')



class Command(BaseCommand):
    help = 'Runs the telegram bot'

    def handle(self, *args, **options):
        bot.polling()