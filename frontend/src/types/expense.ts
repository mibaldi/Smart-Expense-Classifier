export interface Expense {
  id: number;
  date: string;
  description: string;
  amount: number;
  category: string | null;
  subcategory: string | null;
  is_corrected: boolean;
  created_at: string;
  updated_at: string;
}

export interface KPIs {
  total: number;
  by_category: Record<string, number>;
  by_month: Record<string, number>;
  count: number;
}

export interface ImportResponse {
  imported: number;
  expenses: Expense[];
}
