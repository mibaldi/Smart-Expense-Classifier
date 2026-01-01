from io import BytesIO
from typing import BinaryIO

import pandas as pd


def parse_csv(file: BinaryIO, filename: str = "") -> pd.DataFrame:
    """Parse a CSV file and return a DataFrame."""
    content = file.read()

    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            df = pd.read_csv(
                BytesIO(content),
                encoding=encoding,
                sep=None,
                engine="python",
            )
            if not df.empty:
                return df
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            continue

    raise ValueError(f"Could not parse CSV file: {filename}")


def parse_excel(file: BinaryIO, filename: str = "") -> pd.DataFrame:
    """Parse an Excel file and return a DataFrame."""
    content = file.read()

    try:
        df = pd.read_excel(BytesIO(content), engine="openpyxl")
        if df.empty:
            raise ValueError(f"Empty Excel file: {filename}")
        return df
    except Exception as e:
        raise ValueError(f"Could not parse Excel file: {filename}. Error: {e}")


def parse_file(file: BinaryIO, filename: str) -> pd.DataFrame:
    """Parse a file based on its extension."""
    ext = filename.lower().split(".")[-1]

    if ext == "csv":
        return parse_csv(file, filename)
    elif ext in ("xlsx", "xls"):
        return parse_excel(file, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
