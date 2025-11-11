#!/bin/bash

# Startskript für alle Services der Shop AG Integration

cd "$(dirname "$0")"
source .venv/bin/activate

echo "=== Shop AG Integration - Services starten ==="
echo ""

# Prüfe ob RabbitMQ läuft
if ! docker ps | grep -q rabbitmq; then
    echo "Starte RabbitMQ..."
    docker compose up -d
    sleep 3
fi

echo "Services werden gestartet..."
echo "Drücke Ctrl+C zum Beenden aller Services"
echo ""

# Funktion zum Beenden aller Services beim Beenden des Skripts
cleanup() {
    echo ""
    echo "Beende Services..."
    kill $INVENTORY_PID $PAYMENT_PID $WMS_PID $OMS_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Starte Inventory Service
echo "Starte Inventory Service (gRPC, Port 50051)..."
python scripts/run_inventory.py &
INVENTORY_PID=$!

sleep 2

# Starte Payment Service
echo "Starte Payment Service (REST, Port 8100)..."
python scripts/run_payment.py &
PAYMENT_PID=$!

sleep 2

# Starte WMS Worker
echo "Starte WMS Worker (RabbitMQ)..."
python scripts/run_wms.py &
WMS_PID=$!

sleep 2

# Starte OMS
echo "Starte OMS (REST, Port 8000)..."
python scripts/run_oms.py &
OMS_PID=$!

sleep 3

echo ""
echo "=== Alle Services gestartet ==="
echo "Inventory Service: http://localhost:50051 (gRPC)"
echo "Payment Service: http://localhost:8100"
echo "OMS: http://localhost:8000"
echo "RabbitMQ Management: http://localhost:15672 (guest/guest)"
echo ""
echo "Services laufen. Drücke Ctrl+C zum Beenden."
echo ""

# Warte auf Beendigung
wait

