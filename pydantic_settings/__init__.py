import os
from pydantic import BaseModel

class BaseSettings(BaseModel):
    def __init__(self, **kwargs):
        annotations = getattr(self.__class__, "__annotations__", {})
        for name in annotations:
            env_name = name.upper()
            value = kwargs.get(name, os.getenv(env_name, getattr(self.__class__, name, None)))
            setattr(self, name, value)
