from __future__ import annotations

from shop_integration.config import get_settings
from shop_integration.messaging.rabbitmq import RabbitMQConsumer, RabbitMQPublisher
from shop_integration.wms.worker import WarehouseWorker


if __name__ == "__main__":
    settings = get_settings()
    worker = WarehouseWorker(
        command_consumer=RabbitMQConsumer(settings.rabbitmq_url, settings.fulfillment_command_queue),
        status_publisher=RabbitMQPublisher(settings.rabbitmq_url, settings.fulfillment_status_queue),
    )
    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()

