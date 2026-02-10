from __future__ import annotations

import json
from pathlib import Path

from datasets import load_dataset
from datasets.features import Image as DatasetsImage


def find_image_columns(features) -> list[str]:
    cols: list[str] = []
    for col_name, feature in features.items():
        if isinstance(feature, DatasetsImage):
            cols.append(col_name)
    return cols


def safe_stem(text: str) -> str:
    keep = []
    for ch in text:
        if ch.isalnum() or ch in ['_', '.']:
            keep.append(ch)
        else:
            keep.append('_')
    return ''.join(keep).strip('_') or 'col'


def export_split(split, out_dir: Path, split_name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    image_cols = find_image_columns(split.features)
    if not image_cols:
        raise ValueError(f'No image columns found in split {split_name}')

    decoded = split
    for col in image_cols:
        decoded = decoded.cast_column(col, DatasetsImage(decode=True))

    meta_path = out_dir / 'metadata.jsonl'
    with meta_path.open('w', encoding='utf_8') as f:
        for idx, row in enumerate(decoded):
            row_meta: dict = {
                'index': idx,
                'split': split_name,
                'files': {},
            }

            for col in image_cols:
                img = row[col]
                col_dir = out_dir / safe_stem(col)
                col_dir.mkdir(parents=True, exist_ok=True)

                file_name = f'{idx:06d}.png'
                file_path = col_dir / file_name

                img.save(file_path)
                row_meta['files'][col] = str(file_path)

            for key, value in row.items():
                if key in image_cols:
                    continue
                try:
                    json.dumps(value)
                    row_meta[key] = value
                except TypeError:
                    row_meta[key] = str(value)

            f.write(json.dumps(row_meta, ensure_ascii=False) + '\n')


def export_dataset(dataset_name: str, out_root: Path) -> None:
    ds = load_dataset(dataset_name)

    out_root.mkdir(parents=True, exist_ok=True)

    for split_name, split in ds.items():
        split_out = out_root / split_name
        export_split(split, split_out, split_name)


if __name__ == '__main__':
    dataset_name = 'ngaggion/ChronoRoot2'
    out_root = Path('chronoroot2_export')
    export_dataset(dataset_name, out_root)
