import json
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess
import sys
import re
import os
from typing import Dict, List, Any

class TestReportGenerator:
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'success_rate': 0.0,
            'test_details': [],
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version
        }

    def run_tests(self) -> bool:
        """Запускает тесты и собирает результаты"""
        try:
            # Определяем правильную команду для запуска pytest
            # Пробуем разные варианты, так как путь к pytest может отличаться
            pytest_commands = [
                [sys.executable, '-m', 'pytest', 'test_main.py', '-v'],
                ['pytest', 'test_main.py', '-v'],
                ['python', '-m', 'pytest', 'test_main.py', '-v'],
                ['py', '-m', 'pytest', 'test_main.py', '-v']
            ]
            
            result = None
            for cmd in pytest_commands:
                try:
                    print(f"Пробуем команду: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode != 127:  # 127 означает "command not found"
                        break
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            if result is None:
                print("❌ Не удалось найти pytest. Установите его: pip install pytest")
                return False
                
            # Парсим вывод для получения результатов
            self._parse_console_output(result.stdout)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Ошибка при запуске тестов: {e}")
            return False

    def _parse_console_output(self, output: str):
        """Парсит консольный вывод pytest"""
        print("🔍 Анализ результатов тестов...")
        
        # Регулярные выражения для поиска результатов тестов
        passed_pattern = r'test_main.py::(\w+::\w+)\s+PASSED'
        failed_pattern = r'test_main.py::(\w+::\w+)\s+FAILED'
        skipped_pattern = r'test_main.py::(\w+::\w+)\s+SKIPPED'
        
        # Альтернативные паттерны для разных форматов вывода
        passed_pattern_alt = r'(\w+::\w+)\s+\.\.\.\s+PASSED'
        failed_pattern_alt = r'(\w+::\w+)\s+\.\.\.\s+FAILED'
        
        # Ищем все результаты тестов
        passed_tests = re.findall(passed_pattern, output) or re.findall(passed_pattern_alt, output)
        failed_tests = re.findall(failed_pattern, output) or re.findall(failed_pattern_alt, output)
        skipped_tests = re.findall(skipped_pattern, output)
        
        # Если не нашли через regex, пробуем анализировать построчно
        if not passed_tests and not failed_tests:
            lines = output.split('\n')
            for line in lines:
                if 'PASSED' in line and 'test_main.py' in line:
                    # Извлекаем имя теста из строки
                    parts = line.split()
                    for part in parts:
                        if '::' in part and 'test_main.py' in part:
                            test_name = part.split('::')[-2] + '::' + part.split('::')[-1]
                            passed_tests.append(test_name)
                            break
                elif 'FAILED' in line and 'test_main.py' in line:
                    parts = line.split()
                    for part in parts:
                        if '::' in part and 'test_main.py' in part:
                            test_name = part.split('::')[-2] + '::' + part.split('::')[-1]
                            failed_tests.append(test_name)
                            break
        
        # Обновляем счетчики
        self.results['passed'] = len(passed_tests)
        self.results['failed'] = len(failed_tests)
        self.results['skipped'] = len(skipped_tests)
        self.results['total_tests'] = self.results['passed'] + self.results['failed'] + self.results['skipped']
        
        # Добавляем детали тестов
        for test_name in passed_tests:
            self.results['test_details'].append({
                'name': test_name,
                'status': 'PASSED',
                'error': None
            })
            
        for test_name in failed_tests:
            self.results['test_details'].append({
                'name': test_name,
                'status': 'FAILED',
                'error': 'Смотри детали в полном отчете'
            })
            
        for test_name in skipped_tests:
            self.results['test_details'].append({
                'name': test_name,
                'status': 'SKIPPED',
                'error': None
            })
        
        # Рассчитываем процент успеха
        if self.results['total_tests'] > 0:
            total_executed = self.results['passed'] + self.results['failed']
            if total_executed > 0:
                self.results['success_rate'] = round(
                    (self.results['passed'] / total_executed) * 100, 1
                )

    def generate_json_report(self, filename: str = 'test_results.json'):
        """Генерирует JSON отчет"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"✅ JSON отчет сохранен в {filename}")
        except Exception as e:
            print(f"❌ Ошибка при создании JSON отчета: {e}")

    def generate_markdown_report(self, filename: str = 'TEST_RESULTS.md'):
        """Генерирует Markdown отчет для GitHub"""
        try:
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

            # Добавляем успешные тесты
            passed_tests = [t for t in self.results['test_details'] if t['status'] == 'PASSED']
            for test in passed_tests:
                md_content += f"- **`{test['name']}`** - PASSED\n"

            md_content += f"\n### ❌ Проваленные тесты ({self.results['failed']})\n"

            # Добавляем проваленные тесты
            failed_tests = [t for t in self.results['test_details'] if t['status'] == 'FAILED']
            for test in failed_tests:
                md_content += f"- **`{test['name']}`** - FAILED\n"

            if self.results['skipped'] > 0:
                md_content += f"\n### ⏭️ Пропущенные тесты ({self.results['skipped']})\n"
                skipped_tests = [t for t in self.results['test_details'] if t['status'] == 'SKIPPED']
                for test in skipped_tests:
                    md_content += f"- **`{test['name']}`** - SKIPPED\n"

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

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"✅ Markdown отчет сохранен в {filename}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании Markdown отчета: {e}")

    def generate_html_report(self, filename: str = 'test_report.html'):
        """Генерирует HTML отчет"""
        try:
            status_class = 'success' if self.results['success_rate'] > 90 else 'warning' if self.results['success_rate'] > 70 else 'danger'
            status_text = 'Отлично' if self.results['success_rate'] > 90 else 'Требует внимания' if self.results['success_rate'] > 70 else 'Критично'
            
            html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Результаты тестирования</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .success {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .skipped {{ color: #6c757d; }}
        .warning {{ color: #ffc107; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .badge {{ display: inline-block; padding: 8px 15px; border-radius: 20px; color: white; font-weight: bold; margin: 5px; }}
        .badge-success {{ background-color: #28a745; }}
        .badge-warning {{ background-color: #ffc107; }}
        .badge-danger {{ background-color: #dc3545; }}
        .badge-info {{ background-color: #17a2b8; }}
        .test-list {{ margin: 20px 0; }}
        .test-item {{ padding: 10px; margin: 5px 0; border-left: 4px solid; }}
        .test-passed {{ border-left-color: #28a745; background-color: #f8fff8; }}
        .test-failed {{ border-left-color: #dc3545; background-color: #fff8f8; }}
        .test-skipped {{ border-left-color: #6c757d; background-color: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Результаты тестирования</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div>Всего тестов</div>
                <div class="stat-number">{self.results['total_tests']}</div>
            </div>
            <div class="stat-card">
                <div class="success">Успешных</div>
                <div class="stat-number success">{self.results['passed']} ✅</div>
            </div>
            <div class="stat-card">
                <div class="failed">Проваленных</div>
                <div class="stat-number failed">{self.results['failed']} ❌</div>
            </div>
            <div class="stat-card">
                <div class="skipped">Пропущенных</div>
                <div class="stat-number skipped">{self.results['skipped']} ⏭️</div>
            </div>
        </div>

        <div class="stat-card">
            <div>Процент успеха</div>
            <div class="stat-number" style="color: {'#28a745' if self.results['success_rate'] > 90 else '#ffc107' if self.results['success_rate'] > 70 else '#dc3545'}">
                {self.results['success_rate']}%
            </div>
        </div>

        <h2>Детальные результаты</h2>
        
        <h3 class="success">✅ Успешные тесты ({self.results['passed']})</h3>
        <div class="test-list">
"""

            for test in [t for t in self.results['test_details'] if t['status'] == 'PASSED']:
                html_content += f'            <div class="test-item test-passed"><strong>{test["name"]}</strong> - PASSED</div>\n'

            html_content += f"""        </div>

        <h3 class="failed">❌ Проваленные тесты ({self.results['failed']})</h3>
        <div class="test-list">
"""

            for test in [t for t in self.results['test_details'] if t['status'] == 'FAILED']:
                html_content += f'            <div class="test-item test-failed"><strong>{test["name"]}</strong> - FAILED</div>\n'

            if self.results['skipped'] > 0:
                html_content += f"""
        <h3 class="skipped">⏭️ Пропущенные тесты ({self.results['skipped']})</h3>
        <div class="test-list">
"""
                for test in [t for t in self.results['test_details'] if t['status'] == 'SKIPPED']:
                    html_content += f'            <div class="test-item test-skipped"><strong>{test["name"]}</strong> - SKIPPED</div>\n'
                html_content += '        </div>'

            html_content += f"""
        <h2>Информация о системе</h2>
        <p><strong>Время тестирования:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Версия Python:</strong> {sys.version.split()[0]}</p>

        <div class="badge badge-{status_class}">
            Статус: {status_text}
        </div>
        <div class="badge badge-info">
            Всего тестов: {self.results['total_tests']}
        </div>
    </div>
</body>
</html>"""

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ HTML отчет сохранен в {filename}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании HTML отчета: {e}")

    def print_summary(self):
        """Выводит сводку результатов в консоль"""
        print("\n" + "="*60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
        print("="*60)
        print(f"Всего тестов:    {self.results['total_tests']}")
        print(f"Успешных:        {self.results['passed']} ✅")
        print(f"Проваленных:     {self.results['failed']} ❌")
        print(f"Пропущенных:     {self.results['skipped']} ⏭️")
        print(f"Процент успеха:  {self.results['success_rate']}%")
        print("="*60)
        
        if self.results['failed'] > 0:
            print("❌ ПРОВАЛЕННЫЕ ТЕСТЫ:")
            for test in [t for t in self.results['test_details'] if t['status'] == 'FAILED']:
                print(f"   - {test['name']}")

    def manual_test_analysis(self):
        """Ручной анализ тестов, если автоматический не сработал"""
        print("\n🤖 Ручной анализ тестов...")
        print("Введите результаты тестов вручную:")
        
        self.results['total_tests'] = int(input("Всего тестов: ") or "11")
        self.results['passed'] = int(input("Успешных тестов: ") or "8")
        self.results['failed'] = int(input("Проваленных тестов: ") or "3")
        self.results['skipped'] = int(input("Пропущенных тестов: ") or "0")
        
        if self.results['total_tests'] > 0:
            total_executed = self.results['passed'] + self.results['failed']
            if total_executed > 0:
                self.results['success_rate'] = round(
                    (self.results['passed'] / total_executed) * 100, 1
                )

def main():
    """Основная функция генерации отчетов"""
    print("🚀 Запуск тестов и генерация отчетов...")
    
    generator = TestReportGenerator()
    tests_passed = generator.run_tests()
    
    # Если автоматический запуск не сработал, предлагаем ручной ввод
    if generator.results['total_tests'] == 0:
        print("⚠️  Автоматический запуск тестов не сработал")
        use_manual = input("Хотите ввести результаты вручную? (y/n): ").lower()
        if use_manual == 'y':
            generator.manual_test_analysis()
    
    # Генерируем все форматы отчетов
    generator.generate_json_report()
    generator.generate_markdown_report()
    generator.generate_html_report()
    
    # Выводим сводку в консоль
    generator.print_summary()
    
    if tests_passed and generator.results['failed'] == 0:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("⚠️  Обнаружены проваленные тесты или проблемы с запуском!")
    
    return tests_passed and generator.results['failed'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)