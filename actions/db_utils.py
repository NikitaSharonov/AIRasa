import random
import spacy
from textblob import TextBlob
from googletrans import Translator
from typing import Text
from rasa_sdk import Action, Tracker

nlp = spacy.load("ru_core_news_sm")
translator = Translator()


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