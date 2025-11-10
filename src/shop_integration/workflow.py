from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Dict, Optional

import grpc
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .inventory.client import InventoryClient, ReservationResult
from .messaging.rabbitmq import RabbitMQPublisher
from .models import Order, OrderHistoryEntry, OrderRecord, OrderStatus, PaymentResponse, PaymentStatus
from .payment.client import PaymentClient

LOGGER = logging.getLogger(__name__)


class OrderRepository:
    def __init__(self) -> None:
        self._orders: Dict[str, OrderRecord] = {}
        self._lock = threading.RLock()

    def create(self, order: Order) -> OrderRecord:
        with self._lock:
            now = datetime.utcnow()
            record = OrderRecord(order=order, status=OrderStatus.RECEIVED, createdAt=now, updatedAt=now)
            record.history.append(
                OrderHistoryEntry(timestamp=now, status=OrderStatus.RECEIVED, message="Bestellung empfangen.")
            )
            self._orders[order.orderId] = record
            LOGGER.info("Order %s gespeichert.", order.orderId)
            return record

    def get(self, order_id: str) -> Optional[OrderRecord]:
        with self._lock:
            return self._orders.get(order_id)

    def update_status(self, order_id: str, status: OrderStatus, message: str) -> Optional[OrderRecord]:
        with self._lock:
            record = self._orders.get(order_id)
            if not record:
                LOGGER.warning("Order %s nicht gefunden für Statusupdate.", order_id)
                return None
            now = datetime.utcnow()
            record.status = status
            record.updatedAt = now
            record.history.append(OrderHistoryEntry(timestamp=now, status=status, message=message))
            LOGGER.info("Order %s -> %s (%s)", order_id, status, message)
            return record

    def set_reservation(self, order_id: str, reservation_id: str) -> None:
        with self._lock:
            record = self._orders.get(order_id)
            if record:
                record.reservationId = reservation_id

    def set_payment(self, order_id: str, payment_id: str) -> None:
        with self._lock:
            record = self._orders.get(order_id)
            if record:
                record.paymentId = payment_id


