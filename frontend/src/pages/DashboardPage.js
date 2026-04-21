import React, { useEffect, useMemo, useState } from 'react';
import StatsCard from '../components/StatsCard';
import { getOperations } from '../api/operations';
import { getBudgetCompare } from '../api/budget';
import { getCurrentUser } from '../api/users';

function formatMoney(value) {
  return `${Number(value || 0).toFixed(2)} ₽`;
}

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

export default function DashboardPage() {
  const now = useMemo(() => new Date(), []);
  const [selectedMonth, setSelectedMonth] = useState(toMonthValue(now.getFullYear(), now.getMonth() + 1));
  const [minMonth, setMinMonth] = useState('');
  const [maxMonth] = useState(getNextMonthValue());
  const [operations, setOperations] = useState([]);
  const [compare, setCompare] = useState([]);
  const [error, setError] = useState('');

  const { month, year } = useMemo(() => parseMonthValue(selectedMonth), [selectedMonth]);

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
    Promise.all([
      getOperations(month, year),
      getBudgetCompare(month, year),
    ])
      .then(([operationsData, compareData]) => {
        setOperations(operationsData);
        setCompare(compareData);
      })
      .catch((err) => setError(err.message));
  }, [month, year]);

  const totals = operations.reduce(
    (acc, item) => {
      if (item.type === 'income') acc.income += Number(item.amount);
      if (item.type === 'expense') acc.expense += Number(item.amount);
      return acc;
    },
    { income: 0, expense: 0 }
  );

  return (
    <div>
      <div className="page-header">
        <h1>Главная</h1>
        <p>Обзор финансов за выбранный месяц</p>
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

      <div className="stats-grid">
        <StatsCard title="Доходы" value={formatMoney(totals.income)} />
        <StatsCard title="Расходы" value={formatMoney(totals.expense)} />
        <StatsCard title="Баланс" value={formatMoney(totals.income - totals.expense)} />
      </div>

      <div className="content-grid">
        <section className="card">
          <h2>Последние операции</h2>
          <div className="list-table">
            <div className="list-table__head dashboard-operations-head">
              <span>Дата</span>
              <span>Категория</span>
              <span>Тип</span>
              <span>Сумма</span>
              <span>Комментарий</span>
            </div>
            {operations.length === 0 ? (
              <div className="empty-state">Нет данных за выбранный период</div>
            ) : (
              operations.slice(0, 8).map((item) => (
                <div className="list-table__row dashboard-operations-row" key={item.id}>
                  <span>{item.operation_date}</span>
                  <span>{item.category_name || '—'}</span>
                  <span>{item.type === 'expense' ? 'Расход' : 'Доход'}</span>
                  <span>{formatMoney(item.amount)}</span>
                  <span>{item.comment || '—'}</span>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="card">
          <h2>План и факт</h2>
          <div className="list-table">
            <div className="list-table__head dashboard-compare-head">
              <span>Категория</span>
              <span>План</span>
              <span>Факт</span>
            </div>
            {compare.length === 0 ? (
              <div className="empty-state">План бюджета не заполнен</div>
            ) : (
              compare.map((item, index) => (
                <div className="list-table__row dashboard-compare-row" key={`${item.category_name || index}`}>
                  <span>{item.category_name || 'Категория'}</span>
                  <span>{formatMoney(item.planned_amount)}</span>
                  <span>{formatMoney(item.actual_amount)}</span>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
