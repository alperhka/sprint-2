from __future__ import annotations

import logging
from dataclasses import dataclass

import grpc
from google.protobuf.json_format import MessageToDict

from .proto import inventory_pb2 as pb2
from .proto import inventory_pb2_grpc as pb2_grpc

LOGGER = logging.getLogger(__name__)


@dataclass
class ReservationResult:
    success: bool
    reservation_id: str | None
    unavailable_items: list[dict]
    message: str


class InventoryClient:
    def __init__(self, host: str, port: int, timeout_seconds: float = 5.0) -> None:
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        self._stub = pb2_grpc.InventoryServiceStub(self._channel)
        self._timeout = timeout_seconds

    def check_and_reserve(self, order_id: str, items: list[dict]) -> ReservationResult:
        request = pb2.ReservationRequest(
            order_id=order_id,
            items=[pb2.OrderItem(product_id=item["productId"], quantity=item["quantity"]) for item in items],
        )
        LOGGER.info("Frage Inventory Service für Order %s an.", order_id)
        response = self._stub.CheckAndReserve(request, timeout=self._timeout)
        unavailable_items = [
            MessageToDict(item, preserving_proto_field_name=True) for item in response.unavailable_items
        ]
        success = response.status == pb2.ReservationStatus.RESERVATION_STATUS_CONFIRMED
        return ReservationResult(
            success=success,
            reservation_id=response.reservation_id if success else None,
            unavailable_items=unavailable_items,
            message=response.message,
        )

    def release(self, reservation_id: str, order_id: str) -> bool:
        LOGGER.info("Gebe Reservierung %s für Order %s frei.", reservation_id, order_id)
        response = self._stub.ReleaseReservation(
            pb2.ReleaseRequest(reservation_id=reservation_id, order_id=order_id), timeout=self._timeout
        )
        return bool(response.success)

    def close(self) -> None:
        self._channel.close()

