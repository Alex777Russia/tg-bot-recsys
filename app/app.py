import telebot
from telebot import types
import pandas as pd
import model_v1_bert
import math
import server

bot = telebot.TeleBot('6367567016:AAGH3495UxQO4kTYIASfFcsEbWDiCjk-w6Q')

path_to_rubrics_file = "rubric_to_vector_windows.csv"
path_to_organizations_file = "organizations_with_coordinates.csv"

rubrics = model_v1_bert.prepare_data(path_to_rubrics_file)
db = model_v1_bert.load_organisations(path_to_organizations_file)
len_rubrics = len(rubrics)

####
# EXTREAME!!
server.create_db()

####

my_coords = [55.766667939589304, 37.68488226285589] # КООРДИНАТЫ МГТУ ГЗ

@bot.message_handler(commands = ['start'])
def main(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, введи свой запрос')

@bot.message_handler(commands=["geo"])
def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Привет! Нажми на кнопку и передай мне свое местоположение", reply_markup=keyboard)

@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        print(message.location)
        print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))
        # bot.send_message(message.chat.id, f'latitude: {message.location.latitude}, longitude: {message.location.longitude}')

        my_coords[0] = message.location.latitude
        my_coords[1] = message.location.longitude

@bot.message_handler(commands = ['site', 'website'])
def site(message):
    # webbrowser.open('https://github.com/Alex777Russia')
    bot.send_message(message.chat.id, 'https://github.com/Alex777Russia')

@bot.message_handler()
def info(message):

    server.insert_message(message.from_user.id, message.from_user.first_name, message.chat.id, message.text, message.date)
    print(message)
    
    vector_text = model_v1_bert.embed_bert_cls(message.text)
    
    r1, r2, r3 = model_v1_bert.rubric_to_vector(vector_text, rubrics, len_rubrics)
    
    data = db[db.rubrics.str.contains('|'.join([r1, r2]))] # data = db[db.rubrics.str.contains('|'.join([r1, r2, r3]))]

    print(f"DEBUG:\nМои координаты: {my_coords[0]}, {my_coords[1]}")

    data = calculate_distance(data, my_coords)

    data = calculate_reccomendation(data)

    dist = calculate_distance_meters(data, my_coords, 3)

    ans_1, ans_2, ans_3 = answer_for_user(data, dist, 0)

    bot.send_message(message.chat.id, ans_1)
    bot.send_message(message.chat.id, ans_2)
    bot.send_message(message.chat.id, ans_3)

    print(f"DEBUG:\n{r1},\n{r2},\n{r3}")

def calculate_reccomendation(dataFrame):
    result_with_distance = (dataFrame.mean_rating * dataFrame.count_reviews ** 1.1) / dataFrame.count_reviews * (10 / dataFrame.distance)
    dataFrame['sort_value'] = result_with_distance
    dataFrame = dataFrame.sort_values(by=['sort_value'], ascending=False)
    return dataFrame

def calculate_distance(dataFrame, my_coords):
    distance = []
    for i in range(len(dataFrame)):
        distance.append(math.sqrt((my_coords[0] - float(dataFrame.iloc[i].coordinates.split(' ')[0])) ** 2 + \
                                  (my_coords[1] - float(dataFrame.iloc[i].coordinates.split(' ')[1])) ** 2))
    dataFrame['distance'] = distance
    return dataFrame

def calculate_distance_meters(dataFrame, my_coords, count):
    R = 6371  # средний радиус Земли в км
    dist = []
    for i in range(count):
        row = dataFrame.iloc[i].coordinates.split(' ')
        d_lat = math.radians(float(row[0]) - my_coords[0])
        d_lon = math.radians(float(row[1]) - my_coords[1])

        rad = math.sin(d_lat / 2) * math.sin(d_lat / 2) + \
            math.cos(math.radians(my_coords[0])) * math.cos(math.radians(float(row[0]))) * \
            math.sin(d_lon / 2) * math.sin(d_lon / 2)

        c = 2 * math.atan2(math.sqrt(rad), math.sqrt(1 - rad))
        dist.append(R * c * 1000)

    return dist

def answer_for_user(dataFrame, distination, i):
    ans_1 = convert_to_str(dataFrame.iloc[i], distination, i)
    ans_2 = convert_to_str(dataFrame.iloc[i+1], distination, i+1)
    ans_3 = convert_to_str(dataFrame.iloc[i+2], distination, i+2)
    return ans_1, ans_2, ans_3

def convert_to_str(ans, distination, i):
    string = ("адрес: " + str(ans.adress) + "\n\n" + \
    "название: " + str(ans.name_ru) + "\n\n" + \
    "категория: " + "\n" + ("\n".join(ans.rubrics.split(";"))) + "\n\n" + \
    "кол-во отзывов: " + str(ans.count_reviews) + "\n\n" + \
    "средняя оценка: " + str(ans.mean_rating) + "\n\n" + \
    "расстояние до места: " + str(round(distination[i], 2)) + "м")
    return string

bot.polling(none_stop=True)