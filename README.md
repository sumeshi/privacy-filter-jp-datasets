# privacy-filter-jp-datasets

Japanese training-data generators and source-conversion scripts for
`privacy-filter.cpp`.

This repository intentionally tracks scripts and documentation, not generated
training JSONL files or local copies of upstream source data.

## Layout

- `scripts/gen_synthetic_address_jp.py`: Japanese address examples. Place names
  come from Japan Post postal-code data; street numbers, building names, and
  rooms are fabricated.
- `scripts/gen_synthetic_date_id_jp.py`: synthetic dates and internal IDs.
- `scripts/gen_synthetic_structured_pii_jp.py`: synthetic email, phone, URL, and
  secret examples.
- `scripts/gen_synthetic_boundary_jp.py`: boundary regression cases.
- `scripts/convert_stockmark_ner.py`: local converter for Stockmark
  `ner-wikipedia-dataset`.
- `generated/`: local generated JSONL output, ignored by git.
- `raw/`: local upstream data downloads, ignored by git.

## Generate

Run from this repository root:

```sh
python3 scripts/gen_synthetic_address_jp.py -n 4000 --seed 3
python3 scripts/gen_synthetic_date_id_jp.py -n 2000 --seed 1
python3 scripts/gen_synthetic_structured_pii_jp.py --per-label 1200 --seed 2
python3 scripts/gen_synthetic_boundary_jp.py -n 3000 --seed 4
python3 scripts/convert_stockmark_ner.py --require-entity
```

Each script writes to `generated/` by default, using the script location rather
than the current working directory.

From the parent `privacy-filter.cpp` repository, prefix the script paths with
`datasets/jp-data/`.

## Source And Redistribution Notes

- Synthetic template data is fabricated and can be regenerated locally.
- Address generation downloads Japan Post postal-code data at runtime unless
  `--ken-all` is supplied.
- Stockmark `ner-wikipedia-dataset` is CC-BY-SA 3.0. This repository does not
  redistribute the upstream dataset or converted JSONL; run the converter
  locally when needed.
- Review upstream terms before redistributing any generated or converted data.
