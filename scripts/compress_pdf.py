import os
import subprocess
from pathlib import Path
import math

# ==============================
# ⚙️ CONFIGURATION
# ==============================

# Seuil en MB
SIZE_LIMIT_MB = 100

# Nombre max de passes de compression
MAX_PASSES = 3

# Stop si le gain est trop faible (<10%)
MIN_GAIN_RATIO = 0.9

# Niveau de compression :
# /screen   -> très compressé (faible qualité)
# /ebook    -> bon compromis
# /printer  -> haute qualité
PDF_QUALITY = "/screen"


# ==============================
# 🧠 UTILITAIRES
# ==============================

def get_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)


def get_pdf_pages(pdf):
    """Retourne le nombre de pages via pdfinfo"""
    result = subprocess.run(
        ["pdfinfo", str(pdf)],
        capture_output=True,
        text=True
    )
    for line in result.stdout.splitlines():
        if "Pages:" in line:
            return int(line.split(":")[1].strip())
    return 1


def compress_once(input_path, output_path):
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={PDF_QUALITY}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        "-dDownsampleColorImages=true",
        "-dColorImageResolution=100",
        str(input_path)
    ]
    subprocess.run(cmd, check=True)


# ==============================
# ✂️ DECOUPE INTELLIGENTE
# ==============================

def split_pdf(pdf, replace=False):
    size = get_size_mb(pdf)
    pages = get_pdf_pages(pdf)

    parts = math.ceil(size / SIZE_LIMIT_MB * 2 )

    print(f"\n✂️ Découpe de {pdf}")
    print(f"   Taille: {size:.2f} MB | Pages: {pages}")
    print(f"   → {parts} morceaux")

    pages_per_part = math.ceil(pages / parts)

    temp_dir = pdf.parent / f"tmp_split_{pdf.stem}"
    temp_dir.mkdir(exist_ok=True)

    for i in range(parts):
        start = i * pages_per_part + 1
        end = min((i + 1) * pages_per_part, pages)

        percent_start = int((start / pages) * 100)
        percent_end = int((end / pages) * 100)

        # 1️⃣ extraire pages individuelles
        temp_pattern = temp_dir / f"page_%04d.pdf"

        cmd_extract = [
            "pdfseparate",
            "-f", str(start),
            "-l", str(end),
            str(pdf),
            str(temp_pattern)
        ]
        subprocess.run(cmd_extract, check=True)

        # 2️⃣ récupérer les fichiers générés
        pages_files = sorted(temp_dir.glob("page_*.pdf"))

        # 3️⃣ fusionner
        output = pdf.with_name(
            f"{pdf.stem}_{percent_start}-{percent_end}pct.pdf"
        )

        cmd_merge = ["pdfunite"] + [str(p) for p in pages_files] + [str(output)]
        subprocess.run(cmd_merge, check=True)

        print(f"   📄 {output} ({start}-{end})")

        # 4️⃣ cleanup pages
        for p in pages_files:
            p.unlink()

    temp_dir.rmdir()

    print("   ✅ Découpe terminée")

    # 🔥 suppression si demandé
    if replace:
        print("   🗑️ Suppression de l'original")
        pdf.unlink()


# ==============================
# 🔥 COMPRESSION INTELLIGENTE
# ==============================

def smart_compress(pdf, replace=False):
    original_size = get_size_mb(pdf)
    current_file = pdf

    print(f"\n📄 {pdf}")
    print(f"   Taille initiale: {original_size:.2f} MB")

    for i in range(MAX_PASSES):
        temp_file = pdf.with_name(pdf.stem + f"_tmp_{i}.pdf")

        compress_once(current_file, temp_file)

        new_size = get_size_mb(temp_file)
        old_size = get_size_mb(current_file)

        print(f"   Pass {i+1}: {new_size:.2f} MB")

        if new_size < SIZE_LIMIT_MB:
            print("   ✅ Sous 100MB atteint")

            if replace:
                if current_file != pdf:
                    current_file.unlink()
                temp_file.rename(pdf)
            return True

        if new_size > old_size * MIN_GAIN_RATIO:
            print("   ⚠️ Gain trop faible → arrêt")
            temp_file.unlink()
            break

        if current_file != pdf:
            current_file.unlink()

        current_file = temp_file

    print("   ❌ Impossible de descendre sous 100MB")

    if current_file != pdf and current_file.exists():
        current_file.unlink()

    return False


# ==============================
# 🔍 RECHERCHE DES PDF
# ==============================

def find_pdfs(directory, recursive):
    directory = Path(directory)
    if recursive:
        return list(directory.rglob("*.pdf"))  # 🔁 récursif
    else:
        return list(directory.glob("*.pdf"))   # 📁 seulement dossier courant


# ==============================
# 📂 TRAITEMENT
# ==============================

def process_directory(directory, replace=False, recursive=False, do_compress=True, do_split=False):
    pdfs = find_pdfs(directory, recursive)

    for pdf in pdfs:
        if not pdf.exists():
            continue

        size = get_size_mb(pdf)

        if size > SIZE_LIMIT_MB:
            success = False

            if do_compress:
                success = smart_compress(pdf, replace=replace)

            # Si demandé OU compression insuffisante
            if do_split or (do_compress and not success):
                split_pdf(pdf, replace=replace)


# ==============================
# 🚀 MAIN
# ==============================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Compresser ou découper les PDF > 100MB"
    )

    parser.add_argument("directory")

    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--recursive", action="store_true")

    parser.add_argument("--quality", choices=["screen", "ebook", "printer"],
                        default="screen")

    parser.add_argument("--compress", action="store_true",
                        help="Activer compression")

    parser.add_argument("--split", action="store_true",
                        help="Activer découpe")

    args = parser.parse_args()

    global PDF_QUALITY
    PDF_QUALITY = f"/{args.quality}"

    # 🔥 logique des options
    do_compress = args.compress or not args.split
    do_split = args.split

    process_directory(
        args.directory,
        replace=args.replace,
        recursive=args.recursive,
        do_compress=do_compress,
        do_split=do_split
    )


if __name__ == "__main__":
    main()