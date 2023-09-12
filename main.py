import openai
import sqlite3
import environs

env = environs.Env()
env.read_env('.env')

openai.api_key = env('OPENAI_TOKEN')

conn = sqlite3.connect('db.sqlite3.mygpt')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mygpt (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_user TEXT,
        message_chatgpt TEXT
    )
''')
print('База данных создана')
conn.commit()


def close_db():
    cursor.close()
    conn.close()
    print('Соединение с базой данных закрыто')


messages = [
    {'role': 'system', 'content': 'You are a programmer and your job is to help you learn how to program and help you write code.'},
    {'role': 'user', 'content': 'I am a beginner programmer and I need your help in learning programming and writing code'},
    {'role': 'assistant', 'content': 'Greetings! How can I help?'},
]


def update_list_messages(messages, role, content):
    messages.append({'role': role, 'content': content})
    return messages


while True:
    try:
        message_user = input('Введите сообщение: ')
        if message_user.lower() == 'выход':
            close_db()
            break
        update_list_messages(messages, 'user', message_user)
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
        )
        message_chatgpt = response['choices'][0]['message']['content']
        print(f'GPT: {message_chatgpt}')
        cursor.execute('''
            INSERT INTO mygpt (message_user, message_chatgpt) 
            VALUES (?, ?)
            ''', (message_user, message_chatgpt)
        )
        conn.commit()
    except:
        close_db()
