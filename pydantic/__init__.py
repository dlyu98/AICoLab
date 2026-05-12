from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime
from typing import Any


def Field(default=None, default_factory=None):
    if default_factory is not None:
        return field(default_factory=default_factory)
    return field(default=default)


def _convert(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_convert(v) for v in value]
    if isinstance(value, dict):
        return {k: _convert(v) for k, v in value.items()}
    return value

class BaseModel:
    def __init_subclass__(cls):
        dataclass(cls, kw_only=True)
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def model_dump(self) -> dict[str, Any]:
        if is_dataclass(self):
            return {f.name: _convert(getattr(self, f.name)) for f in fields(self)}
        return {k: _convert(v) for k, v in self.__dict__.items()}
    def dict(self):
        return self.model_dump()
