import openai
import sqlite3
import environs
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher

env = environs.Env()
env.read_env('.env')

openai.api_key = env('OPENAI_TOKEN')

conn = sqlite3.connect('mygpt.db.sqlite3')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mygpt (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_user TEXT,
        message_chatgpt TEXT
    )
''')
print('[INFO] Create database')
conn.commit()

bot = Bot(env('TELETOKEN'))
dp = Dispatcher(bot)

messages = [
    {'role': 'system', 'content': 'You are a programmer and your job is to help you learn how to program and help you write code.'},
    {'role': 'user', 'content': 'I am a beginner programmer and I need your help in learning programming and writing code'},
    {'role': 'assistant', 'content': 'Greetings! How can I help?'},
]


def update_list_messages(messages, role, content):
    messages.append({'role': role, 'content': content})
    return messages


@dp.message_handler()
async def chat(message: types.Message):
    update_list_messages(messages, 'user', message.text)
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages 
    )
    try:
        bot_response = response['choices'][0]['message']['content']
        await message.answer(bot_response)
        cursor.execute('''
            INSERT INTO mygpt (message_user, message_chatgpt) 
            VALUES (?, ?)
            ''', (message.text, bot_response)
        )
        conn.commit()
    except Exception as ex:
        cursor.close()
        conn.close()
        print('[INFO] Database closed connection')
        await message.answer(ex)


executor.start_polling(dp, skip_updates=True)
