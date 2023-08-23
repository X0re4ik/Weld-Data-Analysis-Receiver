import os
from dotenv import load_dotenv

# DOTENV_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".web.env")
# if os.path.exists(DOTENV_PATH):
#     load_dotenv(DOTENV_PATH)
# else:
#     raise FileNotFoundError(f"""
#     Cруктура проекта должна быть следующая:
#         |-<папка web сервиса>
#             |-receiver
#             |-run.py
#         |-.env
    
#     В данном приложении отсутсвует .env файл.
#     env файл содержит основные настройки web-приложения
#     Обязательные аргументы, входящте в env файл:
    
#         #Секретный ключ Flask
#         FLASK_SECRET_KEY            = "..."

#         # Настройки приложения
#         APP_HOST                    = "..."
#         APP_PORT                    = "..."
#         APP_DEBUG                   = "..."

#         # Настройки базы данных
#         DATA_BASE_USERNAME          = "..."
#         DATA_BASE_PASSWORD          = "..."
#         DATA_BASE_HOST              = "..."
#         DATA_BASE_PORT              = "..."
#         DATA_BASE_NAME              = "..."

#         #Прочие настройки
#         PATH_TO_DB_WITH_FILES       = "..."

#     При запуске, приложение искало env в директории:
#         {DOTENV_PATH}
    
#     Текщая директория:
#         {os.path.abspath(__file__)}
# """)

from receiver.configs import RECEIVER_HOST, RECEIVER_PORT, RECEIVER_DEBUG
from receiver import app

if __name__ == '__main__':
    app.run(
        host=RECEIVER_HOST,
        port=RECEIVER_PORT,
        debug=RECEIVER_DEBUG
    )