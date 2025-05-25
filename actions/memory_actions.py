import sqlite3
import json
from datetime import datetime, timedelta
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

DB_PATH = "memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_memory (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        favorite_topic TEXT,
        last_seen TEXT,
        extra TEXT
    );
    """)
    conn.commit()
    conn.close()

class ActionLoadUserMemory(Action):
    def name(self):
        return "action_load_user_memory"

    def run(self, dispatcher, tracker: Tracker, domain):
        init_db()
        user_id = tracker.sender_id

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, favorite_topic FROM user_memory WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        events = []
        if row:
            name, topic = row
            if name:
                dispatcher.utter_message(text=f"Привет, {name}! Как я могу помочь?")
                events.append(SlotSet("name", name))
            else:
                dispatcher.utter_message(text="Привет! Как тебя зовут?")
            events.append(SlotSet("favorite_topic", topic))
        else:
            dispatcher.utter_message(text="Привет! Как тебя зовут?")
        return events

class ActionSaveUserMemory(Action):
    def name(self):
        return "action_save_user_memory"

    def run(self, dispatcher, tracker: Tracker, domain):
        init_db()
        user_id = tracker.sender_id
        name = tracker.get_slot("name")
        topic = tracker.get_slot("favorite_topic")
        extra_data = {}  # можно добавить дополнительные данные позже

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_memory(user_id, name, favorite_topic, last_seen, extra)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
              name=excluded.name,
              favorite_topic=excluded.favorite_topic,
              extra=excluded.extra;
        """, (user_id, name, topic, None, json.dumps(extra_data)))
        conn.commit()
        conn.close()

        dispatcher.utter_message(text=f"Хорошо, {name}, я тебя запомнил.")
        return []

class ActionSetLastSeen(Action):
    def name(self):
        return "action_set_last_seen"

    def run(self, dispatcher, tracker: Tracker, domain):
        init_db()
        user_id = tracker.sender_id
        now = (datetime.utcnow() + timedelta(hours=3)).isoformat()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE user_memory SET last_seen = ? WHERE user_id = ?", (now, user_id))
        conn.commit()
        conn.close()

        dispatcher.utter_message(text="До встречи!")
        return []

class ActionTellLastSeen(Action):
    def name(self):
        return "action_tell_last_seen"

    def run(self, dispatcher, tracker: Tracker, domain):
        init_db()
        user_id = tracker.sender_id

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT last_seen FROM user_memory WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row and row[0]:
            dt = datetime.fromisoformat(row[0])
            dispatcher.utter_message(text=f"Мы последний раз общались {dt.strftime('%d.%m.%Y в %H:%M')}.")
        else:
            dispatcher.utter_message(text="У меня нет информации о времени последнего взаимодействия.")
        return []
