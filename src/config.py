from pydantic_settings import BaseSettings 
from pydantic import Field


class Config(BaseSettings):
    token: str = Field(..., alias='TELEGRAM_TOKEN')

config = Config()