"""Flatten a PDF using pypdf.

What 'flatten' means here:
- Remove the AcroForm dictionary (interactive form fields)
- Remove page-level annotations (comments, highlights, fillable fields)
- Keep all VISUAL content (text, images, signatures rendered as images)

For a PDF with an ink-signature IMAGE (not a cryptographic DSC), this is safe
and produces a clean, locked-down page that embeds cleanly via \\includepdf.

For a PDF with a cryptographic DSC signature, this would invalidate the
signature -- DO NOT use this on a DSC-signed PDF. Use the original signed PDF
directly with \\includepdf instead.
"""
from __future__ import annotations

import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject


def flatten(src_path: Path, dst_path: Path) -> None:
    reader = PdfReader(str(src_path))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Strip AcroForm from the document root if present
    root = writer._root_object
    if NameObject("/AcroForm") in root:
        del root[NameObject("/AcroForm")]
        print("  removed /AcroForm from document root")

    # Strip per-page annotations
    annots_removed = 0
    for page in writer.pages:
        if NameObject("/Annots") in page:
            del page[NameObject("/Annots")]
            annots_removed += 1
    if annots_removed:
        print(f"  removed /Annots from {annots_removed} page(s)")

    # Set producer metadata so downstream tools see it as the flattened version
    writer.add_metadata({
        "/Producer": "pypdf flatten (interactive forms removed)",
        "/Title": "Internship Certificate (flattened)",
        "/Creator": "VibeTensor Private Limited",
    })

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_path, "wb") as f:
        writer.write(f)
    print(f"  wrote {dst_path} ({dst_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: flatten_pdf.py <input.pdf> <output.pdf>")
        sys.exit(1)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    print(f"Flattening: {src}")
    flatten(src, dst)
    print("Done.")
