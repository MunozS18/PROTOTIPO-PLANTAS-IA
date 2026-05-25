"""
Prepara el dataset de Kaggle para entrenamiento.

Estructuras soportadas:
  1. ImageFolder: data/raw/<clase>/*.jpg
  2. Plant Seedlings: data/raw/train/<especie>/
  3. PlantVillage: data/raw/PlantVillage/train/<Cultivo___Estado>/
  4. PlantVillage directo: data/raw/train/<Cultivo___Estado>/

Salida: data/processed/{train,val,test}/<clase>/
"""
from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".JPG", ".JPEG", ".PNG"}


def _collect_images(folder: Path) -> list[Path]:
    return [
        f for f in folder.rglob("*")
        if f.is_file() and f.suffix in IMAGE_EXTENSIONS
    ]


def _is_class_folder(folder: Path) -> bool:
    """Carpeta de clase: contiene imágenes directamente o en un nivel."""
    if not folder.is_dir() or folder.name.startswith("."):
        return False
    images = _collect_images(folder)
    return len(images) > 0


def _scan_train_root(train_root: Path) -> dict[str, list[Path]]:
    """Escanea un directorio train/ con subcarpetas por clase."""
    classes: dict[str, list[Path]] = {}
    for item in sorted(train_root.iterdir()):
        if not _is_class_folder(item):
            continue
        images = _collect_images(item)
        if images:
            classes[item.name] = images
    return classes


def find_class_folders(root: Path) -> dict[str, list[Path]]:
    """Detecta carpetas de clases en múltiples layouts de Kaggle."""
    search_paths: list[Path] = []

    # Rutas típicas PlantVillage / Kaggle
    for candidate in [
        root,
        root / "train",
        root / "PlantVillage" / "train",
        root / "plantvillage" / "train",
    ]:
        if candidate.is_dir():
            search_paths.append(candidate)

    # Buscar cualquier carpeta train/ con ≥3 subcarpetas con imágenes
    for train_dir in root.rglob("train"):
        if train_dir.is_dir() and train_dir not in search_paths:
            subdirs = [d for d in train_dir.iterdir() if d.is_dir()]
            if len(subdirs) >= 3:
                search_paths.append(train_dir)

    best: dict[str, list[Path]] = {}
    for search_root in search_paths:
        found = _scan_train_root(search_root)
        if len(found) > len(best):
            best = found

    # Fallback: carpetas de clase directamente bajo root
    if len(best) < 2:
        direct: dict[str, list[Path]] = {}
        for item in sorted(root.iterdir()):
            if _is_class_folder(item):
                direct[item.name] = _collect_images(item)
        if len(direct) > len(best):
            best = direct

    return best


def split_and_copy(
    classes: dict[str, list[Path]],
    output_dir: Path,
    train_ratio: float,
    val_ratio: float,
    seed: int,
    max_per_class: int | None,
) -> dict[str, int]:
    random.seed(seed)
    stats = {"train": 0, "val": 0, "test": 0, "classes": len(classes)}

    for class_name, images in classes.items():
        shuffled = images.copy()
        random.shuffle(shuffled)
        if max_per_class and len(shuffled) > max_per_class:
            shuffled = shuffled[:max_per_class]

        n = len(shuffled)
        if n == 0:
            continue

        n_train = max(1, int(n * train_ratio))
        n_val = max(1, int(n * val_ratio)) if n > 2 else 0
        n_test = n - n_train - n_val
        if n_test < 0:
            n_test = 0
            n_val = n - n_train

        splits = {
            "train": shuffled[:n_train],
            "val": shuffled[n_train : n_train + n_val],
            "test": shuffled[n_train + n_val :],
        }

        for split_name, files in splits.items():
            if not files:
                continue
            dest_dir = output_dir / split_name / class_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            for i, src in enumerate(files):
                dest = dest_dir / f"{class_name}_{i}{src.suffix.lower()}"
                shutil.copy2(src, dest)
                stats[split_name] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(description="Preparar dataset de plantas desde Kaggle")
    parser.add_argument("--input", default="data/raw", help="Carpeta con dataset descomprimido")
    parser.add_argument("--output", default="data/processed", help="Carpeta de salida")
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--max-per-class",
        type=int,
        default=400,
        help="Máximo imágenes por clase (None = todas). Default 400 para entrenar más rápido.",
    )
    args = parser.parse_args()

    root = Path(args.input)
    if not root.exists():
        raise SystemExit(f"No existe {root}. Ver docs/GUIA_DATASET.md")

    classes = find_class_folders(root)
    if len(classes) < 2:
        raise SystemExit(
            f"Solo se encontraron {len(classes)} clase(s) en {root}.\n"
            "Para PlantVillage usa: python scripts/prepare_dataset.py --input data/raw"
        )

    output = Path(args.output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    max_pc = args.max_per_class if args.max_per_class > 0 else None
    stats = split_and_copy(
        classes, output, args.train_ratio, args.val_ratio, args.seed, max_pc
    )

    print(f"OK {stats['classes']} clases procesadas")
    print(f"  Train: {stats['train']} | Val: {stats['val']} | Test: {stats['test']}")
    print(f"  Salida: {output.resolve()}")
    print("\nClases detectadas:")
    for name in sorted(classes.keys()):
        print(f"  - {name}")


if __name__ == "__main__":
    main()
