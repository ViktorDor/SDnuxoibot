
#-=-=-=-=-=-=-=-=-=-=-=-
#Создатель:ViktorGoldFox
#-=-=-=-=-=-=-=-=-=-=-=-
#SDNuxoiBot
#Бот для поздравления с дней рожения и не только

#Функционал:
#В 8:00 по МСК выводит погоду
#В 10:00 проходит по базе данных и поздравляет именниников

# */add - добавить человека в базу данных (Добавляет не на прямую в рабочую базу а в 
# текстовый документ "NewData")
# */weather - вывести погоду

#Админ комманды:
# */stats - получить статистику о работе бота
# */logs - получить логи
# */send_message - отправить сообщение от имени бота

#Импортирование всех модулей
#Некоторые модули нужно установить команнды смотреть в modls.txt
from shlex import join
from time import sleep 
import time
import telebot
import pandas as pd
import schedule
import datetime 
import threading
from urllib import request 
import requests 
import sys, os
import pymorphy2
from gigachat import GigaChat
import openai
from translate import Translator
import click

version = 'v2.6'
#OpenAi
openai.api_key = ""
Gigachat_token = ''
AIlimit = 50
Animspeed = 0.01
Text_limit = 200

translator= Translator(from_lang="Russian",to_lang="English")

#Указание сайта погоды (Open wheather)
#Зайти на сатй openwheather.org и следовать интрукциям
url = ''

#Бот конфиг 
chatid = '' #Поменяйте на id группы
token = '' #Поменяйте на token своего бота

bot = telebot.TeleBot(token=token)

#Указание админов
#Первый админ главный
admins = []

#Указание пути к DataFrame
data = pd.read_csv("Путь")

#Указание переменных (Не менять!!!)
NowDR = []
start_time = datetime.datetime.now()
NowDate = datetime.datetime.now()
time = NowDate.replace(microsecond=0)

#Установка времени. По желанию менять
Weather_time = "08:00"
Gift_time = "10:00"

#========================================================= 
#Обработка команнд
@bot.message_handler(commands=['help'])
def get_help(message):
    bot.send_message(message.chat.id, "/ask - Задать вопрос chatGPT \n /ask_gigachat - Задать вопрос GigaChat \n /add - Добавиться в базу данных \n /weather - Вывести погоду Version: " + version)

#========================================================= 
#Обработка команнд AI
@bot.message_handler(commands=['generate'])
def generate_image(message):
    try:
        argus = message.text.split()
        if len(argus) < 2:
            bot.send_message(message.chat.id, "Нужно ввести запрос. Попробуй снова.")
            return False
        argus.pop(0)
        txt = " ".join(argus)
        # txt = translator.translate(txt)
        mess = bot.send_message(message.chat.id, "🕐 Подождите несколько секунд. Ваше изображение обрабатывается...")
        mess
        completion = openai.Image.create(
  model='dall-e-2',
  prompt=txt,
  n=1
)
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="🕒 Подождите несколько секунд. Ваше изображение обрабатывается.")
        sleep(0.5)
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="🕕 Подождите несколько секунд. Ваше изображение обрабатывается..")
        sleep(0.5)
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="🕘 Подождите несколько секунд. Ваше изображение обрабатывается...")
        sleep(0.5)
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="✅Ваше изображение готово:")
        logs_save(log_text=str(str("[Info] @" + message.from_user.username) + ' Сгенерировал изображение: ' + txt))
        image_url = completion['data'][0]['url']
        file_name = 'image.png'
        request.urlretrieve(image_url, file_name)
        with open("image.png", 'rb') as im:
            bot.send_photo(message.chat.id, im)
            im.close()
        os.remove('image.png')
    except Exception as e:
        bot.send_message(message.chat.id, 'В промте ошибка. Генерация не возможна')
        logs_save(log_text=str('[Error] ChatGPT generate. code' + str(e)))
        return False
   
