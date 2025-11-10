from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt


class OrderStatus(str, Enum):
    RECEIVED = "RECEIVED"
    INVENTORY_RESERVED = "INVENTORY_RESERVED"
    INVENTORY_UNAVAILABLE = "INVENTORY_UNAVAILABLE"
    PAYMENT_AUTHORIZED = "PAYMENT_AUTHORIZED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    FULFILLMENT_STARTED = "FULFILLMENT_STARTED"
    ITEMS_PICKED = "ITEMS_PICKED"
    ORDER_PACKED = "ORDER_PACKED"
    ORDER_SHIPPED = "ORDER_SHIPPED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class PaymentStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    DECLINED = "DECLINED"
    ERROR = "ERROR"


class Address(BaseModel):
    street: str
    city: str
    zipCode: str
    country: str


class Customer(BaseModel):
    customerId: str
    prename: str
    name: str


class OrderItem(BaseModel):
    productId: str
    quantity: PositiveInt
    price: float


class Order(BaseModel):
    orderId: str
    customer: Customer
    items: List[OrderItem]
    totalAmount: float
    shippingAddress: Address
    metadata: dict[str, str] | None = None


class OrderHistoryEntry(BaseModel):
    timestamp: datetime
    status: OrderStatus
    message: str


class OrderRecord(BaseModel):
    order: Order
    status: OrderStatus
    createdAt: datetime
    updatedAt: datetime
    history: List[OrderHistoryEntry] = Field(default_factory=list)
    reservationId: Optional[str] = None
    paymentId: Optional[str] = None


class PaymentRequest(BaseModel):
    paymentId: str
    orderId: str
    amount: float
    currency: str = "EUR"
    method: str = "CREDIT_CARD"
    metadata: dict[str, str] | None = None


class PaymentResponse(BaseModel):
    paymentId: str
    orderId: str
    status: PaymentStatus
    authorizationCode: Optional[str] = None
    failureReason: Optional[str] = None

