import os
import sys


def test_import_app():
    try:
        project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sys.path.insert(0, project_path)

        from app import app

        assert app is not None
        print("Приложение импортируется корректно")
        return True
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return False


def test_weather_codes():
    try:
        project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sys.path.insert(0, project_path)

        from app import get_weather_description

        test_cases = [
            (0, "Ясно"),
            (1, "Преимущественно ясно"),
            (3, "Пасмурно"),
            (45, "Туман"),
            (95, "Гроза"),
        ]

        all_passed = True
        for code, expected in test_cases:
            result = get_weather_description(code)
            if result != expected:
                print(f"Код {code}: ожидалось '{expected}', получено '{result}'")
                all_passed = False
            else:
                print(f"Код {code}: '{result}'")

        if all_passed:
            print("Все коды погоды конвертируются корректно")

        return all_passed
    except Exception as e:
        print(f"Ошибка теста кодов погоды: {e}")
        return False


def test_files_exist():
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    repo_root = os.path.abspath(os.path.join(project_path, ".."))

    required_files = [
        os.path.join(project_path, "app.py"),
        os.path.join(repo_root, "requirements.txt"),
        os.path.join(project_path, "templates", "index.html"),
        os.path.join(project_path, "templates", "forecast.html"),
        os.path.join(project_path, "templates", "error.html"),
    ]

    all_exist = True

    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
            all_exist = False
        else:
            print(f"Файл найден: {file_path}")

    if all_exist:
        print("Все необходимые файлы присутствуют")

    return all_exist


if __name__ == "__main__":
    print("Запуск базовых тестов приложения")
    print("=" * 50)

    tests = [
        test_import_app,
        test_weather_codes,
        test_files_exist,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Результат: {passed}/{total} тестов пройдено")

    sys.exit(0 if passed == total else 1)