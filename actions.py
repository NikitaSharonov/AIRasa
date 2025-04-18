import re
import random
import datetime
import webbrowser
import requests

import spacy
from textblob import TextBlob
from googletrans import Translator
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

nlp = spacy.load("ru_core_news_sm")
translator = Translator()
API_KEY = "апи_ключ"

def lemmatize_text(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc])

def get_sentiment_reply(text):
    try:
        translated = translator.translate(text, dest='en').text
        polarity = TextBlob(translated).sentiment.polarity
    except Exception:
        polarity = TextBlob(text).sentiment.polarity

    if polarity > 0:
        return random.choice([
            "Ого, ты в хорошем настроении!",
            "Позитивчик ловлю от тебя!",
            "Ты явно на волне позитива!"
        ])
    elif polarity < 0:
        return random.choice([
            "Что-то ты грустный...",
            "Не грусти, всё наладится!",
            "Чувствую негатив... Давай поговорим!"
        ])
    else:
        return random.choice([
            "Нейтрально как-то... расскажи больше!",
            "Ты в спокойном настроении — это тоже круто.",
            "Хмм, звучит довольно ровно."
        ])

class ActionSentimentResponse(Action):
    def name(self) -> Text:
        return "action_sentiment_response"

    def run(self, dispatcher, tracker: Tracker, domain):
        user_input = tracker.latest_message.get("text", "")
        reply = get_sentiment_reply(user_input)
        dispatcher.utter_message(text=reply)
        return []

class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher, tracker: Tracker, domain):
        text = tracker.latest_message.get("text", "")
        city = tracker.get_slot("city")

        if not city:
            # Пробуем найти город через лемматизацию
            doc = nlp(text)
            for token in doc:
                if token.pos_ == "PROPN" or token.ent_type_ == "LOC":
                    city = token.lemma_.capitalize()
                    break

        if not city:
            dispatcher.utter_message(text="Город не найден.")
            return []

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]
            dispatcher.utter_message(text=f"В городе {city} сейчас {weather_desc}, {temp}°C.")
        else:
            dispatcher.utter_message(text="Не удалось получить погоду.")
        return []

class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

    def run(self, dispatcher, tracker, domain):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        dispatcher.utter_message(text=f"Сейчас {now}")
        return []

class ActionGetDate(Action):
    def name(self) -> Text:
        return "action_get_date"

    def run(self, dispatcher, tracker, domain):
        today = datetime.datetime.now().strftime("%d.%m.%Y, %A")
        dispatcher.utter_message(text=f"Сегодня {today}")
        return []

class ActionWebSearch(Action):
    def name(self) -> Text:
        return "action_web_search"

    def run(self, dispatcher, tracker: Tracker, domain):
        query = tracker.get_slot("query")
        user_input = tracker.latest_message.get("text", "")

        if not query:
            # Лемматизация и очистка от служебных слов
            doc = nlp(user_input)
            keywords = [
                token.lemma_ for token in doc
                if token.pos_ not in ("ADP", "CCONJ", "PRON", "SCONJ", "PUNCT", "PART", "DET")
            ]
            query = " ".join(keywords).strip()

        if not query:
            dispatcher.utter_message(text="Что искать?")
            return []

        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        dispatcher.utter_message(text=f"Открываю поиск по запросу: {query}")
        return []

class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher, tracker, domain):
        user_msg = tracker.latest_message.get("text")
        try:
            match = re.search(r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', user_msg)
            if match:
                a, op, b = match.groups()
                a, b = float(a), float(b)
                if op == '+':
                    result = a + b
                elif op == '-':
                    result = a - b
                elif op == '*':
                    result = a * b
                elif op == '/' and b != 0:
                    result = a / b
                else:
                    result = "Ошибка: деление на ноль"
                dispatcher.utter_message(text=f"Результат: {result}")
            else:
                dispatcher.utter_message(text="Не могу вычислить.")
        except:
            dispatcher.utter_message(text="Ошибка при вычислении.")
        return []
