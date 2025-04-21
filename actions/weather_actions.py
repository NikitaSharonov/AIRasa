import requests
from typing import Text
from rasa_sdk import Action, Tracker
import spacy

nlp = spacy.load("ru_core_news_sm")
API_KEY = "9303b20b05c95a33fed3ef81df34f36f"

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