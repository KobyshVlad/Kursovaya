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

    def register():
        resp = api_request("POST", "/auth/register", json=user)
        check(resp.status_code == 201, f"ожидался 201, получен {resp.status_code}: {resp.text}")

    def duplicate_register():
        resp = api_request("POST", "/auth/register", json=user)
        check(resp.status_code == 400, f"ожидался 400, получен {resp.status_code}: {resp.text}")

    def login_ok():
        resp = api_request("POST", "/auth/login", json={"email": user["email"], "password": user["password"]})
        check(resp.status_code == 200, f"ожидался 200, получен {resp.status_code}: {resp.text}")
        data = resp.json()
        check("access_token" in data, "access_token отсутствует в ответе")

    def login_bad_password():
        resp = api_request("POST", "/auth/login", json={"email": user["email"], "password": "WrongPass123"})
        check(resp.status_code == 401, f"ожидался 401, получен {resp.status_code}: {resp.text}")

    def protected_without_token():
        resp = api_request("GET", "/users/me")
        check(resp.status_code == 401, f"ожидался 401, получен {resp.status_code}: {resp.text}")

    run_case(results, "test_auth.py", "Регистрация нового пользователя", "HTTP 201, пользователь создан", register)
    run_case(results, "test_auth.py", "Повторная регистрация с тем же email", "HTTP 400, пользователь не создан повторно", duplicate_register)
    run_case(results, "test_auth.py", "Вход с корректными данными", "HTTP 200, access_token в ответе", login_ok)
    run_case(results, "test_auth.py", "Вход с неверным паролем", "HTTP 401", login_bad_password)
    run_case(results, "test_auth.py", "Доступ к защищенному API без токена", "HTTP 401", protected_without_token)

    print_results(results)

if __name__ == "__main__":
    main()
