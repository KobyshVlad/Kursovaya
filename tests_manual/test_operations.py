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

    cats = api_request("GET", "/categories", token=token)
    check(cats.status_code == 200, f"не удалось получить категории: {cats.text}")
    food = next((c for c in cats.json() if c["name"] == "Продукты"), None)
    check(food is not None, "категория 'Продукты' не найдена")

    operation_id = None
    month = date.today().month
    year = date.today().year

    def create_operation():
        nonlocal operation_id
        resp = api_request(
            "POST",
            "/operations",
            token=token,
            json={
                "category_id": food["id"],
                "type": "expense",
                "amount": "950.00",
                "operation_date": date.today().isoformat(),
                "comment": "Тестовая операция",
            },
        )
        check(resp.status_code == 201, f"ожидался 201, получен {resp.status_code}: {resp.text}")
        data = resp.json()
        operation_id = data["id"]
        check(data["category_name"] == "Продукты", "у операции неверная категория")

    def list_operations():
        resp = api_request("GET", f"/operations?month={month}&year={year}", token=token)
        check(resp.status_code == 200, f"ожидался 200, получен {resp.status_code}: {resp.text}")
        check(any(item["id"] == operation_id for item in resp.json()), "созданная операция не найдена в списке")

    def update_operation():
        resp = api_request(
            "PUT",
            f"/operations/{operation_id}",
            token=token,
            json={
                "category_id": food["id"],
                "type": "expense",
                "amount": "1200.00",
                "operation_date": date.today().isoformat(),
                "comment": "Обновленная операция",
            },
        )
        check(resp.status_code == 200, f"ожидался 200, получен {resp.status_code}: {resp.text}")

    def delete_operation():
        resp = api_request("DELETE", f"/operations/{operation_id}", token=token)
        check(resp.status_code == 204, f"ожидался 204, получен {resp.status_code}: {resp.text}")

    run_case(results, "test_operations.py", "Создание финансовой операции", "HTTP 201, операция создана", create_operation)
    run_case(results, "test_operations.py", "Получение операций за выбранный месяц", "HTTP 200, список операций возвращен", list_operations)
    run_case(results, "test_operations.py", "Редактирование финансовой операции", "HTTP 200, операция обновлена", update_operation)
    run_case(results, "test_operations.py", "Удаление финансовой операции", "HTTP 204, операция удалена", delete_operation)

    print_results(results)

if __name__ == "__main__":
    main()
