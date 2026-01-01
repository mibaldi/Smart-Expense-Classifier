import type { KPIs } from '../types/expense';

interface Props {
  kpis: KPIs | null;
}

export function KPICards({ kpis }: Props) {
  if (!kpis) return null;

  const formatAmount = (amount: number) => {
    return amount.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' });
  };

  const topCategories = Object.entries(kpis.by_category)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  return (
    <div className="kpi-cards">
      <div className="kpi-card">
        <div className="icon-wrapper">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="1" x2="12" y2="23" />
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
        </div>
        <span className="kpi-label">Total Gastos</span>
        <span className="kpi-value">{formatAmount(kpis.total)}</span>
      </div>

      <div className="kpi-card">
        <div className="icon-wrapper">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
          </svg>
        </div>
        <span className="kpi-label">Movimientos</span>
        <span className="kpi-value">{kpis.count}</span>
      </div>

      <div className="kpi-card">
        <div className="icon-wrapper">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 20V10" />
            <path d="M18 20V4" />
            <path d="M6 20v-4" />
          </svg>
        </div>
        <span className="kpi-label">Media / Movimiento</span>
        <span className="kpi-value">
          {kpis.count > 0 ? formatAmount(kpis.total / kpis.count) : '€0'}
        </span>
      </div>

      <div className="kpi-card top-categories">
        <div className="icon-wrapper">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
          </svg>
        </div>
        <span className="kpi-label">Top Categorías</span>
        <div className="category-list">
          {topCategories.map(([cat, amount]) => (
            <div key={cat} className="category-item">
              <span className="name">{cat}</span>
              <span className="amount">{formatAmount(amount)}</span>
            </div>
          ))}
          {topCategories.length === 0 && (
            <div className="category-item">
              <span className="name" style={{ color: 'var(--color-text-muted)' }}>Sin datos</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
