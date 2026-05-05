import re

from sqlalchemy.orm import DeclarativeBase, declared_attr

_CAMEL_TO_SNAKE = re.compile(r"(?<!^)(?=[A-Z])")


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return _CAMEL_TO_SNAKE.sub("_", cls.__name__).lower()
