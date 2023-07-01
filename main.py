import requests
import json
import pandas as pd
from telegram.ext import Updater, CommandHandler

# Показываем все столбцы таблицы
pd.set_option('display.max_columns', None)
ids = [18382, 18387, 18417, 18409, 18424]


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для парсинга сайта ITMO.")


def parse(update, context):
    for id in ids:
        # Подключаемся к API
        url = f"https://abitlk.itmo.ru/api/v1/rating/master/budget?program_id={id}&manager_key=&sort=&showLosers=true"

        # Отправляем GET-запрос на получение HTML-кода страницы
        response = requests.get(url)

        # Сохраняем json файл
        dictionary = json.loads(response.text)

        # Выделяем необходимые данные: подавшие документы + количество мест и направление
        data = dictionary['result']

        # Выделяем необходимые данные: подавшие документы
        result = data['general_competition']

        # Выделяем необходимые данные: количество мест и направление + что-то лишнее
        direction = [data['direction']]

        # # Выделяем необходимые данные: средний балл диплома, приоритет и тд.
        df_result = pd.DataFrame(result)
        df_result = df_result[['diploma_average', 'position', 'priority', 'exam_scores', 'total_scores', 'is_send_original']]

        # Выделяем необходимые данные: количество мест и направление
        df_direction = pd.DataFrame(direction)
        df_direction = df_direction[['budget_min', 'program_title']]

        # Вычисляем конкурс на место
        competition = df_result.shape[0] / df_direction['budget_min'][0]

        # Выводим результат
        context.bot.send_message(chat_id=update.effective_chat.id,
            text=f"{df_result.head(7).to_string()}\n\n"
                 f"Конкурс на одно место: {round(competition, 2)} по направлению {df_direction['program_title'][0]}"
                 f" с количеством мест: {df_direction['budget_min'][0]}\n")


updater = Updater('MY_TOKEN', use_context=True)

# Получаем экземпляр диспетчера для регистрации обработчиков команд
dispatcher = updater.dispatcher

# Регистрируем обработчики команд
start_handler = CommandHandler('start', start)
parse_handler = CommandHandler('parse', parse)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(parse_handler)

# Запускаем бота
updater.start_polling()