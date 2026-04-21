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

    month = date.today().month
    year = date.today().year

    def create_budget():
        resp = api_request(
            "POST",
            "/budget",
            token=token,
            json={
                "category_id": food["id"],
                "month": month,
                "year": year,
                "planned_amount": "5000.00",
            },
        )
        check(resp.status_code == 201, f"ожидался 201, получен {resp.status_code}: {resp.text}")

    def get_budget():
        resp = api_request("GET", f"/budget?month={month}&year={year}", token=token)
        check(resp.status_code == 200, f"ожидался 200, получен {resp.status_code}: {resp.text}")
        check(any(item["category_id"] == food["id"] for item in resp.json()), "бюджетная запись не найдена")

    def get_compare():
        op = api_request(
            "POST",
            "/operations",
            token=token,
            json={
                "category_id": food["id"],
                "type": "expense",
                "amount": "1250.00",
                "operation_date": date.today().isoformat(),
                "comment": "Факт для сравнения",
            },
        )
        check(op.status_code == 201, f"не удалось создать операцию: {op.text}")

        resp = api_request("GET", f"/budget/compare?month={month}&year={year}", token=token)
        check(resp.status_code == 200, f"ожидался 200, получен {resp.status_code}: {resp.text}")
        data = resp.json()
        match = next((item for item in data if item["category_id"] == food["id"]), None)
        check(match is not None, "сравнение по категории не найдено")

    run_case(results, "test_budget.py", "Создание лимита по категории", "HTTP 201, запись бюджета создана", create_budget)
    run_case(results, "test_budget.py", "Получение бюджета за месяц", "HTTP 200, бюджетные записи возвращены", get_budget)
    run_case(results, "test_budget.py", "Получение сравнения плана и факта", "HTTP 200, возвращены плановые и фактические значения", get_compare)

    print_results(results)

if __name__ == "__main__":
    main()
