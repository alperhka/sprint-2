from __future__ import annotations

import json
import logging
import threading
from typing import Callable, Optional

import pika

LOGGER = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(self, url: str, queue: str) -> None:
        parameters = pika.URLParameters(url)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._queue = queue
        self._channel.queue_declare(queue=queue, durable=True)
        LOGGER.info("RabbitMQPublisher bereit für Queue %s", queue)

    def publish(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self._channel.basic_publish(
            exchange="",
            routing_key=self._queue,
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
        )
        LOGGER.info("Nachricht in Queue %s gesendet: %s", self._queue, payload)

    def close(self) -> None:
        self._connection.close()


class RabbitMQConsumer:
    def __init__(self, url: str, queue: str) -> None:
        parameters = pika.URLParameters(url)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._queue = queue
        self._channel.queue_declare(queue=queue, durable=True)
        self._callback: Optional[Callable[[dict], None]] = None
        LOGGER.info("RabbitMQConsumer hört auf Queue %s", queue)

    def _on_message(self, channel, method, properties, body) -> None:
        try:
            message = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:  # pragma: no cover - Schutzmaßnahme
            LOGGER.error("Fehler beim JSON-Parsing: %s", exc)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        if self._callback:
            try:
                self._callback(message)
            except Exception as exc:  # pragma: no cover - Schutzmaßnahme
                LOGGER.exception("Fehler in der Consumer-Callback: %s", exc)
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                return

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def start(self, callback: Callable[[dict], None], auto_ack: bool = False) -> None:
        self._callback = callback
        self._channel.basic_consume(queue=self._queue, on_message_callback=self._on_message, auto_ack=auto_ack)
        LOGGER.info("Starte RabbitMQConsumer Loop für Queue %s", self._queue)
        self._channel.start_consuming()

    def stop(self) -> None:
        if self._channel.is_open:
            self._channel.stop_consuming()
        if self._connection.is_open:
            self._connection.close()


class ThreadedConsumer:
    def __init__(self, consumer: RabbitMQConsumer) -> None:
        self._consumer = consumer
        self._thread: Optional[threading.Thread] = None

    def start(self, callback: Callable[[dict], None]) -> None:
        if self._thread and self._thread.is_alive():
            LOGGER.warning("Consumer läuft bereits.")
            return

        def runner() -> None:
            self._consumer.start(callback)

        self._thread = threading.Thread(target=runner, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._consumer.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

