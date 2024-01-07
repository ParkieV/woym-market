from pydantic_settings import BaseSettings

# DBUSER = getenv('DBUSER', 'admin123')
# DBPASSWORD = getenv('DBPASSWORD', 'p0ssw0rd')
# DBHOST = getenv('DBHOST', 'db')
# DBNAME = getenv('DBNAME', 'postgres')
# DBPORT = getenv('DBPORT', '5432')
# RESET_DB = getenv('RESET_DB', 'False')
# SCHEDULE_UPDATE = getenv('SCHEDULE_UPDATE', 'False')
# YANDEX_MARKET_TOKEN = getenv('YANDEX_MARKET_TOKEN', 'y0_AgAAAAAW8Hr_AAsIRgAAAAD1j7NA7uQ9YJbpR-elaniG1o-TiKxVJhU')


class Config(BaseSettings):
    dbuser: str = 'admin123'
    dbpassword: str = 'p0ssw0rd'
    dbhost: str = 'db'
    dbname: str = 'postgres'
    dbport: int = 5432
    reset_db: bool = False
    schedule_update: bool = False
    yandex_token: str = 'y0_AgAAAAAW8Hr_AAsIRgAAAAD1j7NA7uQ9YJbpR-elaniG1o-TiKxVJhU'


config = Config(_env_file='.env', _env_file_encoding='utf-8')
