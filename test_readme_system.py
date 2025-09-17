import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import glob
import tempfile
import shutil

# Импортируем функции из основного кода
def find_all_readme_files():
    """Находит все README файлы в текущей папке"""
    readme_files = glob.glob("README*.md")
    return readme_files

def search_user_in_files(fio, files):
    """Ищет пользователя во всех README файлах"""
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                if fio in content:
                    return True
        except:
            continue
    return False

def create_new_readme(fio, filename):
    """Создает новый README файл с данными пользователя"""
    print(f"👋 Привет, {fio}! Давай заполним твои данные...")
    
    course = input("Введи свой курс: ")
    group = input("Введи свою группу: ")
    specialty = input("Введи специальность: ")
    specialty_code = input("Введи код специальности: ")
    practice = input("Введи название практики: ")
    team = input("Введи номер команды: ")
    
    content = f"""# Профиль студента

## Основная информация
- ФИО: {fio}
- Курс: {course}
- Группа: {group}
- Специальность: {specialty}
- Код специальности: {specialty_code}
- Практика: {practice}
- Команда: {team}

"""
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"✅ Файл {filename} успешно создан!")

def process_user():
    """Обрабатывает одного пользователя"""
    print("\n" + "="*40)
    print("🌟 Проверка профиля")
    print("="*40)
    
    fio = input("Введи свое ФИО (или 'выход' для завершения): ").strip()
    
    if fio.lower() in ['выход', 'exit', 'quit', '']:
        return False
    
    all_readme_files = find_all_readme_files()
    user_exists = search_user_in_files(fio, all_readme_files)
    
    if user_exists:
        print(f"✅ Привет, {fio}! Ты уже есть в одном из профилей.")
    else:
        filename = f"README_{fio.replace(' ', '_')}.md"
        create_new_readme(fio, filename)
        print(f"🎉 Готово, {fio}! Твой профиль создан.")
    
    return True

def main():
    """Главная функция программы"""
    print("Добро пожаловать в систему управления профилями!")
    print("Для выхода введите 'выход'")
    
    while True:
        try:
            if not process_user():
                break
        except KeyboardInterrupt:
            print("\n\nПрограмма завершена пользователем.")
            break
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            continue
    
    print("\nСпасибо за использование программы! До свидания! 👋")

