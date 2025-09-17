import os
import glob

def find_all_readme_files():
    """Находит все README файлы в текущей папке"""
    # Ищем файлы, которые начинаются с README и заканчиваются .md
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
            continue  # Если файл не читается, пропускаем его
    return False

def create_new_readme(fio, filename):
    """Создает новый README файл с данными пользователя"""
    
    # Приветственное сообщение перед заполнением данных
    print(f"👋 Привет, {fio}! Давай заполним твои данные...")
    
    # Запрашиваем дополнительные данные
    course = input("Введи свой курс: ")
    group = input("Введи свою группу: ")
    specialty = input("Введи специальность: ")
    specialty_code = input("Введи код специальности: ")
    practice = input("Введи название практики: ")
    team = input("Введи номер команды: ")
    
    # Создаем содержимое файла
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
    
    # Записываем в файл
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"✅ Файл {filename} успешно создан!")

def process_user():
    """Обрабатывает одного пользователя"""
    print("\n" + "="*40)
    print("🌟 Проверка профиля")
    print("="*40)
    
    # Запрашиваем ФИО
    fio = input("Введи свое ФИО (или 'выход' для завершения): ").strip()
    
    if fio.lower() in ['выход', 'exit', 'quit', '']:
        return False
    
    # Находим все README файлы
    all_readme_files = find_all_readme_files()
    
    # Ищем пользователя во всех файлах
    user_exists = search_user_in_files(fio, all_readme_files)
    
    if user_exists:
        print(f"✅ Привет, {fio}! Ты уже есть в одном из профилей.")
    else:
        # Если пользователя нет - создаем новый файл
        filename = f"README_{fio.replace(' ', '_')}.md"
        create_new_readme(fio, filename)
        print(f"🎉 Готово, {fio}! Твой профиль создан.")
    
    return True

def main():
    print("Добро пожаловать в систему управления профилями!")
    print("Для выхода введите 'выход'")
    
    # Бесконечный цикл для обработки пользователей
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

# Запускаем программу
if __name__ == "__main__":
    main()