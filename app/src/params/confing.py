from os import getenv

# TODO Поменять на from pydantic_settings import BaseSettings

DBUSER = getenv('DBUSER', 'admin123')
DBPASSWORD = getenv('DBPASSWORD', 'p0ssw0rd')
DBHOST = getenv('DBHOST', 'localhost')
DBNAME = getenv('DBNAME', 'postgres')
DBPORT = getenv('DBPORT', '5432')
RESET_DB = getenv('RESET_DB', 'False')
SCHEDULE_UPDATE = getenv('SCHEDULE_UPDATE', 'False')
YANDEX_MARKET_TOKEN = getenv('YANDEX_MARKET_TOKEN', 'y0_AgAAAAAW8Hr_AAsIRgAAAAD1j7NA7uQ9YJbpR-elaniG1o-TiKxVJhU')

