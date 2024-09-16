import pytest
from todo_project import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.drop_all()

def test_register_and_login(client):
    """Teste simples para registro e login do usuário"""

    # 1. Registrar um novo usuário
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'Test@1234',
        'confirm_password': 'Test@1234'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Verifica se redireciona para a página de login

    # 2. Fazer login com o usuário registrado
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'Test@1234'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'All Tasks' in response.data  # Verifica se redireciona para a página de tarefas
