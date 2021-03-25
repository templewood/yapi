import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = ""
    class Config:
        env_file = ".env"

app_dir = os.path.dirname(os.path.abspath(__file__))
settings = Settings(_env_file=str(app_dir) + '/.env')
