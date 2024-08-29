from datetime import tzinfo, timedelta, timezone
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    dbuser: str
    dbpassword: str
    dbhost: str
    dbname: str
    dbport: int
    reset_db: bool
    schedule_update: bool
    mode: str
    yandex_disk_token: str
    yandex_disk_work_dir: str

    @property
    def is_dev(self) -> bool:
        return self.mode == "DEV"

    @property
    def is_prod(self) -> bool:
        return self.mode == "PROD"

    @property
    def is_local(self) -> bool:
        return self.mode == "LOCAL"

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.dbuser}:{self.dbpassword}@{self.dbhost}:{self.dbport}/{self.dbname}'

    @property
    def time_zone_ino(self) -> tzinfo:
        return timezone(timedelta(hours=3))


config = Config(_env_file='.env.local', _env_file_encoding='utf-8')