class OrderWorkflow:
    def __init__(
        self,
        repository: OrderRepository,
        inventory_client: InventoryClient,
        payment_client: PaymentClient,
        fulfillment_publisher: RabbitMQPublisher,
    ) -> None:
        self._repository = repository
        self._inventory_client = inventory_client
        self._payment_client = payment_client
        self._publisher = fulfillment_publisher

    def process_order(self, order: Order, metadata: Optional[dict] = None) -> OrderRecord:
        record = self._repository.create(order)

        reservation_result = self._reserve_inventory(order)
        if not reservation_result.success:
            message = f"Inventar nicht verfügbar: {reservation_result.message}"
            self._repository.update_status(order.orderId, OrderStatus.INVENTORY_UNAVAILABLE, message)
            return self._repository.get(order.orderId) or record

        self._repository.set_reservation(order.orderId, reservation_result.reservation_id or "")

        payment_response = self._authorize_payment(order, metadata)
        if payment_response is None:
            return self._repository.get(order.orderId) or record

        if payment_response.status == PaymentStatus.DECLINED:
            self._repository.update_status(
                order.orderId,
                OrderStatus.PAYMENT_FAILED,
                payment_response.failureReason or "Zahlung abgelehnt.",
            )
            self._release_inventory(order, reservation_result)
            return self._repository.get(order.orderId) or record

        self._repository.set_payment(order.orderId, payment_response.paymentId)
        self._repository.update_status(
            order.orderId,
            OrderStatus.PAYMENT_AUTHORIZED,
            f"Zahlung autorisiert (AuthCode: {payment_response.authorizationCode}).",
        )

        self._start_fulfillment(order, reservation_result.reservation_id)
        return self._repository.get(order.orderId) or record

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4.0),
        retry=retry_if_exception_type((grpc.RpcError, ConnectionError)),
        reraise=True,
    )
    def _call_inventory(self, order: Order) -> ReservationResult:
        return self._inventory_client.check_and_reserve(order.orderId, [item.model_dump() for item in order.items])

    def _reserve_inventory(self, order: Order) -> ReservationResult:
        try:
            result = self._call_inventory(order)
        except Exception as exc:  # pragma: no cover - Schutzmaßnahme
            LOGGER.exception("Fehler beim Inventory-Aufruf: %s", exc)
            self._repository.update_status(order.orderId, OrderStatus.FAILED, "Inventory Service nicht erreichbar.")
            return ReservationResult(False, None, [], "Inventory Service nicht erreichbar.")

        if result.success:
            self._repository.update_status(order.orderId, OrderStatus.INVENTORY_RESERVED, result.message)
        else:
            self._repository.update_status(order.orderId, OrderStatus.INVENTORY_UNAVAILABLE, result.message)

        return result

    def _authorize_payment(self, order: Order, metadata: Optional[dict]) -> Optional[PaymentResponse]:
        try:
            response = self._payment_client.authorize(order.orderId, order.totalAmount, metadata or {})
        except ValueError as exc:
            LOGGER.warning("Ungültige Zahlungsdaten: %s", exc)
            self._repository.update_status(order.orderId, OrderStatus.FAILED, "Ungültige Zahlungsdaten.")
            self._release_if_needed(order.orderId)
            return None
        except Exception as exc:
            LOGGER.exception("Fehler beim Payment-Service: %s", exc)
            self._repository.update_status(
                order.orderId, OrderStatus.FAILED, "Payment Service nicht verfügbar."
            )
            self._release_if_needed(order.orderId)
            return None

        return response

    def _release_if_needed(self, order_id: str) -> None:
        record = self._repository.get(order_id)
        if record and record.reservationId:
            try:
                self._inventory_client.release(record.reservationId, order_id)
            except Exception as exc:  # pragma: no cover - Schutzmaßnahme
                LOGGER.exception("Fehler beim Release der Reservierung: %s", exc)

    def _release_inventory(self, order: Order, reservation_result: ReservationResult) -> None:
        if reservation_result.reservation_id:
            try:
                self._inventory_client.release(reservation_result.reservation_id, order.orderId)
            except Exception as exc:  # pragma: no cover - Schutzmaßnahme
                LOGGER.exception("Fehler beim Freigeben der Reservierung: %s", exc)

    def _start_fulfillment(self, order: Order, reservation_id: Optional[str]) -> None:
        command = {
            "eventType": "ORDER_FULFILLMENT_COMMAND",
            "occurredAt": datetime.utcnow().isoformat(),
            "orderId": order.orderId,
            "reservationId": reservation_id,
            "items": [item.model_dump() for item in order.items],
            "shippingAddress": order.shippingAddress.model_dump(),
        }
        self._publisher.publish(command)
        self._repository.update_status(
            order.orderId,
            OrderStatus.FULFILLMENT_STARTED,
            "Fulfillment im WMS angestoßen.",
        )

    def handle_status_update(self, event: dict) -> None:
        order_id = event.get("orderId")
        status = event.get("status")
        if not order_id or not status:
            LOGGER.warning("Ungültiges Status-Event: %s", event)
            return

        status_map = {
            "ITEMS_PICKED": OrderStatus.ITEMS_PICKED,
            "ORDER_PACKED": OrderStatus.ORDER_PACKED,
            "ORDER_SHIPPED": OrderStatus.ORDER_SHIPPED,
            "FULFILLMENT_ERROR": OrderStatus.FAILED,
        }
        mapped_status = status_map.get(status)
        if not mapped_status:
            LOGGER.warning("Unbekannter Status %s für Order %s", status, order_id)
            return

        message = event.get("details", f"WMS Status: {status}")
        self._repository.update_status(order_id, mapped_status, message)

