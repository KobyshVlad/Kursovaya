import React, { useEffect, useState } from 'react';

const initialState = {
  type: 'expense',
  category_id: '',
  amount: '',
  operation_date: '',
  comment: '',
};

export default function OperationForm({
  categories,
  initialValues,
  onSubmit,
  onCancel,
  submitLabel = 'Сохранить',
}) {
  const [form, setForm] = useState(initialState);

  useEffect(() => {
    if (initialValues) {
      setForm({
        type: initialValues.type || 'expense',
        category_id: initialValues.category_id || '',
        amount: initialValues.amount || '',
        operation_date: initialValues.operation_date || '',
        comment: initialValues.comment || '',
      });
    } else {
      setForm(initialState);
    }
  }, [initialValues]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({
      ...form,
      category_id: Number(form.category_id),
      amount: Number(form.amount),
    });
  };

  return (
    <form className="form-grid" onSubmit={handleSubmit}>
      <label className="field">
        <span>Тип операции</span>
        <select name="type" value={form.type} onChange={handleChange}>
          <option value="expense">Расход</option>
          <option value="income">Доход</option>
        </select>
      </label>

      <label className="field">
        <span>Категория</span>
        <select name="category_id" value={form.category_id} onChange={handleChange} required>
          <option value="">Выберите категорию</option>
          {categories.map((item) => (
            <option key={item.id} value={item.id}>{item.name}</option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Сумма</span>
        <input name="amount" type="number" min="0" step="0.01" value={form.amount} onChange={handleChange} required />
      </label>

      <label className="field">
        <span>Дата</span>
        <input name="operation_date" type="date" value={form.operation_date} onChange={handleChange} required />
      </label>

      <label className="field field--full">
        <span>Комментарий</span>
        <textarea name="comment" value={form.comment} onChange={handleChange} rows="3" />
      </label>

      <div className="form-actions">
        <button className="primary-button" type="submit">{submitLabel}</button>
        <button className="secondary-button" type="button" onClick={onCancel}>Отмена</button>
      </div>
    </form>
  );
}
