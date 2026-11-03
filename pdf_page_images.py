#!/usr/bin/env python3
"""Render local PDF pages as white-background PNG or JPEG images."""

import argparse
import math
from pathlib import Path
import re

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_raw


class ConversionError(ValueError):
    """A document or conversion option cannot be processed."""


def parse_pages(selection: str | None, page_count: int) -> list[int]:
    """Return unique 1-based page numbers in the requested order."""
    if selection is None:
        return list(range(1, page_count + 1))
    pages = []
    seen = set()
    for part in selection.split(","):
        match = re.fullmatch(r"\s*([0-9]+)(?:\s*-\s*([0-9]+))?\s*", part)
        if not match:
            raise ConversionError("Invalid pages: use 1-based numbers/ranges, e.g. 1,3-5.")
        start = int(match[1])
        end = int(match[2]) if match[2] else start
        if start < 1 or end > page_count or start > page_count:
            raise ConversionError(f"Page selection is out of bounds: document has {page_count} pages.")
        if end < start:
            raise ConversionError(f"Invalid descending page range: {part.strip()}.")
        for number in range(start, end + 1):
            if number not in seen:
                pages.append(number)
                seen.add(number)
    return pages


def positive_dpi(value: str) -> float:
    try:
        dpi = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("DPI must be a positive finite number.") from exc
    if not math.isfinite(dpi) or dpi <= 0:
        raise argparse.ArgumentTypeError("DPI must be a positive finite number.")
    return dpi


def convert_pdf(
    input_pdf: Path,
    output_dir: Path,
    *,
    pages: str | None = None,
    dpi: float = 144,
    image_format: str = "png",
) -> list[Path]:
    """Render selected pages without changing the source PDF; never overwrite images."""
    if not math.isfinite(dpi) or dpi <= 0:
        raise ConversionError("DPI must be a positive finite number.")
    if image_format not in {"png", "jpeg", "jpg"}:
        raise ConversionError("Format must be png, jpeg, or jpg.")
    if not input_pdf.is_file():
        raise ConversionError(f"Input PDF does not exist or is not a file: {input_pdf}")
    try:
        document = pdfium.PdfDocument(input_pdf)
    except pdfium.PdfiumError as exc:
        if pdfium_raw.FPDF_GetLastError() == pdfium_raw.FPDF_ERR_PASSWORD:
            raise ConversionError("Password-protected PDFs are not supported.") from exc
        raise ConversionError(f"Cannot open PDF: {exc}") from exc

    try:
        # Reject even encryption that accepts an empty user password.
        if pdfium_raw.FPDF_GetSecurityHandlerRevision(document) >= 0:
            raise ConversionError("Password-protected PDFs are not supported.")
        selected = parse_pages(pages, len(document))
        if not selected:
            raise ConversionError("PDF contains no pages.")
        extension = "png" if image_format == "png" else "jpg"
        outputs = [output_dir / f"{input_pdf.stem}-page-{number:03d}.{extension}" for number in selected]
        for target in outputs:
            if target.exists():
                raise ConversionError(f"Output already exists (not overwritten): {target}")
        output_dir.mkdir(parents=True, exist_ok=True)
        for number, target in zip(selected, outputs):
            page = document[number - 1]
            try:
                bitmap = page.render(scale=dpi / 72, fill_color=(255, 255, 255, 255))
                try:
                    with bitmap.to_pil() as rendered, rendered.convert("RGB") as image:
                        options = {"quality": 95} if extension == "jpg" else {}
                        image.save(target, format="PNG" if extension == "png" else "JPEG", dpi=(dpi, dpi), **options)
                finally:
                    bitmap.close()
            finally:
                page.close()
        return outputs
    finally:
        document.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=Path, help="Local source PDF (never modified).")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--pages", help="1-based page numbers/ranges, e.g. 1,3-5; default: all pages.")
    selection.add_argument("--all", action="store_true", help="Render every page (also the default).")
    parser.add_argument("--dpi", type=positive_dpi, default=144, help="Resolution in dots per inch (default: 144).")
    parser.add_argument("--format", choices=("png", "jpeg", "jpg"), default="png", dest="image_format")
    parser.add_argument("--output-dir", type=Path, default=Path("out"), help="Image directory (default: out).")
    args = parser.parse_args(argv)
    try:
        outputs = convert_pdf(args.input_pdf, args.output_dir, pages=args.pages, dpi=args.dpi, image_format=args.image_format)
    except (ConversionError, OSError, pdfium.PdfiumError) as exc:
        parser.error(str(exc))
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
