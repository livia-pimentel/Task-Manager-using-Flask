import pytest
from todo_project import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilitar CSRF para testes

    with app.app_context():  # Garantir que o contexto da aplicação seja criado
        db.create_all()
        client = app.test_client()
        yield client
        db.drop_all()

def test_functional_workflow(client):
    """Teste funcional simples para registro, login e criação de tarefa"""

    # 1. Registrar um novo usuário
    response = client.post('/register', data={
        'username': 'functionaluser',
        'password': 'Func@1234',
        'confirm_password': 'Func@1234'
    }, follow_redirects=True)
    assert response.status_code == 200  # Verifica se a resposta foi bem-sucedida

    # 2. Fazer login com o usuário registrado
    response = client.post('/login', data={
        'username': 'functionaluser',
        'password': 'Func@1234'
    }, follow_redirects=True)
    assert response.status_code == 200  # Verifica se a resposta foi bem-sucedida
    assert b'All Tasks' in response.data  # Verifica se o login foi bem-sucedido

    # 3. Adicionar uma tarefa
    response = client.post('/add_task', data={
        'task_name': 'Comprar leite'
    }, follow_redirects=True)
    assert response.status_code == 200  # Verifica se a resposta foi bem-sucedida

    # 4. Verificar se a tarefa aparece na lista de tarefas
    response = client.get('/all_tasks', follow_redirects=True)  # Seguir redirecionamentos
    assert response.status_code == 200
