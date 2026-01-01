from datetime import date
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.expense import Expense, Correction
from app.schemas.expense import (
    ExpenseResponse,
    ExpenseUpdate,
    ImportResponse,
    KPIResponse,
)
from app.services.classifier import classify_with_ai
from app.services.column_detector import detect_columns
from app.services.parsers import parse_file

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/import", response_model=ImportResponse)
async def import_expenses(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Import expenses from CSV or Excel file."""
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    try:
        df = parse_file(file.file, file.filename)
    except ValueError as e:
        raise HTTPException(400, str(e))

    columns = detect_columns(df)
    if not columns.date or not columns.description or not columns.amount:
        raise HTTPException(
            400,
            f"Could not detect required columns. Found: date={columns.date}, "
            f"description={columns.description}, amount={columns.amount}",
        )

    # Get existing corrections for AI context
    corrections_result = await db.execute(
        select(Correction).order_by(Correction.usage_count.desc()).limit(50)
    )
    corrections = [
        {"pattern": c.description_pattern, "category": c.category, "subcategory": c.subcategory}
        for c in corrections_result.scalars().all()
    ]

    expenses = []
    for _, row in df.iterrows():
        # Skip rows with NaN values in required columns
        if pd.isna(row[columns.date]) or pd.isna(row[columns.description]) or pd.isna(row[columns.amount]):
            continue

        try:
            expense_date = pd.to_datetime(row[columns.date], dayfirst=True).date()
        except Exception:
            continue

        description = str(row[columns.description]).strip()
        # Skip if description is empty or just "nan"
        if not description or description.lower() == "nan":
            continue

        try:
            amount_str = str(row[columns.amount]).replace(",", ".").replace("€", "").strip()
            amount = float(amount_str)
            # Skip NaN amounts
            if pd.isna(amount):
                continue
        except (ValueError, TypeError):
            continue

        # Classify with AI
        classification = await classify_with_ai(description, amount, corrections)

        expense = Expense(
            date=expense_date,
            description=description,
            amount=amount,
            category=classification.category,
            subcategory=classification.subcategory,
        )
        db.add(expense)
        expenses.append(expense)

    await db.commit()

    for expense in expenses:
        await db.refresh(expense)

    return ImportResponse(
        imported=len(expenses),
        expenses=[ExpenseResponse.model_validate(e) for e in expenses],
    )


@router.get("", response_model=list[ExpenseResponse])
async def list_expenses(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=5000),
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    """List expenses with optional filters."""
    query = select(Expense).order_by(Expense.date.desc())

    if category:
        query = query.where(Expense.category == category)
    if start_date:
        query = query.where(Expense.date >= start_date)
    if end_date:
        query = query.where(Expense.date <= end_date)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)

    return [ExpenseResponse.model_validate(e) for e in result.scalars().all()]


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    update: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update expense category (saves correction for learning)."""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(404, "Expense not found")

    if update.category:
        expense.category = update.category
        expense.is_corrected = True

        # Save correction for future learning
        pattern = expense.description[:100].lower()
        existing = await db.execute(
            select(Correction).where(Correction.description_pattern == pattern)
        )
        correction = existing.scalar_one_or_none()

        if correction:
            correction.category = update.category
            correction.subcategory = update.subcategory
            correction.usage_count += 1
        else:
            correction = Correction(
                description_pattern=pattern,
                category=update.category,
                subcategory=update.subcategory,
            )
            db.add(correction)

    if update.subcategory:
        expense.subcategory = update.subcategory

    await db.commit()
    await db.refresh(expense)

    return ExpenseResponse.model_validate(expense)


@router.get("/kpis", response_model=KPIResponse)
async def get_kpis(
    db: AsyncSession = Depends(get_db),
    year: int | None = None,
    month: int | None = None,
):
    """Get expense KPIs for a given period."""
    query = select(Expense).where(Expense.amount < 0)  # Only expenses, not income

    if year:
        query = query.where(extract("year", Expense.date) == year)
    if month:
        query = query.where(extract("month", Expense.date) == month)

    result = await db.execute(query)
    expenses = result.scalars().all()

    total = sum(abs(e.amount) for e in expenses)

    by_category: dict[str, float] = {}
    for e in expenses:
        cat = e.category or "Sin categoría"
        by_category[cat] = by_category.get(cat, 0) + abs(e.amount)

    by_month: dict[str, float] = {}
    for e in expenses:
        key = e.date.strftime("%Y-%m")
        by_month[key] = by_month.get(key, 0) + abs(e.amount)

    return KPIResponse(
        total=round(total, 2),
        by_category={k: round(v, 2) for k, v in sorted(by_category.items())},
        by_month={k: round(v, 2) for k, v in sorted(by_month.items())},
        count=len(expenses),
    )


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an expense."""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(404, "Expense not found")

    await db.delete(expense)
    await db.commit()

    return {"deleted": expense_id}