@bot.message_handler(commands=['ask'])
def ask_gpt(message):
    try:
        argus = message.text.split()
        if len(argus) < 2:
            bot.send_message(message.chat.id, "Нужно ввести запрос. Попробуй снова.")
            return False
        argus.pop(0)
        txt = " ".join(argus)
        mess = bot.send_message(message.chat.id, "🕐 Подождите несколько секунд. Ваше сообщение обрабатывается")
        mess
        completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": txt}
  ]
)
        logs_save(log_text=str(str("[Info] @" + message.from_user.username) + ' Воспользовался ChatGPT: ' + txt))
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="🕒 Подождите несколько секунд. Ваше сообщение обрабатывается.")
        sleep(0.5)
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="🕕 Подождите несколько секунд. Ваше сообщение обрабатывается..")
        sleep(0.5)
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="🕘 Подождите несколько секунд. Ваше сообщение обрабатывается...")
        sleep(0.5)
        text = ''
        argus = completion.choices[0].message.content.split()
        if len(argus) > Text_limit:
            txt_one = " ".join(argus[:Text_limit])
            txt_two = " ".join(argus[Text_limit:])
            bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text=str("ChatGPT3.5 - " + txt_one))
            bot.send_message(message.chat.id, txt_two)
            return False
        
        for i in range(len(argus)):
            text = text + argus[i] + ' '
            bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text=text)
            sleep(Animspeed)
    except Exception as e:
        logs_save(log_text=str('[Error] ChatGPT ask. code' + str(e)))
        bot.send_message(message.chat.id, 'ChatGPT времмено недоступен! Попробуйте позже.')
#========================================================= 
#Обработка команнд GigaChat
@bot.message_handler(commands=['ask_gigachat'])
def ask_giga_chat(message):
    try:
        argus = message.text.split()
        if len(argus) < 2:
            bot.send_message(message.chat.id, "Нужно ввести запрос. Попробуй снова.")
            return False
        argus.pop(0)
        txt = " ".join(argus)
        mess = bot.send_message(message.chat.id, "🕐 Подождите несколько секунд. Ваше сообщение обрабатывается")
        mess
        with GigaChat(credentials=Gigachat_token, verify_ssl_certs=False) as giga:
            response = giga.chat(txt)
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="🕒 Подождите несколько секунд. Ваше сообщение обрабатывается.")
        sleep(0.5)
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="🕕 Подождите несколько секунд. Ваше сообщение обрабатывается..")
        sleep(0.5)
        bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text="🕘 Подождите несколько секунд. Ваше сообщение обрабатывается...")
        sleep(0.5)
        text = ''
        argus = response.choices[0].message.content.split()
        if len(argus) > Text_limit:
            txt_one = " ".join(argus[:Text_limit])
            txt_two = " ".join(argus[Text_limit:])
            bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text=str("GigaChat - " + txt_one))
            bot.send_message(message.chat.id, txt_two)
            return False
        
        for i in range(len(argus)):
            text = text + argus[i] + ' '
            bot.edit_message_text(chat_id=message.chat.id, message_id=mess.message_id, text=text)
            sleep(Animspeed)
        logs_save(log_text=str(str("[Info] @" + message.from_user.username) + ' Воспользовался GiGaChat: ' + txt))
    except Exception as e:
        logs_save(log_text=str('[Error] GigaChat ask. code' + str(e)))
        bot.send_message(message.chat.id, "GiGaChat времмено недоступен! Попробуйте позже.")

#========================================================= 
#Обработка команнд
@bot.message_handler(commands=['weather'])
def send_weather_person(message):
    weather_data = requests.get(url).json()
    temperature = round(weather_data['main']['temp'])
    humidity = (weather_data['main']['humidity'])
    weathers = (weather_data['weather'][0]['description'])
    text = ("В Питере сейчас: " + str(weathers) + '\nТемпература: ' + str(temperature) + '°C' + '\nВлажность: ' + str(humidity) + '%')
    logs_save(log_text=str('[Info] Выведенна погода пользователю: ' + str(message.from_user.username)))
    bot.send_message(message.chat.id,text)   
#----------------------------------------------------------
@bot.message_handler(commands=['add'])
def appending(message):
    bot.send_message(message.from_user.id, "Отправь данные без нулей через пробелы в формате: Name Day Month. Пример: Виктор 1 5. Если хотите отменить запись введите: Отмена")
    bot.register_next_step_handler(message,save_new)

