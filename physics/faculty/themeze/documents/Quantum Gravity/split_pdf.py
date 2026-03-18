#!/usr/bin/env python3
import os
import sys
import subprocess
import venv
import shutil
import tempfile

# nom du package nécessaire
REQUIREMENTS = ["pymupdf"]

def in_venv():
    return sys.prefix != sys.base_prefix


def bootstrap():
    temp_dir = tempfile.mkdtemp(prefix="pdf_split_env_")

    print("Creating temporary venv:", temp_dir)

    venv.create(temp_dir, with_pip=True)

    if sys.platform == "win32":
        python_bin = os.path.join(temp_dir, "Scripts", "python")
    else:
        python_bin = os.path.join(temp_dir, "bin", "python")

    print("Installing dependencies...")
    subprocess.check_call([python_bin, "-m", "pip", "install"] + REQUIREMENTS)

    print("Relaunching script inside venv...")
    subprocess.check_call([python_bin] + sys.argv)

    print("Cleaning temporary environment...")
    shutil.rmtree(temp_dir)

    sys.exit()


# --------------------------------------------------
# Bootstrap
# --------------------------------------------------

if not in_venv():
    bootstrap()

# --------------------------------------------------
# CODE PRINCIPAL (dans le venv)
# --------------------------------------------------

import fitz
import math

SIZES = {
    "A4": (595, 842),
    "A5": (420, 595)
}

def split_pdf(
    input_pdf,
    output_pdf,
    target="A4",
    margin=(0,0,0,0),
    padding=(0,0,0,0),
    overlap=0
):

    target_w, target_h = SIZES[target]

    margin_top, margin_bottom, margin_left, margin_right = margin
    pad_top, pad_bottom, pad_left, pad_right = padding

    doc = fitz.open(input_pdf)
    new_doc = fitz.open()

    for page in doc:

        rect = page.rect

        src_x0 = pad_left
        src_y0 = pad_top
        src_x1 = rect.width - pad_right
        src_y1 = rect.height - pad_bottom

        src_w = src_x1 - src_x0
        src_h = src_y1 - src_y0

        usable_w = target_w - margin_left - margin_right
        usable_h = target_h - margin_top - margin_bottom

        scale = usable_w / src_w

        step = usable_h - overlap
        step_src = step / scale
        page_height_src = usable_h / scale

        y = src_y0

        while y < src_y1:

            remaining = src_y1 - y

            # si la tranche restante est trop petite → on arrête
            if remaining < overlap:
                break

            y0 = y
            y1 = min(y + page_height_src, src_y1)

            clip = fitz.Rect(src_x0, y0, src_x1, y1)

            new_page = new_doc.new_page(width=target_w, height=target_h)

            dest = fitz.Rect(
                margin_left,
                margin_top,
                target_w - margin_right,
                target_h - margin_bottom
            )

            new_page.show_pdf_page(
                dest,
                doc,
                page.number,
                clip=clip
            )

            y += step_src

    new_doc.save(output_pdf)
    doc.close()
    new_doc.close()


split_pdf(
    "Gravitation quantique.pdf",
    "remarkable_A4.pdf",
    target="A4",
    margin=(50,50,40,40),
    padding=(0,0,0,0),
    overlap=80
)