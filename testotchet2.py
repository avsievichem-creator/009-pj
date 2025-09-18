# Импортируем необходимые библиотеки
import subprocess  # Для запуска внешних команд (как командная строка)
import sys         # Для работы с системными параметрами Python
import re          # Для поиска текста по шаблонам (регулярные выражения)
from datetime import datetime  # Для работы с датой и временем
from typing import Dict, List, Any  # Для подсказок типов (необязательно, но полезно)


class TestReportGenerator:
    """Класс для генерации отчетов о тестировании"""
    
    def __init__(self):
        """Конструктор - создает структуру для хранения результатов"""
        # Словарь для хранения всех результатов тестирования
        self.results = {
            'total_tests': 0,      # Общее количество тестов
            'passed': 0,           # Количество успешных тестов
            'failed': 0,           # Количество проваленных тестов
            'skipped': 0,          # Количество пропущенных тестов
            'success_rate': 0.0,   # Процент успешных тестов (0.0 - 100.0)
            'test_details': [],    # Список с детальной информацией о каждом тесте
            'timestamp': datetime.now().isoformat(),  # Время запуска в формате ISO
            'python_version': sys.version  # Информация о версии Python
        }

    def run_tests(self) -> bool:
        """Запускает тесты и возвращает True если все прошли успешно"""
        try:
            # Список возможных команд для запуска pytest
            # Пробуем разные варианты, так как pytest может быть установлен по-разному
            pytest_commands = [
                [sys.executable, '-m', 'pytest', 'test_main.py', '-v'],  # 1. python -m pytest
                ['pytest', 'test_main.py', '-v'],                        # 2. просто pytest
                ['python', '-m', 'pytest', 'test_main.py', '-v'],        # 3. явно python
                ['py', '-m', 'pytest', 'test_main.py', '-v']             # 4. для Windows
            ]
            
            result = None  # Переменная для хранения результата выполнения команды
            
            # Перебираем все возможные команды пока не найдем working
            for cmd in pytest_commands:
                try:
                    # Показываем какую команду пробуем
                    print(f"Пробуем команду: {' '.join(cmd)}")
                    
                    # Запускаем команду с захватом вывода
                    result = subprocess.run(
                        cmd, 
                        capture_output=True,  # Захватываем вывод команды
                        text=True,            # Возвращаем текст вместо байтов
                        timeout=30            # Максимальное время выполнения - 30 сек
                    )
                    
                    # Если команда выполнена (не "command not found"), выходим из цикла
                    if result.returncode != 127:
                        break
                        
                # Если команда не найдена или время вышло, пробуем следующую
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            # Если ни одна команда не сработала
            if result is None:
                print("❌ Не удалось найти pytest. Установите его: pip install pytest")
                return False  # Возвращаем False
                
            # Анализируем вывод тестов
            self._parse_console_output(result.stdout)
            
            # Возвращаем True если все тесты прошли успешно (код возврата 0)
            return result.returncode == 0
            
        # Если произошла любая другая ошибка
        except Exception as e:
            print(f"Ошибка при запуске тестов: {e}")
            return False

    def _parse_console_output(self, output: str):
        """Анализирует текстовый вывод pytest и извлекает результаты"""
        print("🔍 Анализ результатов тестов...")
        
        # Регулярные выражения для поиска результатов тестов
        # Ищем строки вида: test_main.py::TestClass::test_method PASSED
        passed_pattern = r'test_main.py::(\w+::\w+)\s+PASSED'
        failed_pattern = r'test_main.py::(\w+::\w+)\s+FAILED'
        skipped_pattern = r'test_main.py::(\w+::\w+)\s+SKIPPED'
        
        # Альтернативные форматы вывода (для разных версий pytest)
        passed_pattern_alt = r'(\w+::\w+)\s+\.\.\.\s+PASSED'
        failed_pattern_alt = r'(\w+::\w+)\s+\.\.\.\s+FAILED'

        """r'...' - "сырая" строка (игнорирует специальные символы)

        test_main.py:: - ищет точную строку "test_main.py::"

        (\w+::\w+) - ГРУППА ЗАХВАТА - находит и запоминает:

        \w+ - одно или больше букв/цифр (название класса)

        :: - два двоеточия

        \w+ - одно или больше букв/цифр (название метода)

        \s+ - один или больше пробельных символов (пробелы, табы)

        PASSED - точное слово "PASSED"""


        
        # Ищем все совпадения с шаблонами в выводе тестов
        # Используем or чтобы пробовать оба варианта шаблонов
        passed_tests = re.findall(passed_pattern, output) or re.findall(passed_pattern_alt, output)
        failed_tests = re.findall(failed_pattern, output) or re.findall(failed_pattern_alt, output)
        skipped_tests = re.findall(skipped_pattern, output)
        
        # Если не нашли тестов через регулярные выражения, используем резервный метод
        if not passed_tests and not failed_tests:
            # Разбиваем вывод на отдельные строки
            lines = output.split('\n')
            
            # Анализируем каждую строку
            for line in lines:
                # Ищем строки с успешными тестами
                if 'PASSED' in line and 'test_main.py' in line:
                    # Разбиваем строку на слова
                    parts = line.split()
                    
                    # Ищем часть с названием теста
                    for part in parts:
                        # Тест содержит :: и упоминает test_main.py
                        if '::' in part and 'test_main.py' in part:
                            # Извлекаем название теста: TestClass::test_method
                            test_name = part.split('::')[-2] + '::' + part.split('::')[-1]
                            passed_tests.append(test_name)  # Добавляем в список успешных
                            break  # Выходим из внутреннего цикла
                
                # Аналогично для проваленных тестов
                elif 'FAILED' in line and 'test_main.py' in line:
                    parts = line.split()
                    for part in parts:
                        if '::' in part and 'test_main.py' in part:
                            test_name = part.split('::')[-2] + '::' + part.split('::')[-1]
                            failed_tests.append(test_name)
                            break
        
        # Обновляем счетчики в результатах
        self.results['passed'] = len(passed_tests)    # Количество успешных
        self.results['failed'] = len(failed_tests)    # Количество проваленных
        self.results['skipped'] = len(skipped_tests)  # Количество пропущенных
        
        # Общее количество тестов = сумма всех типов
        self.results['total_tests'] = (self.results['passed'] + 
                                      self.results['failed'] + 
                                      self.results['skipped'])
        
        # Добавляем детальную информацию о каждом успешном тесте
        for test_name in passed_tests:
            self.results['test_details'].append({
                'name': test_name,      # Название теста
                'status': 'PASSED',     # Статус - успешно
                'error': None           # Ошибок нет
            })
            
        # Добавляем информацию о каждом проваленном тесте
        for test_name in failed_tests:
            self.results['test_details'].append({
                'name': test_name,
                'status': 'FAILED',     # Статус - провален
                'error': 'Смотри детали в полном отчете'  # Сообщение об ошибке
            })
            
        # Добавляем информацию о каждом пропущенном тесте
        for test_name in skipped_tests:
            self.results['test_details'].append({
                'name': test_name,
                'status': 'SKIPPED',    # Статус - пропущен
                'error': None           # Ошибок нет
            })
        
        # Рассчитываем процент успеха только если есть тесты
        if self.results['total_tests'] > 0:
            # Пропущенные тесты не учитываются в проценте успеха
            total_executed = self.results['passed'] + self.results['failed']
            
            # Если есть выполненные тесты (не все пропущены)
            if total_executed > 0:
                # Процент = (успешные / выполненные) * 100, округляем до 1 знака
                self.results['success_rate'] = round(
                    (self.results['passed'] / total_executed) * 100, 1
                )

    def generate_markdown_report(self, filename: str = 'TEST_RESULTS.md'):
        """Создает Markdown отчет для GitHub"""
        try:
            # Начинаем формировать содержимое Markdown файла
            md_content = f"""# 📊 Результаты тестирования

## Общая статистика

| Метрика | Значение |
|---------|----------|
| Всего тестов | {self.results['total_tests']} |
| Успешных | {self.results['passed']} ✅ |
| Проваленных | {self.results['failed']} ❌ |
| Пропущенных | {self.results['skipped']} ⏭️ |
| **Процент успеха** | **{self.results['success_rate']}%** |

## Детальные результаты

### ✅ Успешные тесты ({self.results['passed']})
"""

            # 1. ФИЛЬТРАЦИЯ УСПЕШНЫХ ТЕСТОВ
            # Создаем список только тех тестов, у которых статус равен 'PASSED'
            # Это называется "list comprehension" - компактный способ фильтрации списков
            passed_tests = [t for t in self.results['test_details'] if t['status'] == 'PASSED']
            # - [ ... ] - создаем новый список
