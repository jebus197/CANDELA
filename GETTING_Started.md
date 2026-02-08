# CANDELA - Quick-Start Guide (v0.3)

This page is intentionally short. The full reviewer run guide lives at:
- `docs/RUNNING.md`

## 1) Clone and install

```bash
git clone https://github.com/jebus197/CANDELA.git
cd CANDELA
python3 -m pip install -r requirements.txt
```

Note: `requirements.txt` includes `torch` and `sentence-transformers` (larger downloads).

## 2) Run the Guardian against a file

```bash
python3 run_guardian.py --input path/to/file.txt --mode strict
```

You should see a clear PASS/FAIL plus a short list of reasons.

## 3) Optional: run tests (sanity check)

```bash
python3 -m pytest -q
```

## 4) Optional: anchoring (tamper-evident receipts)

If you want on-chain receipts, follow:
- `docs/RUNNING.md` (Anchoring section)
- `docs/ANCHORS.md` (what has already been anchored)

## Next: model integration demo (optional)

If you want to see CANDELA checking a model's generated output live, use:
- `docs/MODEL_INTEGRATION.md`
