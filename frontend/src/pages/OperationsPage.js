import React, { useEffect, useState } from 'react';
import OperationForm from '../components/OperationForm';
import { getCategories } from '../api/categories';
import { createOperation, deleteOperation, getOperations, updateOperation } from '../api/operations';

export default function OperationsPage() {
  const [categories, setCategories] = useState([]);
  const [operations, setOperations] = useState([]);
  const [editingItem, setEditingItem] = useState(null);
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      const [categoriesData, operationsData] = await Promise.all([
        getCategories(),
        getOperations(),
      ]);
      setCategories(categoriesData);
      setOperations(operationsData);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (payload) => {
    await createOperation(payload);
    setEditingItem(null);
    await loadData();
  };

  const handleUpdate = async (payload) => {
    await updateOperation(editingItem.id, payload);
    setEditingItem(null);
    await loadData();
  };

  const handleDelete = async (id) => {
    await deleteOperation(id);
    await loadData();
  };

  return (
    <div>
      <div className="page-header">
        <h1>Операции</h1>
        <p>Добавление, редактирование и удаление доходов и расходов</p>
      </div>

      {error ? <div className="error-message">{error}</div> : null}

      <div className="content-grid">
        <section className="card">
          <h2>{editingItem ? 'Редактирование операции' : 'Добавление операции'}</h2>
          <OperationForm
            categories={categories}
            initialValues={editingItem}
            onSubmit={editingItem ? handleUpdate : handleCreate}
            onCancel={() => setEditingItem(null)}
            submitLabel={editingItem ? 'Обновить' : 'Сохранить'}
          />
        </section>

        <section className="card">
          <h2>Список операций</h2>
          <div className="list-table">
            <div className="list-table__head operations-head">
              <span>Дата</span>
              <span>Категория</span>
              <span>Сумма</span>
              <span>Действия</span>
            </div>

            {operations.length === 0 ? (
              <div className="empty-state">Операции отсутствуют</div>
            ) : (
              operations.map((item) => (
                <div className="list-table__row operations-row" key={item.id}>
                  <span>{item.operation_date}</span>
                  <span>{item.category_name || item.category_id}</span>
                  <span>{item.amount} ₽</span>
                  <span className="row-actions">
                    <button className="link-button" onClick={() => setEditingItem(item)}>Изменить</button>
                    <button className="link-button link-button--danger" onClick={() => handleDelete(item.id)}>Удалить</button>
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
