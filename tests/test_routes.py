import pytest
from todo_project import app, db, bcrypt
from todo_project.models import User, Task

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.drop_all()

### Testando rotas principais

def test_about_page(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About' in response.data

def test_home_page(client):
    """Teste simples para verificar se a página inicial carrega corretamente."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'About' in response.data  # Verifica se o texto 'About' está na página

def test_login_page(client):
    """Teste para verificar se a página de login carrega corretamente."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_page(client):
    """Teste para verificar se a página de registro carrega corretamente."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_all_tasks_page_redirects_when_not_logged_in(client):
    """Teste para verificar se a página de 'all_tasks' redireciona quando o usuário não está logado."""
    response = client.get('/all_tasks', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in' in response.data  # Verifica se há uma mensagem de login na página