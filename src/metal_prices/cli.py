from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .fetcher import fetch_latest_rates, to_pretty_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch XAU/XAG prices across currencies")
    parser.add_argument(
        "--metals",
        nargs="+",
        default=["XAU", "XAG"],
        help="List of metal symbols to fetch (e.g., XAU XAG)",
    )
    parser.add_argument(
        "--currencies",
        nargs="+",
        default=["USD", "EUR", "GBP", "JPY", "INR", "CNY", "AUD", "CAD"],
        help="List of fiat currencies (e.g., USD EUR)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional output JSON file path",
    )

    args = parser.parse_args()

    data = fetch_latest_rates(list(args.metals), list(args.currencies))

    if not args.out:
        print(to_pretty_json(data))
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(to_pretty_json(data))
    print(str(args.out))


if __name__ == "__main__":
    main()
