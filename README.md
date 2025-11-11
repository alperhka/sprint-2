# Shop AG Integrationslösung

Diese Repository enthält die Ausarbeitung der **Aufgabe 2 – Integration** für die Shop AG. Die Lösung umfasst Schnittstellenspezifikationen, Architekturartefakte, eine Referenzimplementierung der beteiligten (simulierten) Services sowie automatisierte Tests für mehrere Szenarien.

## Projektüberblick

- **OMS (Order Management Service)** – FastAPI-Anwendung, die Bestellungen entgegennimmt und den Integrationsworkflow steuert.
- **Inventory Service** – gRPC-Microservice mit In-Memory-Lagerbestand.
- **Payment Service** – REST-Service zur Simulation verschiedener Zahlungsergebnisse.
- **WMS (Warehouse Management System)** – Worker, der RabbitMQ-Nachrichten verarbeitet und Statusupdates zurückmeldet.
- **RabbitMQ** – Message Broker für Fulfillment-Kommandos und Statusereignisse.

Die wichtigsten Artefakte:

- Schnittstellen: `docs/openapi/*.yaml`, `docs/proto/inventory.proto`, `docs/messaging/wms_messages.yaml`
- Architektur & Fehlerbehandlung: `docs/architecture.md`
- Implementierungscode: `src/shop_integration`
- Tests: `tests/test_workflow.py`

## Voraussetzungen

- Python 3.9+
- `pip` bzw. `uv` o.ä. Paketmanager
- Docker (zum Starten von RabbitMQ via Compose)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
```

## Infrastruktur starten

```bash
docker compose up -d
```

RabbitMQ ist anschließend unter `amqp://guest:guest@localhost:5672/` erreichbar; das Management-UI steht auf `http://localhost:15672` bereit.

## Services starten

### Option 1: Alle Services auf einmal (empfohlen)

```bash
./start_all_services.sh
```

Dieses Skript startet alle Services in einem Terminal und beendet sie gemeinsam mit Ctrl+C.

### Option 2: Einzelne Services in separaten Terminals

```bash
# Inventory (gRPC, Port 50051)
python scripts/run_inventory.py

# Payment (REST, Port 8100)
python scripts/run_payment.py

# WMS Worker (RabbitMQ-Consumer/Publisher)
python scripts/run_wms.py

# OMS (REST, Port 8000)
python scripts/run_oms.py
```

Der OMS erzeugt/aktualisiert die Logdatei `order-processing.log`.

## Beispielaufrufe (cURL)

### 1. Happy Path – Bestellung erfolgreich
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d @examples/order_happy.json
```

### 2. Inventar nicht verfügbar
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d @examples/order_out_of_stock.json
```

### 3. Zahlung abgelehnt
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d @examples/order_payment_declined.json
```

Die Beispielpayloads können anhand des Templates im Aufgabenblatt erstellt werden. Zur Simulation einer Zahlungsablehnung genügt ein Eintrag `"metadata": {"simulate": "decline"}` in der Bestellung.

### Alle Testszenarien auf einmal

```bash
./test_scenarios.sh
```

Dieses Skript führt alle drei Testszenarien nacheinander aus.

## Tests ausführen

```bash
pytest
```

Die Tests prüfen den Workflow für drei Kernpfade (Erfolg, Inventarfehler, Zahlung abgelehnt) mithilfe von Stub-Implementierungen der externen Services.

## Logging & Monitoring

- Zentrale Logdatei: `order-processing.log`
- Alle Services loggen zusätzlich auf STDOUT (sichtbar in den Konsolenfenstern).
- RabbitMQ UI zeigt Queue-Status und Nachrichtenmetriken.

## Weiteres Vorgehen

- Infrastruktur härten (TLS, Authentifizierung, Observability)
- Persistente Order-Datenbank anschließen
- Automatisierte Contract-Tests (OpenAPI, gRPC) ergänzen

