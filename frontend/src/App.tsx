import { useState, useEffect, useCallback } from 'react';
import { FileUpload } from './components/FileUpload';
import { ExpenseTable } from './components/ExpenseTable';
import { KPICards } from './components/KPICards';
import { Charts } from './components/Charts';
import { getExpenses, getKPIs } from './api/expenses';
import type { Expense, KPIs } from './types/expense';
import './App.css';

function App() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [expensesData, kpisData] = await Promise.all([
        getExpenses(),
        getKPIs(),
      ]);
      setExpenses(expensesData);
      setKpis(kpisData);
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <div className="logo-icon">$</div>
          <div>
            <h1>Smart Expense</h1>
            <span className="subtitle">Clasificador inteligente de gastos</span>
          </div>
        </div>
        <div className="header-badge">
          <span className="dot"></span>
          IA Activa
        </div>
      </header>

      <main className="app-main">
        <FileUpload onImport={loadData} />

        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Cargando datos...</p>
          </div>
        ) : (
          <>
            <section className="kpi-section">
              <KPICards kpis={kpis} />
            </section>

            <section className="charts-section">
              <Charts kpis={kpis} />
            </section>

            <section className="table-section">
              <ExpenseTable expenses={expenses} onUpdate={loadData} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
