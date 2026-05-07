#!/bin/bash
# simulate_tamper.sh
# Simula alteracion maliciosa directa en la base de datos.
# USO: ./simulate_tamper.sh <REPORT_ID> <DB_HOST> <DB_USER> <DB_NAME>

REPORT_ID=${1:-1}
DB_HOST=${2:-"localhost"}
DB_USER=${3:-"postgres"}
DB_NAME=${4:-"cloud_integrity_db"}

echo "SIMULANDO ATAQUE: Alterando reporte ID=$REPORT_ID directamente en DB..."

PSQL_CMD="UPDATE reports_cloudresourcereport
  SET total_cost = total_cost + 9999.99,
      services = services || '{\"Malicious\": 9999.99}'::jsonb
  WHERE id = $REPORT_ID;"

psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "$PSQL_CMD"

echo " Alteracion aplicada. El hash almacenado ya NO coincide con los datos."
echo "   Ahora consulta GET /api/reports/$REPORT_ID/ para ver la deteccion."
