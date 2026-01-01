from datetime import date, datetime
from pydantic import BaseModel


class ExpenseBase(BaseModel):
    date: date
    description: str
    amount: float
    category: str | None = None
    subcategory: str | None = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category: str | None = None
    subcategory: str | None = None


class ExpenseResponse(ExpenseBase):
    id: int
    is_corrected: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ImportResponse(BaseModel):
    imported: int
    expenses: list[ExpenseResponse]


class KPIResponse(BaseModel):
    total: float
    by_category: dict[str, float]
    by_month: dict[str, float]
    count: int
