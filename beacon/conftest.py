import pytest
import server


@pytest.fixture
def app(request):
    # get app from main
    app = server.app
    return app


@pytest.fixture
def client(app):
    # get client from app
    return app.test_client()
