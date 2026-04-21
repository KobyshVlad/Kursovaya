import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api/auth';

function getCurrentMonthValue() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
}

function monthToDate(value) {
  return `${value}-01`;
}

export default function RegisterPage() {
  const defaultMonth = useMemo(() => getCurrentMonthValue(), []);
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirm_password: '',
    start_month: defaultMonth,
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    if (form.password !== form.confirm_password) {
      setError('Пароли не совпадают');
      return;
    }

    if (new TextEncoder().encode(form.password).length > 72) {
      setError('Пароль не должен превышать 72 байта');
      return;
    }

    try {
      await register({
        name: form.name,
        email: form.email,
        password: form.password,
        start_month: monthToDate(form.start_month),
      });
      navigate('/login');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Регистрация</h1>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label className="field">
            <span>Имя</span>
            <input name="name" value={form.name} onChange={handleChange} required />
          </label>

          <label className="field">
            <span>Email</span>
            <input name="email" type="email" value={form.email} onChange={handleChange} required />
          </label>

          <label className="field">
            <span>Пароль</span>
            <input name="password" type="password" value={form.password} onChange={handleChange} maxLength={72} required />
          </label>

          <label className="field">
            <span>Подтверждение пароля</span>
            <input name="confirm_password" type="password" value={form.confirm_password} onChange={handleChange} maxLength={72} required />
          </label>

          <label className="field">
            <span>Месяц начала ведения личного бюджета</span>
            <input name="start_month" type="month" value={form.start_month} onChange={handleChange} required />
          </label>

          {error ? <div className="error-message">{error}</div> : null}

          <button className="primary-button" type="submit">Зарегистрироваться</button>
        </form>

        <div className="auth-link">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </div>
      </div>
    </div>
  );
}
