from django.core.management.base import BaseCommand
from telebot import TeleBot, types
from telebot.types import Message, CallbackQuery
from mybot.models import *
from django.core.files.base import ContentFile
from django.core.files import File
import os
from datetime import datetime

user_language_preferences = {}

ADMIN_TELEGRAM_ID = 865127428
bot = TeleBot('6122302252:AAHEre4ween54cvQtZn3bQ9Nsv20dEO7QMo')


# Сюда можно команды пихнуть
@bot.message_handler(commands=['help'])
def help_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f'/start - перезапуск бота')
    

# Функция для выбора языка при старте бота
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Выберите язык / Тілді таңдаңыз",
                     reply_markup=generate_language_markup())


# Функция для генерации клавиатуры выбора языка
def generate_language_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Русский"), types.KeyboardButton("Қазақша"))
    return markup


# Функция для обработки выбора языка
@bot.message_handler(func=lambda message: message.text in ['Русский', 'Қазақша'])
def process_language(message):
    chat_id = message.chat.id
    language = message.text.lower()

    user_language_preferences[chat_id] = language

    send_welcome_message(chat_id, language)


# Функция для отправки приветственного сообщения на выбранном языке
def send_welcome_message(chat_id, language):
    if language == 'русский':
        bot.send_message(chat_id, "Добро пожаловать в главное меню бота 'Название Организации'.\n"
                                  "Здесь вы можете подать свои обращения, жалобы и вопросы на предмет экологии города Алматы.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        request_button = types.KeyboardButton("Подать заявку")
        markup.add(request_button)

        bot.send_message(chat_id, "Вы можете подать заявку, нажав на кнопку ниже:", reply_markup=markup)
        
    else:
        bot.send_message(chat_id, "Ұйымның атауы ботының негізгі мәзіріне қош келдіңіз\n"
                                  "Мұнда Сіз Алматы қаласының экологиясы бойынша өз өтініштеріңізді, шағымдарыңызды және сұрақтарыңызды бере аласыз.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        request_button = types.KeyboardButton("Өтініш беру")
        markup.add(request_button)

        bot.send_message(chat_id, "Төмендегі түймені басу арқылы өтініш бере аласыз:", reply_markup=markup)




# Это обработчик текста Подать Заявку
@bot.message_handler(func=lambda message: message.text in ['Подать заявку', 'Өтініш беру'])
def request_application(message):
    chat_id = message.chat.id
    language = user_language_preferences.get(chat_id, 'русский')
    markup = types.ReplyKeyboardRemove()

    if language == 'русский':
        bot.send_message(chat_id, "Для начала, пожалуйста, напишите ваше ФИО", reply_markup=markup)
    else: 
        bot.send_message(chat_id, "Бастау үшін аты-жөніңізді жазыңыз", reply_markup=markup)
        
    
    bot.register_next_step_handler(message, process_name_step)




# Это фунция обработки имени юзера
def process_name_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = user_language_preferences.get(chat_id, 'русский')

    if message.text is None:
        if language == 'русский':
            bot.send_message(chat_id, "Пожалуйста, напишите имя текстом")
        else:
            bot.send_message(chat_id, "Атын мәтінмен жазыңыз")

        bot.register_next_step_handler(message, process_name_step)
        return
    
    
    full_name = message.text.strip()

    if not all(char.isalpha() or char.isspace() for char in full_name):
        if language == 'русский':
            bot.send_message(chat_id, "Пожалуйста, введите ваше имя в правильном формате.")
        else:
            bot.send_message(chat_id, "Атыңызды дұрыс форматта енгізіңіз.")
        
        bot.register_next_step_handler(message, process_name_step)
        return
    
    user_request = UserRequest(user_id=user_id, full_name=full_name)
    user_request.save()

    if language == 'русский':
        markup = types.ReplyKeyboardMarkup()
        categories = ['Свалка', 'Задымление', 'Вырубка деревьев', 'Незаконный выброс естественных отходов', 'Другое']

        for category in categories:
            markup.add(types.KeyboardButton(category))
    else:
        markup = types.ReplyKeyboardMarkup()
        categories = ['Свалка', 'Түтін', 'Ағаштарды кесу', 'Табиғи қалдықтардың заңсыз шығарылуы', 'Басқа']

        for category in categories:
            markup.add(types.KeyboardButton(category))

    if language == 'русский':
        bot.send_message(chat_id, "Отлично! Теперь выберите категорию:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Керемет! Енді санатты таңдаңыз:", reply_markup=markup)

    bot.register_next_step_handler(message, process_category_step)




# Это функция обработки категории
def process_category_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = user_language_preferences.get(chat_id, 'русский')

    if message.text is None:
        if language == 'русский':
            bot.send_message(chat_id, "Пожалуйста, выберите категорию из списка.")
        else:
            bot.send_message(chat_id, "Тізімнен санатты таңдаңыз.")

        bot.register_next_step_handler(message, process_category_step)
        return

    category = message.text
    if language == 'русский':
        if category not in ['Свалка', 'Задымление', 'Вырубка деревьев', 'Незаконный выброс естественных отходов', 'Другое']:
            bot.send_message(chat_id, "Пожалуйста, выберите категорию из списка.")
            bot.register_next_step_handler(message, process_category_step)  
    else:
        if category not in ['Свалка', 'Түтін', 'Ағаштарды кесу', 'Табиғи қалдықтардың заңсыз шығарылуы', 'Басқа']:
            bot.send_message(chat_id, "Тізімнен санатты таңдаңыз.")
            bot.register_next_step_handler(message, process_category_step)  
            return
    
    # вот такую фигню с latest нужно обязательно использовать иначе сломается
    user_request = UserRequest.objects.filter(user_id=user_id).latest('time')
    
    user_request.report_category = category
    user_request.save()

    markup = types.ReplyKeyboardRemove()
    if language == 'русский':
        bot.send_message(chat_id, "Отлично! Теперь напишите описание вашего запроса.", reply_markup=markup)
        bot.register_next_step_handler(message, process_description_step)
    else:
        bot.send_message(chat_id, "Керемет! Енді сұрауыңыздың сипаттамасын жазыңыз.", reply_markup=markup)
        bot.register_next_step_handler(message, process_description_step)



# это функция для обработки описания
def process_description_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = user_language_preferences.get(chat_id, 'русский')

    if message.text is None:
        if language == 'русский':
            bot.send_message(chat_id, "Пожалуйста напишите описание.")
            bot.register_next_step_handler(message, process_description_step)
            return
        else:
            bot.send_message(chat_id, "Сипаттама жазыңыз.")
            bot.register_next_step_handler(message, process_description_step)
            return

    description = message.text.strip()

    user_request = UserRequest.objects.filter(user_id=user_id).latest('time')
    
    user_request.report_text = description
    user_request.save()
    
    if language == 'русский':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton(text="Отправить свою локацию", request_location=True)
        markup.add(button)
        bot.send_message(chat_id, "Спасибо! Теперь отправьте мне свою геолокацию.", reply_markup=markup)
        bot.register_next_step_handler(message, process_location_step)


    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton(text="Орналасқан жеріңізді жіберіңіз", request_location=True)
        markup.add(button)
        bot.send_message(chat_id, "Рахмет! Енді маған геолокацияңызды жіберіңіз.", reply_markup=markup)
        bot.register_next_step_handler(message, process_location_step)






# это функция обработки геопозиции
def process_location_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    markup = types.ReplyKeyboardRemove()
    language = user_language_preferences.get(chat_id, 'русский')

    if message.location:
        location_lat = message.location.latitude
        location_lon = message.location.longitude

        user_request = UserRequest.objects.filter(user_id=user_id).latest('time')
        user_request.location_lat = location_lat
        user_request.location_lon = location_lon
        user_request.save()
        
        if language == 'русский':
            bot.send_message(chat_id, "Спасибо! Теперь отправьте мне фотографию.", reply_markup=markup)
        else:
            bot.send_message(chat_id, "Рахмет! Енді маған фотосурет жіберіңіз.", reply_markup=markup)
        
        bot.register_next_step_handler(message, process_photo_step)
    else:
        if language == 'русский':
            bot.send_message(chat_id, "Пожалуйста, отправьте ваше местоположение.")
        else:
            bot.send_message(chat_id, "Орналасқан жеріңізді жіберіңіз.")
        
        bot.register_next_step_handler(message, process_location_step)


# это функция обработки фотографии
def process_photo_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = user_language_preferences.get(chat_id, 'русский')

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

        if language == 'русский':
            bot.send_message(chat_id, "Отлично! Ваша заявка успешно сохранена.")
        else:
            bot.send_message(chat_id, "Керемет! Сіздің өтінішіңіз сәтті сақталды.")

        create_report_message(message)
    else:
        if language == 'русский':
            bot.send_message(chat_id, "Пожалуйста, отправьте фотографию.")
        else:
            bot.send_message(chat_id, "Фотосуретті жіберіңіз.")

        bot.register_next_step_handler(message, process_photo_step)

    
def create_report_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_request = UserRequest.objects.filter(user_id=user_id).latest('time')

    formatted_time = user_request.time.strftime('%Y-%m-%d %H:%M:%S')

    language = user_language_preferences.get(chat_id, 'русский')

    if language == 'русский':
        caption_text = (f'<b>ФИО:</b> {user_request.full_name}'
                        f'\n<b>Дата обращения:</b> {formatted_time}'
                        f'\n<b>Категория обращения:</b> {user_request.report_category}'
                        f'\n<b>Описание:</b>\n{user_request.report_text}')
        location_text = "Отправляю ваше местоположение:"
    else:
        caption_text = (f'<b>ТАӘ</b> {user_request.full_name}'
                        f'\n<b>Жүгінген күні:</b> {formatted_time}'
                        f'\n<b>Өтініш санаты:</b> {user_request.report_category}'
                        f'\n<b>Сипаттама:</b>\n{user_request.report_text}')
        location_text = "сіздің орналасқан жеріңіз:"

    with open(user_request.report_photo.path, 'rb') as photo_file:
        bot.send_photo(chat_id, photo=photo_file,
                       caption=caption_text,
                       parse_mode='HTML')

    bot.send_message(chat_id, location_text)
    bot.send_location(chat_id, latitude=user_request.location_lat, longitude=user_request.location_lon)




# тУТА аДМиНсКаЯ ЧаСтЬ


ADMIN_TELEGRAM_ID = 943230099
 
# команда для админа типа старт
@bot.message_handler(commands=['show_requests'])
def show_requests(message):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        send_all_requests(message.chat.id)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")


# высылаются все задачи непрочитанные
def send_all_requests(chat_id):
    requests = UserRequest.objects.filter(status=True)
    if requests:
        for request in requests:
            send_request(chat_id, request)
    else:
        bot.send_message(chat_id, "Нет непрочитанных заявок.")



# заявочки
def send_request(chat_id, request):
    formatted_time = request.time.strftime('%Y-%m-%d %H:%M:%S')
    bot.send_photo(chat_id, photo=open(request.report_photo.path, 'rb'),
                   caption=(f'<b>ФИО:</b> {request.full_name}'
                            f'\n<b>Дата обращения:</b> {formatted_time}'
                            f'\n<b>Категория обращения:</b> {request.report_category}'
                            f'\n<b>Описание:</b>\n{request.report_text}'),
                   parse_mode='HTML',
                   reply_markup=generate_reply_markup(request.id))
    
    bot.send_location(chat_id, latitude=request.location_lat, longitude=request.location_lon)
    
    


# Функция для генерации клавиатуры с кнопкой выбора заявки
def generate_reply_markup(request_id):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Выбрать заявку", callback_data=f"select_request:{request_id}")
    markup.add(button)
    return markup



# Выбрать заявку обработчик
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_request'))
def select_request(call):
    request_id = int(call.data.split(':')[1])
    request = UserRequest.objects.get(id=request_id)
    send_request_to_admin(call.message.chat.id, request)

    # Удаляем сообщение о выбранной заявке
    bot.delete_message(call.message.chat.id, call.message.message_id)



# Функция для отправки выбранной заявки администратору и изменения ее статуса
def send_request_to_admin(chat_id, request):
    formatted_time = request.time.strftime('%Y-%m-%d %H:%M:%S')
    bot.send_photo(chat_id, photo=open(request.report_photo.path, 'rb'),
                   caption=(f'<b>ФИО:</b> {request.full_name}'
                            f'\n<b>Дата обращения:</b> {formatted_time}'
                            f'\n<b>Категория обращения:</b> {request.report_category}'
                            f'\n<b>Описание:</b>\n{request.report_text}'),
                   parse_mode='HTML',
                   reply_markup=generate_answer_markup(request.id))
    bot.send_location(chat_id, latitude=request.location_lat, longitude=request.location_lon)
    
    


# Функция для генерации клавиатуры с кнопкой ответа на заявку
def generate_answer_markup(request_id):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Ответить на заявку", callback_data=f"answer_request:{request_id}")
    markup.add(button)
    return markup



# Статус меняем и отправляем сообщение юзеру
def update_request_status(request_id):
    request = UserRequest.objects.get(id=request_id)
    request.status = False
    request.save()

    user_id = request.user_id
    bot.send_message(user_id, "Ваша заявка была выбрана для обработки. Ожидайте ответа в течении 15 рабочий дней.\n"
                     "Сіздің өтінішіңіз өңдеу үшін таңдалды. 15 жұмыс күні ішінде жауап күтіңіз.")



# Ответить на заявку обработчик
@bot.callback_query_handler(func=lambda call: call.data.startswith('answer_request'))
def answer_request(call):
    request_id = int(call.data.split(':')[1])
    update_request_status(request_id)
    bot.send_message(call.message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(call.message, process_name_step2, request_id)



# это функция обработки имени пользователя
def process_name_step2(message, request_id):
    chat_id = message.chat.id

    if message.text is None:
        bot.send_message(chat_id, "Пожалуйста, напишите имя текстом")
        bot.register_next_step_handler(message, process_name_step2, request_id)
        return
    
    name = message.text.strip()

    if not all(char.isalpha() or char.isspace() for char in name):
        bot.send_message(chat_id, "Пожалуйста, введите ваше имя в правильном формате.")
        bot.register_next_step_handler(message, process_name_step2, request_id)
        return
    
    bot.send_message(message.chat.id, "Введите описание вашего действия:")
    bot.register_next_step_handler(message, process_description_step2, request_id, name)

    

# это функция для обработки описания
def process_description_step2(message, request_id, name):
    chat_id = message.chat.id

    if message.text is None:
        bot.send_message(chat_id, "Пожалуйста напишите описание.")
        bot.register_next_step_handler(message, process_description_step2, request_id, name)
        return
    
    description = message.text.strip()

    bot.send_message(message.chat.id, "Отправьте фотографию вашего действия:")
    bot.register_next_step_handler(message, process_photo_step2, request_id, name, description)


# Обработчик фотографии действия
def process_photo_step2(message, request_id, name, description):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.photo:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)

        photo_content = ContentFile(downloaded_file)

        photo_file = File(photo_content)

        image_path = os.path.join('response_photos', file_path.split('/')[-1])

        with open(image_path, 'wb') as f:
            f.write(photo_file.read())

        admin_response = AdminResponse.objects.create(user_request_id=request_id, admin_full_name=name,
                                                       admin_response_text=description, admin_response_photo=image_path)
        admin_response.save()

        send_full_response_to_user(request_id, name, description, image_path)
        bot.send_message(chat_id, 'Благодарим за обработку заявления')

    else:
        bot.send_message(chat_id, "Пожалуйста, отправьте фотографию.")
        bot.register_next_step_handler(message, process_photo_step2, request_id, name, description)


# Отправляем полное сообщение юзеру о выполненной работе
def send_full_response_to_user(request_id, name, description, photo_path):
    user_request = UserRequest.objects.get(id=request_id)
    formatted_time = user_request.time.strftime('%Y-%m-%d %H:%M:%S')
    language = user_language_preferences.get(user_request.user_id, 'русский')

    if language == 'русский':
        caption_text = (f'<b>ФИО администратора:</b> {name}'
                        f'\n<b>Описание действия:</b> {description}'
                        f'\n<b>Дата выполнения:</b> {formatted_time}')
    else:
        caption_text = (f'<b>Әкімшінің аты-жөні:</b> {name}'
                        f'\n<b>Әрекет сипаттамасы:</b> {description}'
                        f'\n<b>Орындалу күні:</b> {formatted_time}')

    bot.send_photo(user_request.user_id, photo=open(photo_path, 'rb'),
                   caption=caption_text,
                   parse_mode='HTML')








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