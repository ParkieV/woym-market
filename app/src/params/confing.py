from pydantic_settings import BaseSettings


class Config(BaseSettings):
    dbuser: str
    dbpassword: str
    dbhost: str
    dbname: str
    dbport: int
    reset_db: bool
    schedule_update: bool
    yandex_token: str


config = Config(_env_file='.env', _env_file_encoding='utf-8')