class TestReadmeSystem(unittest.TestCase):

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        self.test_files = []

    def tearDown(self):
        """Очистка после каждого теста"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def create_test_file(self, filename, content):
        """Создает тестовый файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        self.test_files.append(filename)

    def test_1_find_all_readme_files_empty(self):
        """Тест 1: Поиск README файлов в пустой директории"""
        result = find_all_readme_files()
        self.assertEqual(result, [])

    def test_2_find_all_readme_files_with_files(self):
        """Тест 2: Поиск README файлов с существующими файлами"""
        self.create_test_file("README.md", "# Test")
        self.create_test_file("README_test.md", "# Test")
        self.create_test_file("not_readme.txt", "test")
        
        result = find_all_readme_files()
        self.assertEqual(len(result), 2)
        self.assertIn("README.md", result)
        self.assertIn("README_test.md", result)

    def test_3_search_user_in_files_found(self):
        """Тест 3: Поиск пользователя (найден)"""
        self.create_test_file("test.md", "Иванов Иван Иванович\nКурс: 3")
        
        result = search_user_in_files("Иванов Иван Иванович", ["test.md"])
        self.assertTrue(result)

    def test_4_search_user_in_files_not_found(self):
        """Тест 4: Поиск пользователя (не найден)"""
        self.create_test_file("test.md", "Петров Петр Петрович\nКурс: 2")
        
        result = search_user_in_files("Иванов Иван Иванович", ["test.md"])
        self.assertFalse(result)

    def test_5_search_user_in_files_multiple_files(self):
        """Тест 5: Поиск пользователя в нескольких файлах"""
        self.create_test_file("file1.md", "Петров Петр Петрович")
        self.create_test_file("file2.md", "Иванов Иван Иванович")
        
        result = search_user_in_files("Иванов Иван Иванович", ["file1.md", "file2.md"])
        self.assertTrue(result)

    def test_6_search_user_in_files_nonexistent_file(self):
        """Тест 6: Поиск пользователя в несуществующем файле"""
        result = search_user_in_files("Иванов Иван Иванович", ["nonexistent.md"])
        self.assertFalse(result)

    @patch('builtins.input')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_7_create_new_readme(self, mock_print, mock_file, mock_input):
        """Тест 7: Создание нового README файла"""
        mock_input.side_effect = ['3', 'ИСП-301', 'Программирование', '09.02.07', 'Веб-разработка', '5']
        
        create_new_readme('Иванов Иван Иванович', 'README_test.md')
        
        mock_file.assert_called_once_with('README_test.md', 'w', encoding='utf-8')
        mock_print.assert_any_call("👋 Привет, Иванов Иван Иванович! Давай заполним твои данные...")
        mock_print.assert_any_call("✅ Файл README_test.md успешно создан!")

    @patch('builtins.input')
    @patch('builtins.open', new_callable=mock_open)
    def test_8_create_new_readme_content(self, mock_file, mock_input):
        """Тест 8: Проверка содержимого создаваемого файла"""
        mock_input.side_effect = ['3', 'ИСП-301', 'Программирование', '09.02.07', 'Веб-разработка', '5']
        
        create_new_readme('Иванов Иван Иванович', 'README_test.md')
        
        handle = mock_file()
        expected_content = """# Профиль студента

## Основная информация
- ФИО: Иванов Иван Иванович
- Курс: 3
- Группа: ИСП-301
- Специальность: Программирование
- Код специальности: 09.02.07
- Практика: Веб-разработка
- Команда: 5

"""
        handle.write.assert_called_once_with(expected_content)

    @patch('builtins.input', return_value='выход')
    @patch('builtins.print')
    def test_9_process_user_exit(self, mock_print, mock_input):
        """Тест 9: Выход из process_user"""
        result = process_user()
        self.assertFalse(result)
        mock_print.assert_called_with("="*40)

    @patch('builtins.input')
    @patch('builtins.print')
    @patch(__name__ + '.find_all_readme_files')
    @patch(__name__ + '.search_user_in_files')
    def test_10_process_user_existing(self, mock_search, mock_find, mock_print, mock_input):
        """Тест 10: Обработка существующего пользователя"""
        mock_input.return_value = 'Иванов Иван Иванович'
        mock_find.return_value = ['README.md']
        mock_search.return_value = True
        
        result = process_user()
        self.assertTrue(result)
        mock_print.assert_any_call("✅ Привет, Иванов Иван Иванович! Ты уже есть в одном из профилей.")

    @patch('builtins.input')
    @patch('builtins.print')
    @patch(__name__ + '.find_all_readme_files')
    @patch(__name__ + '.search_user_in_files')
    @patch(__name__ + '.create_new_readme')
    def test_11_process_user_new(self, mock_create, mock_search, mock_find, mock_print, mock_input):
        """Тест 11: Обработка нового пользователя"""
        mock_input.return_value = 'Петров Петр Петрович'
        mock_find.return_value = ['README.md']
        mock_search.return_value = False
        
        result = process_user()
        self.assertTrue(result)
        mock_create.assert_called_once_with('Петров Петр Петрович', 'README_Петров_Петр_Петрович.md')
        mock_print.assert_any_call("🎉 Готово, Петров Петр Петрович! Твой профиль создан.")

    @patch('builtins.input', side_effect=['Иванов', 'выход'])
    @patch('builtins.print')
    @patch(__name__ + '.process_user')
    def test_12_main_functionality(self, mock_process, mock_print, mock_input):
        """Тест 12: Основная функциональность main"""
        mock_process.side_effect = [True, False]
        
        # Тестируем main функцию напрямую
        with patch('builtins.input', side_effect=['выход']):
            with patch(__name__ + '.process_user', return_value=False):
                main()
        
        mock_print.assert_any_call("Добро пожаловать в систему управления профилями!")

def run_tests():
    """Запуск всех тестов"""
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestReadmeSystem)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    print(f"\n{'='*50}")
    print(f"Результаты тестирования:")
    print(f"Пройдено тестов: {result.testsRun - len(result.failures) - len(result.errors)}/{result.testsRun}")
    print(f"Ошибки: {len(result.errors)}")
    print(f"Провалы: {len(result.failures)}")
    print(f"{'='*50}")
    
    if result.wasSuccessful():
        print("🎉 Все 12 тестов прошли успешно!")
        return True
    else:
        print("❌ Некоторые тесты не прошли")
        return False

if __name__ == '__main__':
    print("Запуск комплексного тестирования системы README...")
    success = run_tests()
    
    if success:
        print("\n✅ Тестирование завершено успешно! Код готов к использованию.")
    else:
        print("\n❌ Требуется отладка кода.")