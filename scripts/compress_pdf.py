import os
import subprocess
from pathlib import Path
import math

# ==============================
# ⚙️ CONFIGURATION
# ==============================

SIZE_LIMIT_MB = 100           # Taille seuil en MB
MAX_PASSES = 3                # Nombre max de passes de compression
MIN_GAIN_RATIO = 0.9          # Stop si gain trop faible (<10%)
# Niveau de compression :
# /screen   -> très compressé (faible qualité)
# /ebook    -> bon compromis
# /printer  -> haute qualité
PDF_QUALITY = "/ebook"       # /screen, /ebook, /printer

# ==============================
# 🧠 UTILITAIRES
# ==============================

def get_output_dir(pdf):
    """Crée un dossier de sortie au même endroit que le PDF avec le même nom"""
    output_dir = pdf.parent / pdf.stem
    output_dir.mkdir(exist_ok=True)
    return output_dir

def get_size_mb(file_path):
    """Retourne la taille d'un fichier en MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

def get_pdf_pages(pdf):
    """Retourne le nombre de pages d'un PDF via pdfinfo"""
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
    """Compression Ghostscript simple"""
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
# 🧹 GITIGNORE CENTRALISÉ
# ==============================

def update_gitignore(pdf, base_gitignore=None):
    """
    Ajoute le chemin relatif complet du dossier PDF ou PDF généré dans le .gitignore centralisé
    """
    if base_gitignore is None:
        base_gitignore = Path.cwd() / ".gitignore"

    # Chemin relatif complet depuis le dossier courant
    try:
        relative_path = pdf.parent.relative_to(Path.cwd())
    except ValueError:
        # si le PDF est hors du cwd, prendre le chemin absolu
        relative_path = pdf.parent

    # Ajouter un slash à la fin pour ignorer le dossier
    #folder_path = "/" + str(relative_path / pdf.stem) + "/"

    # Ajouter un slash à la fin pour ignorer le ficher
    folder_path = "/" + str(relative_path / pdf.stem) + ".pdf"

    if base_gitignore.exists():
        with open(base_gitignore, "r") as f:
            lines = f.read().splitlines()
    else:
        lines = []

    if folder_path not in lines:
        with open(base_gitignore, "a") as f:
            f.write(folder_path + "\n")
        print(f"   🧹 Ajouté à .gitignore central: {folder_path}")

# ==============================
# ✂️ DECOUPE INTELLIGENTE
# ==============================

def split_pdf(pdf, replace=False , do_gitignore=True) :
    size = get_size_mb(pdf)
    pages = get_pdf_pages(pdf)
    parts = math.ceil(size / SIZE_LIMIT_MB * 2)

    print(f"\n✂️ Découpe de {pdf}")
    print(f"   Taille: {size:.2f} MB | Pages: {pages}")
    print(f"   → {parts} morceaux")

    pages_per_part = math.ceil(pages / parts)
    output_dir = get_output_dir(pdf)
    temp_dir = output_dir / "tmp"
    temp_dir.mkdir(exist_ok=True)

    for i in range(parts):
        start = i * pages_per_part + 1
        end = min((i + 1) * pages_per_part, pages)
        percent_start = int((start / pages) * 100)
        percent_end = int((end / pages) * 100)

        temp_pattern = temp_dir / f"page_%04d.pdf"
        cmd_extract = ["pdfseparate", "-f", str(start), "-l", str(end), str(pdf), str(temp_pattern)]
        subprocess.run(cmd_extract, check=True)

        pages_files = sorted(temp_dir.glob("page_*.pdf"))
        output_file = output_dir / f"{pdf.stem}_{percent_start}-{percent_end}pct.pdf"
        cmd_merge = ["pdfunite"] + [str(p) for p in pages_files] + [str(output_file)]
        subprocess.run(cmd_merge, check=True)

        print(f"   📄 {output_file} ({start}-{end})")
        for p in pages_files:
            p.unlink()

    temp_dir.rmdir()
    print("   ✅ Découpe terminée")

    if replace:
        pdf.unlink()
        print("   🗑️ Original supprimé après découpe")

    if do_gitignore:
        update_gitignore(pdf, base_gitignore)
        print("  🧹 GITIGNORE")