# - t for t in self.results['test_details'] - для каждого элемента t в списке test_details
# - if t['status'] == 'PASSED' - только если статус теста равен 'PASSED'
# Результат: список только с успешными тестами
            
            # 2. ДОБАВЛЕНИЕ УСПЕШНЫХ ТЕСТОВ В ОТЧЕТ
            # Проходим по каждому успешному тесту в отфильтрованном списке
            for test in passed_tests:
                # Добавляем строку в Markdown содержание
                # f-строка позволяет вставлять переменные прямо в текст
                # **`...`** - Markdown разметка: жирный шрифт + код (backticks)
                md_content += f"- **`{test['name']}`** - PASSED\n"
                # Разбор:
                # - "- " - маркер списка в Markdown
                # - **`{test['name']}`** - название теста в формате жирного кода
                # - " - PASSED" - текст статуса
                # - "\n" - перенос строки

            # 3. СОЗДАНИЕ РАЗДЕЛА ДЛЯ ПРОВАЛЕННЫХ ТЕСТОВ
            # Добавляем заголовок раздела для проваленных тестов
            md_content += f"\n### ❌ Проваленные тесты ({self.results['failed']})\n"
            # Разбор:
            # - "\n" - пустая строка для разделения
            # - "### " - заголовок третьего уровня в Markdown (### Заголовок)
            # - "❌ Проваленные тесты" - текст заголовка с эмодзи
            # - "({self.results['failed']})" - количество проваленных тестов в скобках
            # Пример: "### ❌ Проваленные тесты (3)"

            # 4. ФИЛЬТРАЦИЯ ПРОВАЛЕННЫХ ТЕСТОВ
            # Аналогично успешным, но фильтруем по статусу 'FAILED'
            failed_tests = [t for t in self.results['test_details'] if t['status'] == 'FAILED']
            # Результат: список только с проваленными тестами
            
            # 5. ДОБАВЛЕНИЕ ПРОВАЛЕННЫХ ТЕСТОВ В ОТЧЕТ
            for test in failed_tests:
                # Для каждого проваленного теста добавляем строку в отчет
                md_content += f"- **`{test['name']}`** - FAILED\n"
                # Формат аналогичен успешным тестам, но с статусом FAILED

            # 6. ПРОВЕРКА НАЛИЧИЯ ПРОПУЩЕННЫХ ТЕСТОВ
            # Проверяем, есть ли хотя бы один пропущенный тест
            if self.results['skipped'] > 0:
                # Если пропущенные тесты есть, добавляем раздел для них

                # 7. СОЗДАНИЕ РАЗДЕЛА ДЛЯ ПРОПУЩЕННЫХ ТЕСТОВ
                md_content += f"\n### ⏭️ Пропущенные тесты ({self.results['skipped']})\n"
                # Аналогично предыдущим разделам, но для пропущенных тестов
                # "⏭️" - эмодзи для пропущенных тестов

                # 8. ФИЛЬТРАЦИЯ ПРОПУЩЕННЫХ ТЕСТОВ
                skipped_tests = [t for t in self.results['test_details'] if t['status'] == 'SKIPPED']
                # Создаем список только с тестами со статусом 'SKIPPED'
                
                # 9. ДОБАВЛЕНИЕ ПРОПУЩЕННЫХ ТЕСТОВ В ОТЧЕТ
                for test in skipped_tests:
                    md_content += f"- **`{test['name']}`** - SKIPPED\n"
                    # Форматирование аналогично предыдущим типам тестов

