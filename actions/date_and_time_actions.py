import datetime
from typing import Text
from rasa_sdk import Action

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
        day_names = {
            "Monday": "Понедельник",
            "Tuesday": "Вторник",
            "Wednesday": "Среда",
            "Thursday": "Четверг",
            "Friday": "Пятница",
            "Saturday": "Суббота",
            "Sunday": "Воскресенье"
        }
        now = datetime.datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        weekday_eng = now.strftime("%A")
        weekday_ru = day_names.get(weekday_eng, weekday_eng)
        dispatcher.utter_message(text=f"Сегодня {date_str}, {weekday_ru}")
        return []

