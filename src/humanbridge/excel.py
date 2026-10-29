"""Stream pinned source workbooks without extracting archive paths to disk."""
from __future__ import annotations

import io
import zipfile
from collections.abc import Iterator
from pathlib import Path

import openpyxl


def rows(asset: Path, member: str | None = None, sheet: str | int = 0) -> Iterator[tuple]:
    """Yield raw worksheet rows, closing the workbook even on parser failure."""
    if member is None:
        source = asset
    else:
        with zipfile.ZipFile(asset) as archive:
            if archive.getinfo(member).file_size > 500_000_000:
                raise ValueError("Workbook member exceeds memory budget")
            source = io.BytesIO(archive.read(member))
    workbook = openpyxl.load_workbook(source, read_only=True, data_only=True)
    try:
        worksheet = workbook.worksheets[sheet] if isinstance(sheet, int) else workbook[sheet]
        yield from worksheet.iter_rows(values_only=True)
    finally:
        workbook.close()


def records(asset: Path, member: str | None = None, sheet: str | int = 0,
            required: tuple[str, ...] = (),
            allowed_duplicates: tuple[str, ...] = ()) -> Iterator[dict]:
    """Locate a header containing every required field; reject ambiguous columns."""
    stream = rows(asset, member, sheet)
    try:
        for _ in range(30):
            header_row = next(stream)
            header = [str(value).strip() if value is not None else "" for value in header_row]
            if required and not set(required).issubset(header):
                continue
            nonempty = [name for name in header if name]
            repeated = {name for name in nonempty if nonempty.count(name) > 1}
            if repeated - set(allowed_duplicates):
                raise ValueError("Duplicate header fields")
            seen: dict[str, int] = {}
            for index, name in enumerate(header):
                seen[name] = seen.get(name, 0) + 1
                if name and seen[name] > 1:
                    header[index] = f"{name}__{seen[name]}"
            for row in stream:
                if any(value is not None for value in row):
                    yield {name: value for name, value in zip(header, row) if name}
            return
    except StopIteration:
        pass
    finally:
        stream.close()
    raise ValueError(f"No expected header found: {required}")


def member_name(asset: Path, filename: str) -> str:
    """Require exactly one matching workbook basename in a source archive."""
    with zipfile.ZipFile(asset) as archive:
        matches = [name for name in archive.namelist() if Path(name).name == filename]
    if len(matches) != 1:
        raise ValueError(f"Expected one {filename}; found {len(matches)}")
    return matches[0]
