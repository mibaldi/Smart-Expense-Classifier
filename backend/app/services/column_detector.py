import re
from dataclasses import dataclass

import pandas as pd

DATE_PATTERNS = [
    "fecha", "date", "f.valor", "f.operacion", "fecha_operacion",
    "fecha_valor", "f. valor", "f. operacion", "data",
]

DESCRIPTION_PATTERNS = [
    "concepto", "descripcion", "description", "detalle", "movimiento",
    "comercio", "beneficiario", "pagador", "texto", "referencia",
]

AMOUNT_PATTERNS = [
    "importe", "cantidad", "amount", "monto", "valor", "total",
    "cargo", "abono", "saldo", "euros", "eur",
]


@dataclass
class DetectedColumns:
    date: str | None = None
    description: str | None = None
    amount: str | None = None


def _normalize(text: str) -> str:
    """Normalize column name for matching."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _find_column(columns: list[str], patterns: list[str]) -> str | None:
    """Find a column matching any of the patterns."""
    normalized_cols = {_normalize(col): col for col in columns}

    for pattern in patterns:
        norm_pattern = _normalize(pattern)
        for norm_col, original_col in normalized_cols.items():
            if norm_pattern in norm_col or norm_col in norm_pattern:
                return original_col
    return None


def _detect_by_content(df: pd.DataFrame, detected: DetectedColumns) -> DetectedColumns:
    """Detect columns by analyzing their content."""
    for col in df.columns:
        if col in (detected.date, detected.description, detected.amount):
            continue

        sample = df[col].dropna().head(100)
        if sample.empty:
            continue

        # Detect date by trying to parse
        if detected.date is None:
            try:
                parsed = pd.to_datetime(sample, errors="coerce", dayfirst=True)
                if parsed.notna().sum() > len(sample) * 0.8:
                    detected.date = col
                    continue
            except Exception:
                pass

        # Detect amount by checking numeric values
        if detected.amount is None:
            if pd.api.types.is_numeric_dtype(sample):
                detected.amount = col
                continue
            try:
                cleaned = sample.astype(str).str.replace(r"[€$,\s]", "", regex=True)
                cleaned = cleaned.str.replace(",", ".")
                numeric = pd.to_numeric(cleaned, errors="coerce")
                if numeric.notna().sum() > len(sample) * 0.8:
                    detected.amount = col
                    continue
            except Exception:
                pass

        # Detect description by checking string length
        if detected.description is None:
            if sample.astype(str).str.len().mean() > 10:
                detected.description = col

    return detected


def detect_columns(df: pd.DataFrame) -> DetectedColumns:
    """Detect date, description, and amount columns in a DataFrame."""
    columns = list(df.columns)

    detected = DetectedColumns(
        date=_find_column(columns, DATE_PATTERNS),
        description=_find_column(columns, DESCRIPTION_PATTERNS),
        amount=_find_column(columns, AMOUNT_PATTERNS),
    )

    # If any column wasn't found by name, try content analysis
    if None in (detected.date, detected.description, detected.amount):
        detected = _detect_by_content(df, detected)

    return detected
