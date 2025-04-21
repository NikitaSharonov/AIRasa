import re
import webbrowser
import spacy
from typing import Text
from rasa_sdk import Action, Tracker

nlp = spacy.load("ru_core_news_sm")

class ActionWebSearch(Action):
    def name(self) -> Text:
        return "action_web_search"

    def run(self, dispatcher, tracker: Tracker, domain):
        user_input = tracker.latest_message.get("text", "").lower()
        # Находим ключевое слово и вырезаем всё после него
        pattern = r"(поищи|найди|гугли)\s+(.+)"
        match = re.search(pattern, user_input)
        if match:
            query = match.group(2).strip()
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            dispatcher.utter_message(text=f"Открываю поиск по запросу: {query}")
        else:
            dispatcher.utter_message(text="Не понял, что искать.")
        return []