#==========================================================
#admins commands
@bot.message_handler(commands=['send_message'])
def send_message(message):
    argus = message.text.split()
    if len(argus) < 2:
        bot.send_message(message.from_user.id, 'Напиши текст после комманды')
    else:
        for i in range(len(admins)):
                if str(message.from_user.id) == admins[i]:
                    argus.pop(0)
                    txt = " ".join(argus)
                    logs_save(log_text=str('[Warn] Отправленно сообщение от имени бота:') + txt)
                    bot.send_message(chatid, txt)
                    bot.send_message(message.from_user.id, "Успешно отправленно!")
                else:
                    continue
#----------------------------------------------------------      
@bot.message_handler(commands=['stats'])
def get_stats(message):
    for i in range(len(admins)):
                if str(message.from_user.id) == admins[i]:
                    current_time = datetime.datetime.now()
                    time_work = round(current_time - start_time, 3)
                    bot.send_message(message.from_user.id,"Stats: OK \n Work Time: " + str(time_work))
#----------------------------------------------------------
@bot.message_handler(commands=['logs'])
def get_stats(message):
    for i in range(len(admins)):
                if str(message.from_user.id) == admins[i]:
                    with open('logs.txt', 'r+') as log:
                        bot.send_message(message.from_user.id,str(log.read()))
                    logs_save(logs_text='[Info] Выведены логи пользователю: ' + message.from_user.nickname)
                    log.close
#----------------------------------------------------------
@bot.message_handler(commands=['logsclear'])
def get_stats(message):
    for i in range(len(admins)):
        if str(message.from_user.id) == admins[i]:
            with open('logs.txt', 'w+') as log:
                log.write("\n")
            logs_save(log_text=str("[Warn] Logs clear! \n"))
            bot.send_message(message.from_user.id, "Логи очищенны!")
#----------------------------------------------------------     
#Тестовая функция для разработки
#Для отключения закомментировать!
@bot.message_handler(commands=['test'])
def getmessage(message):    
    if (message.from_user,id == admins[1]):
        bot.send_message(message.from_user.id, message)    
#=========================================================
#Отправка погоды 
def send_weather():
    try:
        #Запись в логи
        logs_save(str(str(NowDate) + '[Info] Выведенна погода'))
        
        #Получение погоды с сайта OpenWeather
        try:
            weather_data = requests.get(url).json()
            temperature = round(weather_data['main']['temp'])
            humidity = (weather_data['main']['humidity'])
            weathers = (weather_data['weather'][0]['description'])
        except Exception as e:
            logs_save(log_text=str('[Error] Weather input. code' + str(e)))
            return False
        #Поменяйте текст под свой!
        text_w = ("Доброе утро, Петербуржцы!" + "\nВ городе сейчас: " + str(weathers) + '\nТемпература: ' + str(temperature) + '°C' + '\nВлажность: ' + str(humidity) + '%')
        
        #Отправка в группу
        bot.send_message(chatid,text_w)
    except Exception as e:
        logs_save(log_text=str("[Error] - Send weather. code" + str(e)))
#==========================================================
#Указание функций комманд
def treager():
    while True:
        schedule.run_pending()
        sleep(1)
#----------------------------------------------------------  
def check():
    try:
        NowDate = datetime.datetime.now()
        NowDay = NowDate.day
        NowMonth = NowDate.month
        
        if int(data[(data['dday'] == NowDay) & (data["dmon"] == NowMonth)].shape[0]) >= 1:
            NowDR = data.index[(data['dday'] == NowDay) & (data["dmon"] == NowMonth)].tolist()
            
        if int(data[(data['dday'] == NowDay) & (data["dmon"] == NowMonth)].shape[0]) <= 0:
            logs_save(log_text='[Info] Имменниников нету!')
            return False
        ind = 0
        for b in range(int(len(NowDR))):
            #Заменить текст на свой!
            text = "Доброго дня! Сегодня день рождения у " + data.loc[NowDR[ind],"nickname"] + ", пожелаем " + data.loc[NowDR[ind],"name"] + " удачи, счастья, отличного настроения и всего наилучшего!\n"
            bot.send_message(chatid,"–=–=–=–=–=–=–=–=–=–=–=–=-=–=\n" + text + "–=–=–=–=–=–=–=–=–=–=–=–=-=–=")
            logs_save(str('[Info] Отправленно поздравление пользователю ' + data.loc[NowDR[ind],"nickname"]))
            ind += 1
            NowDR = []
    except Exception as e:
        logs_save(log_text=str("[Error] Gift message. code:", e))
