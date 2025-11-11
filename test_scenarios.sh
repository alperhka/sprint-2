#!/bin/bash

# Testskript für die drei Szenarien der Shop AG Integration

OMS_URL="http://localhost:8000"

echo "=== Shop AG Integration - Testszenarien ==="
echo ""

# Test 1: Happy Path
echo "Test 1: Happy Path - Bestellung erfolgreich"
echo "--------------------------------------------"
curl -X POST "$OMS_URL/orders" \
  -H "Content-Type: application/json" \
  -d @examples/order_happy.json \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool 2>/dev/null || echo "Fehler: OMS nicht erreichbar oder ungültige Antwort"
echo ""
sleep 2

# Test 2: Out of Stock
echo "Test 2: Inventar nicht verfügbar"
echo "--------------------------------------------"
curl -X POST "$OMS_URL/orders" \
  -H "Content-Type: application/json" \
  -d @examples/order_out_of_stock.json \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool 2>/dev/null || echo "Fehler: OMS nicht erreichbar oder ungültige Antwort"
echo ""
sleep 2

# Test 3: Payment Declined
echo "Test 3: Zahlung abgelehnt"
echo "--------------------------------------------"
curl -X POST "$OMS_URL/orders" \
  -H "Content-Type: application/json" \
  -d @examples/order_payment_declined.json \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool 2>/dev/null || echo "Fehler: OMS nicht erreichbar oder ungültige Antwort"
echo ""

echo "=== Tests abgeschlossen ==="
echo "Log-Datei prüfen: cat order-processing.log"

