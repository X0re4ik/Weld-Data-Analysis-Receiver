import os

#Секретный ключ Flask
FLASK_SECRET_KEY                = os.getenv("FLASK_SECRET_KEY")

# Код приемника
RECEIVER_HOST                   = os.getenv("RECEIVER_HOST")
RECEIVER_DEBUG                  = bool(int(os.getenv("RECEIVER_DEBUG")))
RECEIVER_USING_PROTOCOL         = os.getenv("RECEIVER_USING_PROTOCOL")
# Настройка http
RECEIVER_PORT                   = int(os.getenv("RECEIVER_PORT"))
RECEIVER_ACTIVE_LOGIN           = bool(int(os.getenv("RECEIVER_ACTIVE_LOGIN")))
RECEIVER_USERNAME               = os.getenv("RECEIVER_USERNAME")
RECEIVER_PASSWORD               = os.getenv("RECEIVER_PASSWORD")

# url базы данных
DB_URI                          = os.getenv("DB_URI")

#Прочие настройки
PATH_TO_DB_WITH_FILES           = os.getenv("PATH_TO_DB_WITH_FILES")