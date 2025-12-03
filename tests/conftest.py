from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel

from nikitabarskov.url_shortener.app import app
from nikitabarskov.url_shortener.db import get_session


@pytest.fixture(scope="session")
def engine(tmp_path_factory: pytest.TempPathFactory) -> Generator[Engine, None, None]:
    engine = create_engine(
        f"sqlite:///{tmp_path_factory.mktemp(basename='pytest').joinpath('pytest.db')}"
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session(engine: Engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
        yield session
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = override_session

    yield TestClient(app)

    app.dependency_overrides.clear()
