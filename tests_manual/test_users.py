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

    def get_me():
        resp = api_request("GET", "/users/me", token=token)
        check(resp.status_code == 200, f"ожидался 200, получен {resp.status_code}: {resp.text}")
        data = resp.json()
        check(data["email"] == user["email"], "email профиля не совпадает")

    def update_me():
        payload = {
            "name": "Обновленный Пользователь",
            "email": f"updated_{uuid.uuid4().hex[:8]}@example.com",
            "start_month": user["start_month"],
        }
        resp = api_request("PUT", "/users/me", token=token, json=payload)
        check(resp.status_code == 200, f"ожидался 200, получен {resp.status_code}: {resp.text}")
        data = resp.json()
        check(data["name"] == payload["name"], "имя не обновилось")
        check(data["email"] == payload["email"], "email не обновился")

    run_case(results, "test_users.py", "Получение данных текущего пользователя", "HTTP 200, данные профиля возвращены", get_me)
    run_case(results, "test_users.py", "Обновление имени, email и месяца начала бюджета", "HTTP 200, данные пользователя обновлены", update_me)

    print_results(results)

if __name__ == "__main__":
    main()
