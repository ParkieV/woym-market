from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    dbuser: str
    dbpassword: str
    dbhost: str
    dbname: str
    dbport: int
    reset_db: bool
    schedule_update: bool
    mode: str

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.dbuser}:{self.dbpassword}@{self.dbhost}:{self.dbport}/{self.dbname}'


config = Config(_env_file='../.env', _env_file_encoding='utf-8')
