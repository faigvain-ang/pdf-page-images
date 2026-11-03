# PDF Page Images

[Español](README.es.md) · [English guides](https://pdf.findfindata.com/) · [Guías en español](https://pdf.findfindata.com/es/)

A Python 3.11+ command-line tool that renders pages from a local PDF to PNG or JPEG. Select individual pages, ranges, or the entire document. Rendering runs on your computer: no server, account, API key, upload, or backend is used by this script.

## Install

```sh
git clone https://github.com/faigvain-ang/pdf-page-images.git
cd pdf-page-images
python -m venv .venv
```

Activate the environment in PowerShell on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or in a macOS/Linux shell:

```sh
source .venv/bin/activate
```

Then install the pinned runtime dependencies:

```sh
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` instead of `python` in the install and run commands. The script needs no installation as a package. Dependencies are `pypdfium2==4.30.0` and `Pillow==11.1.0`; Python 3.13.11 on Windows was used for the included tests. Installation downloads third-party packages; conversion itself makes no network requests. A compatible PDFium wheel is required for your platform.

## Export selected pages

The repository includes `examples/statement.pdf`, a synthetic three-page document with no real personal or financial information.

```sh
python pdf_page_images.py examples/statement.pdf --pages 1,3 --dpi 144 --format png --output-dir out
```

Output:

```text
out/statement-page-001.png
out/statement-page-003.png
```

Numbers refer to the **source PDF page**, not the order of exported files. Page numbers are 1-based. The sample has a 612 × 792 point MediaBox on all three pages. At 144 DPI, pages 1 and 2 produce 1224 × 1584 pixels. Page 3 has a built-in clockwise 90° rotation and produces 1584 × 1224 pixels; the tool respects that rotation.

### Ranges and JPEG

```sh
python pdf_page_images.py examples/statement.pdf --pages 1-2 --dpi 144 --format jpeg --output-dir jpg-out
```

Produces `statement-page-001.jpg` and `statement-page-002.jpg`. Both `jpeg` and `jpg` are accepted format names. JPEG quality is 95; PNG is lossless. Both formats use an opaque white background and RGB color.

### All pages

```sh
python pdf_page_images.py examples/statement.pdf --all --output-dir all-out
python pdf_page_images.py examples/statement.pdf --output-dir another-out
```

Omitting both `--pages` and `--all` also exports every page. Defaults: 144 DPI, PNG, and `out/`. `--all` and `--pages` cannot be used together. A selection such as `3,1-2,2` exports pages 3, 1, and 2 once each, in that order. Output names use at least three digits, expanding naturally past page 999.

## Errors and limits

- Rejects page 0, out-of-bounds pages, descending ranges, malformed selections, invalid PDFs, and missing files. Errors use exit status 2; successful exports use 0 and print their output paths.
- Rejects encrypted/password-protected documents, including documents that open with an empty password. There is no password option in this version.
- Existing destination images are not overwritten. Choose a new output directory or remove unwanted output files yourself. Selection and name collisions are checked before rendering; a later I/O/render failure can leave earlier images in the output directory.
- DPI must be a positive finite number. Larger DPI uses more memory; the tool renders one page at a time but does not impose a memory limit or sandbox the PDF engine. Only process documents you trust.
- Renders visible pages; it does not extract original embedded images. PDF rendering may vary with fonts and document features. Interactive behavior is not preserved.
- **No OCR and no redaction.** Exporting an image is not a secure redaction workflow. Anything still visible on the page remains visible in the image.
- Images do **not** retain PDF digital signatures, signature validity, selectable text, searchable text layers, links, or editable form fields. A rendered signature appearance is only pixels, not a valid digital signature.
- The source PDF is opened for reading and is never rewritten. You remain responsible for handling sensitive source documents and exported images on your own computer.

## Reproduce the sample and tests

No PDF-generation or test package is needed beyond the runtime dependencies. The sample generator uses Python's standard library and writes a valid PDF with an xref table. Its optional legacy encryption code exists only to create rejection-test fixtures, not to secure documents.

```sh
python examples/make_sample.py
python tests/test_pdf_page_images.py
```

The 11 test methods cover actual PDF reading/rendering, PNG/JPEG decoding, page-to-filename mapping, 144-DPI dimensions, intrinsic rotation, white background, ranges, all-pages defaults, invalid inputs, password rejection, no-overwrite behavior, and unchanged input bytes. Test files live temporarily under the repository's ignored `tmp/` directory and are removed after each test.

## Maintenance and related product

This repository is maintained under the GitHub account **faigvain-ang** by the same maintenance team as [KomoPDF](https://komopdf.com/). It is an affiliated open-source companion, not an independent third-party recommendation or a copy of KomoPDF's implementation. KomoPDF is a related PDF editing product; this repository only provides the local page-image CLI described above. Using it does not require visiting or signing up for KomoPDF.

## License

Original code, documentation, and synthetic examples are available under the [MIT License](LICENSE). Dependencies have separate licenses; see [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
