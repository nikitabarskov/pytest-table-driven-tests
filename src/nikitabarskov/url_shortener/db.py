from datetime import datetime
from typing import Generator

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import Field, Session, SQLModel, create_engine


def get_engine() -> Engine:
    return create_engine("sqlite:///main.db")


def get_session(engine: Engine = Depends(get_engine)) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init(engine: Engine = Depends(get_engine)) -> None:
    SQLModel.metadata.create_all(engine)


class ShortenedURL(SQLModel, table=True):
    code: str = Field(primary_key=True)
    original_url: str
    created_at: datetime
