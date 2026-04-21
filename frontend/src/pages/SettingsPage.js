import React, { useEffect, useState } from 'react';
import { getCurrentUser, updateCurrentUser } from '../api/users';

function dateToMonth(value) {
  if (!value) return '';
  return String(value).slice(0, 7);
}

function monthToDate(value) {
  return `${value}-01`;
}

export default function SettingsPage() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    start_month: '',
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    getCurrentUser()
      .then((data) => {
        setForm({
          name: data.name || '',
          email: data.email || '',
          start_month: dateToMonth(data.start_month),
        });
      })
      .catch((err) => setError(err.message));
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage('');
    setError('');

    try {
      await updateCurrentUser({
        ...form,
        start_month: monthToDate(form.start_month),
      });
      setMessage('Данные успешно обновлены');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Настройки</h1>
        <p>Управление данными учетной записи</p>
      </div>

      <section className="card settings-card">
        <form className="form-grid" onSubmit={handleSubmit}>
          <label className="field">
            <span>Имя</span>
            <input value={form.name} onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))} />
          </label>

          <label className="field">
            <span>Email</span>
            <input type="email" value={form.email} onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))} />
          </label>

          <label className="field">
            <span>Месяц начала ведения личного бюджета</span>
            <input type="month" value={form.start_month} onChange={(e) => setForm((prev) => ({ ...prev, start_month: e.target.value }))} />
          </label>

          {error ? <div className="error-message">{error}</div> : null}
          {message ? <div className="success-message">{message}</div> : null}

          <div className="form-actions">
            <button className="primary-button" type="submit">Сохранить</button>
          </div>
        </form>
      </section>
    </div>
  );
}
