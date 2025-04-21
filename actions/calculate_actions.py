import re
from typing import Text
from rasa_sdk import Action, Tracker

class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher, tracker: Tracker, domain):
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