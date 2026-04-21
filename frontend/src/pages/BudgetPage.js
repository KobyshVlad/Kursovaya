import React, { useEffect, useMemo, useState } from 'react';
import { getCategories } from '../api/categories';
import { createBudget, getBudget, getBudgetCompare } from '../api/budget';
import { getCurrentUser } from '../api/users';

function toMonthValue(year, month) {
  return `${year}-${String(month).padStart(2, '0')}`;
}

function parseMonthValue(value) {
  const [year, month] = value.split('-').map(Number);
  return { year, month };
}

function getNextMonthValue() {
  const now = new Date();
  now.setMonth(now.getMonth() + 1);
  return toMonthValue(now.getFullYear(), now.getMonth() + 1);
}

export default function BudgetPage() {
  const now = useMemo(() => new Date(), []);
  const [selectedMonth, setSelectedMonth] = useState(toMonthValue(now.getFullYear(), now.getMonth() + 1));
  const [minMonth, setMinMonth] = useState('');
  const [maxMonth] = useState(getNextMonthValue());
  const { month, year } = useMemo(() => parseMonthValue(selectedMonth), [selectedMonth]);

  const [categories, setCategories] = useState([]);
  const [budgetRows, setBudgetRows] = useState([]);
  const [compareRows, setCompareRows] = useState([]);
  const [form, setForm] = useState({ category_id: '', planned_amount: '' });
  const [error, setError] = useState('');

  const loadData = async (currentMonth = month, currentYear = year) => {
    try {
      const [categoriesData, budgetData, compareData] = await Promise.all([
        getCategories(),
        getBudget(currentMonth, currentYear),
        getBudgetCompare(currentMonth, currentYear),
      ]);
      setCategories(categoriesData);
      setBudgetRows(budgetData);
      setCompareRows(compareData);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    getCurrentUser()
      .then((user) => {
        if (user.start_month) {
          const min = String(user.start_month).slice(0, 7);
          setMinMonth(min);
          if (selectedMonth < min) {
            setSelectedMonth(min);
          }
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    loadData(month, year);
  }, [month, year]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await createBudget({
      category_id: Number(form.category_id),
      planned_amount: Number(form.planned_amount),
      month,
      year,
    });
    setForm({ category_id: '', planned_amount: '' });
    await loadData(month, year);
  };

  return (
    <div>
      <div className="page-header">
        <h1>Планирование бюджета</h1>
        <p>Настройка плановых расходов по категориям</p>
      </div>

      <section className="card month-filter-card">
        <div className="month-filter">
          <label className="field month-field">
            <span>Месяц</span>
            <input
              type="month"
              value={selectedMonth}
              min={minMonth || undefined}
              max={maxMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
            />
          </label>
        </div>
      </section>

      {error ? <div className="error-message">{error}</div> : null}

      <div className="content-grid">
        <section className="card">
          <h2>Добавить лимит</h2>
          <form className="form-grid" onSubmit={handleSubmit}>
            <label className="field">
              <span>Категория</span>
              <select
                value={form.category_id}
                onChange={(e) => setForm((prev) => ({ ...prev, category_id: e.target.value }))}
                required
              >
                <option value="">Выберите категорию</option>
                {categories.map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Плановая сумма</span>
              <input
                type="number"
                min="0"
                step="0.01"
                value={form.planned_amount}
                onChange={(e) => setForm((prev) => ({ ...prev, planned_amount: e.target.value }))}
                required
              />
            </label>

            <div className="form-actions">
              <button className="primary-button" type="submit">Сохранить</button>
            </div>
          </form>
        </section>

        <section className="card">
          <h2>Текущий бюджет</h2>
          <div className="list-table">
            <div className="list-table__head budget-head">
              <span>Категория</span>
              <span>План</span>
            </div>
            {budgetRows.length === 0 ? (
              <div className="empty-state">Лимиты еще не заданы</div>
            ) : (
              budgetRows.map((item) => (
                <div className="list-table__row budget-row" key={item.id}>
                  <span>{item.category_name || item.category_id}</span>
                  <span>{item.planned_amount} ₽</span>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      <section className="card">
        <h2>Сравнение плана и факта</h2>
        <div className="list-table">
          <div className="list-table__head compare-head">
            <span>Категория</span>
            <span>План</span>
            <span>Факт</span>
          </div>
          {compareRows.length === 0 ? (
            <div className="empty-state">Нет данных для сравнения</div>
          ) : (
            compareRows.map((item, index) => (
              <div className="list-table__row compare-row" key={`${item.category_name || index}`}>
                <span>{item.category_name || 'Категория'}</span>
                <span>{item.planned_amount} ₽</span>
                <span>{item.actual_amount} ₽</span>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
