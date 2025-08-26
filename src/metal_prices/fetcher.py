from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Dict, List
from urllib.request import Request, urlopen


GOLDPRICE_USD_URL = "https://data-asg.goldprice.org/dbXRates/USD"
FRANKFURTER_USD_URL = "https://api.frankfurter.app/latest?base=USD"


@dataclass
class MetalRate:
    base: str
    quote: str
    rate: float
    timestamp: int


def fetch_latest_rates(
    metals: List[str] = ["XAU", "XAG"],
    currencies: List[str] = ["USD", "EUR", "GBP", "JPY", "INR", "CNY", "AUD", "CAD"],
    timeout_seconds: int = 15,
) -> Dict[str, Dict[str, MetalRate]]:
    """
    Fetch latest spot prices (USD-based) for metals and convert to requested fiat currencies.

    Sources:
    - Gold/Silver USD spot: goldprice.org public endpoint
    - FX rates: European Central Bank via frankfurter.app

    Returns nested mapping metal -> currency -> MetalRate
    """
    def fetch_json(url: str) -> Dict:
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
            },
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    # Fetch USD spot prices for gold/silver
    gp_payload = fetch_json(GOLDPRICE_USD_URL)

    items = gp_payload.get("items") or []
    if not items:
        raise RuntimeError(f"GoldPrice payload missing items: {gp_payload}")

    usd_spot_by_metal: Dict[str, float] = {}
    first = items[0]
    if "xauPrice" in first:
        usd_spot_by_metal["XAU"] = float(first["xauPrice"])  # USD per XAU
    if "xagPrice" in first:
        usd_spot_by_metal["XAG"] = float(first["xagPrice"])  # USD per XAG

    # Fetch USD-based FX rates (USD -> target currency)
    fx_payload = fetch_json(FRANKFURTER_USD_URL)

    fx_rates: Dict[str, float] = fx_payload.get("rates", {})
    fx_rates["USD"] = 1.0
    timestamp = int(time.time())

    # Build cross rates: price of metal in currency = rate(currency/EUR) / rate(metal/EUR)
    # Because API returns rates as 1 EUR = rate[SYMBOL]
    result: Dict[str, Dict[str, MetalRate]] = {}
    for metal in metals:
        usd_price = usd_spot_by_metal.get(metal.upper())
        if usd_price is None:
            continue
        result[metal] = {}
        for currency in currencies:
            factor = fx_rates.get(currency.upper())
            if factor is None:
                continue
            cross = usd_price * factor
            result[metal][currency] = MetalRate(
                base=metal,
                quote=currency,
                rate=float(cross),
                timestamp=timestamp,
            )

    return result


def to_pretty_json(data: Dict[str, Dict[str, MetalRate]]) -> str:
    def encode(obj):
        if isinstance(obj, MetalRate):
            return obj.__dict__
        raise TypeError(f"Type not serializable: {type(obj)}")

    return json.dumps(data, default=encode, indent=2, sort_keys=True)
