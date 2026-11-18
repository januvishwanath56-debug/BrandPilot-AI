import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.seed import seed_database


@pytest.fixture
def client():
    testing_engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(testing_engine)
    with Session(testing_engine) as db:
        seed_database(db)

    def override_db():
        with Session(testing_engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        c.headers.update({'X-Demo-Session': 'tests-session-1234',
                          'X-Demo-Role': 'creator', 'X-Demo-Actor': 'Demo Creator'})
        yield c
    app.dependency_overrides.clear()
    testing_engine.dispose()
