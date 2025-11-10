from __future__ import annotations

import logging
import random
import string

from fastapi import FastAPI, HTTPException

from ..models import PaymentRequest, PaymentResponse, PaymentStatus

LOGGER = logging.getLogger(__name__)


def _authorization_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def create_app() -> FastAPI:
    app = FastAPI(title="Payment Service Simulation", version="1.0.0")

    @app.post("/payments", response_model=PaymentResponse)
    def authorize_payment(body: PaymentRequest) -> PaymentResponse:
        LOGGER.info("Zahlungsanforderung erhalten: %s", body.paymentId)
        metadata = body.metadata or {}
        scenario = (metadata.get("simulate") or metadata.get("scenario") or "").lower()

        if scenario == "decline":
            LOGGER.info("Simuliere abgelehnte Zahlung für %s", body.paymentId)
            return PaymentResponse(
                paymentId=body.paymentId,
                orderId=body.orderId,
                status=PaymentStatus.DECLINED,
                failureReason="Zahlung manuell abgelehnt (Simulation).",
            )

        if scenario == "error":
            LOGGER.error("Simuliere technischen Fehler für %s", body.paymentId)
            raise HTTPException(status_code=500, detail="Simulierter Payment Service Fehler")

        if body.amount <= 0:
            LOGGER.warning("Ungültiger Betrag für %s", body.paymentId)
            raise HTTPException(status_code=400, detail="Betrag muss größer als 0 sein.")

        if body.method == "INVOICE" and body.amount > 500:
            LOGGER.info("Rechnungszahlung über Schwellenwert, lehne ab.")
            return PaymentResponse(
                paymentId=body.paymentId,
                orderId=body.orderId,
                status=PaymentStatus.DECLINED,
                failureReason="Rechnungsgrenze überschritten.",
            )

        return PaymentResponse(
            paymentId=body.paymentId,
            orderId=body.orderId,
            status=PaymentStatus.AUTHORIZED,
            authorizationCode=_authorization_code(),
        )

    return app

