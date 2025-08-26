# Track Global Gold and Silver Prices

This minimal tool fetches latest spot prices for gold (XAU) and silver (XAG) across multiple fiat currencies using exchangerate.host.

Quick run without installing packages:

```bash
PYTHONPATH=src python3 -m metal_prices.cli --metals XAU XAG --currencies USD EUR
```

Save to a file:

```bash
PYTHONPATH=src python3 -m metal_prices.cli --metals XAU XAG --currencies USD EUR --out data/sample.json

Notes:
- Data sources: goldprice.org (USD spot) and frankfurter.app (ECB FX). No API keys required.
- Output JSON structure: nested mapping metal -> currency -> object with fields `base`, `quote`, `rate`, `timestamp`.
```
