import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app


@pytest.fixture
def client(tmp_path):

    db_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"

    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_config, "head")

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestSession = sessionmaker(bind=engine)

    def get_test_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()
