from __future__ import annotations

from dataclasses import dataclass

from shop_integration.inventory.client import ReservationResult
from shop_integration.models import (
    Address,
    Customer,
    Order,
    OrderItem,
    OrderStatus,
    PaymentResponse,
    PaymentStatus,
)
from shop_integration.workflow import OrderRepository, OrderWorkflow


@dataclass
class FakeInventoryClient:
    result: ReservationResult
    released: bool = False

    def check_and_reserve(self, order_id: str, items: list[dict]) -> ReservationResult:
        return self.result

    def release(self, reservation_id: str, order_id: str) -> bool:
        self.released = True
        return True

    def close(self) -> None:  # pragma: no cover - für Schnittstellenkompatibilität
        pass


@dataclass
class FakePaymentClient:
    response: PaymentResponse | None
    raises: Exception | None = None

    def authorize(self, order_id: str, amount: float, metadata: dict | None = None) -> PaymentResponse:
        if self.raises:
            raise self.raises
        assert self.response is not None
        return self.response


class FakePublisher:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    def publish(self, payload: dict) -> None:
        self.sent.append(payload)

    def close(self) -> None:  # pragma: no cover
        pass


def sample_order() -> Order:
    return Order(
        orderId="ORD-1",
        customer=Customer(customerId="CUST-1", prename="Max", name="Mustermann"),
        items=[OrderItem(productId="P-1", quantity=1, price=10.0)],
        totalAmount=10.0,
        shippingAddress=Address(street="Street 1", city="City", zipCode="00000", country="DE"),
    )


def test_happy_path():
    inventory = FakeInventoryClient(
        ReservationResult(success=True, reservation_id="RES-1", unavailable_items=[], message="OK")
    )
    payment = FakePaymentClient(
        PaymentResponse(paymentId="PAY-ORD-1", orderId="ORD-1", status=PaymentStatus.AUTHORIZED, authorizationCode="AUTH")
    )
    publisher = FakePublisher()

    workflow = OrderWorkflow(OrderRepository(), inventory, payment, publisher)
    record = workflow.process_order(sample_order())

    assert record is not None
    assert record.status == OrderStatus.FULFILLMENT_STARTED
    assert publisher.sent and publisher.sent[0]["orderId"] == "ORD-1"


def test_inventory_unavailable():
    inventory = FakeInventoryClient(
        ReservationResult(
            success=False,
            reservation_id=None,
            unavailable_items=[{"product_id": "P-1", "available": 0, "requested": 1}],
            message="Nicht verfügbar",
        )
    )
    payment = FakePaymentClient(
        PaymentResponse(paymentId="PAY-ORD-1", orderId="ORD-1", status=PaymentStatus.AUTHORIZED)
    )
    publisher = FakePublisher()

    workflow = OrderWorkflow(OrderRepository(), inventory, payment, publisher)
    record = workflow.process_order(sample_order())

    assert record is not None
    assert record.status == OrderStatus.INVENTORY_UNAVAILABLE
    assert publisher.sent == []


def test_payment_declined_triggers_release():
    inventory = FakeInventoryClient(
        ReservationResult(success=True, reservation_id="RES-1", unavailable_items=[], message="OK")
    )
    payment = FakePaymentClient(
        PaymentResponse(
            paymentId="PAY-ORD-1",
            orderId="ORD-1",
            status=PaymentStatus.DECLINED,
            failureReason="Bank lehnt ab",
        )
    )
    publisher = FakePublisher()

    workflow = OrderWorkflow(OrderRepository(), inventory, payment, publisher)
    record = workflow.process_order(sample_order())

    assert record is not None
    assert record.status == OrderStatus.PAYMENT_FAILED
    assert inventory.released is True
    assert publisher.sent == []

