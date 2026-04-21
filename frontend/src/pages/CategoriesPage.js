import React, { useEffect, useState } from 'react';
import { createCategory, deleteCategory, getCategories, updateCategory } from '../api/categories';

export default function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [name, setName] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editingName, setEditingName] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const loadData = async () => {
    try {
      const data = await getCategories();
      setCategories(data);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    setError('');
    setMessage('');
    if (!name.trim()) return;
    try {
      await createCategory({ name: name.trim() });
      setName('');
      setMessage('Категория добавлена');
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdate = async (id) => {
    setError('');
    setMessage('');
    if (!editingName.trim()) return;
    try {
      await updateCategory(id, { name: editingName.trim() });
      setEditingId(null);
      setEditingName('');
      setMessage('Категория обновлена');
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    setError('');
    setMessage('');
    try {
      await deleteCategory(id);
      setMessage('Категория удалена');
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Категории</h1>
        <p>Создание, редактирование и удаление категорий расходов</p>
      </div>

      <div className="content-grid">
        <section className="card">
          <h2>Добавить категорию</h2>
          <form className="form-grid" onSubmit={handleCreate}>
            <label className="field">
              <span>Наименование</span>
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Например, Продукты" />
            </label>
            {error ? <div className="error-message">{error}</div> : null}
            {message ? <div className="success-message">{message}</div> : null}
            <div className="form-actions">
              <button className="primary-button" type="submit">Добавить</button>
            </div>
          </form>
        </section>

        <section className="card">
          <h2>Список категорий</h2>
          <div className="list-table">
            <div className="list-table__head categories-head">
              <span>Название</span>
              <span>Действия</span>
            </div>
            {categories.length === 0 ? (
              <div className="empty-state">Категории пока не добавлены</div>
            ) : (
              categories.map((item) => (
                <div className="list-table__row categories-row" key={item.id}>
                  <span>
                    {editingId === item.id ? (
                      <input
                        className="inline-input"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                      />
                    ) : (
                      item.name
                    )}
                  </span>
                  <span className="row-actions">
                    {editingId === item.id ? (
                      <>
                        <button className="link-button" type="button" onClick={() => handleUpdate(item.id)}>Сохранить</button>
                        <button className="link-button" type="button" onClick={() => { setEditingId(null); setEditingName(''); }}>Отмена</button>
                      </>
                    ) : (
                      <>
                        <button className="link-button" type="button" onClick={() => { setEditingId(item.id); setEditingName(item.name); }}>Изменить</button>
                        <button className="link-button link-button--danger" type="button" onClick={() => handleDelete(item.id)}>Удалить</button>
                      </>
                    )}
                  </span>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