# 10. ДОБАВЛЕНИЕ СВОДКИ И СИСТЕМНОЙ ИНФОРМАЦИИ
# Многострочная f-строка для добавления заключительной информации
            md_content += f"""
## Сводка

**Всего выполнено тестов:** {self.results['passed'] + self.results['failed']}
**Успешных:** {self.results['passed']} ({self.results['success_rate']}%)
**Проваленных:** {self.results['failed']}
**Пропущенных:** {self.results['skipped']}

## Время тестирования
**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Версия Python:** {sys.version.split()[0]}

## Статус

![Тестирование](https://img.shields.io/badge/Тесты-{self.results['success_rate']}%25%20успеха-{'green' if self.results['success_rate'] > 90 else 'yellow' if self.results['success_rate'] > 70 else 'red'}?style=for-the-badge)
![Статус](https://img.shields.io/badge/Статус-{'Отлично' if self.results['success_rate'] > 90 else 'Требует%20внимания' if self.results['success_rate'] > 70 else 'Критично'}-{'success' if self.results['success_rate'] > 90 else 'yellow' if self.results['success_rate'] > 70 else 'red'}?style=for-the-badge)
![Всего тестов](https://img.shields.io/badge/Тестов-{self.results['total_tests']}-blue?style=for-the-badge)
"""
# Разбор многострочной строки:
# - Тройные кавычки """ позволяют писать многострочный текст
# - ## Сводка - заголовок второго уровня
# - **Жирный текст** - Markdown для выделения
# - {выражения} - подставляются значения переменных
# - datetime.now().strftime() - текущее время в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС"
# - sys.version.split()[0] - только версия Python (первое слово)
# - shields.io бейджи - динамические значки для отображения статуса

            # Записываем содержимое в файл
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"✅ Markdown отчет сохранен в {filename}")
            
        # Если произошла ошибка при создании отчета
        except Exception as e:
            print(f"❌ Ошибка при создании Markdown отчета: {e}")

    def print_summary(self):
        """Выводит краткую сводку результатов в консоль"""
        print("\n" + "="*60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
        print("="*60)
        print(f"Всего тестов:    {self.results['total_tests']}")
        print(f"Успешных:        {self.results['passed']} ✅")
        print(f"Проваленных:     {self.results['failed']} ❌")
        print(f"Пропущенных:     {self.results['skipped']} ⏭️")
        print(f"Процент успеха:  {self.results['success_rate']}%")
        print("="*60)
        
        # Если есть проваленные тесты, показываем их список
        if self.results['failed'] > 0:
            print("❌ ПРОВАЛЕННЫЕ ТЕСТЫ:")
            # Фильтруем только проваленные тесты
            failed_tests = [t for t in self.results['test_details'] if t['status'] == 'FAILED']
            
            # Выводим каждый проваленный тест
            for test in failed_tests:
                print(f"   - {test['name']}")

    def display_results(self):
        """Показывает детальные результаты в консоли в красивом формате"""
        print("\n" + "="*60)
        print("🎯 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("="*60)
        
        # Выводим общую статистику
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего тестов:    {self.results['total_tests']}")
        print(f"   ✅ Успешных:     {self.results['passed']}")
        print(f"   ❌ Проваленных:  {self.results['failed']}")
        print(f"   ⏭️ Пропущенных:  {self.results['skipped']}")
        print(f"   📊 Процент успеха: {self.results['success_rate']}%")
        
        # Если есть детальная информация о тестах
        if self.results['test_details']:
            print(f"\n🔍 ДЕТАЛИ ТЕСТОВ:")
            
            # Фильтруем и выводим успешные тесты
            passed_tests = [t for t in self.results['test_details'] if t['status'] == 'PASSED']
            if passed_tests:
                print(f"\n   ✅ УСПЕШНЫЕ ТЕСТЫ ({len(passed_tests)}):")
                for test in passed_tests:
                    print(f"      ✓ {test['name']}")
            
            # Фильтруем и выводим проваленные тесты
            failed_tests = [t for t in self.results['test_details'] if t['status'] == 'FAILED']
            if failed_tests:
                print(f"\n   ❌ ПРОВАЛЕННЫЕ ТЕСТЫ ({len(failed_tests)}):")
                for test in failed_tests:
                    print(f"      ✗ {test['name']}")
            
            # Фильтруем и выводим пропущенные тесты
            skipped_tests = [t for t in self.results['test_details'] if t['status'] == 'SKIPPED']
            if skipped_tests:
                print(f"\n   ⏭️ ПРОПУЩЕННЫЕ ТЕСТЫ ({len(skipped_tests)}):")
                for test in skipped_tests:
                    print(f"      → {test['name']}")
        
        # Выводим системную информацию
        print(f"\n🖥️  СИСТЕМНАЯ ИНФОРМАЦИЯ:")
        print(f"   Время тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Версия Python: {sys.version.split()[0]}")
        
        print("="*60)

    def manual_test_analysis(self):
        """Позволяет ввести результаты тестов вручную если автоматика не сработала"""
        print("\n🤖 Ручной анализ тестов...")
        print("Введите результаты тестов вручную:")
        
        # Запрашиваем у пользователя данные о тестах
        # or "11" - значение по умолчанию если пользователь просто нажмет Enter
        self.results['total_tests'] = int(input("Всего тестов: ") or "11")
        self.results['passed'] = int(input("Успешных тестов: ") or "8")
        self.results['failed'] = int(input("Проваленных тестов: ") or "3")
        self.results['skipped'] = int(input("Пропущенных тестов: ") or "0")
        
        # Пересчитываем процент успеха на основе введенных данных
        if self.results['total_tests'] > 0:
            total_executed = self.results['passed'] + self.results['failed']
            if total_executed > 0:
                self.results['success_rate'] = round(
                    (self.results['passed'] / total_executed) * 100, 1
                )


def main():
    """Главная функция которая управляет всем процессом"""
    print("🚀 Запуск тестов и генерация отчетов...")
    
    # Создаем генератор отчетов
    generator = TestReportGenerator()
    
    # Запускаем тесты и запоминаем результат
    tests_passed = generator.run_tests()
    
    # Если автоматический запуск не сработал (нет тестов)
    if generator.results['total_tests'] == 0:
        print("⚠️  Автоматический запуск тестов не сработал")
        
        # Спрашиваем пользователя хочет ли он ввести результаты вручную
        use_manual = input("Хотите ввести результаты вручную? (y/n): ").lower()
        
        # Если пользователь согласился, запускаем ручной ввод
        if use_manual == 'y':
            generator.manual_test_analysis()
    
    # Генерируем Markdown отчет
    generator.generate_markdown_report()
    
    # Показываем детальные результаты в консоли
    generator.display_results()
    
    # Показываем краткую сводку
    generator.print_summary()
    
    # Проверяем успешность выполнения
    if tests_passed and generator.results['failed'] == 0:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("⚠️  Обнаружены проваленные тесты или проблемы с запуском!")
    
    # Возвращаем результат: True если успешно, False если есть ошибки
    return tests_passed and generator.results['failed'] == 0


# Этот код выполнится только если файл запущен напрямую
# (а не импортирован как модуль в другой файл)
if __name__ == "__main__":
    # Запускаем главную функцию и получаем результат
    success = main()
    
    # Завершаем программу с кодом 0 (успех) или 1 (ошибка)
    # Это важно для систем автоматизации (CI/CD)
    sys.exit(0 if success else 1)