import axios from 'axios';
import type { Expense, KPIs, ImportResponse } from '../types/expense';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

export async function importExpenses(file: File): Promise<ImportResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post<ImportResponse>('/expenses/import', formData);
  return data;
}

export async function getExpenses(): Promise<Expense[]> {
  const { data } = await api.get<Expense[]>('/expenses');
  return data;
}

export async function updateExpense(
  id: number,
  update: { category?: string; subcategory?: string }
): Promise<Expense> {
  const { data } = await api.put<Expense>(`/expenses/${id}`, update);
  return data;
}

export async function deleteExpense(id: number): Promise<void> {
  await api.delete(`/expenses/${id}`);
}

export async function getKPIs(year?: number, month?: number): Promise<KPIs> {
  const params = new URLSearchParams();
  if (year) params.append('year', year.toString());
  if (month) params.append('month', month.toString());
  const { data } = await api.get<KPIs>(`/expenses/kpis?${params}`);
  return data;
}
