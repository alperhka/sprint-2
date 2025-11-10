from __future__ import annotations

import uvicorn

from shop_integration.config import get_settings
from shop_integration.oms.api import create_app


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(create_app(settings), host="0.0.0.0", port=8000)

