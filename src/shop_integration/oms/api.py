from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException

from ..config import Settings, get_settings
from ..inventory.client import InventoryClient
from ..logging_utils import configure_logging
from ..messaging.rabbitmq import RabbitMQConsumer, RabbitMQPublisher, ThreadedConsumer
from ..models import Order, OrderRecord
from ..payment.client import PaymentClient
from ..workflow import OrderRepository, OrderWorkflow

LOGGER = logging.getLogger(__name__)


class AppState:
    def __init__(self, settings: Settings) -> None:
        configure_logging(settings.log_file)
        LOGGER.info("Starte OMS mit Einstellungen: %s", settings)

        self.settings = settings
        self.repository = OrderRepository()
        self.inventory_client = InventoryClient(settings.inventory_host, settings.inventory_port)
        self.payment_client = PaymentClient(settings.payment_base_url, settings.request_timeout_seconds)
        self.fulfillment_publisher = RabbitMQPublisher(settings.rabbitmq_url, settings.fulfillment_command_queue)

        self.status_consumer = ThreadedConsumer(
            RabbitMQConsumer(settings.rabbitmq_url, settings.fulfillment_status_queue)
        )
        self.workflow = OrderWorkflow(
            repository=self.repository,
            inventory_client=self.inventory_client,
            payment_client=self.payment_client,
            fulfillment_publisher=self.fulfillment_publisher,
        )
        self.status_consumer.start(self.workflow.handle_status_update)

    def shutdown(self) -> None:
        LOGGER.info("Fahre OMS herunter.")
        self.status_consumer.stop()
        self.fulfillment_publisher.close()
        self.inventory_client.close()


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="Order Management Service", version="1.0.0")
    app_state = AppState(settings)

    @app.on_event("shutdown")
    def _shutdown() -> None:
        app_state.shutdown()

    def get_workflow() -> OrderWorkflow:
        return app_state.workflow

    def get_repository() -> OrderRepository:
        return app_state.repository

    @app.post("/orders", response_model=OrderRecord, status_code=201)
    def create_order(order: Order, workflow: OrderWorkflow = Depends(get_workflow)) -> OrderRecord:
        LOGGER.info("Neue Bestellung %s eingegangen", order.orderId)
        record = workflow.process_order(order, order.metadata)
        return record

    @app.get("/orders/{order_id}", response_model=OrderRecord)
    def get_order(order_id: str, repository: OrderRepository = Depends(get_repository)) -> OrderRecord:
        record = repository.get(order_id)
        if not record:
            raise HTTPException(status_code=404, detail="Order nicht gefunden.")
        return record

    return app

