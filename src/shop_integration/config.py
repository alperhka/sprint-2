from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    inventory_host: str = Field(default="localhost", description="Hostname des Inventory Service")
    inventory_port: int = Field(default=50051, description="Port des Inventory Service")
    payment_base_url: str = Field(default="http://localhost:8100", description="Basis-URL des Payment Service")
    rabbitmq_url: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        description="Verbindungs-URL zum RabbitMQ Broker",
    )
    fulfillment_command_queue: str = Field(
        default="shop.fulfillment.commands", description="Queue für Fulfillment-Aufträge"
    )
    fulfillment_status_queue: str = Field(
        default="shop.fulfillment.status", description="Queue für Fulfillment-Statusupdates"
    )
    log_file: Path = Field(
        default=Path("order-processing.log"),
        description="Pfad zur Log-Datei, in der der Workflow protokolliert wird.",
    )
    request_timeout_seconds: float = Field(
        default=5.0, description="Standard Timeout für externe Service-Aufrufe in Sekunden."
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

