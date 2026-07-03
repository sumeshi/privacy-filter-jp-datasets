# privacy-filter-jp-datasets

Japanese training-data generators, source-conversion scripts, and
redistributable synthetic JSONL data for `privacy-filter.cpp`.

This repository intentionally tracks only data that is clear to redistribute:
purely synthetic template data and hand-authored boundary cases. Local copies of
upstream source data and converted upstream-derived JSONL are not tracked.

## Layout

- `scripts/gen_synthetic_address_jp.py`: Japanese address examples. Place names
  come from Japan Post postal-code data; street numbers, building names, and
  rooms are fabricated.
- `scripts/gen_synthetic_date_id_jp.py`: synthetic dates and internal IDs.
- `scripts/gen_synthetic_structured_pii_jp.py`: synthetic email, phone, URL, and
  secret examples.
- `scripts/gen_synthetic_boundary_jp.py`: boundary regression cases.
- `scripts/pii_values.py`: shared library of fictional PII value generators
  (name pools, all Japanese phone formats, Japan-specific identifiers).
- `scripts/gen_synthetic_person_jp.py`: ordinary Japanese names in business
  contexts (furigana pairs, joint names, honorific/title boundaries, romaji).
- `scripts/gen_synthetic_phone_id_jp.py`: Japanese phone-number format
  variants and Japan-specific identifiers (My Number, driver's license,
  passport, pension, health insurance, bank account, residence card) mapped
  to `account_number`.
- `scripts/gen_synthetic_docs_jp.py`: long multi-PII business documents
  (emails with signatures, application forms, support logs, delivery notes,
  minutes, incident reports). Uses the generated address JSONL as an address
  pool via `--address-file`.
- `scripts/gen_synthetic_negative_jp.py`: O-only negative rows (business text
  with PII-lookalike numbers) to suppress over-detection.
- `scripts/validate_jsonl.py`: validator for span JSONL (offsets, labels,
  overlaps, duplicates, benchmark-leak check via `--against`).
- `scripts/make_benchmark_v2.py`: emits the hand-curated benchmark v2 files
  into the parent repository (`datasets/benchmark/{eval2,challenge2}.jsonl`).
- `scripts/convert_stockmark_ner.py`: local converter for Stockmark
  `ner-wikipedia-dataset`.
- `generated/`: selected redistributable synthetic JSONL plus ignored local
  generated output.
- `raw/`: local upstream data downloads, ignored by git.

## Redistributed Data

Tracked under `generated/`:

- `synthetic_date_id_jp.jsonl`
- `synthetic_structured_pii_jp.jsonl`
- `synthetic_boundary_jp.jsonl`
- `synthetic_person_jp.jsonl`
- `synthetic_phone_id_jp.jsonl`
- `synthetic_negative_jp.jsonl`

These tracked synthetic JSONL files are distributed under this repository's MIT
License.

Not tracked:

- `stockmark_ner_jp.jsonl`: converted from Stockmark
  `ner-wikipedia-dataset` (CC-BY-SA 3.0). Regenerate locally if needed.
- `synthetic_address_jp*.jsonl`: generated from Japan Post postal-code data.
  Regenerate locally if needed.
- `synthetic_docs_jp.jsonl`: derived from the address JSONL above via
  `--address-file` (Japan Post place names). Regenerate locally if needed.
- `generated/eval/`: local predictions and evaluation artifacts.

## Generate

Run from this repository root:

```sh
python3 scripts/gen_synthetic_address_jp.py -n 4000 --seed 3
python3 scripts/gen_synthetic_date_id_jp.py -n 2000 --seed 1
python3 scripts/gen_synthetic_structured_pii_jp.py --per-label 1200 --seed 2
python3 scripts/gen_synthetic_boundary_jp.py -n 3000 --seed 4  # add --exclude <benchmark JSONLs> when run from the parent repo
python3 scripts/convert_stockmark_ner.py --require-entity
python3 scripts/gen_synthetic_phone_id_jp.py -n 4000 --seed 11
python3 scripts/gen_synthetic_person_jp.py -n 4000 --seed 12
python3 scripts/gen_synthetic_negative_jp.py -n 2000 --seed 13
python3 scripts/gen_synthetic_docs_jp.py -n 3000 --seed 14 \
  --address-file generated/synthetic_address_jp.jsonl
python3 scripts/validate_jsonl.py generated/*.jsonl
```

Each script writes to `generated/` by default, using the script location rather
than the current working directory.

From the parent `privacy-filter.cpp` repository, prefix the script paths with
`datasets/jp-data/`.

## Source And Redistribution Notes

- Tracked synthetic template data is fabricated and can be regenerated locally.
- Address generation downloads Japan Post postal-code data at runtime unless
  `--ken-all` is supplied. Generated address JSONL is intentionally not tracked
  because it is derived from that external dataset.
- Stockmark `ner-wikipedia-dataset` is CC-BY-SA 3.0. This repository does not
  redistribute the upstream dataset or converted JSONL; run the converter
  locally when needed.
- Review upstream terms before redistributing any generated or converted data.
