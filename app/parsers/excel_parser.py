"""
Excel text extraction for benefit-related spreadsheets.
"""
from __future__ import annotations


def extract_text_from_excel_bytes(data: bytes) -> str:
    """
    Extract text from an Excel workbook given as bytes.
    Flattens all non-empty cell values across all sheets into a single string.
    """
    import io
    from openpyxl import load_workbook  # type: ignore[import]

    wb = load_workbook(io.BytesIO(data), data_only=True)
    parts: list[str] = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                text = str(cell.value).strip()
                if text:
                    parts.append(text)
    return "\n".join(parts).strip()

