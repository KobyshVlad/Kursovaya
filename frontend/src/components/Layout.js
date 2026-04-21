import React, { useEffect, useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { logout } from '../api/auth';
import { getCurrentUser } from '../api/users';

export default function Layout() {
  const navigate = useNavigate();
  const [accountName, setAccountName] = useState('Аккаунт');

  useEffect(() => {
    getCurrentUser()
      .then((data) => {
        setAccountName(data.name || 'Аккаунт');
      })
      .catch(() => {
        setAccountName('Аккаунт');
      });
  }, []);

  const onLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar__brand">{accountName}</div>
        <nav className="sidebar__nav">
          <NavLink to="/" end className="sidebar__link">Главная</NavLink>
          <NavLink to="/operations" className="sidebar__link">Операции</NavLink>
          <NavLink to="/categories" className="sidebar__link">Категории</NavLink>
          <NavLink to="/budget" className="sidebar__link">Планирование</NavLink>
        </nav>
        <div className="sidebar__footer">
          <NavLink to="/settings" className="sidebar__link">Настройки</NavLink>
          <button className="logout-button" onClick={onLogout}>Выйти</button>
        </div>
      </aside>

      <main className="page-content">
        <Outlet />
      </main>
    </div>
  );
}
