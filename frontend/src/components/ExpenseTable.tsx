import { useState } from 'react';
import type { Expense } from '../types/expense';
import { updateExpense, deleteExpense } from '../api/expenses';

const CATEGORIES = [
  'Alimentación',
  'Transporte',
  'Hogar',
  'Salud',
  'Ocio',
  'Compras',
  'Finanzas',
  'Ingresos',
  'Otros',
];

interface Props {
  expenses: Expense[];
  onUpdate: () => void;
}

export function ExpenseTable({ expenses, onUpdate }: Props) {
  const [editingId, setEditingId] = useState<number | null>(null);

  const handleCategoryChange = async (id: number, category: string) => {
    await updateExpense(id, { category });
    setEditingId(null);
    onUpdate();
  };

  const handleDelete = async (id: number) => {
    if (confirm('¿Eliminar este gasto?')) {
      await deleteExpense(id);
      onUpdate();
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatAmount = (amount: number) => {
    return amount.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' });
  };

  if (expenses.length === 0) {
    return (
      <div className="table-container">
        <div className="empty-state">
          <div className="icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="12" y1="18" x2="12" y2="12" />
              <line x1="9" y1="15" x2="15" y2="15" />
            </svg>
          </div>
          <h3>Sin gastos registrados</h3>
          <p>Importa un archivo CSV o Excel para comenzar a clasificar tus gastos automáticamente.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-container">
      <div className="table-header">
        <h3>
          <svg className="icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="8" y1="6" x2="21" y2="6" />
            <line x1="8" y1="12" x2="21" y2="12" />
            <line x1="8" y1="18" x2="21" y2="18" />
            <line x1="3" y1="6" x2="3.01" y2="6" />
            <line x1="3" y1="12" x2="3.01" y2="12" />
            <line x1="3" y1="18" x2="3.01" y2="18" />
          </svg>
          Movimientos
        </h3>
        <span className="count">{expenses.length} registros</span>
      </div>

      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Descripción</th>
              <th style={{ textAlign: 'right' }}>Importe</th>
              <th>Categoría</th>
              <th style={{ width: '50px' }}></th>
            </tr>
          </thead>
          <tbody>
            {expenses.map((expense) => (
              <tr key={expense.id} className={expense.is_corrected ? 'corrected' : ''}>
                <td className="date-cell">{formatDate(expense.date)}</td>
                <td className="description-cell" title={expense.description}>
                  {expense.description}
                </td>
                <td className={`amount-cell ${expense.amount >= 0 ? 'income' : 'expense'}`}>
                  {formatAmount(expense.amount)}
                </td>
                <td>
                  {editingId === expense.id ? (
                    <select
                      className="category-select"
                      autoFocus
                      defaultValue={expense.category || ''}
                      onChange={(e) => handleCategoryChange(expense.id, e.target.value)}
                      onBlur={() => setEditingId(null)}
                    >
                      <option value="">Seleccionar...</option>
                      {CATEGORIES.map((cat) => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  ) : (
                    <span
                      className="category-badge"
                      onClick={() => setEditingId(expense.id)}
                    >
                      {expense.category || 'Sin categoría'}
                      <svg className="edit-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                      </svg>
                    </span>
                  )}
                </td>
                <td>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(expense.id)}
                    title="Eliminar"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="3 6 5 6 21 6" />
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
