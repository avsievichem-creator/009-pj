import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open
from priv import find_all_readme_files, search_user_in_files, create_new_readme, process_user

class TestFindAllReadmeFiles:
    """Тесты для функции find_all_readme_files"""
    
    def test_find_readme_files(self, tmpdir):
        # Создаем временные файлы
        with tmpdir.as_cwd():
            # Создаем тестовые файлы
            open("README.md", "w").close()
            open("README_test.md", "w").close()
            open("readme.md", "w").close()  # не должен быть найден (регистр)
            open("OTHER_FILE.txt", "w").close()
            
            result = find_all_readme_files()
            assert len(result) == 2
            assert "README.md" in result
            assert "README_test.md" in result

    def test_no_readme_files(self, tmpdir):
        # Тест когда нет README файлов
        with tmpdir.as_cwd():
            result = find_all_readme_files()
            assert result == []

class TestSearchUserInFiles:
    """Тесты для функции search_user_in_files"""
    
    def test_user_found(self, tmpdir):
        with tmpdir.as_cwd():
            # Создаем файл с содержимым
            with open("test_file.md", "w", encoding="utf-8") as f:
                f.write("Иванов Иван Иванович\nДругие данные")
            
            result = search_user_in_files("Иванов Иван Иванович", ["test_file.md"])
            assert result is True

    def test_user_not_found(self, tmpdir):
        with tmpdir.as_cwd():
            with open("test_file.md", "w", encoding="utf-8") as f:
                f.write("Петров Петр Петрович\nДругие данные")
            
            result = search_user_in_files("Иванов Иван Иванович", ["test_file.md"])
            assert result is False

    def test_multiple_files(self, tmpdir):
        with tmpdir.as_cwd():
            # Создаем несколько файлов
            with open("file1.md", "w", encoding="utf-8") as f:
                f.write("Петров Петр Петрович")
            with open("file2.md", "w", encoding="utf-8") as f:
                f.write("Иванов Иван Иванович")
            
            result = search_user_in_files("Иванов Иван Иванович", ["file1.md", "file2.md"])
            assert result is True

    def test_file_not_found(self):
        # Тест с несуществующим файлом
        result = search_user_in_files("Иванов Иван Иванович", ["nonexistent_file.md"])
        assert result is False

class TestCreateNewReadme:
    """Тесты для функции create_new_readme"""
    
    @patch('builtins.input', side_effect=[
        '3', 'Группа-101', 'Программист', '09.02.07', 
        'Производственная практика', 'Команда-5'
    ])
    def test_create_readme_file(self, mock_input, tmpdir):
        with tmpdir.as_cwd():
            fio = "Иванов Иван Иванович"
            filename = "README_Иванов_Иван_Иванович.md"
            
            create_new_readme(fio, filename)
            
            # Проверяем что файл создан
            assert os.path.exists(filename)
            
            # Проверяем содержимое файла
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                assert f"ФИО: {fio}" in content
                assert "Курс: 3" in content
                assert "Группа: Группа-101" in content

class TestProcessUser:
    """Тесты для функции process_user"""
    
    @patch('builtins.input', side_effect=['выход'])
    def test_exit_condition(self, mock_input):
        result = process_user()
        assert result is False

    @patch('builtins.input', side_effect=['Иванов Иван Иванович'])
    @patch('main.search_user_in_files', return_value=True)
    def test_user_exists(self, mock_search, mock_input, capsys):
        result = process_user()
        captured = capsys.readouterr()
        assert "Ты уже есть в одном из профилей" in captured.out
        assert result is True

    @patch('builtins.input', side_effect=[
        'Иванов Иван Иванович',  # ФИО
        '3', 'Группа-101', 'Программист', '09.02.07', 
        'Производственная практика', 'Команда-5'  # дополнительные данные
    ])
    @patch('main.search_user_in_files', return_value=False)
    @patch('main.find_all_readme_files', return_value=[])
    def test_create_new_user(self, mock_find, mock_search, mock_input, tmpdir, capsys):
        with tmpdir.as_cwd():
            result = process_user()
            captured = capsys.readouterr()
            
            assert result is True
            assert "Твой профиль создан" in captured.out
            assert os.path.exists("README_Иванов_Иван_Иванович.md")

# Интеграционные тесты
class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_flow(self, tmpdir, capsys):
        with tmpdir.as_cwd():
            # Мокаем ввод пользователя
            with patch('builtins.input', side_effect=[
                'Иванов Иван Иванович',  # ФИО
                '3', 'Группа-101', 'Программист', '09.02.07', 
                'Производственная практика', 'Команда-5',  # данные
                'выход'  # выход
            ]):
                # Мокаем основную функцию чтобы не запускать бесконечный цикл
                with patch('main.main') as mock_main:
                    # Импортируем и запускаем
                    import priv
                    if __name__ == "__main__":
                        priv.main()
            
            # Проверяем что файл создан
            assert os.path.exists("README_Иванов_Иван_Иванович.md")
            
            # Проверяем содержимое
            with open("README_Иванов_Иван_Иванович.md", 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Иванов Иван Иванович" in content
                assert "Курс: 3" in content