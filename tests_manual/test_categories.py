import os
import uuid
from datetime import date

import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
API = f"{BASE_URL}/api"

DEFAULT_CATEGORIES = {
    "Медицина",
    "Образование",
    "Продукты",
    "Транспорт",
    "ЖКХ",
    "Аренда",
    "Кредит",
    "Ипотека",
    "Зарплата",
    "Премия",
}


class TestFailure(Exception):
    pass


def check(condition: bool, message: str) -> None:
    if not condition:
        raise TestFailure(message)


def api_request(method: str, path: str, token: str | None = None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if "json" in kwargs:
        headers.setdefault("Content-Type", "application/json")
    return requests.request(method, f"{API}{path}", headers=headers, timeout=20, **kwargs)


def unique_user_payload():
    unique = uuid.uuid4().hex[:8]
    return {
        "name": "Тестовый Пользователь",
        "email": f"test_{unique}@example.com",
        "password": "TestPass123!",
        "start_month": date.today().replace(day=1).isoformat(),
    }


def print_results(rows):
    headers = ["Модуль", "Сценарий", "Ожидаемый результат", "Статус"]
    widths = [len(h) for h in headers]
    data_rows = [[r["module"], r["scenario"], r["expected"], r["status"]] for r in rows]
    for row in data_rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)))

    def fmt(row):
        return " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(row))

    print("\n" + fmt(headers))
    print("-+-".join("-" * w for w in widths))
    for row in data_rows:
        print(fmt(row))


def run_case(results, module, scenario, expected, fn):
    try:
        fn()
        results.append({
            "module": module,
            "scenario": scenario,
            "expected": expected,
            "status": "Успешно",
        })
    except Exception as exc:
        results.append({
            "module": module,
            "scenario": scenario,
            "expected": expected,
            "status": f"Неуспешно: {exc}",
        })

def main():
    results = []
    user = unique_user_payload()

    resp = api_request("POST", "/auth/register", json=user)
    check(resp.status_code == 201, f"не удалось зарегистрировать пользователя: {resp.text}")
    login = api_request("POST", "/auth/login", json={"email": user["email"], "password": user["password"]})
    check(login.status_code == 200, f"не удалось войти: {login.text}")
    token = login.json()["access_token"]

    category_id = None

    def default_categories():
        resp = api_request("GET", "/categories", token=token)
        check(resp.status_code == 200, f"ожидался 200, получен {resp.status_code}: {resp.text}")
        names = {item["name"] for item in resp.json()}
        missing = DEFAULT_CATEGORIES - names
        check(not missing, f"отсутствуют категории: {sorted(missing)}")

    def create_category():
        nonlocal category_id
        resp = api_request("POST", "/categories", token=token, json={"name": "Путешествия"})
        check(resp.status_code == 201, f"ожидался 201, получен {resp.status_code}: {resp.text}")
        data = resp.json()
        category_id = data["id"]
        check(data["name"] == "Путешествия", "категория не создана корректно")

    def update_category():
        resp = api_request("PUT", f"/categories/{category_id}", token=token, json={"name": "Отпуск"})
        check(resp.status_code == 200, f"ожидался 200, получен {resp.status_code}: {resp.text}")
        check(resp.json()["name"] == "Отпуск", "категория не обновилась")

    def delete_category():
        resp = api_request("DELETE", f"/categories/{category_id}", token=token)
        check(resp.status_code == 204, f"ожидался 204, получен {resp.status_code}: {resp.text}")

    run_case(results, "test_categories.py", "Наличие категорий по умолчанию после регистрации", "HTTP 200, стандартные категории возвращены", default_categories)
    run_case(results, "test_categories.py", "Создание новой категории", "HTTP 201, категория создана", create_category)
    run_case(results, "test_categories.py", "Редактирование категории", "HTTP 200, категория обновлена", update_category)
    run_case(results, "test_categories.py", "Удаление категории", "HTTP 204, категория удалена", delete_category)

    print_results(results)

if __name__ == "__main__":
    main()
