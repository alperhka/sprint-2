from __future__ import annotations

import logging
import random
import string
from concurrent import futures
from typing import Dict, Tuple

import grpc

from .proto import inventory_pb2 as pb2
from .proto import inventory_pb2_grpc as pb2_grpc

LOGGER = logging.getLogger(__name__)


def _generate_reservation_id(order_id: str) -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"RES-{order_id}-{suffix}"


class InventoryService(pb2_grpc.InventoryServiceServicer):
    def __init__(self, initial_stock: Dict[str, int] | None = None) -> None:
        self._stock: Dict[str, int] = initial_stock or {}
        self._reservations: Dict[str, Tuple[str, Dict[str, int]]] = {}
        LOGGER.info("InventoryService initialisiert mit Bestand: %s", self._stock)

    def CheckAndReserve(self, request: pb2.ReservationRequest, context) -> pb2.ReservationResponse:
        LOGGER.info("CheckAndReserve für Order %s", request.order_id)
        unavailable: list[pb2.UnavailableItem] = []

        for item in request.items:
            available_quantity = self._stock.get(item.product_id, 0)
            if available_quantity < item.quantity:
                unavailable.append(
                    pb2.UnavailableItem(
                        product_id=item.product_id,
                        requested=item.quantity,
                        available=available_quantity,
                    )
                )

        if unavailable:
            LOGGER.warning("Artikel nicht verfügbar für Order %s: %s", request.order_id, unavailable)
            return pb2.ReservationResponse(
                order_id=request.order_id,
                status=pb2.ReservationStatus.RESERVATION_STATUS_UNAVAILABLE,
                unavailable_items=unavailable,
                message="Nicht alle Artikel verfügbar.",
            )

        reservation_id = _generate_reservation_id(request.order_id)
        reserved_items: Dict[str, int] = {}

        for item in request.items:
            self._stock[item.product_id] -= item.quantity
            reserved_items[item.product_id] = item.quantity

        self._reservations[reservation_id] = (request.order_id, reserved_items)
        LOGGER.info(
            "Reservierung %s erstellt für Order %s (%s)", reservation_id, request.order_id, reserved_items
        )
        return pb2.ReservationResponse(
            order_id=request.order_id,
            status=pb2.ReservationStatus.RESERVATION_STATUS_CONFIRMED,
            reservation_id=reservation_id,
            message="Alle Artikel reserviert.",
        )

    def ReleaseReservation(self, request: pb2.ReleaseRequest, context) -> pb2.ReleaseResponse:
        LOGGER.info("ReleaseReservation %s", request.reservation_id)
        reservation = self._reservations.pop(request.reservation_id, None)
        if not reservation:
            LOGGER.warning("Reservierung %s nicht gefunden.", request.reservation_id)
            return pb2.ReleaseResponse(
                reservation_id=request.reservation_id, success=False, message="Reservierung unbekannt."
            )

        _, items = reservation
        for product_id, quantity in items.items():
            self._stock[product_id] = self._stock.get(product_id, 0) + quantity

        LOGGER.info("Reservierung %s freigegeben, Bestand aktualisiert.", request.reservation_id)
        return pb2.ReleaseResponse(
            reservation_id=request.reservation_id, success=True, message="Reservierung freigegeben."
        )


def serve(host: str = "0.0.0.0", port: int = 50051, initial_stock: Dict[str, int] | None = None) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = InventoryService(initial_stock=initial_stock)
    pb2_grpc.add_InventoryServiceServicer_to_server(service, server)
    server.add_insecure_port(f"{host}:{port}")
    LOGGER.info("InventoryService läuft auf %s:%s", host, port)
    server.start()
    server.wait_for_termination()