#----------------------------------------------------------      
def save_new(message):
    if message.text == "Отмена" or message.text == 'отмена':
        bot.send_message(message.from_user.id, "Отменяю")
        return False
    try:
        argus = message.text.split()
        morph = pymorphy2.MorphAnalyzer()
        word_c = morph.parse(argus[0])[0]
        gent = word_c.inflect({'datv'})
        save_text = str((gent.word).title() + "," + "@" +message.from_user.username + "," + argus[1] + "," + argus[2])
        day_range = 0
        month_range = 0
        
        for i in argus[1]:
            day_range += 1
            if i == "0":
                #Заменить текст на свой!
                bot.send_message(message.from_user.id, "Я же сказал без нулей. Попробуй снова.")
                bot.send_message(message.from_user.id, "Отправь данные без нулей через пробелы в формате: Name Nickname Day Month. Пример: Виктор @Test 1 5")
                bot.register_next_step_handler(message,save_new)
                return False
        
        for i in argus[2]:
            month_range += 1
            if i == "0":
                #Заменить текст на свой!
                bot.send_message(message.from_user.id, "Я же сказал без нулей. Попробуй снова.")
                bot.send_message(message.from_user.id, "Отправь данные без нулей через пробелы в формате: Name Nickname Day Month. Пример: Виктор @Test 1 5")
                bot.register_next_step_handler(message,save_new)
                return False
        if day_range > 2 or day_range < 1 or month_range > 2 or day_range < 1 or int(argus[1]) > 31 or int(argus[2]) > 12:
            #Заменить текст на свой!
            bot.send_message(message.from_user.id, "Такой даты не существует. Попробуй снова.")
            bot.send_message(message.from_user.id, "Отправь данные без нулей через пробелы в формате: Name Nickname Day Month. Пример: Виктор @Test 1 5")
            bot.register_next_step_handler(message,save_new)
            return False
        
        with open('NewData.txt', 'a') as f:
            f.write(save_text + '\n')
        #Заменить текст на свой!
        bot.send_message(message.from_user.id, "Ладно-ладно, записал, отстань")
        logs_save(log_text=str('[Info] Записан новый пользователь в базу данных:' + save_text))
        f.close()
    except Exception as e:
        # Заменить текст на свой!
        bot.send_message(message.from_user.id, "У вас что-то не правильно. Попробуйте снова.")
        bot.send_message(message.from_user.id, "Отправь данные без нулей через пробелы в формате: Name Nickname Day Month. Пример: Виктор @Test 1 5")
        bot.register_next_step_handler(message,save_new)
        logs_save(log_text=str('[Error] Add. code:' + e))
        return False
#==========================================================
# Сохранение и вывод логов
def logs_save(log_text=''):
    NowDate = datetime.datetime.now()
    time = NowDate.replace(microsecond=0)
    argus = log_text.split()
    if argus[0] == '[Error]':
        click.echo(click.style(f"{log_text}", fg="red"))
    else:
        if argus[0] == '[Warn]':
            click.echo(click.style(f"{log_text}", fg="yellow"))
        else:
            click.echo(click.style(f"{log_text}", fg="green"))
            
    # print(str(time) + " - " + log_text + '\n')
    bot.send_message(admins[1], str(str(time) + " - " + log_text))
    with open('logs.txt', 'a') as log:
        log.write(str(time) + " - " + log_text + '\n')
    log.close

#==========================================================
#Установка таймеров
schedule.every().day.at(Weather_time).do(send_weather)
schedule.every().day.at(Gift_time).do(check)   

#Установка и запуск потоков
threading_treager = threading.Thread(target=treager)
threading_treager.start()

# Ручное поздравленние
# Раскоментировать стоку ниже, указать сегодняшний день и месяц и перезапутить скрипт
# check(NowDay=15, NowMonth=11)

#==========================================================
#Запуск бота
logs_save(log_text=str('[Info] Bot start'))
try:
    bot.polling(non_stop=True, interval=1)
except Exception as e:
    logs_save(log_text="[Error] Time out. code: " + str(e))
