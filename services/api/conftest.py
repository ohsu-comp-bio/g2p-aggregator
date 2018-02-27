import pytest
import app as server
server.test()


@pytest.fixture
def app(request):
    # get app from main
    app = server.application
    return app


@pytest.fixture
def client(app):
    # get client from app
    return app.test_client()
