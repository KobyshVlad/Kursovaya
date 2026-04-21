# Ручные API-тесты

В этой папке находятся тестовые скрипты для проверки backend API.
Они **не запускаются автоматически** и предназначены для ручного запуска после старта приложения.

## Подготовка

1. Запустить приложение:
   ```bash
   docker compose up --build
   ```

2. Установить зависимости для тестов:
   ```bash
   pip install -r tests_manual/requirements.txt
   ```

## Запуск

Каждый модуль можно запускать отдельно:

```bash
python tests_manual/test_auth.py
python tests_manual/test_users.py
python tests_manual/test_categories.py
python tests_manual/test_operations.py
python tests_manual/test_budget.py
python tests_manual/test_dashboard.py
```

При необходимости можно переопределить адрес backend:

```bash
BASE_URL=http://localhost:8000 python tests_manual/test_auth.py
```

## Что выводят скрипты

Каждый скрипт выполняет один набор сценариев и печатает таблицу:

- Модуль
- Сценарий
- Ожидаемый результат
- Статус

Статусы:
- Успешно
- Неуспешно

## Важно

- Скрипты создают тестовые данные в базе.
- Тесты выполняются вручную и не привязаны к автозапуску приложения.
- Для корректной повторной проверки лучше использовать свежую базу данных.
