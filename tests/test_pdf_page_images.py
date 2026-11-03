"""Core integration tests. Run this file directly; no test dependencies required."""

from contextlib import closing
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image
import pypdfium2 as pdfium

from examples.make_sample import build_pdf
from pdf_page_images import ConversionError, convert_pdf, parse_pages


class PdfPageImagesTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        self.work = tempfile.TemporaryDirectory(dir=ROOT / "tmp")
        self.addCleanup(self.work.cleanup)
        self.folder = Path(self.work.name)
        self.source = self.folder / "statement.pdf"
        self.source.write_bytes(build_pdf())
        self.output = self.folder / "out"

    def cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(ROOT / "pdf_page_images.py"), str(self.source), *arguments, "--output-dir", str(self.output)],
            capture_output=True, text=True, cwd=ROOT, check=False,
        )

    def test_synthetic_pdf_is_readable(self):
        with closing(pdfium.PdfDocument(self.source)) as document:
            self.assertEqual(len(document), 3)
            page = document[0]
            try:
                self.assertEqual(page.get_size(), (612.0, 792.0))
                text = page.get_textpage()
                try:
                    self.assertIn("Synthetic statement - page 1", text.get_text_range())
                finally:
                    text.close()
            finally:
                page.close()

    def test_png_cli_selection_dimensions_rotation_and_input_unchanged(self):
        before = hashlib.sha256(self.source.read_bytes()).digest()
        result = self.cli("--pages", "1,3", "--dpi", "144", "--format", "png")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sorted(p.name for p in self.output.iterdir()), ["statement-page-001.png", "statement-page-003.png"])
        for number, size, point, color in [
            (1, (1224, 1584), (200, 1300), (255, 0, 0)),
            (3, (1584, 1224), (200, 200), (0, 0, 255)),
        ]:
            with Image.open(self.output / f"statement-page-{number:03d}.png") as image:
                image.load()
                self.assertEqual(image.format, "PNG")
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(image.size, size)
                self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))
                self.assertEqual(image.getpixel(point), color)
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).digest(), before)

    def test_jpeg_readable_white_background_and_dpi_scaling(self):
        result = self.cli("--pages", "2", "--dpi", "72", "--format", "jpeg")
        self.assertEqual(result.returncode, 0, result.stderr)
        with Image.open(self.output / "statement-page-002.jpg") as image:
            image.load()
            self.assertEqual(image.format, "JPEG")
            self.assertEqual(image.size, (612, 792))
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))
            r, g, b = image.getpixel((100, 650))
            self.assertLess(r, 5)
            self.assertGreater(g, 140)
            self.assertLess(b, 5)

    def test_all_and_omitted_pages(self):
        for option in ([], ["--all"]):
            with self.subTest(option=option):
                self.output = self.folder / ("explicit" if option else "default")
                result = self.cli(*option, "--dpi", "36")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(list(self.output.glob("*.png"))), 3)

    def test_range_order_and_duplicates(self):
        self.assertEqual(parse_pages("3, 1-2,2", 3), [3, 1, 2])
        outputs = convert_pdf(self.source, self.output, pages="3,1-2", dpi=36)
        self.assertEqual([p.name for p in outputs], [f"statement-page-{n:03d}.png" for n in (3, 1, 2)])

    def test_invalid_selections_do_not_write_images(self):
        for selection in ("0", "4", "1-4", "3-2", "1,,3", "", "-1", "1-", "a", "1.5", "1-2-3"):
            with self.subTest(selection=selection):
                result = self.cli("--pages", selection)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(self.output.exists())

    def test_pages_and_all_are_mutually_exclusive(self):
        self.assertEqual(self.cli("--pages", "1", "--all").returncode, 2)

    def test_invalid_dpi(self):
        for value in ("0", "-1", "nan", "inf", "bad"):
            with self.subTest(value=value):
                self.assertEqual(self.cli("--dpi", value).returncode, 2)

    def test_password_and_empty_password_encryption_rejected(self):
        for password in ("test-only", ""):
            with self.subTest(empty_password=not password):
                self.source.write_bytes(build_pdf(password=password))
                # Establish this is a genuinely readable encrypted PDF, not malformed input.
                with closing(pdfium.PdfDocument(self.source, password=password)) as document:
                    self.assertEqual(len(document), 3)
                result = self.cli()
                self.assertEqual(result.returncode, 2)
                self.assertIn("Password-protected PDFs are not supported", result.stderr)
                self.assertFalse(self.output.exists())

    def test_invalid_and_missing_input(self):
        self.source.write_bytes(b"not a PDF")
        self.assertEqual(self.cli().returncode, 2)
        self.source.unlink()
        self.assertEqual(self.cli().returncode, 2)

    def test_existing_output_not_overwritten(self):
        self.output.mkdir()
        target = self.output / "statement-page-003.png"
        target.write_bytes(b"keep existing file")
        with self.assertRaisesRegex(ConversionError, "already exists"):
            convert_pdf(self.source, self.output, pages="1,3")
        self.assertEqual(target.read_bytes(), b"keep existing file")
        self.assertFalse((self.output / "statement-page-001.png").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
