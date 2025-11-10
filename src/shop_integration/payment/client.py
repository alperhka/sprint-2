from __future__ import annotations

import logging
from typing import Mapping

import requests
from requests import Response

from ..models import PaymentRequest, PaymentResponse, PaymentStatus

LOGGER = logging.getLogger(__name__)


class PaymentClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def authorize(
        self, order_id: str, amount: float, metadata: Mapping[str, str] | None = None
    ) -> PaymentResponse:
        payment_id = f"PAY-{order_id}"
        body = PaymentRequest(
            paymentId=payment_id,
            orderId=order_id,
            amount=amount,
            metadata=dict(metadata or {}),
        )
        LOGGER.info("Rufe Payment Service für Order %s auf.", order_id)
        response: Response = requests.post(
            url=f"{self._base_url}/payments",
            json=body.model_dump(),
            timeout=self._timeout,
        )

        if response.status_code >= 500:
            LOGGER.error("Payment Service Fehler (%s) für Order %s", response.status_code, order_id)
            raise RuntimeError(f"Payment Service Fehler: {response.text}")

        if response.status_code == 400:
            LOGGER.warning("Ungültige Zahlungsanfrage für Order %s: %s", order_id, response.text)
            raise ValueError(f"Ungültige Zahlungsanfrage: {response.text}")

        payload = response.json()
        payment_response = PaymentResponse.model_validate(payload)

        if payment_response.status == PaymentStatus.ERROR:
            raise RuntimeError("Zahlung konnte nicht verarbeitet werden.")

        return payment_response