def split_pdf(pdf, replace=False, do_gitignore=True, base_gitignore=None):
    """
    Découpe un PDF en morceaux si sa taille dépasse SIZE_LIMIT_MB
    Ne refait pas la découpe si le dossier de sortie existe déjà et contient des PDF.
    """
    output_dir = get_output_dir(pdf)

    # Vérifier si la découpe a déjà été faite
    existing_files = list(output_dir.glob(f"{pdf.stem}_*pct.pdf"))
    if existing_files:
        print(f"⚠️ Découpe déjà existante pour {pdf}, on skippe.")
        if do_gitignore:
            update_gitignore(pdf, base_gitignore)
        return

    size = get_size_mb(pdf)
    pages = get_pdf_pages(pdf)
    parts = math.ceil(size / SIZE_LIMIT_MB * 2)

    print(f"\n✂️ Découpe de {pdf}")
    print(f"   Taille: {size:.2f} MB | Pages: {pages}")
    print(f"   → {parts} morceaux")

    pages_per_part = math.ceil(pages / parts)
    temp_dir = output_dir / "tmp"
    temp_dir.mkdir(exist_ok=True)

    for i in range(parts):
        start = i * pages_per_part + 1
        end = min((i + 1) * pages_per_part, pages)
        percent_start = int((start / pages) * 100)
        percent_end = int((end / pages) * 100)

        temp_pattern = temp_dir / f"page_%04d.pdf"
        cmd_extract = ["pdfseparate", "-f", str(start), "-l", str(end), str(pdf), str(temp_pattern)]
        subprocess.run(cmd_extract, check=True)

        pages_files = sorted(temp_dir.glob("page_*.pdf"))
        output_file = output_dir / f"{pdf.stem}_{percent_start}-{percent_end}pct.pdf"
        cmd_merge = ["pdfunite"] + [str(p) for p in pages_files] + [str(output_file)]
        subprocess.run(cmd_merge, check=True)

        print(f"   📄 {output_file} ({start}-{end})")

        # Cleanup pages individuelles
        for p in pages_files:
            p.unlink()

    temp_dir.rmdir()
    print("   ✅ Découpe terminée")

    if replace:
        pdf.unlink()
        print("   🗑️ Original supprimé après découpe")

    if do_gitignore:
        update_gitignore(pdf, base_gitignore)
        print("  🧹 GITIGNORE")



# ==============================
# 🔥 COMPRESSION INTELLIGENTE
# ==============================

def smart_compress(pdf, replace=False):
    original_size = get_size_mb(pdf)
    current_file = pdf
    output_dir = get_output_dir(pdf)

    print(f"\n📄 {pdf} | Taille initiale: {original_size:.2f} MB")

    for i in range(MAX_PASSES):
        temp_file = output_dir / f"{pdf.stem}_tmp_{i}.pdf"
        compress_once(current_file, temp_file)

        new_size = get_size_mb(temp_file)
        old_size = get_size_mb(current_file)
        print(f"   Pass {i+1}: {new_size:.2f} MB")

        if new_size < SIZE_LIMIT_MB:
            print("   ✅ Sous 100MB atteint")
            if replace:
                if current_file != pdf:
                    current_file.unlink()
                temp_file.rename(output_dir / pdf.name)
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
    return list(directory.rglob("*.pdf")) if recursive else list(directory.glob("*.pdf"))

# ==============================
# 📂 TRAITEMENT
# ==============================

def process_directory(directory, replace=False, recursive=False, do_compress=True, do_split=False, do_gitignore=False):
    base_gitignore = Path.cwd() / ".gitignore" if do_gitignore else None
    pdfs = find_pdfs(directory, recursive)

    for pdf in pdfs:
        if not pdf.exists():
            continue

        size = get_size_mb(pdf)
        success = False

        if do_compress and size > SIZE_LIMIT_MB:
            success = smart_compress(pdf, replace=replace)

        if (do_split and size > SIZE_LIMIT_MB) or (do_compress and not success):
            split_pdf(pdf, replace=replace , do_gitignore=do_gitignore)

        #if do_gitignore:
        #    update_gitignore(pdf, base_gitignore)

# ==============================
# 🚀 MAIN
# ==============================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compresser ou découper les PDF > 100MB")
    parser.add_argument("directory")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--quality", choices=["screen", "ebook", "printer"], default="screen")
    parser.add_argument("--compress", action="store_true", help="Activer compression")
    parser.add_argument("--split", action="store_true", help="Activer découpe")
    parser.add_argument("--gitignore", action="store_true", help="Ajouter les dossiers générés au .gitignore central")

    args = parser.parse_args()
    global PDF_QUALITY
    PDF_QUALITY = f"/{args.quality}"

    do_compress = args.compress or not args.split
    do_split = args.split
    do_gitignore = args.gitignore

    process_directory(
        args.directory,
        replace=args.replace,
        recursive=args.recursive,
        do_compress=do_compress,
        do_split=do_split,
        do_gitignore=do_gitignore
    )

if __name__ == "__main__":
    main()