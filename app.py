import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World!"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Используем переменную окружения PORT
    app.run(host='0.0.0.0', port=port)   # Привязываем к порту
