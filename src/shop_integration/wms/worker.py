from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Callable, Iterable, Optional

from ..messaging.rabbitmq import RabbitMQConsumer, RabbitMQPublisher

LOGGER = logging.getLogger(__name__)


class WarehouseWorker:
    def __init__(
        self,
        command_consumer: RabbitMQConsumer,
        status_publisher: RabbitMQPublisher,
        processing_delays: Optional[Iterable[float]] = None,
    ) -> None:
        self._consumer = command_consumer
        self._publisher = status_publisher
        self._delays = list(processing_delays or [1.0, 1.0, 1.0])

    def _publish_status(self, order_id: str, status: str, details: Optional[str] = None) -> None:
        event = {
            "eventType": status,
            "occurredAt": datetime.utcnow().isoformat(),
            "orderId": order_id,
            "status": status,
        }
        if details:
            event["details"] = details
        LOGGER.info("WMS Status %s für Order %s", status, order_id)
        self._publisher.publish(event)

    def _process_command(self, command: dict) -> None:
        order_id = command.get("orderId")
        if not order_id:
            LOGGER.warning("Ungültiges Fulfillment-Kommando: %s", command)
            return

        LOGGER.info("Starte Kommissionierung für Order %s", order_id)
        statuses = ["ITEMS_PICKED", "ORDER_PACKED", "ORDER_SHIPPED"]
        for delay, status in zip(self._delays, statuses):
            time.sleep(delay)
            self._publish_status(order_id, status)

    def start(self) -> None:
        LOGGER.info("WMS Worker gestartet.")
        self._consumer.start(self._process_command)

    def stop(self) -> None:
        LOGGER.info("WMS Worker wird gestoppt.")
        self._consumer.stop()
        self._publisher.close()

