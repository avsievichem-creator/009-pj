import pytest
import tempfile
import os

@pytest.fixture
def setup_test_environment():
    """Настройка тестовой среды"""
    # Создаем временную директорию для тестов
    test_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(test_dir)
    
    yield test_dir  # это то, что будет передано в тест
    
    # Очистка после теста
    os.chdir(original_dir)
    import shutil
    shutil.rmtree(test_dir)