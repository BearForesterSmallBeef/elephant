from flask import Flask, request
import logging
import os

import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sessionStorage = {}
word = 'слона'


@app.route('/')
def index():
    return 'Hello, world!'


@app.route('/post', methods=['POST'])
def main_1():
    from main import word
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return json.dumps(response)


def handle_dialog(req, res):
    from main import word
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {word}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'я покупаю',
        'я куплю'
    ]:
        res['response']['text'] = f'{word.capitalize()} можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = False
        global word
        word = 'кролика'
        return

    res['response']['text'] = f'Все говорят "%s", а ты купи {word}!' % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    from main import word
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={word[:-1]}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

