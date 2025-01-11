import os
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Получаем данные из запроса
        json_str = request.get_data().decode('UTF-8')
        # Тут нужно обработать данные и выполнить нужные действия с сообщениями
        print(json_str)  # Для отладки, выводим полученные данные
        return 'OK'

if __name__ == '__main__':
    # Получаем порт из окружения или используем 5000 по умолчанию
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
