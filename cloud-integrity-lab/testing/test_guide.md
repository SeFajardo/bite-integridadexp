# Guia de Pruebas - Laboratorio de Integridad de Datos

Este documento describe paso a paso como reproducir el experimento del ASR
de integridad de datos con hashing.

---

## 1. Preparacion Local (sin AWS)

### 1.1 Requisitos
- Python 3.10+
- PostgreSQL 14+ corriendo localmente
- `pip install -r requirements.txt`

### 1.2 Configurar la base de datos
```sql
CREATE DATABASE cloud_integrity_db;
```

### 1.3 Variables de entorno
```bash
cp .env.example .env
# editar .env con DB_HOST=localhost y la password de postgres
```

### 1.4 Inicializar el proyecto
```bash
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8080
```

Salida esperada del seed:
```
Datos de prueba creados: 18 reportes para 3 proyectos.
```

---

## 2. Despliegue en AWS con Terraform

```bash
cd terraform/
terraform init
terraform validate
terraform apply \
  -var="db_password=ChangeMe123!" \
  -var="key_name=mi-keypair-aws"
```

Outputs:
- `app_public_ip` - IP publica de la instancia Django
- `db_private_ip` - IP privada de la instancia PostgreSQL
- `app_url` - URL base para llamar la API

---

## 3. Prueba Manual Paso a Paso

### 3.1 Crear reportes y verificar hash
```bash
curl -X POST http://localhost:8080/api/reports/ \
  -H "Content-Type: application/json" \
  -d '{"project_name":"ProyectoTest","month":7,"year":2025,
       "services":{"EC2":120.5,"S3":45.0,"RDS":200.0}}'
```
La respuesta incluye `report_hash` (SHA-256 hex) e `is_valid: true`.

```bash
curl http://localhost:8080/api/reports/1/verify/
# {"is_intact": true, "stored_hash": "...", "computed_hash": "...", ...}
```

### 3.2 Simular ataque (alterar DB)
Desde la instancia DB (o conectado por psql):
```bash
chmod +x scripts/simulate_tamper.sh
./scripts/simulate_tamper.sh 1 localhost postgres cloud_integrity_db
```
Esto suma 9999.99 a `total_cost` e injecta `Malicious` en `services`,
**sin tocar `report_hash`**.

### 3.3 Verificar deteccion y bloqueo
```bash
curl -i http://localhost:8080/api/reports/1/
```
Respuesta esperada:
```
HTTP/1.1 403 Forbidden
{
  "error": "INTEGRITY_VIOLATION",
  "message": "Este reporte ha sido alterado. Acceso bloqueado.",
  "report_id": 1,
  "alert_id": 1
}
```

### 3.4 Revisar alertas de auditoria
```bash
curl http://localhost:8080/api/audit/alerts/
curl http://localhost:8080/api/audit/dashboard/
```

---

## 4. Pruebas con JMeter

```bash
jmeter -n -t testing/jmeter_plan.jmx -l results.jtl
```
Para usar un host distinto: `-Jhost=ec2-xx-xx-xx-xx.compute.amazonaws.com`.

Los Thread Groups corren **en serie** (`serialize_threadgroups=true`):
1. Crea reporte (POST 201)
2. Lee reporte integro (GET 200)
3. *Manualmente correr `simulate_tamper.sh` aqui* y luego seguir
4. Detectar violacion (GET 403 + INTEGRITY_VIOLATION)
5. Listar alertas (GET 200 + CRITICAL)
6. Dashboard (GET 200)

---

## 5. Pruebas con curl (referencia rapida)

```bash
# Crear reporte
curl -X POST $URL/api/reports/ -H "Content-Type: application/json" \
  -d '{"project_name":"X","month":1,"year":2025,"services":{"EC2":10}}'

# Listar reportes
curl $URL/api/reports/

# Detalle de reporte
curl $URL/api/reports/1/

# Verificacion explicita de hash
curl $URL/api/reports/1/verify/

# Estadisticas
curl $URL/api/reports/stats/

# Alertas
curl $URL/api/audit/alerts/
curl $URL/api/audit/alerts/1/
curl -X PATCH $URL/api/audit/alerts/1/resolve/
curl $URL/api/audit/dashboard/
```

---

## 6. Resultados Esperados

| Escenario | Tipo de Accion | Resultado Esperado | ASR Cumplido |
|-----------|---------------|--------------------|--------------|
| Consulta reporte sin alterar | GET /api/reports/1/ | HTTP 200, datos completos, is_valid=true | Si |
| Consulta tras alteracion manual DB | GET /api/reports/1/ | HTTP 403 + INTEGRITY_VIOLATION + alerta CRITICAL | Si |
| Intento de alterar via API (POST con hash falso) | POST /api/reports/ | Hash recalculado automaticamente, no se acepta | Si |
| Verificacion explicita de integridad | GET /api/reports/1/verify/ | Respuesta detallada del estado del hash | Si |
| Listado de reportes con uno alterado | GET /api/reports/ | Solo retorna validos; el alterado se marca invalido y dispara alerta | Si |
| Listar alertas tras ataque | GET /api/audit/alerts/ | Al menos una alerta CRITICAL no resuelta | Si |

---

## 7. Analisis del ASR

### Se cumple el ASR?
**Si.** Cada lectura recalcula el hash SHA-256 sobre los campos criticos
y lo compara con el almacenado en la fila. Cualquier alteracion directa en
PostgreSQL produce un mismatch y dispara:
- `is_valid = False` en el reporte
- `AuditAlert` de severidad `CRITICAL`
- HTTP 403 al usuario final con explicacion

Esto da una tasa de deteccion del 100% para alteraciones en los campos
hasheados (`project_name`, `month`, `year`, `services`, `total_cost`,
`currency`).

### Tactica implementada: Hashing
- Algoritmo: SHA-256 (modulo `hashlib` de Python).
- Serializacion determinista: `json.dumps(..., sort_keys=True, ensure_ascii=True)`.
- Almacenamiento del hash: campo `report_hash` (CHAR(64) hex) en la misma tabla.
- Verificacion en cada GET (lista y detalle), no solo bajo demanda.

### Limitaciones y mejoras posibles
- **Atacante con acceso a la app**: si el atacante puede ejecutar codigo Python
  con el SECRET_KEY, puede recalcular y regrabar el hash. Mitigacion: usar HMAC
  con una llave en KMS/Secrets Manager.
- **Hash en la misma fila**: un atacante con escritura en DB puede cambiar
  datos *y* hash a la vez. Mitigacion: almacenar hashes en un ledger separado
  (tabla append-only, otra DB, o un servicio externo) o encadenar hashes
  estilo blockchain.
- **Campos no hasheados**: `consolidated_at` e `id` no estan en el hash.
  Si se quiere proteger esos campos hay que incluirlos en `compute_report_hash`.
- **Deteccion vs prevencion**: el sistema detecta y bloquea, pero no impide
  la escritura. Para prevencion real se requieren controles a nivel DB
  (roles, triggers, row-level security).
