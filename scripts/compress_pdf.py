import os
import subprocess
from pathlib import Path

# Seuil en MB
SIZE_LIMIT_MB = 100

# Niveau de compression :
# /screen   -> très compressé (faible qualité)
# /ebook    -> bon compromis
# /printer  -> haute qualité
PDF_QUALITY = "/ebook"

def get_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)

def compress_pdf(input_path, output_path):
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={PDF_QUALITY}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        str(input_path)
    ]
    subprocess.run(cmd, check=True)

def find_pdfs(directory, recursive):
    directory = Path(directory)
    if recursive:
        return directory.rglob("*.pdf")  # 🔁 récursif
    else:
        return directory.glob("*.pdf")   # 📁 seulement dossier courant

def process_directory(directory, replace=False, recursive=False):
    pdfs = find_pdfs(directory, recursive)

    for pdf in pdfs:
        size = get_size_mb(pdf)

        if size > SIZE_LIMIT_MB:
            print(f"\n📄 {pdf}")
            print(f"   Taille: {size:.2f} MB → compression...")

            if replace:
                temp_output = pdf.with_name(pdf.stem + "_compressed.pdf")
                compress_pdf(pdf, temp_output)

                temp_size = get_size_mb(temp_output)
                print(f"   Nouvelle taille: {temp_size:.2f} MB")

                if temp_size < size:
                    pdf.unlink()
                    temp_output.rename(pdf)
                    print("   ✅ Remplacé")
                else:
                    temp_output.unlink()
                    print("   ❌ Compression inefficace, conservé")
            else:
                output = pdf.with_name(pdf.stem + "_compressed.pdf")
                compress_pdf(pdf, output)

                new_size = get_size_mb(output)
                print(f"   Nouvelle taille: {new_size:.2f} MB")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Compresser les PDF > 100MB")
    parser.add_argument("directory", help="Répertoire à scanner")
    parser.add_argument("--replace", action="store_true",
                        help="Remplacer les fichiers originaux")
    parser.add_argument("--recursive", action="store_true",
                        help="Inclure les sous-dossiers")

    args = parser.parse_args()

    process_directory(
        args.directory,
        replace=args.replace,
        recursive=args.recursive
    )

if __name__ == "__main__":
    main()
