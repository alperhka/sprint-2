from __future__ import annotations

import logging

from shop_integration.inventory.service import serve

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    initial_stock = {
        "P-8821": 10,
        "P-3344": 5,
        "P-9999": 0,
    }
    serve(initial_stock=initial_stock)

